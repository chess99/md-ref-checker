"""Test cases for the checker module."""
from typing import TYPE_CHECKING
import pytest
from md_ref_checker.checker import ReferenceChecker
from md_ref_checker.models import Reference

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def checker(tmp_path):
    """Create a ReferenceChecker instance with a temporary directory."""
    return ReferenceChecker(str(tmp_path))


def test_check_single_file(checker, tmp_path):
    """Test checking a single file with valid and invalid references."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("""
Here's a valid reference [[doc2]]
And an invalid one [[nonexistent]]
Also a valid image ![[image.png]]
And an invalid image ![[missing.png]]
""")
    (tmp_path / "doc2.md").write_text("Some content")
    (tmp_path / "image.png").touch()
    
    result = checker.check_file("doc1.md")
    
    # 检查无效引用
    assert len(result.invalid_refs) == 2
    invalid_targets = {ref.target for ref in result.invalid_refs}
    assert invalid_targets == {"nonexistent", "missing.png"}


def test_check_directory(checker, tmp_path):
    """Test checking an entire directory."""
    # 创建测试文件结构
    (tmp_path / "doc1.md").write_text("""
Reference to [[doc2]]
Invalid reference [[nonexistent]]
""")
    (tmp_path / "doc2.md").write_text("""
Back reference to [[doc1]]
Image reference ![[image.png]]
""")
    (tmp_path / "image.png").touch()
    (tmp_path / "unused.png").touch()
    
    result = checker.check_directory()
    
    # 检查无效引用
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "nonexistent"
    
    # 检查未使用的图片
    assert result.unused_images == {"unused.png"}
    
    # 检查单向链接
    assert not result.unidirectional_links  # doc1 和 doc2 互相引用


def test_unidirectional_links(checker, tmp_path):
    """Test detection of unidirectional links."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("Reference to [[doc2]]")
    (tmp_path / "doc2.md").write_text("No back reference")
    
    result = checker.check_directory()
    
    assert len(result.unidirectional_links) == 1
    assert result.unidirectional_links[0] == ("doc1.md", "doc2.md")


def test_ignore_patterns(checker, tmp_path):
    """Test that ignored files are not checked."""
    # 创建.gitignore
    (tmp_path / ".gitignore").write_text("""
/ignored/
temp.md
""")
    
    # 创建测试文件
    (tmp_path / "doc.md").write_text("""
[[ignored/doc]]
[[temp]]
""")
    (tmp_path / "ignored").mkdir()
    (tmp_path / "ignored/doc.md").write_text("Should be ignored")
    (tmp_path / "temp.md").write_text("Should be ignored")
    
    # 重新创建checker以加载ignore文件
    checker = ReferenceChecker(str(tmp_path))
    result = checker.check_directory()
    
    # 引用被忽略的文件应该被视为无效
    assert len(result.invalid_refs) == 2


def test_nested_references(checker, tmp_path):
    """Test handling of nested directory references."""
    # 创建测试目录结构
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1/doc1.md").write_text("""
[[../dir2/doc2]]
[[doc3]]
""")
    (tmp_path / "dir2").mkdir()
    (tmp_path / "dir2/doc2.md").write_text("Some content")
    (tmp_path / "dir1/doc3.md").write_text("Some content")
    
    result = checker.check_file("dir1/doc1.md")
    
    assert not result.invalid_refs  # 所有引用都应该是有效的


def test_image_references(checker, tmp_path):
    """Test handling of image references."""
    # 创建测试文件结构
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/image1.png").touch()
    (tmp_path / "assets/image2.jpg").touch()
    (tmp_path / "doc.md").write_text("""
![[assets/image1.png]]
![Regular markdown](assets/image2.jpg)
![[missing.png]]
""")
    
    result = checker.check_file("doc.md")
    
    # 只有missing.png应该被报告为无效
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "missing.png"


def test_reference_with_heading(checker, tmp_path):
    """Test handling of references with heading anchors."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("""
[[doc2#heading1]]
[[doc2#nonexistent]]
[[missing#heading]]
""")
    (tmp_path / "doc2.md").write_text("""
# heading1
Some content
""")
    
    result = checker.check_file("doc1.md")
    
    # 只有missing#heading应该被报告为无效
    # 注意：我们不检查标题是否存在，只检查文件是否存在
    assert len(result.invalid_refs) == 1
    assert result.invalid_refs[0].target == "missing"
