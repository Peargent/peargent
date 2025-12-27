# peargent/tools/__init__.py

from .math_tool import MathTool
from .text_extraction_tool import TextExtractionTool

calculator = MathTool()
text_extractor = TextExtractionTool()

BUILTIN_TOOLS = {
    "calculator": calculator,
    "extract_text": text_extractor,
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")