# peargent/core/router.py

"""
Router module for agent routing and decision-making.
Provides routing strategies and intelligent agent selection.
"""

from typing import Callable, Optional, List, Dict, Any
from .state import State
from .agent import Agent


class RouterResult:
    """
    Result object from a router decision.

    Attributes:
        next_agent_name (Optional[str]): Name of the next agent to execute,
                                         or None to stop the workflow
    """

    def __init__(self, next_agent_name: Optional[str]):
        self.next_agent_name = next_agent_name


RouterFn = Callable[[State, int, Optional[Dict[str, Any]]], RouterResult]
"""Type alias for router functions: (state, call_count, last_result) -> RouterResult"""


def round_robin_router(agent_names: List[str]) -> RouterFn:
    """
    Create a simple round-robin router.

    Routes to agents in sequential order, stopping after all have been called once.

    Args:
        agent_names (List[str]): List of agent names to route between

    Returns:
        RouterFn: Router function that cycles through agents
    """
    def _router(
        state: State, call_count: int, last_result: Optional[dict]
    ) -> RouterResult:
        if call_count >= len(agent_names):
            return RouterResult(None)
        return RouterResult(agent_names[call_count % len(agent_names)])

    return _router


class RoutingAgent(Agent):
    """
    LLM-based intelligent routing agent.

    Uses an LLM to make context-aware decisions about which agent should act next
    based on conversation history, agent capabilities, and workflow progress.

    Attributes:
        agents (List[str]): List of allowed agent names for routing
        agent_objects (Dict): Mapping of agent names to Agent objects for context
    """

    def __init__(self, name, model, persona, agents, agent_objects=None, stop=None):
        # agents can be either a list of names or a list of Agent objects
        if agents and hasattr(agents[0], 'name'):
            # If passed Agent objects, extract names and store objects
            self.agent_objects = {a.name: a for a in agents}
            agent_names = [a.name for a in agents]
        else:
            # If passed strings, store as names (backwards compatibility)
            agent_names = agents
            self.agent_objects = agent_objects or {}

        # Initialize parent Agent class with empty tools list since routing agents don't use tools
        super().__init__(
            name=name,
            model=model,
            persona=persona,
            description=f"Routing agent that decides which agent should act next from: {', '.join(agent_names)}",
            tools=[],  # Routing agents don't use tools
            stop=stop
        )
        self.agents = agent_names  # allowed agent names

    def decide(self, state: State, last_result: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Decide which agent should act next.

        Uses LLM to analyze conversation history, agent capabilities, and workflow
        progress to make an intelligent routing decision.

        Args:
            state (State): Shared state containing conversation history
            last_result (Optional[Dict]): Result from the last agent execution

        Returns:
            Optional[str]: Name of the next agent to execute, or None to stop
        """
        # Build agent details for the template
        agent_details = []
        for agent_name in self.agents:
            agent_obj = self.agent_objects.get(agent_name)
            if agent_obj:
                agent_details.append({
                    "name": agent_obj.name,
                    "description": agent_obj.description or "No description available",
                    "tools": list(agent_obj.tools.keys()) if agent_obj.tools else []
                })
            else:
                # Fallback if agent object not available
                agent_details.append({
                    "name": agent_name,
                    "description": "No description available",
                    "tools": []
                })

        # Determine last agent
        last_agent = last_result.get("agent") if last_result else None

        # Use the Jinja2 template for routing
        template = self.jinja_env.get_template("routing_prompt.j2")
        prompt = template.render(
            persona=self.persona,
            history=state.history,
            agents=self.agents,
            agent_details=agent_details,
            last_agent=last_agent
        )

        response = self.model.generate(prompt).strip()

        if response.upper() == "STOP":
            return None
        if response not in self.agents:
            raise ValueError(f"RoutingAgent produced invalid agent name: '{response}'")

        return response

    def to_dict(self) -> Dict[str, Any]:
        """Convert routing agent to serializable dictionary."""
        from peargent.atlas.serializer import serialize_model_info, serialize_stop_conditions
        
        return {
            "type": "routing_agent",
            "name": self.name,
            "persona": self.persona,
            "description": self.description,
            "model": serialize_model_info(self.model),
            "agents": self.agents,
            "stop_conditions": serialize_stop_conditions(self.stop_conditions)
        }

