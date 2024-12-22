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
    """Test parsing wiki-style link references."""
    content = "This is a [[reference]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="reference",
        line_number=1,
        column=11,
        line_content=content,
        is_embed=False,  # Link only
    )


def test_parse_wiki_reference_with_alias(parser: MarkdownParser) -> None:
    """Test parsing wiki-style link references with aliases."""
    content = "This is a [[file|alias]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="file",
        line_number=1,
        column=11,
        line_content=content,
        is_embed=False,  # Link only
    )


def test_parse_wiki_embed(parser: MarkdownParser) -> None:
    """Test parsing wiki-style embed references."""
    content = "This is an ![[file.md]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="file.md",
        line_number=1,
        column=12,
        line_content=content,
        is_embed=True,  # Embed content
    )


def test_parse_wiki_embed_with_alias(parser: MarkdownParser) -> None:
    """Test parsing wiki-style embed references with aliases."""
    content = "This is an ![[file.md|alt text]] in text."
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 1
    assert refs[0] == Reference(
        source_file="test.md",
        target="file.md",
        line_number=1,
        column=12,
        line_content=content,
        is_embed=True,  # Embed content
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
        is_embed=True,  # Embed content
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
    content = "[[ref1]] and [[ref2]] and ![[file.md]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 3
    assert [ref.target for ref in refs] == ["ref1", "ref2", "file.md"]
    assert [ref.is_embed for ref in refs] == [False, False, True]  # Link, Link, Embed


def test_reference_with_heading(parser: MarkdownParser) -> None:
    """Test that heading references are cleaned."""
    content = "[[file#heading]] and ![[doc.md#section=100]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 2
    assert [ref.target for ref in refs] == ["file", "doc.md"]


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
Here's an embed: ![[code.py|300]]

```python
# This [[should]] be ignored
print("![[also ignored]]")
```

Some `[[inline code]]` followed by [[real ref]].

Regular markdown: ![alt text](local.png)
External link: ![external](https://example.com/img.png)

[[file#heading|alias]] and ![[doc.md#size=200|alt]]
    """.strip()

    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 6

    expected = [
        ("reference", False),  # Link
        ("code.py", True),  # Embed
        ("real ref", False),  # Link
        ("local.png", True),  # Embed (standard MD image)
        ("file", False),  # Link
        ("doc.md", True),  # Embed
    ]

    for ref, (target, is_embed) in zip(refs, expected):
        assert ref.target == target
        assert ref.is_embed == is_embed


def test_reference_without_extension(parser: MarkdownParser) -> None:
    """Test that references without extensions assume .md."""
    content = "[[file]] and ![[document]]"
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 2
    assert [ref.target for ref in refs] == ["file", "document"]
    assert [ref.is_embed for ref in refs] == [False, True]


def test_non_markdown_references(parser: MarkdownParser) -> None:
    """Test references to non-markdown files."""
    content = """
        [[script.py]] and ![[data.csv]]
        [[image.png]] and ![[doc.pdf]]
    """.strip()
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 4
    assert [ref.target for ref in refs] == [
        "script.py",
        "data.csv",
        "image.png",
        "doc.pdf",
    ]
    assert [ref.is_embed for ref in refs] == [False, True, False, True]


def test_references_with_spaces(parser: MarkdownParser) -> None:
    """Test references to files with spaces in names."""
    content = """
        [[my document]] and ![[project notes]]
        [[meeting notes.md]] and ![[final report.pdf]]
    """.strip()
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 4
    assert [ref.target for ref in refs] == [
        "my document",
        "project notes",
        "meeting notes.md",
        "final report.pdf",
    ]
    assert [ref.is_embed for ref in refs] == [False, True, False, True]


def test_references_with_multiple_dots(parser: MarkdownParser) -> None:
    """Test references to files with multiple dots in names."""
    content = """
        [[v1.0.0.md]] and ![[backup.2023.12.22.md]]
        [[test.spec.ts]] and ![[data.backup.csv]]
    """.strip()
    refs = list(parser.parse_references("test.md", content))
    assert len(refs) == 4
    assert [ref.target for ref in refs] == [
        "v1.0.0.md",
        "backup.2023.12.22.md",
        "test.spec.ts",
        "data.backup.csv",
    ]
    assert [ref.is_embed for ref in refs] == [False, True, False, True]
