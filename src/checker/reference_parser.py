"""
Reference parser for extracting references from markdown files
"""

import re
from typing import List, Tuple, Set
from .utils import normalize_link, is_url

class ReferenceParser:
    """引用解析器"""

    def __init__(self):
        """初始化引用解析器"""
        # 匹配 Markdown 链接和图片的正则表达式
        self.link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.wiki_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        self.image_wiki_pattern = re.compile(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        
        # 匹配代码块的正则表达式
        self.code_block_pattern = re.compile(r'```[\s\S]*?```|`[^`\n]+`')
        self.html_comment_pattern = re.compile(r'<!--[\s\S]*?-->')

    def parse_references(self, content: str) -> List[Tuple[str, bool]]:
        """解析引用

        Args:
            content: Markdown 文件内容

        Returns:
            引用列表，每个元素为 (引用路径, 是否为图片)
        """
        # 移除代码块和 HTML 注释
        content = self._remove_code_blocks(content)
        content = self.html_comment_pattern.sub('', content)

        references: Set[Tuple[str, bool]] = set()

        # 解析图片引用
        for match in self.image_pattern.finditer(content):
            link = match.group(2).strip()
            link = normalize_link(link)
            if link and not is_url(link):
                references.add((link, True))

        # 解析图片 Wiki 引用
        for match in self.image_wiki_pattern.finditer(content):
            link = match.group(1).strip()
            link = normalize_link(link)
            if link and not is_url(link):
                references.add((link, True))

        # 解析 Markdown 链接
        for match in self.link_pattern.finditer(content):
            link = match.group(2).strip()
            link = normalize_link(link)
            if link and not is_url(link) and not link.startswith('#'):
                references.add((link, False))

        # 解析 Wiki 链接
        for match in self.wiki_pattern.finditer(content):
            link = match.group(1).strip()
            link = normalize_link(link)
            if link and not is_url(link) and not link.startswith('#'):
                references.add((link, False))

        # 过滤重复引用
        filtered_refs = []
        seen = set()
        for ref, is_image in sorted(references):
            if (ref, is_image) not in seen:
                filtered_refs.append((ref, is_image))
                seen.add((ref, is_image))

        return filtered_refs

    def _remove_code_blocks(self, content: str) -> str:
        """移除代码块

        Args:
            content: 原始内容

        Returns:
            处理后的内容
        """
        # 记录代码块的位置
        positions = []
        for match in self.code_block_pattern.finditer(content):
            positions.append((match.start(), match.end()))

        # 如果没有代码块，直接返回
        if not positions:
            return content

        # 构建不包含代码块的内容
        result = []
        last_end = 0
        for start, end in positions:
            if start > last_end:
                result.append(content[last_end:start])
            last_end = end
        if last_end < len(content):
            result.append(content[last_end:])

        return ''.join(result)