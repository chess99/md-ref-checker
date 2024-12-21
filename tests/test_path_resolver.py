"""
Tests for path resolver functionality
"""

import os
import unittest
from src.checker.ignore_rules import IgnoreRules
from src.checker.file_scanner import FileScanner
from src.checker.path_resolver import PathResolver
from tests.utils import create_test_structure, cleanup_test_dir

class TestPathResolver(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_resolver')
        cleanup_test_dir(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test structure
        self.create_test_files()
        
        # Initialize components
        self.ignore_rules = IgnoreRules(self.test_dir)
        self.file_scanner = FileScanner(self.test_dir, self.ignore_rules)
        self.file_scanner.scan()
        self.resolver = PathResolver(self.file_scanner)
    
    def tearDown(self):
        """Clean up test environment"""
        cleanup_test_dir(self.test_dir)
    
    def create_test_files(self):
        """Create test files and directories"""
        structure = {
            'docs': {
                'index.md': '# Index',
                'subfolder': {
                    'doc1.md': '# Doc 1',
                    'doc2.md': '# Doc 2',
                },
            },
            'assets': {
                'image1.png': 'dummy image content',
                'subfolder': {
                    'image2.jpg': 'dummy image content',
                },
            },
            'README.md': '# README',
        }
        create_test_structure(self.test_dir, structure)
    
    def test_absolute_paths(self):
        """Test absolute path resolution"""
        # Test markdown file
        resolved = self.resolver.resolve_link(
            '/docs/index',
            'README.md',
            is_image=False
        )
        self.assertEqual(resolved, 'docs/index.md')
        
        # Test image file
        resolved = self.resolver.resolve_link(
            '/assets/image1.png',
            'README.md',
            is_image=True
        )
        self.assertEqual(resolved, 'assets/image1.png')
    
    def test_relative_paths(self):
        """Test relative path resolution"""
        # Test same directory
        resolved = self.resolver.resolve_link(
            'doc2',
            'docs/subfolder/doc1.md',
            is_image=False
        )
        self.assertEqual(resolved, 'docs/subfolder/doc2.md')
        
        # Test parent directory
        resolved = self.resolver.resolve_link(
            '../index',
            'docs/subfolder/doc1.md',
            is_image=False
        )
        self.assertEqual(resolved, 'docs/index.md')
        
        # Test image in parent directory
        resolved = self.resolver.resolve_link(
            '../image1.png',
            'assets/subfolder/image2.jpg',
            is_image=True
        )
        self.assertEqual(resolved, 'assets/image1.png')
    
    def test_image_resolution(self):
        """Test image path resolution"""
        # Test direct reference
        resolved = self.resolver.resolve_link(
            'image1.png',
            'README.md',
            is_image=True
        )
        self.assertEqual(resolved, 'assets/image1.png')
        
        # Test subfolder reference
        resolved = self.resolver.resolve_link(
            'subfolder/image2.jpg',
            'README.md',
            is_image=True
        )
        self.assertEqual(resolved, 'assets/subfolder/image2.jpg')
        
        # Test non-existent image
        resolved = self.resolver.resolve_link(
            'non_existent.png',
            'README.md',
            is_image=True
        )
        self.assertEqual(resolved, 'assets/non_existent.png')
    
    def test_markdown_resolution(self):
        """Test markdown file resolution"""
        # Test with extension
        resolved = self.resolver.resolve_link(
            'index.md',
            'README.md',
            is_image=False
        )
        self.assertEqual(resolved, 'docs/index.md')
        
        # Test without extension
        resolved = self.resolver.resolve_link(
            'index',
            'README.md',
            is_image=False
        )
        self.assertEqual(resolved, 'docs/index.md')
        
        # Test non-existent file
        resolved = self.resolver.resolve_link(
            'non_existent',
            'README.md',
            is_image=False
        )
        self.assertEqual(resolved, 'non_existent.md')
    
    def test_referenced_images(self):
        """Test referenced images tracking"""
        # Reference some images
        self.resolver.resolve_link('image1.png', 'README.md', is_image=True)
        self.resolver.resolve_link('subfolder/image2.jpg', 'README.md', is_image=True)
        
        # Check referenced images
        expected_refs = {
            'assets/image1.png',
            'assets/subfolder/image2.jpg',
        }
        self.assertEqual(self.resolver.referenced_images, expected_refs)

if __name__ == '__main__':
    unittest.main() 