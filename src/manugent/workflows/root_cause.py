"""Deterministic root-cause workflow for manufacturing incidents."""

from __future__ import annotations

from collections import Counter
from typing import Any

from manugent.connector.base import MESConnector
from manugent.memory import MemoryLayer, MemoryStore
from manugent.memory.recipes import remember_incident_report
from manugent.models import Evidence, EvidenceType, IncidentReport, Recommendation


class RootCauseWorkflow:
    """Analyze a line incident with an explicit MES evidence chain."""

    def __init__(
        self,
        connector: MESConnector,
        memory_store: MemoryStore | None = None,
        memory_scope: str = "default",
    ) -> None:
        self.connector = connector
        self.memory_store = memory_store
        self.memory_scope = memory_scope

    async def analyze_yield_drop(
        self,
        line_id: str,
        time_range: str = "24h",
    ) -> IncidentReport:
        """Analyze a yield drop by correlating production, quality, and equipment."""
        yield_data = await self._require_tool(
            "query_production_data",
            {"line_id": line_id, "metric": "yield", "time_range": time_range},
        )
        quality_data = await self._require_tool(
            "get_quality_records",
            {"line_id": line_id, "time_range": time_range},
        )
        equipment_id = self._infer_equipment_id(line_id)
        equipment_history = await self._require_tool(
            "get_equipment_history",
            {"equipment_id": equipment_id, "days": 7},
        )

        evidence = [
            self._production_evidence(yield_data),
            self._quality_evidence(quality_data),
            self._material_evidence(quality_data),
            self._equipment_evidence(equipment_id, equipment_history),
        ]
        evidence.extend(self._memory_evidence(line_id))

        finding = self._build_finding(evidence)
        confidence = self._score_confidence(evidence)
        recommendations = self._recommend_actions(evidence)

        report = IncidentReport(
            incident_type="yield_drop",
            line_id=line_id,
            finding=finding,
            confidence=confidence,
            evidence=evidence,
            recommendations=recommendations,
        )
        self._persist_report(report)
        return report

    async def _require_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        result = await self.connector.execute_tool(tool_name, params)
        if not result.success:
            raise RuntimeError(f"{tool_name} failed: {result.error}")
        return result.data

    def _production_evidence(self, yield_data: dict[str, Any]) -> Evidence:
        summary = yield_data["summary"]
        return Evidence(
            evidence_type=EvidenceType.PRODUCTION,
            source_tool="query_production_data",
            summary=(
                f"当前良率为 {summary['current']}%，趋势为"
                f"{self._translate_trend(summary['trend'])}，"
                f"区间平均良率为 {summary['average']}%。"
            ),
            confidence=0.9,
            data=summary,
        )

    def _quality_evidence(self, quality_data: dict[str, Any]) -> Evidence:
        summary = quality_data["summary"]
        top_defects = summary.get("top_defects") or []
        top_defect = top_defects[0] if top_defects else ("unknown", 0)
        return Evidence(
            evidence_type=EvidenceType.QUALITY,
            source_tool="get_quality_records",
            summary=(
                f"最高频缺陷为 {self._translate_defect(top_defect[0])}，"
                f"共 {top_defect[1]} 条记录。"
            ),
            confidence=0.86,
            data={"top_defects": top_defects, "total_defects": summary["total_defects"]},
        )

    def _material_evidence(self, quality_data: dict[str, Any]) -> Evidence:
        records = quality_data.get("records", [])
        material_counts = Counter(record.get("material_lot", "unknown") for record in records)
        top_lot = material_counts.most_common(1)[0] if material_counts else ("unknown", 0)
        return Evidence(
            evidence_type=EvidenceType.MATERIAL,
            source_tool="get_quality_records",
            summary=f"缺陷集中在物料批次 {top_lot[0]}，关联记录 {top_lot[1]} 条。",
            confidence=0.82,
            data={"top_material_lot": top_lot[0], "count": top_lot[1]},
        )

    def _equipment_evidence(
        self,
        equipment_id: str,
        equipment_history: list[dict[str, Any]],
    ) -> Evidence:
        warnings = [
            event
            for event in equipment_history
            if event.get("severity") in {"warning", "critical"}
        ]
        event_names = [event.get("event", "unknown") for event in warnings]
        translated_events = [self._translate_event(event) for event in event_names]
        return Evidence(
            evidence_type=EvidenceType.EQUIPMENT,
            source_tool="get_equipment_history",
            summary=(
                f"{equipment_id} 存在 {len(warnings)} 条告警事件："
                f"{'、'.join(translated_events) if translated_events else '暂无'}。"
            ),
            confidence=0.8 if warnings else 0.35,
            data={"equipment_id": equipment_id, "events": warnings},
        )

    def _memory_evidence(self, line_id: str) -> list[Evidence]:
        if self.memory_store is None:
            return []

        records = self.memory_store.search(
            query=f"{line_id} yield",
            layer=MemoryLayer.EPISODIC,
            scope=self.memory_scope,
            limit=2,
        )
        return [
            Evidence(
                evidence_type=EvidenceType.MEMORY,
                source_tool="memory_search",
                summary=record.content,
                confidence=record.confidence,
                data={"record_id": record.record_id, "tags": record.tags},
            )
            for record in records
        ]

    def _persist_report(self, report: IncidentReport) -> None:
        if self.memory_store is None:
            return
        remember_incident_report(
            self.memory_store,
            report,
            scope=self.memory_scope,
        )

    def _build_finding(self, evidence: list[Evidence]) -> str:
        material = next(item for item in evidence if item.evidence_type == EvidenceType.MATERIAL)
        equipment = next(item for item in evidence if item.evidence_type == EvidenceType.EQUIPMENT)
        return (
            "本次良率下降最可能由物料批次异常与设备状态波动共同触发："
            f"{material.summary}{equipment.summary}"
        )

    def _score_confidence(self, evidence: list[Evidence]) -> float:
        if not evidence:
            return 0.0
        score = sum(item.confidence for item in evidence) / len(evidence)
        return round(min(score, 0.95), 2)

    def _recommend_actions(self, evidence: list[Evidence]) -> list[Recommendation]:
        material = next(item for item in evidence if item.evidence_type == EvidenceType.MATERIAL)
        equipment = next(item for item in evidence if item.evidence_type == EvidenceType.EQUIPMENT)
        lot = material.data.get("top_material_lot", "可疑物料批次")
        equipment_id = equipment.data.get("equipment_id", "可疑设备")
        return [
            Recommendation(
                action=f"隔离物料批次 {lot}，并与上一批次的 SPI/AOI 记录做对比。",
                owner="quality_engineer",
                rationale="缺陷记录在同一物料批次上聚集，需要先排除批次性来料问题。",
            ),
            Recommendation(
                action=(
                    f"检查 {equipment_id}，重点确认吸嘴取料稳定性和飞达振动告警。"
                ),
                owner="equipment_engineer",
                rationale="设备告警与良率下降窗口重叠，存在设备状态影响贴装质量的风险。",
            ),
            Recommendation(
                action="后续 30 片先执行首件/加严检查，确认缺陷收敛后再恢复正常放行。",
                owner="production_supervisor",
                requires_approval=True,
                rationale="该动作会影响产线放行节奏，属于生产控制边界。",
            ),
        ]

    def _infer_equipment_id(self, line_id: str) -> str:
        suffix = line_id.split("-")[-1]
        return f"MOUNTER-{suffix}A"

    def _translate_trend(self, trend: str) -> str:
        return {
            "up": "上升",
            "down": "下降",
            "stable": "稳定",
        }.get(trend, trend)

    def _translate_defect(self, defect: str) -> str:
        return {
            "solder_bridge": "锡桥",
            "missing_component": "缺件",
            "tombstone": "立碑",
            "offset": "偏移",
            "unknown": "未知缺陷",
        }.get(defect, defect)

    def _translate_event(self, event: str) -> str:
        return {
            "NOZZLE_PICKUP_LOW": "吸嘴取料率偏低",
            "FEEDER_VIBRATION_HIGH": "飞达振动偏高",
            "TEMPERATURE_DRIFT": "温度漂移",
            "unknown": "未知事件",
        }.get(event, event)
