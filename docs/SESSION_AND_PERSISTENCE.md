# 会话隔离与持久化

ManuGent 将运行时会话状态和可持久化 memory 分开处理。

## 为什么重要

MES Agent 会被班长、质量工程师、设备工程师和管理者同时使用。不同角色的对话上下文不能互相串线，但历史异常、工厂事实和审计记录又需要沉淀下来。

因此 API 使用：

```text
session_id -> isolated MESAgent -> isolated conversation history
session_id -> memory scope -> durable audit/memory records
```

## Session Manager

实现位置：

```text
src/manugent/agent/session.py
```

`AgentSessionManager` 为每个 `session_id` 创建独立 `MESAgent`。

```python
manager.get("quality-shift-a")  # independent history
manager.get("equipment-shift-b")  # independent history
```

请求不传 `session_id` 时使用 `default`。

## SQLite Memory Store

实现位置：

```text
src/manugent/memory/sqlite.py
```

SQLite backend 存储：

- `record_id`
- `layer`
- `scope`
- `content`
- `tags`
- `metadata`
- `policy`
- `confidence`
- timestamps

默认路径：

```text
data/manugent-memory.sqlite3
```

可通过环境变量覆盖：

```bash
MEMORY_DB_PATH=/path/to/manugent-memory.sqlite3
```

运行演示：

```bash
PYTHONPATH=src python3 examples/demo_sqlite_memory.py
```

## Workflow Report Persistence

RCA workflow 完成后会把报告写入 episodic memory：

```text
yield_drop report -> MemoryLayer.EPISODIC -> tags: incident_report / line_id / yield
```

这样下一次分析同一条产线时，workflow 会把历史 RCA 报告作为 memory evidence 纳入证据链。

持久化内容包括：

- 报告结论和置信度
- 完整 `report.to_dict()` 元数据
- evidence 数量
- recommendation 数量
- memory scope

## API 行为

`POST /chat` accepts:

```json
{
  "session_id": "morning-shift",
  "message": "SMT-03 今天良率为什么下降？"
}
```

`POST /query` accepts:

```json
{
  "session_id": "morning-shift",
  "tool": "query_wip",
  "params": {"line_id": "SMT-03"}
}
```

`POST /chat/clear?session_id=morning-shift` clears one session.

## 当前限制

- Session state 仍在进程内，多副本部署需要共享 session backend。
- SQLite search 是关键词检索，不是向量检索。
- Memory scope 当前偏 session 维度，后续应扩展 `factory_id`、`line_id`、`role`、`user_id`。
- API authentication 仍是后续增强项。
