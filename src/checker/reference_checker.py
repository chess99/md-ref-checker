"""
Main reference checker class for Markdown reference checker
"""

import os
from collections import defaultdict
from typing import Dict, Set, List, Tuple, DefaultDict

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
        
        self.invalid_links: List[Tuple[str, Tuple[str, int, int, str]]] = []
        self.unidirectional_links: List[Tuple[str, str]] = []
        self.reference_stats: DefaultDict[str, Dict[str, Union[int, Set[str]]]] = \
            defaultdict(lambda: {"incoming": 0, "outgoing": set()})
    
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
        """检查所有文件的引用"""
        self.scan_files()
        
        # 检查每个文件
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    norm_path = self.normalize_path(rel_path)
                    
                    # 如果文件应该被忽略，则跳过检查
                    if self.ignore_rules.should_ignore(norm_path):
                        continue
                    
                    invalid, outgoing = self.check_file(full_path)
                    
                    # 记录无效引用
                    for link_info in invalid:
                        self.invalid_links.append((norm_path, link_info))
                    
                    # 更新引用统计（只统计markdown文件，且排除被忽略的文件）
                    outgoing = {link for link in outgoing 
                              if link in self.file_scanner.files 
                              and not self.ignore_rules.should_ignore(link)}
                    self.reference_stats[norm_path]["outgoing"] = outgoing
                    for link in outgoing:
                        self.reference_stats[link]["incoming"] += 1
        
        # 检查单向链接（仅检查markdown文件之间的链接，且排除被忽略的文件）
        for source, data in self.reference_stats.items():
            if source in self.file_scanner.files and not self.ignore_rules.should_ignore(source):
                for target in data["outgoing"]:
                    if target in self.file_scanner.files \
                            and not self.ignore_rules.should_ignore(target) \
                            and source not in self.reference_stats[target]["outgoing"]:
                        self.unidirectional_links.append((source, target))
    
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
                if stats['incoming'] > 0 or stats['outgoing']:
                    print(f"\n  {file}:")
                    print(f"  - 被引用次数: {stats['incoming']}")
                    print(f"  - 引用其他文件数: {len(stats['outgoing'])}")
                    if stats['outgoing']:
                        print("  - 引用的文件:")
                        for target in sorted(stats['outgoing']):
                            print(f"    * {target}")
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """规范化路径，处理路径分隔符"""
        # 统一使用正斜杠
        path = path.replace('\\', '/')
        # 移除开头的 ./
        path = re.sub(r'^\./', '', path)
        return path 