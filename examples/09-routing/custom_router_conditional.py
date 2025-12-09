"""
Conditional custom router example.

Demonstrates how to create a router that makes decisions based on
call count and agent list.
"""

from peargent import create_agent, create_pool, create_tool
from peargent import RouterResult
from peargent.models import groq


def research_tool(topic: str) -> str:
    """Simulated research tool"""
    return f"Research findings on {topic}: AI is transforming multiple industries including healthcare, finance, and transportation."


def writing_tool(content: str) -> str:
    """Simulated writing tool"""
    return f"Formatted content: {content}"


# Create agents
researcher = create_agent(
    name="Researcher",
    description="Conducts research on topics",
    persona="You are a research expert. Use tools to gather information on the given topic.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="research",
        description="Research a topic",
        input_parameters={"topic": str},
        call_function=research_tool
    )]
)

writer = create_agent(
    name="Writer",
    description="Writes content based on research",
    persona="You are a technical writer. Transform research findings into clear, engaging content.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="write",
        description="Format and write content",
        input_parameters={"content": str},
        call_function=writing_tool
    )]
)


# Define conditional router
def conditional_router(state, call_count, last_result):
    """
    Conditional router that routes through a predefined agent list.

    Args:
        state: Shared state containing conversation history
        call_count: Number of agents executed so far
        last_result: Dictionary with info about the last agent's execution

    Returns:
        RouterResult: Contains next agent name or None to stop
    """
    # Define routing sequence
    agents = ["Researcher", "Writer"]

    # Route to next agent if within bounds
    if call_count < len(agents):
        next_agent = agents[call_count]
        print(f"\n[Router] Routing to {next_agent} (call #{call_count})")
        return RouterResult(next_agent)

    # Stop when all agents have executed
    print(f"\n[Router] All agents completed, stopping workflow")
    return RouterResult(None)


# Create pool with conditional router
pool = create_pool(
    agents=[researcher, writer],
    router=conditional_router,
    max_iter=4
)


if __name__ == "__main__":
    # Run the pool
    print("=== Conditional Router Example ===\n")
    result = pool.run("Research and write about AI in healthcare")
    print("\n=== Final Result ===")
    print(result)
