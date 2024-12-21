"""
Ignore rules handling for Markdown reference checker
"""

import os
import fnmatch
import re
from typing import List, Set
from .utils import normalize_path

class IgnoreRules:
    """忽略规则管理器"""

    def __init__(self, root_dir: str):
        """初始化忽略规则管理器。
        
        Args:
            root_dir: 根目录路径
        """
        self.root_dir = root_dir
        self.patterns = []  # 全局忽略模式
        self.ignore_rules = {}  # 每个目录的忽略规则
        
        # 加载默认规则
        self.add_patterns([
            '*.tmp',
            '*.temp',
            '*.swp',
            '*.bak',
            '*.log',
            '.git/',
            '.svn/',
            '.DS_Store',
            'node_modules/',
            '__pycache__/',
            '.pytest_cache/',
            '.coverage'
        ])
        
        # 加载.gitignore文件
        gitignore_path = os.path.join(root_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                self.add_patterns(f.read().splitlines())
                
        # 加载.mdignore文件
        mdignore_path = os.path.join(root_dir, '.mdignore')
        if os.path.exists(mdignore_path):
            with open(mdignore_path, 'r', encoding='utf-8') as f:
                self.add_patterns(f.read().splitlines())
    
    def add_patterns(self, patterns: List[str]) -> None:
        """添加忽略模式。
        
        Args:
            patterns: 忽略模式列表
        """
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern and not pattern.startswith('#'):
                self.patterns.append(pattern)
                self.ignore_rules.setdefault('', []).append(re.compile(fnmatch.translate(pattern)))
    
    def should_ignore(self, path: str) -> bool:
        """检查路径是否应该被忽略。
        
        Args:
            path: 要检查的路径
            
        Returns:
            是否应该忽略
        """
        # 规范化路径
        path = normalize_path(path)
        
        # 检查每个目录层级的规则
        current_path = ''
        parts = path.split('/')
        
        for part in parts:
            if current_path:
                current_path += '/'
            current_path += part
            
            # 检查当前目录的规则
            if current_path in self.ignore_rules:
                for pattern in self.ignore_rules[current_path]:
                    if pattern.match(path):
                        return True
        
        # 检查根目录的规则
        if '' in self.ignore_rules:
            for pattern in self.ignore_rules['']:
                if pattern.match(path):
                    return True
        
        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """检查路径是否匹配模式

        Args:
            path: 要检查的路径
            pattern: 忽略模式

        Returns:
            bool: 是否匹配
        """
        # 移除开头的斜杠
        if pattern.startswith('/'):
            pattern = pattern[1:]
        if path.startswith('/'):
            path = path[1:]

        # 处理目录匹配
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if not os.path.isdir(os.path.join(self.root_dir, path)):
                return False

        # 处理通配符
        pattern = pattern.replace('.', r'\.')
        pattern = pattern.replace('*', '[^/]*')
        pattern = pattern.replace('?', '[^/]')

        # 处理目录通配符
        if '**/' in pattern:
            pattern = pattern.replace('**/', '.*')
        elif '*/' in pattern:
            pattern = pattern.replace('*/', '[^/]*/') 

        # 添加开头和结尾的锚点
        pattern = f'^{pattern}$'

        return bool(re.match(pattern, path))
    
    def _parse_ignore_file(self, content: str) -> List[str]:
        """解析.gitignore文件内容为忽略规则列表

        Args:
            content: .gitignore文件内容

        Returns:
            List[str]: 忽略规则列表
        """
        patterns = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
        return patterns