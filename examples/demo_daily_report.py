"""Demo: production morning report from MES tool calls.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_daily_report.py
"""

from __future__ import annotations

import asyncio

from manugent.connector.demo import DemoMESConnector


async def main() -> None:
    connector = DemoMESConnector()
    await connector.connect()

    yield_result = await connector.execute_tool(
        "query_production_data",
        {"line_id": "SMT-03", "metric": "yield", "time_range": "today"},
    )
    oee_result = await connector.execute_tool(
        "query_production_data",
        {"line_id": "SMT-03", "metric": "oee", "time_range": "today"},
    )
    quality_result = await connector.execute_tool(
        "get_quality_records",
        {"line_id": "SMT-03", "time_range": "today"},
    )
    wip_result = await connector.execute_tool("query_wip", {"line_id": "SMT-03"})
    rca_result = await connector.execute_tool(
        "analyze_root_cause",
        {"issue_type": "yield_drop", "context": {"line_id": "SMT-03", "time_range": "today"}},
    )

    yield_summary = yield_result.data["summary"]
    oee_summary = oee_result.data["summary"]
    quality_summary = quality_result.data["summary"]

    print("# SMT-03 Production Morning Report")
    print()
    print(
        f"- Yield: {yield_summary['current']}% "
        f"({yield_summary['trend']}, avg {yield_summary['average']}%)"
    )
    print(
        f"- OEE: {oee_summary['current']}% "
        f"({oee_summary['trend']}, avg {oee_summary['average']}%)"
    )
    print(f"- WIP stations: {len(wip_result.data)}")
    print(f"- Defects: {quality_summary['total_defects']}")
    print(f"- Top defect: {quality_summary['top_defects'][0][0]}")
    print()
    print("## Root-Cause Hypothesis")
    print(rca_result.data["finding"])
    print()
    print("## Recommended Actions")
    for action in rca_result.data["recommended_actions"]:
        print(f"- {action}")

    await connector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
