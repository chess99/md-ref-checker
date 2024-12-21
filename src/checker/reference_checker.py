"""
Main reference checker class for Markdown reference checker
"""

import os
import re
from collections import defaultdict
from typing import Dict, Set, List, Tuple, DefaultDict, Optional, Union
from .utils import normalize_path, is_markdown_file
from .ignore_rules import IgnoreRules
from .file_scanner import FileScanner
from .path_resolver import PathResolver
from .reference_parser import ReferenceParser

class ReferenceChecker:
    """Markdown引用检查器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.ignore_rules = IgnoreRules(self.root_dir)
        self.file_scanner = FileScanner(self.root_dir, self.ignore_rules)
        self.path_resolver = PathResolver(self.file_scanner)
        self.parser = ReferenceParser()
        
        self.invalid_links: List[Tuple[str, Tuple[str, str, bool, Optional[str]]]] = []
        self.unidirectional_links: List[Tuple[str, str]] = []
        self.reference_stats: DefaultDict[str, Dict[str, Set[str]]] = \
            defaultdict(lambda: {"incoming": set(), "outgoing": set()})
        self.referenced_images: Set[str] = set()
    
    def scan_files(self) -> None:
        """扫描文件系统"""
        self.file_scanner.scan()
    
    def check_file(self, file_path: str) -> Tuple[List[Tuple[str, int, int, str]], Set[str]]:
        """检查单个文件中的引用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            invalid = []
            all_links = set()
            rel_path = os.path.relpath(file_path, self.root_dir)
            current_file = self.normalize_path(rel_path)
            
            # 如果当前文件应该被忽略，则跳过检查
            if self.ignore_rules.should_ignore(current_file):
                return [], set()
            
            in_code_block = False
            current_line = 0
            
            while current_line < len(lines):
                line = lines[current_line]
                
                # 检查是否进入或离开代码块
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    current_line += 1
                    continue
                
                # 在代码块内跳过处理
                if in_code_block:
                    current_line += 1
                    continue
                
                # 处理当前行的引用
                refs = ReferenceParser.find_references_in_text(line, current_line + 1)
                for link, line_num, col, line_content, is_image in refs:
                    resolved_link = self.path_resolver.resolve_link(link, current_file, is_image)
                    # 如果引用文件应该被忽略，则跳过检查
                    if self.ignore_rules.should_ignore(resolved_link):
                        continue
                    all_links.add(resolved_link)
                    if resolved_link not in self.file_scanner.files:
                        invalid.append((link, line_num, col, line_content))
                
                current_line += 1
            
            return invalid, all_links
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return [], set()
    
    def check_all_references(self) -> None:
        """检查所有引用"""
        self.invalid_links.clear()
        self.referenced_images.clear()
        
        # 初始化引用统计
        self.reference_stats = {}
        for file in self.files:
            if file.endswith('.md'):
                self.reference_stats[file] = {
                    'outgoing': set(),
                    'incoming': set()
                }
        
        # 检查每个Markdown文件中的引用
        for file in self.files:
            if file.endswith('.md'):
                self._check_file_references(file)
                
        # 更新incoming引用
        for file, stats in self.reference_stats.items():
            for target in stats['outgoing']:
                if target in self.reference_stats:
                    self.reference_stats[target]['incoming'].add(file)
    
    def _check_file_references(self, file_path: str) -> None:
        """检查单个文件中的引用。
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析引用
            references = self.parser.parse_references(content)
            for link, is_image in references:
                resolved_link = self.path_resolver.resolve_link(link, file_path, is_image)
                
                # 如果引用文件应该被忽略，则跳过检查
                if self.ignore_rules.should_ignore(resolved_link):
                    continue
                
                if is_image:
                    if resolved_link.startswith('assets/'):
                        self.referenced_images.add(resolved_link)
                    # 检查图片是否存在
                    if resolved_link not in self.file_scanner.image_files:
                        self.invalid_links.append((file_path, (link, resolved_link, is_image, None)))
                else:
                    # 只统计 Markdown 文件之间的引用
                    if resolved_link.endswith('.md'):
                        self.reference_stats[file_path]['outgoing'].add(resolved_link)
                        # 检查文件是否存在
                        if resolved_link not in self.file_scanner.files:
                            self.invalid_links.append((file_path, (link, resolved_link, is_image, None)))
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            full_path = os.path.join(self.root_dir, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def print_report(self, verbosity: int = 0, no_color: bool = False) -> None:
        """打印检查报告"""
        # 颜色代码
        red = '' if no_color else '\x1b[31m'
        yellow = '' if no_color else '\x1b[33m'
        reset = '' if no_color else '\x1b[0m'
        
        if self.invalid_links:
            error_count = len(self.invalid_links)
            for file_path, (link, line, col, line_content) in self.invalid_links:
                print(f"{red}{file_path}:{line}:{col}  error  无效引用 '{link}'{reset}")
                print(f"  {line_content}")
                print(f"  {red}{' ' * (col-1)}^{reset}")
            print(f"\n✖ 发现 {error_count} 个无效引用")
        
        # 检查未被引用的图片
        unused_images = self.file_scanner.image_files - self.path_resolver.referenced_images
        if unused_images:
            if self.invalid_links:
                print()  # 添加空行分隔
            print(f"{yellow}未被引用的图片文件:{reset}")
            for image in sorted(unused_images):
                print(f"  {image}")
            print(f"\n⚠ 发现 {len(unused_images)} 个未被引用的图片文件")
        
        if verbosity >= 1 and self.unidirectional_links:
            print("\n单向链接:")
            for source, target in self.unidirectional_links:
                print(f"  {source} -> {target}")
        
        if verbosity >= 2:
            print("\n引用统计:")
            for file, stats in sorted(self.reference_stats.items()):
                if stats['incoming'] or stats['outgoing']:
                    print(f"\n  {file}:")
                    print(f"  - 被引用次数: {len(stats['incoming'])}")
                    print(f"  - 引用其他文件数: {len(stats['outgoing'])}")
                    if stats['outgoing']:
                        print("  - 引用的文件:")
                        for target in sorted(stats['outgoing']):
                            print(f"    * {target}")
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """规范化路径，处理���径分隔符"""
        # 统一使用正斜杠
        path = path.replace('\\', '/')
        # 移除开头的 ./
        path = re.sub(r'^\./', '', path)
        return path 