"""
File scanning functionality for Markdown reference checker
"""

import os
from typing import Dict, Set, List
from .utils import normalize_path, is_image_file, is_markdown_file, get_file_name
from .ignore_rules import IgnoreRules
from collections import defaultdict

class FileScanner:
    """文件扫描器"""

    def __init__(self, root_dir: str, ignore_rules: IgnoreRules):
        """初始化文件扫描器

        Args:
            root_dir: 根目录路径
            ignore_rules: 忽略规则
        """
        self.root_dir = root_dir
        self.ignore_rules = ignore_rules
        self.files: Set[str] = set()
        self.file_names: Set[str] = set()

    def scan(self) -> None:
        """扫描文件"""
        self.files.clear()
        self.file_names.clear()

        for root, _, files in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == '.':
                rel_root = ''

            for file in files:
                rel_path = os.path.join(rel_root, file).replace('\\', '/')
                if not self.ignore_rules.should_ignore(rel_path):
                    self.files.add(rel_path)
                    name = get_file_name(file)
                    self.file_names.add(name)

    def rescan(self) -> None:
        """重新扫描文件"""
        self.scan()

    @property
    def markdown_files(self) -> Set[str]:
        """获取所有 Markdown 文件

        Returns:
            Markdown 文件集合
        """
        return {f for f in self.files if is_markdown_file(f)}

    @property
    def image_files(self) -> Set[str]:
        """获取所有图片文件

        Returns:
            图片文件集合
        """
        return {f for f in self.files if is_image_file(f)}

    def get_file_mapping(self, file_name: str = None) -> Dict[str, List[str]]:
        """获取文件名到文件路径的映射

        Args:
            file_name: 要查找的文件名,如果为 None 则返回所有映射

        Returns:
            文件名到文件路径的映射
        """
        mapping = defaultdict(list)
        for file in self.files:
            name = get_file_name(file)
            mapping[name].append(file)

        if file_name is not None:
            # 如果指定了文件名,返回该文件名对应的路径列表
            if file_name in self.files:
                return {file_name: [file_name]}
            name = get_file_name(file_name)
            return {name: mapping[name]} if name in mapping else {}

        return mapping