# peargent/tools/__init__.py

from .math_tool import MathTool
from .text_extraction_tool import TextExtractionTool
<<<<<<< HEAD
from .wikipedia_tool import WikipediaKnowledgeTool

calculator = MathTool()
text_extractor = TextExtractionTool()
wikipedia_tool = WikipediaKnowledgeTool()
=======
from .http_tools import HttpTool

calculator = MathTool()
text_extractor = TextExtractionTool()
http_client = HttpTool()
>>>>>>> f1eb8ac (Add HTTP client tool  with retries,timeout,header support)

BUILTIN_TOOLS = {
    "calculator": calculator,
    "extract_text": text_extractor,
<<<<<<< HEAD
    "search_wikipedia": wikipedia_tool,
=======
    "http_client": http_client,
>>>>>>> f1eb8ac (Add HTTP client tool  with retries,timeout,header support)
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")
