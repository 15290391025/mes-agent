"""Basic tests for ManuGent."""

import pytest


def test_version():
    """Test version import."""
    import manugent
    assert manugent.__version__ == "0.1.0"


def test_tool_registry():
    """Test MCP tool registration."""
    from manugent.protocol.tools import SafetyLevel, ToolCategory, list_tools

    tools = list_tools()
    assert len(tools) > 0

    # Check production tools exist
    prod_tools = list_tools(category=ToolCategory.PRODUCTION)
    assert any(t.name == "query_production_data" for t in prod_tools)

    # Check safety levels
    read_only = list_tools(safety_level=SafetyLevel.READ_ONLY)
    assert len(read_only) > 0


def test_query_result():
    """Test QueryResult dataclass."""
    from manugent.connector.base import QueryResult

    result = QueryResult(success=True, data={"oee": 85.2})
    assert result.success
    assert result.data["oee"] == 85.2

    d = result.to_dict()
    assert d["success"] is True
    assert d["data"]["oee"] == 85.2


def test_mes_connection_config():
    """Test MES connection config."""
    from manugent.connector.base import MESConnectionConfig

    config = MESConnectionConfig(
        mes_type="rest",
        base_url="http://localhost:8080/api",
        auth_token="test-token",
    )
    assert config.mes_type == "rest"
    assert config.base_url == "http://localhost:8080/api"
    assert config.timeout == 30  # default


def test_rest_connector_init():
    """Test REST connector initialization."""
    from manugent.connector.base import MESConnectionConfig
    from manugent.connector.rest import RestConnector

    config = MESConnectionConfig(
        mes_type="rest",
        base_url="http://localhost:8080/api",
    )
    connector = RestConnector(config)
    assert connector.mes_type == "rest"
    assert not connector.is_connected


def test_demo_connector_schema():
    """Test demo MES connector exposes manufacturing schema."""
    from manugent.connector.demo import DemoMESConnector

    connector = DemoMESConnector()
    assert connector.mes_type == "demo"
    assert "SMT-03" in connector._data["lines"]


@pytest.mark.asyncio
async def test_demo_root_cause_analysis():
    """Test demo root-cause analysis returns evidence and actions."""
    from manugent.connector.demo import DemoMESConnector

    connector = DemoMESConnector()
    await connector.connect()
    result = await connector.execute_tool(
        "analyze_root_cause",
        {"issue_type": "yield_drop", "context": {"line_id": "SMT-03"}},
    )

    assert result.success
    assert result.data["confidence"] > 0
    assert len(result.data["evidence"]) >= 3
    assert len(result.data["recommended_actions"]) >= 1


def test_rest_connector_path_params_mapping():
    """Test REST connector maps path parameters for templated URLs."""
    from manugent.connector.base import MESConnectionConfig
    from manugent.connector.rest import RestConnector

    connector = RestConnector(MESConnectionConfig(mes_type="rest", base_url="http://mes/api"))
    mapping = connector.endpoint_map["get_equipment_status"]
    assert mapping["path"] == "/equipment/{equipment_id}/status"
    assert mapping["param_map"]["equipment_id"] == "equipment_id"


def test_rest_connector_loads_yaml_mapping(tmp_path):
    """Test REST connector can load endpoint mapping from YAML."""
    from manugent.connector.base import MESConnectionConfig
    from manugent.connector.rest import RestConnector

    mapping_path = tmp_path / "rest-mapping.yaml"
    mapping_path.write_text(
        """
tools:
  query_production_data:
    method: GET
    path: /api/kpi
    param_map:
      line_id: lineCode
      metric: metricCode
    response_path: result.data
""",
        encoding="utf-8",
    )
    connector = RestConnector(
        MESConnectionConfig(
            mes_type="rest",
            base_url="http://mes/api",
            extra={"endpoint_mapping_path": str(mapping_path)},
        )
    )

    mapping = connector.endpoint_map["query_production_data"]
    assert mapping["path"] == "/api/kpi"
    assert mapping["param_map"]["line_id"] == "lineCode"
    assert connector.endpoint_map["query_wip"]["path"] == "/production/wip"


def test_agent_response():
    """Test AgentResponse dataclass."""
    from manugent.agent.core import AgentResponse

    response = AgentResponse(
        content="3号线OEE今天是85.2%",
        tool_calls=[{"tool": "query_production_data", "args": {}}],
    )
    assert "85.2%" in response.content
    assert len(response.tool_calls) == 1
    assert str(response) == response.content


def test_memory_context_builder_groups_layers():
    """Test memory context includes relevant factory and incident memories."""
    from manugent.memory import InMemoryMemoryStore, MemoryContextBuilder
    from manugent.memory.recipes import remember_factory_fact, remember_incident

    store = InMemoryMemoryStore()
    remember_factory_fact(
        store,
        "SMT-03 uses solder paste lot tracking for yield investigations.",
        tags=["SMT-03", "yield"],
    )
    remember_incident(
        store,
        "Previous SMT-03 yield drop was linked to nozzle pickup alarms.",
        tags=["SMT-03", "yield"],
    )

    context = MemoryContextBuilder(store).build_context("SMT-03 yield", scope="default")

    assert "semantic" in context
    assert "episodic" in context
    assert "solder paste" in context
    assert "nozzle pickup" in context


@pytest.mark.asyncio
async def test_agent_query_writes_audit_memory():
    """Test direct tool queries write audit memories when memory is configured."""
    from manugent.agent.core import MESAgent
    from manugent.connector.demo import DemoMESConnector
    from manugent.memory import InMemoryMemoryStore, MemoryLayer

    class DummyLLM:
        async def ainvoke(self, *args, **kwargs):  # pragma: no cover
            raise AssertionError("query() should not invoke the LLM")

    store = InMemoryMemoryStore()
    connector = DemoMESConnector()
    await connector.connect()
    agent = MESAgent(
        llm=DummyLLM(),
        connector=connector,
        memory_store=store,
        memory_scope="factory-a",
    )

    result = await agent.query("query_wip", {"line_id": "SMT-03"})
    audit = store.search(layer=MemoryLayer.AUDIT, scope="factory-a")

    assert result.success
    assert len(audit) == 1
    assert audit[0].metadata["tool_name"] == "query_wip"


@pytest.mark.asyncio
async def test_agent_query_requires_approval_for_action_tools():
    """Test direct queries do not execute approval-required action tools."""
    from manugent.agent.core import MESAgent
    from manugent.connector.demo import DemoMESConnector
    from manugent.security import ApprovalQueue

    class DummyLLM:
        async def ainvoke(self, *args, **kwargs):  # pragma: no cover
            raise AssertionError("query() should not invoke the LLM")

    approvals = ApprovalQueue()
    connector = DemoMESConnector()
    await connector.connect()
    agent = MESAgent(
        llm=DummyLLM(),
        connector=connector,
        approval_queue=approvals,
        approval_session_id="shift-a",
    )

    result = await agent.query("suggest_schedule", {"line_ids": ["SMT-03"]})
    pending = approvals.list_pending("shift-a")

    assert result.success
    assert result.data["status"] == "needs_approval"
    assert result.data["approval_request_id"] == pending[0].request_id
    assert pending[0].tool_name == "suggest_schedule"


@pytest.mark.asyncio
async def test_root_cause_workflow_evidence_chain():
    """Test deterministic RCA workflow returns typed evidence and actions."""
    from manugent.connector.demo import DemoMESConnector
    from manugent.memory import InMemoryMemoryStore
    from manugent.memory.recipes import remember_incident
    from manugent.models import EvidenceType
    from manugent.workflows import RootCauseWorkflow

    memory = InMemoryMemoryStore()
    remember_incident(
        memory,
        "Previous SMT-03 yield drop was linked to MOUNTER-03A nozzle pickup alarms.",
        tags=["SMT-03", "yield"],
    )
    connector = DemoMESConnector()
    await connector.connect()
    workflow = RootCauseWorkflow(connector, memory_store=memory)

    report = await workflow.analyze_yield_drop("SMT-03")
    evidence_types = {item.evidence_type for item in report.evidence}

    assert report.incident_type == "yield_drop"
    assert report.confidence > 0.5
    assert EvidenceType.PRODUCTION in evidence_types
    assert EvidenceType.QUALITY in evidence_types
    assert EvidenceType.MATERIAL in evidence_types
    assert EvidenceType.EQUIPMENT in evidence_types
    assert EvidenceType.MEMORY in evidence_types
    assert any(item.requires_approval for item in report.recommendations)
    assert "良率下降" in report.finding
    assert any("当前良率" in item.summary for item in report.evidence)
    assert any("隔离物料批次" in item.action for item in report.recommendations)


@pytest.mark.asyncio
async def test_root_cause_workflow_persists_report_memory():
    """Test RCA workflow writes completed reports into episodic memory."""
    from manugent.connector.demo import DemoMESConnector
    from manugent.memory import InMemoryMemoryStore, MemoryLayer
    from manugent.workflows import RootCauseWorkflow

    memory = InMemoryMemoryStore()
    connector = DemoMESConnector()
    await connector.connect()
    workflow = RootCauseWorkflow(
        connector,
        memory_store=memory,
        memory_scope="factory-a",
    )

    report = await workflow.analyze_yield_drop("SMT-03")
    records = memory.search(
        "SMT-03 yield",
        layer=MemoryLayer.EPISODIC,
        scope="factory-a",
        limit=5,
    )

    persisted = next(record for record in records if "incident_report" in record.tags)
    assert persisted.metadata["report"]["line_id"] == "SMT-03"
    assert persisted.metadata["evidence_count"] == len(report.evidence)
    assert persisted.confidence == report.confidence


@pytest.mark.asyncio
async def test_langgraph_root_cause_workflow_steps():
    """Test LangGraph RCA workflow keeps orchestration steps explicit."""
    pytest.importorskip("langgraph")

    from manugent.connector.demo import DemoMESConnector
    from manugent.models import EvidenceType
    from manugent.workflows import LangGraphRootCauseWorkflow

    connector = DemoMESConnector()
    await connector.connect()
    workflow = LangGraphRootCauseWorkflow(connector)

    report = await workflow.analyze_yield_drop("SMT-03")
    evidence_types = {item.evidence_type for item in report.evidence}

    assert workflow.last_steps == [
        "query_production",
        "query_quality",
        "query_equipment",
        "build_evidence",
        "build_report",
    ]
    assert report.incident_type == "yield_drop"
    assert EvidenceType.PRODUCTION in evidence_types
    assert EvidenceType.QUALITY in evidence_types
    assert EvidenceType.EQUIPMENT in evidence_types


def test_sqlite_memory_store_persists_records(tmp_path):
    """Test SQLite memory persists records across store instances."""
    from manugent.memory import MemoryLayer, SQLiteMemoryStore
    from manugent.memory.recipes import remember_factory_fact

    db_path = tmp_path / "memory.sqlite3"
    store = SQLiteMemoryStore(db_path)
    remember_factory_fact(
        store,
        "SMT-03 requires solder paste lot checks during yield RCA.",
        scope="factory-a",
        tags=["SMT-03", "yield"],
    )

    reopened = SQLiteMemoryStore(db_path)
    records = reopened.search("SMT-03 yield", layer=MemoryLayer.SEMANTIC, scope="factory-a")

    assert len(records) == 1
    assert records[0].content.startswith("SMT-03 requires")


def test_session_manager_isolates_agent_history():
    """Test session manager creates independent agent histories."""
    from manugent.agent.session import AgentSessionManager
    from manugent.connector.demo import DemoMESConnector

    class DummyLLM:
        pass

    manager = AgentSessionManager(
        llm_factory=DummyLLM,
        connector_factory=DemoMESConnector,
    )

    session_a = manager.get("a")
    session_b = manager.get("b")
    session_a._history.append("a-only")

    assert session_a is manager.get("a")
    assert session_b is manager.get("b")
    assert session_a is not session_b
    assert session_b.history == []
    assert manager.count() == 2
    assert manager.clear("a") is True
    assert manager.count() == 1


def test_optional_bearer_token_verification():
    """Test minimal API token guard helper."""
    from manugent.security import verify_bearer_token

    assert verify_bearer_token(None, "") is True
    assert verify_bearer_token("Bearer secret", "secret") is True
    assert verify_bearer_token("Bearer wrong", "secret") is False
    assert verify_bearer_token("Basic secret", "secret") is False


def test_approval_queue_lifecycle():
    """Test approval queue submit/list/decide lifecycle."""
    from manugent.security import (
        ApprovalDecision,
        ApprovalQueue,
        ApprovalRequest,
        ApprovalStatus,
    )

    queue = ApprovalQueue()
    request = queue.submit(
        ApprovalRequest(
            tool_name="suggest_schedule",
            params={"line_ids": ["SMT-03"]},
            safety_level="approval",
            session_id="shift-a",
        )
    )

    assert queue.get(request.request_id) is request
    assert queue.list_pending("shift-a") == [request]

    updated = queue.decide(
        ApprovalDecision(
            request_id=request.request_id,
            approved=False,
            reason="Need supervisor review",
        )
    )

    assert updated is not None
    assert updated.status == ApprovalStatus.REJECTED
    assert queue.list_pending("shift-a") == []
