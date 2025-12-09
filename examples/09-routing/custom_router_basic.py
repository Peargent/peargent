"""
Basic custom router example.

Demonstrates how to create a simple sequential router that
routes to agents in a specific order.
"""

from peargent import create_agent, create_pool, create_tool
from peargent import RouterResult
from peargent.models import groq


def search_tool(query: str) -> str:
    """Simulated search tool"""
    return f"Search results for '{query}': Renewable energy includes solar, wind, and hydro power."


def analyze_tool(text: str) -> str:
    """Simulated analysis tool"""
    return f"Analysis: The text discusses renewable energy sources and their benefits."


# Create agents
researcher = create_agent(
    name="Researcher",
    description="Research agent that gathers information",
    persona="You are a researcher. Use the search tool to gather information about topics.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="search",
        description="Search for information",
        input_parameters={"query": str},
        call_function=search_tool
    )]
)

analyst = create_agent(
    name="Analyst",
    description="Analysis agent that processes information",
    persona="You are an analyst. Analyze the information provided and extract key insights.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="analyze",
        description="Analyze text",
        input_parameters={"text": str},
        call_function=analyze_tool
    )]
)

summarizer = create_agent(
    name="Summarizer",
    description="Summary agent that creates concise summaries",
    persona="You are a summarizer. Create a clear, concise summary of the information provided.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[]
)


# Define custom sequential router
def simple_sequential_router(state, call_count, last_result):
    """
    Simple sequential router that routes agents in order.

    Args:
        state: Shared state containing conversation history
        call_count: Number of agents executed so far
        last_result: Dictionary with info about the last agent's execution

    Returns:
        RouterResult: Contains next agent name or None to stop
    """
    if call_count == 0:
        return RouterResult("Researcher")
    elif call_count == 1:
        return RouterResult("Analyst")
    elif call_count == 2:
        return RouterResult("Summarizer")

    # Stop after all agents have run
    return RouterResult(None)


# Create pool with custom router
pool = create_pool(
    agents=[researcher, analyst, summarizer],
    router=simple_sequential_router,
    max_iter=3
)


if __name__ == "__main__":
    # Run the pool
    print("=== Sequential Router Example ===\n")
    result = pool.run("What are the benefits of renewable energy?")
    print("\n=== Final Result ===")
    print(result)
