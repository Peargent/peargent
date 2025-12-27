"""
Advanced Text Extraction Example

Demonstrates advanced features including:
- Batch processing multiple files
- Metadata extraction
- Integration with agents for document analysis
- Different document formats
"""

import os
from pathlib import Path
from peargent import create_agent
from peargent.tools import text_extractor
from peargent.tools.text_extraction_tool import extract_text
from peargent.models import gemini


def create_sample_files():
    """Create sample files for demonstration."""
    # Sample HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI and Machine Learning</title>
        <meta name="author" content="Tech Research Team">
        <meta name="description" content="An overview of AI and ML technologies">
    </head>
    <body>
        <h1>Introduction to AI and Machine Learning</h1>
        <p>Artificial Intelligence (AI) and Machine Learning (ML) are transforming industries worldwide.</p>
        <h2>Key Applications</h2>
        <ul>
            <li>Natural Language Processing</li>
            <li>Computer Vision</li>
            <li>Predictive Analytics</li>
        </ul>
    </body>
    </html>
    """
    with open("ai_overview.html", "w") as f:
        f.write(html_content)
    
    # Sample text file
    txt_content = """
# Project Documentation

## Overview
This project implements a text extraction system supporting multiple formats.

## Features
- HTML extraction with metadata
- PDF text extraction
- DOCX document processing
- Automatic encoding detection
    """
    with open("readme.txt", "w") as f:
        f.write(txt_content)
    
    # Sample markdown
    md_content = """
# Python Best Practices

## Code Style
Follow PEP 8 guidelines for consistent code formatting.

## Documentation
Use docstrings for all public functions and classes.

## Testing
Write unit tests using pytest framework.
    """
    with open("guide.md", "w") as f:
        f.write(md_content)


def batch_extract_demo():
    """Demonstrate batch extraction from multiple files."""
    print("\n" + "=" * 60)
    print("Batch Processing Multiple Documents")
    print("=" * 60)
    
    files = ["ai_overview.html", "readme.txt", "guide.md"]
    
    for file_path in files:
        if os.path.exists(file_path):
            print(f"\n Processing: {file_path}")
            print("-" * 60)
            
            result = extract_text(file_path, extract_metadata=True, max_length=200)
            
            if result["success"]:
                print(f"Format: {result['format']}")
                print(f"\nMetadata:")
                for key, value in result['metadata'].items():
                    if value:  # Only show non-empty values
                        print(f"  {key}: {value}")
                print(f"\nText Preview:\n{result['text'][:150]}...")
            else:
                print(f"❌ Error: {result['error']}")


def metadata_analysis_demo():
    """Demonstrate detailed metadata extraction."""
    print("\n\n" + "=" * 60)
    print("Detailed Metadata Extraction")
    print("=" * 60)
    
    file_path = "ai_overview.html"
    
    if os.path.exists(file_path):
        result = extract_text(file_path, extract_metadata=True)
        
        if result["success"]:
            print(f"\n File: {file_path}")
            print(f" Format: {result['format']}\n")
            
            metadata = result['metadata']
            
            print("Document Information:")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Author: {metadata.get('author', 'N/A')}")
            print(f"  Description: {metadata.get('description', 'N/A')}")
            print(f"\nStatistics:")
            print(f"  Word Count: {metadata.get('word_count', 0):,}")
            print(f"  Character Count: {metadata.get('char_count', 0):,}")
            
            print(f"\n📖 Full Text:\n{result['text']}")


def agent_integration_demo():
    """Demonstrate integration with an agent for document analysis."""
    print("\n\n" + "=" * 60)
    print("Agent-Based Document Analysis")
    print("=" * 60)
    
    print("\n Agent analyzing 'ai_overview.html'...")
    print("-" * 60)
    
    try:
        # Create an agent specialized in document analysis
        agent = create_agent(
            name="DocumentAnalyst",
            description="Analyzes documents and provides insights",
            persona=(
                "You are a professional document analyst. When analyzing documents:\n"
                "1. Extract the text content\n"
                "2. Identify the main topics and themes\n"
                "3. Highlight key insights\n"
                "4. Provide a concise summary\n"
                "Be thorough but concise in your analysis."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[text_extractor]
        )
        
        response = agent.run(
            "Please analyze the document 'ai_overview.html'. "
            "Extract its content and provide a summary of the main points."
        )
        print(f"\n{response}")
    except Exception as e:
        print(f"\n Note: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run agent integration.")
        print("\nDirect extraction works without API key:")
        result = text_extractor.run({"file_path": "ai_overview.html"})
        if result["success"]:
            print(f"\n{result['text']}")


def comparison_demo():
    """Compare text extraction from different formats."""
    print("\n\n" + "=" * 60)
    print("Format Comparison")
    print("=" * 60)
    
    files = {
        "HTML": "ai_overview.html",
        "Text": "readme.txt",
        "Markdown": "guide.md"
    }
    
    print("\nExtraction Statistics by Format:\n")
    print(f"{'Format':<12} {'Words':<10} {'Characters':<12} {'Lines':<8}")
    print("-" * 50)
    
    for format_name, file_path in files.items():
        if os.path.exists(file_path):
            result = extract_text(file_path, extract_metadata=True)
            if result["success"]:
                metadata = result['metadata']
                words = metadata.get('word_count', 0)
                chars = metadata.get('char_count', 0)
                lines = metadata.get('line_count', len(result['text'].splitlines()))
                print(f"{format_name:<12} {words:<10} {chars:<12} {lines:<8}")


def cleanup_files():
    """Remove sample files."""
    files = ["ai_overview.html", "readme.txt", "guide.md"]
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)


def main():
    print("\n" + "=" * 60)
    print("Text Extraction Tool - Advanced Examples")
    print("=" * 60)
    
    # Create sample files
    print("\n Creating sample files...")
    create_sample_files()
    
    try:
        # Run demonstrations
        batch_extract_demo()
        metadata_analysis_demo()
        comparison_demo()
        agent_integration_demo()
        
    finally:
        # Cleanup
        print("\n\n Cleaning up sample files...")
        cleanup_files()
    
    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
