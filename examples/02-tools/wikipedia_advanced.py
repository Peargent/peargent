"""
Advanced Wikipedia Knowledge Tool Example

Demonstrates advanced features including:
- Handling disambiguation pages
- Multi-language support
- Summary length control
- Integration with agents for research tasks
"""

from peargent import create_agent
from peargent.tools import wikipedia_tool
from peargent.models import gemini




def main():
    print("=" * 60)
    print("Wikipedia Knowledge Tool - Advanced Example")
    print("=" * 60)
    
    # Example 1: Handling disambiguation pages
    print("\n1. Handling disambiguation page (Mercury):")
    print("-" * 60)
    
    result = wikipedia_tool.run({"query": "Mercury"})
    
    if 'disambiguation' in result.get('metadata', {}):
        print(f"'{result['metadata']['title']}' is a disambiguation page.")
        print(f"Disambiguation options (first 10):")
        for i, option in enumerate(result['metadata']['disambiguation'][:10], 1):
            print(f"  {i}. {option}")
        
        # Now search for a specific option
        print("\n\nSearching for specific option 'Mercury (planet)':")
        result = wikipedia_tool.run({"query": "Mercury (planet)"})
        if result["success"] and result["text"]:
            print(f"Title: {result['metadata']['title']}")
            print(f"Summary: {result['text'][:200]}...")
    
    # Example 2: Multi-language support
    print("\n\n2. Multi-language support (searching in French):")
    print("-" * 60)
    
    result = wikipedia_tool.run({
        "query": "Tour Eiffel",
        "language": "fr"
    })
    
    if result["success"] and result["text"]:
        print(f"Title: {result['metadata']['title']}")
        print(f"URL: {result['metadata']['url']}")
        print(f"Summary (first 200 chars): {result['text'][:200]}...")
    
    # Example 3: Summary length control
    print("\n\n3. Controlling summary length:")
    print("-" * 60)
    
    result = wikipedia_tool.run({
        "query": "Machine Learning",
        "max_summary_length": 200
    })
    
    if result["success"] and result["text"]:
        print(f"Title: {result['metadata']['title']}")
        print(f"Summary (max 200 chars):\n{result['text']}")
    
    # Example 4: Research agent with follow-up questions
    print("\n\n4. Research agent with Wikipedia tool:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="WikipediaExpertAgent",
            description="An expert Wikipedia research assistant",
            persona=(
                "You are an expert research assistant. Use Wikipedia to find accurate "
                "information about topics. When you find information, cite the Wikipedia "
                "article by including the article title and URL. If a term has multiple "
                "meanings (disambiguation), ask the user to clarify which one they mean."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[wikipedia_tool]
        )
        
        # Research task
        response = agent.run(
            "I want to learn about quantum computing. Please provide a brief "
            "overview and tell me about any key pioneers in this field."
        )
        print(f"\nAgent Response:\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect Wikipedia lookup works without API key:")
        result = wikipedia_tool.run({"query": "Quantum computing"})
        if result["success"] and result["text"]:
            print(f"Title: {result['metadata']['title']}")
            print(f"Summary: {result['text'][:300]}...")
    
    # Example 5: Comparing related topics
    print("\n\n5. Comparing related topics:")
    print("-" * 60)
    
    topics = ["Artificial Intelligence", "Machine Learning", "Deep Learning"]
    
    for topic in topics:
        result = wikipedia_tool.run({
            "query": topic,
            "max_summary_length": 150,
            "extract_categories": True
        })
        
        if result["success"] and result["text"]:
            print(f"\n{result['metadata']['title']}:")
            print(f"Summary: {result['text']}")
            if 'categories' in result['metadata']:
                print(f"Categories: {', '.join(result['metadata']['categories'][:3])}")
    
    # Example 6: Fact-checking with agent
    print("\n\n6. Fact-checking with agent:")
    print("-" * 60)
    
    try:
        fact_checker = create_agent(
            name="FactCheckerAgent",
            description="A Wikipedia-powered fact checker",
            persona=(
                "You are a fact-checker. When given a statement, use Wikipedia to verify "
                "if it's accurate. Cite your sources and explain your findings clearly."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[wikipedia_tool]
        )
        
        statement = "The Great Wall of China was built in the 15th century."
        response = fact_checker.run(f"Verify this statement: {statement}")
        print(f"\nFact-check result:\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect Wikipedia lookup works without API key:")
        result = wikipedia_tool.run({"query": "Great Wall of China"})
        if result["success"] and result["text"]:
            print(f"Title: {result['metadata']['title']}")
            print(f"Summary: {result['text'][:300]}...")
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
