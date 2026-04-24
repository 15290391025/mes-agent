"""Demo: ChatGPT-inspired memory layers for a MES Agent.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_memory.py
"""

from __future__ import annotations

import asyncio

from manugent.connector.demo import DemoMESConnector
from manugent.memory import InMemoryMemoryStore, MemoryContextBuilder, MemoryLayer
from manugent.memory.recipes import (
    remember_factory_fact,
    remember_incident,
    remember_operator_preference,
    remember_tool_audit,
)


async def main() -> None:
    store = InMemoryMemoryStore()
    scope = "demo-factory"

    remember_operator_preference(
        store,
        "Production managers prefer reports in Chinese with KPI, risk, and action sections.",
        scope=scope,
        tags=["report", "manager"],
    )
    remember_factory_fact(
        store,
        "SMT-03 is an SMT line where yield investigations must check solder paste lots.",
        scope=scope,
        tags=["SMT-03", "yield"],
    )
    remember_incident(
        store,
        "Previous SMT-03 yield drops were linked to MOUNTER-03A nozzle pickup alarms.",
        scope=scope,
        tags=["SMT-03", "yield", "MOUNTER-03A"],
        confidence=0.82,
    )

    connector = DemoMESConnector()
    await connector.connect()

    yield_result = await connector.execute_tool(
        "query_production_data",
        {"line_id": "SMT-03", "metric": "yield"},
    )
    remember_tool_audit(
        store,
        tool_name="query_production_data",
        params={"line_id": "SMT-03", "metric": "yield"},
        result_summary="success" if yield_result.success else str(yield_result.error),
        scope=scope,
        safety_level="read_only",
    )

    history_result = await connector.execute_tool(
        "get_equipment_history",
        {"equipment_id": "MOUNTER-03A"},
    )
    remember_tool_audit(
        store,
        tool_name="get_equipment_history",
        params={"equipment_id": "MOUNTER-03A"},
        result_summary="success" if history_result.success else str(history_result.error),
        scope=scope,
        safety_level="read_only",
    )

    context = MemoryContextBuilder(store).build_context("SMT-03 yield", scope=scope)
    audit_records = store.search(layer=MemoryLayer.AUDIT, scope=scope)

    print("# Memory Context")
    print(context)
    print()
    print("# Audit Memories")
    for record in audit_records:
        print(f"- {record.content}")


if __name__ == "__main__":
    asyncio.run(main())
