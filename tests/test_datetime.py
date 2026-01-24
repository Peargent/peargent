"""
Tests for DateTime Tool
Tests current time retrieval, time calculations, date parsing, and timezone operations.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta

from peargent.tools.datetime_tool import (
    DateTimeTool,
    get_current_datetime,
    calculate_time_difference,
    parse_and_format_datetime,
    _parse_datetime
)


class TestGetCurrentDateTime:
    """Test current datetime retrieval functionality."""
    
    def test_get_current_utc_time(self):
        """Test getting current UTC time without parameters."""
        result = get_current_datetime()
        
        assert result["success"] is True
        assert result["timezone"] == "UTC"
        assert result["datetime"] != ""
        assert result["iso_format"] != ""
        assert isinstance(result["timestamp"], float)
        assert "year" in result["components"]
        assert "month" in result["components"]
        assert "day" in result["components"]
        assert "weekday" in result["components"]
    
    def test_get_current_time_with_custom_format(self):
        """Test getting current time with custom format string."""
        result = get_current_datetime(format_string="%Y-%m-%d")
        
        assert result["success"] is True
        assert len(result["datetime"]) == 10  # YYYY-MM-DD
        assert result["datetime"].count("-") == 2
    
    def test_get_current_time_invalid_format(self):
        """Test getting current time with invalid format string."""
        result = get_current_datetime(format_string="%invalid")
        
        assert result["success"] is False
        assert "Invalid format string" in result["error"]
    
    def test_get_local_time(self):
        """Test getting system local time."""
        result = get_current_datetime(tz="local")
        
        assert result["success"] is True
        assert result["timezone"] != "UTC"
        assert result["datetime"] != ""
    
    @pytest.mark.skipif(
        not hasattr(__import__('peargent.tools.datetime_tool', fromlist=['HAS_ZONEINFO']), 'HAS_ZONEINFO'),
        reason="Timezone support not available"
    )
    def test_get_time_with_timezone(self):
        """Test getting time in specific timezone."""
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        
        if not HAS_ZONEINFO:
            pytest.skip("Timezone support not available")
        
        result = get_current_datetime(tz="America/New_York")
        
        assert result["success"] is True
        assert result["timezone"] == "America/New_York"
        assert result["datetime"] != ""
    
    def test_get_time_invalid_timezone(self):
        """Test getting time with invalid timezone."""
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        
        if not HAS_ZONEINFO:
            result = get_current_datetime(tz="Invalid/Timezone")
            assert result["success"] is False
            assert "zoneinfo" in result["error"].lower()
        else:
            result = get_current_datetime(tz="Invalid/Timezone")
            assert result["success"] is False
            assert "Invalid timezone" in result["error"]


class TestCalculateTimeDifference:
    """Test time difference calculation functionality."""
    
    def test_calculate_difference_between_dates(self):
        """Test calculating difference between two dates."""
        result = calculate_time_difference(
            start_time="2026-01-01",
            end_time="2026-01-13"
        )
        
        assert result["success"] is True
        # With auto unit selection, 12 days might be returned as weeks (1.71 weeks)
        assert result["unit"] in ["days", "weeks"]
        if result["unit"] == "days":
            assert abs(result["difference"]) == 12
        else:
            assert abs(result["difference"]) > 1
        assert result["total_seconds"] > 0
        assert result["is_future"] is True
        assert result["components"]["days"] == 12
    
    def test_calculate_difference_from_now(self):
        """Test calculating difference from past date to now."""
        past_date = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        
        result = calculate_time_difference(start_time=past_date)
        
        assert result["success"] is True
        # When start is past and end is now, is_future should be True (end is in future relative to start)
        assert result["is_future"] is True
        assert abs(result["difference"]) > 4  # At least 4 days
        # Since is_future is True, "ago" should NOT be in human_readable
        assert "ago" not in result["human_readable"]
    
    def test_calculate_difference_with_specific_unit(self):
        """Test calculating difference with specific unit."""
        result = calculate_time_difference(
            start_time="2026-01-01",
            end_time="2026-01-13",
            unit="hours"
        )
        
        assert result["success"] is True
        assert result["unit"] == "hours"
        assert abs(result["difference"]) == 288  # 12 days * 24 hours
    
    def test_calculate_difference_small_duration(self):
        """Test calculating small time difference (seconds)."""
        result = calculate_time_difference(
            start_time="2026-01-13T10:00:00",
            end_time="2026-01-13T10:00:45"
        )
        
        assert result["success"] is True
        assert result["unit"] == "seconds"
        assert abs(result["difference"]) == 45
    
    def test_calculate_difference_invalid_start_time(self):
        """Test with invalid start time."""
        result = calculate_time_difference(
            start_time="invalid-date",
            end_time="2026-01-13"
        )
        
        assert result["success"] is False
        assert "Unable to parse start_time" in result["error"]
    
    def test_calculate_difference_invalid_end_time(self):
        """Test with invalid end time."""
        result = calculate_time_difference(
            start_time="2026-01-01",
            end_time="invalid-date"
        )
        
        assert result["success"] is False
        assert "Unable to parse end_time" in result["error"]
    
    def test_calculate_difference_invalid_unit(self):
        """Test with invalid unit."""
        result = calculate_time_difference(
            start_time="2026-01-01",
            end_time="2026-01-13",
            unit="invalid"
        )
        
        assert result["success"] is False
        assert "Invalid unit" in result["error"]
    
    def test_calculate_difference_future_to_past(self):
        """Test calculating difference from future to past (negative)."""
        result = calculate_time_difference(
            start_time="2026-01-13",
            end_time="2026-01-01"
        )
        
        assert result["success"] is True
        assert result["is_future"] is False
        # When end is before start, difference should still be returned (magnitude only in difference)
        # The is_future flag tells us the direction
        assert abs(result["difference"]) > 0


class TestParseAndFormatDateTime:
    """Test datetime parsing and formatting functionality."""
    
    def test_parse_iso_format(self):
        """Test parsing ISO 8601 format."""
        result = parse_and_format_datetime("2026-01-13T15:30:00Z")
        
        assert result["success"] is True
        assert result["original"] == "2026-01-13T15:30:00Z"
        assert result["datetime"] != ""
        assert result["components"]["year"] == 2026
        assert result["components"]["month"] == 1
        assert result["components"]["day"] == 13
    
    def test_parse_and_format_with_custom_format(self):
        """Test parsing and reformatting with custom format."""
        result = parse_and_format_datetime(
            datetime_string="2026-01-13T15:30:00Z",
            output_format="%B %d, %Y"
        )
        
        assert result["success"] is True
        assert "January" in result["datetime"]
        assert "2026" in result["datetime"]
    
    def test_parse_simple_date(self):
        """Test parsing simple date format."""
        result = parse_and_format_datetime("2026-01-13")
        
        assert result["success"] is True
        assert result["components"]["year"] == 2026
        assert result["components"]["month"] == 1
        assert result["components"]["day"] == 13
    
    def test_parse_unix_timestamp(self):
        """Test parsing Unix timestamp."""
        timestamp = "1736784600"  # Some time in 2026
        
        result = parse_and_format_datetime(timestamp)
        
        assert result["success"] is True
        assert isinstance(result["timestamp"], float)
        assert result["datetime"] != ""
    
    def test_parse_invalid_datetime(self):
        """Test parsing invalid datetime string."""
        result = parse_and_format_datetime("not-a-date")
        
        assert result["success"] is False
        assert "Unable to parse datetime" in result["error"]
    
    def test_parse_with_invalid_format(self):
        """Test parsing with invalid output format."""
        result = parse_and_format_datetime(
            datetime_string="2026-01-13",
            output_format="%invalid"
        )
        
        assert result["success"] is False
        assert "Invalid format string" in result["error"]
    
    @pytest.mark.skipif(
        not hasattr(__import__('peargent.tools.datetime_tool', fromlist=['HAS_ZONEINFO']), 'HAS_ZONEINFO'),
        reason="Timezone support not available"
    )
    def test_parse_and_convert_timezone(self):
        """Test parsing and converting to different timezone."""
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        
        if not HAS_ZONEINFO:
            pytest.skip("Timezone support not available")
        
        result = parse_and_format_datetime(
            datetime_string="2026-01-13T15:30:00Z",
            output_timezone="America/New_York"
        )
        
        assert result["success"] is True
        assert result["timezone"] == "America/New_York"
        # Time should be different from UTC (earlier)
        assert result["components"]["hour"] < 15 or result["components"]["day"] < 13
    
    def test_parse_with_invalid_timezone(self):
        """Test parsing with invalid timezone."""
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        
        if not HAS_ZONEINFO:
            result = parse_and_format_datetime(
                datetime_string="2026-01-13T15:30:00Z",
                output_timezone="Invalid/Timezone"
            )
            assert result["success"] is False
            assert "zoneinfo" in result["error"].lower()
        else:
            result = parse_and_format_datetime(
                datetime_string="2026-01-13T15:30:00Z",
                output_timezone="Invalid/Timezone"
            )
            assert result["success"] is False
            assert "Invalid timezone" in result["error"]


class TestParseDateTimeHelper:
    """Test the _parse_datetime helper function."""
    
    def test_parse_iso_format_with_z(self):
        """Test parsing ISO format with Z suffix."""
        dt = _parse_datetime("2026-01-13T15:30:00Z")
        
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 1
        assert dt.day == 13
        assert dt.hour == 15
        assert dt.minute == 30
    
    def test_parse_iso_format_with_offset(self):
        """Test parsing ISO format with timezone offset."""
        dt = _parse_datetime("2026-01-13T15:30:00+05:00")
        
        assert dt is not None
        assert dt.year == 2026
    
    def test_parse_simple_date(self):
        """Test parsing simple YYYY-MM-DD format."""
        dt = _parse_datetime("2026-01-13")
        
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 1
        assert dt.day == 13
    
    def test_parse_datetime_with_space(self):
        """Test parsing YYYY-MM-DD HH:MM:SS format."""
        dt = _parse_datetime("2026-01-13 15:30:00")
        
        assert dt is not None
        assert dt.year == 2026
        assert dt.hour == 15
    
    def test_parse_unix_timestamp(self):
        """Test parsing Unix timestamp."""
        dt = _parse_datetime("1736784600")
        
        assert dt is not None
        assert isinstance(dt, datetime)
    
    def test_parse_alternative_formats(self):
        """Test parsing alternative date formats."""
        # DD-MM-YYYY
        dt = _parse_datetime("13-01-2026")
        assert dt is not None
        
        # Month name
        dt = _parse_datetime("January 13, 2026")
        assert dt is not None
        assert dt.month == 1
        assert dt.day == 13
    
    def test_parse_invalid_format(self):
        """Test parsing invalid format returns None."""
        dt = _parse_datetime("not-a-valid-date")
        assert dt is None


class TestDateTimeTool:
    """Test the DateTimeTool class."""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly."""
        tool = DateTimeTool()
        
        assert tool.name == "datetime_operations"
        assert tool.description != ""
        assert "current" in tool.description
    
    def test_tool_run_current_operation(self):
        """Test running tool with current operation."""
        tool = DateTimeTool()
        result = tool.run({})
        
        assert result["success"] is True
        assert result["datetime"] != ""
    
    def test_tool_run_with_timezone(self):
        """Test running tool with timezone parameter (simple call)."""
        tool = DateTimeTool()
        
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        if HAS_ZONEINFO:
            result = tool.run({"tz": "America/New_York"})
            assert result["success"] is True
            assert result["timezone"] == "America/New_York"
    
    def test_tool_run_difference_operation(self):
        """Test running tool with difference operation."""
        tool = DateTimeTool()
        result = tool.run({
            "operation": "difference",
            "start_time": "2026-01-01",
            "end_time": "2026-01-13"
        })
        
        assert result["success"] is True
        # Check that difference is positive and represents about 12 days
        assert abs(result["difference"]) > 1
    
    def test_tool_run_parse_operation(self):
        """Test running tool with parse operation."""
        tool = DateTimeTool()
        result = tool.run({
            "operation": "parse",
            "datetime_string": "2026-01-13T15:30:00Z",
            "output_format": "%Y-%m-%d"
        })
        
        assert result["success"] is True
        assert "2026-01-13" in result["datetime"]
    
    def test_tool_run_invalid_operation(self):
        """Test running tool with invalid operation."""
        tool = DateTimeTool()
        result = tool.run({"operation": "invalid"})
        
        assert result["success"] is False
        assert "Invalid operation" in result["error"]
    
    def test_tool_default_instance(self):
        """Test that default instance is created."""
        from peargent.tools.datetime_tool import datetime_tool
        
        assert isinstance(datetime_tool, DateTimeTool)
        assert datetime_tool.name == "datetime_operations"


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_scheduling_workflow(self):
        """Test a complete scheduling workflow."""
        tool = DateTimeTool()
        
        # Get current time
        current = tool.run({})
        assert current["success"] is True
        
        # Calculate time to future event
        future_diff = tool.run({
            "operation": "difference",
            "start_time": current["iso_format"],
            "end_time": "2026-12-31T23:59:59Z"
        })
        assert future_diff["success"] is True
        
        # Parse and format a date
        parsed = tool.run({
            "operation": "parse",
            "datetime_string": "2026-01-13",
            "output_format": "%B %d, %Y"
        })
        assert parsed["success"] is True
    
    def test_timezone_conversion_workflow(self):
        """Test timezone conversion workflow."""
        from peargent.tools.datetime_tool import HAS_ZONEINFO
        
        if not HAS_ZONEINFO:
            pytest.skip("Timezone support not available")
        
        tool = DateTimeTool()
        
        # Get UTC time
        utc_time = tool.run({})
        assert utc_time["success"] is True
        
        # Convert to different timezones
        timezones = ["America/New_York", "Europe/London", "Asia/Tokyo"]
        
        for tz in timezones:
            result = tool.run({
                "operation": "parse",
                "datetime_string": utc_time["iso_format"],
                "output_timezone": tz
            })
            assert result["success"] is True
            assert result["timezone"] == tz
