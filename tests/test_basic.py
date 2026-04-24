"""Basic tests for ManuGent."""

import pytest


def test_version():
    """Test version import."""
    import manugent
    assert manugent.__version__ == "0.1.0"


def test_tool_registry():
    """Test MCP tool registration."""
    from manugent.protocol.tools import list_tools, ToolCategory, SafetyLevel

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
