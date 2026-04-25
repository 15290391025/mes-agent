"""Convenience helpers for common MES memory writes."""

from __future__ import annotations

from typing import Any

from manugent.memory.base import MemoryLayer, MemoryRecord, MemoryStore, MemoryWritePolicy
from manugent.models import IncidentReport


def remember_factory_fact(
    store: MemoryStore,
    content: str,
    *,
    scope: str = "default",
    tags: list[str] | None = None,
) -> MemoryRecord:
    """Store stable factory knowledge such as line layout or SOP rules."""
    return store.add(
        MemoryRecord(
            content=content,
            layer=MemoryLayer.SEMANTIC,
            scope=scope,
            tags=tags or ["factory"],
            policy=MemoryWritePolicy.EXPLICIT,
        )
    )


def remember_incident(
    store: MemoryStore,
    content: str,
    *,
    scope: str = "default",
    tags: list[str] | None = None,
    confidence: float = 1.0,
) -> MemoryRecord:
    """Store an operational incident, root-cause hypothesis, or corrective action."""
    return store.add(
        MemoryRecord(
            content=content,
            layer=MemoryLayer.EPISODIC,
            scope=scope,
            tags=tags or ["incident"],
            policy=MemoryWritePolicy.INFERRED,
            confidence=confidence,
        )
    )


def remember_incident_report(
    store: MemoryStore,
    report: IncidentReport,
    *,
    scope: str = "default",
) -> MemoryRecord:
    """Store a completed RCA report for future incident correlation."""
    content = (
        f"RCA报告: {report.line_id} {report.incident_type} yield 良率; "
        f"结论: {report.finding}; 置信度: {report.confidence}"
    )
    return store.add(
        MemoryRecord(
            content=content,
            layer=MemoryLayer.EPISODIC,
            scope=scope,
            tags=["incident_report", report.incident_type, report.line_id, "yield"],
            metadata={
                "report": report.to_dict(),
                "evidence_count": len(report.evidence),
                "recommendation_count": len(report.recommendations),
            },
            policy=MemoryWritePolicy.INFERRED,
            confidence=report.confidence,
        )
    )


def remember_operator_preference(
    store: MemoryStore,
    content: str,
    *,
    scope: str = "default",
    tags: list[str] | None = None,
) -> MemoryRecord:
    """Store a user or role preference that should shape future responses."""
    return store.add(
        MemoryRecord(
            content=content,
            layer=MemoryLayer.PREFERENCE,
            scope=scope,
            tags=tags or ["preference"],
            policy=MemoryWritePolicy.EXPLICIT,
        )
    )


def remember_tool_audit(
    store: MemoryStore,
    *,
    tool_name: str,
    params: dict[str, Any],
    result_summary: str,
    scope: str = "default",
    safety_level: str = "read_only",
) -> MemoryRecord:
    """Store an auditable tool-call record."""
    return store.add(
        MemoryRecord(
            content=f"{tool_name} called with {params}; result: {result_summary}",
            layer=MemoryLayer.AUDIT,
            scope=scope,
            tags=["audit", tool_name, safety_level],
            metadata={
                "tool_name": tool_name,
                "params": params,
                "result_summary": result_summary,
                "safety_level": safety_level,
            },
            policy=MemoryWritePolicy.AUDIT,
        )
    )
