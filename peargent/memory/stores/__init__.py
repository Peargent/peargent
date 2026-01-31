"""
Vector store backends for long-term memory.
"""

from .base import VectorStore, Memory
from .in_memory import InMemoryVectorStore

# Try to import ChromaDB store
try:
    from .chroma import ChromaVectorStore
    CHROMA_AVAILABLE = True
except ImportError:
    ChromaVectorStore = None
    CHROMA_AVAILABLE = False

__all__ = [
    'VectorStore',
    'Memory',
    'InMemoryVectorStore',
]

if CHROMA_AVAILABLE:
    __all__.append('ChromaVectorStore')
