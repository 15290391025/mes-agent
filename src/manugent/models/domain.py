"""Manufacturing domain models for Agent workflows.

These models are intentionally compact. They capture the MES entities needed
for portfolio-grade reasoning demos without forcing every connector to expose a
full ISA-95 implementation on day one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


@dataclass(frozen=True)
class ProductionLine:
    """A production line or cell."""

    line_id: str
    name: str
    process: str
    shift: str = ""


@dataclass(frozen=True)
class WorkOrder:
    """A production order running through MES execution."""

    order_id: str
    product_id: str
    line_id: str
    status: str
    planned_qty: int
    finished_qty: int
    due: str


class EvidenceType(StrEnum):
    """Kinds of evidence used in manufacturing analysis."""

    PRODUCTION = "production"
    QUALITY = "quality"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    TRACEABILITY = "traceability"
    MEMORY = "memory"


@dataclass(frozen=True)
class Evidence:
    """One evidence item in a manufacturing reasoning chain."""

    evidence_type: EvidenceType
    summary: str
    source_tool: str
    confidence: float = 1.0
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    """A recommended action produced by a workflow."""

    action: str
    owner: str = "production_engineer"
    requires_approval: bool = False
    rationale: str = ""


@dataclass(frozen=True)
class IncidentReport:
    """Structured incident analysis output."""

    incident_type: str
    line_id: str
    finding: str
    confidence: float
    evidence: list[Evidence]
    recommendations: list[Recommendation]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report."""
        return {
            "incident_type": self.incident_type,
            "line_id": self.line_id,
            "finding": self.finding,
            "confidence": self.confidence,
            "evidence": [
                {
                    "type": item.evidence_type.value,
                    "summary": item.summary,
                    "source_tool": item.source_tool,
                    "confidence": item.confidence,
                    "data": item.data,
                }
                for item in self.evidence
            ],
            "recommendations": [
                {
                    "action": item.action,
                    "owner": item.owner,
                    "requires_approval": item.requires_approval,
                    "rationale": item.rationale,
                }
                for item in self.recommendations
            ],
        }
