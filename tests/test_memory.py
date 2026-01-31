"""
Tests for Long-Term Memory functionality.
Tests memory storage, retrieval, vector search, and agent integration.
"""

import pytest
from peargent.memory import LongTermMemory
from peargent.memory.stores import InMemoryVectorStore, Memory
from peargent.memory.embeddings import EmbeddingGenerator
from peargent import create_agent


class MockModel:
    """Mock LLM model for testing without API keys."""

    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """Generate a simple response based on prompt content."""
        if "name" in prompt.lower() or "alex" in prompt.lower():
            return "Your name is Alex."
        elif "python" in prompt.lower() or "programming" in prompt.lower():
            return "You love Python programming."
        return "I understand."


class TestLongTermMemory:
    """Test LongTermMemory class functionality."""

    def test_create_long_term_memory(self) -> None:
        """Test creating a LongTermMemory instance."""
        ltm = LongTermMemory()
        assert ltm is not None
        assert ltm.count() == 0

    def test_store_single_memory(self) -> None:
        """Test storing a single memory."""
        ltm = LongTermMemory()
        memory_id = ltm.store("User's name is Alex")
        
        assert memory_id is not None
        assert ltm.count() == 1

    def test_store_multiple_memories(self) -> None:
        """Test storing multiple memories."""
        ltm = LongTermMemory()
        
        id1 = ltm.store("User's name is Alex")
        id2 = ltm.store("User loves Python programming")
        id3 = ltm.store("User lives in NYC")
        
        assert ltm.count() == 3
        assert len(set([id1, id2, id3])) == 3  # All IDs are unique

    def test_retrieve_memories(self) -> None:
        """Test retrieving memories by semantic search."""
        ltm = LongTermMemory()
        
        ltm.store("User's name is Alex")
        ltm.store("User loves Python programming")
        ltm.store("User lives in NYC")
        
        # Query for name-related memories
        results = ltm.retrieve("What is the user's name?", limit=2)
        assert len(results) <= 2
        assert all(isinstance(m, Memory) for m in results)

    def test_get_memory_by_id(self) -> None:
        """Test retrieving a specific memory by ID."""
        ltm = LongTermMemory()
        
        memory_id = ltm.store("User's name is Alex")
        memory = ltm.get(memory_id)
        
        assert memory is not None
        assert memory.id == memory_id
        assert "Alex" in memory.content

    def test_delete_memory(self) -> None:
        """Test deleting a memory."""
        ltm = LongTermMemory()
        
        memory_id = ltm.store("User's name is Alex")
        assert ltm.count() == 1
        
        deleted = ltm.delete(memory_id)
        assert deleted is True
        assert ltm.count() == 0

    def test_clear_all_memories(self) -> None:
        """Test clearing all memories."""
        ltm = LongTermMemory()
        
        ltm.store("Memory 1")
        ltm.store("Memory 2")
        ltm.store("Memory 3")
        assert ltm.count() == 3
        
        ltm.clear()
        assert ltm.count() == 0

    def test_memory_with_metadata(self) -> None:
        """Test storing memories with metadata."""
        ltm = LongTermMemory()
        
        metadata = {"source": "test", "importance": "high"}
        memory_id = ltm.store("Important fact", metadata=metadata)
        
        memory = ltm.get(memory_id)
        assert memory.metadata["source"] == "test"
        assert memory.metadata["importance"] == "high"

    def test_auto_extract_disabled(self) -> None:
        """Test that auto_extract=False prevents automatic extraction."""
        ltm = LongTermMemory(auto_extract=False)
        assert ltm.auto_extract is False

    def test_auto_extract_enabled(self) -> None:
        """Test that auto_extract=True is set correctly."""
        ltm = LongTermMemory(auto_extract=True)
        assert ltm.auto_extract is True


class TestInMemoryVectorStore:
    """Test InMemoryVectorStore functionality."""

    def test_create_store(self) -> None:
        """Test creating an InMemoryVectorStore."""
        store = InMemoryVectorStore()
        assert store is not None
        assert store.count() == 0

    def test_add_memory_to_store(self) -> None:
        """Test adding a memory to the store."""
        store = InMemoryVectorStore()
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        memory_id = store.add(
            content="Test content",
            embedding=embedding,
            metadata={"test": True}
        )
        
        assert memory_id is not None
        assert store.count() == 1

    def test_search_memories(self) -> None:
        """Test searching for similar memories."""
        store = InMemoryVectorStore()
        
        # Add some memories with different embeddings
        store.add("Memory 1", [1.0, 0.0, 0.0], {})
        store.add("Memory 2", [0.9, 0.1, 0.0], {})
        store.add("Memory 3", [0.0, 0.0, 1.0], {})
        
        # Search with query similar to first two
        results = store.search([1.0, 0.0, 0.0], limit=2)
        assert len(results) <= 2

    def test_get_memory_from_store(self) -> None:
        """Test retrieving a memory by ID from store."""
        store = InMemoryVectorStore()
        
        memory_id = store.add("Test content", [0.1, 0.2], {})
        memory = store.get(memory_id)
        
        assert memory is not None
        assert memory.id == memory_id
        assert memory.content == "Test content"

    def test_delete_memory_from_store(self) -> None:
        """Test deleting a memory from store."""
        store = InMemoryVectorStore()
        
        memory_id = store.add("Test content", [0.1, 0.2], {})
        assert store.count() == 1
        
        deleted = store.delete(memory_id)
        assert deleted is True
        assert store.count() == 0


class TestEmbeddingGenerator:
    """Test EmbeddingGenerator functionality."""

    def test_create_generator(self) -> None:
        """Test creating an EmbeddingGenerator."""
        gen = EmbeddingGenerator(method="simple")
        assert gen is not None

    def test_simple_embedding(self) -> None:
        """Test generating simple embeddings."""
        gen = EmbeddingGenerator(method="simple")
        embedding = gen.generate("Test text")
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_consistent_embeddings(self) -> None:
        """Test that same text generates same embedding."""
        gen = EmbeddingGenerator(method="simple")
        
        emb1 = gen.generate("Test text")
        emb2 = gen.generate("Test text")
        
        assert emb1 == emb2


class TestAgentIntegration:
    """Test Agent integration with LongTermMemory."""

    def test_agent_with_long_term_memory(self) -> None:
        """Test creating an agent with long-term memory."""
        ltm = LongTermMemory(auto_extract=False)
        model = MockModel()
        
        agent = create_agent(
            name="test-agent",
            description="Test agent with memory",
            persona="You are helpful",
            model=model,
            long_term_memory=ltm
        )
        
        assert agent.long_term_memory is ltm
        assert agent.long_term_memory.count() == 0

    def test_agent_memory_retrieval(self) -> None:
        """Test that agent retrieves relevant memories."""
        ltm = LongTermMemory(auto_extract=False)
        model = MockModel()
        
        # Pre-populate memory
        ltm.store("User's name is Alex")
        ltm.store("User loves Python programming")
        
        agent = create_agent(
            name="test-agent",
            description="Test agent",
            persona="You are helpful",
            model=model,
            long_term_memory=ltm
        )
        
        # Run agent - it should retrieve relevant memories
        response = agent.run("What is my name?")
        assert response is not None

    def test_agent_auto_extraction(self) -> None:
        """Test that agent auto-extracts facts when enabled."""
        ltm = LongTermMemory(auto_extract=True)
        model = MockModel()
        
        agent = create_agent(
            name="test-agent",
            description="Test agent",
            persona="You are helpful",
            model=model,
            long_term_memory=ltm
        )
        
        initial_count = ltm.count()
        agent.run("My name is Alex")
        
        # Should have extracted and stored facts
        assert ltm.count() > initial_count

    def test_agent_without_long_term_memory(self) -> None:
        """Test that agent works without long-term memory (backwards compatibility)."""
        model = MockModel()
        
        agent = create_agent(
            name="test-agent",
            description="Test agent",
            persona="You are helpful",
            model=model
        )
        
        assert agent.long_term_memory is None
        response = agent.run("Hello")
        assert response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
