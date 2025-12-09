# peargent/core/state.py

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from peargent.history import ConversationHistory

class State:
    """
    Shared key-value store + message history across the pool loop.
    Accessible by the router and the agents/tools.

    Optionally supports persistent history through ConversationHistory.
    """
    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        history_manager: Optional["ConversationHistory"] = None,
        agents: Optional[Dict[str, Any]] = None
    ):
        self.kv: Dict[str, Any] = data or {}
        self.history: List[Dict[str, Any]] = []
        self.history_manager = history_manager
        self.agents: Dict[str, Any] = agents or {}

    def add_message(self, role: str, content: str, agent: Optional[str] = None):
        """
        Add a message to the state history.

        If a history manager is configured, also persists to storage.
        """
        self.history.append({
            "role": role,
            "content": content,
            "agent": agent
        })

        # Sync to persistent history if available
        if self.history_manager:
            if role == "user":
                self.history_manager.add_user_message(content)
            elif role == "assistant":
                self.history_manager.add_assistant_message(content, agent=agent)

    def get(self, key: str, default=None): return self.kv.get(key, default)
    def set(self, key: str, value: Any): self.kv[key] = value