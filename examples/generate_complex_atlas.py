import sys
import os

# Add parent directory to path to import peargent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from peargent import create_agent, create_pool, create_tool, create_routing_agent
from peargent.atlas import create_pear
from peargent.models import groq

# --- Create Mock Tools ---

@create_tool(name="search_web", description="Searches the web for information about a given query.")
def search_web(query: str) -> str:
    return f"Results for {query}"

@create_tool(name="get_weather", description="Gets the current weather for a specific location.")
def get_weather(location: str) -> str:
    return "Sunny, 25C"

@create_tool(name="send_email", description="Sends an email to a recipient with a subject and body.")
def send_email(recipient: str, subject: str, body: str) -> bool:
    return True

@create_tool(name="read_file", description="Reads the content of a file from the local filesystem.")
def read_file(path: str) -> str:
    return "File content"

@create_tool(name="write_file", description="Writes content to a file in the local filesystem.")
def write_file(path: str, content: str) -> bool:
    return True

@create_tool(name="analyze_data", description="Analyzes a dataset and provides insights.")
def analyze_data(dataset: str) -> str:
    return "Analysis results"

@create_tool(name="generate_image", description="Generates an image based on a text prompt.")
def generate_image(prompt: str) -> str:
    return "image_url"

@create_tool(name="translate_text", description="Translates text from one language to another.")
def translate_text(text: str, target_language: str) -> str:
    return "Translated text"

@create_tool(name="summarize_text", description="Summarizes a long piece of text into a concise summary.")
def summarize_text(text: str) -> str:
    return "Summary"

@create_tool(name="execute_python", description="Executes a Python script in a sandboxed environment.")
def execute_python(script: str) -> str:
    return "Execution result"

@create_tool(name="query_database", description="Executes a SQL query against the connected database.")
def query_database(query: str) -> str:
    return "Query result"

@create_tool(name="schedule_meeting", description="Schedules a meeting on the user's calendar.")
def schedule_meeting(title: str, time: str) -> bool:
    return True

# --- Create Agents with Long Personas ---

long_persona_researcher = """You are a senior research analyst with over 20 years of experience in data science and academic research. 
Your goal is to uncover deep insights from vast amounts of information. You are meticulous, detail-oriented, and skeptical of unverified claims. 
You always cite your sources and prefer to cross-reference data points before forming a conclusion. 
When asked a question, you first break it down into sub-components, investigate each thoroughly, and then synthesize your findings into a comprehensive report.
You utilize advanced search techniques and data analysis tools to ensure accuracy."""

long_persona_editor = """You are the Chief Editor of a prestigious technology publication. You have an eagle eye for grammatical errors, stylistic inconsistencies, and tonal mismatches.
Your job is to ensure that every piece of content produced is polished, professional, and engaging. 
You value clarity and conciseness above all else. You are not afraid to rewrite entire sections if they fail to meet your high standards.
You believe that good writing is not just about correct grammar, but about compelling storytelling and logical flow.
You are tasked with refining raw drafts into masterpieces."""

long_persona_developer = """You are a 10x Full Stack Developer and Systems Architect. You live and breathe code. 
You are proficient in Python, TypeScript, Rust, and Go. You care deeply about clean architecture, SOLID principles, and performance optimization.
You are pragmatic but insist on high-quality implementations. You are often called upon to solve the most complex technical challenges that stump others.
When writing code, you always include error handling, type definitions, and comprehensive documentation.
You prefer automation over manual toil and always look for ways to optimize workflows."""

long_persona_creative = """You are a Visionary Creative Director with a background in fine arts and digital design.
You see the world in colors, shapes, and emotions. Your mission is to bring abstract concepts to life through visual media.
You are highly intuitive and empathetic, often understanding the user's emotional needs better than they do themselves.
You encourage bold experimentation and are never satisfied with the status quo. 
You use generative AI tools as an extension of your artistic capability to act as a force multiplier for your imagination."""

agent_researcher = create_agent(
    name="Research_Analyst",
    description="Conducts deep research and data analysis.",
    persona=long_persona_researcher,
    tools=[search_web, read_file, analyze_data], # 3 tools
    model=groq("groq/llama-3.2-70b-instruct")
)

agent_editor = create_agent(
    name="Chief_Editor",
    description="Reviews and refines content.",
    persona=long_persona_editor,
    tools=[summarize_text, translate_text, write_file], # 3 tools
    model=groq("groq/llama-3.2-70b-instruct")
)

agent_developer = create_agent(
    name="Lead_Developer",
    description="Writes and executes code.",
    persona=long_persona_developer,
    tools=[execute_python, query_database, read_file], # 3 tools
    model=groq("groq/llama-3.2-70b-instruct")   
)

agent_creative = create_agent(
    name="Creative_Director",
    description="Generates assets and visual concepts.",
    persona=long_persona_creative,
    tools=[generate_image, send_email, schedule_meeting], # 3 tools
    model=groq("groq/llama-3.2-70b-instruct")
)

# --- Create Router and Pool ---

all_agents = [agent_researcher, agent_editor, agent_developer, agent_creative]

router_persona = """You are the Master Orchestrator. Your role is to understand user requests and delegate them to the most appropriate specialist agent.
You verify the input, clarify ambiguities, and ensure that the chosen agent has the necessary context to succeed.
You do not perform the work yourself; you manage the team of experts."""

router_agent = create_routing_agent(
    name="Orchestrator",
    model=groq("groq/llama-3.2-70b-instruct"),
    persona=router_persona,
    agents=all_agents
)

pool = create_pool(
    agents=all_agents,
    router=router_agent,
    max_iter=10
)

# --- Generate .pear ---

output_file = "complex_pool_with_router.pear"
print(f"Generating {output_file}...")
create_pear(pool, output_file)
print("Done!")
