"""Tests for models module."""

from typing import TYPE_CHECKING

from md_ref_checker.models import CheckResult, Reference

if TYPE_CHECKING:
    pass


def test_reference_creation() -> None:
    """Test Reference class creation."""
    ref = Reference(
        target="test.md",
        source_file="source.md",
        line_number=1,
        column=2,
        line_content="[[test.md]]",
        is_embed=False,
    )
    assert ref.target == "test.md"
    assert ref.source_file == "source.md"
    assert ref.line_number == 1
    assert ref.column == 2
    assert ref.line_content == "[[test.md]]"
    assert not ref.is_embed


def test_reference_str_representation() -> None:
    """Test Reference string representation."""
    ref = Reference(
        target="test.md",
        source_file="source.md",
        line_number=1,
        column=2,
        line_content="[[test.md]]",
        is_embed=False,
    )
    assert str(ref) == "source.md:1:2 -> test.md"


def test_reference_equality() -> None:
    """Test Reference equality comparison."""
    ref1 = Reference(
        target="test.md",
        source_file="source.md",
        line_number=1,
        column=2,
        line_content="[[test.md]]",
        is_embed=False,
    )
    ref2 = Reference(
        target="test.md",
        source_file="source.md",
        line_number=1,
        column=2,
        line_content="[[test.md]]",
        is_embed=False,
    )
    assert ref1 == ref2
    assert hash(ref1) == hash(ref2)


def test_check_result_add_invalid_ref() -> None:
    """Test adding invalid references to CheckResult."""
    result = CheckResult()
    ref = Reference(
        target="test.md",
        source_file="source.md",
        line_number=1,
        column=2,
        line_content="[[test.md]]",
        is_embed=False,
    )
    result.add_invalid_ref(ref)
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0] == ref


def test_check_result_merge() -> None:
    """Test merging two CheckResult instances."""
    result1 = CheckResult()
    result2 = CheckResult()

    ref1 = Reference(
        target="test1.md",
        source_file="source1.md",
        line_number=1,
        column=2,
        line_content="[[test1.md]]",
        is_embed=False,
    )
    ref2 = Reference(
        target="test2.md",
        source_file="source2.md",
        line_number=3,
        column=4,
        line_content="[[test2.md]]",
        is_embed=True,
    )

    result1.add_invalid_ref(ref1)
    result2.add_invalid_ref(ref2)

    result1.add_unused_image("unused1.png")
    result2.add_unused_image("unused2.png")

    result1.add_unidirectional_link("source1.md", "target1.md")
    result2.add_unidirectional_link("source2.md", "target2.md")

    merged = result1.merge(result2)

    assert len(merged.invalid_refs) == 2
    assert merged.invalid_refs[0] == ref1
    assert merged.invalid_refs[1] == ref2

    assert len(merged.unused_images) == 2
    assert "unused1.png" in merged.unused_images
    assert "unused2.png" in merged.unused_images

    assert len(merged.unidirectional_links) == 2
    assert merged.unidirectional_links[0] == ("source1.md", "target1.md")
    assert merged.unidirectional_links[1] == ("source2.md", "target2.md")
