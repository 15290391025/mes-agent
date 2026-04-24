"""ManuGent - Manufacturing Intelligence Agent Platform.

Give your factory MES a brain. AI Agent middleware that connects
to existing MES systems and provides natural language interaction,
intelligent monitoring, root cause analysis, and smart scheduling.

Example:
    >>> from manugent import MESAgent
    >>> agent = MESAgent(mes_type="rest", mes_url="http://mes.local/api")
    >>> response = agent.chat("3号线今天OEE是多少？")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

__version__ = "0.1.0"

if TYPE_CHECKING:
    from manugent.agent.core import MESAgent
    from manugent.connector.base import MESConnector


def __getattr__(name: str):
    """Lazy exports keep lightweight connector demos free of LLM dependencies."""
    if name == "MESAgent":
        from manugent.agent.core import MESAgent

        return MESAgent
    if name == "MESConnector":
        from manugent.connector.base import MESConnector

        return MESConnector
    raise AttributeError(f"module 'manugent' has no attribute {name!r}")


__all__ = ["MESAgent", "MESConnector", "__version__"]
