"""
Reference parser for Markdown reference checker
"""

import re
from typing import List, Tuple, Set

class ReferenceParser:
    """引用解析器"""

    def __init__(self):
        """初始化引用解析器"""
        # 匹配 Markdown 链接: [text](link)
        self.link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        # 匹配 Wiki 风格链接: [[link]] 或 [[link|text]]
        self.wiki_pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        
        # 匹配图片: ![text](link) 或 ![[link]]
        self.image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)|!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        
        # 匹配代码块
        self.code_block_pattern = r'```[\s\S]*?```|`[^`\n]+`'

    def parse_references(self, content: str) -> List[Tuple[str, bool]]:
        """解析引用

        Args:
            content: 要解析的内容

        Returns:
            引用列表，每个元素为 (引用路径, 是否为图片) 的元组
        """
        # 首先找出所有代码块的位置
        code_blocks = []
        for match in re.finditer(self.code_block_pattern, content):
            code_blocks.append((match.start(), match.end()))

        # 检查位置是否在代码块中
        def is_in_code_block(pos: int) -> bool:
            return any(start <= pos <= end for start, end in code_blocks)

        references = []
        seen = set()  # 用于去重

        # 解析图片引用（优先处理，避免被普通链接匹配）
        for match in re.finditer(self.image_pattern, content):
            if not is_in_code_block(match.start()):
                if match.group(2):  # Markdown 风格
                    link = match.group(2).split()[0]  # 移除标题等额外内容
                else:  # Wiki 风格
                    link = match.group(3)
                if link not in seen:
                    references.append((link, True))
                    seen.add(link)

        # 解析 Markdown 链接
        for match in re.finditer(self.link_pattern, content):
            if not is_in_code_block(match.start()):
                link = match.group(2).split()[0]  # 移除标题等额外内容
                if link not in seen:
                    references.append((link, False))
                    seen.add(link)

        # 解析 Wiki 风格链接
        for match in re.finditer(self.wiki_pattern, content):
            if not is_in_code_block(match.start()):
                link = match.group(1)
                if link not in seen:
                    references.append((link, False))
                    seen.add(link)

        return references

    def _extract_nested_references(self, content: str) -> List[str]:
        """提取嵌套引用

        Args:
            content: 要解析的内容

        Returns:
            引用列表
        """
        references = []
        stack = []
        current = ''
        i = 0
        
        while i < len(content):
            if i + 1 < len(content) and content[i:i+2] == '[[':
                if current:
                    stack.append(current)
                current = ''
                i += 2
            elif i + 1 < len(content) and content[i:i+2] == ']]':
                if current:
                    if '|' in current:  # 处理别名
                        current = current.split('|')[0]
                    references.append(current)
                if stack:
                    current = stack.pop()
                else:
                    current = ''
                i += 2
            else:
                current += content[i]
                i += 1
        
        return references