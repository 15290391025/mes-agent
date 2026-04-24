# MES Domain Model

ManuGent models MES as an execution system, not just a database behind a chat
interface. The Agent needs explicit manufacturing objects so it can reason over
production, quality, equipment, materials, and traceability.

## Core Objects

| Object | Why it matters to the Agent |
|--------|-----------------------------|
| `ProductionLine` | Defines where production happens and anchors KPI queries. |
| `WorkOrder` | Connects product, line, quantity, status, and due date. |
| `Equipment` | Explains downtime, alarms, maintenance, and process instability. |
| `MaterialLot` | Links defects to supplier, batch, and process windows. |
| `QualityRecord` | Provides defect evidence and inspection results. |
| `TraceabilityRecord` | Connects serial number, route, material lots, equipment, and operators. |
| `IncidentReport` | Captures root-cause findings, evidence, confidence, and actions. |
| `AuditEvent` | Records tool calls and approval boundaries for governance. |

The first implemented domain models live in:

```text
src/manugent/models/domain.py
```

## Why Domain Models Matter

Without domain models, a MES Agent is just a natural-language query wrapper.
With domain models, the Agent can:

- distinguish production evidence from quality evidence
- explain why a material lot is relevant to a yield drop
- trace a failed serial number through route, equipment, and inspection records
- decide whether an action is advisory or requires approval
- produce evidence chains that humans can review

## Current Scope

The current model layer is intentionally compact:

- `ProductionLine`
- `WorkOrder`
- `Evidence`
- `Recommendation`
- `IncidentReport`

Connectors can still return dictionaries for flexibility, while workflows use
typed models at the reasoning boundary. This keeps integration easy while making
Agent outputs more structured and inspectable.

## Next Extensions

- Add `Equipment`, `MaterialLot`, `QualityRecord`, and `TraceabilityRecord`
- Validate connector outputs with Pydantic or dataclass adapters
- Persist `IncidentReport` and `AuditEvent` into SQLite/PostgreSQL
- Add ISA-95 naming and hierarchy mapping for enterprise MES integrations
