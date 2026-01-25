"""
In-memory vector store implementation.

Simple dictionary-based storage for testing and development.
Uses cosine similarity for vector search.
"""

import uuid
from typing import List, Dict, Optional
import numpy as np

from .base import VectorStore, Memory


class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store using dictionaries.
    
    Good for:
    - Testing and development
    - Small-scale applications
    - Temporary sessions
    
    Not suitable for:
    - Production (data lost when program ends)
    - Large datasets
    - Concurrent access
    """
    
    def __init__(self):
        """Initialize empty memory store."""
        self.memories: Dict[str, Memory] = {}
    
    def add(self, content: str, embedding: List[float], metadata: Optional[Dict] = None) -> str:
        """Add a memory to the store."""
        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        self.memories[memory_id] = memory
        return memory_id
    
    def search(self, query_embedding: List[float], limit: int = 5) -> List[Memory]:
        """
        Search for similar memories using cosine similarity.
        
        Args:
            query_embedding: Vector embedding of the query
            limit: Maximum number of results to return
            
        Returns:
            List[Memory]: Most similar memories, ordered by similarity score
        """
        if not self.memories:
            return []
        
        # Convert query to numpy array
        query_vec = np.array(query_embedding)
        
        # Calculate similarity scores for all memories
        scores = []
        for memory in self.memories.values():
            if memory.embedding:
                mem_vec = np.array(memory.embedding)
                # Cosine similarity
                query_norm = np.linalg.norm(query_vec)
                mem_norm = np.linalg.norm(mem_vec)
                if query_norm > 0 and mem_norm > 0:
                    similarity = np.dot(query_vec, mem_vec) / (query_norm * mem_norm)
                    scores.append((similarity, memory))
        
        # Sort by similarity (highest first)
        scores.sort(reverse=True, key=lambda x: x[0])
        
        # Return top N memories
        return [memory for _, memory in scores[:limit]]
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a specific memory by ID."""
        return self.memories.get(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory from the store."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memories from the store."""
        self.memories.clear()
    
    def count(self) -> int:
        """Return the total number of memories stored."""
        return len(self.memories)
