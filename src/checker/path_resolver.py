"""
Path resolution functionality for Markdown reference checker
"""

import os
from typing import Set, Optional
from .utils import normalize_path, is_markdown_file

class PathResolver:
    """路径解析器"""
    
    def __init__(self, root_dir: str):
        """初始化路径解析器

        Args:
            root_dir: 根目录路径
        """
        self.root_dir = str(root_dir)  # 确保是字符串
        self.referenced_images: Set[str] = set()
    
    def resolve_link(self, link: str, source_file: str, is_image: bool = False) -> str:
        """解析链接

        Args:
            link: 链接路径
            source_file: 源文件路径
            is_image: 是否为图片链接

        Returns:
            解析后的路径
        """
        # 移除文件扩展名
        if not is_image and link.endswith('.md'):
            link = link[:-3]

        # 处理绝对路径
        if link.startswith('/'):
            resolved = link[1:]
        else:
            # 处理相对路径
            source_dir = os.path.dirname(source_file)
            resolved = os.path.normpath(os.path.join(source_dir, link))
            resolved = resolved.replace('\\', '/')

        # 处理图片路径
        if is_image:
            # 检查原始路径
            if os.path.exists(os.path.join(self.root_dir, resolved)):
                self.referenced_images.add(resolved)
                return resolved

            # 检查 assets 目录
            assets_path = os.path.join('assets', os.path.basename(resolved))
            assets_path = assets_path.replace('\\', '/')
            if os.path.exists(os.path.join(self.root_dir, assets_path)):
                self.referenced_images.add(assets_path)
                return assets_path

            # 如果都不存在，返回原始路径
            return link

        # 处理 Markdown 文件路径
        if not resolved.endswith('.md'):
            resolved += '.md'

        # 如果文件不存在，返回原始路径
        if not os.path.exists(os.path.join(self.root_dir, resolved)):
            if not link.endswith('.md'):
                return link
            return link[:-3]

        return resolved