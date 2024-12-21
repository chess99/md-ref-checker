"""
Ignore rules handling for Markdown reference checker
"""

import os
import fnmatch
import re
from typing import List, Set, Dict
from .utils import normalize_path
import sys

class IgnoreRules:
    """忽略规则处理器"""

    def __init__(self, root_dir: str):
        """初始化忽略规则处理器

        Args:
            root_dir: 根目录路径
        """
        self.root_dir = root_dir
        self.patterns: Dict[str, List[str]] = {'': []}  # 按目录存储规则
        self._load_default_patterns()
        self._load_ignore_files()

    def _load_default_patterns(self) -> None:
        """加载默认忽略模式"""
        default_patterns = [
            '.*',           # 隐藏文件
            '*~',          # 临时文件
            '*.tmp',       # 临时文件
            '*.temp',      # 临时文件
            '*.swp',       # Vim 临时文件
            '*.swo',       # Vim 临时文件
            '__pycache__', # Python 缓存
            '*.pyc',       # Python 编译文件
            '.git/**',     # Git 目录
            '.svn/**',     # SVN 目录
            '.hg/**',      # Mercurial 目录
            '.DS_Store',   # macOS 系统文件
            'Thumbs.db',   # Windows 系统文件
            'node_modules/**', # Node.js 模块
            '.obsidian/**',    # Obsidian 配置
            '.trash/**',       # 回收站
            '.vscode/**'       # VSCode 配置
        ]
        self.patterns[''].extend(default_patterns)

    def _load_ignore_files(self) -> None:
        """加载忽略文件"""
        # 加载根目录的忽略文件
        for ignore_file in ['.gitignore', '.mdignore']:
            file_path = os.path.join(self.root_dir, ignore_file)
            if os.path.exists(file_path):
                self._load_ignore_file(file_path)

        # 加载子目录中的忽略文件
        for root, _, files in os.walk(self.root_dir):
            rel_dir = os.path.relpath(root, self.root_dir).replace('\\', '/')
            if rel_dir == '.':
                rel_dir = ''
            
            for file in files:
                if file in ['.gitignore', '.mdignore']:
                    ignore_file = os.path.join(root, file)
                    if rel_dir not in self.patterns:
                        self.patterns[rel_dir] = []
                    self._load_ignore_file(ignore_file, rel_dir)

    def _load_ignore_file(self, file_path: str, base_dir: str = '') -> None:
        """加载忽略文件

        Args:
            file_path: 忽略文件路径
            base_dir: 基准目录
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if base_dir:
                            pattern = os.path.join(base_dir, line).replace('\\', '/')
                            self.patterns[base_dir].append(line)
                        else:
                            pattern = line.replace('\\', '/')
                            self.patterns[''].append(pattern)
        except Exception as e:
            print(f"Error reading ignore file {file_path}: {e}", file=sys.stderr)

    def add_patterns(self, patterns: List[str]) -> None:
        """添加忽略模式

        Args:
            patterns: 忽略模式列表
        """
        self.patterns[''].extend(patterns)

    def should_ignore(self, path: str) -> bool:
        """检查是否应该忽略路径

        Args:
            path: 要检查的路径

        Returns:
            是否应该忽略
        """
        path = normalize_path(path)
        path_parts = self._get_path_parts(path)
        
        # 检查每个目录级别的规则
        current_path = ''
        for part in path_parts[:-1]:
            if current_path in self.patterns:
                for pattern in self.patterns[current_path]:
                    if self._match_pattern(pattern, path):
                        return True
            current_path = os.path.join(current_path, part).replace('\\', '/')
        
        # 检查文件所在目录的规则
        file_dir = os.path.dirname(path).replace('\\', '/')
        if file_dir in self.patterns:
            for pattern in self.patterns[file_dir]:
                if self._match_pattern(pattern, os.path.basename(path)):
                    return True
        
        # 检查根目录规则
        for pattern in self.patterns['']:
            if self._match_pattern(pattern, path):
                return True
        
        return False

    def _match_pattern(self, pattern: str, path: str) -> bool:
        """匹配模式

        Args:
            pattern: 忽略模式
            path: 要匹配的路径

        Returns:
            是否匹配
        """
        # 处理否定模式
        if pattern.startswith('!'):
            return not self._match_pattern(pattern[1:], path)

        # 处理目录匹配
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if not os.path.isdir(os.path.join(self.root_dir, path)):
                return False

        # 转换模式为正则表达式
        pattern = pattern.replace('.', r'\.')
        pattern = pattern.replace('*', r'[^/]*')
        pattern = pattern.replace('?', r'[^/]')
        pattern = f'^{pattern}$'

        return bool(re.match(pattern, path))

    def _get_path_parts(self, path: str) -> List[str]:
        """获取路径各部分

        Args:
            path: 路径

        Returns:
            路径各部分列表
        """
        parts = []
        while path:
            path, part = os.path.split(path)
            if part:
                parts.append(part)
            elif path:
                parts.append(path)
                break
        return list(reversed(parts))