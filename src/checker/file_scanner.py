"""
File scanning functionality for Markdown reference checker
"""

import os
from typing import Dict, Set, List
from .utils import normalize_path, is_image_file, is_markdown_file
from .ignore_rules import IgnoreRules
from collections import defaultdict

class FileScanner:
    """文件扫描器，负责扫描和管理文件系统"""
    
    def __init__(self, root_dir: str, ignore_rules: IgnoreRules):
        self.root_dir = os.path.abspath(root_dir)
        self.ignore_rules = ignore_rules
        self.files: Set[str] = set()
        self.file_names: Set[str] = set()
        self.file_map: Dict[str, Set[str]] = {}
        self.image_files: Set[str] = set()
    
    def scan(self) -> None:
        """扫描目录下的所有文件"""
        self.files.clear()
        self.image_files.clear()
        self.file_names.clear()
        self.file_map.clear()
        
        for root, _, files in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == '.':
                rel_root = ''
            
            # 检查目录是否应该被忽略
            if self.ignore_rules.should_ignore(rel_root):
                continue
            
            for file in files:
                # 获取相对路径
                rel_path = os.path.join(rel_root, file).replace('\\', '/')
                if rel_path.startswith('./'):
                    rel_path = rel_path[2:]
                
                # 检查是否应该忽略
                if self.ignore_rules.should_ignore(rel_path):
                    continue
                
                # 添加到文件集合
                self.files.add(rel_path)
                
                # 处理文件名映射
                name, ext = os.path.splitext(file)
                self.file_names.add(name)
                
                # 添加各种映射关系
                self._add_to_file_map(rel_path, rel_path)  # 完整路径映射
                self._add_to_file_map(name, rel_path)      # 基本文件名映射
                self._add_to_file_map(file, rel_path)      # 带扩展名的文件名映射
                
                # 如果是图片文件，添加到图片集合
                if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                    self.image_files.add(rel_path)
                    # 添加图片文件的特殊映射
                    if rel_path.startswith('assets/'):
                        base_name = os.path.basename(rel_path)
                        self._add_to_file_map(base_name, rel_path)
    
    def _add_to_file_map(self, key: str, value: str) -> None:
        """添加文件映射。
        
        Args:
            key: 映射键
            value: 映射值
        """
        if key not in self.file_map:
            self.file_map[key] = set()
        self.file_map[key].add(value)
    
    def get_file_mapping(self, key: str) -> List[str]:
        """获取文件映射"""
        return list(self.file_map.get(key, set()))