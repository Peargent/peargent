# Tool Decorator Guide

## Overview

Peargent now supports two ways to create tools:

1. **`create_tool()`** - Traditional function-based approach
2. **`@create_tool()`** - New decorator with automatic parameter inference

## Why Use the Decorator?

The `@create_tool()` decorator makes tool creation **simpler and cleaner** by:

- **Auto-inferring** tool name from function name
- **Auto-extracting** description from docstring
- **Auto-detecting** parameters from type hints
- **Reducing boilerplate** by ~40-60%
- **Supporting** all `create_tool()` features (timeout, retries, error handling, etc.)

## Basic Usage

### Before (create_tool)

```python
def get_weather_func(city: str) -> str:
    return f"Weather in {city}: Sunny"

weather_tool = create_tool(
    name="get_weather",
    description="Get current weather for a city",
    input_parameters={"city": str},
    call_function=get_weather_func
)
```

**Lines of code: 8**

### After (@create_tool decorator)

```python
@create_tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    return f"Weather in {city}: Sunny"
```

**Lines of code: 4 (50% less!)**

## Feature Comparison

| Feature | create_tool() | @create_tool() |
|---------|---------------|---------|
| Manual name | Required | Optional (auto-inferred) |
| Manual description | Required | Optional (from docstring) |
| Manual parameters | Required | Optional (from type hints) |
| Timeout support | ✓ | ✓ |
| Retry logic | ✓ | ✓ |
| Error handling | ✓ | ✓ |
| Output validation | ✓ | ✓ |

## Examples

### 1. Basic Tool (Auto-Inference)

```python
@create_tool()
def search_docs(query: str) -> list:
    """Search documentation database"""
    return [f"Result for {query}"]

# Automatically creates:
# - name: "search_docs"
# - description: "Search documentation database"
# - input_parameters: {"query": str}
```

### 2. Optional Parameters (with defaults)

```python
@create_tool()
def send_email(to: str, subject: str, priority: int = 1) -> str:
    """Send an email"""
    return f"Email sent to {to} (Priority: {priority})"

# Only 'to' and 'subject' are required
# 'priority' is optional with default value 1
```

### 3. Custom Name and Description

```python
@create_tool(name="calc", description="Perform calculations")
def calculate(expression: str) -> float:
    """Internal calculation function"""
    return eval(expression)

# Uses custom name "calc" instead of "calculate"
# Uses custom description instead of docstring
```

### 4. Timeout and Retries

```python
@create_tool(timeout=5.0, max_retries=3, retry_delay=1.0)
def fetch_api(url: str) -> dict:
    """Fetch data from external API"""
    import requests
    return requests.get(url).json()

# Automatically retries up to 3 times
# Times out after 5 seconds
# Exponential backoff between retries
```

### 5. Error Handling

```python
@create_tool(on_error="return_error")
def risky_operation(data: str) -> str:
    """Operation that might fail"""
    # If this fails, returns error message instead of crashing
    return process_data(data)

# Options: "raise" (default), "return_error", "return_none"
```

### 6. Output Validation with Pydantic

```python
from pydantic import BaseModel

class WeatherOutput(BaseModel):
    temperature: float
    condition: str

@create_tool(output_schema=WeatherOutput)
def get_weather(city: str) -> dict:
    """Get weather with validated output"""
    return {
        "temperature": 72.0,
        "condition": "Sunny"
    }

# Output is automatically validated against WeatherOutput schema
```

## Using Tools with Agents

Both `create_tool()` and `@create_tool()` work identically with agents:

```python
from peargent import create_agent, tool
from peargent.models import groq

@create_tool()
def search(query: str) -> list:
    """Search documentation"""
    return ["result1", "result2"]

@create_tool()
def calculate(expr: str) -> float:
    """Perform calculation"""
    return eval(expr)

# Create agent with decorated tools
agent = create_agent(
    name="Assistant",
    description="Helpful assistant",
    persona="You are a helpful assistant",
    model=groq("llama-3.3-70b-versatile"),
    tools=[search, calculate]  # Pass decorated tools directly
)

response = agent.run("Search for python tutorials")
```

## Advanced: All Parameters

The decorator supports **all** parameters from `create_tool()`:

```python
@create_tool(
    name="custom_name",              # Custom tool name
    description="Custom description", # Custom description
    input_parameters={"x": int},     # Override auto-inference
    timeout=10.0,                    # Execution timeout
    max_retries=5,                   # Retry attempts
    retry_delay=2.0,                 # Initial retry delay
    retry_backoff=True,              # Exponential backoff
    on_error="return_error",         # Error handling
    output_schema=MyModel            # Output validation
)
def my_tool(x: int) -> dict:
    """Tool with all options"""
    return {"result": x * 2}
```

## Best Practices

1. **Always add type hints** - The decorator uses them for parameter inference
2. **Write clear docstrings** - Used as tool description for the LLM
3. **Use meaningful function names** - Becomes the tool name
4. **Handle optional parameters** - Use default values for optional params
5. **Validate outputs** - Use `output_schema` for type-safe responses

## Migration Guide

### From create_tool() to @create_tool()

**Step 1:** Identify the function being wrapped

```python
def my_func(param: str) -> str:
    return f"Result: {param}"

tool = create_tool(
    name="my_tool",
    description="Does something",
    input_parameters={"param": str},
    call_function=my_func
)
```

**Step 2:** Add docstring to function

```python
def my_func(param: str) -> str:
    """Does something"""
    return f"Result: {param}"
```

**Step 3:** Replace create_tool() with @create_tool()

```python
@create_tool()
def my_func(param: str) -> str:
    """Does something"""
    return f"Result: {param}"
```

**Done!** The tool works identically but with cleaner code.

## FAQ

**Q: Can I still use create_tool()?**
A: Yes! Both methods are fully supported and work identically.

**Q: What if my function has no type hints?**
A: The decorator defaults to `str` type for untyped parameters.

**Q: What about functions with *args or **kwargs?**
A: Not currently supported. Use `create_tool()` for those cases.

**Q: Can I override auto-inference?**
A: Yes! Pass explicit `name`, `description`, or `input_parameters` to override.

**Q: Does this work with async functions?**
A: The decorator syntax works, but async execution depends on your agent's model.

## Summary

| Scenario | Recommendation |
|----------|----------------|
| Simple functions with type hints | Use `@create_tool()` |
| Functions with clear docstrings | Use `@create_tool()` |
| Need timeout/retry/error handling | Use `@create_tool()` with parameters |
| Need full control over parameters | Use `create_tool()` |
| Complex signatures (*args/**kwargs) | Use `create_tool()` |

**Bottom line:** The `@create_tool()` decorator makes tool creation faster and cleaner while maintaining full compatibility with `create_tool()`.
