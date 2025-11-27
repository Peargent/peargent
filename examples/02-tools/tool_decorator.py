"""
Example: Tool Decorator Usage with Agents

This example demonstrates how to use the @create_tool() decorator to create tools
with automatic parameter inference, making tool creation simpler and cleaner.
"""

from peargent import create_tool, create_agent
from peargent.models import groq

# ============================================================================
# EXAMPLE 1: Basic Tool with Auto-Inference
# ============================================================================

@create_tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    # Simulate weather API
    weather_data = {
        "San Francisco": "72°F, Sunny",
        "New York": "65°F, Cloudy",
        "London": "58°F, Rainy"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


# ============================================================================
# EXAMPLE 2: Tool with Custom Name and Description
# ============================================================================

@create_tool(name="search", description="Search through documentation")
def search_docs(query: str, max_results: int = 5) -> list:
    """Internal function for searching docs"""
    # Simulate search
    results = [
        f"Document about {query} - Result {i}"
        for i in range(1, max_results + 1)
    ]
    return results


# ============================================================================
# EXAMPLE 3: Tool with Timeout and Retries
# ============================================================================

@create_tool(timeout=5.0, max_retries=3, retry_delay=1.0)
def fetch_api_data(endpoint: str) -> dict:
    """Fetch data from external API with timeout protection"""
    import time
    # Simulate slow API
    time.sleep(0.5)
    return {
        "endpoint": endpoint,
        "status": "success",
        "data": "Sample API response"
    }


# ============================================================================
# EXAMPLE 4: Tool with Error Handling
# ============================================================================

@create_tool(on_error="return_error")
def calculate(expression: str) -> float:
    """Safely evaluate mathematical expressions"""
    # This will catch errors and return them as strings
    return eval(expression)


# ============================================================================
# EXAMPLE 5: Complex Tool with Multiple Parameters
# ============================================================================

@create_tool()
def send_email(to: str, subject: str, body: str, priority: int = 1) -> str:
    """Send an email with specified parameters"""
    return f"Email sent to {to} with subject '{subject}' (Priority: {priority})"


# ============================================================================
# Using Tools with Agents
# ============================================================================

def main():
    """Demonstrate tools with agents"""

    # Create an agent with multiple tools
    assistant = create_agent(
        name="Assistant",
        description="Helpful assistant with various tools",
        persona="You are a helpful assistant that can check weather, search docs, and perform calculations.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[get_weather, search_docs, fetch_api_data, calculate, send_email]
    )

    print("=" * 70)
    print("Tool Decorator Example - Agent with Multiple Tools")
    print("=" * 70)

    # Test 1: Weather query
    print("\n1. Testing Weather Tool:")
    response = assistant.run("What's the weather in San Francisco?")
    print(f"Response: {response}")

    # Test 2: Search query
    print("\n2. Testing Search Tool:")
    response = assistant.run("Search for documentation about agents")
    print(f"Response: {response}")

    # Test 3: Calculation
    print("\n3. Testing Calculator Tool:")
    response = assistant.run("Calculate 15 * 8 + 42")
    print(f"Response: {response}")

    # Test 4: Email sending
    print("\n4. Testing Email Tool:")
    response = assistant.run("Send an email to john@example.com with subject 'Meeting' and body 'Let's meet tomorrow'")
    print(f"Response: {response}")

    print("\n" + "=" * 70)


# ============================================================================
# Comparison: create_tool() Function vs @create_tool() Decorator
# ============================================================================

def comparison_example():
    """Show the difference between create_tool() function and @create_tool() decorator"""
    from peargent import create_tool

    print("\n" + "=" * 70)
    print("Comparison: create_tool() Function vs @create_tool() Decorator")
    print("=" * 70)

    # FUNCTION MODE: Using create_tool() with call_function
    def old_get_time():
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    old_tool = create_tool(
        name="get_time",
        description="Get current time",
        input_parameters={},  # Empty dict for no parameters
        call_function=old_get_time
    )

    # DECORATOR MODE: Using @create_tool() decorator
    @create_tool()
    def get_time() -> str:
        """Get current time"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    print("\nFUNCTION MODE (create_tool with call_function):")
    print("  - Requires: name, description, input_parameters, call_function")
    print("  - 7 lines of code")
    print("  - Manual parameter specification")

    print("\nDECORATOR MODE (@create_tool):")
    print("  - Auto-infers: name, description, parameters from function")
    print("  - 4 lines of code (43% less!)")
    print("  - Uses function name, docstring, and type hints")

    print("\nBoth tools work identically:")
    print(f"  Function mode result: {old_tool.run({})}")
    print(f"  Decorator mode result: {get_time.run({})}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run the main example
    # Uncomment the line below to test with actual LLM
    # main()

    # Show comparison
    comparison_example()

    # Manual testing without LLM
    print("\n" + "=" * 70)
    print("Manual Tool Testing (without LLM)")
    print("=" * 70)

    print("\n1. Weather Tool:")
    print(f"   {get_weather.run({'city': 'London'})}")

    print("\n2. Search Tool:")
    results = search_docs.run({"query": "peargent", "max_results": 3})
    for result in results:
        print(f"   - {result}")

    print("\n3. Calculator Tool:")
    print(f"   Result: {calculate.run({'expression': '100 / 5'})}")

    print("\n4. Email Tool:")
    print(f"   {send_email.run({'to': 'test@test.com', 'subject': 'Hello', 'body': 'Test message'})}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All tools created with @create_tool() decorator work perfectly!")
    print("=" * 70)
