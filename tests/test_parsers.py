"""Test cases for the parsers module."""
from typing import TYPE_CHECKING

import pytest
from md_ref_checker.parsers import MarkdownParser

if TYPE_CHECKING:
    pass  # No type checking imports needed


def test_parse_simple_reference():
    """Test parsing a simple file reference."""
    parser = MarkdownParser()
    content = "This is a [[test]] reference."
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    ref = refs[0]
    assert ref.source_file == "source.md"
    assert ref.target == "test"
    assert ref.line_number == 1
    assert ref.column == 11
    assert not ref.is_image


def test_parse_reference_with_alias():
    """Test parsing a reference with alias."""
    parser = MarkdownParser()
    content = "This is a [[test|Test File]] reference."
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "test"


def test_parse_heading_reference():
    """Test parsing a reference with heading."""
    parser = MarkdownParser()
    content = "See [[file#heading]] for details."
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "file"  # heading is stripped


def test_parse_image_reference():
    """Test parsing an image reference."""
    parser = MarkdownParser()
    content = "Here's an image: ![[image.png]]"
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "image.png"
    assert ref.is_image


def test_parse_markdown_image():
    """Test parsing a standard Markdown image."""
    parser = MarkdownParser()
    content = "![Alt text](image.png)"
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "image.png"
    assert ref.is_image


def test_ignore_code_blocks():
    """Test that references in code blocks are ignored."""
    parser = MarkdownParser()
    content = """
Here's a reference [[test]]
```python
# This [[code]] should be ignored
```
Another reference [[test2]]
"""
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 2
    targets = {ref.target for ref in refs}
    assert targets == {"test", "test2"}


def test_ignore_inline_code():
    """Test that references in inline code are ignored."""
    parser = MarkdownParser()
    content = "Here's a reference [[test]] and `some [[code]]` to ignore."
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    assert refs[0].target == "test"


def test_multiple_references_same_line():
    """Test parsing multiple references on the same line."""
    parser = MarkdownParser()
    content = "See [[file1]] and [[file2]] for details."
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 2
    targets = {ref.target for ref in refs}
    assert targets == {"file1", "file2"}


def test_reference_with_spaces():
    """Test parsing references with spaces."""
    parser = MarkdownParser()
    content = "[[My File.md]]"
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    assert refs[0].target == "My File.md"


def test_ignore_external_urls():
    """Test that external URLs are ignored."""
    parser = MarkdownParser()
    content = """
[[local-file]]
![External Image](https://example.com/image.png)
"""
    refs = list(parser.parse_references("source.md", content))
    
    assert len(refs) == 1
    assert refs[0].target == "local-file"
