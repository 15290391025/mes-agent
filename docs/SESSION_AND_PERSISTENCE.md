# Session Isolation and Persistence

ManuGent now separates runtime session state from durable memory.

## Why It Matters

An MES Agent may be used by production supervisors, quality engineers, equipment
engineers, and managers at the same time. Their conversations must not share
private context by accident.

The API therefore uses:

```text
session_id -> isolated MESAgent -> isolated conversation history
session_id -> memory scope -> durable audit/memory records
```

## Session Manager

Implemented in:

```text
src/manugent/agent/session.py
```

`AgentSessionManager` creates one `MESAgent` per `session_id`.

```python
manager.get("quality-shift-a")  # independent history
manager.get("equipment-shift-b")  # independent history
```

If a request omits `session_id`, it uses `default`.

## SQLite Memory Store

Implemented in:

```text
src/manugent/memory/sqlite.py
```

The SQLite backend stores:

- `record_id`
- `layer`
- `scope`
- `content`
- `tags`
- `metadata`
- `policy`
- `confidence`
- timestamps

Default path:

```text
data/manugent-memory.sqlite3
```

Override with:

```bash
MEMORY_DB_PATH=/path/to/manugent-memory.sqlite3
```

Run the demo:

```bash
PYTHONPATH=src python3 examples/demo_sqlite_memory.py
```

## API Behavior

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

## Current Limitations

- Session state is in-process; multiple API replicas need a shared session backend.
- SQLite search is keyword-based, not vector retrieval.
- Memory scopes are session-oriented today; future versions should include
  `factory_id`, `line_id`, `role`, and `user_id`.
- API authentication is still a next milestone.
