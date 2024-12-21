"""
Tests for path resolver functionality
"""

import os
import pytest
from src.checker.ignore_rules import IgnoreRules
from src.checker.file_scanner import FileScanner
from src.checker.path_resolver import PathResolver

@pytest.fixture
def test_env(tmp_path):
    """Set up test environment"""
    # Create test directories
    (tmp_path / "docs" / "subfolder").mkdir(parents=True)
    (tmp_path / "assets" / "subfolder").mkdir(parents=True)
    
    # Create test files
    (tmp_path / "docs" / "index.md").write_text("# Index")
    (tmp_path / "docs" / "subfolder" / "doc1.md").write_text("# Doc 1")
    (tmp_path / "docs" / "subfolder" / "doc2.md").write_text("# Doc 2")
    (tmp_path / "assets" / "image1.png").write_text("dummy image content")
    (tmp_path / "assets" / "subfolder" / "image2.jpg").write_text("dummy image content")
    (tmp_path / "README.md").write_text("# README")
    (tmp_path / ".gitignore").write_text("")  # Add empty .gitignore
    
    # Initialize components
    ignore_rules = IgnoreRules(tmp_path)
    file_scanner = FileScanner(tmp_path, ignore_rules)
    file_scanner.scan()
    resolver = PathResolver(file_scanner)
    
    return resolver

def test_absolute_paths(test_env):
    """Test absolute path resolution"""
    resolver = test_env
    
    # Test markdown file
    resolved = resolver.resolve_link(
        '/docs/index',
        'README.md',
        is_image=False
    )
    assert resolved == 'docs/index.md'
    
    # Test image file
    resolved = resolver.resolve_link(
        '/assets/image1.png',
        'README.md',
        is_image=True
    )
    assert resolved == 'assets/image1.png'

def test_relative_paths(test_env):
    """Test relative path resolution"""
    resolver = test_env
    
    # Test same directory
    resolved = resolver.resolve_link(
        'doc2',
        'docs/subfolder/doc1.md',
        is_image=False
    )
    assert resolved == 'docs/subfolder/doc2.md'
    
    # Test parent directory
    resolved = resolver.resolve_link(
        '../index',
        'docs/subfolder/doc1.md',
        is_image=False
    )
    assert resolved == 'docs/index.md'
    
    # Test image in parent directory
    resolved = resolver.resolve_link(
        '../image1.png',
        'assets/subfolder/image2.jpg',
        is_image=True
    )
    assert resolved == 'assets/image1.png'

def test_image_resolution(test_env):
    """Test image path resolution"""
    resolver = test_env
    
    # Test direct reference
    resolved = resolver.resolve_link(
        'image1.png',
        'README.md',
        is_image=True
    )
    assert resolved == 'assets/image1.png'
    
    # Test subfolder reference
    resolved = resolver.resolve_link(
        'subfolder/image2.jpg',
        'README.md',
        is_image=True
    )
    assert resolved == 'assets/subfolder/image2.jpg'
    
    # Test non-existent image
    resolved = resolver.resolve_link(
        'non_existent.png',
        'README.md',
        is_image=True
    )
    assert resolved == 'non_existent.png'  # Changed: don't add assets/ prefix

def test_markdown_resolution(test_env):
    """Test markdown file resolution"""
    resolver = test_env
    
    # Test with extension
    resolved = resolver.resolve_link(
        'index.md',
        'README.md',
        is_image=False
    )
    assert resolved == 'docs/index.md'
    
    # Test without extension
    resolved = resolver.resolve_link(
        'index',
        'README.md',
        is_image=False
    )
    assert resolved == 'docs/index.md'
    
    # Test non-existent file
    resolved = resolver.resolve_link(
        'non_existent',
        'README.md',
        is_image=False
    )
    assert resolved == 'non_existent'  # Changed: don't add .md extension

def test_referenced_images(test_env):
    """Test referenced images tracking"""
    resolver = test_env
    
    # Reference some images
    resolver.resolve_link('image1.png', 'README.md', is_image=True)
    resolver.resolve_link('subfolder/image2.jpg', 'README.md', is_image=True)
    
    # Check referenced images
    expected_refs = {
        'assets/image1.png',
        'assets/subfolder/image2.jpg',
    }
    assert resolver.referenced_images == expected_refs