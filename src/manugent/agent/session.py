"""Session isolation for ManuGent agents."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from langchain_core.language_models import BaseChatModel

from manugent.agent.core import MESAgent
from manugent.connector.base import MESConnector
from manugent.memory import MemoryStore
from manugent.security.approvals import ApprovalQueue


@dataclass
class AgentSessionManager:
    """Create one MESAgent per session_id to avoid cross-user history leaks."""

    llm_factory: Callable[[], BaseChatModel]
    connector_factory: Callable[[], MESConnector]
    memory_store: MemoryStore | None = None
    approval_queue: ApprovalQueue | None = None
    default_scope: str = "default"
    _sessions: dict[str, MESAgent] = field(default_factory=dict)

    def get(self, session_id: str | None = None) -> MESAgent:
        """Return an isolated agent for a session."""
        resolved_id = session_id or "default"
        if resolved_id not in self._sessions:
            self._sessions[resolved_id] = MESAgent(
                llm=self.llm_factory(),
                connector=self.connector_factory(),
                memory_store=self.memory_store,
                memory_scope=self._scope_for(resolved_id),
                approval_queue=self.approval_queue,
                approval_session_id=resolved_id,
            )
        return self._sessions[resolved_id]

    def clear(self, session_id: str | None = None) -> bool:
        """Clear one session history, or all sessions when session_id is omitted."""
        if session_id is None:
            for agent in self._sessions.values():
                agent.clear_history()
            self._sessions.clear()
            return True

        agent = self._sessions.get(session_id)
        if not agent:
            return False
        agent.clear_history()
        del self._sessions[session_id]
        return True

    def count(self) -> int:
        """Return active in-memory session count."""
        return len(self._sessions)

    def _scope_for(self, session_id: str) -> str:
        return f"{self.default_scope}:session:{session_id}"
