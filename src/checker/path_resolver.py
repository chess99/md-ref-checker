"""
Path resolution functionality for Markdown reference checker
"""

import os
from typing import Set
from .utils import normalize_path, is_markdown_file
from .file_scanner import FileScanner

class PathResolver:
    """路径解析器，负责解析和处理文件路径"""
    
    def __init__(self, file_scanner: FileScanner):
        self.file_scanner = file_scanner
        self.referenced_images: Set[str] = set()
    
    def resolve_link(self, link: str, current_file: str, is_image: bool = False) -> str:
        """解析引用链接，处理相对路径"""
        # 规范化路径
        link = normalize_path(link)
        current_file = normalize_path(current_file)
        
        # 如果是绝对路径（以/开头）
        if link.startswith('/'):
            link = link.lstrip('/')
        else:
            # 处理相对路径
            current_dir = os.path.dirname(current_file)
            if current_dir:
                link = os.path.join(current_dir, link)
                # 规范化路径，处理 .. 和 .
                link = os.path.normpath(link)
                link = normalize_path(link)
        
        base_link = os.path.splitext(link)[0]  # 不带扩展名的路径
        base_name = os.path.basename(link)
        base_name_no_ext = os.path.splitext(base_name)[0]
        
        # 如果是图片引用，优先在assets目录下查找
        if is_image:
            # 如果已经在assets目录下，检查是否存在
            if link.startswith('assets/'):
                if link in self.file_scanner.image_files:
                    self.referenced_images.add(link)
                    return link
            
            # 尝试在assets目录下查找
            assets_path = f"assets/{base_name}"
            if assets_path in self.file_scanner.image_files:
                self.referenced_images.add(assets_path)
                return assets_path
            
            # 如果在其他位置找到了图片文件，也返回
            if link in self.file_scanner.image_files:
                self.referenced_images.add(link)
                return link
            
            # 如果找不到图片，返回原始链接
            return link
        
        # 检查所有可能的映射
        possible_keys = [
            link,  # 完整路径
            base_link,  # 不带扩展名的完整路径
            base_name,  # 文件名（带扩展名）
            base_name_no_ext,  # 文件名（不带扩展名）
        ]
        
        # 对于每个可能的键，检查是否存在映射
        for key in possible_keys:
            files = self.file_scanner.get_file_mapping(key)
            if files:
                # 如果是图片引用，优先查找图片文件
                if is_image:
                    # 先尝试查找图片文件
                    image_files = [f for f in files if f in self.file_scanner.image_files]
                    if image_files:
                        self.referenced_images.add(image_files[0])
                        return image_files[0]
                else:
                    # 如果不是图片引用，优先返回.md文件
                    md_files = [f for f in files if is_markdown_file(f)]
                    if md_files:
                        return md_files[0]
                    # 如果找不到.md文件，返回第一个匹配的文件
                    if files:
                        return files[0]
        
        # 如果��找不到，返回原始链接
        return link