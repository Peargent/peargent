"""
DateTime Tool for Peargent
Retrieves current date/time, performs time calculations, and handles timezone operations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import re

from peargent import Tool

try:
    from zoneinfo import ZoneInfo
    HAS_ZONEINFO = True
    # On Windows, ensure tzdata is available
    try:
        import tzdata
    except ImportError:
        pass  # tzdata might not be installed
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
        HAS_ZONEINFO = True
        try:
            import tzdata
        except ImportError:
            pass
    except ImportError:
        ZoneInfo = None
        HAS_ZONEINFO = False


def get_current_datetime(
    tz: Optional[str] = None,
    format_string: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the current date and time.
    
    By default, returns the current UTC time. Can optionally return time in a specific timezone
    and format the output.
    
    Args:
        tz: Timezone name (e.g., "America/New_York", "Europe/London", "Asia/Tokyo").
            If None, returns UTC time. Use "local" for system local time.
        format_string: Python strftime format string (e.g., "%Y-%m-%d %H:%M:%S", "%B %d, %Y").
            If None, returns ISO format.
            
    Returns:
        Dictionary containing:
            - datetime: Formatted datetime string
            - timezone: Timezone name
            - timestamp: Unix timestamp (seconds since epoch)
            - iso_format: ISO 8601 formatted string
            - components: Dict with year, month, day, hour, minute, second, weekday
            - success: Boolean indicating success
            - error: Error message if any
            
    Example:
        >>> result = get_current_datetime()
        >>> print(result["datetime"])
        '2026-01-13T15:30:45.123456+00:00'
        
        >>> result = get_current_datetime(tz="America/New_York")
        >>> print(result["datetime"])
        '2026-01-13T10:30:45.123456-05:00'
        
        >>> result = get_current_datetime(format_string="%B %d, %Y at %I:%M %p")
        >>> print(result["datetime"])
        'January 13, 2026 at 03:30 PM'
    """
    try:
        # Get current datetime
        if tz is None:
            # Default to UTC
            current_dt = datetime.now(timezone.utc)
            tz_name = "UTC"
        elif tz.lower() == "local":
            # Use system local time
            current_dt = datetime.now().astimezone()
            tz_name = str(current_dt.tzinfo)
        else:
            # Use specified timezone
            if not HAS_ZONEINFO:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "success": False,
                    "error": (
                        "Timezone support requires zoneinfo (Python 3.9+) or backports.zoneinfo. "
                        "Install with: pip install backports.zoneinfo"
                    )
                }
            
            try:
                tz_obj = ZoneInfo(tz)
                current_dt = datetime.now(tz_obj)
                tz_name = tz
            except Exception as e:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "success": False,
                    "error": f"Invalid timezone '{tz}': {str(e)}"
                }
        
        # Format the datetime
        if format_string:
            try:
                formatted_dt = current_dt.strftime(format_string)
            except Exception as e:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "success": False,
                    "error": f"Invalid format string '{format_string}': {str(e)}"
                }
        else:
            formatted_dt = current_dt.isoformat()
        
        # Build result
        result = {
            "datetime": formatted_dt,
            "timezone": tz_name,
            "timestamp": current_dt.timestamp(),
            "iso_format": current_dt.isoformat(),
            "components": {
                "year": current_dt.year,
                "month": current_dt.month,
                "day": current_dt.day,
                "hour": current_dt.hour,
                "minute": current_dt.minute,
                "second": current_dt.second,
                "microsecond": current_dt.microsecond,
                "weekday": current_dt.strftime("%A"),
                "weekday_number": current_dt.weekday(),  # 0=Monday, 6=Sunday
            },
            "success": True,
            "error": None
        }
        
        return result
        
    except Exception as e:
        return {
            "datetime": "",
            "timezone": "",
            "timestamp": 0,
            "iso_format": "",
            "components": {},
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def calculate_time_difference(
    start_time: str,
    end_time: Optional[str] = None,
    unit: str = "auto"
) -> Dict[str, Any]:
    """
    Calculate the time difference between two dates/times.
    
    If only start_time is provided, calculates the difference from now.
    Supports various input formats including ISO 8601, common date formats, and Unix timestamps.
    
    Args:
        start_time: Start datetime (ISO format, "YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS", or Unix timestamp)
        end_time: End datetime (same formats as start_time). If None, uses current time.
        unit: Unit for the result ("seconds", "minutes", "hours", "days", "weeks", "auto").
            "auto" chooses the most appropriate unit.
            
    Returns:
        Dictionary containing:
            - difference: Numeric time difference in the specified unit
            - unit: Unit of the difference
            - total_seconds: Total difference in seconds
            - components: Dict with days, hours, minutes, seconds breakdown
            - human_readable: Human-friendly description (e.g., "2 days, 3 hours")
            - is_future: Boolean indicating if end_time is in the future relative to start_time
            - success: Boolean indicating success
            - error: Error message if any
            
    Example:
        >>> result = calculate_time_difference("2026-01-01", "2026-01-13")
        >>> print(result["difference"])
        12  # days
        
        >>> result = calculate_time_difference("2026-01-13T10:00:00")
        >>> print(result["human_readable"])
        '5 hours, 30 minutes ago'
    """
    try:
        # Parse start_time
        start_dt = _parse_datetime(start_time)
        if start_dt is None:
            return {
                "difference": 0,
                "unit": "",
                "total_seconds": 0,
                "components": {},
                "human_readable": "",
                "is_future": False,
                "success": False,
                "error": f"Unable to parse start_time: '{start_time}'"
            }
        
        # Parse end_time
        if end_time is None:
            end_dt = datetime.now(timezone.utc)
        else:
            end_dt = _parse_datetime(end_time)
            if end_dt is None:
                return {
                    "difference": 0,
                    "unit": "",
                    "total_seconds": 0,
                    "components": {},
                    "human_readable": "",
                    "is_future": False,
                    "success": False,
                    "error": f"Unable to parse end_time: '{end_time}'"
                }
        
        # Calculate difference
        time_delta = end_dt - start_dt
        total_seconds = time_delta.total_seconds()
        is_future = total_seconds > 0
        abs_seconds = abs(total_seconds)
        
        # Break down into components
        days = int(abs_seconds // 86400)
        remaining = abs_seconds % 86400
        hours = int(remaining // 3600)
        remaining = remaining % 3600
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        # Determine unit and value
        if unit == "auto":
            if abs_seconds < 60:
                final_unit = "seconds"
                final_value = abs_seconds
            elif abs_seconds < 3600:
                final_unit = "minutes"
                final_value = abs_seconds / 60
            elif abs_seconds < 86400:
                final_unit = "hours"
                final_value = abs_seconds / 3600
            elif abs_seconds < 604800:
                final_unit = "days"
                final_value = abs_seconds / 86400
            else:
                final_unit = "weeks"
                final_value = abs_seconds / 604800
        else:
            unit_map = {
                "seconds": 1,
                "minutes": 60,
                "hours": 3600,
                "days": 86400,
                "weeks": 604800
            }
            if unit not in unit_map:
                return {
                    "difference": 0,
                    "unit": "",
                    "total_seconds": 0,
                    "components": {},
                    "human_readable": "",
                    "is_future": False,
                    "success": False,
                    "error": f"Invalid unit: '{unit}'. Must be one of: {list(unit_map.keys())} or 'auto'"
                }
            final_unit = unit
            final_value = abs_seconds / unit_map[unit]
        
        # Build human-readable string
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 and days == 0:  # Don't show minutes if showing days
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 and days == 0 and hours == 0:  # Only show seconds for small durations
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        if not parts:
            human_readable = "0 seconds"
        else:
            human_readable = ", ".join(parts)
        
        # Add "ago" only if end is before start (is_future is False)
        # When start is past and end is now, is_future is True, so don't add "ago"
        # The naming is from perspective of start->end, so we only add ago for backwards time
        if not is_future:
            human_readable += " ago"
        
        result = {
            "difference": round(-final_value, 2) if not is_future else round(final_value, 2),
            "unit": final_unit,
            "total_seconds": total_seconds,
            "components": {
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds
            },
            "human_readable": human_readable,
            "is_future": is_future,
            "success": True,
            "error": None
        }
        
        return result
        
    except Exception as e:
        return {
            "difference": 0,
            "unit": "",
            "total_seconds": 0,
            "components": {},
            "human_readable": "",
            "is_future": False,
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def parse_and_format_datetime(
    datetime_string: str,
    output_format: Optional[str] = None,
    output_timezone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse a datetime string and optionally reformat or convert timezone.
    
    Supports various input formats and can convert between timezones.
    
    Args:
        datetime_string: Input datetime string (ISO format, "YYYY-MM-DD", Unix timestamp, etc.)
        output_format: Python strftime format for output (e.g., "%Y-%m-%d %H:%M:%S")
            If None, returns ISO format.
        output_timezone: Timezone to convert to (e.g., "America/New_York").
            If None, preserves original timezone.
            
    Returns:
        Dictionary containing:
            - datetime: Formatted datetime string
            - timezone: Output timezone name
            - timestamp: Unix timestamp
            - iso_format: ISO 8601 formatted string
            - components: Dict with date/time components
            - original: Original input string
            - success: Boolean indicating success
            - error: Error message if any
            
    Example:
        >>> result = parse_and_format_datetime("2026-01-13T15:30:00Z", output_format="%B %d, %Y")
        >>> print(result["datetime"])
        'January 13, 2026'
        
        >>> result = parse_and_format_datetime("2026-01-13T15:30:00Z", output_timezone="America/New_York")
        >>> print(result["datetime"])
        '2026-01-13T10:30:00-05:00'
    """
    try:
        # Parse input datetime
        parsed_dt = _parse_datetime(datetime_string)
        if parsed_dt is None:
            return {
                "datetime": "",
                "timezone": "",
                "timestamp": 0,
                "iso_format": "",
                "components": {},
                "original": datetime_string,
                "success": False,
                "error": f"Unable to parse datetime: '{datetime_string}'"
            }
        
        # Convert timezone if specified
        if output_timezone:
            if not HAS_ZONEINFO:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "original": datetime_string,
                    "success": False,
                    "error": (
                        "Timezone conversion requires zoneinfo (Python 3.9+) or backports.zoneinfo. "
                        "Install with: pip install backports.zoneinfo"
                    )
                }
            
            try:
                tz_obj = ZoneInfo(output_timezone)
                parsed_dt = parsed_dt.astimezone(tz_obj)
                tz_name = output_timezone
            except Exception as e:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "original": datetime_string,
                    "success": False,
                    "error": f"Invalid timezone '{output_timezone}': {str(e)}"
                }
        else:
            tz_name = str(parsed_dt.tzinfo) if parsed_dt.tzinfo else "naive"
        
        # Format output
        if output_format:
            try:
                formatted = parsed_dt.strftime(output_format)
            except Exception as e:
                return {
                    "datetime": "",
                    "timezone": "",
                    "timestamp": 0,
                    "iso_format": "",
                    "components": {},
                    "original": datetime_string,
                    "success": False,
                    "error": f"Invalid format string '{output_format}': {str(e)}"
                }
        else:
            formatted = parsed_dt.isoformat()
        
        result = {
            "datetime": formatted,
            "timezone": tz_name,
            "timestamp": parsed_dt.timestamp(),
            "iso_format": parsed_dt.isoformat(),
            "components": {
                "year": parsed_dt.year,
                "month": parsed_dt.month,
                "day": parsed_dt.day,
                "hour": parsed_dt.hour,
                "minute": parsed_dt.minute,
                "second": parsed_dt.second,
                "microsecond": parsed_dt.microsecond,
                "weekday": parsed_dt.strftime("%A"),
                "weekday_number": parsed_dt.weekday(),
            },
            "original": datetime_string,
            "success": True,
            "error": None
        }
        
        return result
        
    except Exception as e:
        return {
            "datetime": "",
            "timezone": "",
            "timestamp": 0,
            "iso_format": "",
            "components": {},
            "original": datetime_string,
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def _parse_datetime(datetime_string: str) -> Optional[datetime]:
    """
    Parse a datetime string in various formats.
    
    Supports:
    - ISO 8601 format with timezone
    - ISO 8601 format without timezone (assumes UTC)
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM:SS
    - Unix timestamp (integer or float)
    
    Returns:
        Parsed datetime object with timezone, or None if parsing fails
    """
    # Try Unix timestamp (integer or float)
    try:
        timestamp = float(datetime_string)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (ValueError, OverflowError):
        pass
    
    # Try ISO 8601 format
    try:
        return datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
    except ValueError:
        pass
    
    # Try common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%B %d, %Y %H:%M:%S",
        "%B %d, %Y",
        "%b %d, %Y %H:%M:%S",
        "%b %d, %Y",
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(datetime_string, fmt)
            # Add UTC timezone if naive
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    
    return None


class DateTimeTool(Tool):
    """
    Tool for datetime operations including current time, time calculations, and timezone conversions.
    
    Handles:
    - Getting current date and time (UTC or any timezone)
    - Calculating time differences between dates
    - Parsing and formatting datetime strings
    - Converting between timezones
    
    By default, calling this tool without parameters returns the current UTC time.
    
    Example:
        >>> from peargent.tools import datetime_tool
        >>> # Get current time
        >>> result = datetime_tool.run({})
        >>> print(result["datetime"])
        
        >>> # Get time in specific timezone
        >>> result = datetime_tool.run({"operation": "current", "tz": "America/New_York"})
        >>> print(result["datetime"])
        
        >>> # Calculate time difference
        >>> result = datetime_tool.run({
        ...     "operation": "difference",
        ...     "start_time": "2026-01-01",
        ...     "end_time": "2026-01-13"
        ... })
        >>> print(result["human_readable"])
    """
    
    def __init__(self):
        super().__init__(
            name="datetime_operations",
            description=(
                "DateTime tool for getting current time, calculating time differences, and timezone conversions. "
                "**CURRENT DATE: 2026-01-13** "
                "\n\n**OPERATIONS:**\n"
                "1. GET CURRENT TIME (operation='current' or omit operation):\n"
                "   - Get UTC time: {} or {'operation': 'current'}\n"
                "   - Get timezone time: {'operation': 'current', 'tz': 'America/New_York'} (use IANA timezones like 'America/New_York', 'Europe/London', 'Asia/Tokyo')\n"
                "   - Custom format: {'operation': 'current', 'format_string': '%Y-%m-%d %H:%M:%S'}\n"
                "\n2. CALCULATE TIME DIFFERENCE (operation='difference'):\n"
                "   - Required: 'start_time' (ISO format like '2026-01-13T15:30:00Z')\n"
                "   - Optional: 'end_time' (defaults to now), 'unit' ('seconds', 'minutes', 'hours', 'days', 'weeks', 'auto')\n"
                "   - Example: {'operation': 'difference', 'start_time': '2026-01-01T00:00:00Z', 'end_time': '2026-12-31T23:59:59Z'}\n"
                "   - For 'days until X': Use current date as start_time and target date as end_time\n"
                "\n3. PARSE/CONVERT DATES (operation='parse'):\n"
                "   - Required: 'datetime_string' (ISO format, YYYY-MM-DD, or Unix timestamp)\n"
                "   - Optional: 'output_format' (strftime format), 'output_timezone' (IANA timezone)\n"
                "   - Example: {'operation': 'parse', 'datetime_string': '2026-01-13T15:30:00Z', 'output_timezone': 'America/New_York'}\n"
                "\n**IMPORTANT:** Always use ISO 8601 format with timezone for datetime strings (e.g., '2026-01-13T15:30:00Z'). "
                "Use full IANA timezone names (e.g., 'America/New_York', 'Asia/Tokyo', 'Europe/London'). "
                "For 'days/time until' queries: call difference with start_time=current_date and end_time=target_date."
            ),
            input_parameters={},
            call_function=self._execute_operation
        )
    
    def _execute_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Execute datetime operation with all parameters passed as kwargs.
        This allows the tool to accept any parameters without validation issues.
        """
        operation = kwargs.pop("operation", "current")  # Use pop to remove it from kwargs
        return self._route_operation(operation=operation, **kwargs)
    
    def _route_operation(self, operation: str = "current", **kwargs) -> Dict[str, Any]:
        """
        Route to the appropriate operation based on the operation parameter.
        """
        if operation == "current":
            return get_current_datetime(
                tz=kwargs.get("tz"),
                format_string=kwargs.get("format_string")
            )
        elif operation == "difference":
            return calculate_time_difference(
                start_time=kwargs.get("start_time", ""),
                end_time=kwargs.get("end_time"),
                unit=kwargs.get("unit", "auto")
            )
        elif operation == "parse":
            return parse_and_format_datetime(
                datetime_string=kwargs.get("datetime_string", ""),
                output_format=kwargs.get("output_format"),
                output_timezone=kwargs.get("output_timezone")
            )
        else:
            return {
                "success": False,
                "error": f"Invalid operation: '{operation}'. Must be one of: 'current', 'difference', 'parse'"
            }


# Create default instance for easy import
datetime_tool = DateTimeTool()
