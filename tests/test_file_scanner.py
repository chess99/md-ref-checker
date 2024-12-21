"""
Tests for file scanner functionality
"""

import os
import pytest
from src.checker.file_scanner import FileScanner
from src.checker.ignore_rules import IgnoreRules
from .conftest import create_test_files

@pytest.fixture
def scanner(temp_dir: str) -> FileScanner:
    """创建文件扫描器实例"""
    return FileScanner(temp_dir, IgnoreRules(temp_dir))

def test_scan_basic(scanner: FileScanner, temp_dir: str) -> None:
    """测试基本扫描功能"""
    # 创建测试文件
    files = {
        'doc1.md': '# Doc 1',
        'doc2.md': '# Doc 2',
        'img1.png': 'fake image 1',
        'img2.jpg': 'fake image 2',
        'other.txt': 'text file'
    }
    create_test_files(temp_dir, files)

    # 扫描文件
    scanner.scan()

    # 验证结果
    assert len(scanner.files) == 5
    assert len(scanner.markdown_files) == 2
    assert len(scanner.image_files) == 2
    assert 'doc1.md' in scanner.markdown_files
    assert 'doc2.md' in scanner.markdown_files
    assert 'img1.png' in scanner.image_files
    assert 'img2.jpg' in scanner.image_files

def test_scan_nested_directories(scanner: FileScanner, temp_dir: str) -> None:
    """测试嵌套目录扫描"""
    # 创建测试文件
    files = {
        'dir1/doc1.md': '# Doc 1',
        'dir1/dir2/doc2.md': '# Doc 2',
        'dir1/img1.png': 'fake image 1',
        'dir2/img2.jpg': 'fake image 2'
    }
    create_test_files(temp_dir, files)

    # 扫描文件
    scanner.scan()

    # 验证结果
    assert len(scanner.files) == 4
    assert len(scanner.markdown_files) == 2
    assert len(scanner.image_files) == 2
    assert 'dir1/doc1.md' in scanner.markdown_files
    assert 'dir1/dir2/doc2.md' in scanner.markdown_files
    assert 'dir1/img1.png' in scanner.image_files
    assert 'dir2/img2.jpg' in scanner.image_files

def test_scan_with_ignore_rules(scanner: FileScanner, temp_dir: str) -> None:
    """测试忽略规则"""
    # 创建 .mdignore 文件
    create_test_files(temp_dir, {
        '.mdignore': 'ignored/*\n*.txt'
    })

    # 创建测试文件
    files = {
        'doc1.md': '# Doc 1',
        'ignored/doc2.md': '# Doc 2',
        'img1.png': 'fake image 1',
        'ignored/img2.jpg': 'fake image 2',
        'note.txt': 'text file'
    }
    create_test_files(temp_dir, files)

    # 扫描文件
    scanner.scan()

    # 验证结果
    assert len(scanner.files) == 3  # .mdignore + doc1.md + img1.png
    assert len(scanner.markdown_files) == 1
    assert len(scanner.image_files) == 1
    assert 'doc1.md' in scanner.markdown_files
    assert 'img1.png' in scanner.image_files
    assert 'ignored/doc2.md' not in scanner.markdown_files
    assert 'ignored/img2.jpg' not in scanner.image_files
    assert 'note.txt' not in scanner.files

def test_scan_empty_directory(scanner: FileScanner, temp_dir: str) -> None:
    """测试空目录扫描"""
    # 扫描文件
    scanner.scan()

    # 验证结果
    assert len(scanner.files) == 0
    assert len(scanner.markdown_files) == 0
    assert len(scanner.image_files) == 0

def test_rescan(scanner: FileScanner, temp_dir: str) -> None:
    """测试重新扫描"""
    # 创建初始文件
    files = {
        'doc1.md': '# Doc 1',
        'img1.png': 'fake image 1'
    }
    create_test_files(temp_dir, files)

    # 第一次扫描
    scanner.scan()
    assert len(scanner.files) == 2

    # 添加新文件
    create_test_files(temp_dir, {
        'doc2.md': '# Doc 2',
        'img2.jpg': 'fake image 2'
    })

    # 重新扫描
    scanner.rescan()
    assert len(scanner.files) == 4
    assert len(scanner.markdown_files) == 2
    assert len(scanner.image_files) == 2

def test_file_mapping(scanner: FileScanner, temp_dir: str) -> None:
    """测试文件映射"""
    # 创建测试文件
    files = {
        'dir1/doc.md': '# Doc 1',
        'dir2/doc.md': '# Doc 2',
        'img.png': 'fake image 1',
        'dir1/img.png': 'fake image 2'
    }
    create_test_files(temp_dir, files)

    # 扫描文件
    scanner.scan()

    # 测试文件名映射
    mapping = scanner.get_file_mapping()
    assert len(mapping['doc']) == 2
    assert 'dir1/doc.md' in mapping['doc']
    assert 'dir2/doc.md' in mapping['doc']
    assert len(mapping['img']) == 2
    assert 'img.png' in mapping['img']
    assert 'dir1/img.png' in mapping['img']

    # 测试特定文件名映射
    doc_mapping = scanner.get_file_mapping('doc.md')
    assert len(doc_mapping['doc']) == 2
    assert 'dir1/doc.md' in doc_mapping['doc']
    assert 'dir2/doc.md' in doc_mapping['doc'] 