"""
Utility functions for the Markdown reference checker
"""

import os
import re
from typing import Set

def normalize_path(path: str) -> str:
    """规范化路径，处理路径分隔符"""
    # 统一使用正斜杠
    path = path.replace('\\', '/')
    # 移除开头的 ./
    path = re.sub(r'^\./', '', path)
    return path

def is_image_file(filename: str) -> bool:
    """检查文件是否是图片文件"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
    return os.path.splitext(filename)[1].lower() in image_extensions

def is_markdown_file(filename: str) -> bool:
    """检查文件是否是Markdown文件"""
    return filename.lower().endswith('.md')

def get_valid_chars() -> Set[str]:
    """获取文件名中允许的字符集合"""
    return set('\u4e00\u9fff-_()（）[]【】') 