# peargent/atlas/loader.py

"""
Loader module for deserializing .pear files back into runnable Python objects.
Used to run agents/pools exported from Peargent Atlas.
"""

import json
from typing import Any, Dict, Optional, Union
from pathlib import Path


def load_pear(file_path: str) -> Union["Agent", "Pool", list]:
    """
    Load a .pear file and reconstruct the agent/pool/collection.
    
    Args:
        file_path: Path to the .pear file
        
    Returns:
        Agent, Pool, or list of Agents depending on the file type
    """
    from peargent._core.agent import Agent
    from peargent._core.pool import Pool
    
    path = Path(file_path)
    # Validate file extension
    if not str(path).endswith(".pear"):
        raise ValueError(f"File must be a .pear file: {file_path}")

    if not path.exists():
        raise FileNotFoundError(f"Pear file not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    
    pear_type = payload.get("type", "unknown")
    data = payload.get("data", {})
    
    # Handle 'project' type from Atlas (same as pool with settings wrapper)
    if pear_type == "project":
        # Atlas exports with a 'pool' key inside data
        pool_data = data.get("pool")
        if pool_data:
            return _parse_pool(pool_data)
        # Check for unassigned agents
        unassigned = data.get("unassigned_agents", [])
        if unassigned:
            return [_parse_agent(a) for a in unassigned]
        raise ValueError("Project file contains no pool or agents")
    
    elif pear_type == "pool":
        return _parse_pool(data)
    
    elif pear_type == "agent":
        return _parse_agent(data)
    
    elif pear_type == "collection":
        agents_data = data.get("agents", [])
        return [_parse_agent(a) for a in agents_data]
    
    else:
        raise ValueError(f"Unknown .pear file type: {pear_type}")


def _parse_model(config: Optional[Union[Dict, str]], temperature: float = 0.7, fallback_model: Any = None) -> Any:
    """
    Instantiate a model from serialized config.
    
    Args:
        config: Model config dict with 'type' and 'model_name', or str for shorthand
        temperature: Temperature parameter for the model
        fallback_model: Model to use if the specified model fails to initialize
        
    Returns:
        Model instance
    """
    from peargent import models
    
    if config is None:
        return fallback_model
    
    params = {"temperature": temperature}
    
    def try_create_model(model_name: str, model_type: str = None):
        """Try to create a model, return None on failure."""
        model_name_lower = model_name.lower() if model_name else ""
        type_lower = (model_type or "").lower()
        
        try:
            # Determine which model factory to use
            if "gemini" in type_lower or "gemini" in model_name_lower:
                return models.gemini(model_name, parameters=params)
            elif "anthropic" in type_lower or "claude" in type_lower or "claude" in model_name_lower:
                return models.anthropic(model_name, parameters=params)
            elif "groq" in type_lower or "llama" in model_name_lower or "mixtral" in model_name_lower:
                return models.groq(model_name, parameters=params)
            elif "openai" in type_lower or "gpt" in model_name_lower or "o1" in model_name_lower or "o3" in model_name_lower:
                return models.openai(model_name, parameters=params)
            else:
                # Default: try OpenAI
                return models.openai(model_name, parameters=params)
        except EnvironmentError:
            # API key not found - return None to trigger fallback
            return None
    
    # Handle string shorthand like "gpt-4o"
    if isinstance(config, str):
        model = try_create_model(config)
        if model is not None:
            return model
        # Fallback
        if fallback_model is not None:
            print(f"⚠️  Model '{config}' unavailable (missing API key), using fallback")
            return fallback_model
        raise EnvironmentError(f"Model '{config}' requires API key but none is set")
    
    # Handle dict config
    model_type = config.get("type", "")
    model_name = config.get("model_name", "gpt-4o")
    
    model = try_create_model(model_name, model_type)
    if model is not None:
        return model
    
    # Fallback
    if fallback_model is not None:
        print(f"⚠️  Model '{model_name}' unavailable (missing API key), using fallback")
        return fallback_model
    raise EnvironmentError(f"Model '{model_name}' requires API key but none is set")


def _parse_tool(config: Dict) -> Any:
    """
    Reconstruct a tool from serialized config.
    
    The tool's function_body contains the actual Python code.
    We execute it to define the function, then wrap it with create_tool.
    
    Supports all tool parameters: timeout, max_retries, retry_delay, retry_backoff, on_error
    """
    from peargent import create_tool
    from datetime import datetime  # Common import for tools
    
    tool_name = config.get("name", "unnamed_tool")
    description = config.get("description", "")
    function_body = config.get("function_body", "")
    
    # Parse optional tool parameters
    timeout = config.get("timeout")  # None means no timeout
    max_retries = config.get("max_retries", 0)
    retry_delay = config.get("retry_delay", 1.0)
    retry_backoff = config.get("retry_backoff", True)
    on_error = config.get("on_error", "raise")
    
    input_parameters = config.get("input_parameters")

    # Common kwargs for create_tool
    tool_kwargs = {
        "name": tool_name,
        "description": description,
    }
    
    if input_parameters:
        # Convert string types to actual types
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "Any": Any
        }
        converted_params = {}
        for k, v in input_parameters.items():
            if isinstance(v, str):
                # Remove quotes if present? types usually come as raw strings "str"
                clean_v = v.strip("'\"")
                converted_params[k] = type_map.get(clean_v, Any)
            else:
                converted_params[k] = v
                
        tool_kwargs["input_parameters"] = converted_params

    
    # Only add optional params if they have non-default values
    if timeout is not None:
        tool_kwargs["timeout"] = timeout
    if max_retries > 0:
        tool_kwargs["max_retries"] = max_retries
    if retry_delay != 1.0:
        tool_kwargs["retry_delay"] = retry_delay
    if not retry_backoff:
        tool_kwargs["retry_backoff"] = retry_backoff
    if on_error != "raise":
        tool_kwargs["on_error"] = on_error
    
    if not function_body:
        # Fallback: create a dummy tool that returns a message
        @create_tool(**tool_kwargs)
        def dummy_tool(**kwargs):
            return f"Tool '{tool_name}' has no implementation"
        return dummy_tool
    
    # Create a namespace with common imports for tool execution
    namespace = {
        "datetime": datetime,
        "__builtins__": __builtins__,
    }
    
    try:
        # Execute the function body to define the function
        exec(function_body, namespace)
        
        # The function should be defined with the tool_name
        if tool_name in namespace:
            func = namespace[tool_name]
        else:
            # Try to find any callable defined
            for key, val in namespace.items():
                if callable(val) and not key.startswith("_"):
                    func = val
                    break
            else:
                raise ValueError(f"Could not find function in tool body: {tool_name}")
        
        # Wrap the function as a tool with all parameters
        tool_kwargs["call_function"] = func
        return create_tool(**tool_kwargs)
    except Exception as e:
        # Create a fallback tool that reports the error
        err_msg = str(e)
        @create_tool(name=tool_name, description=description)
        def error_tool(**kwargs):
            return f"Tool '{tool_name}' failed to load: {err_msg}"
        return error_tool


def _parse_history(config: Optional[Dict]) -> Any:
    """
    Reconstruct a history store from config.
    Automatically creates a thread for persistent stores.
    """
    from peargent import create_history
    
    if config is None:
        return None
    
    store_type = config.get("type", "session_buffer").lower()
    history = None
    
    if "sqlite" in store_type:
        db_path = config.get("db_path", "./history.db")
        history = create_history("sqlite", database_path=db_path)
    elif "postgresql" in store_type:
        conn_string = config.get("connection_string", "")
        history = create_history("postgresql", connection_string=conn_string)
    elif "file" in store_type:
        file_path = config.get("file_path", "./history.json")
        history = create_history("file", file_path=file_path)
    else:
        history = create_history("session_buffer")
    
    # Create a thread so history is ready to use
    if history is not None and hasattr(history, 'create_thread'):
        try:
            history.create_thread(metadata={"source": "peargent-cli"})
        except Exception:
            pass  # Thread might already exist or store doesn't support it
    
    return history


def _parse_agent(config: Dict, default_model: Any = None) -> "Agent":
    """
    Reconstruct an Agent from serialized config.
    
    Handles all agent parameters: name, description, persona, model, tools, 
    stop, history, tracing, output_schema, max_retries
    """
    from peargent import create_agent
    from peargent._core.stopping import limit_steps
    
    name = config.get("name", "Agent")
    description = config.get("description", "")
    persona = config.get("persona", "You are a helpful AI assistant.")
    temperature = config.get("temperature", 0.7)
    tracing = config.get("tracing")
    max_retries = config.get("max_retries", 3)
    
    # Parse stop conditions
    stop = None
    stop_config = config.get("stop_conditions")
    if stop_config:
        max_steps = stop_config.get("max_steps", 5)
        stop = limit_steps(max_steps)
    
    # Parse output_schema (just store the schema info for now, can't reconstruct Pydantic models)
    # TODO: Support reconstructing Pydantic schemas from JSON schema
    output_schema = None  # config.get("output_schema") - needs special handling
    
    # Parse model - use default_model as fallback if API key is missing
    model_config = config.get("model")
    model = _parse_model(model_config, temperature, fallback_model=default_model) if model_config else default_model
    
    # Parse tools
    tools_config = config.get("tools", [])
    tools = [_parse_tool(t) for t in tools_config] if tools_config else None
    
    # Parse history (agent-level)
    history_config = config.get("history")
    history = _parse_history(history_config) if history_config else None
    
    return create_agent(
        name=name,
        description=description,
        persona=persona,
        model=model,
        tools=tools,
        stop=stop,
        history=history,
        tracing=tracing if tracing is not None else True,
        output_schema=output_schema,
        max_retries=max_retries
    )


def _parse_pool(config: Dict) -> "Pool":
    """
    Reconstruct a Pool from serialized config.
    """
    from peargent import create_pool
    from peargent._core.router import round_robin_router
    
    max_iter = config.get("max_iter", 5)
    tracing = config.get("tracing", True)
    
    # Parse pool-level model (default for agents)
    pool_model_config = config.get("model")
    default_model = _parse_model(pool_model_config) if pool_model_config else None
    
    # Parse agents
    agents_config = config.get("agents", [])
    agents = [_parse_agent(a, default_model) for a in agents_config]
    
    # Parse router - pass default_model for semantic router fallback
    router_config = config.get("router")
    router = _parse_router(router_config, agents, default_model) if router_config else round_robin_router
    
    # Parse pool-level history
    history_config = config.get("history")
    history = _parse_history(history_config) if history_config else None
    
    return create_pool(
        agents=agents,
        default_model=default_model,
        router=router,
        max_iter=max_iter,
        history=history,
        tracing=tracing
    )


def _parse_router(config: Optional[Dict], agents: list, fallback_model: Any = None) -> Any:
    """
    Reconstruct a router from config.
    
    For 'semantic_router' or 'routing_agent' type, we create a RoutingAgent.
    Otherwise, we use the default round_robin_router.
    """
    from peargent import create_routing_agent
    from peargent._core.router import round_robin_router
    
    if config is None:
        return round_robin_router
    
    router_type = config.get("type", "round_robin")
    
    name = config.get("name", "Router")
    persona = config.get("persona", "You are a routing agent that directs requests to the appropriate specialist agent.")
    
    # semantic_router: Embedding based
    if router_type == "semantic_router":
        from peargent import create_semantic_router
        model_config = config.get("model", "gpt-4o") 
        model = _parse_model(model_config, fallback_model=fallback_model)
        
        return create_semantic_router(
            name=name,
            model=model,
            agents=agents,
            persona=persona
        )
        
    # routing_agent: LLM based
    if router_type == "routing_agent":
        from peargent import create_routing_agent
        model_config = config.get("model", "gpt-4o")
        model = _parse_model(model_config, fallback_model=fallback_model)
        
        return create_routing_agent(
            name=name,
            model=model,
            persona=persona,
            agents=agents
        )
    
    # Default to round robin
    return round_robin_router
