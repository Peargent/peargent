# peargent/tools/math_tool.py

from peargent._core.tool import Tool


def evaluate(expression: str) -> float:
    return eval(expression, {"__builtins__": {}}, {})

class MathTool(Tool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Evaluate mathematical expressions.",
            input_parameters={"expression": str},
            call_function=evaluate
        )
