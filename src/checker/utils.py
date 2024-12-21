"""
Utility functions for Markdown reference checker
"""

import os
from typing import Set

def normalize_path(path: str) -> str:
    """标准化路径

    Args:
        path: 要标准化的路径

    Returns:
        标准化后的路径
    """
    return path.replace('\\', '/')

def is_markdown_file(file_path: str) -> bool:
    """检查是否为 Markdown 文件

    Args:
        file_path: 文件路径

    Returns:
        是否为 Markdown 文件
    """
    return file_path.lower().endswith('.md')

def is_image_file(file_path: str) -> bool:
    """检查是否为图片文件

    Args:
        file_path: 文件路径

    Returns:
        是否为图片文件
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
    return os.path.splitext(file_path.lower())[1] in image_extensions

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