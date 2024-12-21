import os
import pytest
from io import StringIO
from unittest.mock import patch
from src.cli import main

def test_basic_command(clean_test_files):
    """Test basic command execution"""
    test_dir = os.path.join(clean_test_files, 'test_case_cli')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'test1.md'), 'w', encoding='utf-8') as f:
        f.write('# Test Document\n\n[[test2]]\n![[image1.png]]')
    
    with open(os.path.join(test_dir, 'test2.md'), 'w', encoding='utf-8') as f:
        f.write('# Test Document 2\n\n[[test1]]')
    
    with open(os.path.join(test_dir, 'assets/image1.png'), 'w') as f:
        f.write('dummy image content')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'error' not in output.lower()

def test_invalid_directory(clean_test_files):
    """Test behavior with invalid directory"""
    test_dir = os.path.join(clean_test_files, 'non_existent_dir')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stderr', new=StringIO()) as fake_err:
            with pytest.raises(SystemExit):
                main()
            assert 'error' in fake_err.getvalue().lower()

def test_broken_references(clean_test_files):
    """Test detection of broken references"""
    test_dir = os.path.join(clean_test_files, 'test_case_cli')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test file with broken reference
    with open(os.path.join(test_dir, 'broken.md'), 'w', encoding='utf-8') as f:
        f.write('# Test Document\n\n[[non_existent]]\n![[missing.png]]')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'non_existent' in output
            assert 'missing.png' in output

def test_ignore_patterns(clean_test_files):
    """Test ignore patterns functionality"""
    test_dir = os.path.join(clean_test_files, 'test_case_cli')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create .mdignore file
    with open(os.path.join(test_dir, '.mdignore'), 'w', encoding='utf-8') as f:
        f.write('ignored/*\n*.draft.md')
    
    # Create test files
    os.makedirs(os.path.join(test_dir, 'ignored'))
    with open(os.path.join(test_dir, 'ignored/test.md'), 'w', encoding='utf-8') as f:
        f.write('# Ignored Document\n\n[[non_existent]]')
    
    with open(os.path.join(test_dir, 'draft.draft.md'), 'w', encoding='utf-8') as f:
        f.write('# Draft Document\n\n[[non_existent]]')
    
    with open(os.path.join(test_dir, 'normal.md'), 'w', encoding='utf-8') as f:
        f.write('# Normal Document\n\n[[test2]]')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'ignored/test.md' not in output
            assert 'draft.draft.md' not in output
            assert 'normal.md' in output

def test_verbose_output(clean_test_files):
    """Test verbose output mode"""
    test_dir = os.path.join(clean_test_files, 'test_case_cli')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'test.md'), 'w', encoding='utf-8') as f:
        f.write('# Test Document\n\n[[test2]]\n![[image.png]]')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir, '--verbose']):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'Scanning directory' in output
            assert 'Checking references' in output 