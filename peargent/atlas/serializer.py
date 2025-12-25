# peargent/atlas/serializer.py

"""
Serialization helpers for extracting source code and serializing complex objects.
Used by create_pear to generate complete .pear files.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Type


def get_source_code(func: Callable) -> Optional[str]:
    """
    Extract the source code of a function.
    
    Args:
        func: The function to extract source code from
        
    Returns:
        Source code as string, or None if unavailable
    """
    if func is None:
        return None
        
    try:
        return inspect.getsource(func)
    except (OSError, TypeError):
        # OSError: Source code not available (e.g., built-in, C extension)
        # TypeError: Not a function-like object
        try:
            # Try to get at least the signature
            sig = inspect.signature(func)
            return f"# Source unavailable\n# Signature: {func.__name__}{sig}"
        except (ValueError, TypeError):
            return f"# Source unavailable for: {getattr(func, '__name__', str(func))}"


def serialize_model_info(model: Any) -> Optional[Dict[str, Any]]:
    """
    Serialize model information to a dictionary.
    
    Args:
        model: The LLM model instance
        
    Returns:
        Dictionary with model metadata
    """
    if model is None:
        return None
        
    info = {
        "type": type(model).__name__,
    }
    
    # Try to get model name/identifier
    if hasattr(model, 'model_name'):
        info["model_name"] = model.model_name
    elif hasattr(model, 'model'):
        info["model_name"] = model.model
    elif hasattr(model, 'model_id'):
        info["model_name"] = model.model_id
    
    # Try to get API base if available
    if hasattr(model, 'api_base'):
        info["api_base"] = model.api_base
    elif hasattr(model, 'base_url'):
        info["api_base"] = model.base_url
        
    return info


def serialize_history_config(history: Any) -> Optional[Dict[str, Any]]:
    """
    Serialize conversation history configuration.
    
    Args:
        history: ConversationHistory instance
        
    Returns:
        Dictionary with history configuration
    """
    if history is None:
        return None
        
    config = {
        "type": type(history).__name__,
    }
    
    # Get current thread if available
    if hasattr(history, 'current_thread_id'):
        config["current_thread_id"] = history.current_thread_id
        
    # Get store type
    if hasattr(history, 'store'):
        config["store_type"] = type(history.store).__name__
        
    return config


def serialize_output_schema(schema: Optional[Type]) -> Optional[Dict[str, Any]]:
    """
    Serialize a Pydantic output schema to JSON Schema format.
    
    Args:
        schema: Pydantic model class
        
    Returns:
        JSON Schema dictionary or None
    """
    if schema is None:
        return None
        
    try:
        from pydantic import BaseModel
        
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Get JSON schema from Pydantic model
            return {
                "name": schema.__name__,
                "schema": schema.model_json_schema()
            }
    except ImportError:
        pass
    except Exception:
        pass
        
    # Fallback: just return the name
    return {
        "name": getattr(schema, '__name__', str(schema)),
        "schema": None
    }


def serialize_stop_conditions(stop) -> Optional[Dict[str, Any]]:
    """
    Serialize stop conditions configuration.
    
    Args:
        stop: Stop conditions object
        
    Returns:
        Dictionary with stop conditions info
    """
    if stop is None:
        return None
        
    info = {
        "type": type(stop).__name__,
        "description": str(stop)
    }
    
    # Try to get specific attributes
    if hasattr(stop, 'max_steps'):
        info["max_steps"] = stop.max_steps
    if hasattr(stop, 'conditions'):
        info["conditions"] = [str(c) for c in stop.conditions]
        
    return info


def serialize_type(t: type) -> str:
    """
    Convert a Python type to a string representation.
    
    Args:
        t: Python type
        
    Returns:
        String representation of the type
    """
    if isinstance(t, type):
        return t.__name__
    return str(t)
