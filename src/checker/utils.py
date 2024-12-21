"""
Utility functions for Markdown reference checker
"""

import os
from typing import Set

def normalize_path(path: str) -> str:
    """标准化路径，统一使用正斜杠"""
    return path.replace('\\', '/')

def is_markdown_file(filename: str) -> bool:
    """判断是否为 Markdown 文件"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in {'.md', '.markdown'}

def is_image_file(filename: str) -> bool:
    """判断是否为图片文件"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}

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