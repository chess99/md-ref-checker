"""
Tests for ignore rules functionality
"""

import os
import unittest
from src.checker.ignore_rules import IgnoreRules
from tests.utils import create_test_structure, cleanup_test_dir, create_ignore_file

class TestIgnoreRules(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_ignore')
        cleanup_test_dir(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test structure
        self.create_test_files()
        
        # Initialize ignore rules
        self.ignore_rules = IgnoreRules(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        cleanup_test_dir(self.test_dir)
    
    def create_test_files(self):
        """Create test files and directories"""
        # Create .gitignore
        gitignore_patterns = [
            'ignored_dir/*',
            '*.tmp',
            'temp.*',
            'node_modules/',
        ]
        create_ignore_file(self.test_dir, '.gitignore', gitignore_patterns)
        
        # Create .mdignore
        mdignore_patterns = [
            'draft_*',
            '_private/*',
            '*.draft.md',
        ]
        create_ignore_file(self.test_dir, '.mdignore', mdignore_patterns)
        
        # Create test structure
        structure = {
            'ignored_dir': {
                'file1.txt': 'content',
                'file2.md': 'content',
            },
            'normal_dir': {
                'file1.md': 'content',
                'file2.txt': 'content',
            },
            '_private': {
                'secret.md': 'content',
            },
            'draft_post.md': 'draft content',
            'normal_post.md': 'normal content',
            'temp.txt': 'temporary content',
            'file.tmp': 'temporary content',
            'post.draft.md': 'draft content',
        }
        create_test_structure(self.test_dir, structure)
    
    def test_default_patterns(self):
        """Test default ignore patterns"""
        default_ignored = [
            '.git/file.txt',
            '.obsidian/workspace',
            '.trash/deleted.md',
            'node_modules/package.json',
            '.DS_Store',
            'Thumbs.db',
        ]
        
        for path in default_ignored:
            with self.subTest(path=path):
                self.assertTrue(
                    self.ignore_rules.should_ignore(path),
                    f"Should ignore {path}"
                )
    
    def test_gitignore_patterns(self):
        """Test .gitignore patterns"""
        # Test directory patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('ignored_dir/file.txt'),
            "Should ignore files in ignored_dir"
        )
        
        # Test file patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('file.tmp'),
            "Should ignore .tmp files"
        )
        self.assertTrue(
            self.ignore_rules.should_ignore('temp.txt'),
            "Should ignore temp.* files"
        )
        
        # Test non-ignored files
        self.assertFalse(
            self.ignore_rules.should_ignore('normal_dir/file.txt'),
            "Should not ignore files in normal directories"
        )
    
    def test_mdignore_patterns(self):
        """Test .mdignore patterns"""
        # Test prefix patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('draft_post.md'),
            "Should ignore draft_ files"
        )
        
        # Test directory patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('_private/secret.md'),
            "Should ignore files in _private directory"
        )
        
        # Test suffix patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('post.draft.md'),
            "Should ignore .draft.md files"
        )
        
        # Test non-ignored files
        self.assertFalse(
            self.ignore_rules.should_ignore('normal_post.md'),
            "Should not ignore normal files"
        )
    
    def test_add_patterns(self):
        """Test adding custom patterns"""
        # Add custom patterns
        custom_patterns = [
            'custom_*',
            '*.test',
            'test_dir/',
        ]
        self.ignore_rules.add_patterns(custom_patterns)
        
        # Test custom patterns
        self.assertTrue(
            self.ignore_rules.should_ignore('custom_file.txt'),
            "Should ignore custom_* files"
        )
        self.assertTrue(
            self.ignore_rules.should_ignore('file.test'),
            "Should ignore .test files"
        )
        self.assertTrue(
            self.ignore_rules.should_ignore('test_dir/file.txt'),
            "Should ignore files in test_dir"
        )
    
    def test_pattern_precedence(self):
        """Test pattern precedence"""
        # Add a pattern that would match everything
        self.ignore_rules.add_patterns(['*'])
        
        # Add a negation pattern
        self.ignore_rules.add_patterns(['!important.md'])
        
        # The more specific pattern should take precedence
        self.assertTrue(
            self.ignore_rules.should_ignore('random.txt'),
            "Should ignore random files"
        )
        self.assertFalse(
            self.ignore_rules.should_ignore('important.md'),
            "Should not ignore important.md"
        )

if __name__ == '__main__':
    unittest.main() 