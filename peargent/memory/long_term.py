"""
Long-term memory system for Peargent agents.

Provides semantic memory storage and retrieval using vector embeddings.
Unlike conversation history (episodic memory), long-term memory stores
facts and knowledge that persist across sessions.

Example:
    >>> from peargent.memory import LongTermMemory
    >>> from peargent.memory.stores import InMemoryVectorStore
    >>> 
    >>> # Create long-term memory
    >>> ltm = LongTermMemory(store=InMemoryVectorStore())
    >>> 
    >>> # Store facts
    >>> ltm.store("User's name is Alex")
    >>> ltm.store("Alex loves Python programming")
    >>> 
    >>> # Retrieve relevant memories
    >>> memories = ltm.retrieve("What is the user's name?")
    >>> print(memories[0].content)  # "User's name is Alex"
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .stores import VectorStore, InMemoryVectorStore
from .stores.base import Memory
from .embeddings import EmbeddingGenerator


class LongTermMemory:
    """
    Long-term memory system for AI agents.
    
    Stores semantic memories (facts, knowledge) that persist across conversations.
    Uses vector embeddings for similarity-based retrieval.
    
    Attributes:
        store: Vector store backend for persistence
        embedding_generator: Generates embeddings for text
        auto_extract: Whether to automatically extract facts from conversations
    """
    
    def __init__(
        self,
        store: Optional[VectorStore] = None,
        embedding_method: str = "simple",
        embedding_model: Optional[str] = None,
        auto_extract: bool = False
    ):
        """
        Initialize long-term memory.
        
        Args:
            store: Vector store backend (default: InMemoryVectorStore)
            embedding_method: "simple", "sentence-transformers", or "openai"
            embedding_model: Model name for embeddings
            auto_extract: Automatically extract facts from conversations
        """
        self.vector_store = store or InMemoryVectorStore()
        self.embedding_generator = EmbeddingGenerator(
            method=embedding_method,
            model=embedding_model
        )
        self.auto_extract = auto_extract
    
    def store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory in long-term memory.
        
        Args:
            content: The text content to store (fact, knowledge, etc.)
            metadata: Optional metadata (source, timestamp, importance, etc.)
            
        Returns:
            str: ID of the stored memory
            
        Example:
            >>> ltm.store("User prefers Python over Java")
            >>> ltm.store("User lives in NYC", metadata={"category": "location"})
        """
        # Generate embedding
        embedding = self.embedding_generator.generate(content)
        
        # Add timestamp if not provided
        if metadata is None:
            metadata = {}
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        
        # Store in vector database
        memory_id = self.vector_store.add(
            content=content,
            embedding=embedding,
            metadata=metadata
        )
        
        return memory_id
    
    def retrieve(
        self,
        query: str,
        limit: int = 5,
        min_similarity: Optional[float] = None
    ) -> List[Memory]:
        """
        Retrieve relevant memories based on semantic similarity.
        
        Args:
            query: Query text to search for
            limit: Maximum number of memories to retrieve
            min_similarity: Minimum similarity score (0-1) to include
            
        Returns:
            List[Memory]: Most relevant memories, ordered by relevance
            
        Example:
            >>> memories = ltm.retrieve("What programming languages does the user like?")
            >>> for mem in memories:
            >>>     print(mem.content)
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate(query)
        
        # Search vector store
        memories = self.vector_store.search(query_embedding, limit=limit)
        
        # Filter by similarity threshold if provided
        if min_similarity is not None:
            # Note: We'd need to add similarity scores to Memory class
            # For now, this is a placeholder
            pass
        
        return memories
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory if found, None otherwise
        """
        return self.vector_store.get(memory_id)
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory from long-term memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.vector_store.delete(memory_id)
    
    def clear(self) -> None:
        """Clear all memories from long-term memory."""
        self.vector_store.clear()
    
    def count(self) -> int:
        """Return the total number of memories stored."""
        return self.vector_store.count()
    
    def extract_and_store(self, conversation: str, metadata: Optional[Dict] = None) -> List[str]:
        """
        Extract facts from a conversation and store them.
        
        This is a placeholder for future LLM-based fact extraction.
        Currently just stores the entire conversation.
        
        Args:
            conversation: Conversation text to extract facts from
            metadata: Optional metadata for extracted facts
            
        Returns:
            List[str]: IDs of stored memories
        """
        # TODO: Implement LLM-based fact extraction
        # For now, just store the conversation as-is
        memory_id = self.vector_store.add(
            content=conversation,
            embedding=self.embedding_generator.generate(conversation),
            metadata=metadata or {}
        )
        return [memory_id]
    
    def format_memories_for_context(self, memories: List[Memory]) -> str:
        """
        Format retrieved memories for inclusion in agent context.
        
        Args:
            memories: List of retrieved memories
            
        Returns:
            str: Formatted string ready to add to agent prompt
        """
        if not memories:
            return ""
        
        formatted = "=== RELEVANT MEMORIES ===\n"
        for i, mem in enumerate(memories, 1):
            formatted += f"{i}. {mem.content}\n"
        formatted += "========================\n"
        
        return formatted
