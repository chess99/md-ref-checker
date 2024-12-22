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
        self._resolution_cache: Dict[str, Optional[str]] = (
            {}
        )  # Cache for resolved paths
        self._ref_map: Dict[str, Set[str]] = {}  # Map of file to its referenced files

    def _resolve_reference(self, ref: Reference) -> Optional[str]:
        """Resolve a reference to its actual file path.

        Resolution order for both links ([[...]]) and embeds (![[...]]):
        1. Try exact path with extension
        2. Try adding .md extension if no extension (for non-image files)
        3. Try in assets directory (for image files)
        4. Try finding any file with the same basename in the same directory
        5. Try finding any file with the same basename in any directory
        """
        # Check cache first
        cache_key = f"{ref.source_file}:{ref.target}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]

        # Get the directory of the source file
        source_dir = os.path.dirname(ref.source_file)

        # Try different path combinations
        possible_paths = [
            # Original path (keep as is)
            ref.target,
            # Path relative to source file (normalized)
            os.path.normpath(os.path.join(source_dir, ref.target)),
            # Try in root directory
            os.path.basename(ref.target),
        ]

        # For image files, also try in assets directory
        if os.path.splitext(ref.target)[1].lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".webp",
        }:
            possible_paths.append(os.path.join("assets", os.path.basename(ref.target)))

        # Try each possible path
        for path in possible_paths:
            if not path:
                continue

            # Normalize path
            path = self.fs.normalize_path(path)

            # If path has extension, try it directly
            if os.path.splitext(path)[1]:
                if self.fs.file_exists(path):
                    self._resolution_cache[cache_key] = path
                    return path
                continue

            # Try with .md extension first (only for non-image files)
            if not any(
                ref.target.lower().endswith(ext)
                for ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
            ):
                md_path = path + ".md"
                if self.fs.file_exists(md_path):
                    resolved = self.fs.normalize_path(md_path)
                    self._resolution_cache[cache_key] = resolved
                    return resolved

            # Try finding any file with the same basename
            basename = os.path.basename(path)
            matches = self.fs.find_by_basename(basename)
            if matches:
                # Use the first match (they're sorted)
                self._resolution_cache[cache_key] = matches[0]
                return matches[0]

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

    def _build_ref_map(self) -> None:
        """Build a map of files to their referenced files."""
        self._ref_map.clear()
        for source_file, refs in self.file_refs.items():
            referenced_files = set()
            for ref in refs:
                resolved_path = self._resolve_reference(ref)
                if resolved_path and not self.fs.is_image_file(resolved_path):
                    referenced_files.add(resolved_path)
            self._ref_map[source_file] = referenced_files

    def check_directory(self) -> CheckResult:
        """Check all Markdown files in the directory."""
        result = CheckResult()
        self.file_refs.clear()
        self.image_refs.clear()
        self._resolution_cache.clear()
        self._ref_map.clear()

        # Find all Markdown files
        for file_path in self.fs.find_files(pattern="*.md"):
            file_result = self.check_file(file_path)
            result = result.merge(file_result)

        # Build reference map for faster unidirectional link checking
        self._build_ref_map()

        # Find unused images
        image_patterns = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp")
        all_images = set(self.fs.find_files(pattern=image_patterns))
        unused_images = all_images - self.image_refs
        for image in unused_images:
            result.add_unused_image(image)

        # Check for unidirectional links between markdown files
        for source_file, referenced_files in self._ref_map.items():
            for target_file in referenced_files:
                if target_file.endswith(".md"):
                    # Check for back references
                    source_base = os.path.splitext(source_file)[0]
                    target_refs = self._ref_map.get(target_file, set())
                    if (
                        source_file not in target_refs
                        and source_base not in target_refs
                    ):
                        result.add_unidirectional_link(source_file, target_file)

        return result
