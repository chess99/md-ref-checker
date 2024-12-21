"""Test path resolver"""

import os
import pytest
from src.checker.path_resolver import PathResolver

@pytest.fixture
def resolver(temp_dir: str) -> PathResolver:
    """创建路径解析器实例"""
    return PathResolver(temp_dir)

def test_resolve_absolute_link(resolver: PathResolver) -> None:
    """测试绝对路径解析"""
    # 测试绝对路径
    assert resolver.resolve_link('/doc.md', 'source.md') == 'doc.md'
    assert resolver.resolve_link('/dir/doc.md', 'source.md') == 'dir/doc.md'
    assert resolver.resolve_link('/img.png', 'source.md', True) == 'img.png'

def test_resolve_relative_link(resolver: PathResolver) -> None:
    """测试相对路径解析"""
    # 测试相对路径
    assert resolver.resolve_link('doc.md', 'source.md') == 'doc.md'
    assert resolver.resolve_link('./doc.md', 'source.md') == 'doc.md'
    assert resolver.resolve_link('../doc.md', 'dir/source.md') == 'doc.md'
    assert resolver.resolve_link('dir/doc.md', 'source.md') == 'dir/doc.md'

def test_resolve_image_link(resolver: PathResolver) -> None:
    """测试图片路径解析"""
    # 测试图片路径
    assert resolver.resolve_link('img.png', 'source.md', True) == 'img.png'
    assert resolver.resolve_link('./img.png', 'source.md', True) == 'img.png'
    assert resolver.resolve_link('../img.png', 'dir/source.md', True) == 'img.png'
    assert resolver.resolve_link('dir/img.png', 'source.md', True) == 'dir/img.png'

def test_resolve_complex_paths(resolver: PathResolver) -> None:
    """测试复杂路径解析"""
    # 测试复杂路径
    assert resolver.resolve_link('../../doc.md', 'a/b/c/source.md') == 'a/doc.md'
    assert resolver.resolve_link('./dir/../doc.md', 'source.md') == 'doc.md'
    assert resolver.resolve_link('dir/./doc.md', 'source.md') == 'dir/doc.md'
    assert resolver.resolve_link('dir//doc.md', 'source.md') == 'dir/doc.md'

def test_resolve_with_different_source_locations(resolver: PathResolver) -> None:
    """测试不同源文件位置的解析"""
    # 测试不同源文件位置
    assert resolver.resolve_link('doc.md', 'dir/source.md') == 'dir/doc.md'
    assert resolver.resolve_link('../doc.md', 'dir/source.md') == 'doc.md'
    assert resolver.resolve_link('../../doc.md', 'dir1/dir2/source.md') == 'doc.md'
    assert resolver.resolve_link('./doc.md', 'dir/source.md') == 'dir/doc.md'

def test_resolve_special_cases(resolver: PathResolver) -> None:
    """测试特殊情况"""
    # 测试空路径
    assert resolver.resolve_link('', 'source.md') == ''
    
    # 测试当前目录
    assert resolver.resolve_link('.', 'source.md') == ''
    assert resolver.resolve_link('./', 'source.md') == ''
    
    # 测试父目录
    assert resolver.resolve_link('..', 'dir/source.md') == ''
    assert resolver.resolve_link('../', 'dir/source.md') == ''

def test_resolve_with_windows_paths(resolver: PathResolver) -> None:
    """测试 Windows 路径解析"""
    # 测试 Windows 路径
    assert resolver.resolve_link('dir\\doc.md', 'source.md') == 'dir/doc.md'
    assert resolver.resolve_link('.\\doc.md', 'source.md') == 'doc.md'
    assert resolver.resolve_link('..\\doc.md', 'dir\\source.md') == 'doc.md'
    assert resolver.resolve_link('dir\\..\\doc.md', 'source.md') == 'doc.md'