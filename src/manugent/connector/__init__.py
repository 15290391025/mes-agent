"""ManuGent Connectors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from manugent.connector.base import MESConnectionConfig, MESConnector, QueryResult

if TYPE_CHECKING:
    from manugent.connector.demo import DemoMESConnector
    from manugent.connector.rest import RestConnector

__all__ = [
    "DemoMESConnector",
    "MESConnectionConfig",
    "MESConnector",
    "QueryResult",
    "RestConnector",
    "create_connector",
]


def __getattr__(name: str):
    """Lazy connector exports avoid importing optional HTTP dependencies for demos."""
    if name == "DemoMESConnector":
        from manugent.connector.demo import DemoMESConnector

        return DemoMESConnector
    if name == "RestConnector":
        from manugent.connector.rest import RestConnector

        return RestConnector
    if name == "create_connector":
        from manugent.connector.factory import create_connector

        return create_connector
    raise AttributeError(f"module 'manugent.connector' has no attribute {name!r}")
