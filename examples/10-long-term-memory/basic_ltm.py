"""
Long-Term Memory Example

This example demonstrates how to use LongTermMemory with an Agent
to remember facts across conversations using semantic search.

Setup:
    Set your Groq API key:
    export GROQ_API_KEY="your-key-here"  # Linux/Mac
    $env:GROQ_API_KEY = "your-key-here"  # Windows PowerShell
    
    Get a free API key at: https://console.groq.com/
"""

from peargent import create_agent, limit_steps
from peargent.models import groq
from peargent.memory import LongTermMemory


def main():
    print("=" * 70)
    print("Long-Term Memory Demo - Agent with Semantic Memory")
    print("=" * 70)
    
    # Create long-term memory with auto-extraction enabled
    # This will automatically extract facts from conversations
    ltm = LongTermMemory(
        auto_extract=True,  # Automatically store facts from conversations
        embedding_method="simple"  # Use simple embeddings (no extra deps needed)
    )
    
    print(f"\n✓ Created LongTermMemory (current count: {ltm.count()})")
    
    # Create agent with long-term memory
    agent = create_agent(
        name="MemoryBot",
        description="An AI assistant with long-term memory",
        persona="You are a helpful assistant with excellent memory. You remember facts about users across conversations.",
        model=groq("llama-3.3-70b-versatile"),  # Free and fast!
        tools=[],
        long_term_memory=ltm,
        stop=limit_steps(3)
    )
    
    print("✓ Created Agent with long-term memory enabled\n")
    
    # Conversation 1: Teaching the agent some facts
    print("-" * 70)
    print("Conversation 1: Teaching the agent about yourself")
    print("-" * 70)
    
    user_input_1 = "Hi! My name is Alex. I'm a Python developer and I love building web applications with FastAPI."
    print(f"You: {user_input_1}\n")
    
    response_1 = agent.run(user_input_1)
    print(f"Agent: {response_1}\n")
    
    print(f"✓ Memories stored: {ltm.count()}")
    
    # Conversation 2: Agent should remember from long-term memory
    print("\n" + "-" * 70)
    print("Conversation 2: Testing memory recall (new session)")
    print("-" * 70)
    
    # Clear temporary memory to simulate a new session
    agent.temporary_memory = []
    
    user_input_2 = "What's my favorite web framework?"
    print(f"You: {user_input_2}\n")
    
    response_2 = agent.run(user_input_2)
    print(f"Agent: {response_2}\n")
    
    # Conversation 3: More specific recall
    print("-" * 70)
    print("Conversation 3: Another query about stored facts")
    print("-" * 70)
    
    agent.temporary_memory = []
    
    user_input_3 = "What do you know about my profession?"
    print(f"You: {user_input_3}\n")
    
    response_3 = agent.run(user_input_3)
    print(f"Agent: {response_3}\n")
    
    # Show what's in long-term memory
    print("-" * 70)
    print("Inspecting Long-Term Memory")
    print("-" * 70)
    
    all_memories = ltm.retrieve("user information", limit=5)
    print(f"\nTotal memories stored: {ltm.count()}")
    print("\nStored memories:")
    for i, mem in enumerate(all_memories, 1):
        print(f"  {i}. {mem.content[:100]}...")
        if mem.metadata:
            print(f"     Metadata: {mem.metadata}")
    
    # Cleanup
    print("\n" + "-" * 70)
    print("Cleanup")
    print("-" * 70)
    ltm.clear()
    print(f"✓ Cleared all memories (count: {ltm.count()})")
    
    print("\n" + "=" * 70)
    print("✅ Demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set GROQ_API_KEY environment variable.")
        print("Get a free key at: https://console.groq.com/")
