"""
Test Agent with Long-Term Memory Integration

This script demonstrates how the Agent class integrates with LongTermMemory
to remember facts across conversations.
"""

from peargent import Agent
from peargent.models import AnthropicModel
from peargent.memory import LongTermMemory


def test_agent_with_ltm():
    """Test agent with long-term memory enabled."""
    
    print("=" * 60)
    print("Testing Agent with Long-Term Memory")
    print("=" * 60)
    
    # Create LongTermMemory with auto-extraction enabled
    ltm = LongTermMemory(auto_extract=True)
    
    # Create agent with long-term memory
    agent = Agent(
        name="MemoryBot",
        model=AnthropicModel(model_name="claude-3-5-sonnet-20241022"),
        persona="You are a helpful assistant with excellent memory.",
        description="An assistant that remembers user preferences and facts",
        tools=[],
        long_term_memory=ltm
    )
    
    print("\n1. First conversation - teaching the agent some facts...")
    print("-" * 60)
    
    response1 = agent.run("My name is Alex and I love Python programming. I'm building a web app.")
    print(f"Agent: {response1}")
    
    print(f"\n   Memories stored: {ltm.count()}")
    
    print("\n2. Second conversation - asking about stored facts...")
    print("-" * 60)
    
    response2 = agent.run("What programming language do I like?")
    print(f"Agent: {response2}")
    
    print("\n3. Checking stored memories...")
    print("-" * 60)
    
    all_memories = ltm.retrieve("user preferences", limit=5)
    print(f"   Total memories: {len(all_memories)}")
    for i, mem in enumerate(all_memories, 1):
        print(f"   {i}. {mem.content[:80]}...")
    
    print("\n4. Third conversation - more complex query...")
    print("-" * 60)
    
    response3 = agent.run("Can you remind me what I told you about myself?")
    print(f"Agent: {response3}")
    
    print("\n" + "=" * 60)
    print("✅ Agent with Long-Term Memory test completed!")
    print("=" * 60)
    
    # Cleanup
    ltm.clear()


def test_agent_without_ltm():
    """Test agent without long-term memory for comparison."""
    
    print("\n" + "=" * 60)
    print("Testing Agent WITHOUT Long-Term Memory (for comparison)")
    print("=" * 60)
    
    # Create agent without long-term memory
    agent = Agent(
        name="RegularBot",
        model=AnthropicModel(model_name="claude-3-5-sonnet-20241022"),
        persona="You are a helpful assistant.",
        description="A regular assistant without long-term memory",
        tools=[]
    )
    
    print("\n1. First conversation...")
    response1 = agent.run("My name is Alex and I love Python programming.")
    print(f"Agent: {response1}")
    
    print("\n2. Second conversation (in a new session, agent forgets)...")
    # Clear temporary memory to simulate new session
    agent.temporary_memory = []
    response2 = agent.run("What programming language do I like?")
    print(f"Agent: {response2}")
    
    print("\n" + "=" * 60)
    print("✅ Comparison test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Test with long-term memory
        test_agent_with_ltm()
        
        # Optional: Test without for comparison
        # Uncomment the line below to see the difference
        # test_agent_without_ltm()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
