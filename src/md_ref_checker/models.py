"""Data models for the Markdown reference checker."""

from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass(frozen=True)
class Reference:
    """Represents a reference in a Markdown file.

    Attributes:
        source_file: The file containing the reference
        target: The referenced file or resource
        line_number: Line number where the reference appears
        column: Column number where the reference starts
        line_content: The full line content containing the reference
        is_embed: Whether this is an embed reference (![[...]]) that embeds the target's
                content into the current document, rather than just a link reference ([[...]])
                that creates a clickable link
    """

    source_file: str
    target: str
    line_number: int
    column: int
    line_content: str
    is_embed: bool

    def __str__(self) -> str:
        """Return a string representation of the reference."""
        return f"{self.source_file}:{self.line_number}:{self.column} -> {self.target}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Reference):
            return NotImplemented
        return (
            self.source_file == other.source_file
            and self.target == other.target
            and self.line_number == other.line_number
            and self.column == other.column
            and self.line_content == other.line_content
            and self.is_embed == other.is_embed
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.source_file,
                self.target,
                self.line_number,
                self.column,
                self.line_content,
                self.is_embed,
            )
        )


@dataclass
class FileStats:
    """Statistics about references for a single file."""

    incoming_count: int = 0
    outgoing_refs: Set[Reference] = field(default_factory=set)

    def add_incoming_ref(self, ref: Reference) -> None:
        """Add an incoming reference."""
        self.incoming_count += 1

    def add_outgoing_ref(self, ref: Reference) -> None:
        """Add an outgoing reference."""
        self.outgoing_refs.add(ref)


@dataclass
class CheckResult:
    """Results of checking references in a directory."""

    invalid_refs: List[Reference] = field(default_factory=list)
    unused_images: Set[str] = field(default_factory=set)
    unidirectional_links: List[Tuple[str, str]] = field(default_factory=list)

    def add_invalid_ref(self, ref: Reference) -> None:
        """Add an invalid reference."""
        self.invalid_refs.append(ref)

    def add_unused_image(self, image_path: str) -> None:
        """Add an unused image."""
        self.unused_images.add(image_path)

    def add_unidirectional_link(self, source: str, target: str) -> None:
        """Add a unidirectional link."""
        self.unidirectional_links.append((source, target))

    def merge(self, other: "CheckResult") -> "CheckResult":
        """Merge another CheckResult into this one."""
        result = CheckResult()
        result.invalid_refs.extend(self.invalid_refs)
        result.invalid_refs.extend(other.invalid_refs)
        result.unused_images.update(self.unused_images)
        result.unused_images.update(other.unused_images)
        result.unidirectional_links.extend(self.unidirectional_links)
        result.unidirectional_links.extend(other.unidirectional_links)
        return result
