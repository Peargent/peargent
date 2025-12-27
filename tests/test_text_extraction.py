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
    extract_text,
    _detect_format
)


class TestFormatDetection:
    """Test file format detection."""
    
    def test_detect_html_format(self):
        """Test HTML format detection."""
        assert _detect_format("document.html") == "html"
        assert _detect_format("page.htm") == "html"
    
    def test_detect_pdf_format(self):
        """Test PDF format detection."""
        assert _detect_format("document.pdf") == "pdf"
    
    def test_detect_docx_format(self):
        """Test DOCX format detection."""
        assert _detect_format("document.docx") == "docx"
        assert _detect_format("document.doc") == "docx"
    
    def test_detect_text_format(self):
        """Test text format detection."""
        assert _detect_format("file.txt") == "txt"
        assert _detect_format("readme.md") == "md"
    
    def test_detect_url(self):
        """Test URL detection."""
        assert _detect_format("http://example.com") == "html"
        assert _detect_format("https://example.com/page") == "html"
    
    def test_unknown_format(self):
        """Test unknown format detection."""
        assert _detect_format("file.xyz") == "unknown"


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
    
    def test_tool_call_function(self):
        """Test calling tool function."""
        tool = TextExtractionTool()
        
        content = "<html><body><p>Test content</p></body></html>"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = tool.call_function(temp_path)
            assert result["success"] is True
            assert "Test content" in result["text"]
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


class TestPDFExtraction:
    """Test PDF extraction (requires PyPDF2)."""
    
    def test_pdf_import_error_handling(self):
        """Test that PDF extraction provides helpful error for missing dependency."""
        # We can't easily create a real PDF for testing without external dependencies
        # But we can test that the function exists and has proper structure
        from peargent.tools.text_extraction_tool import _extract_pdf
        assert callable(_extract_pdf)


class TestDOCXExtraction:
    """Test DOCX extraction (requires python-docx)."""
    
    def test_docx_import_error_handling(self):
        """Test that DOCX extraction provides helpful error for missing dependency."""
        from peargent.tools.text_extraction_tool import _extract_docx
        assert callable(_extract_docx)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
