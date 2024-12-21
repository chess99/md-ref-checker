"""
Tests for file scanner functionality
"""

import os
from src.checker.ignore_rules import IgnoreRules
from src.checker.file_scanner import FileScanner

def test_file_scanning(clean_test_files):
    """Test basic file scanning"""
    test_dir = os.path.join(clean_test_files, 'test_case_scanner')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test structure
    os.makedirs(os.path.join(test_dir, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'ignored'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'docs/index.md'), 'w', encoding='utf-8') as f:
        f.write('# Index\n[[doc1]]\n[[doc2]]')
    with open(os.path.join(test_dir, 'docs/doc1.md'), 'w', encoding='utf-8') as f:
        f.write('# Doc 1\n[[index]]\n![[image1.png]]')
    with open(os.path.join(test_dir, 'docs/doc2.md'), 'w', encoding='utf-8') as f:
        f.write('# Doc 2\n[[doc1]]')
    with open(os.path.join(test_dir, 'assets/image1.png'), 'w') as f:
        f.write('dummy image content')
    with open(os.path.join(test_dir, 'assets/image2.jpg'), 'w') as f:
        f.write('dummy image content')
    with open(os.path.join(test_dir, 'assets/unused.png'), 'w') as f:
        f.write('dummy image content')
    with open(os.path.join(test_dir, 'ignored/draft.md'), 'w') as f:
        f.write('# Draft')
    with open(os.path.join(test_dir, 'ignored/temp.txt'), 'w') as f:
        f.write('temp content')
    
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

def test_file_mapping(clean_test_files):
    """Test file mapping functionality"""
    test_dir = os.path.join(clean_test_files, 'test_case_scanner')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test structure
    os.makedirs(os.path.join(test_dir, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'docs/index.md'), 'w', encoding='utf-8') as f:
        f.write('# Index')
    with open(os.path.join(test_dir, 'assets/image1.png'), 'w') as f:
        f.write('dummy image content')
    
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

def test_file_names(clean_test_files):
    """Test file names collection"""
    test_dir = os.path.join(clean_test_files, 'test_case_scanner')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test structure
    os.makedirs(os.path.join(test_dir, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'docs/index.md'), 'w', encoding='utf-8') as f:
        f.write('# Index')
    with open(os.path.join(test_dir, 'docs/doc1.md'), 'w', encoding='utf-8') as f:
        f.write('# Doc 1')
    with open(os.path.join(test_dir, 'assets/image1.png'), 'w') as f:
        f.write('dummy image content')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Test file names
    expected_names = {
        'index',
        'doc1',
        'image1',
    }
    assert scanner.file_names == expected_names, \
        "Should correctly collect file names"

def test_ignore_rules(clean_test_files):
    """Test ignore rules integration"""
    test_dir = os.path.join(clean_test_files, 'test_case_scanner')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test structure
    os.makedirs(os.path.join(test_dir, 'ignored'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'docs'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write('ignored/\n*.tmp\n')
    with open(os.path.join(test_dir, 'ignored/draft.md'), 'w') as f:
        f.write('# Draft')
    with open(os.path.join(test_dir, 'docs/normal.md'), 'w') as f:
        f.write('# Normal')
    with open(os.path.join(test_dir, 'temp.tmp'), 'w') as f:
        f.write('temp content')
    
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

def test_rescan(clean_test_files):
    """Test rescanning functionality"""
    test_dir = os.path.join(clean_test_files, 'test_case_scanner')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create initial test structure
    os.makedirs(os.path.join(test_dir, 'docs'), exist_ok=True)
    with open(os.path.join(test_dir, 'docs/index.md'), 'w', encoding='utf-8') as f:
        f.write('# Index')
    
    # Initialize scanner
    ignore_rules = IgnoreRules(test_dir)
    scanner = FileScanner(test_dir, ignore_rules)
    scanner.scan()
    
    # Add new file
    with open(os.path.join(test_dir, 'docs/new_doc.md'), 'w', encoding='utf-8') as f:
        f.write('# New Doc')
    
    # Rescan
    scanner.scan()
    
    # Test new file detection
    assert 'docs/new_doc.md' in scanner.files, \
        "Should detect new files after rescan"
    assert 'new_doc' in scanner.file_names, \
        "Should update file names after rescan"
    assert scanner.get_file_mapping('new_doc') == ['docs/new_doc.md'], \
        "Should update file mappings after rescan" 