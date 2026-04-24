"""Demo MES connector with built-in manufacturing data.

This connector is designed for portfolio demos and tests. It models a small
SMT factory with production metrics, equipment events, quality defects, WIP,
orders, and traceability records so the agent can demonstrate MES reasoning
without depending on a live MES.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from manugent.connector.base import MESConnectionConfig, MESConnector, QueryResult


class DemoMESConnector(MESConnector):
    """In-memory MES connector for manufacturing-agent demonstrations."""

    def __init__(self, config: MESConnectionConfig | None = None) -> None:
        super().__init__(
            config
            or MESConnectionConfig(
                mes_type="demo",
                base_url="demo://smt-factory",
                auth_type="none",
            )
        )
        self._data = _build_demo_data()

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def health_check(self) -> bool:
        return self._connected

    async def get_schema(self) -> dict[str, Any]:
        return {
            "entities": {
                "line": ["line_id", "name", "process", "shift"],
                "production_metric": ["line_id", "metric", "time_range", "points", "summary"],
                "equipment": ["equipment_id", "line_id", "status", "alerts", "maintenance"],
                "quality_record": ["line_id", "defect_type", "material_lot", "station"],
                "traceability": ["serial_number", "order_id", "route", "quality_checks"],
            },
            "supported_lines": list(self._data["lines"].keys()),
            "supported_tools": [
                "query_production_data",
                "query_wip",
                "query_production_orders",
                "get_equipment_status",
                "get_equipment_history",
                "get_quality_records",
                "get_traceability",
                "analyze_root_cause",
                "suggest_schedule",
                "create_alert",
            ],
        }

    async def execute_tool(self, tool_name: str, params: dict[str, Any]) -> QueryResult:
        handlers = {
            "query_production_data": self._query_production_data,
            "query_wip": self._query_wip,
            "query_production_orders": self._query_production_orders,
            "get_equipment_status": self._get_equipment_status,
            "get_equipment_history": self._get_equipment_history,
            "get_quality_records": self._get_quality_records,
            "get_traceability": self._get_traceability,
            "analyze_root_cause": self._analyze_root_cause,
            "suggest_schedule": self._suggest_schedule,
            "create_alert": self._create_alert,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return QueryResult(success=False, error=f"Unknown demo tool: {tool_name}")
        try:
            return handler(params)
        except KeyError as exc:
            return QueryResult(success=False, error=f"Unknown entity: {exc}")

    def _query_production_data(self, params: dict[str, Any]) -> QueryResult:
        line_id = params.get("line_id", "SMT-03")
        metric = params.get("metric", "yield")
        metrics = self._data["production_metrics"].get(line_id)
        if not metrics or metric not in metrics:
            return QueryResult(success=False, error=f"No {metric} data for line {line_id}")

        points = metrics[metric]
        values = [p["value"] for p in points]
        data = {
            "line": self._data["lines"][line_id],
            "metric": metric,
            "time_range": params.get("time_range", "24h"),
            "granularity": params.get("granularity", "hourly"),
            "points": points,
            "summary": {
                "current": values[-1],
                "average": round(sum(values) / len(values), 2),
                "min": min(values),
                "max": max(values),
                "trend": "down" if values[-1] < values[0] else "up",
            },
        }
        return QueryResult(success=True, data=data, metadata={"source": "demo_mes"})

    def _query_wip(self, params: dict[str, Any]) -> QueryResult:
        line_id = params.get("line_id")
        product_id = params.get("product_id")
        station = params.get("station")
        rows = self._data["wip"]
        if line_id:
            rows = [r for r in rows if r["line_id"] == line_id]
        if product_id:
            rows = [r for r in rows if r["product_id"] == product_id]
        if station:
            rows = [r for r in rows if r["station"] == station]
        return QueryResult(success=True, data=rows, metadata={"count": len(rows)})

    def _query_production_orders(self, params: dict[str, Any]) -> QueryResult:
        order_id = params.get("order_id")
        status = params.get("status")
        rows = self._data["orders"]
        if order_id:
            rows = [r for r in rows if r["order_id"] == order_id]
        if status:
            rows = [r for r in rows if r["status"] == status]
        return QueryResult(success=True, data=rows, metadata={"count": len(rows)})

    def _get_equipment_status(self, params: dict[str, Any]) -> QueryResult:
        equipment_id = params["equipment_id"]
        equipment = self._data["equipment"][equipment_id]
        return QueryResult(success=True, data=equipment, metadata={"source": "demo_mes"})

    def _get_equipment_history(self, params: dict[str, Any]) -> QueryResult:
        equipment_id = params["equipment_id"]
        days = int(params.get("days", 30))
        history = self._data["equipment_history"].get(equipment_id, [])
        return QueryResult(
            success=True,
            data=history,
            metadata={"equipment_id": equipment_id, "days": days, "count": len(history)},
        )

    def _get_quality_records(self, params: dict[str, Any]) -> QueryResult:
        line_id = params.get("line_id")
        defect_type = params.get("defect_type")
        rows = self._data["quality_records"]
        if line_id:
            rows = [r for r in rows if r["line_id"] == line_id]
        if defect_type:
            rows = [r for r in rows if r["defect_type"] == defect_type]
        defect_counts = Counter(r["defect_type"] for r in rows)
        material_counts = Counter(r["material_lot"] for r in rows)
        return QueryResult(
            success=True,
            data={
                "records": rows,
                "summary": {
                    "total_defects": len(rows),
                    "top_defects": defect_counts.most_common(5),
                    "top_material_lots": material_counts.most_common(5),
                },
            },
            metadata={"source": "demo_mes"},
        )

    def _get_traceability(self, params: dict[str, Any]) -> QueryResult:
        serial_number = params["serial_number"]
        trace = self._data["traceability"].get(serial_number)
        if not trace:
            return QueryResult(success=False, error=f"Serial number not found: {serial_number}")
        return QueryResult(success=True, data=trace, metadata={"source": "demo_mes"})

    def _analyze_root_cause(self, params: dict[str, Any]) -> QueryResult:
        context = params.get("context", {})
        line_id = context.get("line") or context.get("line_id") or "SMT-03"
        quality = self._get_quality_records({"line_id": line_id}).data
        equipment_history = self._data["equipment_history"].get("MOUNTER-03A", [])
        yield_summary = self._query_production_data(
            {"line_id": line_id, "metric": "yield", "time_range": context.get("time_range", "24h")}
        ).data["summary"]

        report = {
            "issue_type": params.get("issue_type", "yield_drop"),
            "line_id": line_id,
            "finding": "SMT-03 yield drop is most likely linked to solder paste lot SP-20260424-A and mounter nozzle alarms.",
            "confidence": 0.78,
            "evidence": [
                {
                    "type": "production_metric",
                    "detail": f"Yield trend moved {yield_summary['trend']} from 98.1 to {yield_summary['current']}.",
                },
                {
                    "type": "quality",
                    "detail": f"Top defect is {quality['summary']['top_defects'][0][0]} with {quality['summary']['top_defects'][0][1]} records.",
                },
                {
                    "type": "material",
                    "detail": "Defects concentrate on material lot SP-20260424-A after 10:00.",
                },
                {
                    "type": "equipment",
                    "detail": f"{len(equipment_history)} related mounter events found for MOUNTER-03A.",
                },
            ],
            "recommended_actions": [
                "Quarantine solder paste lot SP-20260424-A and compare SPI records with the previous lot.",
                "Inspect and clean MOUNTER-03A nozzle bank 2 before the next shift.",
                "Run first-article inspection for the next 30 panels on SMT-03.",
            ],
            "human_approval_required": False,
        }
        return QueryResult(success=True, data=report, metadata={"source": "demo_rca"})

    def _suggest_schedule(self, params: dict[str, Any]) -> QueryResult:
        line_ids = params.get("line_ids", ["SMT-01", "SMT-03"])
        return QueryResult(
            success=True,
            data={
                "proposal_id": "SCH-DEMO-001",
                "horizon": params.get("horizon", "24h"),
                "line_ids": line_ids,
                "plan": [
                    {"line_id": "SMT-01", "order_id": "MO-20260424-001", "slot": "08:00-16:00"},
                    {"line_id": "SMT-03", "order_id": "MO-20260424-003", "slot": "16:00-23:00"},
                ],
                "constraints_checked": ["material_availability", "equipment_status", "due_date"],
                "note": "Advisory only. MES write-back requires human approval.",
            },
            metadata={"source": "demo_scheduler"},
        )

    def _create_alert(self, params: dict[str, Any]) -> QueryResult:
        return QueryResult(
            success=True,
            data={
                "alert_id": "ALERT-DEMO-001",
                "severity": params.get("severity", "warning"),
                "message": params.get("message", ""),
                "status": "draft_pending_approval",
            },
            metadata={"source": "demo_alerts"},
        )


def _build_demo_data() -> dict[str, Any]:
    return {
        "lines": {
            "SMT-01": {"line_id": "SMT-01", "name": "SMT Line 1", "process": "SMT", "shift": "A"},
            "SMT-03": {"line_id": "SMT-03", "name": "SMT Line 3", "process": "SMT", "shift": "B"},
        },
        "production_metrics": {
            "SMT-03": {
                "yield": [
                    {"time": "08:00", "value": 98.1},
                    {"time": "10:00", "value": 97.6},
                    {"time": "12:00", "value": 95.9},
                    {"time": "14:00", "value": 93.8},
                    {"time": "16:00", "value": 92.4},
                ],
                "oee": [
                    {"time": "08:00", "value": 86.2},
                    {"time": "10:00", "value": 84.7},
                    {"time": "12:00", "value": 80.3},
                    {"time": "14:00", "value": 76.8},
                    {"time": "16:00", "value": 74.1},
                ],
                "output": [
                    {"time": "08:00", "value": 1180},
                    {"time": "10:00", "value": 1164},
                    {"time": "12:00", "value": 1088},
                    {"time": "14:00", "value": 1012},
                    {"time": "16:00", "value": 984},
                ],
            },
            "SMT-01": {
                "yield": [
                    {"time": "08:00", "value": 98.4},
                    {"time": "10:00", "value": 98.6},
                    {"time": "12:00", "value": 98.5},
                    {"time": "14:00", "value": 98.7},
                ],
                "oee": [
                    {"time": "08:00", "value": 87.4},
                    {"time": "10:00", "value": 88.1},
                    {"time": "12:00", "value": 87.9},
                    {"time": "14:00", "value": 88.5},
                ],
            },
        },
        "equipment": {
            "MOUNTER-03A": {
                "equipment_id": "MOUNTER-03A",
                "line_id": "SMT-03",
                "status": "warning",
                "uptime_hours": 426,
                "last_maintenance": "2026-04-18",
                "active_alerts": ["NOZZLE_PICKUP_LOW", "FEEDER_VIBRATION_HIGH"],
            },
            "SPI-03": {
                "equipment_id": "SPI-03",
                "line_id": "SMT-03",
                "status": "running",
                "uptime_hours": 218,
                "last_maintenance": "2026-04-21",
                "active_alerts": [],
            },
        },
        "equipment_history": {
            "MOUNTER-03A": [
                {
                    "time": "2026-04-24 10:12",
                    "event": "NOZZLE_PICKUP_LOW",
                    "severity": "warning",
                    "station": "mounting",
                },
                {
                    "time": "2026-04-24 11:05",
                    "event": "FEEDER_VIBRATION_HIGH",
                    "severity": "warning",
                    "station": "mounting",
                },
                {
                    "time": "2026-04-24 13:44",
                    "event": "NOZZLE_CLEANING_OVERDUE",
                    "severity": "info",
                    "station": "mounting",
                },
            ]
        },
        "quality_records": [
            {
                "time": "2026-04-24 10:18",
                "line_id": "SMT-03",
                "serial_number": "SN202604240031",
                "defect_type": "solder_bridge",
                "station": "AOI",
                "material_lot": "SP-20260424-A",
            },
            {
                "time": "2026-04-24 10:42",
                "line_id": "SMT-03",
                "serial_number": "SN202604240044",
                "defect_type": "solder_bridge",
                "station": "AOI",
                "material_lot": "SP-20260424-A",
            },
            {
                "time": "2026-04-24 11:21",
                "line_id": "SMT-03",
                "serial_number": "SN202604240058",
                "defect_type": "component_offset",
                "station": "AOI",
                "material_lot": "SP-20260424-A",
            },
            {
                "time": "2026-04-24 12:37",
                "line_id": "SMT-03",
                "serial_number": "SN202604240073",
                "defect_type": "solder_bridge",
                "station": "AOI",
                "material_lot": "SP-20260424-A",
            },
        ],
        "wip": [
            {"line_id": "SMT-03", "station": "printer", "product_id": "P-A100", "quantity": 120},
            {"line_id": "SMT-03", "station": "mounter", "product_id": "P-A100", "quantity": 86},
            {"line_id": "SMT-03", "station": "reflow", "product_id": "P-A100", "quantity": 74},
            {"line_id": "SMT-01", "station": "aoi", "product_id": "P-B200", "quantity": 42},
        ],
        "orders": [
            {
                "order_id": "MO-20260424-001",
                "product_id": "P-B200",
                "line_id": "SMT-01",
                "status": "in_progress",
                "planned_qty": 8000,
                "finished_qty": 5220,
                "due": "2026-04-25",
            },
            {
                "order_id": "MO-20260424-003",
                "product_id": "P-A100",
                "line_id": "SMT-03",
                "status": "on_hold",
                "planned_qty": 6000,
                "finished_qty": 2190,
                "due": "2026-04-24",
            },
        ],
        "traceability": {
            "SN202604240031": {
                "serial_number": "SN202604240031",
                "order_id": "MO-20260424-003",
                "product_id": "P-A100",
                "material_lots": {
                    "pcb": "PCB-20260423-C",
                    "solder_paste": "SP-20260424-A",
                    "ic": "IC-7788-0422",
                },
                "route": [
                    {"station": "printer", "equipment_id": "PRINTER-03", "operator": "OP102", "result": "pass"},
                    {"station": "spi", "equipment_id": "SPI-03", "operator": "OP102", "result": "pass"},
                    {"station": "mounter", "equipment_id": "MOUNTER-03A", "operator": "OP117", "result": "pass"},
                    {"station": "reflow", "equipment_id": "REFLOW-03", "operator": "OP117", "result": "pass"},
                    {"station": "aoi", "equipment_id": "AOI-03", "operator": "OP211", "result": "fail"},
                ],
                "quality_checks": [
                    {"station": "AOI", "defect_type": "solder_bridge", "severity": "major"},
                ],
                "disposition": "hold_for_rework",
            }
        },
    }
