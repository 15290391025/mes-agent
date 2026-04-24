"""Demo: SQLite-backed memory persists MES Agent records.

Run from the repository root:
    PYTHONPATH=src python3 examples/demo_sqlite_memory.py
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from manugent.memory import MemoryLayer, SQLiteMemoryStore
from manugent.memory.recipes import remember_incident, remember_tool_audit


def main() -> None:
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "manugent-memory.sqlite3"
        store = SQLiteMemoryStore(db_path)
        remember_incident(
            store,
            "SMT-03 yield drop was linked to solder paste lot SP-20260424-A.",
            scope="demo:session:morning-shift",
            tags=["SMT-03", "yield", "SP-20260424-A"],
            confidence=0.86,
        )
        remember_tool_audit(
            store,
            tool_name="query_production_data",
            params={"line_id": "SMT-03", "metric": "yield"},
            result_summary="success",
            scope="demo:session:morning-shift",
        )

        reopened = SQLiteMemoryStore(db_path)
        incidents = reopened.search(
            "SMT-03 yield",
            layer=MemoryLayer.EPISODIC,
            scope="demo:session:morning-shift",
        )
        audits = reopened.search(layer=MemoryLayer.AUDIT, scope="demo:session:morning-shift")

        print("# SQLite Memory")
        print(f"DB: {db_path}")
        print("Incidents:")
        for record in incidents:
            print(f"- {record.content}")
        print("Audit:")
        for record in audits:
            print(f"- {record.content}")


if __name__ == "__main__":
    main()
