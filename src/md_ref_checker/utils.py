"""File system utilities."""

import fnmatch
import os
import re
from typing import Iterator, List, Tuple, Union


class FileSystem:
    """File system operations handler."""

    def __init__(self, root_dir: str, debug: bool = False) -> None:
        """Initialize with root directory."""
        self.root_dir = os.path.abspath(root_dir)
        self.debug = debug
        self.ignore_patterns = self._load_ignore_patterns()
        if self.debug:
            print(f"Loaded ignore patterns: {self.ignore_patterns}")

    def _clean_ignore_line(self, line: str) -> str:
        """Clean and validate an ignore pattern line."""
        # 移除注释
        line = line.split("#")[0].strip()

        # 跳过空行
        if not line:
            return ""

        # 移除开头的 ./
        if line.startswith("./"):
            line = line[2:]

        # 确保目录模式以/结尾
        if not line.endswith("/*") and os.path.isdir(os.path.join(self.root_dir, line)):
            line = line.rstrip("/") + "/"

        if self.debug:
            print(f"Cleaned ignore line: {line}")
        return line

    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from .gitignore and .mdignore."""
        patterns = [
            # 默认忽略的模式
            ".git/*",
            ".obsidian/*",
            ".trash/*",
            "node_modules/*",
            ".DS_Store",
            "Thumbs.db",
        ]

        def read_ignore_file(file_path: str) -> None:
            """Read patterns from an ignore file."""
            if os.path.exists(file_path):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        for line in f:
                            pattern = self._clean_ignore_line(line)
                            if pattern:
                                patterns.append(pattern)
                except Exception as e:
                    print(f"Warning: Error reading {os.path.basename(file_path)}: {e}")

        # 读取 .gitignore
        read_ignore_file(os.path.join(self.root_dir, ".gitignore"))

        # 读取 .mdignore
        read_ignore_file(os.path.join(self.root_dir, ".mdignore"))

        return patterns

    def normalize_path(self, path: str) -> str:
        """Normalize a path to use forward slashes and no leading ./."""
        # 统一使用正斜杠
        path = path.replace("\\", "/")
        # 移除开头的 ./
        path = re.sub(r"^\./", "", path)
        # 移除多余的斜杠
        path = re.sub(r"/+", "/", path)
        return path

    def is_markdown_file(self, path: str) -> bool:
        """Check if a path points to a Markdown file."""
        return path.lower().endswith(".md")

    def is_image_file(self, path: str) -> bool:
        """Check if a path points to an image file."""
        ext = os.path.splitext(path.lower())[1]
        return ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match a path against a single pattern."""
        if self.debug:
            print(f"Matching path '{path}' against pattern '{pattern}'")

        # 处理以/开头的模式（根目录相对路径）
        if pattern.startswith("/"):
            pattern = pattern[1:]
            # 如果模式以/结尾，表示目录
            if pattern.endswith("/"):
                pattern = pattern[:-1]
                result = path == pattern or path.startswith(pattern + "/")
            else:
                result = fnmatch.fnmatch(path, pattern)
            if self.debug:
                print(f"  Root pattern: {pattern} -> {result}")
            return result

        # 处理以/结尾的目录模式
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            result = path == pattern or path.startswith(pattern + "/")
            if self.debug:
                print(f"  Directory pattern: {pattern} -> {result}")
            return result

        # 处理通配符模式
        if "*" in pattern:
            # 对路径的每一部分都尝试匹配
            path_parts = path.split("/")
            pattern_parts = pattern.split("/")

            if len(pattern_parts) == 1:
                # 单层模式匹配任意层级
                result = any(fnmatch.fnmatch(part, pattern) for part in path_parts)
                if self.debug:
                    print(f"  Single-level wildcard: {pattern} -> {result}")
                return result
            else:
                # 多层模式需要完整匹配
                result = fnmatch.fnmatch(path, pattern)
                if self.debug:
                    print(f"  Multi-level wildcard: {pattern} -> {result}")
                return result

        # 精确匹配
        result = path == pattern or path.startswith(pattern + "/")
        if self.debug:
            print(f"  Exact match: {pattern} -> {result}")
        return result

    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored based on ignore patterns."""
        path = self.normalize_path(path)
        if self.debug:
            print(f"\nChecking if path should be ignored: {path}")

        for pattern in self.ignore_patterns:
            if not pattern:  # 跳过空模式
                continue

            if self._match_pattern(path, pattern):
                if self.debug:
                    print(f"  Ignoring path due to pattern: {pattern}")
                return True

        if self.debug:
            print("  Path not ignored")
        return False

    def find_files(self, pattern: Union[str, Tuple[str, ...]] = "*") -> Iterator[str]:
        """Find files matching the pattern(s), respecting ignore rules."""
        patterns = (pattern,) if isinstance(pattern, str) else pattern

        for root, _, files in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == ".":
                rel_root = ""

            # 检查目录是否应该被忽略
            if self.should_ignore(rel_root):
                continue

            for file in files:
                rel_path = os.path.join(rel_root, file)
                norm_path = self.normalize_path(rel_path)

                # 检查文件是否应该被忽略
                if self.should_ignore(norm_path):
                    continue

                # 检查是否匹配模式
                if any(fnmatch.fnmatch(file, p) for p in patterns):
                    yield norm_path

    def read_file(self, rel_path: str) -> str:
        """Read a file's contents."""
        abs_path = os.path.join(self.root_dir, rel_path)
        try:
            with open(abs_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {rel_path}: {e}")
            return ""

    def file_exists(self, rel_path: str) -> bool:
        """Check if a file exists."""
        abs_path = os.path.join(self.root_dir, rel_path)
        return os.path.isfile(abs_path)
