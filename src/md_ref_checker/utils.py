"""File system utilities."""

import fnmatch
import os
import re
from typing import Dict, Iterator, List, Tuple, Union


class FileSystem:
    """File system operations handler."""

    def __init__(self, root_dir: str, debug: bool = False) -> None:
        """Initialize with root directory."""
        self.root_dir = os.path.abspath(root_dir)
        self.debug = debug
        self.ignore_patterns = self._load_ignore_patterns()
        self._file_exists_cache: Dict[str, bool] = {}
        self._dir_listing_cache: Dict[str, List[str]] = {}
        self._pattern_match_cache: Dict[Tuple[str, str], bool] = {}
        self._basename_cache: Dict[str, List[str]] = {}
        self._compiled_patterns: Dict[str, re.Pattern] = (
            {}
        )  # Cache for compiled patterns
        if self.debug:
            print(f"Loaded ignore patterns: {self.ignore_patterns}")

    def _clear_caches(self) -> None:
        """Clear all caches."""
        self._file_exists_cache.clear()
        self._dir_listing_cache.clear()
        self._pattern_match_cache.clear()
        self._basename_cache.clear()
        self._compiled_patterns.clear()

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

    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Convert a glob pattern to a regex pattern."""
        if pattern in self._compiled_patterns:
            return self._compiled_patterns[pattern]

        # Convert glob pattern to regex pattern
        regex = fnmatch.translate(pattern)
        compiled = re.compile(regex)
        self._compiled_patterns[pattern] = compiled
        return compiled

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match a path against a single pattern."""
        cache_key = (path, pattern)
        if cache_key in self._pattern_match_cache:
            return self._pattern_match_cache[cache_key]

        if self.debug:
            print(f"Matching path '{path}' against pattern '{pattern}'")

        # Handle root-relative patterns
        if pattern.startswith("/"):
            pattern = pattern[1:]
            if pattern.endswith("/"):
                pattern = pattern[:-1]
                result = path == pattern or path.startswith(pattern + "/")
            else:
                compiled = self._compile_pattern(pattern)
                result = bool(compiled.match(path))
            if self.debug:
                print(f"  Root pattern: {pattern} -> {result}")
            self._pattern_match_cache[cache_key] = result
            return result

        # Handle directory patterns
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            result = path == pattern or path.startswith(pattern + "/")
            if self.debug:
                print(f"  Directory pattern: {pattern} -> {result}")
            self._pattern_match_cache[cache_key] = result
            return result

        # Handle wildcard patterns
        if "*" in pattern:
            path_parts = path.split("/")
            pattern_parts = pattern.split("/")

            if len(pattern_parts) == 1:
                # Single-level pattern matches any level
                compiled = self._compile_pattern(pattern)
                result = any(bool(compiled.match(part)) for part in path_parts)
                if self.debug:
                    print(f"  Single-level wildcard: {pattern} -> {result}")
                self._pattern_match_cache[cache_key] = result
                return result
            else:
                # Multi-level pattern needs exact match
                compiled = self._compile_pattern(pattern)
                result = bool(compiled.match(path))
                if self.debug:
                    print(f"  Multi-level wildcard: {pattern} -> {result}")
                self._pattern_match_cache[cache_key] = result
                return result

        # Exact match
        result = path == pattern or path.startswith(pattern + "/")
        if self.debug:
            print(f"  Exact match: {pattern} -> {result}")
        self._pattern_match_cache[cache_key] = result
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

    def file_exists(self, rel_path: str) -> bool:
        """Check if a file exists."""
        if rel_path in self._file_exists_cache:
            return self._file_exists_cache[rel_path]

        abs_path = os.path.join(self.root_dir, rel_path)
        result = os.path.isfile(abs_path) and not self.should_ignore(rel_path)
        self._file_exists_cache[rel_path] = result
        return result

    def _get_dir_listing(self, dir_path: str) -> List[str]:
        """Get directory listing with caching."""
        if dir_path in self._dir_listing_cache:
            return self._dir_listing_cache[dir_path]

        try:
            files = sorted(os.listdir(dir_path))
            self._dir_listing_cache[dir_path] = files
            return files
        except OSError:
            self._dir_listing_cache[dir_path] = []
            return []

    def find_files(self, pattern: Union[str, Tuple[str, ...]] = "*") -> Iterator[str]:
        """Find files matching the pattern(s), respecting ignore rules."""
        patterns = (pattern,) if isinstance(pattern, str) else pattern

        # Clear caches before starting a new search
        self._clear_caches()

        for root, _, _ in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == ".":
                rel_root = ""

            # Check if directory should be ignored
            if self.should_ignore(rel_root):
                continue

            # Use cached directory listing
            for file in self._get_dir_listing(root):
                rel_path = os.path.join(rel_root, file)
                norm_path = self.normalize_path(rel_path)

                # Check if file should be ignored
                if self.should_ignore(norm_path):
                    continue

                # Check if matches pattern
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

    def _build_basename_cache(self) -> None:
        """Build cache of file basenames to their full paths."""
        if self._basename_cache:
            return

        for root, _, _ in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == "." or self.should_ignore(rel_root):
                continue

            for file in self._get_dir_listing(root):
                basename = os.path.splitext(file)[0]
                rel_path = os.path.join(rel_root, file)
                norm_path = self.normalize_path(rel_path)

                if not self.should_ignore(norm_path):
                    self._basename_cache.setdefault(basename, []).append(norm_path)

    def find_by_basename(self, basename: str) -> List[str]:
        """Find all files with a given basename."""
        self._build_basename_cache()
        return self._basename_cache.get(basename, [])
