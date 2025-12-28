# peargent/tools/__init__.py

from .math_tool import MathTool
from .text_extraction_tool import TextExtractionTool
from .http_tools import HttpTool

calculator = MathTool()
text_extractor = TextExtractionTool()
http_client = HttpTool()

BUILTIN_TOOLS = {
    "calculator": calculator,
    "extract_text": text_extractor,
    "http_client": http_client,
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")
