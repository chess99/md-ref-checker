"""Tests for the Markdown parser."""

from typing import TYPE_CHECKING

import pytest

from md_ref_checker.models import Reference
from md_ref_checker.parsers import MarkdownParser

if TYPE_CHECKING:
    pass


@pytest.fixture
def parser() -> MarkdownParser:
    """Create a parser instance."""
    return MarkdownParser()


def test_parse_wiki_reference(parser: MarkdownParser) -> None:
    """Test parsing Obsidian-style wiki references."""
    content = "This is a [[reference]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="reference",
        line_number=1,
        column=11,
        line_content=content,
        is_image=False,
    )


def test_parse_wiki_reference_with_alias(parser: MarkdownParser) -> None:
    """Test parsing Obsidian-style wiki references with aliases."""
    content = "This is a [[file|alias]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="file",
        line_number=1,
        column=11,
        line_content=content,
        is_image=False,
    )


def test_parse_wiki_image(parser: MarkdownParser) -> None:
    """Test parsing Obsidian-style image references."""
    content = "This is an ![[image.png]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="image.png",
        line_number=1,
        column=12,
        line_content=content,
        is_image=True,
    )


def test_parse_wiki_image_with_alias(parser: MarkdownParser) -> None:
    """Test parsing Obsidian-style image references with aliases."""
    content = "This is an ![[image.png|alt text]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="image.png",
        line_number=1,
        column=12,
        line_content=content,
        is_image=True,
    )


def test_parse_markdown_image(parser: MarkdownParser) -> None:
    """Test parsing standard Markdown image references."""
    content = "This is a ![alt](image.png) in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="image.png",
        line_number=1,
        column=11,
        line_content=content,
        is_image=True,
    )


def test_skip_external_urls(parser: MarkdownParser) -> None:
    """Test that external URLs are skipped."""
    content = "![](https://example.com/image.png)"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 0


def test_skip_code_blocks(parser: MarkdownParser) -> None:
    """Test that references in code blocks are skipped."""
    content = """
Some text
```python
print("[[not a reference]]")
```
[[real reference]]
    """.strip()
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0].target == "real reference"


def test_skip_inline_code(parser: MarkdownParser) -> None:
    """Test that references in inline code are skipped."""
    content = "This is `[[not a reference]]` but this is [[a reference]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0].target == "a reference"


def test_multiple_references(parser: MarkdownParser) -> None:
    """Test parsing multiple references in one line."""
    content = "[[ref1]] and [[ref2]] and ![[img.png]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 3
    assert [ref.target for ref in refs] == ["ref1", "ref2", "img.png"]
    assert [ref.is_image for ref in refs] == [False, False, True]


def test_reference_with_heading(parser: MarkdownParser) -> None:
    """Test that heading references are cleaned."""
    content = "[[file#heading]] and ![[image.png#size=100]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 2
    assert [ref.target for ref in refs] == ["file", "image.png"]


def test_empty_references(parser: MarkdownParser) -> None:
    """Test that empty references are skipped."""
    content = "[[]] and ![[]] and ![]()"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 0


def test_complex_document(parser: MarkdownParser) -> None:
    """Test parsing a complex document with various reference types."""
    content = """
# Title

This is a [[reference]] to a file.
Here's an image: ![[image.png|300]]

```python
# This [[should]] be ignored
print("![[also ignored]]")
```

Some `[[inline code]]` followed by [[real ref]].

Regular markdown: ![alt text](local.png)
External link: ![external](https://example.com/img.png)

[[file#heading|alias]] and ![[image.jpg#size=200|alt]]
    """.strip()

    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 6

    expected = [
        ("reference", False),
        ("image.png", True),
        ("real ref", False),
        ("local.png", True),
        ("file", False),
        ("image.jpg", True),
    ]

    for ref, (target, is_image) in zip(refs, expected):
        assert ref.target == target
        assert ref.is_image == is_image
