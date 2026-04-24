# ManuGent - MES Agent 参考架构

> 面向制造业 MES 场景的 Agent 中间层示范项目。它展示如何把生产执行数据、质量追溯、设备状态、物料批次和工单流转，转化为 Agent 可安全调用、可解释、可审计的智能能力。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Status: Reference Architecture](https://img.shields.io/badge/status-reference_architecture-orange.svg)](https://github.com/15290391025/manugent)

## 1. 项目定位

ManuGent 不是要替代 MES，而是一个 **MES + Agent 能力背书项目**。

它回答的问题是：

> 如果一个工厂已经有 MES，如何在不破坏现有系统的前提下，让工程师、班长、质量和设备人员用自然语言查询、分析、追溯和复盘生产现场？

传统方式：

```text
打开 MES → 筛选产线 → 导出报表 → Excel 分析 → 找设备/质量记录 → 写报告
```

ManuGent 方式：

```text
问：SMT-03 最近 24 小时良率为什么下降？
答：查询良率趋势、品质缺陷、物料批次、设备告警、历史记忆 → 生成证据链和建议动作
```

## 2. 核心能力

| 能力 | 项目中如何体现 |
|------|----------------|
| MES 领域建模 | 产线、工单、WIP、设备、物料批次、质量记录、SN 追溯、OEE、良率 |
| Agent 工具协议 | MES 能力被封装成 typed tools，LLM 不直接访问数据库 |
| 根因分析工作流 | 确定性 RCA workflow 生成 production / quality / material / equipment / memory 证据链 |
| 记忆架构 | 参考 ChatGPT 记忆逻辑，映射为 session、incident、factory fact、preference、audit |
| 会话隔离 | API `session_id` 对应独立 Agent history 和 memory scope |
| 安全边界 | read-only 默认执行，approval/restricted 工具进入审批队列 |
| 审计能力 | 工具调用、参数、安全级别、结果摘要写入 audit memory |
| 可展示 Demo | Web 页面、API endpoint、CLI demo scripts 均可运行 |

## 3. 架构概览

```text
用户 / Web Demo / API
        │
        ▼
Session Manager ── Memory Store(SQLite)
        │                 │
        ▼                 ▼
MES Agent ─────── Audit / Incident / Preference Memory
        │
        ▼
Manufacturing Tool Protocol
        │
        ├── DemoMESConnector
        └── RestConnector
        │
        ▼
MES / ERP / QMS / 设备系统
```

核心原则：

- **不侵入 MES**：先读数据，写操作必须审批。
- **工具受控**：Agent 只能调用注册过的 MES tools。
- **证据优先**：回答必须能追溯到生产、质量、物料、设备或记忆证据。
- **记忆沉淀**：历史异常、工厂知识、用户偏好和审计记录可以影响后续分析。
- **企业安全兼容**：身份认证/RBAC 交给企业 SSO/API Gateway/MES 权限体系。

## 4. 快速体验

项目内置 `DemoMESConnector`，无需真实 MES 即可运行。

```bash
git clone https://github.com/15290391025/manugent.git
cd manugent

cp configs/.env.example configs/.env
pip install -e .
manugent serve --config configs/.env
```

打开：

```text
http://localhost:8000/
```

Web Demo 会调用：

```text
POST /workflows/root-cause/yield-drop
```

## 5. 不依赖 LLM 的演示脚本

这些脚本可以直接展示 MES Agent 的核心能力：

```bash
PYTHONPATH=src python3 examples/demo_workflow_root_cause.py
PYTHONPATH=src python3 examples/demo_traceability.py
PYTHONPATH=src python3 examples/demo_daily_report.py
PYTHONPATH=src python3 examples/demo_memory.py
PYTHONPATH=src python3 examples/demo_sqlite_memory.py
```

## 6. API 示例

### 根因分析 Workflow

```bash
curl -X POST http://localhost:8000/workflows/root-cause/yield-drop \\
  -H "Content-Type: application/json" \\
  -d '{"line_id":"SMT-03","time_range":"24h","session_id":"demo"}'
```

返回结构包含：

- `finding`
- `confidence`
- `evidence`
- `recommendations`

### 工具调用

```bash
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"tool":"query_wip","params":{"line_id":"SMT-03"},"session_id":"demo"}'
```

### 审批队列

```bash
curl http://localhost:8000/approvals
```

## 7. 关键文档

- [项目故事：为什么需要 MES Agent](docs/PROJECT_STORY_ZH.md)
- [MES 领域模型](docs/MES_DOMAIN_MODEL.md)
- [根因分析工作流](docs/ROOT_CAUSE_WORKFLOW.md)
- [记忆、会话和持久化](docs/SESSION_AND_PERSISTENCE.md)
- [Agent 安全边界](docs/SECURITY_MODEL.md)
- [Demo 场景说明](docs/DEMO_SCENARIOS.md)

## 8. 当前完成度

已实现：

- Demo MES 数据源
- 通用 REST connector
- Manufacturing tool registry
- Domain models
- Root Cause Workflow
- Evidence Chain
- Memory model
- SQLite memory persistence
- Session isolation
- Audit memory
- Optional API token
- Approval queue skeleton
- Workflow API endpoint
- Minimal Web Demo

仍可继续增强：

- REST connector YAML mapping
- Approval 通过后的动作执行
- Approval 持久化
- LangGraph 编排版本
- 更完整的 Web UI
- CI 运行所有 demo scripts

## 9. License

MIT License.
