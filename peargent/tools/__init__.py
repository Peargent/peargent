# peargent/tools/__init__.py

from .math_tool import MathTool
from .text_extraction_tool import TextExtractionTool
from .wikipedia_tool import WikipediaKnowledgeTool
from .email_tool import EmailTool
from .discord_tool import DiscordTool
from .datetime_tool import DateTimeTool

calculator = MathTool()
text_extractor = TextExtractionTool()
wikipedia_tool = WikipediaKnowledgeTool()
email_tool = EmailTool()
discord_tool = DiscordTool()
datetime_tool = DateTimeTool()

BUILTIN_TOOLS = {
    "calculator": calculator,
    "extract_text": text_extractor,
    "search_wikipedia": wikipedia_tool,
    "send_notification": email_tool,
    "send_discord_message": discord_tool,
    "datetime_operations": datetime_tool,
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")