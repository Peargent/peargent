# my_agent_lib/__init__.py

from os import name
from typing import Optional, Union, Type
from dotenv import load_dotenv
import inspect

from peargent._core.router import round_robin_router
from peargent._core.state import State

load_dotenv()

from ._core.agent import Agent
from ._core.tool import Tool
from .tools import get_tool_by_name
from peargent._core.router import RouterResult, RoutingAgent
from ._core.stopping import limit_steps, StepLimitCondition
from ._core.pool import Pool
from ._core.streaming import UpdateType, StreamUpdate
from .history import (
    ConversationHistory,
    HistoryStore,
    FunctionalHistoryStore,
    InMemoryHistoryStore,
    FileHistoryStore,
    Thread,
    Message,
)
from .storage import (
    StorageType,
    InMemory,
    File,
    Sqlite,
    Postgresql,
    Redis
)
from ._config import HistoryConfig

# Try to import SQL-based stores
try:
    from .history import PostgreSQLHistoryStore
except ImportError:
    PostgreSQLHistoryStore = None

try:
    from .history import SQLiteHistoryStore
except ImportError:
    SQLiteHistoryStore = None

# Define what gets imported with "from peargent import *"
__all__ = [
    'create_agent',
    'create_tool',
    'create_pool',
    'create_routing_agent',
    'create_history',
    'Agent',
    'Tool',
    'Pool',
    'RoutingAgent',
    'RouterResult',
    'State',
    'UpdateType',
    'StreamUpdate',
    'InMemory',
    'File',
    'Sqlite',
    'Postgresql',
    'Redis',
    'limit_steps',
    'StepLimitCondition',
    'ConversationHistory',
    'HistoryStore',
    'FunctionalHistoryStore',
    'InMemoryHistoryStore',
    'FileHistoryStore',
    'Thread',
    'Message',
    'HistoryConfig',
]

# Add SQL stores to __all__ if available
if PostgreSQLHistoryStore:
    __all__.append('PostgreSQLHistoryStore')
if SQLiteHistoryStore:
    __all__.append('SQLiteHistoryStore')

# Sentinel value to detect if tracing was explicitly passed
_TRACING_NOT_SET = object()

def create_agent(name: str, description: str, persona: str, model=None, tools=None, stop=None, history=None, tracing=_TRACING_NOT_SET, output_schema=None, max_retries: int = 3):
    """
    Create an agent with optional persistent history.

    Args:
        name: Agent name
        description: Agent description
        persona: Agent persona/system prompt
        model: LLM model instance
        tools: List of tool names (str) or Tool objects
        stop: Stop condition
        history: Optional ConversationHistory, HistoryConfig, or None for persistent conversation storage
        tracing: Enable/disable tracing for this agent. Behavior:
                 - None (default): Inherits from global tracer if enable_tracing() was called
                 - True: Explicitly enable tracing for this agent
                 - False: Explicitly disable tracing (opt-out), even if global tracing is enabled
        output_schema: Optional Pydantic model for structured output validation
        max_retries: Maximum number of retries for structured output validation (default: 3)

    Returns:
        Agent instance

    Examples:
        # Agent with default tracing behavior (inherits from global)
        enable_tracing(store_type="sqlite", ...)  # Enable global tracing
        agent = create_agent(
            name="Assistant",
            description="A helpful assistant",
            persona="You are helpful",
            model=groq()
        )  # This agent will be traced

        # Explicitly enable tracing for one agent
        agent = create_agent(..., tracing=True)  # Always traced

        # Opt-out from global tracing
        enable_tracing(...)  # Global tracing on
        agent = create_agent(..., tracing=False)  # This agent won't be traced

        # With history
        agent = create_agent(
            name="Assistant",
            description="A helpful assistant",
            persona="You are helpful",
            model=groq(),
            history=HistoryConfig(
                auto_manage_context=True,
                max_context_messages=10,
                strategy="smart",
                store=File(storage_dir="./conversations")
            )
        )
    """
    parsed_tools = []
    for t in tools or []:
        if isinstance(t, str):
            parsed_tools.append(get_tool_by_name(t))
        elif isinstance(t, Tool):
            parsed_tools.append(t)
        else:
            raise ValueError("Tools must be instances of the Tool class.")

    # Determine if tracing was explicitly set
    tracing_explicitly_set = tracing is not _TRACING_NOT_SET

    # Smart tracing logic:
    # 1. If tracing=True explicitly -> enable tracing
    # 2. If tracing=False explicitly -> disable tracing (opt-out)
    # 3. If tracing not set (None/default):
    #    - Check if global tracer was configured (enable_tracing() was called)
    #    - If global tracer configured and enabled -> inherit (enable tracing)
    #    - If global tracer not configured -> disable tracing (default off)
    if tracing is _TRACING_NOT_SET:
        # Check if global tracer was explicitly configured
        from peargent.observability.tracer import _global_tracer
        if _global_tracer is not None and _global_tracer.enabled:
            # Global tracer was configured with enable_tracing() and is enabled
            actual_tracing = True
        else:
            # No global tracer configured, default to disabled
            actual_tracing = False
    else:
        # User explicitly set tracing=True or tracing=False
        actual_tracing = tracing

    # Handle HistoryConfig
    if isinstance(history, HistoryConfig):
        config = history
        actual_history = config.create_history()
        return Agent(
            name=name,
            description=description,
            persona=persona,
            model=model,
            tools=parsed_tools,
            stop=stop,
            history=actual_history,
            tracing=actual_tracing,
            _tracing_explicitly_set=tracing_explicitly_set,
            output_schema=output_schema,
            max_retries=max_retries
        )

    # Legacy behavior
    return Agent(
        name=name,
        description=description,
        persona=persona,
        model=model,
        tools=parsed_tools,
        stop=stop,
        history=history,
        tracing=actual_tracing,
        _tracing_explicitly_set=tracing_explicitly_set,
        output_schema=output_schema,
        max_retries=max_retries
    )

def create_tool(
    name=None,
    description=None,
    input_parameters=None,
    call_function=None,
    timeout: Optional[float] = None,
    max_retries: int = 0,
    retry_delay: float = 1.0,
    retry_backoff: bool = True,
    on_error: str = "raise",
    output_schema: Optional[Type] = None
):
    """
    Create a tool that agents can use. Works as both a function and a decorator.

    Args:
        name: Tool name (required for function mode, optional for decorator mode - auto-inferred from function name)
        description: Tool description (required for function mode, optional for decorator - uses docstring)
        input_parameters: Dictionary of parameter names to types (required for function mode, optional for decorator - auto-inferred)
        call_function: Function to execute when tool is called (required for function mode only)
        timeout: Maximum execution time in seconds (None = no limit)
        max_retries: Number of retry attempts on failure (0 = no retries)
        retry_delay: Initial delay between retries in seconds
        retry_backoff: Use exponential backoff for retries (True = exponential, False = fixed delay)
        on_error: Error handling strategy - "raise" (default), "return_error", or "return_none"
        output_schema: Optional Pydantic model for output validation

    Returns:
        Tool instance (function mode) or decorated function (decorator mode)

    Examples:
        # FUNCTION MODE (backward compatible)
        tool = create_tool("calculator", "Does math", {"expr": str}, eval_expr)

        # Function mode with timeout
        tool = create_tool("api_call", "Calls API", {"url": str}, fetch_api,
                          timeout=5.0)

        # DECORATOR MODE - Auto-inference
        @create_tool()
        def get_weather(city: str) -> dict:
            '''Get current weather for a city'''
            return weather_api.get(city)

        # Decorator mode - Custom parameters
        @create_tool(name="search", description="Search docs", timeout=5.0)
        def search_docs(query: str) -> list:
            return db.search(query)

        # Decorator mode - Without parentheses
        @create_tool
        def calculate(expr: str) -> float:
            '''Evaluate expression'''
            return eval(expr)
    """
    # CASE 1: Function mode - call_function is provided
    if call_function is not None:
        # Traditional usage: create_tool(name, desc, params, func, ...)
        if name is None:
            raise ValueError("name is required when call_function is provided")
        if description is None:
            raise ValueError("description is required when call_function is provided")
        if input_parameters is None:
            raise ValueError("input_parameters is required when call_function is provided")

        return Tool(
            name=name,
            description=description,
            input_parameters=input_parameters,
            call_function=call_function,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            on_error=on_error,
            output_schema=output_schema
        )

    # CASE 2: Decorator mode without parentheses - @create_tool
    if callable(name):
        func = name
        return _create_decorated_tool(
            func=func,
            name=None,
            description=None,
            input_parameters=None,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            on_error=on_error,
            output_schema=output_schema
        )

    # CASE 3: Decorator mode with parentheses - @create_tool(...) or @create_tool()
    def decorator(func):
        return _create_decorated_tool(
            func=func,
            name=name,
            description=description,
            input_parameters=input_parameters,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            on_error=on_error,
            output_schema=output_schema
        )

    return decorator


def _create_decorated_tool(
    func,
    name=None,
    description=None,
    input_parameters=None,
    timeout=None,
    max_retries=0,
    retry_delay=1.0,
    retry_backoff=True,
    on_error="raise",
    output_schema=None
):
    """
    Internal helper to create a tool from a decorated function.
    Auto-infers name, description, and parameters from the function.
    """
    # Infer tool name from function name if not provided
    tool_name = name or func.__name__

    # Infer description from docstring if not provided
    if description is not None:
        tool_description = description
    else:
        # Use docstring if available, otherwise generate default
        tool_description = func.__doc__.strip() if func.__doc__ else f"Tool: {tool_name}"

    # Infer input_parameters from function signature if not provided
    if input_parameters is None:
        sig = inspect.signature(func)
        inferred_params = {}

        for param_name, param in sig.parameters.items():
            # Only include parameters without defaults as required
            # Parameters with defaults are optional and shouldn't be in input_parameters
            if param.default == inspect.Parameter.empty:
                if param.annotation != inspect.Parameter.empty:
                    # Use type annotation
                    inferred_params[param_name] = param.annotation
                else:
                    # No type hint provided, default to str
                    inferred_params[param_name] = str

        tool_input_params = inferred_params
    else:
        tool_input_params = input_parameters

    # Create and return the tool
    return Tool(
        name=tool_name,
        description=tool_description,
        input_parameters=tool_input_params,
        call_function=func,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_backoff=retry_backoff,
        on_error=on_error,
        output_schema=output_schema
    )


def create_pool(agents, default_model=None, router=None, max_iter=5, default_state=None, history=None, tracing=False):
    """
    Create a pool of agents with optional persistent history.

    Args:
        agents: List of Agent instances
        default_model: Default LLM model for agents without one
        router: Router function or RoutingAgent
        max_iter: Maximum number of agent executions
        default_state: Optional State instance
        history: Optional ConversationHistory, HistoryConfig, or None for persistent conversation storage
        tracing: Enable tracing for all agents in the pool (default: False).
                 Individual agents with explicit tracing=False will not be overridden.

    Returns:
        Pool instance

    Examples:
        # New DSL with HistoryConfig
        pool = create_pool(
            agents=[agent1, agent2],
            history=HistoryConfig(
                auto_manage_context=True,
                max_context_messages=15,
                strategy="smart",
                store=InMemory()
            )
        )

        # Enable tracing for all agents in pool
        pool = create_pool(
            agents=[agent1, agent2, agent3],
            tracing=True
        )

        # Mix: pool tracing enabled, but one agent explicitly opts out
        agent1 = create_agent(..., tracing=False)  # Will stay False
        agent2 = create_agent(...)  # Will become True from pool
        pool = create_pool(agents=[agent1, agent2], tracing=True)
    """
    # Handle HistoryConfig
    actual_history = None
    if isinstance(history, HistoryConfig):
        actual_history = history.create_history()
    else:
        actual_history = history

    return Pool(
        agents=agents,
        default_model=default_model,
        router=router or round_robin_router([agent.name for agent in agents]),
        max_iter=max_iter,
        default_state=default_state or State(),
        history=actual_history,
        tracing=tracing
    )

def create_routing_agent(name: str, model, persona: str, agents: list):
    """
    Create a routing agent that intelligently selects the next agent.

    Args:
        name: Router agent name
        model: LLM model instance
        persona: Router persona/system prompt
        agents: List of available agents

    Returns:
        RoutingAgent instance
    """
    return RoutingAgent(name=name, model=model, persona=persona, agents=agents)

def create_history(store_type=None, **kwargs) -> ConversationHistory:
    """
    Create a conversation history manager.

    Args:
        store_type: Either a string ("session_buffer", "file", "sqlite", "postgresql") for backward compatibility,
                   or a StorageType instance (InMemory(), File(), Sqlite(), Postgresql(), Redis()) for new DSL.
        **kwargs: Additional parameters for backward compatibility with string-based API:
                 - storage_dir: Directory for file-based storage
                 - connection_string: PostgreSQL connection string
                 - database_path: SQLite database file path
                 - table_prefix: Prefix for database tables

    Returns:
        ConversationHistory instance

    Examples:
        # New DSL (recommended)
        history = create_history(store_type=InMemory())
        history = create_history(store_type=File(storage_dir="./my_conversations"))
        history = create_history(store_type=Sqlite(database_path="./my_app.db"))
        history = create_history(store_type=Postgresql(
            connection_string="postgresql://user:pass@localhost:5432/mydb"
        ))
        history = create_history(store_type=Redis(host="localhost", port=6379))

        # Old string-based API (backward compatibility)
        history = create_history("session_buffer")
        history = create_history("file", storage_dir="./my_conversations")
        history = create_history("sqlite", database_path="./my_app.db")
        history = create_history("postgresql", connection_string="postgresql://...")
    """
    # Default to session_buffer if no store_type provided
    if store_type is None:
        store_type = "session_buffer"

    # Handle new class-based DSL
    if isinstance(store_type, StorageType):
        if isinstance(store_type, InMemory):
            store = InMemoryHistoryStore()
        elif isinstance(store_type, File):
            store = FileHistoryStore(storage_dir=store_type.storage_dir)
        elif isinstance(store_type, Sqlite):
            if not SQLiteHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for SQLite storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = SQLiteHistoryStore(
                database_path=store_type.database_path,
                table_prefix=store_type.table_prefix
            )
        elif isinstance(store_type, Postgresql):
            if not PostgreSQLHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for PostgreSQL storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = PostgreSQLHistoryStore(
                connection_string=store_type.connection_string,
                table_prefix=store_type.table_prefix
            )
        elif isinstance(store_type, Redis):
            # Import Redis store dynamically
            try:
                from .history import RedisHistoryStore
            except ImportError:
                RedisHistoryStore = None
            
            if not RedisHistoryStore:
                raise ImportError(
                    "Redis is required for Redis storage. "
                    "Install it with: pip install redis"
                )
            store = RedisHistoryStore(
                host=store_type.host,
                port=store_type.port,
                db=store_type.db,
                password=store_type.password,
                key_prefix=store_type.key_prefix
            )
        else:
            raise ValueError(f"Unknown storage type: {type(store_type)}")
    
    # Handle backward-compatible string-based API
    elif isinstance(store_type, str):
        # Extract keyword arguments for backward compatibility
        storage_dir = kwargs.get("storage_dir", ".peargent_history")
        connection_string = kwargs.get("connection_string")
        database_path = kwargs.get("database_path", "peargent_history.db")
        table_prefix = kwargs.get("table_prefix", "peargent")
        
        if store_type == "session_buffer":
            store = InMemoryHistoryStore()
        elif store_type == "file":
            store = FileHistoryStore(storage_dir=storage_dir)
        elif store_type == "sqlite":
            if not SQLiteHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for SQLite storage. "
                    "Install it with: pip install sqlalchemy"
                )
            store = SQLiteHistoryStore(
                database_path=database_path,
                table_prefix=table_prefix
            )
        elif store_type == "postgresql":
            if not PostgreSQLHistoryStore:
                raise ImportError(
                    "SQLAlchemy is required for PostgreSQL storage. "
                    "Install it with: pip install sqlalchemy"
                )
            if not connection_string:
                raise ValueError("connection_string is required for PostgreSQL storage")
            store = PostgreSQLHistoryStore(
                connection_string=connection_string,
                table_prefix=table_prefix
            )
        else:
            raise ValueError(f"Unknown store_type: {store_type}. Use 'session_buffer', 'file', 'sqlite', or 'postgresql'")
    else:
        raise ValueError(f"store_type must be a string or StorageType instance, got {type(store_type)}")

    return ConversationHistory(store=store)