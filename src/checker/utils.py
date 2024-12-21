"""
Utility functions for Markdown reference checker
"""

import os
import re
from typing import Set, Optional
from urllib.parse import urlparse

def normalize_path(path: str) -> str:
    """标准化路径

    Args:
        path: 要标准化的路径

    Returns:
        标准化后的路径
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

def is_markdown_file(file_path: str) -> bool:
    """检查是否为 Markdown 文件

    Args:
        file_path: 文件路径

    Returns:
        是否为 Markdown 文件
    """
    return bool(file_path) and file_path.lower().endswith('.md')

def is_image_file(file_path: str) -> bool:
    """检查是否为图片文件

    Args:
        file_path: 文件路径

    Returns:
        是否为图片文件
    """
    if not file_path:
        return False
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
    return os.path.splitext(file_path.lower())[1] in image_extensions

def get_file_name(path: str) -> str:
    """获取文件名（不含扩展名）

    Args:
        path: 文件路径

    Returns:
        文件名
    """
    if not path:
        return ''
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
    if not path:
        return ''
    return os.path.basename(os.path.dirname(path))

def get_relative_path(path: str, base_path: str) -> str:
    """获取相对路径

    Args:
        path: 目标路径
        base_path: 基准路径

    Returns:
        相对路径
    """
    if not path or not base_path:
        return normalize_path(path)
    try:
        rel_path = os.path.relpath(path, base_path)
        return normalize_path(rel_path)
    except ValueError:
        # 处理不同驱动器的情况
        return normalize_path(path)

def normalize_link(link: str) -> str:
    """标准化链接

    Args:
        link: 链接

    Returns:
        标准化后的链接
    """
    if not link:
        return ''
    # 移除链接中的锚点和查询参数
    link = link.split('#')[0].split('?')[0]
    # 移除末尾的斜杠
    link = link.rstrip('/')
    return normalize_path(link)

def is_url(link: str) -> bool:
    """检查是否为 URL

    Args:
        link: 链接

    Returns:
        是否为 URL
    """
    if not link:
        return False
    try:
        result = urlparse(link)
        return bool(result.scheme and result.netloc)
    except ValueError:
        return False

def get_unique_files(files: Set[str]) -> Set[str]:
    """获取唯一的文件列表（不区分大小写）

    Args:
        files: 文件集合

    Returns:
        唯一的文件集合
    """
    return {normalize_path(f) for f in files if f} 