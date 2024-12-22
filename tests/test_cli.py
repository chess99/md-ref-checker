"""Test cases for cli module."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from md_ref_checker.cli import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


def test_cli_help(capsys: "CaptureFixture[str]") -> None:
    """Test CLI help output."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Usage: " in captured.out
    assert "Options:" in captured.out


def test_cli_version(capsys: "CaptureFixture[str]") -> None:
    """Test CLI version output."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "md-ref-checker" in captured.out


def test_cli_check_valid_files(temp_dir: Path, capsys: "CaptureFixture[str]") -> None:
    """Test CLI with valid files."""
    # Create test files
    (temp_dir / "file1.md").write_text("Link to [[file2]]")
    (temp_dir / "file2.md").write_text("Link to [[file1]]")

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir)])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "✓ 所有引用都是有效的" in captured.out


def test_cli_check_invalid_files(temp_dir: Path, capsys: "CaptureFixture[str]") -> None:
    """Test CLI with invalid files."""
    # Create test file with invalid reference
    (temp_dir / "source.md").write_text("Link to [[nonexistent]]")

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir)])
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "无效引用" in captured.err
    assert "source.md" in captured.err
    assert "nonexistent" in captured.err


def test_cli_check_unused_images(temp_dir: Path, capsys: "CaptureFixture[str]") -> None:
    """Test CLI with unused images."""
    # Create test files
    (temp_dir / "doc.md").write_text("![[used.png]]")
    (temp_dir / "used.png").touch()
    (temp_dir / "unused.png").touch()

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir)])
    assert exc_info.value.code == 0  # No error for unused images

    captured = capsys.readouterr()
    assert "未被引用的图片文件" in captured.err
    assert "unused.png" in captured.out


def test_cli_check_unidirectional_links(
    temp_dir: Path, capsys: "CaptureFixture[str]"
) -> None:
    """Test CLI with unidirectional links."""
    # Create test files
    (temp_dir / "file1.md").write_text("Link to [[file2]]")
    (temp_dir / "file2.md").write_text("No links here")

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir), "-v", "1"])
    assert exc_info.value.code == 0  # No error for unidirectional links

    captured = capsys.readouterr()
    assert "单向链接" in captured.out
    assert "file1.md" in captured.out
    assert "file2.md" in captured.out


def test_cli_ignore_patterns(temp_dir: Path, capsys: "CaptureFixture[str]") -> None:
    """Test CLI with ignore patterns."""
    # Create test files
    (temp_dir / "main.md").write_text("[[draft]]")
    (temp_dir / "draft.md").write_text("Draft content")

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir), "-i", "draft.*"])
    assert exc_info.value.code == 1  # Error for invalid reference

    captured = capsys.readouterr()
    assert "无效引用" in captured.err
    assert "draft" in captured.err


def test_cli_debug_output(temp_dir: Path, capsys: "CaptureFixture[str]") -> None:
    """Test CLI debug output."""
    # Create test file
    (temp_dir / "test.md").write_text("Test content")

    with pytest.raises(SystemExit) as exc_info:
        main(["-d", str(temp_dir), "-D"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "[DEBUG]" in captured.out
