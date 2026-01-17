from datetime import datetime, timezone
import json
from typing import Union, List, Any
import importlib.metadata

from peargent.atlas.loader import load_pear

__all__ = ["create_pear", "load_pear"]

# Try to get version, handle if package not installed
try:
    VERSION = importlib.metadata.version("peargent")
except importlib.metadata.PackageNotFoundError:
    VERSION = "unknown"

def create_pear(obj: Union[Any, List[Any]], file_path: str):
    """
    Export a Peargent object (Agent, Pool, or List[Agent]) to a .pear file.
    
    Args:
        obj: The object to export (Agent, Pool, or list of Agents)
        file_path: Destination path for the .pear file
    """
    from peargent._core.agent import Agent
    from peargent._core.pool import Pool
    
    data = {}
    obj_type = "unknown"
    
    # Check type
    if isinstance(obj, list):
        # Assume list of agents
        obj_type = "collection"
        agents_data = []
        for item in obj:
            if hasattr(item, "to_dict"):
                agents_data.append(item.to_dict())
            else:
                raise ValueError(f"Item {item} in list is not a serializable Peargent object")
        data = {"agents": agents_data}
        
    elif isinstance(obj, Pool):
        obj_type = "pool"
        data = obj.to_dict()
        
    elif isinstance(obj, Agent):
        obj_type = "agent"
        data = obj.to_dict()
        
    else:
        raise ValueError(f"Unsupported object type for export: {type(obj)}")
        
    # Create envelope
    payload = {
        "meta": {
            "version": "0.1.0", # Schema version
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "library_version": VERSION
        },
        "type": obj_type,
        "data": data
    }
    
    # Write to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    print(f"Successfully exported {obj_type} to {file_path}")
