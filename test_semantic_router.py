from peargent.models import gemini
from peargent import create_agent, create_semantic_router, create_routing_agent, create_pool
from peargent._core.state import State
import time

# Create model using factory function
model = gemini("gemini-2.5-flash-lite")

# Create agents
math_agent = create_agent(
    name="MathAgent",
    description="I am an expert in mathematics and calculation.",
    persona="You solve math problems.",
    model=model
)

writing_agent = create_agent(
    name="WriterAgent",
    description="I am a creative writer and poet.",
    persona="You write poems and stories.",
    model=model
)

agents = [math_agent, writing_agent]

# Create both routers
print("=" * 60)
print("POOL BENCHMARK: Semantic Router vs Routing Agent")
print("=" * 60)

print("\n1. Creating Semantic Router...")
start = time.time()
semantic_router = create_semantic_router(
    name="SemanticRouter",
    model=model,
    agents=agents
)
semantic_init_time = time.time() - start
print(f"   Init time: {semantic_init_time:.3f}s (pre-computes embeddings)")

print("\n2. Creating Routing Agent...")
start = time.time()
routing_agent = create_routing_agent(
    name="RoutingAgent",
    model=model,
    persona="You are a router that selects the best agent for a query.",
    agents=agents
)
routing_init_time = time.time() - start
print(f"   Init time: {routing_init_time:.3f}s")

# Create pools with each router
print("\n3. Creating Pools...")
pool_semantic = create_pool(agents=agents, router=semantic_router, max_iter=1)
pool_routing = create_pool(agents=agents, router=routing_agent, max_iter=1)
print("   Created 2 pools with different routers")

# Test queries
queries = [
    "What is the square root of 144?",
    "Write a poem about the sea.",
]

print("\n" + "=" * 60)
print("POOL EXECUTION COMPARISON")
print("=" * 60)

for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 50)
    
    # Pool with Semantic Router
    start = time.time()
    result_semantic = pool_semantic.run(query)
    semantic_time = time.time() - start
    
    # Pool with Routing Agent
    start = time.time()
    result_routing = pool_routing.run(query)
    routing_time = time.time() - start
    
    print(f"  Semantic Router Pool: {semantic_time*1000:.0f}ms")
    print(f"  Routing Agent Pool:   {routing_time*1000:.0f}ms")
    
    if semantic_time > 0:
        speedup = routing_time / semantic_time
        print(f"  Routing speedup: {speedup:.2f}x")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("Semantic Router: embedding similarity (fast routing, API call at init)")
print("Routing Agent:   LLM inference per routing decision (slower but flexible)")
