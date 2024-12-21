"""
Utility functions for Markdown reference checker
"""

import os
import re
from typing import Set

def normalize_path(path: str) -> str:
    """规范化路径

    Args:
        path: 原始路径

    Returns:
        规范化后的路径
    """
    if not path:
        return ''
    
    # 统一使用正斜杠
    path = path.replace('\\', '/')
    
    # 移除开头的 ./
    if path.startswith('./'):
        path = path[2:]
    
    # 规范化多个斜杠
    path = re.sub(r'/+', '/', path)
    
    # 移除末尾的斜杠
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]
    
    return path

def get_file_name(path: str) -> str:
    """获取文件名（不含扩展名）

    Args:
        path: 文件路径

    Returns:
        文件名
    """
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name

def get_directory_name(path: str) -> str:
    """获取目录名

    Args:
        path: 路径

    Returns:
        目录名
    """
    return os.path.basename(os.path.dirname(path))

def is_markdown_file(filename: str) -> bool:
    """判断是否为 Markdown 文件

    Args:
        filename: 文件名

    Returns:
        是否为 Markdown 文件
    """
    return filename.lower().endswith('.md')

def is_image_file(filename: str) -> bool:
    """判断是否为图片文件

    Args:
        filename: 文件名

    Returns:
        是否为图片文件
    """
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))

def get_relative_path(path: str, base_path: str) -> str:
    """获取相对路径"""
    try:
        rel_path = os.path.relpath(path, base_path)
        return normalize_path(rel_path)
    except ValueError:
        # 处理不同驱动器的情况
        return normalize_path(path)

def normalize_link(link: str) -> str:
    """标准化链接"""
    # 移除链接中的锚点和查询参数
    link = link.split('#')[0].split('?')[0]
    # 移除末尾的斜杠
    link = link.rstrip('/')
    return normalize_path(link)

def get_unique_files(files: Set[str]) -> Set[str]:
    """获取唯一的文件列表（不区分大小写）"""
    return {normalize_path(f) for f in files} 