"""Test cases for the models module."""
from typing import TYPE_CHECKING
import pytest
from md_ref_checker.models import Reference, FileStats, CheckResult

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_reference_creation():
    """Test creating a Reference object."""
    ref = Reference(
        source_file="test.md",
        target="target.md",
        line_number=10,
        column=5,
        line_content="[[target.md]]",
        is_image=False,
    )
    
    assert ref.source_file == "test.md"
    assert ref.target == "target.md"
    assert ref.line_number == 10
    assert ref.column == 5
    assert ref.line_content == "[[target.md]]"
    assert not ref.is_image


def test_reference_equality():
    """Test Reference equality comparison."""
    ref1 = Reference("test.md", "target.md", 10, 5, "[[target.md]]", False)
    ref2 = Reference("test.md", "target.md", 10, 5, "[[target.md]]", False)
    ref3 = Reference("test.md", "other.md", 10, 5, "[[other.md]]", False)
    
    assert ref1 == ref2
    assert ref1 != ref3
    assert hash(ref1) == hash(ref2)
    assert hash(ref1) != hash(ref3)


def test_file_stats_creation():
    """Test creating a FileStats object."""
    stats = FileStats()
    assert stats.incoming_count == 0
    assert not stats.outgoing_refs
    
    stats.add_incoming_ref(Reference("source.md", "target.md", 1, 1, "[[target.md]]", False))
    assert stats.incoming_count == 1
    
    stats.add_outgoing_ref(Reference("target.md", "other.md", 1, 1, "[[other.md]]", False))
    assert len(stats.outgoing_refs) == 1


def test_check_result_creation():
    """Test creating a CheckResult object."""
    result = CheckResult()
    assert not result.invalid_refs
    assert not result.unused_images
    assert not result.unidirectional_links
    
    ref = Reference("test.md", "invalid.md", 1, 1, "[[invalid.md]]", False)
    result.add_invalid_ref(ref)
    assert len(result.invalid_refs) == 1
    
    result.add_unused_image("unused.png")
    assert len(result.unused_images) == 1
    
    result.add_unidirectional_link("source.md", "target.md")
    assert len(result.unidirectional_links) == 1


def test_check_result_merge():
    """Test merging two CheckResult objects."""
    result1 = CheckResult()
    result2 = CheckResult()
    
    ref1 = Reference("test1.md", "invalid1.md", 1, 1, "[[invalid1.md]]", False)
    ref2 = Reference("test2.md", "invalid2.md", 1, 1, "[[invalid2.md]]", False)
    
    result1.add_invalid_ref(ref1)
    result2.add_invalid_ref(ref2)
    
    result1.add_unused_image("unused1.png")
    result2.add_unused_image("unused2.png")
    
    result1.add_unidirectional_link("source1.md", "target1.md")
    result2.add_unidirectional_link("source2.md", "target2.md")
    
    merged = result1.merge(result2)
    assert len(merged.invalid_refs) == 2
    assert len(merged.unused_images) == 2
    assert len(merged.unidirectional_links) == 2
