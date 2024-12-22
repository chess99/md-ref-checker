"""Markdown parsing utilities."""
import re
from typing import Iterator, Match
from .models import Reference


class MarkdownParser:
    """Parser for extracting references from Markdown files."""

    def __init__(self) -> None:
        # 匹配 Obsidian 风格的引用: [[file]] 或 [[file|alias]]
        self.wiki_ref_pattern = re.compile(r'\[\[(.*?)(?:\|.*?)?\]\]')
        # 匹配 Obsidian 风格的图片: ![[image]]
        self.wiki_img_pattern = re.compile(r'!\[\[(.*?)(?:\|.*?)?\]\]')
        # 匹配标准 Markdown 图片: ![alt](path)，但不匹配外部URL
        self.md_img_pattern = re.compile(r'!\[(?:[^\]]*)\]\((?!https?://)(.*?)\)')
        # 匹配行内代码块
        self.inline_code_pattern = re.compile(r'`[^`]+`')

    def _clean_target(self, target: str) -> str:
        """Clean up the target path by removing heading references."""
        # 移除标题引用（如 file#heading -> file）
        return target.split('#')[0]

    def _find_column(self, line: str, match: Match[str]) -> int:
        """Find the real column number in the original line."""
        # 跳过行内代码块
        line_parts = []
        last_end = 0
        for code_match in self.inline_code_pattern.finditer(line):
            line_parts.append(line[last_end:code_match.start()])
            last_end = code_match.end()
        line_parts.append(line[last_end:])
        
        # 计算实际列号
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
            result.append(line[last_end:match.start()])
            # 替换代码块为等长的空格，以保持列号计算正确
            result.append(' ' * (match.end() - match.start()))
            last_end = match.end()
        result.append(line[last_end:])
        return ''.join(result)

    def parse_references(self, source_file: str, content: str) -> Iterator[Reference]:
        """Parse references from Markdown content."""
        lines = content.splitlines()
        in_code_block = False
        
        for line_num, line in enumerate(lines, start=1):
            # 检查是否进入或离开代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # 在代码块内跳过处理
            if in_code_block:
                continue
            
            # 移除行内代码块
            clean_line = self._remove_inline_code(line)
            
            # 处理 Obsidian 风格的图片引用
            for match in self.wiki_img_pattern.finditer(clean_line):
                target = self._clean_target(match.group(1))
                column = self._find_column(line, match)
                yield Reference(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    column=column,
                    line_content=line.strip(),
                    is_image=True,
                )
            
            # 处理标准 Markdown 图片
            for match in self.md_img_pattern.finditer(clean_line):
                target = self._clean_target(match.group(1))
                column = self._find_column(line, match)
                yield Reference(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    column=column,
                    line_content=line.strip(),
                    is_image=True,
                )
            
            # 处理 Obsidian 风格的文件引用
            for match in self.wiki_ref_pattern.finditer(clean_line):
                # 跳过已处理的图片引用
                if clean_line[match.start()-1:match.start()] == '!':
                    continue
                target = self._clean_target(match.group(1))
                column = self._find_column(line, match)
                yield Reference(
                    source_file=source_file,
                    target=target,
                    line_number=line_num,
                    column=column,
                    line_content=line.strip(),
                    is_image=False,
                )
