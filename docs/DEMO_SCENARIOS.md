# ManuGent Demo Scenarios

This project is designed to demonstrate MES + Agent thinking, not just a chatbot
wrapper. The built-in `demo` connector simulates an SMT factory so every scenario
can run without access to a private MES.

## 1. Yield Drop Root-Cause Analysis

User question:

```text
SMT-03 最近 24 小时良率为什么下降？
```

Agent reasoning path:

1. Query yield and OEE trend for `SMT-03`.
2. Query quality records and group defects by type and material lot.
3. Query equipment history for related mounter alarms.
4. Return a hypothesis with evidence and recommended actions.

Run:

```bash
PYTHONPATH=src python3 examples/demo_root_cause.py
```

What this demonstrates:

- MES data is queried through explicit tools, not free-form SQL.
- Root-cause analysis links production, quality, material, and equipment data.
- Recommendations remain advisory and do not write back to MES.

## 2. Product Traceability

User question:

```text
SN202604240031 这台产品经历了哪些工序？有没有异常？
```

Agent reasoning path:

1. Query the traceability chain by serial number.
2. Show order, product, material lots, route, equipment, operators, and checks.
3. Highlight failed quality checks and disposition.

Run:

```bash
PYTHONPATH=src python3 examples/demo_traceability.py
```

What this demonstrates:

- MES traceability is modeled as a first-class workflow.
- Agent output can cite concrete route and quality records.
- The project understands manufacturing genealogy, not just KPI dashboards.

## 3. Production Morning Report

User request:

```text
生成 SMT-03 今天早班生产日报。
```

Agent reasoning path:

1. Query yield, OEE, WIP, and quality records.
2. Summarize current state and top risks.
3. Include root-cause hypothesis and next actions.

Run:

```bash
PYTHONPATH=src python3 examples/demo_daily_report.py
```

What this demonstrates:

- Agent can compose multiple MES tools into an operations report.
- The output is suitable for shift handover or morning meeting context.
- The same protocol can back CLI, API, dashboard, or messaging interfaces.

## Safety Model

ManuGent classifies tools by manufacturing risk:

- `read_only`: Query data, auto-approved.
- `advisory`: Produce analysis or suggestions, no MES write-back.
- `approval`: Draft an action that requires human confirmation.
- `restricted`: Reserved for admin-only operations.

This is the key distinction between an industrial Agent and a generic chatbot:
factory operations need traceability, approval gates, and auditability.
