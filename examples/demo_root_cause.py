"""Demo: yield drop root-cause analysis on a simulated SMT line.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_root_cause.py
"""

from __future__ import annotations

import asyncio
from pprint import pprint

from manugent.connector.demo import DemoMESConnector


async def main() -> None:
    connector = DemoMESConnector()
    await connector.connect()

    result = await connector.execute_tool(
        "analyze_root_cause",
        {
            "issue_type": "yield_drop",
            "context": {"line_id": "SMT-03", "time_range": "24h"},
        },
    )

    print("Question: SMT-03 最近 24 小时良率为什么下降？")
    pprint(result.data, sort_dicts=False)

    await connector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
