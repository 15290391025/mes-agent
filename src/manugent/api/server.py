"""ManuGent FastAPI Server.

REST API server providing:
- /chat - Natural language MES queries
- /query - Structured MES queries
- /mcp - MCP protocol endpoint for agent-to-agent communication
- /health - Health check
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from manugent.agent.core import AgentResponse, MESAgent
from manugent.config.settings import Settings
from manugent.connector.base import MESConnectionConfig
from manugent.connector.factory import create_connector
from manugent.protocol.tools import MANUFACTURING_TOOLS, list_tools

logger = logging.getLogger(__name__)

# Global state
_agent: MESAgent | None = None
_settings: Settings | None = None


# ============================================
# Request/Response Models
# ============================================

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="Natural language query")
    session_id: str | None = Field(default=None, description="Session ID for conversation continuity")
    stream: bool = Field(default=False, description="Enable streaming response")


class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Structured query request."""
    tool: str = Field(..., description="MCP tool name")
    params: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    """Structured query response."""
    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolInfo(BaseModel):
    """Tool information."""
    name: str
    description: str
    category: str
    safety_level: str
    parameters: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    mes_connected: bool
    tools_available: int


# ============================================
# App Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _agent, _settings

    # Startup
    _settings = Settings.from_env()
    logging.basicConfig(level=getattr(logging, _settings.app.log_level))

    logger.info("ManuGent API starting up...")

    # Create LLM
    llm = _settings.llm.get_llm()

    # Create MES connector
    mes_config = MESConnectionConfig(
        mes_type=_settings.mes.mes_type,
        base_url=_settings.mes.mes_url,
        auth_type="bearer" if _settings.mes.mes_token else "none",
        auth_token=_settings.mes.mes_token,
        auth_username=_settings.mes.mes_username,
        auth_password=_settings.mes.mes_password,
        timeout=_settings.mes.mes_timeout,
    )
    connector = create_connector(mes_config)

    try:
        await connector.connect()
        logger.info(f"Connected to MES: {_settings.mes.mes_url}")
    except Exception as e:
        logger.warning(f"Could not connect to MES (will retry on queries): {e}")

    # Create agent
    _agent = MESAgent(llm=llm, connector=connector)
    logger.info(f"Agent initialized with {_settings.llm.provider}/{_settings.llm.model}")

    yield

    # Shutdown
    logger.info("ManuGent API shutting down...")
    await connector.disconnect()


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="ManuGent API",
    description="AI Agent middleware for Manufacturing Execution Systems",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    mes_connected = False
    if _agent:
        try:
            mes_connected = await _agent.config.connector.health_check()
        except Exception:
            pass

    return HealthResponse(
        status="ok",
        version="0.1.0",
        mes_connected=mes_connected,
        tools_available=len(MANUFACTURING_TOOLS),
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Natural language MES query.

    Send a natural language question about factory operations
    and get an AI-analyzed response based on real MES data.
    """
    if not _agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        response: AgentResponse = await _agent.chat(
            message=request.message,
            stream=request.stream,
        )

        return ChatResponse(
            content=response.content,
            tool_calls=response.tool_calls,
            metadata=response.metadata,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Structured MES query.

    Direct tool call without LLM reasoning. For when you
    already know which tool to call.
    """
    if not _agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    result = await _agent.query(request.tool, request.params)
    return QueryResponse(
        success=result.success,
        data=result.data,
        error=result.error,
        metadata=result.metadata,
    )


@app.get("/tools", response_model=list[ToolInfo])
async def list_available_tools():
    """List all available manufacturing tools."""
    tools = list_tools()
    return [
        ToolInfo(
            name=t.name,
            description=t.description,
            category=t.category.value,
            safety_level=t.safety_level.value,
            parameters=[
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "enum_values": p.enum_values,
                }
                for p in t.parameters
            ],
        )
        for t in tools
    ]


@app.post("/chat/clear")
async def clear_chat_history():
    """Clear conversation history."""
    if _agent:
        _agent.clear_history()
    return {"status": "ok", "message": "Chat history cleared"}


# ============================================
# MCP Protocol Endpoint
# ============================================

class MCPToolCall(BaseModel):
    """MCP tool call request."""
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MCPToolResult(BaseModel):
    """MCP tool call result."""
    content: list[dict[str, Any]]
    is_error: bool = False


@app.post("/mcp/v1/tools/call", response_model=MCPToolResult)
async def mcp_tool_call(call: MCPToolCall):
    """MCP protocol tool invocation endpoint.

    Standardized endpoint for agent-to-agent communication
    following the Model Context Protocol.
    """
    if not _agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    result = await _agent.query(call.name, call.arguments)

    return MCPToolResult(
        content=[{
            "type": "text",
            "text": str(result.data) if result.success else result.error,
        }],
        is_error=not result.success,
    )


@app.get("/mcp/v1/tools/list")
async def mcp_list_tools():
    """MCP protocol: list available tools."""
    tools = list_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        p.name: {
                            "type": p.type if p.type != "enum" else "string",
                            "description": p.description,
                            **({"enum": p.enum_values} if p.enum_values else {}),
                        }
                        for p in t.parameters
                    },
                    "required": [p.name for p in t.parameters if p.required],
                },
            }
            for t in tools
        ]
    }
