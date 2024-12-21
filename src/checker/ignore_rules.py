"""
Ignore rules for excluding files from scanning
"""

import os
import fnmatch
from typing import List, Set

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
                        self.ignore_patterns.add(line)

    def should_ignore(self, file_path: str) -> bool:
        """检查文件是否应该被忽略

        Args:
            file_path: 文件路径

        Returns:
            是否应该被忽略
        """
        # 检查每个忽略模式
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False