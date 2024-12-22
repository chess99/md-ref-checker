"""Markdown parsing utilities."""

import re
from typing import Iterator, Match

from .models import Reference


class MarkdownParser:
    """Parser for extracting references from Markdown files."""

    def __init__(self) -> None:
        # Match Obsidian-style references: [[file]] or [[file|alias]]
        self.wiki_ref_pattern = re.compile(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]")
        # Match Obsidian-style images: ![[image]]
        self.wiki_img_pattern = re.compile(r"!\[\[([^|\]]+)(?:\|[^\]]+)?\]\]")
        # Match standard Markdown images: ![alt](path), but not external URLs
        self.md_img_pattern = re.compile(r"!\[(?:[^\]]*)\]\((?!https?://)(.*?)\)")
        # Match inline code blocks
        self.inline_code_pattern = re.compile(r"`[^`]+`")

    def _clean_target(self, target: str) -> str:
        """Clean up the target path by removing heading references."""
        # Remove heading references (e.g., file#heading -> file)
        return target.split("#")[0]

    def _find_column(self, line: str, match: Match[str]) -> int:
        """Find the real column number in the original line."""
        # Skip inline code blocks
        line_parts = []
        last_end = 0
        for code_match in self.inline_code_pattern.finditer(line):
            line_parts.append(line[last_end : code_match.start()])
            last_end = code_match.end()
        line_parts.append(line[last_end:])

        # Calculate actual column number
        pos = 0
        for part in line_parts:
            found_pos = part.find(match.group(0))
            if found_pos != -1:
                return pos + found_pos + 1
            pos += len(part)
        return match.start() + 1

    def _remove_inline_code(self, line: str) -> str:
        """Remove inline code blocks from a line."""
        result = []
        last_end = 0
        for match in self.inline_code_pattern.finditer(line):
            result.append(line[last_end : match.start()])
            # Replace code block with spaces to maintain column numbers
            result.append(" " * (match.end() - match.start()))
            last_end = match.end()
        result.append(line[last_end:])
        return "".join(result)

    def parse_references(self, source_file: str, content: str) -> Iterator[Reference]:
        """Parse references from Markdown content."""
        lines = content.splitlines()
        in_code_block = False

        for line_num, line in enumerate(lines, start=1):
            # Check if entering or leaving code block
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip processing inside code blocks
            if in_code_block:
                continue

            # Remove inline code blocks
            clean_line = self._remove_inline_code(line)

            # Process regular references first
            for match in self.wiki_ref_pattern.finditer(clean_line):
                # Skip if this is part of an image reference
                if clean_line[match.start() - 1 : match.start()] == "!":
                    continue
                target = self._clean_target(match.group(1))
                if target:  # Skip empty references
                    column = self._find_column(line, match)
                    yield Reference(
                        source_file=source_file,
                        target=target,
                        line_number=line_num,
                        column=column,
                        line_content=line.strip(),
                        is_image=False,
                    )

            # Process Obsidian-style image references
            for match in self.wiki_img_pattern.finditer(clean_line):
                target = self._clean_target(match.group(1))
                if target:  # Skip empty references
                    column = self._find_column(line, match)
                    yield Reference(
                        source_file=source_file,
                        target=target,
                        line_number=line_num,
                        column=column,
                        line_content=line.strip(),
                        is_image=True,
                    )

            # Process standard Markdown image references
            for match in self.md_img_pattern.finditer(clean_line):
                target = self._clean_target(match.group(1))
                if target:  # Skip empty references
                    column = self._find_column(line, match)
                    yield Reference(
                        source_file=source_file,
                        target=target,
                        line_number=line_num,
                        column=column,
                        line_content=line.strip(),
                        is_image=True,
                    )
