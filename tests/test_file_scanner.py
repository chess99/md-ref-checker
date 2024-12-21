"""
Tests for file scanner functionality
"""

import os
import unittest
from src.checker.ignore_rules import IgnoreRules
from src.checker.file_scanner import FileScanner
from tests.utils import create_test_structure, cleanup_test_dir

class TestFileScanner(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_scanner')
        cleanup_test_dir(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test structure
        self.create_test_files()
        
        # Initialize scanner
        self.ignore_rules = IgnoreRules(self.test_dir)
        self.scanner = FileScanner(self.test_dir, self.ignore_rules)
        self.scanner.scan()
    
    def tearDown(self):
        """Clean up test environment"""
        cleanup_test_dir(self.test_dir)
    
    def create_test_files(self):
        """Create test files and directories"""
        structure = {
            'docs': {
                'index.md': '# Index\n[[doc1]]\n[[doc2]]',
                'doc1.md': '# Doc 1\n[[index]]\n![[image1.png]]',
                'doc2.md': '# Doc 2\n[[doc1]]',
            },
            'assets': {
                'image1.png': 'dummy image content',
                'image2.jpg': 'dummy image content',
                'unused.png': 'dummy image content',
            },
            'ignored': {
                'draft.md': '# Draft',
                'temp.txt': 'temp content',
            },
        }
        create_test_structure(self.test_dir, structure)
    
    def test_file_scanning(self):
        """Test basic file scanning"""
        # Test markdown files
        expected_md_files = {
            'docs/index.md',
            'docs/doc1.md',
            'docs/doc2.md',
        }
        actual_md_files = {f for f in self.scanner.files if f.endswith('.md')}
        self.assertEqual(actual_md_files, expected_md_files)
        
        # Test image files
        expected_image_files = {
            'assets/image1.png',
            'assets/image2.jpg',
            'assets/unused.png',
        }
        self.assertEqual(self.scanner.image_files, expected_image_files)
    
    def test_file_mapping(self):
        """Test file mapping functionality"""
        # Test complete path mapping
        self.assertEqual(
            self.scanner.get_file_mapping('docs/index.md'),
            ['docs/index.md']
        )
        
        # Test base name mapping
        index_mappings = self.scanner.get_file_mapping('index')
        self.assertEqual(len(index_mappings), 1)
        self.assertIn('docs/index.md', index_mappings)
        
        # Test image mapping
        image_mappings = self.scanner.get_file_mapping('image1.png')
        self.assertEqual(len(image_mappings), 1)
        self.assertIn('assets/image1.png', image_mappings)
    
    def test_file_names(self):
        """Test file names collection"""
        expected_names = {
            'index',
            'doc1',
            'doc2',
            'image1',
            'image2',
            'unused',
        }
        self.assertEqual(self.scanner.file_names, expected_names)
    
    def test_ignore_rules(self):
        """Test ignore rules integration"""
        # Ignored files should not be included
        ignored_files = [
            'ignored/draft.md',
            'ignored/temp.txt',
        ]
        for file in ignored_files:
            self.assertNotIn(file, self.scanner.files)
    
    def test_rescan(self):
        """Test rescanning functionality"""
        # Add a new file
        new_file = os.path.join(self.test_dir, 'docs/new_doc.md')
        with open(new_file, 'w', encoding='utf-8') as f:
            f.write('# New Doc\n[[index]]')
        
        # Rescan
        self.scanner.scan()
        
        # Check if new file is included
        self.assertIn('docs/new_doc.md', self.scanner.files)
        self.assertIn('new_doc', self.scanner.file_names)
        self.assertEqual(
            self.scanner.get_file_mapping('new_doc'),
            ['docs/new_doc.md']
        )

if __name__ == '__main__':
    unittest.main() 