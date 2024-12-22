"""Test cases for utils module."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pytest import CaptureFixture

from md_ref_checker.utils import FileSystem

if TYPE_CHECKING:
    pass


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


def test_file_system_init(temp_dir: Path) -> None:
    """Test FileSystem initialization."""
    fs = FileSystem(str(temp_dir))
    assert fs.root_dir == str(temp_dir)
    # Check default ignore patterns
    assert fs.ignore_patterns == [
        ".git/*",
        ".obsidian/*",
        ".trash/*",
        "node_modules/*",
        ".DS_Store",
        "Thumbs.db",
    ]


def test_file_system_normalize_path(temp_dir: Path) -> None:
    """Test path normalization."""
    fs = FileSystem(str(temp_dir))
    path = os.path.join("dir", "subdir", "file.md")
    normalized = fs.normalize_path(path)
    assert normalized == os.path.normpath(path)


def test_file_system_should_ignore(temp_dir: Path) -> None:
    """Test file ignore patterns."""
    fs = FileSystem(str(temp_dir))
    fs.ignore_patterns.extend(["*.tmp", "draft/*"])

    assert fs.should_ignore("test.tmp")
    assert fs.should_ignore("draft/file.md")
    assert not fs.should_ignore("test.md")


def test_file_system_find_files(temp_dir: Path) -> None:
    """Test finding files with patterns."""
    # Create test files
    (temp_dir / "test1.md").touch()
    (temp_dir / "test2.md").touch()
    (temp_dir / "test.txt").touch()
    (temp_dir / "draft").mkdir()
    (temp_dir / "draft" / "draft.md").touch()

    fs = FileSystem(str(temp_dir))
    fs.ignore_patterns.append("draft/*")

    md_files = list(fs.find_files(pattern="*.md"))
    assert len(md_files) == 2
    assert all(f.endswith(".md") for f in md_files)
    assert not any("draft" in f for f in md_files)

    txt_files = list(fs.find_files(pattern="*.txt"))
    assert len(txt_files) == 1
    assert txt_files[0].endswith(".txt")


def test_file_system_read_file(temp_dir: Path) -> None:
    """Test reading file contents."""
    test_file = temp_dir / "test.md"
    test_content = "Test content\nLine 2"
    test_file.write_text(test_content)

    fs = FileSystem(str(temp_dir))
    content = fs.read_file("test.md")
    assert content == test_content


def test_file_system_file_exists(temp_dir: Path) -> None:
    """Test file existence check."""
    test_file = temp_dir / "test.md"
    test_file.touch()

    fs = FileSystem(str(temp_dir))
    assert fs.file_exists("test.md")
    assert not fs.file_exists("nonexistent.md")


def test_file_system_debug_output(temp_dir: Path, capsys: CaptureFixture[str]) -> None:
    """Test debug output."""
    fs = FileSystem(str(temp_dir), debug=True)
    fs.should_ignore("test.md")  # This method has debug output
    captured = capsys.readouterr()
    assert "Checking if path should be ignored" in captured.out
