"""Demo: deterministic root-cause workflow with evidence chain.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_workflow_root_cause.py
"""

from __future__ import annotations

import asyncio

from manugent.connector.demo import DemoMESConnector
from manugent.memory import InMemoryMemoryStore
from manugent.memory.recipes import remember_incident
from manugent.workflows import RootCauseWorkflow


async def main() -> None:
    memory = InMemoryMemoryStore()
    remember_incident(
        memory,
        "Previous SMT-03 yield drop was resolved by cleaning MOUNTER-03A nozzle bank.",
        scope="demo-factory",
        tags=["SMT-03", "yield", "MOUNTER-03A"],
        confidence=0.84,
    )

    connector = DemoMESConnector()
    await connector.connect()

    workflow = RootCauseWorkflow(
        connector,
        memory_store=memory,
        memory_scope="demo-factory",
    )
    report = await workflow.analyze_yield_drop("SMT-03", "24h")

    print("# Root Cause Workflow Report")
    print(f"Finding: {report.finding}")
    print(f"Confidence: {report.confidence}")
    print()
    print("## Evidence Chain")
    for item in report.evidence:
        print(f"- [{item.evidence_type.value}] {item.summary}")
    print()
    print("## Recommended Actions")
    for item in report.recommendations:
        approval = "approval required" if item.requires_approval else "advisory"
        print(f"- ({approval}) {item.action}")


if __name__ == "__main__":
    asyncio.run(main())
