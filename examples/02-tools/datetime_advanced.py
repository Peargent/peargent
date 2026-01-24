"""
Advanced DateTime Tool Example

Demonstrates advanced usage of DateTimeTool with an AI agent for natural language
date/time queries, scheduling, and time-sensitive operations.
"""

from peargent import create_agent
from peargent.tools import datetime_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("DateTime Tool - Advanced Example with Agent")
    print("=" * 60)
    
    # Example 1: Multiple timezone support
    print("\n1. Working with multiple timezones:")
    print("-" * 60)
    
    timezones = ["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"]
    
    for tz in timezones:
        result = datetime_tool.run({
            "operation": "current",
            "tz": tz,
            "format_string": "%I:%M %p"
        })
        if result["success"]:
            print(f"{tz:25s}: {result['datetime']} ({result['components']['weekday']})")
    
    # Example 2: Complex time calculations
    print("\n\n2. Complex time calculations:")
    print("-" * 60)
    
    # Calculate time until a future event
    result = datetime_tool.run({
        "operation": "difference",
        "start_time": "2026-01-13",
        "end_time": "2026-12-31",
        "unit": "weeks"
    })
    
    if result["success"]:
        print(f"Weeks until end of year: {abs(result['difference']):.1f}")
        print(f"Days: {result['components']['days']}")
    
    # Calculate work hours
    result = datetime_tool.run({
        "operation": "difference",
        "start_time": "2026-01-13T09:00:00",
        "end_time": "2026-01-13T17:30:00",
        "unit": "hours"
    })
    
    if result["success"]:
        print(f"\nWork hours: {result['difference']} hours")
        print(f"Breakdown: {result['components']['hours']} hours, {result['components']['minutes']} minutes")
    
    # Example 3: Parse various date formats
    print("\n\n3. Parsing various date formats:")
    print("-" * 60)
    
    date_inputs = [
        "2026-01-13",
        "2026-01-13 15:30:00",
        "13-01-2026",
        "January 13, 2026",
        "Jan 13, 2026 15:30:00",
        "1736784600"  # Unix timestamp
    ]
    
    for date_input in date_inputs:
        result = datetime_tool.run({
            "operation": "parse",
            "datetime_string": date_input,
            "output_format": "%Y-%m-%d %H:%M:%S"
        })
        if result["success"]:
            print(f"{date_input:30s} -> {result['datetime']}")
        else:
            print(f"{date_input:30s} -> Error: {result['error']}")
    
    # Example 4: Using datetime tool with an AI agent
    print("\n\n4. Using DateTime tool with an AI agent:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="TimeKeeper",
            description="A helpful time and scheduling assistant",
            persona=(
                "You are a knowledgeable time and scheduling assistant. "
                "You help users with date calculations, timezone conversions, and scheduling queries. "
                "Always provide precise information and explain time differences clearly."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[datetime_tool]
        )
        
        # Test various natural language queries
        queries = [
            "What's the current time?",
            "What time is it in Tokyo right now?",
            "How many days until the end of the year?",
            "Convert January 13, 2026 3:30 PM UTC to New York time"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            print(f"Response: ", end="")
            response = agent.run(query)
            print(response)
            print("-" * 50)
        
        # Test the tool directly to verify it works correctly
        print("\n\nDirect tool test for verification:")
        print("-" * 60)
        result = datetime_tool.run({
            "operation": "difference",
            "start_time": "2026-01-13T00:00:00Z",
            "end_time": "2026-12-31T23:59:59Z"
        })
        if result["success"]:
            print(f"Days from Jan 13 to Dec 31, 2026: {result['components']['days']} days")
            print(f"Human readable: {result['human_readable']}")
    
    except Exception as e:
        print(f"\n❌ Agent Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect DateTime tool usage works without API key:")
        
        # Demonstrate direct usage as fallback
        print("\n\nDirect tool usage examples:")
        print("-" * 60)
        
        # Current time
        result = datetime_tool.run({})
        if result["success"]:
            print(f"Current UTC: {result['datetime']}")
        
        # Tokyo time
        result = datetime_tool.run({"tz": "Asia/Tokyo"})
        if result["success"]:
            print(f"Tokyo time: {result['datetime']}")
        
        # Time until year end
        result = datetime_tool.run({
            "operation": "difference",
            "start_time": "2026-01-13",
            "end_time": "2026-12-31"
        })
        if result["success"]:
            print(f"Days until end of year: {abs(result['difference']):.0f}")
    
    # Example 5: Scheduling scenario
    print("\n\n5. Meeting scheduling scenario:")
    print("-" * 60)
    
    meeting_time_utc = "2026-01-15T14:00:00Z"
    
    print(f"Meeting scheduled (UTC): {meeting_time_utc}")
    print("\nMeeting times in different locations:")
    
    locations = {
        "San Francisco": "America/Los_Angeles",
        "New York": "America/New_York",
        "London": "Europe/London",
        "Dubai": "Asia/Dubai",
        "Singapore": "Asia/Singapore"
    }
    
    for city, tz in locations.items():
        result = datetime_tool.run({
            "operation": "parse",
            "datetime_string": meeting_time_utc,
            "output_timezone": tz,
            "output_format": "%I:%M %p on %A, %B %d"
        })
        if result["success"]:
            print(f"{city:15s}: {result['datetime']}")
    
    # Calculate time until meeting
    result = datetime_tool.run({
        "operation": "difference",
        "start_time": meeting_time_utc
    })
    if result["success"]:
        if result["is_future"]:
            print(f"\n⏰ Meeting starts in: {result['human_readable']}")
        else:
            print(f"\n✓ Meeting was {result['human_readable']}")
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
