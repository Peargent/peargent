"""
History configuration module for peargent.

Provides HistoryConfig class for configuring conversation history management.
"""

from typing import Optional, Union, Literal
from dataclasses import dataclass

from peargent.history import ConversationHistory, HistoryStore
from peargent.storage import StorageType


@dataclass
class HistoryConfig:
    """
    Configuration for agent history management.

    This class provides a clean DSL for configuring conversation history with
    automatic context management. It intelligently handles which parameters are
    needed based on the strategy.

    Examples:
        # Simple trim strategy (no summarize_model needed)
        config = HistoryConfig(
            auto_manage_context=True,
            max_context_messages=15,
            strategy="trim_last",
            store=File(storage_dir="./conversations")
        )

        # Smart or summarize strategy (summarize_model auto-inferred or explicit)
        config = HistoryConfig(
            auto_manage_context=True,
            max_context_messages=20,
            strategy="smart",  # Will use agent's model if summarize_model not provided
            store=Memory()
        )

        # Explicit summarize model for smart/summarize strategies
        config = HistoryConfig(
            auto_manage_context=True,
            strategy="summarize",
            summarize_model=groq("llama-3.1-8b-instant"),  # Use faster model for summaries
            store=Sqlite(database_path="./chat.db")
        )
    """
    auto_manage_context: bool = False
    max_context_messages: int = 20
    strategy: str = "smart"
    summarize_model: Optional[object] = None
    store: Optional[Union[StorageType, ConversationHistory, HistoryStore]] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate strategy
        valid_strategies = ["smart", "trim_last", "trim_first", "summarize", "first_last"]
        if self.strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy '{self.strategy}'. Must be one of: {', '.join(valid_strategies)}"
            )

        # Warn if summarize_model is provided but not needed
        if self.summarize_model is not None and self.strategy in ["trim_last", "trim_first", "first_last"]:
            import warnings
            warnings.warn(
                f"summarize_model is provided but will be ignored with strategy='{self.strategy}'. "
                f"Trim strategies don't use LLMs. Remove summarize_model to clean up your config.",
                UserWarning
            )

    def create_history(self) -> Optional[ConversationHistory]:
        """
        Create a ConversationHistory instance from this configuration.

        Returns:
            ConversationHistory instance
        """
        # If store is None, default to InMemory
        if self.store is None:
            # Avoid circular import by importing here if needed
            from peargent.storage import InMemory
            self.store = InMemory()

        # If store is already a ConversationHistory instance, return it
        if isinstance(self.store, ConversationHistory):
            return self.store

        # If store is a HistoryStore (custom storage), wrap it in ConversationHistory
        from peargent.history import HistoryStore
        if isinstance(self.store, HistoryStore):
            return ConversationHistory(store=self.store)

        # If store is a StorageType, create history from it
        if isinstance(self.store, StorageType):
            from peargent import create_history
            return create_history(store_type=self.store)

        raise ValueError(
            f"store must be a StorageType instance, HistoryStore instance, ConversationHistory instance, or None. "
            f"Got: {type(self.store)}"
        )