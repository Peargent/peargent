"""
Custom Router with Agent Access Example

Demonstrates how to access agent information in custom router functions
using state.agents to make intelligent routing decisions.
"""

from peargent import create_agent, create_pool, create_tool
from peargent import RouterResult
from peargent.models import groq


def search_tool(query: str) -> str:
    """Simulated search tool"""
    return f"Search results for '{query}': Found relevant information."


def analyze_tool(data: str) -> str:
    """Simulated analysis tool"""
    return f"Analysis complete: {data}"


def format_tool(text: str) -> str:
    """Simulated formatting tool"""
    return f"Formatted output: {text}"


# Create agents
researcher = create_agent(
    name="Researcher",
    description="Gathers information using search tools",
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
    description="Analyzes data and extracts insights",
    persona="You are an analyst. Analyze the provided data.",
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
    description="Creates formatted content",
    persona="You are a writer. Format the content clearly.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[create_tool(
        name="format",
        description="Format text",
        input_parameters={"text": str},
        call_function=format_tool
    )]
)


def intelligent_router_with_agent_access(state, call_count, last_result):
    """
    Custom router that accesses agent information via state.agents.

    Args:
        state: State object with:
            - state.agents: Dict[str, Agent] - All available agents
            - state.history: List of conversation messages
            - state.get(key), state.set(key, value): Custom storage
        call_count: Number of agents executed so far
        last_result: Dict with last agent's execution info

    Returns:
        RouterResult with next agent name or None to stop
    """

    # ========================================================================
    # ACCESS ALL AGENTS: List all available agents and their properties
    # ========================================================================
    print("\n" + "="*70)
    print("AVAILABLE AGENTS (via state.agents):")
    print("="*70)

    for agent_name, agent_obj in state.agents.items():
        print(f"\nAgent: {agent_name}")
        print(f"  Description: {agent_obj.description}")
        print(f"  Tools: {list(agent_obj.tools.keys())}")
        print(f"  Model: {agent_obj.model}")
        print(f"  Persona (first 80 chars): {agent_obj.persona[:80]}...")


    # ========================================================================
    # ROUTING LOGIC: Use agent information to make decisions
    # ========================================================================

    # Safety: Stop after max iterations
    if call_count >= 10:
        print("\n[Router] Max iterations reached → STOP")
        return RouterResult(None)


    # First call: Find agent with search tool
    if call_count == 0:
        print("\n[Router] Finding agent with 'search' tool...")
        for agent_name, agent_obj in state.agents.items():
            if "search" in agent_obj.tools:
                print(f"[Router] Found! Routing to {agent_name}")
                return RouterResult(agent_name)

        # Fallback if no search tool found
        print("[Router] No agent with search tool, using first agent")
        return RouterResult(list(state.agents.keys())[0])


    # Subsequent calls: Route based on tools used
    if last_result:
        last_agent = last_result.get("agent", "")
        tools_used = last_result.get("tools_used", [])

        print(f"\n[Router] Last agent: {last_agent}")
        print(f"[Router] Tools used: {tools_used}")

        # If search was used, find agent with analyze tool
        if "search" in tools_used:
            print("[Router] Search completed, finding agent with 'analyze' tool...")
            for agent_name, agent_obj in state.agents.items():
                if "analyze" in agent_obj.tools:
                    print(f"[Router] Found! Routing to {agent_name}")
                    return RouterResult(agent_name)

        # If analyze was used, find agent with format tool
        if "analyze" in tools_used:
            print("[Router] Analysis completed, finding agent with 'format' tool...")
            for agent_name, agent_obj in state.agents.items():
                if "format" in agent_obj.tools:
                    print(f"[Router] Found! Routing to {agent_name}")
                    return RouterResult(agent_name)

        # If format was used, we're done
        if "format" in tools_used:
            print("[Router] Formatting completed → STOP")
            return RouterResult(None)


    # Fallback: Stop
    print("\n[Router] No routing logic matched → STOP")
    return RouterResult(None)


# Create pool with custom router
pool = create_pool(
    agents=[researcher, analyst, writer],
    router=intelligent_router_with_agent_access,
    max_iter=5
)


if __name__ == "__main__":
    print("="*70)
    print("CUSTOM ROUTER WITH AGENT ACCESS EXAMPLE")
    print("="*70)

    result = pool.run("Research AI trends, analyze the data, and format a summary")

    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(result)
