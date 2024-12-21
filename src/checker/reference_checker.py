"""
Main reference checker class for Markdown reference checker
"""

import os
import sys
from collections import defaultdict
from typing import Dict, Set, List, Tuple, DefaultDict
from .utils import normalize_path, is_markdown_file, is_image_file
from .ignore_rules import IgnoreRules
from .file_scanner import FileScanner
from .path_resolver import PathResolver
from .reference_parser import ReferenceParser

class ReferenceChecker:
    """引用检查器"""

    def __init__(self, root_dir: str):
        """初始化引用检查器

        Args:
            root_dir: 根目录路径
        """
        self.root_dir = root_dir
        self.file_scanner = FileScanner(root_dir, IgnoreRules(root_dir))
        self.path_resolver = PathResolver(root_dir)
        self.reference_parser = ReferenceParser()
        self.reference_stats: DefaultDict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: {'outgoing': set(), 'incoming': set()}
        )
        self.invalid_links: List[Tuple[str, str, str, bool]] = []
        self.image_files: Set[str] = set()
        self.referenced_images: Set[str] = set()

    def scan_files(self) -> None:
        """扫描文件"""
        self.file_scanner.scan()
        self.image_files = {f for f in self.file_scanner.files if is_image_file(f)}

    def check_all_references(self) -> None:
        """检查所有引用"""
        # 初始化引用统计
        self.reference_stats.clear()
        self.referenced_images.clear()
        self.invalid_links.clear()
        
        for file in self.file_scanner.files:
            if is_markdown_file(file):
                self.reference_stats[file] = {
                    'outgoing': set(),
                    'incoming': set()
                }

        # 检查每个 Markdown 文件中的引用
        for file in self.file_scanner.files:
            if is_markdown_file(file):
                self._check_file_references(file)

    def _check_file_references(self, file_path: str) -> None:
        """检查单个文件中的引用

        Args:
            file_path: 文件路径
        """
        try:
            with open(os.path.join(self.root_dir, file_path), 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            return

        # 解析引用
        references = self.reference_parser.parse_references(content)

        # 检查每个引用
        for ref, is_image in references:
            resolved = self.path_resolver.resolve_link(ref, file_path, is_image)
            
            if is_image:
                # 检查图片是否存在
                img_path = os.path.join(self.root_dir, resolved)
                if os.path.exists(img_path):
                    self.referenced_images.add(resolved)
                else:
                    # 尝试在 assets 目录中查找
                    assets_path = os.path.join('assets', os.path.basename(resolved))
                    assets_path = assets_path.replace('\\', '/')
                    if os.path.exists(os.path.join(self.root_dir, assets_path)):
                        self.referenced_images.add(assets_path)
                    else:
                        self.invalid_links.append((ref, file_path, resolved, True))
            else:
                # 更新引用统计
                if resolved.endswith('.md'):
                    resolved_path = resolved
                else:
                    resolved_path = resolved + '.md'
                
                if os.path.exists(os.path.join(self.root_dir, resolved_path)):
                    self.reference_stats[file_path]['outgoing'].add(resolved_path)
                    self.reference_stats[resolved_path]['incoming'].add(file_path)
                else:
                    self.invalid_links.append((ref, file_path, resolved, False))

    def print_report(self, verbosity: int = 1, no_color: bool = False) -> None:
        """打印报告

        Args:
            verbosity: 详细程度
            no_color: 是否禁用颜色
        """
        # 打印无效引用
        if self.invalid_links:
            print("\nInvalid references:")
            for ref, source, resolved, is_image in self.invalid_links:
                print(f"  - {ref} in {source} -> {resolved}")

        # 打印未使用的图片
        unused_images = self.image_files - self.referenced_images
        if unused_images and verbosity > 1:
            print("\nUnused images:")
            for image in sorted(unused_images):
                print(f"  - {image}")

        # 打印引用统计
        if verbosity > 1:
            print("\nReference statistics:")
            for file in sorted(self.reference_stats.keys()):
                stats = self.reference_stats[file]
                print(f"\n{file}:")
                print(f"  Outgoing: {len(stats['outgoing'])}")
                print(f"  Incoming: {len(stats['incoming'])}")
                if verbosity > 2:
                    if stats['outgoing']:
                        print("  Outgoing references:")
                        for ref in sorted(stats['outgoing']):
                            print(f"    - {ref}")
                    if stats['incoming']:
                        print("  Incoming references:")
                        for ref in sorted(stats['incoming']):
                            print(f"    - {ref}")

        # 打印总结
        print("\nSummary:")
        print(f"  Total files: {len(self.file_scanner.files)}")
        print(f"  Markdown files: {sum(1 for f in self.file_scanner.files if is_markdown_file(f))}")
        print(f"  Image files: {len(self.image_files)}")
        print(f"  Invalid references: {len(self.invalid_links)}")
        print(f"  Unused images: {len(unused_images)}")

    def resolve_link(self, link: str, source_file: str, is_image: bool = False) -> str:
        """解析链接

        Args:
            link: 链接路径
            source_file: 源文件路径
            is_image: 是否为图片链接

        Returns:
            解析后的路径
        """
        return self.path_resolver.resolve_link(link, source_file, is_image)