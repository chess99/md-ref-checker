"""Test cases for checker module."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from md_ref_checker.checker import ReferenceChecker

if TYPE_CHECKING:
    pass


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def checker(temp_dir: Path) -> ReferenceChecker:
    """Create a ReferenceChecker instance with a temporary directory."""
    return ReferenceChecker(str(temp_dir))


def test_check_single_file(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test checking a single file with valid and invalid references."""
    # Create test files
    (temp_dir / "doc1.md").write_text(
        """
Here's a valid reference [[doc2]]
And an invalid one [[nonexistent]]
Also a valid image ![[image.png]]
And an invalid image ![[missing.png]]
"""
    )
    (temp_dir / "doc2.md").write_text("Some content")
    (temp_dir / "image.png").touch()

    result = checker.check_file("doc1.md")

    # Check invalid references
    assert len(result.invalid_refs) == 2
    invalid_targets = {ref.target for ref in result.invalid_refs}
    assert invalid_targets == {"nonexistent", "missing.png"}


def test_check_directory(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test checking an entire directory."""
    # Create test files
    (temp_dir / "doc1.md").write_text(
        """
Reference to [[doc2]]
Invalid reference [[nonexistent]]
"""
    )
    (temp_dir / "doc2.md").write_text(
        """
Back reference to [[doc1]]
Image reference ![[image.png]]
"""
    )
    (temp_dir / "image.png").touch()
    (temp_dir / "unused.png").touch()

    result = checker.check_directory()

    # Check invalid references
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "nonexistent"

    # Check unused images
    assert result.unused_images == {"unused.png"}

    # Check unidirectional links
    assert not result.unidirectional_links  # doc1 and doc2 reference each other


def test_unidirectional_links(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test detection of unidirectional links."""
    # Create test files
    (temp_dir / "doc1.md").write_text("Reference to [[doc2]]")
    (temp_dir / "doc2.md").write_text("No back reference")

    result = checker.check_directory()

    assert len(result.unidirectional_links) == 1
    assert result.unidirectional_links[0] == ("doc1.md", "doc2.md")


def test_ignore_patterns(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test that ignored files are not checked."""
    # Create .gitignore
    (temp_dir / ".gitignore").write_text(
        """
/ignored/
temp.md
"""
    )

    # Create test files
    (temp_dir / "doc.md").write_text(
        """
[[ignored/doc]]
[[temp]]
"""
    )
    (temp_dir / "ignored").mkdir()
    (temp_dir / "ignored/doc.md").write_text("Should be ignored")
    (temp_dir / "temp.md").write_text("Should be ignored")

    # Recreate checker to load ignore file
    checker = ReferenceChecker(str(temp_dir))
    result = checker.check_directory()

    # References to ignored files should be invalid
    assert len(result.invalid_refs) == 2


def test_nested_references(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test handling of nested directory references."""
    # Create test directory structure
    (temp_dir / "dir1").mkdir()
    (temp_dir / "dir1/doc1.md").write_text(
        """
[[../dir2/doc2]]
[[doc3]]
"""
    )
    (temp_dir / "dir2").mkdir()
    (temp_dir / "dir2/doc2.md").write_text("Some content")
    (temp_dir / "dir1/doc3.md").write_text("Some content")

    result = checker.check_file("dir1/doc1.md")

    assert not result.invalid_refs  # All references should be valid


def test_cross_directory_references(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test handling of references across different directories."""
    # Create test directory structure
    (temp_dir / "dir1/subdir1").mkdir(parents=True)
    (temp_dir / "dir2/subdir2").mkdir(parents=True)

    # Reference a file in another directory
    (temp_dir / "dir1/subdir1/source.md").write_text(
        """
Reference to [[../../dir2/subdir2/target]]
Reference to [[target]]
"""
    )
    (temp_dir / "dir2/subdir2/target.md").write_text("Target content")

    result = checker.check_file("dir1/subdir1/source.md")

    assert not result.invalid_refs  # Both reference styles should be valid


def test_image_references(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test handling of image references."""
    # Create test files
    (temp_dir / "assets").mkdir()
    (temp_dir / "assets/image1.png").touch()
    (temp_dir / "assets/image2.jpg").touch()
    (temp_dir / "doc.md").write_text(
        """
![[assets/image1.png]]
![Regular markdown](assets/image2.jpg)
![[missing.png]]
"""
    )

    result = checker.check_file("doc.md")

    # Only missing.png should be reported as invalid
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "missing.png"


def test_reference_with_heading(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test handling of references with heading anchors."""
    # Create test files
    (temp_dir / "doc1.md").write_text(
        """
[[doc2#heading1]]
[[doc2#nonexistent]]
[[missing#heading]]
"""
    )
    (temp_dir / "doc2.md").write_text(
        """
# heading1
Some content
"""
    )

    result = checker.check_file("doc1.md")

    # Only missing#heading should be invalid
    # Note: We don't check if headings exist, only if files exist
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "missing"


def test_reference_search_order(checker: ReferenceChecker, temp_dir: Path) -> None:
    """Test the order of searching for referenced files."""
    # Create test directory structure
    (temp_dir / "dir1/subdir").mkdir(parents=True)
    (temp_dir / "dir2").mkdir()

    # Create test files
    (temp_dir / "dir1/subdir/source.md").write_text(
        """
[[target]]  # Should find local target first
"""
    )
    (temp_dir / "dir1/subdir/target.md").write_text("Local target")
    (temp_dir / "dir2/target.md").write_text("Remote target")

    result = checker.check_file("dir1/subdir/source.md")
    assert not result.invalid_refs  # Should find the local target.md
