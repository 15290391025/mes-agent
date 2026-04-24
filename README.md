# ManuGent - MES Agent Reference Architecture

> 一个面向制造业 MES 场景的 Agent 中间层参考实现，展示如何把生产执行数据、质量追溯、设备状态和工单流转变成 Agent 可安全调用的工具。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Status: Planning](https://img.shields.io/badge/status-planning-orange.svg)](https://github.com/15290391025/manugent)

[English](README.md) | [中文](README_zh.md)

---

## What is ManuGent?

ManuGent is a **MES + Agent portfolio project**. It is not trying to replace a MES. It demonstrates how an AI Agent layer can sit above existing MES/ERP/QMS systems and provide:

- Natural-language MES queries
- Production KPI and WIP analysis
- Product traceability
- Quality and equipment root-cause analysis
- Human-approved manufacturing actions
- Auditable tool calls for industrial governance

**Before ManuGent:**
> 工程师: 打开MES → 筛选产线 → 选日期 → 导出报表 → Excel分析 → 写报告 → 汇报

**With ManuGent:**
> 工程师: "3号线最近一周良率下降的原因是什么？"
> ManuGent: 分析数据 → 关联事件 → 给出根因 → 建议措施

The project ships with a built-in `DemoMESConnector`, so the MES Agent workflow can be demonstrated without access to a private factory system.

---

## What This Project Demonstrates

ManuGent is designed to show practical understanding of both MES and Agent systems:

| Capability | What it demonstrates |
|------------|----------------------|
| MES domain model | Lines, work orders, WIP, equipment, material lots, serial numbers, quality records, OEE, yield, traceability |
| Agent tool protocol | MES functions are exposed as typed tools instead of letting the LLM directly query arbitrary systems |
| Manufacturing reasoning | Deterministic root-cause workflow builds evidence from production, quality, material, equipment, and memory |
| Industrial safety | Read-only tools auto-run, advisory tools produce recommendations, write-like actions require approval |
| Memory architecture | ChatGPT-inspired memory layers adapted to MES: session, incidents, factory facts, preferences, audit |
| Connector abstraction | Demo and REST connectors share one tool interface, making real MES integration incremental |

## Why ManuGent?

| Problem | ManuGent Solution |
|---------|-------------------|
| MES数据需要手动查询导出 | 自然语言直接问，秒级响应 |
| 异常靠人工经验判断 | AI Agent实时监控+根因分析 |
| 多系统数据孤岛 | 统一Agent层打通MES/ERP/QMS |
| 排产靠Excel拍脑袋 | 智能排产建议，约束满足优化 |
| 培训新员工周期长 | AI助手降低MES使用门槛 |

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         User Interfaces             │
                    │   Chat │ Dashboard │ Mobile │ API    │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │       Agent Orchestration           │
                    │  (LangGraph / CrewAI / AutoGen)     │
                    │                                     │
                    │  ┌───────┐ ┌───────┐ ┌───────────┐ │
                    │  │Query  │ │Alert  │ │Schedule   │ │
                    │  │Agent  │ │Agent  │ │Agent      │ │
                    │  └───┬───┘ └───┬───┘ └─────┬─────┘ │
                    │      └─────────┼───────────┘       │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │      MCP Manufacturing Protocol     │
                    │  (Standardized Agent ↔ MES Bridge)  │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
    ┌─────▼─────┐          ┌──────▼──────┐          ┌──────▼──────┐
    │ MES       │          │ ERP         │          │ QMS/WMS/SCADA│
    │ Connector │          │ Connector   │          │ Connector    │
    │           │          │             │          │              │
    │ Siemens   │          │ SAP         │          │ OPC UA       │
    │ 鼎捷      │          │ Oracle      │          │ MQTT         │
    │ 摩尔元数   │          │ 用友/金蝶    │          │ Modbus       │
    │ 自研MES   │          │             │          │ REST/GraphQL │
    └───────────┘          └─────────────┘          └──────────────┘
```

### Key Design Principles

1. **Non-invasive**: Read-heavy first, write operations require explicit approval
2. **ISA-95 Compliant**: Data models follow ISA-95/Purdue model standards
3. **Edge-First**: Local LLM inference (Ollama/vLLM) with cloud fallback
4. **Multi-Agent**: Specialized agents for different concerns (query, alert, schedule)
5. **Memory-Aware**: Historical incidents, factory facts, user preferences, and audit events shape future answers
6. **Governance-First**: Audit trail, constraint validation, human-in-the-loop

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Agent Framework | LangGraph | Stateful multi-step reasoning, production-grade |
| LLM Backend | OpenAI / Claude / Qwen / Local (Ollama) | Flexibility, can run offline |
| Data Protocol | MCP (Model Context Protocol) | Standardized tool calling |
| OT Connectors | OPC UA / MQTT | Industry standard IoT protocols |
| Backend API | FastAPI (Python) | Async, fast, great for data pipelines |
| Database | PostgreSQL + TimescaleDB | Relational + time-series for sensor data |
| Cache | Redis | Real-time state, pub/sub |
| Memory | Layered memory store | Session context, incidents, factory knowledge, preferences, audit |
| Edge Runtime | Ollama / vLLM | On-premise LLM inference |
| Frontend | React + shadcn/ui | Chat interface + dashboards |

---

## Quick Start

The fastest demo path uses the built-in simulated SMT factory data.

```bash
# Clone
git clone https://github.com/15290391025/manugent.git
cd manugent

# Setup
cp configs/.env.example configs/.env
# Default config uses MES_TYPE=demo and Ollama for local inference.

# Run with Docker
docker compose up -d

# Or run locally
pip install -e .
manugent serve --config configs/.env
```

Run demo scenarios without any LLM or real MES:

```bash
PYTHONPATH=src python3 examples/demo_root_cause.py
PYTHONPATH=src python3 examples/demo_traceability.py
PYTHONPATH=src python3 examples/demo_daily_report.py
PYTHONPATH=src python3 examples/demo_memory.py
PYTHONPATH=src python3 examples/demo_workflow_root_cause.py
```

### Connect to your MES

```python
from langchain_openai import ChatOpenAI

from manugent import MESAgent
from manugent.connector import MESConnectionConfig, create_connector

connector = create_connector(
    MESConnectionConfig(
        mes_type="rest",
        base_url="https://your-mes.example.com/api",
        auth_type="bearer",
        auth_token="your-token",
    )
)

llm = ChatOpenAI(model="gpt-4o", api_key="your-key")
agent = MESAgent(llm=llm, connector=connector)

# Natural language query
response = await agent.chat("3号线今天OEE是多少？")
print(response)

# Structured query
result = await agent.query(
    "query_production_data",
    {"line_id": "SMT-03", "metric": "oee", "time_range": "today"},
)
```

## Demo Scenarios

See [DEMO_SCENARIOS.md](docs/DEMO_SCENARIOS.md) for detailed walkthroughs.

| Scenario | User question | Demonstrated capability |
|----------|---------------|-------------------------|
| Yield root cause | "SMT-03 最近 24 小时良率为什么下降？" | Links yield trend, defects, material lot, and equipment alarms |
| Traceability | "SN202604240031 这台产品经历了哪些工序？" | Shows route, equipment, operators, material lots, and quality result |
| Morning report | "生成 SMT-03 今天早班生产日报" | Composes KPI, WIP, quality, RCA, and actions into an operations report |
| Memory context | "SMT-03 yield" | Retrieves preferences, factory facts, incidents, and audit memories |
| Evidence chain | "SMT-03 yield drop RCA" | Runs deterministic workflow and outputs typed evidence + recommendations |

Core design docs:

- [MES_DOMAIN_MODEL.md](docs/MES_DOMAIN_MODEL.md)
- [ROOT_CAUSE_WORKFLOW.md](docs/ROOT_CAUSE_WORKFLOW.md)
- [DEMO_SCENARIOS.md](docs/DEMO_SCENARIOS.md)

## Memory Model

ManuGent adapts ChatGPT-style memory concepts to MES operations:

| Layer | ChatGPT analogy | MES Agent use |
|-------|-----------------|---------------|
| Session memory | Current conversation context | Active shift conversation and follow-up questions |
| Episodic memory | Past chat history | Historical incidents, root-cause hypotheses, corrective actions |
| Semantic memory | Stable remembered facts | Factory layout, line rules, SOPs, product routes, equipment metadata |
| Preference memory | Saved memories / instructions | User, role, and report-format preferences |
| Audit memory | Governance trace | Tool calls, parameters, safety level, result summaries, approvals |

The current implementation includes an in-memory backend and prompt context builder.
It is intentionally small so the architecture is easy to inspect, but the same
interface can be backed by SQLite, PostgreSQL, or vector search later.

---

## Use Cases

### Tier 1: Natural Language MES Query (MVP)
- "3号线最近一周的良率趋势"
- "今天有哪些设备需要保养？"
- "昨天夜班的产量为什么比白班低？"
- 自动生成每日生产晨会报告

### Tier 2: Intelligent Monitoring & Alerting
- 实时异常检测（传感器数据 + 生产指标）
- 良率波动根因分析（关联设备、物料、人员、环境）
- 预测性维护建议（基于设备运行数据趋势）

### Tier 3: Autonomous Operations
- 多约束条件下的智能排产
- 动态人员排班（技能匹配 + 负荷均衡）
- 物料需求预测与采购建议

### Tier 4: Cognitive Manufacturing (Roadmap)
- 跨工厂知识迁移
- 自适应工艺参数优化
- 合规自动化（客户审核、体系认证）

---

## Who Should Use This?

- **大型电子制造企业** (立讯精密、歌尔股份、比亚迪电子...)
  - 已有MES系统，需要AI增强
  - 多工厂、多产线协同需求
  - 客户（Apple/汽车）品质追溯要求高

- **MES系统集成商/ISV**
  - 给客户提供AI增值模块
  - 不想从零开发Agent能力

- **智能制造研究机构**
  - 探索LLM在工业场景的落地

---

## Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for detailed timeline.

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| Phase 1: Foundation | Month 1-2 | Core protocol, one MES connector, basic chat agent |
| Phase 2: Intelligence | Month 3-4 | Multi-agent system, alerting, root cause analysis |
| Phase 3: Operations | Month 5-6 | Scheduling agent, edge deployment, production-ready |
| Phase 4: Ecosystem | Month 7+ | Plugin marketplace, multi-MES federation, enterprise features |

---

## Current Status

ManuGent is an early reference implementation. The current vertical slice includes:

- Built-in demo MES connector with SMT factory data
- Generic REST MES connector
- MES domain models and deterministic root-cause workflow
- Manufacturing tool registry
- Layered memory module with in-memory backend and audit capture
- FastAPI server
- Typer CLI
- Docker Compose
- Demo scripts for root cause, traceability, and daily report workflows

Next milestones:

- Session isolation and API authentication
- Persistent memory backends: SQLite/PostgreSQL/vector retrieval
- Configurable REST field mappings
- LangGraph workflow for root-cause analysis
- Minimal dashboard for demo storytelling

---

## License

MIT License — use it however you want.

---

## Acknowledgments

- [Digital Twin Consortium](https://www.digitaltwinconsortium.org/) — Industrial AI Agent Manifesto
- [MCP Protocol](https://modelcontextprotocol.io/) — Standardized agent-tool communication
- AWS [industrial-data-store-simulation-chatbot](https://github.com/aws-samples/industrial-data-store-simulation-chatbot) — Reference architecture for MES chatbot
- All open-source MES projects that inspire this work
