"""
Long-term memory module for Peargent.

Provides semantic memory storage and retrieval for AI agents.

Example usage:
    >>> from peargent.memory import LongTermMemory
    >>> from peargent.memory.stores import InMemoryVectorStore
    >>> 
    >>> # Create memory
    >>> ltm = LongTermMemory(store=InMemoryVectorStore())
    >>> 
    >>> # Store facts
    >>> ltm.store("User's favorite language is Python")
    >>> 
    >>> # Retrieve memories
    >>> memories = ltm.retrieve("What language does user like?")
"""

from .long_term import LongTermMemory
from .stores import VectorStore, InMemoryVectorStore
from .stores.base import Memory
from .embeddings import EmbeddingGenerator

__all__ = [
    'LongTermMemory',
    'VectorStore',
    'InMemoryVectorStore',
    'Memory',
    'EmbeddingGenerator',
]

# Try to import optional stores
try:
    from .stores.chroma import ChromaVectorStore
    __all__.append('ChromaVectorStore')
except ImportError:
    pass
