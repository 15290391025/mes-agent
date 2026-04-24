"""Demo: product traceability for a single serial number.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_traceability.py
"""

from __future__ import annotations

import asyncio
from pprint import pprint

from manugent.connector.demo import DemoMESConnector


async def main() -> None:
    connector = DemoMESConnector()
    await connector.connect()

    result = await connector.execute_tool(
        "get_traceability",
        {"serial_number": "SN202604240031"},
    )

    print("Question: SN202604240031 这台产品经历了哪些工序？有没有异常？")
    pprint(result.data, sort_dicts=False)

    await connector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
