"""
Main reference checker class for Markdown reference checker
"""

import os
import sys
from typing import Set
from .models import Reference, ReferenceStats, Config, FileAccessError
from .ignore_rules import IgnoreRules
from .file_scanner import FileScanner
from .path_resolver import PathResolver
from .reference_parser import ReferenceParser
from .report import ReportGenerator

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
        """
        # 扫描文件
        self.file_scanner.scan()
        self.image_files = self.file_scanner.image_files

        # 检查每个 Markdown 文件中的引用
        for file in self.file_scanner.markdown_files:
            self._check_file_references(file)

        return self.stats

    def _check_file_references(self, file_path: str) -> None:
        """检查单个文件中的引用

        Args:
            file_path: 文件路径

        Raises:
            FileAccessError: 文件访问错误
        """
        try:
            with open(os.path.join(self.config.root_dir, file_path), 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise FileAccessError(f"Error reading file {file_path}: {str(e)}")

        # 解析引用
        references = self.reference_parser.parse_references(content)

        # 检查每个引用
        for ref_target, is_image in references:
            resolved = self.path_resolver.resolve_link(ref_target, file_path, is_image)
            ref = Reference(
                source=file_path,
                target=ref_target,
                is_image=is_image,
                resolved_path=resolved
            )
            
            if is_image:
                # 检查图片是否存在
                img_path = os.path.join(self.config.root_dir, resolved)
                if os.path.exists(img_path):
                    self.stats.referenced_images.add(resolved)
                else:
                    # 尝试在 assets 目录中查找
                    assets_path = os.path.join('assets', os.path.basename(resolved))
                    assets_path = assets_path.replace('\\', '/')
                    if os.path.exists(os.path.join(self.config.root_dir, assets_path)):
                        self.stats.referenced_images.add(assets_path)
                        ref.resolved_path = assets_path
                    else:
                        ref.is_valid = False
                        self.stats.invalid_references.append(ref)
            else:
                # 更新引用统计
                if resolved.endswith('.md'):
                    resolved_path = resolved
                else:
                    resolved_path = resolved + '.md'
                
                if os.path.exists(os.path.join(self.config.root_dir, resolved_path)):
                    self.stats.outgoing[file_path].add(resolved_path)
                    self.stats.incoming[resolved_path].add(file_path)
                    ref.resolved_path = resolved_path
                else:
                    ref.is_valid = False
                    self.stats.invalid_references.append(ref)

    def print_report(self, output=sys.stdout) -> None:
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