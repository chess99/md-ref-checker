import os
import pytest
from io import StringIO
from unittest.mock import patch
from src.cli import main

def test_basic_command(test_files_root):
    """Test basic command execution"""
    test_dir = os.path.join(test_files_root, 'test_case_cli')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'error' not in output.lower()

def test_invalid_directory(test_files_root):
    """Test behavior with invalid directory"""
    test_dir = os.path.join(test_files_root, 'non_existent_dir')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stderr', new=StringIO()) as fake_err:
            with pytest.raises(SystemExit):
                main()
            assert 'error' in fake_err.getvalue().lower()

def test_broken_references(test_files_root):
    """Test detection of broken references"""
    test_dir = os.path.join(test_files_root, 'test_case_cli')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'non_existent' in output
            assert 'missing.png' in output

def test_ignore_patterns(test_files_root):
    """Test ignore patterns functionality"""
    test_dir = os.path.join(test_files_root, 'test_case_cli')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'ignored/test.md' not in output
            assert 'draft.draft.md' not in output
            assert 'normal.md' in output

def test_verbose_output(test_files_root):
    """Test verbose output mode"""
    test_dir = os.path.join(test_files_root, 'test_case_cli')
    
    with patch('sys.argv', ['md-ref-checker', '--dir', test_dir, '--verbose']):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert 'Scanning directory' in output
            assert 'Checking references' in output