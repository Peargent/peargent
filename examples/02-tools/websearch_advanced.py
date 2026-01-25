"""
Advanced Web Search Tool Example

Demonstrates advanced features of the WebSearchTool including:
- Regional search filtering
- Safe search settings
- Time-based filtering
- Integration with RAG workflows
- Multi-query research patterns
"""

from peargent import create_agent
from peargent.tools import websearch_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Web Search Tool - Advanced Example")
    print("=" * 60)
    
    # Example 1: Regional search
    print("\n1. Regional search (US English):")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "best restaurants near me",
        "max_results": 5,
        "region": "us-en"  # US English results
    })
    
    if result["success"] and result["results"]:
        print(f"Region: {result['metadata']['region']}")
        print(f"Found {len(result['results'])} results")
        for i, r in enumerate(result["results"][:3], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['url']}")
    
    # Example 2: Safe search settings
    print("\n\n2. Strict safe search:")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "educational content",
        "max_results": 3,
        "safesearch": "strict"  # Options: "strict", "moderate", "off"
    })
    
    if result["success"]:
        print(f"Safe search: {result['metadata']['safesearch']}")
        print(f"Found {len(result['results'])} results")
        for r in result["results"]:
            print(f"- {r['title']}")
    
    # Example 3: Time-based filtering
    print("\n\n3. Recent news (past day):")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "breaking news technology",
        "max_results": 5,
        "time_range": "d"  # d=day, w=week, m=month, y=year
    })
    
    if result["success"] and result["results"]:
        print("Recent articles:")
        for i, r in enumerate(result["results"], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['snippet'][:100]}...")
            print(f"   Source: {r['url']}")
    
    # Example 4: RAG-style information retrieval
    print("\n\n4. RAG-style research with multiple queries:")
    print("-" * 60)
    
    queries = [
        "artificial intelligence ethics",
        "AI bias and fairness",
        "responsible AI development"
    ]
    
    all_sources = []
    for query in queries:
        result = websearch_tool.run({
            "query": query,
            "max_results": 3
        })
        if result["success"]:
            all_sources.extend(result["results"])
    
    print(f"Gathered {len(all_sources)} sources across {len(queries)} queries")
    print("\nSample sources:")
    for i, source in enumerate(all_sources[:5], 1):
        print(f"{i}. {source['title']}")
        print(f"   {source['url']}")
    
    # Example 5: Advanced agent with web research capabilities
    print("\n\n5. Advanced research agent with web search:")
    print("-" * 60)
    
    try:
        research_agent = create_agent(
            name="DeepResearchAgent",
            description="An expert research assistant with web search capabilities",
            persona="""You are an expert research assistant with web search capabilities.
            
            When researching a topic:
            1. Break down complex questions into specific search queries
            2. Search for current, authoritative information
            3. Cross-reference multiple sources
            4. Synthesize findings into clear, comprehensive answers
            5. Always cite your sources with URLs
            
            Be thorough, accurate, and provide evidence-based responses.""",
            model=gemini("gemini-2.5-flash-lite"),
            tools=[websearch_tool]
        )
    
        # Complex research query
        query = "Compare the latest advancements in solar energy vs wind energy in 2026"
        print(f"\nResearch query: {query}")
        print("\nAgent researching...")
        
        response = research_agent.run(query)
        print(f"\nResearch findings:\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Set GEMINI_API_KEY in .env file.")
    
    # Example 6: Fact-checking agent
    print("\n\n6. Fact-checking with web search:")
    print("-" * 60)
    
    try:
        fact_checker = create_agent(
            name="FactChecker",
            description="A fact-checking assistant with web search",
            persona="""You are a fact-checking assistant. When given a claim:
            1. Search for authoritative sources
            2. Look for recent information
            3. Verify facts from multiple angles
            4. Provide a verdict: True, False, Partially True, or Unverified
            5. Always cite sources""",
            model=gemini("gemini-2.5-flash-lite"),
            tools=[websearch_tool]
        )
        
        claim = "Python is the most popular programming language in 2026"
        print(f"\nClaim to verify: {claim}")
        
        verification = fact_checker.run(f"Fact-check this claim: {claim}")
        print(f"\nVerification result:\n{verification}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Set GEMINI_API_KEY in .env file.")
    
    # Example 7: Multi-lingual search
    print("\n\n7. Multi-lingual search (German):")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "beste deutsche bücher",
        "max_results": 3,
        "region": "de-de"  # German results
    })
    
    if result["success"] and result["results"]:
        print("German search results:")
        for i, r in enumerate(result["results"], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['url']}")


if __name__ == "__main__":
    main()
