"""
Tests for utility functions
"""

import os
from src.utils import normalize_path, get_file_name, get_directory_name

def test_normalize_path():
    """Test path normalization"""
    # Test forward slash conversion
    assert normalize_path('path\\to\\file') == 'path/to/file'
    assert normalize_path('path/to/file') == 'path/to/file'
    
    # Test multiple slash handling
    assert normalize_path('path//to///file') == 'path/to/file'
    assert normalize_path('path\\\\to\\\\\\file') == 'path/to/file'
    
    # Test mixed slash handling
    assert normalize_path('path\\to/file') == 'path/to/file'
    assert normalize_path('path/to\\file') == 'path/to/file'
    
    # Test empty and None inputs
    assert normalize_path('') == ''
    assert normalize_path(None) == ''

def test_get_file_name():
    """Test file name extraction"""
    # Test basic file name extraction
    assert get_file_name('path/to/file.txt') == 'file'
    assert get_file_name('file.txt') == 'file'
    
    # Test files without extension
    assert get_file_name('path/to/file') == 'file'
    assert get_file_name('file') == 'file'
    
    # Test files with multiple dots
    assert get_file_name('path/to/file.name.txt') == 'file.name'
    assert get_file_name('file.name.txt') == 'file.name'
    
    # Test empty and None inputs
    assert get_file_name('') == ''
    assert get_file_name(None) == ''
    
    # Test special cases
    assert get_file_name('.hidden') == '.hidden'
    assert get_file_name('path/to/.hidden') == '.hidden'

def test_get_directory_name():
    """Test directory name extraction"""
    # Test basic directory name extraction
    assert get_directory_name('path/to/file.txt') == 'path/to'
    assert get_directory_name('path/to/file') == 'path/to'
    
    # Test root directory
    assert get_directory_name('file.txt') == ''
    assert get_directory_name('file') == ''
    
    # Test directory paths
    assert get_directory_name('path/to/dir/') == 'path/to/dir'
    assert get_directory_name('path/to/dir') == 'path/to'
    
    # Test empty and None inputs
    assert get_directory_name('') == ''
    assert get_directory_name(None) == ''
    
    # Test special cases
    assert get_directory_name('/path/to/file') == '/path/to'
    assert get_directory_name('C:/path/to/file') == 'C:/path/to' 