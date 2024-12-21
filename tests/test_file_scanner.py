"""
Tests for file scanner functionality
"""

import os
from src.checker.ignore_rules import IgnoreRules
from src.checker.file_scanner import FileScanner

def test_file_scanning(test_files_root):
    """Test basic file scanning"""
    test_dir = os.path.join(test_files_root, 'test_case_scanner')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test markdown files
    expected_md_files = {
        'docs/index.md',
        'docs/doc1.md',
        'docs/doc2.md',
    }
    actual_md_files = {f for f in scanner.files if f.endswith('.md')}
    assert actual_md_files == expected_md_files, \
        "Should correctly identify markdown files"
    
    # Test image files
    expected_image_files = {
        'assets/image1.png',
        'assets/image2.jpg',
        'assets/unused.png',
    }
    assert scanner.image_files == expected_image_files, \
        "Should correctly identify image files"

def test_file_mapping(test_files_root):
    """Test file mapping functionality"""
    test_dir = os.path.join(test_files_root, 'test_case_scanner')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test complete path mapping
    assert scanner.get_file_mapping('docs/index.md') == ['docs/index.md'], \
        "Should correctly map complete file paths"
    
    # Test base name mapping
    index_mappings = scanner.get_file_mapping('index')
    assert len(index_mappings) == 1, \
        "Should correctly map base file names"
    assert 'docs/index.md' in index_mappings, \
        "Should find correct file for base name"
    
    # Test image mapping
    image_mappings = scanner.get_file_mapping('image1.png')
    assert len(image_mappings) == 1, \
        "Should correctly map image files"
    assert 'assets/image1.png' in image_mappings, \
        "Should find correct image file"

def test_file_names(test_files_root):
    """Test file names collection"""
    test_dir = os.path.join(test_files_root, 'test_case_scanner')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test file names
    expected_names = {
        'index',
        'doc1',
        'doc2',
        'image1',
        'image2',
        'unused'
    }
    assert scanner.file_names == expected_names, \
        "Should correctly collect file names"

def test_ignore_rules(test_files_root):
    """Test ignore rules integration"""
    test_dir = os.path.join(test_files_root, 'test_case_scanner')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test ignored files
    ignored_files = [
        'ignored/draft.md',
        'temp.tmp',
    ]
    for file in ignored_files:
        assert file not in scanner.files, \
            f"Should ignore {file}"
    
    # Test non-ignored files
    assert 'docs/normal.md' in scanner.files, \
        "Should not ignore normal files"

def test_rescan(test_files_root):
    """Test rescanning functionality"""
    test_dir = os.path.join(test_files_root, 'test_case_scanner')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test initial scan
    assert 'docs/index.md' in scanner.files, \
        "Should detect files in initial scan"
    
    # Test rescan
    scanner.scan()
    
    # Test file detection after rescan
    assert 'docs/index.md' in scanner.files, \
        "Should maintain file detection after rescan"
    assert 'index' in scanner.file_names, \
        "Should maintain file names after rescan"
    assert scanner.get_file_mapping('index') == ['docs/index.md'], \
        "Should maintain file mappings after rescan" 