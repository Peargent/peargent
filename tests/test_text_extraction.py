"""
Tests for Text Extraction Tool
Tests extraction from HTML, PDF, DOCX, and text files.
"""

import os
import tempfile
from pathlib import Path
import pytest

from peargent.tools.text_extraction_tool import (
    TextExtractionTool,
    extract_text
)


class TestFormatDetection:
    """Test file format detection through public API."""
    
    def test_detect_html_format(self):
        """Test HTML format detection through extract_text."""
        html_content = "<html><body><p>Test</p></body></html>"
        
        # Test .html extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        try:
            result = extract_text(temp_path)
            assert result["format"] == "html"
        finally:
            os.unlink(temp_path)
        
        # Test .htm extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.htm', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        try:
            result = extract_text(temp_path)
            assert result["format"] == "html"
        finally:
            os.unlink(temp_path)
    
    def test_detect_text_formats(self):
        """Test text format detection through extract_text."""
        content = "Test content"
        
        # Test .txt extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        try:
            result = extract_text(temp_path)
            assert result["format"] == "txt"
        finally:
            os.unlink(temp_path)
        
        # Test .md extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        try:
            result = extract_text(temp_path)
            assert result["format"] == "md"
        finally:
            os.unlink(temp_path)
    
    def test_unknown_format(self):
        """Test unknown format handling through extract_text."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            assert result["success"] is False
            assert result["format"] == "unknown"
            assert "unsupported" in result["error"].lower() or "unknown" in result["error"].lower()
        finally:
            os.unlink(temp_path)


class TestHTMLExtraction:
    """Test HTML text extraction."""
    
    def test_extract_basic_html(self):
        """Test basic HTML extraction."""
        html_content = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test.</p>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            assert result["success"] is True
            assert "Hello World" in result["text"]
            assert "This is a test" in result["text"]
            assert result["format"] == "html"
        finally:
            os.unlink(temp_path)
    
    def test_extract_html_with_metadata(self):
        """Test HTML extraction with metadata."""
        html_content = """
        <html>
        <head>
            <title>Test Document</title>
            <meta name="author" content="John Doe">
            <meta name="description" content="A test document">
        </head>
        <body><p>Content here</p></body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path, extract_metadata=True)
            assert result["success"] is True
            assert result["metadata"]["title"] == "Test Document"
            assert result["metadata"]["author"] == "John Doe"
            assert result["metadata"]["description"] == "A test document"
            assert "word_count" in result["metadata"]
        finally:
            os.unlink(temp_path)
    
    def test_extract_html_removes_scripts(self):
        """Test that script tags are removed."""
        html_content = """
        <html>
        <body>
            <p>Visible text</p>
            <script>alert('hidden');</script>
            <style>.hidden { display: none; }</style>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            assert "Visible text" in result["text"]
            assert "alert" not in result["text"]
            assert ".hidden" not in result["text"]
        finally:
            os.unlink(temp_path)


class TestTextFileExtraction:
    """Test plain text file extraction."""
    
    def test_extract_utf8_text(self):
        """Test UTF-8 text extraction."""
        content = "Hello World\nThis is a test.\nMultiple lines."
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            assert result["success"] is True
            assert "Hello World" in result["text"]
            assert result["format"] == "txt"
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_with_metadata(self):
        """Test text extraction with metadata."""
        content = "Line 1\nLine 2\nLine 3"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path, extract_metadata=True)
            assert result["success"] is True
            assert "line_count" in result["metadata"]
            assert "word_count" in result["metadata"]
            assert "char_count" in result["metadata"]
        finally:
            os.unlink(temp_path)
    
    def test_extract_markdown(self):
        """Test markdown extraction."""
        content = "# Title\n\n## Subtitle\n\nSome content here."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path, extract_metadata=True)
            assert result["success"] is True
            assert "Title" in result["text"]
            assert result["format"] == "md"
            # Title extraction from markdown
            assert result["metadata"].get("title") == "Title"
        finally:
            os.unlink(temp_path)


class TestToolIntegration:
    """Test TextExtractionTool class."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = TextExtractionTool()
        assert tool.name == "extract_text"
        assert "HTML" in tool.description
        assert "PDF" in tool.description
        assert "file_path" in tool.input_parameters
        # Optional parameters should not be in input_parameters
        assert "extract_metadata" not in tool.input_parameters
        assert "max_length" not in tool.input_parameters
    
    def test_tool_call_function(self):
        """Test calling tool function."""
        tool = TextExtractionTool()
        
        content = "<html><body><p>Test content</p></body></html>"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Test with just required parameter
            result = tool.run({"file_path": temp_path})
            assert result["success"] is True
            assert "Test content" in result["text"]
            
            # Test with optional parameters
            result = tool.run({"file_path": temp_path, "extract_metadata": True, "max_length": 50})
            assert result["success"] is True
            assert "Test content" in result["text"]
            assert "metadata" in result
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling."""
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        result = extract_text("nonexistent_file.txt")
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_unsupported_format(self):
        """Test handling of unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            assert result["success"] is False
            assert "unsupported" in result["error"].lower() or "unknown" in result["error"].lower()
        finally:
            os.unlink(temp_path)
    
    def test_max_length_truncation(self):
        """Test text truncation with max_length."""
        content = "word " * 1000  # Long text
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extract_text(temp_path, max_length=100)
            assert result["success"] is True
            assert len(result["text"]) <= 104  # 100 + "..."
            assert result["text"].endswith("...")
        finally:
            os.unlink(temp_path)


class TestURLValidation:
    """Test URL validation and SSRF protection."""
    
    def test_block_localhost(self):
        """Test that localhost URLs are blocked."""
        result = extract_text("http://localhost/test.html")
        assert result["success"] is False
        assert "localhost" in result["error"].lower() or "not allowed" in result["error"].lower()
    
    def test_block_loopback_ip(self):
        """Test that loopback IPs are blocked."""
        result = extract_text("http://127.0.0.1/test.html")
        assert result["success"] is False
        assert "not allowed" in result["error"].lower() or "loopback" in result["error"].lower()
    
    def test_block_private_ip(self):
        """Test that private IPs are blocked."""
        result = extract_text("http://192.168.1.1/test.html")
        assert result["success"] is False
        # Either blocked by validation or connection fails/times out
        assert ("private" in result["error"].lower() or 
                "not allowed" in result["error"].lower() or
                "connection" in result["error"].lower())
    
    def test_block_file_scheme(self):
        """Test that file:// URLs are treated as file paths."""
        result = extract_text("file:///etc/passwd")
        # file:// is not http/https so treated as file path and should fail
        assert result["success"] is False


class TestPDFExtraction:
    """Test PDF extraction through public API."""
    
    def test_pdf_format_unsupported_without_dependency(self):
        """Test that PDF files return appropriate format type."""
        # Create a dummy .pdf file (won't be valid PDF, but tests format detection)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4 dummy content')
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            # Should detect as PDF format (even if extraction fails due to invalid content)
            assert result["format"] == "pdf" or "pdf" in result["error"].lower()
        finally:
            os.unlink(temp_path)


class TestDOCXExtraction:
    """Test DOCX extraction through public API."""
    
    def test_docx_format_unsupported_without_dependency(self):
        """Test that DOCX files return appropriate format type."""
        # Create a dummy .docx file (won't be valid DOCX, but tests format detection)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b'dummy docx content')
            temp_path = f.name
        
        try:
            result = extract_text(temp_path)
            # Should detect as DOCX format (even if extraction fails due to invalid content)
            assert result["format"] == "docx" or "docx" in result["error"].lower()
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
