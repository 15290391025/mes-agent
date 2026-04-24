"""In-memory memory store.

This backend is intentionally simple and deterministic. It is suitable for
tests, demos, and documenting the memory contract before adding SQLite,
PostgreSQL, or vector retrieval backends.
"""

from __future__ import annotations

from manugent.memory.base import MemoryLayer, MemoryRecord


class InMemoryMemoryStore:
    """Simple list-backed memory store."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self._records.append(record)
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
        matches = [
            record
            for record in self._records
            if record.matches(query=query, layer=layer, scope=scope, tags=tags)
        ]
        matches.sort(key=lambda record: record.updated_at, reverse=True)
        return matches[:limit]

    def forget(self, record_id: str) -> bool:
        before = len(self._records)
        self._records = [record for record in self._records if record.record_id != record_id]
        return len(self._records) != before

    def clear(self) -> None:
        self._records = []
