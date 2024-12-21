"""
Test utilities for md-ref-checker
"""

import os
import shutil
from typing import List, Dict, Any

def create_test_files(test_dir: str, files: Dict[str, str]) -> None:
    """创建测试文件
    
    Args:
        test_dir: 测试目录路径
        files: 文件路径到文件内容的映射
    """
    for path, content in files.items():
        full_path = os.path.join(test_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

def create_test_structure(test_dir: str, structure: Dict[str, Any]) -> None:
    """创建测试目录结构
    
    Args:
        test_dir: 测试目录路径
        structure: 目录结构配置
    """
    # 创建基本目录
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建文件和子目录
    for name, content in structure.items():
        path = os.path.join(test_dir, name)
        if isinstance(content, str):
            # 如果是字符串，创建文件
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif isinstance(content, dict):
            # 如果是字典，递归创建子目录
            create_test_structure(path, content)
        elif content is None:
            # 如果是None，创建空目录
            os.makedirs(path, exist_ok=True)

def cleanup_test_dir(test_dir: str) -> None:
    """清理测试目录
    
    Args:
        test_dir: 测试目录路径
    """
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def create_ignore_file(test_dir: str, filename: str, patterns: List[str]) -> None:
    """创建忽略规则文件
    
    Args:
        test_dir: 测试目录路径
        filename: 忽略规则文件名（.gitignore 或 .mdignore）
        patterns: 忽略规则列表
    """
    path = os.path.join(test_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        for pattern in patterns:
            f.write(f"{pattern}\n") 