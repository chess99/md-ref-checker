"""
Main reference checker class for Markdown reference checker
"""

import os
import sys
from typing import Set, Optional, TextIO
from .models import Reference, ReferenceStats, Config, FileAccessError, ParseError
from .ignore_rules import IgnoreRules
from .file_scanner import FileScanner
from .path_resolver import PathResolver
from .reference_parser import ReferenceParser
from .report import ReportGenerator
from .utils import normalize_path, is_image_file

class ReferenceChecker:
    """引用检查器"""

    def __init__(self, config: Config):
        """初始化引用检查器

        Args:
            config: 配置
        """
        self.config = config
        self.file_scanner = FileScanner(config.root_dir, IgnoreRules(config.root_dir))
        self.path_resolver = PathResolver(config.root_dir)
        self.reference_parser = ReferenceParser()
        self.stats = ReferenceStats()
        self.image_files: Set[str] = set()

    def check_references(self) -> ReferenceStats:
        """检查引用

        Returns:
            引用统计

        Raises:
            FileAccessError: 文件访问错误
            ParseError: 解析错误
        """
        try:
            # 扫描文件
            self.file_scanner.scan()
            self.image_files = self.file_scanner.image_files

            # 检查每个 Markdown 文件中的引用
            for file in self.file_scanner.markdown_files:
                try:
                    self._check_file_references(file)
                except (FileAccessError, ParseError) as e:
                    print(f"Error processing file {file}: {str(e)}", file=sys.stderr)

            return self.stats
        except Exception as e:
            raise ParseError(f"Error checking references: {str(e)}")

    def _check_file_references(self, file_path: str) -> None:
        """检查单个文件中的引用

        Args:
            file_path: 文件路径

        Raises:
            FileAccessError: 文件访问错误
            ParseError: 解析错误
        """
        try:
            with open(os.path.join(self.config.root_dir, file_path), 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise FileAccessError(f"Error reading file {file_path}: {str(e)}")

        try:
            # 解析引用
            references = self.reference_parser.parse_references(content)
        except Exception as e:
            raise ParseError(f"Error parsing references in {file_path}: {str(e)}")

        # 检查每个引用
        for ref_target, is_image in references:
            resolved = self.path_resolver.resolve_link(ref_target, file_path, is_image)
            ref = Reference(
                source=file_path,
                target=ref_target,
                is_image=is_image,
                resolved_path=resolved
            )
            
            if is_image or is_image_file(ref_target):
                self._check_image_reference(ref)
            else:
                self._check_markdown_reference(ref)

    def _check_image_reference(self, ref: Reference) -> None:
        """检查图片引用

        Args:
            ref: 引用对象
        """
        # 检查原始路径
        img_path = os.path.join(self.config.root_dir, ref.resolved_path)
        if os.path.exists(img_path):
            self.stats.referenced_images.add(ref.resolved_path)
            ref.is_valid = True
            return

        # 检查 assets 目录
        assets_path = self._find_in_assets(ref.resolved_path)
        if assets_path:
            self.stats.referenced_images.add(assets_path)
            ref.resolved_path = assets_path
            ref.is_valid = True
            return

        # 检查搜索路径
        for search_path in self.config.search_paths:
            full_path = os.path.join(self.config.root_dir, search_path, os.path.basename(ref.resolved_path))
            if os.path.exists(full_path):
                resolved = normalize_path(os.path.join(search_path, os.path.basename(ref.resolved_path)))
                self.stats.referenced_images.add(resolved)
                ref.resolved_path = resolved
                ref.is_valid = True
                return

        # 如果都不存在，标记为无效引用
        ref.is_valid = False
        self.stats.invalid_references.append(ref)

    def _check_markdown_reference(self, ref: Reference) -> None:
        """检查 Markdown 引用

        Args:
            ref: 引用对象
        """
        # 确保有 .md 扩展名
        if ref.resolved_path.endswith('.md'):
            resolved_path = ref.resolved_path
        else:
            resolved_path = ref.resolved_path + '.md'
            ref.resolved_path = resolved_path

        # 检查文件是否存在
        if os.path.exists(os.path.join(self.config.root_dir, resolved_path)):
            self.stats.outgoing[ref.source].add(resolved_path)
            self.stats.incoming[resolved_path].add(ref.source)
            ref.is_valid = True
        else:
            ref.is_valid = False
            self.stats.invalid_references.append(ref)

    def _find_in_assets(self, image_path: str) -> Optional[str]:
        """在 assets 目录中查找图片

        Args:
            image_path: 图片路径

        Returns:
            找到的路径，如果未找到则返回 None
        """
        assets_path = os.path.join('assets', os.path.basename(image_path))
        assets_path = normalize_path(assets_path)
        if os.path.exists(os.path.join(self.config.root_dir, assets_path)):
            return assets_path
        return None

    def print_report(self, output: TextIO = sys.stdout) -> None:
        """打印报告

        Args:
            output: 输出流
        """
        report_generator = ReportGenerator(self.config, output)
        report_generator.generate_report(
            self.stats,
            len(self.file_scanner.files),
            len(self.image_files)
        )