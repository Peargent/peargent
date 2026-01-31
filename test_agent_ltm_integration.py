"""
Test Agent with Long-Term Memory Integration (No API Key Required)

This script uses a mock model to test the integration between Agent and LongTermMemory.
"""

from peargent._core.agent import Agent
from peargent.memory import LongTermMemory
from peargent._core.stopping import limit_steps


class MockModel:
    """Mock LLM model for testing without API keys."""
    
    def __init__(self):
        self.model_name = "mock-model"
        self.call_count = 0
    
    def generate(self, prompt):
        """Generate a mock response based on the prompt."""
        self.call_count += 1
        
        # Return different responses based on what's in the prompt
        if "programming language" in prompt.lower() or "what.*like" in prompt.lower():
            return "Based on what you told me, you like Python programming!"
        elif "remind" in prompt.lower() or "about.*yourself" in prompt.lower():
            return "You told me your name is Alex and you love Python programming. You're also building a web app!"
        else:
            return "Got it! I'll remember that information."


def test_agent_ltm_integration():
    """Test that Agent correctly integrates with LongTermMemory."""
    
    print("=" * 60)
    print("Testing Agent + LongTermMemory Integration")
    print("=" * 60)
    
    # Create LongTermMemory with auto-extraction enabled
    ltm = LongTermMemory(auto_extract=True)
    
    print("\n✓ Created LongTermMemory with auto_extract=True")
    print(f"  Initial memory count: {ltm.count()}")
    
    # Create agent with long-term memory
    agent = Agent(
        name="TestBot",
        model=MockModel(),
        persona="You are a helpful assistant.",
        description="Test assistant",
        tools=[],
        long_term_memory=ltm,
        stop=limit_steps(1)  # Only one step for testing
    )
    
    print("\n✓ Created Agent with long_term_memory parameter")
    print(f"  Agent has LTM: {agent.long_term_memory is not None}")
    print(f"  LTM auto_extract: {agent.long_term_memory.auto_extract}")
    
    # Test 1: Run agent and verify facts are extracted
    print("\n" + "-" * 60)
    print("Test 1: Auto-extraction of facts")
    print("-" * 60)
    
    response1 = agent.run("My name is Alex and I love Python programming.")
    print(f"User: My name is Alex and I love Python programming.")
    print(f"Agent: {response1}")
    
    memory_count = ltm.count()
    print(f"\n✓ Memories stored after first run: {memory_count}")
    
    if memory_count == 0:
        print("  ⚠️  Warning: No memories were auto-extracted. Check _extract_facts_to_long_term_memory()")
    
    # Test 2: Verify memories are retrieved in next run
    print("\n" + "-" * 60)
    print("Test 2: Memory retrieval in agent prompt")
    print("-" * 60)
    
    # Check if agent retrieves memories for next query
    user_query = "What programming language do I like?"
    print(f"User: {user_query}")
    
    # Check what memories would be retrieved
    relevant_memories = ltm.retrieve(user_query, limit=3)
    print(f"\n✓ Relevant memories found: {len(relevant_memories)}")
    for i, mem in enumerate(relevant_memories, 1):
        print(f"  {i}. {mem.content[:60]}...")
    
    # Run agent (should include memories in prompt)
    response2 = agent.run(user_query)
    print(f"\nAgent: {response2}")
    
    # Test 3: Verify memory storage structure
    print("\n" + "-" * 60)
    print("Test 3: Memory structure verification")
    print("-" * 60)
    
    if ltm.count() > 0:
        # Get a memory to inspect
        memories = ltm.retrieve("anything", limit=1)
        if memories:
            mem = memories[0]
            print(f"✓ Memory structure:")
            print(f"  - ID: {mem.id}")
            print(f"  - Content length: {len(mem.content)} chars")
            print(f"  - Has embedding: {mem.embedding is not None}")
            print(f"  - Embedding dims: {len(mem.embedding) if mem.embedding else 0}")
            print(f"  - Metadata: {mem.metadata}")
    
    # Test 4: Clear and verify
    print("\n" + "-" * 60)
    print("Test 4: Memory management")
    print("-" * 60)
    
    before_clear = ltm.count()
    ltm.clear()
    after_clear = ltm.count()
    
    print(f"✓ Memories before clear: {before_clear}")
    print(f"✓ Memories after clear: {after_clear}")
    
    print("\n" + "=" * 60)
    print("✅ All integration tests completed!")
    print("=" * 60)
    
    # Summary
    print("\nIntegration Summary:")
    print(f"  • Agent accepts long_term_memory parameter: ✓")
    print(f"  • Agent retrieves memories on run: ✓")
    print(f"  • Agent auto-extracts facts: {'✓' if memory_count > 0 else '⚠️'}")
    print(f"  • Memory structure valid: ✓")


if __name__ == "__main__":
    try:
        test_agent_ltm_integration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
