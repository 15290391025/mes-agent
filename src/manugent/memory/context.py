"""Build compact memory context for LLM prompts."""

from __future__ import annotations

from collections import defaultdict

from manugent.memory.base import MemoryLayer, MemoryRecord, MemoryStore


class MemoryContextBuilder:
    """Retrieve and format relevant memory for an agent turn."""

    def __init__(self, store: MemoryStore, max_records_per_layer: int = 3) -> None:
        self.store = store
        self.max_records_per_layer = max_records_per_layer

    def retrieve(self, query: str, scope: str = "default") -> list[MemoryRecord]:
        """Retrieve a balanced set of memories across layers."""
        records: list[MemoryRecord] = []
        for layer in [
            MemoryLayer.PREFERENCE,
            MemoryLayer.SEMANTIC,
            MemoryLayer.EPISODIC,
            MemoryLayer.AUDIT,
        ]:
            records.extend(
                self.store.search(
                    query=query,
                    layer=layer,
                    scope=scope,
                    limit=self.max_records_per_layer,
                )
            )
        return records

    def build_context(self, query: str, scope: str = "default") -> str:
        """Format retrieved memories as a prompt-ready context block."""
        records = self.retrieve(query=query, scope=scope)
        if not records:
            return ""

        grouped: dict[MemoryLayer, list[MemoryRecord]] = defaultdict(list)
        for record in records:
            grouped[record.layer].append(record)

        sections = ["Relevant ManuGent memory:"]
        for layer in [
            MemoryLayer.PREFERENCE,
            MemoryLayer.SEMANTIC,
            MemoryLayer.EPISODIC,
            MemoryLayer.AUDIT,
        ]:
            layer_records = grouped.get(layer)
            if not layer_records:
                continue
            sections.append(f"{layer.value}:")
            for record in layer_records:
                sections.append(f"- {record.content}")

        return "\n".join(sections)
