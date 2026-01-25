# test_pear_serialization.py

"""Test script to verify the enhanced .pear file serialization."""

import json
from peargent import create_tool, create_agent, create_pool, create_routing_agent
from peargent.atlas import create_pear


# DECORATOR STYLE - source code is captured
@create_tool()
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression and return the result."""
    return eval(expression)


@create_tool(timeout=5.0, max_retries=2)
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"


# FUNCTION STYLE - define function separately, then wrap
def greet_user(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

greet_tool = create_tool(
    name="greet",
    description="Greet a user",
    input_parameters={"name": str},
    call_function=greet_user
)


# Create agents
math_agent = create_agent(
    name="MathAgent",
    description="An agent that can do mathematical calculations",
    persona="You are a helpful math assistant.",
    tools=[calculate, greet_tool]  # Mix both styles
)

search_agent = create_agent(
    name="SearchAgent",
    description="An agent that can search the web",
    persona="You are a search assistant.",
    tools=[search_web]
)


# Define a routing function
def my_router(state, call_count, last_result):
    """Custom routing logic based on the query."""
    from peargent import RouterResult
    if call_count == 0:
        return RouterResult("MathAgent")
    return RouterResult(None)


# Create a pool with function-based router
pool = create_pool(
    agents=[math_agent, search_agent],
    router=my_router,
    max_iter=3
)


# Test serialization
print("=" * 60)
print("TOOL SERIALIZATION")
print("=" * 60)
print(json.dumps(calculate.to_dict(), indent=2))

print("\n" + "=" * 60)
print("AGENT SERIALIZATION")
print("=" * 60)
print(json.dumps(math_agent.to_dict(), indent=2))

print("\n" + "=" * 60)
print("POOL SERIALIZATION")
print("=" * 60)
print(json.dumps(pool.to_dict(), indent=2))

print("\n" + "=" * 60)
print("CREATE .PEAR FILE")
print("=" * 60)
create_pear(pool, "test_output.pear")

# Read and display the .pear file
with open("test_output.pear", "r") as f:
    pear_data = json.load(f)
    print(json.dumps(pear_data, indent=2))

print("\n✅ All serialization tests passed!")
