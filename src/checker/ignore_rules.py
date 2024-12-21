"""
Ignore rules handling for Markdown reference checker
"""

import os
import fnmatch
from typing import List, Set
from .utils import normalize_path

class IgnoreRules:
    """处理文件忽略规则"""
    
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.patterns: Set[str] = set()
        self._load_default_patterns()
        self._load_gitignore()
        self._load_mdignore()
    
    def _load_default_patterns(self) -> None:
        """加载默认的忽略模式"""
        default_patterns = {
            '.git/*',
            '.obsidian/*',
            '.trash/*',
            'node_modules/*',
            '.DS_Store',
            'Thumbs.db',
        }
        self.patterns.update(default_patterns)
    
    def _load_gitignore(self) -> None:
        """加载.gitignore文件中的规则"""
        gitignore_path = os.path.join(self.root_dir, '.gitignore')
        self._load_ignore_file(gitignore_path)
    
    def _load_mdignore(self) -> None:
        """加载.mdignore文件中的规则"""
        mdignore_path = os.path.join(self.root_dir, '.mdignore')
        self._load_ignore_file(mdignore_path)
    
    def _load_ignore_file(self, file_path: str) -> None:
        """从文件加载忽略规则"""
        if not os.path.exists(file_path):
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.patterns.add(line)
        except Exception as e:
            print(f"Warning: Error reading {os.path.basename(file_path)}: {e}")
    
    def add_patterns(self, patterns: List[str]) -> None:
        """添加新的忽略模式"""
        self.patterns.update(patterns)
    
    def should_ignore(self, path: str) -> bool:
        """检查文件是否应该被忽略"""
        path = normalize_path(path)
        
        # 移除开头的 ./
        if path.startswith('./'):
            path = path[2:]
        
        for pattern in self.patterns:
            # 规范化模式
            pattern = pattern.replace('\\', '/')
            if pattern.startswith('./'):
                pattern = pattern[2:]
            if pattern.endswith('/'):
                pattern = pattern[:-1]
            
            # 处理目录通配符模式
            if pattern.endswith('/*'):
                dir_pattern = pattern[:-1]
                if path.startswith(dir_pattern):
                    return True
            
            # 处理文件通配符
            elif '*' in pattern:
                # 处理 **/ 模式
                if '**/' in pattern:
                    pattern = pattern.replace('**/', '')
                    if fnmatch.fnmatch(os.path.basename(path), pattern):
                        return True
                # 普通通配符匹配
                elif fnmatch.fnmatch(path, pattern):
                    return True
            
            # 处理目录模式
            elif os.path.isdir(os.path.join(self.root_dir, pattern)):
                if path == pattern or path.startswith(pattern + '/'):
                    return True
            
            # 精确匹配
            elif path == pattern:
                return True
            
            # 处理前缀匹配
            elif pattern.endswith('_*') and os.path.basename(path).startswith(pattern[:-1]):
                return True
        
        return False 