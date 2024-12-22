"""Markdown reference checker implementation."""
import os
from typing import Dict, Set, List, Optional
from .models import Reference, CheckResult
from .utils import FileSystem
from .parsers import MarkdownParser


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
        
        # 尝试不同的路径组合
        possible_paths = [
            # 相对于源文件的路径
            os.path.normpath(os.path.join(source_dir, ref.target)),
            # 直接使用目标路径
            ref.target,
            # 如果是图片，尝试在assets目录下查找
            os.path.join("assets", ref.target) if ref.is_image else None,
        ]
        
        # 尝试不同的扩展名
        extensions = [".md"] if not ref.is_image else ["", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
        
        for path in possible_paths:
            if not path:
                continue
            
            # 如果路径已经有扩展名，直接检查
            if os.path.splitext(path)[1]:
                if self.fs.file_exists(path) and not self.fs.should_ignore(path):
                    return self.fs.normalize_path(path)
                continue
            
            # 尝试不同的扩展名
            for ext in extensions:
                full_path = path + ext
                if self.fs.file_exists(full_path) and not self.fs.should_ignore(full_path):
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
            target_path = os.path.normpath(os.path.join(os.path.dirname(file_path), ref.target))
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
