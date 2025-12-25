"""
Tests for the Pool class and create_pool functionality.
Tests pool creation, agent orchestration, routing, and state management.
"""

from typing import Any, Dict

import pytest

from peargent import create_agent, create_pool, create_tool
from peargent._core.router import RouterResult
from peargent._core.state import State


class MockModel:
    """Mock LLM model for testing without API keys."""

    def __init__(self, model_name: str = "mock-model", **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs

    def generate(self, prompt: str, **kwargs) -> str:
        return f"Response from {self.model_name}"


class TestPoolCreation:
    """Test pool creation and initialization."""

    def test_create_pool_with_multiple_agents(self) -> None:
        """Test creating a pool with multiple agents."""
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are helpful",
            model=MockModel(),
        )

        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are helpful",
            model=MockModel(),
        )

        pool = create_pool(agents=[agent1, agent2])

        assert len(pool.agents_dict) == 2
        assert "agent1" in pool.agents_dict
        assert "agent2" in pool.agents_dict

    def test_pool_with_default_model(self) -> None:
        """Test pool assigns default model to agents without one."""
        default_model = MockModel("default-model")
        
        agent1 = create_agent(
            name="agent1",
            description="Agent without model",
            persona="You are helpful",
            model=None,
        )

        pool = create_pool(agents=[agent1], default_model=default_model)

        assert pool.agents_dict["agent1"].model is not None
        assert pool.agents_dict["agent1"].model.model_name == "default-model"


class TestPoolConfiguration:
    """Test pool configuration options."""

    def test_pool_respects_max_iterations(self) -> None:
        """Test that pool respects max_iter configuration."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )

        pool = create_pool(agents=[agent1], max_iter=10)

        assert pool.max_iter == 10

    def test_pool_with_tracing_enabled(self) -> None:
        """Test pool with tracing enabled."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )

        agent2 = create_agent(
            name="agent2",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )

        pool = create_pool(agents=[agent1, agent2], tracing=True)

        assert pool.tracing is True


class TestPoolRouter:
    """Test pool routing functionality."""

    def test_pool_with_custom_router_function(self) -> None:
        """Test pool with custom router function."""
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are helpful",
            model=MockModel(),
        )

        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are helpful",
            model=MockModel(),
        )

        def custom_router(state, call_count, last_result):
            """Simple router that alternates between agents."""
            if call_count == 0:
                return RouterResult("agent1")
            return RouterResult(None)

        pool = create_pool(
            agents=[agent1, agent2],
            router=custom_router,
            max_iter=3,
        )

        assert pool.router is not None
        assert callable(pool.router)


class TestPoolState:
    """Test pool shared state management."""

    def test_pool_with_shared_state(self) -> None:
        """Test pool with shared state across agents."""
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are helpful",
            model=MockModel(),
        )

        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are helpful",
            model=MockModel(),
        )

        custom_state = State()
        pool = create_pool(
            agents=[agent1, agent2],
            default_state=custom_state,
        )

        assert pool.state is not None
        assert pool.state == custom_state

    def test_pool_creates_state_automatically(self) -> None:
        """Test that pool creates state automatically if not provided."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )

        pool = create_pool(agents=[agent1])

        assert pool.state is not None
        assert isinstance(pool.state, State)


class TestPoolExecution:
    """Test pool execution and run method."""

    def test_pool_run_executes_single_agent(self) -> None:
        """Test running pool with a single agent."""
        call_count = []
        
        class TrackingMockModel:
            def generate(self, prompt: str, **kwargs) -> str:
                call_count.append(1)
                return "Agent response"
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=TrackingMockModel(),
        )
        
        def single_agent_router(state, call_count_param, last_result):
            """Router that runs agent once then stops."""
            if call_count_param == 0:
                return RouterResult("agent1")
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1],
            router=single_agent_router,
            max_iter=5,
        )
        
        result = pool.run("Test input")
        
        assert len(call_count) > 0
        assert result is not None
        assert len(pool.state.history) > 0

    def test_pool_run_chains_multiple_agents(self) -> None:
        """Test that pool chains output from one agent to next."""
        execution_order = []
        
        class OrderTrackingModel:
            def __init__(self, agent_name: str):
                self.agent_name = agent_name
            
            def generate(self, prompt: str, **kwargs) -> str:
                execution_order.append(self.agent_name)
                return f"Response from {self.agent_name}"
        
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are first",
            model=OrderTrackingModel("agent1"),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are second",
            model=OrderTrackingModel("agent2"),
        )
        
        def sequential_router(state, call_count, last_result):
            """Router that runs agents sequentially."""
            if call_count == 0:
                return RouterResult("agent1")
            elif call_count == 1:
                return RouterResult("agent2")
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1, agent2],
            router=sequential_router,
            max_iter=5,
        )
        
        result = pool.run("Initial input")
        
        assert len(execution_order) == 2
        assert execution_order[0] == "agent1"
        assert execution_order[1] == "agent2"
        assert "agent2" in result

    def test_pool_run_stops_at_max_iterations(self) -> None:
        """Test that pool respects max_iter limit."""
        call_count_tracker = []
        
        class CountingModel:
            def generate(self, prompt: str, **kwargs) -> str:
                call_count_tracker.append(1)
                return "Response"
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=CountingModel(),
        )
        
        def infinite_router(state, call_count, last_result):
            """Router that always returns agent1 (would run infinitely)."""
            return RouterResult("agent1")
        
        pool = create_pool(
            agents=[agent1],
            router=infinite_router,
            max_iter=3,
        )
        
        result = pool.run("Test input")
        
        # Should stop after max_iter (3) iterations
        assert len(call_count_tracker) == 3

    def test_pool_run_with_empty_input(self) -> None:
        """Test pool handles empty string input."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1], max_iter=1)
        
        result = pool.run("")
        
        assert result is not None
        # Verify empty input was added to history
        assert any(m["role"] == "user" and m["content"] == "" for m in pool.state.history)

    def test_pool_run_updates_state_history(self) -> None:
        """Test that pool run properly updates state history."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1], max_iter=2)
        
        initial_history_length = len(pool.state.history)
        pool.run("Test message")
        
        # Should have at least user message and assistant response
        assert len(pool.state.history) > initial_history_length
        assert any(m["role"] == "user" for m in pool.state.history)
        assert any(m["role"] == "assistant" for m in pool.state.history)


class TestPoolErrorHandling:
    """Test pool error handling and edge cases."""

    def test_pool_raises_error_for_unknown_agent(self) -> None:
        """Test that pool raises error when router selects unknown agent."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        def bad_router(state, call_count, last_result):
            """Router that returns non-existent agent name."""
            return RouterResult("nonexistent_agent")
        
        pool = create_pool(
            agents=[agent1],
            router=bad_router,
            max_iter=5,
        )
        
        with pytest.raises(ValueError, match="unknown agent"):
            pool.run("Test input")

    def test_pool_with_empty_agent_list(self) -> None:
        """Test creating pool with no agents."""
        pool = create_pool(agents=[], max_iter=5)
        
        assert len(pool.agents_dict) == 0
        assert len(pool.agents_names) == 0

    def test_pool_handles_router_returning_none(self) -> None:
        """Test pool stops when router returns None."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        def immediate_stop_router(state, call_count, last_result):
            """Router that immediately returns None."""
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1],
            router=immediate_stop_router,
            max_iter=5,
        )
        
        result = pool.run("Test input")
        
        # Should stop immediately, only user message added
        assert any(m["role"] == "user" for m in pool.state.history)

    def test_pool_with_duplicate_agent_names(self) -> None:
        """Test that pool handles agents with duplicate names (last one wins)."""
        agent1 = create_agent(
            name="duplicate",
            description="First agent",
            persona="You are first",
            model=MockModel("model1"),
        )
        
        agent2 = create_agent(
            name="duplicate",
            description="Second agent",
            persona="You are second",
            model=MockModel("model2"),
        )
        
        pool = create_pool(agents=[agent1, agent2])
        
        # Last agent with duplicate name should win
        assert len(pool.agents_dict) == 1
        assert pool.agents_dict["duplicate"].model.model_name == "model2"


class TestPoolRouterBehavior:
    """Test various router behaviors and scenarios."""

    def test_pool_with_function_router_receives_correct_params(self) -> None:
        """Test that function-based router receives correct parameters."""
        router_calls = []
        
        def tracking_router(state, call_count, last_result):
            """Router that tracks its calls."""
            router_calls.append({
                "state": state,
                "call_count": call_count,
                "last_result": last_result,
            })
            if call_count == 0:
                return RouterResult("agent1")
            return RouterResult(None)
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            router=tracking_router,
            max_iter=5,
        )
        
        pool.run("Test input")
        
        assert len(router_calls) >= 1
        assert router_calls[0]["call_count"] == 0
        assert router_calls[0]["last_result"] is None
        if len(router_calls) > 1:
            assert router_calls[1]["last_result"] is not None

    def test_pool_router_receives_last_result_with_agent_info(self) -> None:
        """Test that router receives last_result with agent execution info."""
        last_results = []
        
        def result_tracking_router(state, call_count, last_result):
            """Router that tracks last_result."""
            if last_result:
                last_results.append(last_result)
            if call_count < 2:
                return RouterResult("agent1")
            return RouterResult(None)
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            router=result_tracking_router,
            max_iter=5,
        )
        
        pool.run("Test input")
        
        assert len(last_results) >= 1
        assert "agent" in last_results[0]
        assert "output" in last_results[0]
        assert last_results[0]["agent"] == "agent1"

    def test_pool_with_routing_agent_class(self) -> None:
        """Test pool with RoutingAgent-based router."""
        from peargent._core.router import RoutingAgent
        
        class MockRoutingAgent:
            """Mock RoutingAgent for testing."""
            def __init__(self):
                self.decide_calls = []
            
            def decide(self, state, last_result=None):
                self.decide_calls.append((state, last_result))
                if len(self.decide_calls) == 1:
                    return "agent1"
                return None
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        router = MockRoutingAgent()
        pool = create_pool(
            agents=[agent1],
            router=router,
            max_iter=5,
        )
        
        pool.run("Test input")
        
        assert len(router.decide_calls) >= 1


class TestPoolStateManagement:
    """Test pool state management across multiple runs."""

    def test_pool_state_persists_across_runs(self) -> None:
        """Test that state accumulates across multiple run calls."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1], max_iter=2)
        
        pool.run("First input")
        history_after_first = len(pool.state.history)
        
        pool.run("Second input")
        history_after_second = len(pool.state.history)
        
        # History should accumulate
        assert history_after_second > history_after_first

    def test_pool_state_kv_store_accessible(self) -> None:
        """Test that state key-value store is accessible and modifiable."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        
        # Test setting and getting values
        pool.state.set("test_key", "test_value")
        assert pool.state.get("test_key") == "test_value"
        
        pool.state.set("counter", 42)
        assert pool.state.get("counter") == 42

    def test_pool_state_agents_dict_available(self) -> None:
        """Test that state has access to agents dictionary."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1, agent2])
        
        assert pool.state.agents is not None
        assert "agent1" in pool.state.agents
        assert "agent2" in pool.state.agents


class TestPoolWithHistory:
    """Test pool integration with conversation history."""

    def test_pool_with_history_config(self) -> None:
        """Test pool with HistoryConfig."""
        from peargent._config import HistoryConfig
        from peargent.storage import InMemory
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        history_config = HistoryConfig(
            auto_manage_context=True,
            max_context_messages=10,
            strategy="smart",
            store=InMemory(),
        )
        
        pool = create_pool(
            agents=[agent1],
            history=history_config,
            max_iter=2,
        )
        
        assert pool.history is not None

    def test_pool_state_syncs_with_history_manager(self) -> None:
        """Test that state messages sync with history manager."""
        from peargent.history import InMemoryHistoryStore, ConversationHistory
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        history_store = InMemoryHistoryStore()
        history_manager = ConversationHistory(store=history_store)
        
        pool = create_pool(
            agents=[agent1],
            history=history_manager,
            max_iter=2,
        )
        
        pool.run("Test message")
        
        # Verify history was synced
        assert pool.state.history_manager is not None


class TestPoolTracingBehavior:
    """Test pool tracing configuration and behavior."""

    def test_pool_tracing_enables_for_all_agents(self) -> None:
        """Test that pool tracing=True enables tracing for agents without explicit setting."""
        agent1 = create_agent(
            name="agent1",
            description="Agent without explicit tracing",
            persona="You are helpful",
            model=MockModel(),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Another agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1, agent2],
            tracing=True,
        )
        
        # Both agents should have tracing enabled
        assert pool.agents_dict["agent1"].tracing is True
        assert pool.agents_dict["agent2"].tracing is True

    def test_pool_tracing_respects_explicit_agent_settings(self) -> None:
        """Test that pool tracing doesn't override explicit agent tracing=False."""
        # Agent with explicit tracing=False
        agent1 = create_agent(
            name="agent1",
            description="Agent with explicit tracing off",
            persona="You are helpful",
            model=MockModel(),
            tracing=False,
        )
        agent1._tracing_explicitly_set = True
        
        # Agent without explicit setting
        agent2 = create_agent(
            name="agent2",
            description="Agent without explicit setting",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1, agent2],
            tracing=True,
        )
        
        # Agent1 should keep tracing=False (explicit)
        assert pool.agents_dict["agent1"].tracing is False
        # Agent2 should get tracing=True from pool
        assert pool.agents_dict["agent2"].tracing is True


class TestPoolDefaultModel:
    """Test pool default model assignment."""

    def test_pool_assigns_default_model_to_agents(self) -> None:
        """Test that pool assigns default model to agents without one."""
        default_model = MockModel("default")
        
        agent1 = create_agent(
            name="agent1",
            description="Agent without model",
            persona="You are helpful",
            model=None,
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Agent with model",
            persona="You are helpful",
            model=MockModel("specific"),
        )
        
        pool = create_pool(
            agents=[agent1, agent2],
            default_model=default_model,
        )
        
        # Agent1 should get default model
        assert pool.agents_dict["agent1"].model is not None
        assert pool.agents_dict["agent1"].model.model_name == "default"
        
        # Agent2 should keep its own model
        assert pool.agents_dict["agent2"].model.model_name == "specific"

    def test_pool_agents_without_model_stay_none_if_no_default(self) -> None:
        """Test that agents without model remain None if no default provided."""
        agent1 = create_agent(
            name="agent1",
            description="Agent without model",
            persona="You are helpful",
            model=None,
        )
        
        pool = create_pool(
            agents=[agent1],
            default_model=None,
        )
        
        # Agent should still have None model
        assert pool.agents_dict["agent1"].model is None


class TestPoolEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pool_with_max_iter_zero(self) -> None:
        """Test pool with max_iter=0."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            max_iter=0,
        )
        
        result = pool.run("Test input")
        
        # Should not execute any agents, only add user message
        user_messages = [m for m in pool.state.history if m["role"] == "user"]
        assistant_messages = [m for m in pool.state.history if m["role"] == "assistant"]
        
        assert len(user_messages) == 1
        assert len(assistant_messages) == 0

    def test_pool_with_max_iter_one(self) -> None:
        """Test pool executes exactly once with max_iter=1."""
        call_count = []
        
        class TrackingModel:
            def generate(self, prompt: str, **kwargs) -> str:
                call_count.append(1)
                return "Response"
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=TrackingModel(),
        )
        
        def always_route_router(state, count, last_result):
            return RouterResult("agent1")
        
        pool = create_pool(
            agents=[agent1],
            router=always_route_router,
            max_iter=1,
        )
        
        pool.run("Test input")
        
        # Should execute exactly once
        assert len(call_count) == 1

    def test_pool_returns_empty_string_if_no_assistant_messages(self) -> None:
        """Test pool returns empty string if router stops before any agent runs."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        def immediate_stop_router(state, call_count, last_result):
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1],
            router=immediate_stop_router,
        )
        
        result = pool.run("Test input")
        
        assert result == ""

    def test_pool_with_very_large_max_iter(self) -> None:
        """Test pool with very large max_iter stops when router returns None."""
        call_count = []
        
        class CountingModel:
            def generate(self, prompt: str, **kwargs) -> str:
                call_count.append(1)
                return "Response"
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=CountingModel(),
        )
        
        def limited_router(state, count, last_result):
            if count < 3:
                return RouterResult("agent1")
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1],
            router=limited_router,
            max_iter=1000,
        )
        
        pool.run("Test input")
        
        # Should only run 3 times despite max_iter=1000
        assert len(call_count) == 3


class TestPoolAgentNames:
    """Test pool agent name handling."""

    def test_pool_agents_names_list_correct(self) -> None:
        """Test that pool.agents_names contains all agent names."""
        agent1 = create_agent(
            name="first",
            description="First agent",
            persona="You are first",
            model=MockModel(),
        )
        
        agent2 = create_agent(
            name="second",
            description="Second agent",
            persona="You are second",
            model=MockModel(),
        )
        
        agent3 = create_agent(
            name="third",
            description="Third agent",
            persona="You are third",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1, agent2, agent3])
        
        assert len(pool.agents_names) == 3
        assert "first" in pool.agents_names
        assert "second" in pool.agents_names
        assert "third" in pool.agents_names

    def test_pool_agents_dict_maps_names_correctly(self) -> None:
        """Test that agents_dict correctly maps names to agent objects."""
        agent1 = create_agent(
            name="test-agent",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        
        assert "test-agent" in pool.agents_dict
        assert pool.agents_dict["test-agent"] == agent1
        assert pool.agents_dict["test-agent"].name == "test-agent"


class TestPoolStreamingMethods:
    """Test pool streaming capabilities."""

    def test_pool_has_stream_method(self) -> None:
        """Test that pool has stream method."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        
        assert hasattr(pool, "stream")
        assert callable(pool.stream)

    def test_pool_has_stream_observe_method(self) -> None:
        """Test that pool has stream_observe method."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        
        assert hasattr(pool, "stream_observe")
        assert callable(pool.stream_observe)

    def test_pool_has_async_stream_methods(self) -> None:
        """Test that pool has async streaming methods."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        
        assert hasattr(pool, "astream")
        assert callable(pool.astream)
        assert hasattr(pool, "astream_observe")
        assert callable(pool.astream_observe)


class TestPoolStateInitialization:
    """Test various state initialization scenarios."""

    def test_pool_with_default_state_preserves_history_manager(self) -> None:
        """Test that providing default_state with history_manager works correctly."""
        from peargent.history import InMemoryHistoryStore, ConversationHistory
        
        history_manager = ConversationHistory(store=InMemoryHistoryStore())
        custom_state = State(history_manager=history_manager)
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            default_state=custom_state,
        )
        
        assert pool.state.history_manager is not None
        assert pool.state.history_manager == history_manager

    def test_pool_with_default_state_and_separate_history(self) -> None:
        """Test pool with both default_state and separate history param."""
        from peargent.history import InMemoryHistoryStore, ConversationHistory
        
        custom_state = State()
        new_history = ConversationHistory(store=InMemoryHistoryStore())
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            default_state=custom_state,
            history=new_history,
        )
        
        # History param should override state's history manager
        assert pool.state.history_manager == new_history

    def test_pool_state_receives_agents_dict(self) -> None:
        """Test that state is initialized with agents dictionary."""
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1, agent2])
        
        assert pool.state.agents is not None
        assert len(pool.state.agents) == 2
        assert "agent1" in pool.state.agents
        assert "agent2" in pool.state.agents


class TestPoolRouterIntegration:
    """Test pool integration with different router types."""

    def test_pool_sets_agent_objects_on_routing_agent(self) -> None:
        """Test that pool sets agent_objects attribute on RoutingAgent."""
        class MockRoutingAgentWithObjects:
            """Mock RoutingAgent that has agent_objects attribute."""
            def __init__(self):
                self.agent_objects = None
            
            def decide(self, state, last_result=None):
                return None
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        router = MockRoutingAgentWithObjects()
        pool = create_pool(
            agents=[agent1],
            router=router,
        )
        
        # Pool should set agent_objects on the router
        assert router.agent_objects is not None
        assert "agent1" in router.agent_objects

    def test_pool_default_router_stops_immediately(self) -> None:
        """Test that default router (when none provided) stops immediately."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        # Create pool without router (uses default)
        pool = create_pool(agents=[agent1])
        
        # Default router should return RouterResult(None)
        result = pool.router(pool.state, 0, None)
        assert result.next_agent_name is None

    def test_pool_with_round_robin_router(self) -> None:
        """Test pool with round_robin_router from peargent."""
        from peargent._core.router import round_robin_router
        
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are first",
            model=MockModel(),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are second",
            model=MockModel(),
        )
        
        router = round_robin_router(["agent1", "agent2"])
        pool = create_pool(
            agents=[agent1, agent2],
            router=router,
        )
        
        assert pool.router is not None
        # First call should route to agent1
        result = pool.router(pool.state, 0, None)
        assert result.next_agent_name == "agent1"


class TestPoolMessageFormatting:
    """Test message formatting and storage in pool."""

    def test_pool_adds_agent_name_to_assistant_messages(self) -> None:
        """Test that assistant messages include agent name."""
        agent1 = create_agent(
            name="test-agent",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        def single_run_router(state, call_count, last_result):
            if call_count == 0:
                return RouterResult("test-agent")
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1],
            router=single_run_router,
        )
        
        pool.run("Test message")
        
        # Find assistant messages
        assistant_messages = [m for m in pool.state.history if m["role"] == "assistant"]
        assert len(assistant_messages) > 0
        assert assistant_messages[0].get("agent") == "test-agent"

    def test_pool_user_messages_have_no_agent(self) -> None:
        """Test that user messages don't have agent attribution."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(agents=[agent1])
        pool.run("Test message")
        
        user_messages = [m for m in pool.state.history if m["role"] == "user"]
        assert len(user_messages) > 0
        assert user_messages[0].get("agent") is None


class TestPoolLastResultFormat:
    """Test the format of last_result passed to router."""

    def test_last_result_contains_required_fields(self) -> None:
        """Test that last_result has agent, output, and tools_used fields."""
        captured_last_result = []
        
        def capturing_router(state, call_count, last_result):
            if last_result:
                captured_last_result.append(last_result)
            if call_count < 2:
                return RouterResult("agent1")
            return RouterResult(None)
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            router=capturing_router,
        )
        
        pool.run("Test input")
        
        assert len(captured_last_result) > 0
        last_res = captured_last_result[0]
        assert "agent" in last_res
        assert "output" in last_res
        assert "tools_used" in last_res

    def test_last_result_tools_used_is_list(self) -> None:
        """Test that tools_used in last_result is a list."""
        captured_last_result = []
        
        def capturing_router(state, call_count, last_result):
            if last_result:
                captured_last_result.append(last_result)
            if call_count < 1:
                return RouterResult("agent1")
            return RouterResult(None)
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool = create_pool(
            agents=[agent1],
            router=capturing_router,
        )
        
        pool.run("Test input")
        
        if captured_last_result:
            assert isinstance(captured_last_result[0]["tools_used"], list)


class TestPoolInputChaining:
    """Test that agent inputs are properly chained."""

    def test_second_agent_receives_first_agent_output(self) -> None:
        """Test that output from first agent becomes input to second."""
        agent_inputs = []
        
        class InputTrackingModel:
            def __init__(self, name: str):
                self.name = name
            
            def generate(self, prompt: str, **kwargs) -> str:
                # Extract the actual input from the prompt
                agent_inputs.append({
                    "agent": self.name,
                    "prompt_preview": prompt[:100] if len(prompt) > 100 else prompt
                })
                return f"Output from {self.name}"
        
        agent1 = create_agent(
            name="agent1",
            description="First agent",
            persona="You are first",
            model=InputTrackingModel("agent1"),
        )
        
        agent2 = create_agent(
            name="agent2",
            description="Second agent",
            persona="You are second",
            model=InputTrackingModel("agent2"),
        )
        
        def sequential_router(state, call_count, last_result):
            if call_count == 0:
                return RouterResult("agent1")
            elif call_count == 1:
                return RouterResult("agent2")
            return RouterResult(None)
        
        pool = create_pool(
            agents=[agent1, agent2],
            router=sequential_router,
        )
        
        pool.run("Initial input")
        
        # Both agents should have been called
        assert len(agent_inputs) == 2
        assert agent_inputs[0]["agent"] == "agent1"
        assert agent_inputs[1]["agent"] == "agent2"


class TestPoolConfigurationValidation:
    """Test pool configuration and parameter validation."""

    def test_pool_stores_max_iter(self) -> None:
        """Test that pool stores max_iter configuration."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        for max_iter_value in [1, 5, 10, 100]:
            pool = create_pool(agents=[agent1], max_iter=max_iter_value)
            assert pool.max_iter == max_iter_value

    def test_pool_stores_tracing_flag(self) -> None:
        """Test that pool stores tracing configuration."""
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        pool_with_tracing = create_pool(agents=[agent1], tracing=True)
        assert pool_with_tracing.tracing is True
        
        pool_without_tracing = create_pool(agents=[agent1], tracing=False)
        assert pool_without_tracing.tracing is False

    def test_pool_stores_history_reference(self) -> None:
        """Test that pool stores history reference."""
        from peargent.history import InMemoryHistoryStore, ConversationHistory
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=MockModel(),
        )
        
        history = ConversationHistory(store=InMemoryHistoryStore())
        pool = create_pool(agents=[agent1], history=history)
        
        assert pool.history == history

    def test_pool_stores_default_model_reference(self) -> None:
        """Test that pool stores default_model reference."""
        default_model = MockModel("default-model")
        
        agent1 = create_agent(
            name="agent1",
            description="Test agent",
            persona="You are helpful",
            model=None,
        )
        
        pool = create_pool(agents=[agent1], default_model=default_model)
        
        assert pool.default_model == default_model
