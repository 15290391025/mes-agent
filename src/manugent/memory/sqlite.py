"""SQLite-backed memory store."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from manugent.memory.base import MemoryLayer, MemoryRecord, MemoryWritePolicy


class SQLiteMemoryStore:
    """Persistent memory store backed by SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def add(self, record: MemoryRecord) -> MemoryRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memory_records (
                    record_id, layer, scope, content, tags, metadata, policy,
                    confidence, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.layer.value,
                    record.scope,
                    record.content,
                    json.dumps(record.tags, ensure_ascii=False),
                    json.dumps(record.metadata, ensure_ascii=False),
                    record.policy.value,
                    record.confidence,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ),
            )
        return record

    def search(
        self,
        query: str = "",
        *,
        layer: MemoryLayer | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        sql = "SELECT * FROM memory_records"
        clauses: list[str] = []
        params: list[Any] = []

        if layer:
            clauses.append("layer = ?")
            params.append(layer.value)
        if scope:
            clauses.append("scope = ?")
            params.append(scope)
        if query:
            terms = query.lower().split()
            for term in terms:
                clauses.append(
                    "(lower(content) LIKE ? OR lower(tags) LIKE ? OR lower(metadata) LIKE ?)"
                )
                like = f"%{term}%"
                params.extend([like, like, like])

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit * 5 if tags else limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        records = [self._row_to_record(row) for row in rows]
        if tags:
            wanted = set(tags)
            records = [record for record in records if wanted.issubset(set(record.tags))]
        return records[:limit]

    def forget(self, record_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM memory_records WHERE record_id = ?",
                (record_id,),
            )
        return cursor.rowcount > 0

    def clear_scope(self, scope: str) -> int:
        """Delete all memory records for a scope."""
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM memory_records WHERE scope = ?", (scope,))
        return cursor.rowcount

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    record_id TEXT PRIMARY KEY,
                    layer TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    policy TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memory_layer_scope
                ON memory_records(layer, scope, updated_at)
                """
            )

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            record_id=row["record_id"],
            layer=MemoryLayer(row["layer"]),
            scope=row["scope"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
            policy=MemoryWritePolicy(row["policy"]),
            confidence=float(row["confidence"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
