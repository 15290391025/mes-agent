"""ManuGent Agent Core.

The core MES Agent that uses LangGraph for stateful multi-step reasoning
to answer natural language queries about manufacturing operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from manugent.connector.base import MESConnector, QueryResult
from manugent.memory import MemoryContextBuilder, MemoryStore
from manugent.memory.recipes import remember_tool_audit
from manugent.protocol.tools import (
    MANUFACTURING_TOOLS,
    MCPTool,
    SafetyLevel,
    list_tools,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个制造业智能助手 (ManuGent)，专门帮助工厂人员查询和分析MES系统数据。

你的能力：
1. 用自然语言回答关于生产数据的问题（OEE、良率、产量等）
2. 分析品质异常和设备故障的根因
3. 提供生产优化建议
4. 生成生产报告

回答原则：
- 基于MES系统的真实数据回答，不要编造数据
- 数据有异常时主动提醒
- 给出具体、可执行的建议
- 使用中文回答
- 使用表格和结构化格式展示数据

当用户询问数据时，你需要调用合适的工具从MES获取数据，然后进行分析和回答。

可用工具：
{tool_descriptions}
"""


@dataclass
class AgentConfig:
    """Agent configuration."""
    llm: BaseChatModel
    connector: MESConnector
    memory_store: MemoryStore | None = None
    memory_scope: str = "default"
    system_prompt: str = ""
    max_tool_calls: int = 10
    require_approval_for: list[str] = field(default_factory=lambda: [
        "suggest_schedule", "create_alert", "create_work_order",
    ])


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    data: Any = None
    needs_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


class MESAgent:
    """Manufacturing Execution System AI Agent.

    Natural language interface to MES systems. Uses LLM + tool calling
    to understand queries, fetch data from MES, and provide analysis.

    Example:
        >>> from manugent import MESAgent
        >>> agent = MESAgent(
        ...     llm=your_llm,
        ...     connector=your_connector,
        ... )
        >>> response = await agent.chat("3号线今天OEE是多少？")
        >>> print(response)
    """

    def __init__(
        self,
        llm: BaseChatModel,
        connector: MESConnector,
        system_prompt: str = "",
        memory_store: MemoryStore | None = None,
        memory_scope: str = "default",
    ) -> None:
        self.config = AgentConfig(
            llm=llm,
            connector=connector,
            memory_store=memory_store,
            memory_scope=memory_scope,
            system_prompt=system_prompt or self._build_system_prompt(),
        )
        self._history: list[BaseMessage] = []
        self._memory_context = (
            MemoryContextBuilder(memory_store) if memory_store is not None else None
        )

    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions."""
        tools = list_tools()
        tool_desc = "\n".join(
            f"- {t.name}: {t.description} (参数: {', '.join(p.name for p in t.parameters)})"
            for t in tools
        )
        return SYSTEM_PROMPT.format(tool_descriptions=tool_desc)

    def _tool_to_openai(self, tool: MCPTool) -> dict[str, Any]:
        """Convert MCP tool to OpenAI function calling format."""
        properties = {}
        required = []

        for param in tool.parameters:
            prop: dict[str, Any] = {
                "type": param.type if param.type != "enum" else "string",
                "description": param.description,
            }
            if param.enum_values:
                prop["enum"] = param.enum_values
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    async def chat(self, message: str, stream: bool = False) -> AgentResponse:
        """Process a user message and return agent response.

        This is the main entry point. It:
        1. Adds the user message to history
        2. Calls the LLM with tool definitions
        3. If LLM wants to call tools, executes them against MES
        4. Feeds tool results back to LLM for final response
        5. Returns the formatted response

        Args:
            message: User's natural language query.
            stream: Whether to stream the response (not yet implemented).

        Returns:
            AgentResponse with the answer and metadata.
        """
        # Add user message
        self._history.append(HumanMessage(content=message))

        # Build tool definitions for LLM
        tools = list_tools()
        tool_schemas = [self._tool_to_openai(t) for t in tools]

        memory_context = self._build_memory_context(message)
        system_prompt = self.config.system_prompt
        if memory_context:
            system_prompt = f"{system_prompt}\n\n{memory_context}"

        # Prepare messages
        messages = [
            SystemMessage(content=system_prompt),
            *self._history,
        ]

        tool_calls_made: list[dict[str, Any]] = []
        max_iterations = self.config.max_tool_calls

        for iteration in range(max_iterations):
            # Call LLM
            response = await self.config.llm.ainvoke(
                messages,
                tools=tool_schemas if tool_schemas else None,
            )

            # Check if LLM wants to call tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                messages.append(response)

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_call_id = tool_call["id"]

                    logger.info(f"Tool call: {tool_name}({tool_args})")

                    # Check if approval needed
                    tool_def = MANUFACTURING_TOOLS.get(tool_name)
                    needs_approval = (
                        tool_def and tool_def.safety_level in (
                            SafetyLevel.APPROVAL_REQUIRED,
                            SafetyLevel.RESTRICTED,
                        )
                    )

                    if needs_approval:
                        tool_result = {
                            "status": "needs_approval",
                            "message": f"操作 '{tool_name}' 需要人工确认。参数: {tool_args}",
                            "tool": tool_name,
                            "params": tool_args,
                        }
                    else:
                        # Execute tool against MES
                        result = await self.config.connector.execute_tool(tool_name, tool_args)
                        tool_result = result.to_dict()

                    self._remember_tool_call(tool_name, tool_args, tool_result, tool_def)

                    tool_calls_made.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": tool_result,
                    })

                    # Add tool result to messages
                    from langchain_core.messages import ToolMessage
                    messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call_id,
                        )
                    )

                # Continue the loop to let LLM process tool results
                continue
            else:
                # LLM gave a final response
                final_content = response.content
                self._history.append(AIMessage(content=final_content))

                return AgentResponse(
                    content=final_content,
                    tool_calls=tool_calls_made,
                    metadata={
                        "iterations": iteration + 1,
                        "tools_used": [tc["tool"] for tc in tool_calls_made],
                    },
                )

        # Max iterations reached
        return AgentResponse(
            content="抱歉，处理您的请求时超出了最大迭代次数。请尝试简化您的问题。",
            tool_calls=tool_calls_made,
            metadata={"error": "max_iterations_reached"},
        )

    async def query(self, tool_name: str, params: dict[str, Any]) -> QueryResult:
        """Direct tool call without LLM reasoning.

        For when you already know which tool to call.
        """
        result = await self.config.connector.execute_tool(tool_name, params)
        self._remember_tool_call(
            tool_name,
            params,
            result.to_dict(),
            MANUFACTURING_TOOLS.get(tool_name),
        )
        return result

    def _build_memory_context(self, message: str) -> str:
        """Build prompt memory context for the current turn."""
        if not self._memory_context:
            return ""
        return self._memory_context.build_context(
            query=message,
            scope=self.config.memory_scope,
        )

    def _remember_tool_call(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_result: dict[str, Any],
        tool_def: MCPTool | None,
    ) -> None:
        """Persist an audit memory for a tool call."""
        if self.config.memory_store is None:
            return

        success = tool_result.get("success")
        result_summary = "approval required"
        if success is not None:
            result_summary = "success" if success else f"error: {tool_result.get('error')}"

        safety_level = tool_def.safety_level.value if tool_def else "unknown"
        remember_tool_audit(
            self.config.memory_store,
            tool_name=tool_name,
            params=tool_args,
            result_summary=result_summary,
            scope=self.config.memory_scope,
            safety_level=safety_level,
        )

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history = []

    @property
    def history(self) -> list[BaseMessage]:
        """Get conversation history."""
        return self._history.copy()
