"""Markdown reference checker implementation."""

import os
from typing import Dict, Optional, Set

from .models import CheckResult, Reference
from .parsers import MarkdownParser
from .utils import FileSystem


class ReferenceChecker:
    """Main reference checker class."""

    def __init__(
        self, root_dir: str, debug: bool = False, strict_image_refs: bool = False
    ) -> None:
        """Initialize with root directory.

        Args:
            root_dir: The root directory to check
            debug: Whether to enable debug output
            strict_image_refs: If True, only count ![[]] and ![] as image usage.
                             If False (default), also count [[]] as image usage.
        """
        self.fs = FileSystem(root_dir, debug=debug)
        self.parser = MarkdownParser()
        self.file_refs: Dict[str, Set[Reference]] = {}  # Map of file to its references
        self.image_refs: Set[str] = set()  # Set of all referenced image files
        self.strict_image_refs = strict_image_refs

    def _resolve_reference(self, ref: Reference) -> Optional[str]:
        """Resolve a reference to its actual file path.

        Resolution order for both links ([[...]]) and embeds (![[...]]):
        1. Try exact path with extension
        2. Try adding .md extension if no extension
        3. Try finding any file with the same basename in the same directory
        4. Try finding any file with the same basename in any directory
        """
        # Get the directory of the source file
        source_dir = os.path.dirname(ref.source_file)

        # Generate list of parent directory paths
        parent_paths = []
        if source_dir:
            parts = source_dir.split(os.path.sep)
            for i in range(len(parts)):
                parent_path = os.path.normpath(
                    os.path.join(*(["."] + [".."] * i), ref.target)
                )
                parent_paths.append(parent_path)

        # Try different path combinations
        possible_paths = [
            # Original path (keep as is)
            ref.target,
            # Path relative to source file (normalized)
            os.path.normpath(os.path.join(source_dir, ref.target)),
            # Try in root directory
            os.path.basename(ref.target),
        ]

        # Add parent directory paths
        possible_paths.extend(parent_paths)

        # If it's a simple reference (no path separators), recursively search in each directory
        if not any(sep in ref.target for sep in ["/", "\\"]):
            for root, _, _files in os.walk(self.fs.root_dir):
                rel_root = os.path.relpath(root, self.fs.root_dir)
                if rel_root == ".":
                    rel_root = ""

                # Skip ignored directories
                if self.fs.should_ignore(rel_root):
                    continue

                # Add possible path in current directory
                possible_paths.append(os.path.join(rel_root, ref.target))

        # Try each possible path
        for path in possible_paths:
            if not path:
                continue

            # Normalize path
            path = self.fs.normalize_path(path)
            basename = os.path.basename(path)
            dirname = (
                os.path.dirname(os.path.join(self.fs.root_dir, path))
                or self.fs.root_dir
            )

            # If path has extension, try it directly
            if os.path.splitext(path)[1]:
                if self.fs.file_exists(path):
                    return path
                continue

            # Try with .md extension first
            md_path = path + ".md"
            if self.fs.file_exists(md_path):
                return self.fs.normalize_path(md_path)

            # Try finding any file with the same basename in the same directory
            try:
                files = os.listdir(dirname)
                # Sort files to ensure consistent resolution order
                files.sort()
                for file in files:
                    if file.startswith(basename + "."):
                        rel_path = os.path.relpath(
                            os.path.join(dirname, file), self.fs.root_dir
                        )
                        if not self.fs.should_ignore(rel_path):
                            return self.fs.normalize_path(rel_path)
            except OSError:
                pass  # Directory might not exist

            # Try finding any file with the same basename in any directory
            for root, _, files in os.walk(self.fs.root_dir):
                if self.fs.should_ignore(os.path.relpath(root, self.fs.root_dir)):
                    continue
                # Sort files to ensure consistent resolution order
                files.sort()
                for file in files:
                    if file.startswith(basename + "."):
                        rel_path = os.path.relpath(
                            os.path.join(root, file), self.fs.root_dir
                        )
                        if not self.fs.should_ignore(rel_path):
                            return self.fs.normalize_path(rel_path)

        return None

    def check_file(self, file_path: str) -> CheckResult:
        """Check references in a single file."""
        result = CheckResult()

        # If file should be ignored, return empty result
        if self.fs.should_ignore(file_path):
            return result

        # Read file content
        content = self.fs.read_file(file_path)
        if not content:
            return result

        # Parse references
        refs = list(self.parser.parse_references(file_path, content))
        self.file_refs[file_path] = set(refs)

        # Check each reference
        for ref in refs:
            # Check if target path should be ignored
            target_path = os.path.normpath(
                os.path.join(os.path.dirname(file_path), ref.target)
            )
            if self.fs.should_ignore(target_path):
                result.add_invalid_ref(ref)
                continue

            # Try to resolve the reference
            resolved_path = self._resolve_reference(ref)
            if not resolved_path:
                # Reference is invalid
                result.add_invalid_ref(ref)
            elif self.fs.is_image_file(resolved_path):
                # Track image usage based on reference type and strict mode
                if not self.strict_image_refs or ref.is_embed:
                    self.image_refs.add(resolved_path)

        return result

    def check_directory(self) -> CheckResult:
        """Check all Markdown files in the directory."""
        result = CheckResult()
        self.file_refs.clear()
        self.image_refs.clear()

        # Find all Markdown files
        for file_path in self.fs.find_files(pattern="*.md"):
            file_result = self.check_file(file_path)
            result = result.merge(file_result)

        # Find unused images
        image_patterns = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp")
        all_images = set(self.fs.find_files(pattern=image_patterns))
        unused_images = all_images - self.image_refs
        for image in unused_images:
            result.add_unused_image(image)

        # Check for unidirectional links between markdown files
        for source_file, refs in self.file_refs.items():
            for ref in refs:
                resolved_path = self._resolve_reference(ref)
                if not resolved_path:
                    continue

                # Skip if the target is an image file
                if self.fs.is_image_file(resolved_path):
                    continue

                # Only check markdown files for unidirectional links
                if not resolved_path.endswith(".md"):
                    continue

                if resolved_path in self.file_refs:
                    # Check for back references
                    source_base = os.path.splitext(source_file)[0]
                    has_back_ref = any(
                        r.target in (source_file, source_base)
                        for r in self.file_refs[resolved_path]
                    )
                    if not has_back_ref:
                        result.add_unidirectional_link(source_file, resolved_path)

        return result
