"""Test cases for parsers module."""

from typing import TYPE_CHECKING

from md_ref_checker.parsers import MarkdownParser

if TYPE_CHECKING:
    pass


def test_parse_simple_reference() -> None:
    """Test parsing a simple reference."""
    parser = MarkdownParser()
    content = "This is a [[test]] reference."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 1
    assert refs[0].target == "test"
    assert refs[0].source_file == "test.md"
    assert refs[0].line_number == 1
    assert refs[0].column == 11
    assert not refs[0].is_image


def test_parse_aliased_reference() -> None:
    """Test parsing a reference with alias."""
    parser = MarkdownParser()
    content = "This is a [[test|alias]] reference."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 1
    assert refs[0].target == "test"


def test_parse_image_reference() -> None:
    """Test parsing an image reference."""
    parser = MarkdownParser()
    content = "This is an ![[image.png]] reference."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 1
    assert refs[0].target == "image.png"
    assert refs[0].is_image


def test_parse_markdown_image() -> None:
    """Test parsing a standard Markdown image."""
    parser = MarkdownParser()
    content = "This is a ![alt text](image.png) reference."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 1
    assert refs[0].target == "image.png"
    assert refs[0].is_image


def test_parse_multiple_references() -> None:
    """Test parsing multiple references in one line."""
    parser = MarkdownParser()
    content = "This has [[ref1]] and [[ref2]] and ![[img.png]]."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 3
    assert refs[0].target == "ref1"
    assert refs[1].target == "ref2"
    assert refs[2].target == "img.png"
    assert refs[2].is_image


def test_parse_multiline_references() -> None:
    """Test parsing references across multiple lines."""
    parser = MarkdownParser()
    content = """Line 1 with [[ref1]]
    Line 2 with [[ref2]]
    Line 3 with ![[img.png]]"""
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 3
    assert refs[0].target == "ref1"
    assert refs[0].line_number == 1
    assert refs[1].target == "ref2"
    assert refs[1].line_number == 2
    assert refs[2].target == "img.png"
    assert refs[2].line_number == 3


def test_parse_no_references() -> None:
    """Test parsing content without references."""
    parser = MarkdownParser()
    content = "This is a test without any references."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 0


def test_parse_invalid_references() -> None:
    """Test parsing invalid reference formats."""
    parser = MarkdownParser()
    content = "This has [[[invalid]]] and [[]] and ![] references."
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 0


def test_parse_code_block_references() -> None:
    """Test that references in code blocks are ignored."""
    parser = MarkdownParser()
    content = """Normal [[ref1]]
    ```
    Code block [[ref2]]
    ```
    Normal ![[img.png]]"""
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 2
    assert refs[0].target == "ref1"
    assert refs[1].target == "img.png"


def test_parse_inline_code_references() -> None:
    """Test that references in inline code are ignored."""
    parser = MarkdownParser()
    content = "Normal [[ref1]] and `[[ref2]]` and ![[img.png]]"
    refs = list(parser.parse_references("test.md", content))

    assert len(refs) == 2
    assert refs[0].target == "ref1"
    assert refs[1].target == "img.png"
