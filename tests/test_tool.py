"""
Tests for the Tool class and create_tool functionality.
Tests basic tool creation, execution, and parameter validation.
"""

import pytest

from peargent import create_tool


class TestToolCreation:
    """Test basic tool creation and initialization."""

    def test_create_simple_tool(self) -> None:
        """Test creating a basic tool with minimal parameters."""

        def add(a: int, b: int) -> int:
            return a + b

        tool = create_tool(
            name="add",
            description="Add two numbers",
            input_parameters={"a": int, "b": int},
            call_function=add,
        )

        assert tool.name == "add"
        assert tool.description == "Add two numbers"
        assert callable(tool.call_function)

    def test_create_tool_with_string_parameter(self) -> None:
        """Test creating a tool with string input parameter."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        tool = create_tool(
            name="greet",
            description="Greet a person",
            input_parameters={"name": str},
            call_function=greet,
        )

        assert tool.name == "greet"
        assert "name" in tool.input_parameters
        assert tool.input_parameters["name"] == str

    def test_create_tool_without_parameters(self) -> None:
        """Test creating a tool with no input parameters."""

        def get_constant() -> int:
            return 42

        tool = create_tool(
            name="get_constant",
            description="Get a constant value",
            input_parameters={},
            call_function=get_constant,
        )

        assert tool.name == "get_constant"
        assert len(tool.input_parameters) == 0

    def test_input_parameter_types(self) -> None:
        """Test that input parameter types are correctly stored."""

        def multi_type_func(name: str, age: int, active: bool) -> str:
            return f"{name} is {age} years old"

        tool = create_tool(
            name="multi_type",
            description="Function with multiple parameter types",
            input_parameters={"name": str, "age": int, "active": bool},
            call_function=multi_type_func,
        )

        assert tool.input_parameters["name"] == str
        assert tool.input_parameters["age"] == int
        assert tool.input_parameters["active"] == bool


class TestToolExecution:
    """Test tool execution and function calling."""

    def test_execute_simple_tool(self) -> None:
        """Test executing a simple tool with parameters."""

        def multiply(x: int, y: int) -> int:
            return x * y

        tool = create_tool(
            name="multiply",
            description="Multiply two numbers",
            input_parameters={"x": int, "y": int},
            call_function=multiply,
        )

        result = tool.call_function(x=5, y=3)
        assert result == 15

    def test_execute_tool_without_parameters(self) -> None:
        """Test executing a tool with no parameters."""

        def get_constant() -> int:
            return 42

        tool = create_tool(
            name="get_constant",
            description="Get a constant value",
            input_parameters={},
            call_function=get_constant,
        )

        result = tool.call_function()
        assert result == 42

    def test_tool_with_multiple_parameter_types(self) -> None:
        """Test tool with multiple different parameter types."""

        def format_message(text: str, repeat: int, uppercase: bool) -> str:
            result = text * repeat
            return result.upper() if uppercase else result

        tool = create_tool(
            name="format_message",
            description="Format a message with options",
            input_parameters={"text": str, "repeat": int, "uppercase": bool},
            call_function=format_message,
        )

        result1 = tool.call_function(text="hi", repeat=2, uppercase=False)
        assert result1 == "hihi"

        result2 = tool.call_function(text="hi", repeat=2, uppercase=True)
        assert result2 == "HIHI"


class TestToolErrorHandling:
    """Test tool error handling."""

    def test_tool_execution_with_exception(self) -> None:
        """Test that tool exceptions are raised properly."""

        def error_function() -> str:
            raise ValueError("Something went wrong")

        tool = create_tool(
            name="error_function",
            description="A function that errors",
            input_parameters={},
            call_function=error_function,
        )

        with pytest.raises(ValueError, match="Something went wrong"):
            tool.call_function()
