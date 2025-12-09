"""
State-based custom router example.

Demonstrates how to create a router that makes intelligent decisions
based on conversation state, last agent output, and tools used.
"""

from peargent import create_agent, create_pool, create_tool
from peargent import RouterResult
from peargent.models import groq


def search_tool(query: str) -> str:
    """Simulated search tool"""
    return f"Found information about {query}: Quantum computing uses quantum mechanics principles for computation."


def analyze_tool(data: str) -> str:
    """Simulated analysis tool"""
    return f"Analysis complete: {data} shows significant technological advancement."


def format_tool(text: str) -> str:
    """Simulated formatting tool"""
    return f"Formatted output: {text}"


# Create agents
researcher = create_agent(
    name="Researcher",
    description="Researches topics using search",
    persona="You are a researcher. Use the search tool to find information.",
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
    description="Analyzes research findings",
    persona="You are an analyst. Use the analyze tool to process information.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="analyze",
        description="Analyze data",
        input_parameters={"data": str},
        call_function=analyze_tool
    )]
)

writer = create_agent(
    name="Writer",
    description="Writes formatted content",
    persona="You are a writer. Create clear, well-formatted content.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="format",
        description="Format text",
        input_parameters={"text": str},
        call_function=format_tool
    )]
)


# Define state-based router
def intelligent_state_router(state, call_count, last_result):
    """
    Intelligent router that makes decisions based on conversation state.

    This router analyzes:
    - Conversation history from state
    - Last agent's output
    - Tools that were used
    - Current execution count

    Args:
        state: Shared state containing conversation history
        call_count: Number of agents executed so far
        last_result: Dictionary with info about the last agent's execution
                    - "agent": Name of the last agent
                    - "output": Output from the last agent
                    - "tools_used": List of tool names used

    Returns:
        RouterResult: Contains next agent name or None to stop
    """
    # First agent always starts with research
    if call_count == 0:
        print("\n[Router] Starting workflow -> Researcher")
        return RouterResult("Researcher")

    # Get information about last execution
    if last_result:
        last_agent = last_result.get("agent", "")
        last_output = last_result.get("output", "")
        tools_used = last_result.get("tools_used", [])

        print(f"\n[Router] Last agent: {last_agent}")
        print(f"[Router] Tools used: {tools_used}")
        print(f"[Router] Output preview: {last_output[:100]}...")

        # If researcher just finished and used search tool, go to analyst
        if last_agent == "Researcher" and "search" in tools_used:
            print("[Router] Researcher used search -> routing to Analyst")
            return RouterResult("Analyst")

        # If analyst finished with analysis, go to writer
        if last_agent == "Analyst" and "analyze" in tools_used:
            print("[Router] Analyst completed analysis -> routing to Writer")
            return RouterResult("Writer")

        # If writer finished, we're done
        if last_agent == "Writer":
            print("[Router] Writer completed -> stopping workflow")
            return RouterResult(None)

        # Check conversation state for keywords
        last_message = state.history[-1] if state.history else None
        if last_message and "content" in last_message:
            content = str(last_message["content"]).lower()

            # Route based on content keywords
            if "research" in content and last_agent != "Researcher":
                print("[Router] Content needs research -> routing to Researcher")
                return RouterResult("Researcher")

            if "analysis" in content and last_agent != "Analyst":
                print("[Router] Content needs analysis -> routing to Analyst")
                return RouterResult("Analyst")

    # Default fallback: stop after 3 iterations
    if call_count >= 3:
        print(f"\n[Router] Max iterations reached -> stopping")
        return RouterResult(None)

    # Fallback to researcher
    print(f"\n[Router] Fallback routing -> Researcher")
    return RouterResult("Researcher")


# Create pool with state-based router
pool = create_pool(
    agents=[researcher, analyst, writer],
    router=intelligent_state_router,
    max_iter=5
)


if __name__ == "__main__":
    # Run the pool
    print("=== State-Based Router Example ===\n")
    result = pool.run("Tell me about quantum computing and analyze its potential")
    print("\n=== Final Result ===")
    print(result)
