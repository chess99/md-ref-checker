"""Test reference checker"""

import os
from typing import TYPE_CHECKING
import pytest
from src.checker.models import Config, FileAccessError, ParseError
from src.checker.reference_checker import ReferenceChecker
from .conftest import create_test_files

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def checker(temp_dir: str) -> ReferenceChecker:
    """创建引用检查器实例"""
    config = Config(
        root_dir=temp_dir,
        search_paths=['.', 'assets', 'images'],
        verbosity=2
    )
    return ReferenceChecker(config)

def test_check_references_basic(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试基本引用检查"""
    # 创建测试文件
    files = {
        'doc1.md': '# Test\n[Link](doc2.md)\n![Image](image.png)',
        'doc2.md': '# Doc 2\n[Back](doc1.md)',
        'image.png': 'fake image content'
    }
    create_test_files(temp_dir, files)

    # 检查引用
    stats = checker.check_references()
    
    # 验证引用统计
    assert len(stats.invalid_references) == 0
    assert len(stats.outgoing['doc1.md']) == 1
    assert len(stats.incoming['doc2.md']) == 1
    assert 'image.png' in stats.referenced_images

def test_check_references_with_invalid_links(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试包含无效引用的情况"""
    # 创建测试文件
    files = {
        'invalid.md': '# Test\n[Bad Link](non-existent.md)\n![Bad Image](missing.png)'
    }
    create_test_files(temp_dir, files)

    # 检查引用
    stats = checker.check_references()
    
    # 验证无效引用
    assert len(stats.invalid_references) == 2
    invalid_refs = [ref for ref in stats.invalid_references if ref.source == 'invalid.md']
    assert len(invalid_refs) == 2
    assert any(ref.target == 'non-existent.md' for ref in invalid_refs)
    assert any(ref.target == 'missing.png' for ref in invalid_refs)

def test_check_references_with_assets(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试 assets 目录中的图片引用"""
    # 创建测试文件
    files = {
        'doc.md': '# Test\n![Image](test.png)',
        'assets/test.png': 'fake image content'
    }
    create_test_files(temp_dir, files)

    # 检查引用
    stats = checker.check_references()
    
    # 验证图片引用
    assert 'assets/test.png' in stats.referenced_images
    assert len(stats.invalid_references) == 0

def test_check_references_with_search_paths(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试搜索路径功能"""
    # 创建测试文件
    files = {
        'doc.md': '# Test\n![Image 1](img1.png)\n![Image 2](img2.png)',
        'images/img1.png': 'fake image 1',
        'assets/img2.png': 'fake image 2'
    }
    create_test_files(temp_dir, files)

    # 检查引用
    stats = checker.check_references()
    
    # 验证图片引用
    assert 'images/img1.png' in stats.referenced_images
    assert 'assets/img2.png' in stats.referenced_images
    assert len(stats.invalid_references) == 0

def test_check_references_with_wiki_links(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试 Wiki 风格链接"""
    # 创建测试文件
    files = {
        'doc.md': '# Test\n[[page]]\n![[image.png]]',
        'page.md': '# Page',
        'image.png': 'fake image'
    }
    create_test_files(temp_dir, files)

    # 检查引用
    stats = checker.check_references()
    
    # 验证引用
    assert len(stats.invalid_references) == 0
    assert len(stats.outgoing['doc.md']) == 1
    assert 'image.png' in stats.referenced_images

def test_check_references_with_errors(checker: ReferenceChecker, temp_dir: str) -> None:
    """测试错误处理"""
    # 创建只读目录
    os.makedirs(os.path.join(temp_dir, 'readonly'), mode=0o555)
    
    # 测试文件访问错误
    with pytest.raises(FileAccessError):
        create_test_files(os.path.join(temp_dir, 'readonly'), {'test.md': 'content'})

    # 测试解析错误
    files = {
        'bad.md': '# Test\n[Bad Link](file:///etc/passwd)'
    }
    create_test_files(temp_dir, files)
    stats = checker.check_references()
    assert len(stats.invalid_references) == 0  # URL 应该被忽略

def test_print_report(checker: ReferenceChecker, temp_dir: str, capsys: "CaptureFixture[str]") -> None:
    """测试报告打印"""
    # 创建测试文件
    files = {
        'doc1.md': '# Test\n[Link](doc2.md)\n![Image](image.png)',
        'doc2.md': '# Doc 2',
        'image.png': 'fake image'
    }
    create_test_files(temp_dir, files)

    # 检查引用并打印报告
    stats = checker.check_references()
    checker.print_report()
    
    # 验证输出
    captured = capsys.readouterr()
    assert "Summary:" in captured.out
    assert "Total files:" in captured.out
    assert "Markdown files:" in captured.out
    assert "Image files:" in captured.out