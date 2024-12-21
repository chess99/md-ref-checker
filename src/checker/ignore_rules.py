"""
Ignore rules for excluding files from scanning
"""

import os
import fnmatch
from typing import List, Set
from .utils import normalize_path

class IgnoreRules:
    """忽略规则"""

    def __init__(self, root_dir: str):
        """初始化忽略规则

        Args:
            root_dir: 根目录路径
        """
        self.root_dir = root_dir
        self.ignore_patterns: Set[str] = {
            '.git/*',
            '.github/*',
            '.vscode/*',
            '.idea/*',
            'node_modules/*',
            '__pycache__/*',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.DS_Store',
            'Thumbs.db'
        }
        self._load_ignore_file()

    def _load_ignore_file(self) -> None:
        """加载 .mdignore 文件"""
        ignore_file = os.path.join(self.root_dir, '.mdignore')
        if os.path.exists(ignore_file):
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 处理目录模式
                        if line.endswith('/'):
                            line = line + '*'
                        # 处理通配符
                        if not any(c in line for c in '*?['):
                            if os.path.isdir(os.path.join(self.root_dir, line)):
                                line = line.rstrip('/') + '/*'
                            else:
                                line = line + '*'
                        self.ignore_patterns.add(line)

    def should_ignore(self, file_path: str) -> bool:
        """检查文件是否应该被忽略

        Args:
            file_path: 文件路径

        Returns:
            是否应该被忽略
        """
        # 规范化路径
        file_path = normalize_path(file_path)
        
        # 检查每个忽略模式
        for pattern in self.ignore_patterns:
            pattern = normalize_path(pattern)
            # 处理目录匹配
            if pattern.endswith('/*'):
                dir_pattern = pattern[:-2]
                if file_path.startswith(dir_pattern):
                    return True
            # 处理文件匹配
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False