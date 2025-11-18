"""
Peargent History Module

Provides a unified interface for conversation history and storage backends.
All history-related imports can be accessed from this module.
"""

# Import HistoryConfig from the config module
from ..config.history import HistoryConfig

# Import storage types from core.history
from ..core.history import (
    SessionBuffer,
    File,
    Sqlite,
    Postgresql,
    Redis,
    StorageType,
    ConversationHistory,
    HistoryStore,
    Thread,
    Message,
)

# Define what gets exported from this module
__all__ = [
    'HistoryConfig',
    'SessionBuffer',
    'File',
    'Sqlite',
    'Postgresql',
    'Redis',
    'StorageType',
    'ConversationHistory',
    'HistoryStore',
    'Thread',
    'Message',
]