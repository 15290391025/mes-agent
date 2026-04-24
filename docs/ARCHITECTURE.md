# ManuGent Architecture Design

## System Overview

ManuGent follows a **layered, non-invasive** architecture that sits on top of existing MES/ERP/QMS systems.

---

## Layer 1: Protocol Layer — MCP Manufacturing Extension

### Why MCP?

Model Context Protocol (Anthropic's open standard) provides standardized agent-to-tool communication. We extend it with manufacturing-specific tool definitions.

### Manufacturing Tool Registry

```yaml
# mcp-tools/manufacturing.yaml
tools:
  # === Production Query ===
  query_production_data:
    description: "Query production metrics (output, yield, OEE, cycle time)"
    parameters:
      line_id: {type: string, required: true}
      metric: {type: enum, values: [oee, yield, output, cycle_time, throughput]}
      time_range: {type: string, default: "today"}
      granularity: {type: enum, values: [hourly, shift, daily], default: "hourly"}
    returns: timeseries_data

  query_wip:
    description: "Query work-in-progress status across stations"
    parameters:
      line_id: {type: string}
      product_id: {type: string}
      station: {type: string}
    returns: wip_list

  # === Equipment ===
  get_equipment_status:
    description: "Get real-time equipment status"
    parameters:
      equipment_id: {type: string, required: true}
    returns: {status, uptime, last_maintenance, alerts}

  get_equipment_history:
    description: "Get equipment alarm and maintenance history"
    parameters:
      equipment_id: {type: string, required: true}
      days: {type: integer, default: 30}
    returns: event_list

  # === Quality ===
  get_quality_records:
    description: "Query quality inspection records"
    parameters:
      line_id: {type: string}
      defect_type: {type: string}
      time_range: {type: string, default: "24h"}
    returns: quality_records

  get_traceability:
    description: "Full traceability chain for a product/serial number"
    parameters:
      serial_number: {type: string, required: true}
    returns: traceability_chain

  # === Analysis (Agent-initiated) ===
  analyze_root_cause:
    description: "Trigger root cause analysis for a quality/equipment issue"
    parameters:
      issue_type: {type: enum, values: [yield_drop, equipment_failure, quality_anomaly]}
      context: {type: object}
    returns: root_cause_report  # Requires human approval before action

  # === Actions (require human approval) ===
  suggest_schedule:
    description: "Generate optimized production schedule"
    parameters:
      line_ids: {type: array}
      horizon: {type: string, default: "24h"}
      constraints: {type: object}
    returns: schedule_proposal  # Always advisory, never auto-execute

  create_alert:
    description: "Create an alert/notification"
    parameters:
      severity: {type: enum, values: [info, warning, critical]}
      message: {type: string}
      assignee: {type: string}
    returns: alert_id
```

### Security Model

```
READ operations:     Auto-approved (query_*, get_*, analyze_*)
WRITE operations:    Human-in-the-loop (suggest_*, create_*)
DANGEROUS operations: Never allowed (delete, shutdown, override safety)
```

---

## Layer 2: Connector Framework

### Architecture

```python
# Abstract connector interface
class MESConnector(ABC):
    """Base class for all MES connectors."""

    @abstractmethod
    async def query(self, tool_name: str, params: dict) -> dict:
        """Execute a read query against MES."""
        pass

    @abstractmethod
    async def get_schema(self) -> MESchema:
        """Return MES data schema for LLM context."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify MES connection."""
        pass
```

### Built-in Connectors

| Connector | Target | Protocol | Status |
|-----------|--------|----------|--------|
| `RestConnector` | Any MES with REST API | REST | Phase 1 |
| `GraphQLConnector` | Any MES with GraphQL | GraphQL | Phase 1 |
| `SiemensConnector` | Opcenter | REST + OPC UA | Phase 2 |
| `DigiwinConnector` | 鼎捷MES | REST | Phase 2 |
| `MqttConnector` | Custom IoT/MES | MQTT | Phase 2 |
| `OpcUaConnector` | Industrial PLCs | OPC UA | Phase 3 |
| `SqlConnector` | Legacy MES (read DB) | SQL | Phase 3 |

### Connector Configuration

```yaml
# configs/connectors.yaml
connectors:
  mes_primary:
    type: rest
    base_url: ${MES_API_URL}
    auth:
      type: bearer
      token: ${MES_API_TOKEN}
    mappings:
      # Map MES API to MCP tool responses
      query_production_data:
        endpoint: /api/v1/production/metrics
        params_map:
          line_id: line
          metric: kpi
          time_range: period
        response_map:
          data: result.data
          timestamp: result.time
    rate_limit: 100/minute
    timeout: 30s
```

---

## Layer 3: Agent Orchestration

### Agent Architecture (LangGraph)

```python
from langgraph.graph import StateGraph, END

class FactoryAgentState(TypedDict):
    messages: list[BaseMessage]
    mes_data: dict
    analysis: dict
    plan: list[str]
    human_approval_needed: bool

# Agent graph
graph = StateGraph(FactoryAgentState)

# Nodes
graph.add_node("understand", understand_intent)      # Parse user query
graph.add_node("query_mes", query_mes_data)           # Fetch relevant data
graph.add_node("analyze", analyze_with_llm)           # LLM analysis
graph.add_node("root_cause", root_cause_analysis)     # Deep dive if needed
graph.add_node("format_response", format_response)    # Format for user
graph.add_node("human_review", human_review_node)     # Approval gate

# Edges
graph.add_edge("understand", "query_mes")
graph.add_conditional_edges("query_mes", route_by_intent, {
    "simple_query": "format_response",
    "analysis": "analyze",
    "root_cause": "root_cause",
    "action": "human_review",
})
graph.add_edge("analyze", "format_response")
graph.add_edge("root_cause", "format_response")
graph.add_edge("human_review", "format_response")
graph.add_edge("format_response", END)

# Entry
graph.set_entry_point("understand")
```

### Specialized Agents

| Agent | Role | Model | Tools |
|-------|------|-------|-------|
| Query Agent | NL → MES query | Qwen2.5-72B | query_*, get_* |
| Alert Agent | Real-time monitoring | Qwen2.5-7B (fast) | get_*, create_alert |
| RootCause Agent | Correlation analysis | Claude 3.5 / GPT-4o | analyze_*, get_* |
| Schedule Agent | Optimization | Qwen2.5-72B | suggest_*, query_* |
| Supervisor | Route & orchestrate | Claude 3.5 | All tools |

---

## Layer 4: Edge Runtime

### Why Edge?

Factory networks are:
- Often air-gapped or restricted
- Latency-sensitive (sub-second decisions needed)
- Data sovereignty requirements (can't send to cloud)

### Architecture

```
┌─────────────────────────────────────┐
│          Edge Node (Factory)        │
│                                     │
│  ┌──────────┐  ┌─────────────────┐ │
│  │ Ollama   │  │ ManuGent Edge   │ │
│  │ (LLM)    │◄─┤ Runtime         │ │
│  │          │  │                 │ │
│  │ Qwen2.5  │  │ - Agent exec    │ │
│  │ 7B/72B   │  │ - MCP server    │ │
│  └──────────┘  │ - Connector hub │ │
│                │ - Local cache   │ │
│                └────────┬────────┘ │
│                         │          │
│  ┌──────────────────────▼────────┐ │
│  │     Local Data Store          │ │
│  │  (SQLite + Parquet files)     │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
                    │
            (Optional cloud sync)
                    │
          ┌─────────▼─────────┐
          │   Cloud Backend   │
          │  (Larger models,  │
          │   analytics)      │
          └───────────────────┘
```

### Model Selection

| Scenario | Model | Size | Latency | Use Case |
|----------|-------|------|---------|----------|
| Fast response | Qwen2.5-7B | ~4GB | <1s | Simple queries, alerts |
| Standard | Qwen2.5-32B | ~18GB | <3s | Analysis, root cause |
| Complex | Qwen2.5-72B | ~40GB | <10s | Scheduling, optimization |
| Cloud fallback | Claude 3.5 / GPT-4o | API | ~3s | Complex reasoning |

---

## Layer 5: Memory System

ManuGent uses a ChatGPT-inspired memory design, adapted to manufacturing
operations. ChatGPT-style memory separates short-lived conversation context,
durable remembered facts/preferences, and project-scoped history. ManuGent maps
that idea to MES concepts where context must be scoped by factory, line, role,
and safety level.

### Memory Layers

| Layer | Purpose | MES examples | Current implementation |
|-------|---------|--------------|------------------------|
| Session | Current conversation context | Follow-up questions in a shift chat | `MESAgent._history` |
| Episodic | Past events and cases | Yield drop incidents, RCA conclusions, corrective actions | `MemoryLayer.EPISODIC` |
| Semantic | Stable factory knowledge | Line layout, SOP rules, material rules, equipment metadata | `MemoryLayer.SEMANTIC` |
| Preference | User or role preferences | Report language, KPI format, manager/operator detail level | `MemoryLayer.PREFERENCE` |
| Audit | Governance trace | Tool, params, safety level, result summary, approval status | `MemoryLayer.AUDIT` |

### Design Principles

1. **Scoped memory**: memories are scoped by factory/project so one plant does not
   leak context into another.
2. **Provenance first**: every memory has layer, policy, confidence, tags, and
   metadata.
3. **Audit is not optional**: tool calls are remembered as audit records even
   when the model response is not stored.
4. **Human control**: explicit memories and future persistent backends must
   support deletion/forgetting.
5. **Prompt budget aware**: `MemoryContextBuilder` retrieves compact relevant
   memory instead of dumping all history into the prompt.

### Current Code

```text
src/manugent/memory/base.py       # MemoryRecord, MemoryLayer, MemoryStore protocol
src/manugent/memory/in_memory.py  # deterministic demo/test backend
src/manugent/memory/context.py    # prompt context retrieval and formatting
src/manugent/memory/recipes.py    # factory fact, incident, preference, audit helpers
```

`MESAgent` accepts an optional memory store:

```python
from manugent.agent.core import MESAgent
from manugent.memory import InMemoryMemoryStore

memory = InMemoryMemoryStore()
agent = MESAgent(
    llm=llm,
    connector=connector,
    memory_store=memory,
    memory_scope="factory-a",
)
```

When memory is configured:

- relevant semantic, episodic, preference, and audit memories are added to the
  system context for each chat turn
- direct `query()` calls and LLM tool calls write audit memories
- `forget(record_id)` can remove an individual memory from the store

### Future Persistent Backends

| Backend | Use |
|---------|-----|
| SQLite | Local edge node memory and audit trail |
| PostgreSQL | Multi-user server memory, RBAC, audit retention |
| Vector DB / pgvector | Semantic retrieval over incidents, SOPs, and reports |
| Object storage | Long RCA reports, attachments, exported MES evidence |

---

## Layer 6: Data & Governance

### ISA-95 Data Model

```python
# Core entities aligned with ISA-95
class ProductionLine:
    """ISA-95 Level 1-2: Equipment module"""
    id: str
    name: str
    type: str  # "smt", "assembly", "test", "packaging"
    status: str  # "running", "idle", "maintenance", "error"
    equipment: list[Equipment]

class WorkOrder:
    """ISA-95 Level 3: Production order"""
    id: str
    product_id: str
    quantity: int
    status: str  # "pending", "in_progress", "completed"
    line_id: str
    scheduled_start: datetime
    actual_start: datetime | None

class QualityRecord:
    """Quality inspection result"""
    id: str
    serial_number: str
    work_order_id: str
    result: str  # "pass", "fail", "rework"
    defect_codes: list[str]
    inspector: str
    timestamp: datetime
```

### Governance Framework

Based on Digital Twin Consortium's Industrial AI Agent Manifesto:

```yaml
governance:
  # Law 1: Agents must be constrained by digital twin models
  constraint_validation:
    enabled: true
    twin_model: configs/digital_twin.yaml
    reject_if_violates: true

  # Law 2: All agent actions must be auditable
  audit:
    enabled: true
    storage: postgresql
    retention_days: 365
    log_level: all_actions  # query, analysis, recommendation, execution

  # Law 3: Human override always available
  human_in_the_loop:
    required_for: [create_work_order, modify_schedule, override_quality]
    timeout: 300s  # Auto-reject if no human response in 5min
    escalation: notify_supervisor

  # Law 4: Explainability required
  explainability:
    always_explain: true
    include_confidence: true
    include_data_sources: true
```

---

## Deployment Architecture

### Single Factory

```yaml
# docker-compose.yaml (simplified)
services:
  manugent-core:
    image: manugent/core:latest
    volumes:
      - ./configs:/app/configs
    ports:
      - "8000:8000"  # API
      - "8001:8001"  # MCP server

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  postgres:
    image: timescale/timescaledb:latest
    volumes:
      - pg-data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  web-ui:
    image: manugent/web:latest
    ports:
      - "3000:3000"
```

### Multi-Factory (Phase 4)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Factory A   │  │  Factory B   │  │  Factory C   │
│  (Edge Node) │  │  (Edge Node) │  │  (Edge Node) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                ┌────────▼────────┐
                │  Cloud Hub      │
                │  - Federation   │
                │  - Cross-factory│
                │    analytics    │
                │  - Model updates│
                └─────────────────┘
```

---

## API Design

### REST API Endpoints

```
POST   /api/v1/chat                    # Natural language query
POST   /api/v1/query                   # Structured query
GET    /api/v1/production/{line_id}    # Production metrics
GET    /api/v1/equipment/{id}/status   # Equipment status
GET    /api/v1/quality/records         # Quality records
POST   /api/v1/analysis/root-cause     # Trigger RCA
POST   /api/v1/schedule/suggest        # Schedule suggestion
GET    /api/v1/alerts                  # Active alerts
GET    /api/v1/audit/log               # Audit trail

# MCP endpoint for agent-to-agent communication
POST   /mcp/v1/tools/call              # MCP tool invocation
GET    /mcp/v1/tools/list              # List available tools
```

### WebSocket Events

```
ws://host/ws/v1/events

Events:
  - production.update    # Real-time production data
  - equipment.alert      # Equipment alarm
  - quality.anomaly      # Quality deviation detected
  - agent.response       # Agent chat response (streaming)
  - schedule.proposal    # New schedule suggestion
```
