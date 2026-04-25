"""ManuGent FastAPI Server.

REST API server providing:
- /chat - Natural language MES queries
- /query - Structured MES queries
- /mcp - MCP protocol endpoint for agent-to-agent communication
- /health - Health check
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from manugent.agent.core import AgentResponse
from manugent.agent.session import AgentSessionManager
from manugent.api.demo_page import DEMO_HTML
from manugent.config.settings import Settings
from manugent.connector.base import MESConnectionConfig
from manugent.connector.factory import create_connector
from manugent.memory import SQLiteMemoryStore
from manugent.protocol.tools import MANUFACTURING_TOOLS, list_tools
from manugent.security import ApprovalDecision, ApprovalQueue, verify_bearer_token
from manugent.workflows import RootCauseWorkflow

logger = logging.getLogger(__name__)

# Global state
_session_manager: AgentSessionManager | None = None
_approval_queue: ApprovalQueue | None = None
_settings: Settings | None = None


# ============================================
# Request/Response Models
# ============================================

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="Natural language query")
    session_id: str | None = Field(
        default=None,
        description="Session ID for conversation continuity",
    )
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
    session_id: str | None = Field(default=None, description="Session ID for audit scope")


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
    active_sessions: int = 0


class ApprovalDecisionRequest(BaseModel):
    """Approval decision request."""
    approved: bool
    decided_by: str = Field(default="human", description="Approver identifier")
    reason: str = Field(default="", description="Decision rationale")


class YieldDropWorkflowRequest(BaseModel):
    """Yield-drop root-cause workflow request."""
    line_id: str = Field(default="SMT-03", description="Production line ID")
    time_range: str = Field(default="24h", description="MES query time range")
    session_id: str | None = Field(default=None, description="Session ID for memory scope")


# ============================================
# App Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _approval_queue, _session_manager, _settings

    # Startup
    _settings = Settings.from_env()
    logging.basicConfig(level=getattr(logging, _settings.app.log_level))

    logger.info("ManuGent API starting up...")

    mes_config = MESConnectionConfig(
        mes_type=_settings.mes.mes_type,
        base_url=_settings.mes.mes_url,
        auth_type="bearer" if _settings.mes.mes_token else "none",
        auth_token=_settings.mes.mes_token,
        auth_username=_settings.mes.mes_username,
        auth_password=_settings.mes.mes_password,
        timeout=_settings.mes.mes_timeout,
        extra={"endpoint_mapping_path": _settings.mes.mes_mapping_path},
    )
    memory_store = SQLiteMemoryStore(_settings.db.memory_db_path)
    _approval_queue = ApprovalQueue()

    def llm_factory():
        return _settings.llm.get_llm()

    def connector_factory():
        connector = create_connector(mes_config)
        return connector

    _session_manager = AgentSessionManager(
        llm_factory=llm_factory,
        connector_factory=connector_factory,
        memory_store=memory_store,
        approval_queue=_approval_queue,
        default_scope=_settings.mes.mes_type,
    )
    logger.info(f"Session manager initialized with {_settings.llm.provider}/{_settings.llm.model}")

    yield

    # Shutdown
    logger.info("ManuGent API shutting down...")


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


@app.middleware("http")
async def optional_api_token_guard(request: Request, call_next):
    """Optional local API token guard.

    Enterprise auth should normally be handled by SSO/API Gateway. This guard is
    a direct-deployment safeguard enabled only when MANUGENT_API_TOKEN is set.
    """
    if _settings and _settings.app.api_token:
        authorization = request.headers.get("Authorization")
        if not verify_bearer_token(authorization, _settings.app.api_token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing bearer token"},
            )
    return await call_next(request)


# ============================================
# Endpoints
# ============================================

@app.get("/", response_class=HTMLResponse)
async def web_demo():
    """Minimal web demo for RCA evidence chain."""
    return HTMLResponse(DEMO_HTML)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    mes_connected = False
    active_sessions = _session_manager.count() if _session_manager else 0
    if _session_manager:
        agent = _session_manager.get("__health__")
        with suppress(Exception):
            await agent.config.connector.connect()
            mes_connected = await agent.config.connector.health_check()
        _session_manager.clear("__health__")

    return HealthResponse(
        status="ok",
        version="0.1.0",
        mes_connected=mes_connected,
        tools_available=len(MANUFACTURING_TOOLS),
        active_sessions=active_sessions,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Natural language MES query.

    Send a natural language question about factory operations
    and get an AI-analyzed response based on real MES data.
    """
    if not _session_manager:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        agent = _session_manager.get(request.session_id)
        await agent.config.connector.connect()
        response: AgentResponse = await agent.chat(
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
    if not _session_manager:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent = _session_manager.get(request.session_id)
    await agent.config.connector.connect()
    result = await agent.query(request.tool, request.params)
    return QueryResponse(
        success=result.success,
        data=result.data,
        error=result.error,
        metadata=result.metadata,
    )


@app.post("/workflows/root-cause/yield-drop")
async def yield_drop_root_cause(request: YieldDropWorkflowRequest):
    """Run deterministic yield-drop RCA workflow and return evidence chain."""
    if not _session_manager:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent = _session_manager.get(request.session_id)
    await agent.config.connector.connect()
    workflow = RootCauseWorkflow(
        agent.config.connector,
        memory_store=agent.config.memory_store,
        memory_scope=agent.config.memory_scope,
    )
    report = await workflow.analyze_yield_drop(
        line_id=request.line_id,
        time_range=request.time_range,
    )
    return report.to_dict()


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
async def clear_chat_history(session_id: str | None = None):
    """Clear conversation history."""
    if not _session_manager:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    cleared = _session_manager.clear(session_id)
    return {"status": "ok", "cleared": cleared, "session_id": session_id}


@app.get("/approvals")
async def list_approvals(session_id: str | None = None):
    """List pending approval requests."""
    if not _approval_queue:
        raise HTTPException(status_code=503, detail="Approval queue not initialized")
    return {
        "approvals": [
            request.to_dict()
            for request in _approval_queue.list_pending(session_id=session_id)
        ]
    }


@app.post("/approvals/{request_id}/decision")
async def decide_approval(request_id: str, decision: ApprovalDecisionRequest):
    """Approve or reject a pending request."""
    if not _approval_queue:
        raise HTTPException(status_code=503, detail="Approval queue not initialized")
    updated = _approval_queue.decide(
        ApprovalDecision(
            request_id=request_id,
            approved=decision.approved,
            decided_by=decision.decided_by,
            reason=decision.reason,
        )
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return updated.to_dict()


# ============================================
# MCP Protocol Endpoint
# ============================================

class MCPToolCall(BaseModel):
    """MCP tool call request."""
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = Field(default=None, description="Session ID for audit scope")


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
    if not _session_manager:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent = _session_manager.get(call.session_id)
    await agent.config.connector.connect()
    result = await agent.query(call.name, call.arguments)

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
