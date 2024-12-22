"""Markdown reference checker implementation."""

import os
from typing import Dict, Optional, Set

from .models import CheckResult, Reference
from .parsers import MarkdownParser
from .utils import FileSystem


class ReferenceChecker:
    """Main reference checker class."""

    def __init__(self, root_dir: str, debug: bool = False) -> None:
        """Initialize with root directory."""
        self.fs = FileSystem(root_dir, debug=debug)
        self.parser = MarkdownParser()
        self.file_refs: Dict[str, Set[Reference]] = {}  # 文件到其引用的映射
        self.image_refs: Set[str] = set()  # 所有被引用的图片

    def _resolve_reference(self, ref: Reference) -> Optional[str]:
        """Resolve a reference to its actual file path."""
        # 获取引用文件的目录
        source_dir = os.path.dirname(ref.source_file)

        # 生成父目录路径列表
        parent_paths = []
        if source_dir:
            parts = source_dir.split(os.path.sep)
            for i in range(len(parts)):
                parent_path = os.path.normpath(
                    os.path.join(*(["."] + [".."] * i), ref.target)
                )
                parent_paths.append(parent_path)

        # 尝试不同的路径组合
        possible_paths = [
            # 相对于源文件的路径（保持原始路径）
            ref.target,
            # 相对于源文件的路径（规范化）
            os.path.normpath(os.path.join(source_dir, ref.target)),
            # 如果是图片，尝试在assets目录下查找
            os.path.join("assets", ref.target) if ref.is_image else None,
            # 尝试在根目录查找
            os.path.basename(ref.target),
        ]

        # 添加父目录路径
        possible_paths.extend(parent_paths)

        # 如果是简单引用（没有路径分隔符），在每个目录中递归查找
        if not any(sep in ref.target for sep in ["/", "\\"]):
            for root, _, _files in os.walk(self.fs.root_dir):
                rel_root = os.path.relpath(root, self.fs.root_dir)
                if rel_root == ".":
                    rel_root = ""

                # 跳过被忽略的目录
                if self.fs.should_ignore(rel_root):
                    continue

                # 添加当前目录下的可能路径
                possible_paths.append(os.path.join(rel_root, ref.target))

        # 尝试不同的扩展名
        extensions = (
            [".md"]
            if not ref.is_image
            else ["", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
        )

        for path in possible_paths:
            if not path:
                continue

            # 规范化路径
            path = self.fs.normalize_path(path)

            # 如果路径已经有扩展名，直接检查
            if os.path.splitext(path)[1]:
                if self.fs.file_exists(path) and not self.fs.should_ignore(path):
                    return path
                continue

            # 尝试不同的扩展名
            for ext in extensions:
                full_path = path + ext
                if self.fs.file_exists(full_path) and not self.fs.should_ignore(
                    full_path
                ):
                    return self.fs.normalize_path(full_path)

        return None

    def check_file(self, file_path: str) -> CheckResult:
        """Check references in a single file."""
        result = CheckResult()

        # 如果文件应该被忽略，返回空结果
        if self.fs.should_ignore(file_path):
            return result

        # 读取文件内容
        content = self.fs.read_file(file_path)
        if not content:
            return result

        # 解析引用
        refs = list(self.parser.parse_references(file_path, content))
        self.file_refs[file_path] = set(refs)

        # 检查每个引用
        for ref in refs:
            # 检查目标路径是否应该被忽略
            target_path = os.path.normpath(
                os.path.join(os.path.dirname(file_path), ref.target)
            )
            if self.fs.should_ignore(target_path):
                result.add_invalid_ref(ref)
                continue

            resolved_path = self._resolve_reference(ref)
            if not resolved_path:
                # 引用无效
                result.add_invalid_ref(ref)
            elif ref.is_image:
                # 记录图片引用
                self.image_refs.add(resolved_path)

        return result

    def check_directory(self) -> CheckResult:
        """Check all Markdown files in the directory."""
        result = CheckResult()
        self.file_refs.clear()
        self.image_refs.clear()

        # 查找所有Markdown文件
        for file_path in self.fs.find_files(pattern="*.md"):
            file_result = self.check_file(file_path)
            result = result.merge(file_result)

        # 查找未使用的图片
        image_patterns = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp")
        all_images = set(self.fs.find_files(pattern=image_patterns))
        unused_images = all_images - self.image_refs
        for image in unused_images:
            result.add_unused_image(image)

        # 检查单向链接
        for source_file, refs in self.file_refs.items():
            for ref in refs:
                if ref.is_image:
                    continue

                resolved_path = self._resolve_reference(ref)
                if resolved_path and resolved_path in self.file_refs:
                    # 检查是否有反向链接
                    has_back_ref = any(
                        r.target in (source_file, os.path.splitext(source_file)[0])
                        for r in self.file_refs[resolved_path]
                    )
                    if not has_back_ref:
                        result.add_unidirectional_link(source_file, resolved_path)

        return result
