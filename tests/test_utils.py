"""
Tests for utility functions
"""

import pytest
from src.checker.utils import normalize_path, is_image_file, is_markdown_file

def test_normalize_path():
    """Test path normalization"""
    test_cases = [
        ('path/to/file', 'path/to/file'),
        ('path\\to\\file', 'path/to/file'),
        ('path/../file', 'path/../file'),
        ('path/./file', 'path/./file'),
    ]
    
    for input_path, expected in test_cases:
        assert normalize_path(input_path) == expected

@pytest.mark.parametrize("filename", [
    'image.png',
    'photo.jpg',
    'photo.jpeg',
    'animation.gif',
    'vector.svg',
    'image.webp',
    'IMAGE.PNG',
    'PHOTO.JPG',
])
def test_is_image_file_valid(filename):
    """Test valid image file detection"""
    assert is_image_file(filename)

@pytest.mark.parametrize("filename", [
    'document.md',
    'script.py',
    'image.txt',
    'photo',
    '.png',
    'image.doc',
])
def test_is_image_file_invalid(filename):
    """Test invalid image file detection"""
    assert not is_image_file(filename)

@pytest.mark.parametrize("filename", [
    'document.md',
    'README.md',
    'notes.MD',
    'doc.markdown',
    'CAPS.MD',
])
def test_is_markdown_file_valid(filename):
    """Test valid Markdown file detection"""
    assert is_markdown_file(filename)

@pytest.mark.parametrize("filename", [
    'document.txt',
    'script.py',
    'doc',
    '.md',
    'markdown',
    'md.doc',
])
def test_is_markdown_file_invalid(filename):
    """Test invalid Markdown file detection"""
    assert not is_markdown_file(filename) 