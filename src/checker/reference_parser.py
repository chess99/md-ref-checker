"""
Reference parser for extracting references from markdown files
"""

import re
from typing import List, Tuple

class ReferenceParser:
    """引用解析器"""

    def __init__(self):
        """初始化引用解析器"""
        # 匹配 Markdown 链接和图片的正则表达式
        self.link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```.*?```', re.DOTALL)

    def parse_references(self, content: str) -> List[Tuple[str, bool]]:
        """解析引用

        Args:
            content: Markdown 文件内容

        Returns:
            引用列表，每个元素为 (引用路径, 是否为图片)
        """
        # 移除代码块
        content = self.code_block_pattern.sub('', content)

        # 解析图片引用
        image_refs = [(match.group(2).split('#')[0].split('?')[0], True)
                     for match in self.image_pattern.finditer(content)]

        # 解析链接引用
        link_refs = [(match.group(2).split('#')[0].split('?')[0], False)
                    for match in self.link_pattern.finditer(content)
                    if not match.group(2).startswith('http')
                    and not match.group(2).startswith('#')]

        return image_refs + link_refs