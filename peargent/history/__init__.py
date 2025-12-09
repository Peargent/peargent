"""
History module for peargent.

Provides conversation history management with multiple storage backends.
"""

# Import base classes and storage implementations from peargent.storage
from peargent.storage import (
    Message,
    Thread,
    HistoryStore,
    FunctionalHistoryStore,
    InMemoryHistoryStore,
    FileHistoryStore,
    PostgreSQLHistoryStore,
    SQLiteHistoryStore,
    RedisHistoryStore,
    InMemory,
    File,
    Sqlite,
    Postgresql,
    Redis,
)

# Export high-level interface
from .history import ConversationHistory
from peargent.config import HistoryConfig

__all__ = [
    'Message',
    'Thread',
    'HistoryStore',
    'FunctionalHistoryStore',
    'InMemoryHistoryStore',
    'FileHistoryStore',
    'PostgreSQLHistoryStore',
    'SQLiteHistoryStore',
    'RedisHistoryStore',
    'ConversationHistory',
    'InMemory',
    'File',
    'Sqlite',
    'Postgresql',
    'Redis',
    'HistoryConfig',
]
