# peargent/tools/__init__.py

from .math_tool import MathTool
from .text_extraction_tool import TextExtractionTool
from .wikipedia_tool import WikipediaKnowledgeTool
from .email_tool import EmailTool

calculator = MathTool()
text_extractor = TextExtractionTool()
wikipedia_tool = WikipediaKnowledgeTool()
email_tool = EmailTool()

BUILTIN_TOOLS = {
    "calculator": calculator,
    "extract_text": text_extractor,
    "search_wikipedia": wikipedia_tool,
    "send_notification": email_tool,
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")