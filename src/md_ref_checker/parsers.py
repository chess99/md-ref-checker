"""Markdown parser implementation."""

import re
from typing import Iterator

from .models import Reference


class MarkdownParser:
    """Parser for Markdown files."""

    def __init__(self) -> None:
        """Initialize the parser."""
        # Wiki-style references: [[file]] or ![[file]]
        self.wiki_ref_pattern = re.compile(r"(!?\[\[([^]|]+)(?:\|[^]]+)?\]\])")
        # Standard Markdown image references: ![alt](file)
        self.md_img_pattern = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")

    def parse_references(self, source_file: str, content: str) -> Iterator[Reference]:
        """Parse references from Markdown content.

        Args:
            source_file: The file being parsed
            content: The Markdown content to parse

        Returns:
            Iterator of Reference objects
        """
        # Track code block state
        in_code_block = False
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Check for code block markers
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip code blocks
            if in_code_block:
                continue

            # Skip inline code
            parts = line.split("`")
            clean_line = ""
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Outside inline code
                    clean_line += part
                else:  # Inside inline code
                    clean_line += " " * len(part)  # Preserve length

            # Find wiki-style references
            for match in self.wiki_ref_pattern.finditer(clean_line):
                full_match, target = match.groups()
                # Check if it's an embed reference
                is_embed = full_match.startswith("!")
                # Remove any heading reference
                target = target.split("#")[0]
                yield Reference(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    column=match.start() + 1,
                    line_content=line,
                    is_embed=is_embed,
                )

            # Find standard Markdown image references
            for match in self.md_img_pattern.finditer(clean_line):
                # Skip external URLs
                target = match.group(2)
                if target.startswith(("http://", "https://")):
                    continue
                yield Reference(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    column=match.start() + 1,
                    line_content=line,
                    is_embed=True,  # Standard Markdown images are always embedded
                )
