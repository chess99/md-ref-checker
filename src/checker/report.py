"""
Report generation functionality
"""

from typing import TextIO
import sys
from .models import ReferenceStats, Config
from .utils import is_markdown_file

class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: Config, output: TextIO = sys.stdout):
        """初始化报告生成器

        Args:
            config: 配置
            output: 输出流
        """
        self.config = config
        self.output = output

    def generate_report(self, stats: ReferenceStats, file_count: int, image_count: int) -> None:
        """生成报告

        Args:
            stats: 引用统计
            file_count: 文件总数
            image_count: 图片文件数
        """
        # 打印无效引用
        if stats.invalid_references:
            self._print("\nInvalid references:")
            for ref in stats.invalid_references:
                self._print(f"  - {ref.target} in {ref.source} -> {ref.resolved_path or ref.target}")

        # 打印未使用的图片
        if self.config.verbosity > 1:
            self._print_unused_images(stats)
            self._print_reference_stats(stats)

        # 打印总结
        self._print("\nSummary:")
        self._print(f"  Total files: {file_count}")
        self._print(f"  Markdown files: {sum(1 for f in stats.outgoing.keys() if is_markdown_file(f))}")
        self._print(f"  Image files: {image_count}")
        self._print(f"  Invalid references: {len(stats.invalid_references)}")

    def _print_unused_images(self, stats: ReferenceStats) -> None:
        """打印未使用的图片

        Args:
            stats: 引用统计
        """
        unused_images = stats.referenced_images - set(ref.target for ref in stats.invalid_references if ref.is_image)
        if unused_images:
            self._print("\nUnused images:")
            for image in sorted(unused_images):
                self._print(f"  - {image}")

    def _print_reference_stats(self, stats: ReferenceStats) -> None:
        """打印引用统计

        Args:
            stats: 引用统计
        """
        self._print("\nReference statistics:")
        for file in sorted(stats.outgoing.keys()):
            self._print(f"\n{file}:")
            self._print(f"  Outgoing: {len(stats.outgoing[file])}")
            self._print(f"  Incoming: {len(stats.incoming[file])}")
            
            if self.config.verbosity > 2:
                if stats.outgoing[file]:
                    self._print("  Outgoing references:")
                    for ref in sorted(stats.outgoing[file]):
                        self._print(f"    - {ref}")
                if stats.incoming[file]:
                    self._print("  Incoming references:")
                    for ref in sorted(stats.incoming[file]):
                        self._print(f"    - {ref}")

    def _print(self, message: str) -> None:
        """打印消息

        Args:
            message: 消息内容
        """
        print(message, file=self.output) 