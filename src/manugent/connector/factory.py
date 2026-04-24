"""Connector factory for ManuGent."""

from __future__ import annotations

from manugent.connector.base import MESConnectionConfig, MESConnector
from manugent.connector.demo import DemoMESConnector


def create_connector(config: MESConnectionConfig) -> MESConnector:
    """Create a MES connector from configuration.

    The demo connector is intentionally first-class: it lets the project
    demonstrate MES-agent workflows without requiring access to a real factory.
    """
    mes_type = config.mes_type.lower()
    if mes_type in {"demo", "mock", "sample"}:
        return DemoMESConnector(config)
    if mes_type == "rest":
        from manugent.connector.rest import RestConnector

        return RestConnector(config)
    raise ValueError(f"Unsupported MES connector type: {config.mes_type}")
