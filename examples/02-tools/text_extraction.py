"""
Basic Text Extraction Example

Demonstrates how to extract text from various document formats
using the TextExtractionTool.
"""

from peargent import create_agent
from peargent.tools import text_extractor
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Text Extraction Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Extract text from a local file
    print("\n1. Extracting text from local file:")
    print("-" * 60)
    
    # For demonstration, create a sample HTML file
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Document</title>
        <meta name="author" content="John Doe">
    </head>
    <body>
        <h1>Welcome to Text Extraction</h1>
        <p>This is a sample HTML document that demonstrates text extraction.</p>
        <p>The tool can extract plain text from various formats including HTML, PDF, and DOCX.</p>
    </body>
    </html>
    """
    
    # Save sample file
    with open("sample.html", "w") as f:
        f.write(sample_html)
    
    # Extract text
    result = text_extractor.run({"file_path": "sample.html"})
    
    if result["success"]:
        print(f"Format: {result['format']}")
        print(f"\nExtracted Text:\n{result['text'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Extract text with metadata
    print("\n\n2. Extracting text with metadata:")
    print("-" * 60)
    
    result = text_extractor.run({"file_path": "sample.html", "extract_metadata": True})
    
    if result["success"]:
        print(f"Format: {result['format']}")
        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        print(f"\nText Preview: {result['text'][:100]}...")
    
    # Example 3: Using with an agent
    print("\n\n3. Using text extraction with an agent:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="DocumentAnalyzer",
            description="Analyzes documents and summarizes their content",
            persona=(
                "You are a document analysis expert. When given a document, "
                "extract the text and provide a concise summary of its main points."
            ),
            model=gemini("gemini-2.0-flash-exp"),
            tools=[text_extractor]
        )
        
        # Ask the agent to analyze the document
        response = agent.run("Please extract and summarize the content from sample.html")
        print(f"\nAgent Response:\n{response}")
    except Exception as e:
        print(f"Note: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect extraction works without API key:")
        result = text_extractor.run({"file_path": "sample.html"})
        if result["success"]:
            print(f"Text: {result['text'][:150]}...")
    
    # Cleanup
    import os
    if os.path.exists("sample.html"):
        os.remove("sample.html")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
