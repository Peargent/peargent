# peargent/core/pool.py

"""
Pool module for orchestrating multiple agents.
Manages agent execution, routing, and shared state.
"""

from typing import List, Dict, Optional, Any, TYPE_CHECKING
from .state import State
from .router import RouterFn, RouterResult

if TYPE_CHECKING:
    from peargent.history import ConversationHistory


class Pool:
    """
    Orchestrates multiple agents with intelligent routing.

    The Pool manages a collection of agents, uses a router to decide which agent
    should act next, maintains shared state across all agents, and chains agent
    outputs as inputs to subsequent agents.

    Attributes:
        agents_dict (Dict): Mapping of agent names to Agent objects
        agents_names (List[str]): List of all agent names
        default_model: Default LLM model for agents without one
        router: Function or RoutingAgent that decides next agent
        max_iter (int): Maximum number of agent executions
        state (State): Shared conversation history and key-value store
    """
    def __init__(
        self,
        agents: List,
        default_model=None,
        router: Optional[RouterFn] = None,
        max_iter: int = 5,
        default_state: Optional[State] = None,
        history: Optional["ConversationHistory"] = None,
        tracing: bool = False,
    ):
        # Assign default model to agents that don't have one
        for agent in agents:
            if agent.model is None and default_model is not None:
                agent.model = default_model

        # Enable tracing for all agents if tracing=True, unless agent explicitly has tracing set
        if tracing:
            for agent in agents:
                # Only set tracing if the agent doesn't have an explicit tracing value
                # Check if _tracing_explicitly_set exists and is False (not explicitly set)
                if not getattr(agent, '_tracing_explicitly_set', False):
                    agent.tracing = True

        self.agents_dict: Dict[str, any] = {a.name: a for a in agents}
        self.agents_names = list(self.agents_dict.keys())
        self.default_model = default_model
        self.router = router or (lambda state, call_count, last: RouterResult(None))
        self.max_iter = max_iter
        self.history = history
        self.tracing = tracing

        # Create state with history manager if provided
        if default_state:
            self.state = default_state
            # Update state's history manager if not already set
            if history and not self.state.history_manager:
                self.state.history_manager = history
            # Update state's agents if not already set
            if not self.state.agents:
                self.state.agents = self.agents_dict
        else:
            self.state = State(history_manager=history, agents=self.agents_dict)

        # If router is a RoutingAgent, provide it with agent objects for better context
        if hasattr(self.router, "agent_objects"):
            self.router.agent_objects = self.agents_dict

    def run(self, user_input: str) -> str:
        """
        Execute the multi-agent workflow.

        Iteratively routes to agents based on router decisions, chains outputs,
        and maintains shared state until completion or max iterations reached.

        Args:
            user_input (str): The initial user request or input

        Returns:
            str: The final assistant response from the last executed agent
        """
        self.state.add_message(role="user", content=user_input, agent=None)
        
        last_result = None
        call_count = 0
        current_input = user_input
        
        while call_count < self.max_iter:
            
            if hasattr(self.router, "decide"):  # RoutingAgent-like
                route_name = self.router.decide(self.state, last_result=last_result)
                route = RouterResult(route_name)
            else:  # Old style function-based router
                route = self.router(self.state, call_count=call_count, last_result=last_result)
                
            if not route or route.next_agent_name is None:
                break
            
            agent = self.agents_dict.get(route.next_agent_name)
            if not agent:
                raise ValueError(f"Router selected unknown agent '{route.next_agent_name}'")
            
            # Execute the selected agent
            agent_input = current_input
            output = agent.run(agent_input)

            # Store agent output in shared state
            self.state.add_message("assistant", str(output), agent=agent.name)
            last_result = {
                "agent": agent.name,
                "output": output,
                "tools_used": [m['content']['name'] for m in agent.temporary_memory if m.get('role') == 'tool'] if hasattr(agent, 'temporary_memory') else []
            }
            
            # Set the output as input for the next agent
            current_input = str(output)
            call_count += 1
            
        final = next((m["content"] for m in reversed(self.state.history) if m["role"] == "assistant"), "")
        return final

    def stream(self, user_input: str):
        """
        Stream the pool execution, yielding chunks from each agent.

        Only streams the final agent's output. For full observability
        of all agents, use observe() instead.

        Args:
            user_input: The initial user request

        Yields:
            String chunks from the final agent's response

        Example:
            for chunk in pool.stream("Explain AI"):
                print(chunk, end="", flush=True)
        """
        self.state.add_message(role="user", content=user_input, agent=None)

        last_result = None
        call_count = 0
        current_input = user_input

        while call_count < self.max_iter:

            if hasattr(self.router, "decide"):
                route_name = self.router.decide(self.state, last_result=last_result)
                route = RouterResult(route_name)
            else:
                route = self.router(self.state, call_count=call_count, last_result=last_result)

            if not route or route.next_agent_name is None:
                break

            agent = self.agents_dict.get(route.next_agent_name)
            if not agent:
                raise ValueError(f"Router selected unknown agent '{route.next_agent_name}'")

            # Check if this is the last agent
            is_last = call_count == self.max_iter - 1

            if is_last or not hasattr(agent, 'stream'):
                # Stream the final agent's output
                if hasattr(agent, 'stream'):
                    full_output = ""
                    for chunk in agent.stream(current_input):
                        full_output += chunk
                        yield chunk

                    output = full_output
                else:
                    output = agent.run(current_input)
                    yield output
            else:
                # Run intermediate agents normally
                output = agent.run(current_input)

            # Store agent output in shared state
            self.state.add_message("assistant", str(output), agent=agent.name)
            last_result = {
                "agent": agent.name,
                "output": output,
                "tools_used": [m['content']['name'] for m in agent.temporary_memory if m.get('role') == 'tool'] if hasattr(agent, 'temporary_memory') else []
            }

            # Set the output as input for the next agent
            current_input = str(output)
            call_count += 1

    def stream_observe(self, user_input: str):
        """
        Stream the entire pool execution with rich updates and metadata.

        Yields StreamUpdate objects for every agent in the pool,
        including start/end events, tokens, and costs.

        Args:
            user_input: The initial user request

        Yields:
            StreamUpdate objects with execution details

        Example:
            for update in pool.stream_observe("Explain AI"):
                if update.is_agent_start:
                    print(f"\\n[{update.agent}] Starting...")
                elif update.is_token:
                    print(update.content, end="", flush=True)
                elif update.is_agent_end:
                    print(f"\\n[{update.agent}] {update.tokens} tokens, ${update.cost:.6f}")
                elif update.type == UpdateType.POOL_END:
                    print(f"\\n\\nPool complete!")
        """
        from peargent._core.streaming import StreamUpdate, UpdateType
        import time

        # Yield pool start event
        yield StreamUpdate(
            type=UpdateType.POOL_START,
            metadata={"input": user_input, "max_iter": self.max_iter}
        )

        pool_start_time = time.time()
        total_tokens = 0
        total_cost = 0.0

        self.state.add_message(role="user", content=user_input, agent=None)

        last_result = None
        call_count = 0
        current_input = user_input

        while call_count < self.max_iter:

            if hasattr(self.router, "decide"):
                route_name = self.router.decide(self.state, last_result=last_result)
                route = RouterResult(route_name)
            else:
                route = self.router(self.state, call_count=call_count, last_result=last_result)

            if not route or route.next_agent_name is None:
                break

            agent = self.agents_dict.get(route.next_agent_name)
            if not agent:
                raise ValueError(f"Router selected unknown agent '{route.next_agent_name}'")

            # Stream this agent with stream_observe() if available
            if hasattr(agent, 'stream_observe'):
                full_output = ""
                agent_tokens = 0
                agent_cost = 0.0

                for update in agent.stream_observe(current_input):
                    # Forward the update
                    yield update

                    # Collect metadata
                    if update.is_token and update.content:
                        full_output += update.content
                    elif update.is_agent_end:
                        agent_tokens = update.tokens or 0
                        agent_cost = update.cost or 0.0
                        total_tokens += agent_tokens
                        total_cost += agent_cost

                output = full_output
            else:
                # Fallback to run() if stream_observe() not available
                yield StreamUpdate(
                    type=UpdateType.AGENT_START,
                    agent=agent.name,
                    metadata={"input": current_input}
                )

                output = agent.run(current_input)

                yield StreamUpdate(
                    type=UpdateType.TOKEN,
                    content=output,
                    agent=agent.name
                )

                yield StreamUpdate(
                    type=UpdateType.AGENT_END,
                    agent=agent.name,
                    metadata={
                        "tokens": 0,
                        "cost": 0.0,
                        "output": output
                    }
                )

            # Store agent output in shared state
            self.state.add_message("assistant", str(output), agent=agent.name)
            last_result = {
                "agent": agent.name,
                "output": output,
                "tools_used": [m['content']['name'] for m in agent.temporary_memory if m.get('role') == 'tool'] if hasattr(agent, 'temporary_memory') else []
            }

            # Set the output as input for the next agent
            current_input = str(output)
            call_count += 1

        # Yield pool end event
        yield StreamUpdate(
            type=UpdateType.POOL_END,
            metadata={
                "duration": time.time() - pool_start_time,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "agents_executed": call_count
            }
        )

    async def astream(self, user_input: str):
        """
        Async version of stream() - Stream pool execution asynchronously.

        Args:
            user_input: The initial user request

        Yields:
            String chunks from the final agent's response

        Example:
            async for chunk in pool.astream("Explain AI"):
                print(chunk, end="", flush=True)
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import queue

        chunk_queue = queue.Queue()

        def run_stream_in_thread():
            try:
                for chunk in self.stream(user_input):
                    chunk_queue.put(('chunk', chunk))
                chunk_queue.put(('done', None))
            except Exception as e:
                chunk_queue.put(('error', e))

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(run_stream_in_thread)

        try:
            while True:
                try:
                    msg_type, data = await asyncio.get_event_loop().run_in_executor(
                        None, chunk_queue.get, True, 0.01
                    )
                    if msg_type == 'chunk':
                        yield data
                    elif msg_type == 'done':
                        break
                    elif msg_type == 'error':
                        raise data
                except queue.Empty:
                    await asyncio.sleep(0)
                    continue
        finally:
            executor.shutdown(wait=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert pool to serializable dictionary with complete details."""
        from peargent.atlas.serializer import (
            get_source_code,
            serialize_model_info,
            serialize_history_config
        )
        
        # Serialize router based on type
        router_info = {"type": "custom", "name": "Unknown Router"}
        
        if hasattr(self.router, "decide"):
            # It's a RoutingAgent - use its to_dict if available
            if hasattr(self.router, "to_dict"):
                router_info = self.router.to_dict()
            else:
                router_info = {
                    "type": "routing_agent",
                    "name": getattr(self.router, "name", "RoutingAgent"),
                    "persona": getattr(self.router, "persona", ""),
                    "agents": getattr(self.router, "agents", [])
                }
        elif callable(self.router):
            # Function-based router
            router_info = {
                "type": "function",
                "name": getattr(self.router, "__name__", "anonymous"),
                "source_code": get_source_code(self.router)
            }

        return {
            "type": "pool",
            "agents": [agent.to_dict() for agent in self.agents_dict.values()],
            "router": router_info,
            "max_iter": self.max_iter,
            "agent_names": self.agents_names,
            "default_model": serialize_model_info(self.default_model),
            "history": serialize_history_config(self.history),
            "tracing": self.tracing
        }

    async def astream_observe(self, user_input: str):
        """
        Async version of stream_observe() - Stream pool execution asynchronously with metadata.

        Args:
            user_input: The initial user request

        Yields:
            StreamUpdate objects with execution details

        Example:
            async for update in pool.astream_observe("Explain AI"):
                if update.is_agent_start:
                    print(f"[{update.agent}] Starting...")
                elif update.is_token:
                    print(update.content, end="", flush=True)
                elif update.is_agent_end:
                    print(f"[{update.agent}] Done! {update.tokens} tokens")
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import queue

        update_queue = queue.Queue()

        def run_observe_in_thread():
            try:
                for update in self.stream_observe(user_input):
                    update_queue.put(('update', update))
                update_queue.put(('done', None))
            except Exception as e:
                update_queue.put(('error', e))

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(run_observe_in_thread)

        try:
            while True:
                try:
                    msg_type, data = await asyncio.get_event_loop().run_in_executor(
                        None, update_queue.get, True, 0.01
                    )
                    if msg_type == 'update':
                        yield data
                    elif msg_type == 'done':
                        break
                    elif msg_type == 'error':
                        raise data
                except queue.Empty:
                    await asyncio.sleep(0)
                    continue
        finally:
            executor.shutdown(wait=False)