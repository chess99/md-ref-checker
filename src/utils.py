"""工具函数模块"""

import os
from typing import List, Set

def normalize_path(path: str) -> str:
    """标准化路径，统一使用正斜杠"""
    return path.replace('\\', '/')

def is_markdown_file(filename: str) -> bool:
    """检查文件是否为 Markdown 文件"""
    return filename.lower().endswith('.md')

def is_image_file(filename: str) -> bool:
    """检查文件是否为图片文件"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
    return os.path.splitext(filename.lower())[1] in image_extensions

def should_ignore_file(filename: str, ignore_patterns: List[str]) -> bool:
    """检查文件是否应该被忽略
    
    Args:
        filename: 要检查的文件名
        ignore_patterns: 忽略模式列表
        
    Returns:
        bool: 如果文件应该被忽略则返回True
    """
    from fnmatch import fnmatch
    return any(fnmatch(filename, pattern) for pattern in ignore_patterns)

def find_markdown_files(
    root_dir: str,
    ignore_patterns: List[str] = None
) -> Set[str]:
    """查找目录下所有的 Markdown 文件
    
    Args:
        root_dir: 根目录
        ignore_patterns: 忽略模式列表
        
    Returns:
        Set[str]: 相对于根目录的 Markdown 文件路径集合
    """
    ignore_patterns = ignore_patterns or []
    markdown_files = set()
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if not is_markdown_file(file):
                continue
                
            rel_path = os.path.relpath(
                os.path.join(root, file),
                root_dir
            )
            
            if should_ignore_file(rel_path, ignore_patterns):
                continue
                
            markdown_files.add(normalize_path(rel_path))
            
    return markdown_files 