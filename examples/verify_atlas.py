import sys
import os

# Add parent directory to path to import peargent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from peargent import create_agent, create_pool, create_tool
from peargent.atlas import create_pear

# Create a sample tool
@create_tool(name="calculator", description="Performs basic math")
def calculator(expression: str) -> float:
    return eval(expression)

# Create agents
agent1 = create_agent(
    name="MathAgent",
    description="An agent that does math",
    persona="You are a mathematician.",
    tools=[calculator],
    model="gpt-4" # Mock model string
)

agent2 = create_agent(
    name="WriterAgent",
    description="An agent that writes",
    persona="You are a writer.",
    model="claude-3-opus" # Mock model string
)

# 1. Export single agent
print("Exporting single agent...")
create_pear(agent1, "math_agent.pear")

# 2. Export pool
print("Exporting pool...")
pool = create_pool(agents=[agent1, agent2], max_iter=3)
create_pear(pool, "agent_pool.pear")

# 3. Export collection (list)
print("Exporting collection...")
create_pear([agent1, agent2], "agent_collection.pear")

print("Done! Check the .pear files.")
