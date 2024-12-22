"""Test cases for the utils module."""
from typing import TYPE_CHECKING
import os
import pytest
from md_ref_checker.utils import FileSystem

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def fs(tmp_path):
    """Create a FileSystem instance with a temporary directory."""
    return FileSystem(str(tmp_path))


def test_normalize_path(fs):
    """Test path normalization."""
    # Windows风格路径
    assert fs.normalize_path("dir\\file.md") == "dir/file.md"
    # 相对路径
    assert fs.normalize_path("./dir/file.md") == "dir/file.md"
    # 多余的斜杠
    assert fs.normalize_path("dir//file.md") == "dir/file.md"


def test_is_markdown_file(fs):
    """Test Markdown file detection."""
    assert fs.is_markdown_file("file.md")
    assert fs.is_markdown_file("dir/file.md")
    assert not fs.is_markdown_file("file.txt")
    assert not fs.is_markdown_file("file")


def test_is_image_file(fs):
    """Test image file detection."""
    assert fs.is_image_file("image.png")
    assert fs.is_image_file("image.jpg")
    assert fs.is_image_file("image.jpeg")
    assert fs.is_image_file("image.gif")
    assert fs.is_image_file("image.svg")
    assert fs.is_image_file("dir/image.png")
    assert not fs.is_image_file("file.txt")
    assert not fs.is_image_file("image")


def test_should_ignore(fs, tmp_path):
    """Test ignore patterns."""
    # 创建.gitignore文件
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("""
# Comments
*.log
/build/
.git/
node_modules/
/ignored.md
""")
    
    # 创建.mdignore文件
    mdignore = tmp_path / ".mdignore"
    mdignore.write_text("""
# Custom ignore
/custom/
temp.*
""")
    
    # 重新创建FileSystem实例以加载ignore文件
    fs = FileSystem(str(tmp_path))
    
    # 测试各种路径
    assert fs.should_ignore("test.log")
    assert fs.should_ignore("dir/test.log")
    assert fs.should_ignore("build/file.md")
    assert fs.should_ignore(".git/config")
    assert fs.should_ignore("node_modules/package.json")
    assert fs.should_ignore("ignored.md")
    assert fs.should_ignore("custom/file.md")
    assert fs.should_ignore("temp.txt")
    
    assert not fs.should_ignore("test.md")
    assert not fs.should_ignore("dir/test.md")
    assert not fs.should_ignore("images/test.png")


def test_find_files(fs, tmp_path):
    """Test file finding functionality."""
    # 创建测试文件结构
    (tmp_path / "doc1.md").touch()
    (tmp_path / "doc2.md").touch()
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/img1.png").touch()
    (tmp_path / "assets/img2.jpg").touch()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules/test.md").touch()
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/config").touch()
    
    # 创建.gitignore
    (tmp_path / ".gitignore").write_text("""
node_modules/
.git/
""")
    
    # 重新创建FileSystem实例以加载ignore文件
    fs = FileSystem(str(tmp_path))
    
    # 测试查找Markdown文件
    md_files = set(fs.find_files(pattern="*.md"))
    assert md_files == {
        "doc1.md",
        "doc2.md",
    }
    
    # 测试查找图片文件
    image_files = set(fs.find_files(pattern=("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg")))
    assert image_files == {
        "assets/img1.png",
        "assets/img2.jpg",
    }


def test_read_file(fs, tmp_path):
    """Test file reading functionality."""
    # 创建测试文件
    test_file = tmp_path / "test.md"
    test_content = "This is a test file.\nWith multiple lines.\n"
    test_file.write_text(test_content)
    
    assert fs.read_file("test.md") == test_content


def test_file_exists(fs, tmp_path):
    """Test file existence checking."""
    # 创建测试文件
    (tmp_path / "exists.md").touch()
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir/nested.md").touch()
    
    assert fs.file_exists("exists.md")
    assert fs.file_exists("dir/nested.md")
    assert not fs.file_exists("nonexistent.md")
    assert not fs.file_exists("dir/nonexistent.md")
