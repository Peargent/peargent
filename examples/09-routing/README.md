# Custom Router Examples

This directory demonstrates how to create custom routers for multi-agent workflows in Peargent.

## Overview

Peargent provides three ways to route agents in a pool:

1. **Custom Function-Based Router** - Full control with your own routing logic
2. **Built-in Round-Robin Router** - Default sequential routing (automatic)
3. **LLM-Based Routing Agent** - Intelligent AI-powered routing decisions

## Files

| File | Description | Key Concepts |
|------|-------------|--------------|
| `custom_router_basic.py` | Simple sequential router | RouterResult, basic routing |
| `custom_router_conditional.py` | Conditional routing based on agent list | call_count, agent sequencing |
| `custom_router_statebased.py` | Intelligent routing using state | state.history, tools_used, context-aware routing |
| `router_comparison.py` | Side-by-side comparison of all three approaches | round_robin_router, create_routing_agent |

## Router Function Signature

A custom router function must follow this signature:

```python
from peargent import RouterResult

def custom_router(state, call_count, last_result) -> RouterResult:
    """
    Args:
        state: Shared State object with conversation history
        call_count: Number of agents executed so far (starts at 0)
        last_result: Dictionary with info about last agent:
                    - "agent": Name of the last agent
                    - "output": Output from the last agent
                    - "tools_used": List of tool names used

    Returns:
        RouterResult: Contains next_agent_name (str) or None to stop
    """
    # Your routing logic here
    return RouterResult("next_agent_name")  # or RouterResult(None) to stop
```

## Quick Start

### 1. Basic Sequential Router

```python
from peargent import create_pool
from peargent import RouterResult

def simple_router(state, call_count, last_result):
    if call_count == 0:
        return RouterResult("Researcher")
    elif call_count == 1:
        return RouterResult("Writer")
    return RouterResult(None)

pool = create_pool(
    agents=[researcher, writer],
    router=simple_router,
    max_iter=2
)
```

### 2. State-Based Router

```python
def intelligent_router(state, call_count, last_result):
    # Check what tools were used
    if last_result and "search" in last_result.get("tools_used", []):
        return RouterResult("Analyst")

    # Check conversation history
    last_message = state.history[-1] if state.history else None
    if last_message and "analyze" in str(last_message.get("content", "")):
        return RouterResult("Writer")

    # Default to researcher
    return RouterResult("Researcher") if call_count == 0 else RouterResult(None)
```

### 3. LLM-Based Router

```python
from peargent import create_routing_agent

router = create_routing_agent(
    name="router",
    model=groq("llama-3.3-70b-versatile"),
    persona="You decide which agent acts next based on the conversation",
    agents=["Researcher", "Analyst", "Writer"]
)

pool = create_pool(
    agents=[researcher, analyst, writer],
    router=router
)
```

## Running the Examples

```bash
# Basic sequential routing
python examples/09-routing/custom_router_basic.py

# Conditional routing
python examples/09-routing/custom_router_conditional.py

# State-based routing
python examples/09-routing/custom_router_statebased.py

# Compare all three approaches
python examples/09-routing/router_comparison.py
```

## When to Use Each Approach

### Custom Function-Based Router
**Best for:**
- Fixed, deterministic workflows
- Rules-based routing logic
- Conditional routing based on state/output
- Cost-sensitive applications (no LLM calls for routing)

**Example use cases:**
- Research → Analysis → Writing pipeline
- Validation → Processing → Formatting workflow
- Error handling with fallback agents

### Round-Robin Router (Default)
**Best for:**
- Simple sequential workflows
- Testing and prototyping
- Scenarios where agent order doesn't matter

**Example use cases:**
- Processing items in a queue
- Simple multi-step pipelines
- Load distribution across similar agents

### LLM-Based Routing Agent
**Best for:**
- Complex, dynamic workflows
- Context-aware routing decisions
- Adaptive multi-agent systems

**Example use cases:**
- Customer support with specialized agents
- Complex research workflows
- Dynamic task decomposition

## Key Concepts

### RouterResult

The `RouterResult` class is used to specify routing decisions:

```python
from peargent import RouterResult

# Route to a specific agent
return RouterResult("AgentName")

# Stop the workflow
return RouterResult(None)
```

### State Object

The `state` parameter provides access to:
- `state.history`: List of all messages in the conversation
- `state.data`: Dictionary for sharing data between agents

```python
def router(state, call_count, last_result):
    # Access conversation history
    messages = state.history

    # Read shared data
    custom_data = state.data.get("key", "default")

    return RouterResult("NextAgent")
```

### Last Result Dictionary

The `last_result` parameter contains:
```python
{
    "agent": "AgentName",           # Name of the last agent
    "output": "Agent output text",   # What the agent returned
    "tools_used": ["tool1", "tool2"] # Tools that were called
}
```

## Advanced Patterns

### Pattern 1: Tool-Based Routing

Route based on which tools were used:

```python
def tool_based_router(state, call_count, last_result):
    if last_result:
        tools = last_result.get("tools_used", [])

        if "search" in tools:
            return RouterResult("Analyst")
        elif "analyze" in tools:
            return RouterResult("Writer")

    return RouterResult("Researcher") if call_count == 0 else RouterResult(None)
```

### Pattern 2: Content-Based Routing

Route based on agent output content:

```python
def content_based_router(state, call_count, last_result):
    if last_result:
        output = last_result.get("output", "").lower()

        if "error" in output or "failed" in output:
            return RouterResult("ErrorHandler")
        elif "complete" in output:
            return RouterResult(None)  # Stop

    return RouterResult("MainAgent")
```

### Pattern 3: Hybrid Routing

Combine multiple routing strategies:

```python
def hybrid_router(state, call_count, last_result):
    # First agent always starts
    if call_count == 0:
        return RouterResult("InitialAgent")

    # Check tools used
    if last_result and "validation" in last_result.get("tools_used", []):
        return RouterResult("Validator")

    # Check conversation state
    if len(state.history) > 10:
        return RouterResult("Summarizer")

    # Default sequence
    agents = ["Agent1", "Agent2", "Agent3"]
    if call_count < len(agents):
        return RouterResult(agents[call_count])

    return RouterResult(None)
```

## Tips and Best Practices

1. **Always return RouterResult**: Never return strings directly, always wrap in `RouterResult()`

2. **Handle None gracefully**: Check if `last_result` exists before accessing it:
   ```python
   if last_result and last_result.get("agent"):
       # Safe to use last_result
   ```

3. **Set appropriate max_iter**: Prevent infinite loops by setting a reasonable `max_iter` value

4. **Use descriptive agent names**: Makes routing logic more readable

5. **Log routing decisions**: Print statements help debug complex routing logic:
   ```python
   print(f"[Router] Routing to {next_agent} based on {reason}")
   ```

6. **Test edge cases**: Test with empty state, no tools used, etc.

## Learn More

- See `examples/08-advanced/routing_agent.py` for LLM-based routing
- See `examples/05-tracing/metrics.py` for router usage with tracing
- Check `peargent/core/router.py` for implementation details
