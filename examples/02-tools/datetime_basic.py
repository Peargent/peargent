"""
Basic DateTime Tool Example

Demonstrates basic usage of the DateTimeTool for getting current time,
calculating time differences, and formatting dates.
"""

from peargent.tools import datetime_tool


def main():
    print("=" * 60)
    print("DateTime Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Get current UTC time (simplest usage - no parameters needed)
    print("\n1. Getting current UTC time (no parameters):")
    print("-" * 60)
    
    result = datetime_tool.run({})
    
    if result["success"]:
        print(f"Current UTC time: {result['datetime']}")
        print(f"Timezone: {result['timezone']}")
        print(f"Unix timestamp: {result['timestamp']}")
        print(f"Date components: {result['components']['year']}-{result['components']['month']:02d}-{result['components']['day']:02d}")
        print(f"It's {result['components']['weekday']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Get current time in a specific timezone
    print("\n\n2. Getting current time in New York:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "current",
        "tz": "America/New_York"
    })
    
    if result["success"]:
        print(f"New York time: {result['datetime']}")
        print(f"Timezone: {result['timezone']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 3: Get current time in custom format
    print("\n\n3. Getting current time with custom format:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "current",
        "format_string": "%B %d, %Y at %I:%M:%S %p"
    })
    
    if result["success"]:
        print(f"Formatted time: {result['datetime']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 4: Calculate time difference
    print("\n\n4. Calculating time difference:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "difference",
        "start_time": "2026-01-01",
        "end_time": "2026-01-13"
    })
    
    if result["success"]:
        print(f"Difference: {result['difference']} {result['unit']}")
        print(f"Human readable: {result['human_readable']}")
        print(f"Total seconds: {result['total_seconds']}")
        print(f"Components: {result['components']['days']} days, {result['components']['hours']} hours")
    else:
        print(f"Error: {result['error']}")
    
    # Example 5: Calculate time from now
    print("\n\n5. Calculating time since a past date:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "difference",
        "start_time": "2026-01-01T00:00:00Z"  # Include timezone to avoid naive/aware mismatch
        # end_time is omitted, so it defaults to current time
    })
    
    if result["success"]:
        print(f"Time since Jan 1, 2026: {result['human_readable']}")
        print(f"Difference: {result['difference']} {result['unit']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 6: Parse and format a date
    print("\n\n6. Parsing and formatting a date:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "parse",
        "datetime_string": "2026-01-13T15:30:00Z",
        "output_format": "%A, %B %d, %Y at %I:%M %p"
    })
    
    if result["success"]:
        print(f"Original: {result['original']}")
        print(f"Formatted: {result['datetime']}")
        print(f"Weekday: {result['components']['weekday']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 7: Convert timezone
    print("\n\n7. Converting timezone:")
    print("-" * 60)
    
    result = datetime_tool.run({
        "operation": "parse",
        "datetime_string": "2026-01-13T15:30:00Z",
        "output_timezone": "Asia/Tokyo"
    })
    
    if result["success"]:
        print(f"Original UTC: {result['original']}")
        print(f"Tokyo time: {result['datetime']}")
        print(f"Timezone: {result['timezone']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
