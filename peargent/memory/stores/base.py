"""
Base class for vector stores.

Defines the interface that all vector store implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Memory:
    """Represents a single memory stored in long-term memory."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary format."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata or {}
        }


class VectorStore(ABC):
    """
    Abstract base class for vector store backends.
    
    All vector store implementations (ChromaDB, Pinecone, etc.) must inherit from this
    and implement these methods.
    """
    
    @abstractmethod
    def add(self, content: str, embedding: List[float], metadata: Optional[Dict] = None) -> str:
        """
        Add a memory to the store.
        
        Args:
            content: The text content to store
            embedding: Vector embedding of the content
            metadata: Optional metadata (timestamp, source, etc.)
            
        Returns:
            str: ID of the stored memory
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], limit: int = 5) -> List[Memory]:
        """
        Search for similar memories using vector similarity.
        
        Args:
            query_embedding: Vector embedding of the query
            limit: Maximum number of results to return
            
        Returns:
            List[Memory]: Most similar memories, ordered by relevance
        """
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory from the store.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all memories from the store."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Return the total number of memories stored."""
        pass
