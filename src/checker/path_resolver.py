"""
Path resolution functionality for Markdown reference checker
"""

import os
from typing import Set, Optional
from .utils import normalize_path, is_markdown_file
from .file_scanner import FileScanner

class PathResolver:
    """路径解析器，负责解析和处理文件路径"""
    
    def __init__(self, file_scanner: FileScanner):
        self.file_scanner = file_scanner
        self.referenced_images: Set[str] = set()
    
    def resolve_link(self, link: str, source_file: str, is_image: bool = False) -> str:
        """解析链接。
        
        Args:
            link: 链接路径
            source_file: 源文件路径
            is_image: 是否为图片链接
            
        Returns:
            解析后的路径
        """
        # 移除链接中的锚点和查询参数
        link = link.split('#')[0].split('?')[0]
        
        # 处理绝对路径（以/开头）
        if link.startswith('/'):
            link = link[1:]  # 移除开头的斜杠
        
        # 处理相对路径
        if not link.startswith('/'):
            source_dir = os.path.dirname(source_file)
            link = os.path.normpath(os.path.join(source_dir, link))
            link = link.replace('\\', '/')
        
        # 处理图片引用
        if is_image:
            # 如果已经在 assets 目录下，检查是否存在
            if link.startswith('assets/'):
                if link in self.file_scanner.image_files:
                    self.referenced_images.add(link)
                return link
            
            # 尝试在 assets 目录下查找
            assets_path = f'assets/{link}'
            if assets_path in self.file_scanner.image_files:
                self.referenced_images.add(assets_path)
                return assets_path
            
            # 如果找不到，返回原始路径
            return link
        
        # 处理文档引用
        if not link.endswith('.md'):
            link += '.md'
        
        # 检查文件是否存在
        if link in self.file_scanner.files:
            return link
        
        # 如果找不到，返回不带扩展名的原始路径
        return link.replace('.md', '')