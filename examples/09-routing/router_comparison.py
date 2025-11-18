"""
Router comparison example.

Demonstrates all three routing approaches:
1. Custom function-based router
2. Built-in round-robin router (default)
3. LLM-based intelligent routing agent
"""

from peargent import create_agent, create_pool, create_routing_agent, create_tool
from peargent.core.router import RouterResult, round_robin_router
from peargent.models import groq


def mock_tool(input: str) -> str:
    """Mock tool for demonstration"""
    return f"Processed: {input}"


# Create reusable agents
def create_test_agents():
    """Create a set of agents for testing different routers"""
    agent1 = create_agent(
        name="Agent1",
        description="First agent in the workflow",
        persona="You are agent 1. Process the input and pass it forward.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[]
    )

    agent2 = create_agent(
        name="Agent2",
        description="Second agent in the workflow",
        persona="You are agent 2. Refine the input from agent 1.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[]
    )

    agent3 = create_agent(
        name="Agent3",
        description="Third agent in the workflow",
        persona="You are agent 3. Finalize the output.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[]
    )

    return [agent1, agent2, agent3]


# ============================================================================
# APPROACH 1: Custom Function-Based Router
# ============================================================================

def custom_function_router(state, call_count, last_result):
    """
    Custom router with full control over routing logic.

    You can implement any logic here based on:
    - state: Conversation history and shared state
    - call_count: Number of agents executed
    - last_result: Previous agent's output and tools used
    """
    if call_count == 0:
        return RouterResult("Agent1")
    elif call_count == 1:
        return RouterResult("Agent2")
    elif call_count == 2:
        return RouterResult("Agent3")
    return RouterResult(None)


def test_custom_router():
    """Test pool with custom function-based router"""
    print("\n" + "=" * 60)
    print("APPROACH 1: Custom Function-Based Router")
    print("=" * 60)

    agents = create_test_agents()
    pool = create_pool(
        agents=agents,
        router=custom_function_router,
        max_iter=3
    )

    result = pool.run("Process this text through custom routing")
    print("\nResult:", result)


# ============================================================================
# APPROACH 2: Built-in Round-Robin Router (Default)
# ============================================================================

def test_round_robin_router():
    """Test pool with default round-robin router"""
    print("\n" + "=" * 60)
    print("APPROACH 2: Built-in Round-Robin Router (Default)")
    print("=" * 60)

    agents = create_test_agents()

    # Method 1: Automatic (default behavior)
    pool = create_pool(
        agents=agents,
        max_iter=3
    )

    # Method 2: Explicit round-robin
    # pool = create_pool(
    #     agents=agents,
    #     router=round_robin_router([a.name for a in agents]),
    #     max_iter=3
    # )

    result = pool.run("Process this text with round-robin routing")
    print("\nResult:", result)


# ============================================================================
# APPROACH 3: LLM-Based Intelligent Routing Agent
# ============================================================================

def test_llm_router():
    """Test pool with LLM-based intelligent router"""
    print("\n" + "=" * 60)
    print("APPROACH 3: LLM-Based Intelligent Routing Agent")
    print("=" * 60)

    agents = create_test_agents()

    # Create intelligent routing agent
    router = create_routing_agent(
        name="IntelligentRouter",
        model=groq("llama-3.3-70b-versatile"),
        persona="""You are an intelligent router that decides which agent should act next.

        Available agents:
        - Agent1: Initial processing
        - Agent2: Refinement
        - Agent3: Finalization

        Choose the most appropriate agent based on the conversation history.
        Return STOP when the task is complete.""",
        agents=["Agent1", "Agent2", "Agent3"]
    )

    pool = create_pool(
        agents=agents,
        router=router,
        max_iter=4
    )

    result = pool.run("Process this text with intelligent LLM routing")
    print("\nResult:", result)


# ============================================================================
# COMPARISON SUMMARY
# ============================================================================

def print_comparison_summary():
    """Print summary of router approaches"""
    print("\n" + "=" * 60)
    print("ROUTER COMPARISON SUMMARY")
    print("=" * 60)
    print("""
1. Custom Function-Based Router:
   ✓ Full control over routing logic
   ✓ Can use state, call_count, and last_result
   ✓ Deterministic and predictable
   ✓ No LLM costs for routing decisions
   ✓ Best for: Fixed workflows, conditional logic, rules-based routing

2. Built-in Round-Robin Router:
   ✓ Simplest approach (default behavior)
   ✓ Cycles through agents sequentially
   ✓ No configuration needed
   ✓ Zero overhead
   ✓ Best for: Simple sequential workflows, testing

3. LLM-Based Routing Agent:
   ✓ Intelligent, context-aware decisions
   ✓ Adapts to conversation flow
   ✓ Can handle complex routing scenarios
   ✗ Incurs LLM API costs for each routing decision
   ✓ Best for: Dynamic workflows, complex multi-agent systems
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ROUTER COMPARISON DEMO")
    print("=" * 60)

    # Test each approach
    test_custom_router()
    test_round_robin_router()
    test_llm_router()

    # Print comparison
    print_comparison_summary()
