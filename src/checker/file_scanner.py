"""
File scanning functionality for Markdown reference checker
"""

import os
from typing import Dict, Set, List
from .utils import normalize_path, is_image_file, is_markdown_file
from .ignore_rules import IgnoreRules

class FileScanner:
    """文件扫描器，负责扫描和管理文件系统"""
    
    def __init__(self, root_dir: str, ignore_rules: IgnoreRules):
        self.root_dir = os.path.abspath(root_dir)
        self.ignore_rules = ignore_rules
        self.files: Set[str] = set()
        self.file_names: Set[str] = set()
        self.file_map: Dict[str, List[str]] = {}
        self.image_files: Set[str] = set()
    
    def scan(self) -> None:
        """扫描目录下的所有文件"""
        self.files.clear()
        self.file_names.clear()
        self.file_map.clear()
        self.image_files.clear()
        
        for root, _, files in os.walk(self.root_dir):
            # 获取相对路径
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == '.':
                rel_root = ''
            
            # 检查目录是否应该被忽略
            if self.ignore_rules.should_ignore(rel_root):
                continue
            
            for file in files:
                # 获取相对路径
                rel_path = os.path.join(rel_root, file)
                norm_path = normalize_path(rel_path)
                
                # 检查文件是否应该被忽略
                if self.ignore_rules.should_ignore(norm_path):
                    continue
                
                # 保存完整路径
                self.files.add(norm_path)
                
                # 保存不带扩展名的文件名和完整路径
                base_name = os.path.splitext(file)[0]
                base_path = os.path.splitext(norm_path)[0]
                self.file_names.add(base_name)
                
                # 记录文件名到实际文件的映射
                self._add_to_file_map(norm_path, norm_path)  # 完整路径映射
                self._add_to_file_map(base_path, norm_path)  # 不带扩展名的完整路径映射
                self._add_to_file_map(file, norm_path)       # 纯文件名映射（带扩展名）
                self._add_to_file_map(base_name, norm_path)  # 纯文件名映射（不带扩展名）
                
                # 记录图片文件
                if is_image_file(file):
                    self.image_files.add(norm_path)
    
    def _add_to_file_map(self, key: str, value: str) -> None:
        """添加文件映射"""
        if key not in self.file_map:
            self.file_map[key] = []
        if value not in self.file_map[key]:
            self.file_map[key].append(value)
    
    def get_file_mapping(self, key: str) -> List[str]:
        """获取文件映射"""
        return self.file_map.get(key, [])