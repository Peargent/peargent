# peargent/core/streaming.py

"""
Streaming support for agents and pools.

Provides rich update objects for observing agent execution in real-time.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class UpdateType(Enum):
    """Types of streaming updates."""
    AGENT_START = "agent_start"
    TOKEN = "token"
    AGENT_END = "agent_end"
    POOL_START = "pool_start"
    POOL_END = "pool_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    ERROR = "error"


@dataclass
class StreamUpdate:
    """
    Rich update object for streaming observations.

    Different from LangChain's approach - uses dataclass instead of dicts
    for better type safety and cleaner API.

    Attributes:
        type: Type of update
        content: Text content (for TOKEN updates)
        agent: Agent name (if applicable)
        metadata: Additional metadata (tokens, cost, etc.)
    """
    type: UpdateType
    content: Optional[str] = None
    agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @property
    def is_token(self) -> bool:
        """Check if this is a token update."""
        return self.type == UpdateType.TOKEN

    @property
    def is_agent_start(self) -> bool:
        """Check if this is an agent start update."""
        return self.type == UpdateType.AGENT_START

    @property
    def is_agent_end(self) -> bool:
        """Check if this is an agent end update."""
        return self.type == UpdateType.AGENT_END

    @property
    def tokens(self) -> Optional[int]:
        """Get token count from metadata."""
        if self.metadata:
            return self.metadata.get('tokens')
        return None

    @property
    def cost(self) -> Optional[float]:
        """Get cost from metadata."""
        if self.metadata:
            return self.metadata.get('cost')
        return None

    @property
    def duration(self) -> Optional[float]:
        """Get duration from metadata."""
        if self.metadata:
            return self.metadata.get('duration')
        return None

    def __str__(self) -> str:
        """String representation for debugging."""
        if self.type == UpdateType.TOKEN:
            return f"Token: {self.content}"
        elif self.type == UpdateType.AGENT_START:
            return f"Agent Start: {self.agent}"
        elif self.type == UpdateType.AGENT_END:
            return f"Agent End: {self.agent} ({self.tokens} tokens, ${self.cost:.6f})"
        else:
            return f"{self.type.value}: {self.agent or 'N/A'}"
