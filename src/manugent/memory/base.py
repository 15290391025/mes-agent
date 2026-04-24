"""Core memory interfaces for ManuGent.

The design mirrors ChatGPT-style memory concepts, but maps them to MES work:
session context, historical incidents, stable factory knowledge, operator
preferences, and audit records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import uuid4


class MemoryLayer(StrEnum):
    """Memory layers used by the MES agent."""

    SESSION = "session"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PREFERENCE = "preference"
    AUDIT = "audit"


class MemoryWritePolicy(StrEnum):
    """How a memory was written and how strongly it should be trusted."""

    EXPLICIT = "explicit"
    INFERRED = "inferred"
    SYSTEM = "system"
    AUDIT = "audit"


@dataclass
class MemoryRecord:
    """A single memory item with provenance and scope."""

    content: str
    layer: MemoryLayer
    scope: str = "default"
    record_id: str = field(default_factory=lambda: uuid4().hex)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    policy: MemoryWritePolicy = MemoryWritePolicy.SYSTEM
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def matches(
        self,
        query: str = "",
        layer: MemoryLayer | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Return whether this record is relevant to a simple metadata query."""
        if layer and self.layer != layer:
            return False
        if scope and self.scope != scope:
            return False
        if tags and not set(tags).issubset(set(self.tags)):
            return False
        if not query:
            return True

        haystack = " ".join([self.content, *self.tags, str(self.metadata)]).lower()
        return all(term in haystack for term in query.lower().split())


class MemoryStore(Protocol):
    """Minimal store interface for memory backends."""

    def add(self, record: MemoryRecord) -> MemoryRecord:
        """Persist a memory record."""
        ...

    def search(
        self,
        query: str = "",
        *,
        layer: MemoryLayer | None = None,
        scope: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        """Search memory records."""
        ...

    def forget(self, record_id: str) -> bool:
        """Delete one memory record."""
        ...
