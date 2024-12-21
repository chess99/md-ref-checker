"""
Tests for utility functions
"""

import unittest
from src.checker.utils import normalize_path, is_image_file, is_markdown_file, get_valid_chars

class TestUtils(unittest.TestCase):
    def test_normalize_path(self):
        """Test path normalization"""
        test_cases = [
            ('path/to/file', 'path/to/file'),
            ('path\\to\\file', 'path/to/file'),
            ('./path/to/file', 'path/to/file'),
            ('.\\path\\to\\file', 'path/to/file'),
            ('path/../file', 'path/../file'),
            ('path/./file', 'path/./file'),
        ]
        
        for input_path, expected in test_cases:
            with self.subTest(input_path=input_path):
                self.assertEqual(normalize_path(input_path), expected)
    
    def test_is_image_file(self):
        """Test image file detection"""
        image_files = [
            'image.png',
            'photo.jpg',
            'photo.jpeg',
            'animation.gif',
            'vector.svg',
            'image.webp',
            'IMAGE.PNG',
            'PHOTO.JPG',
        ]
        
        non_image_files = [
            'document.md',
            'script.py',
            'image.txt',
            'photo',
            '.png',
            'image.doc',
        ]
        
        for filename in image_files:
            with self.subTest(filename=filename):
                self.assertTrue(is_image_file(filename))
        
        for filename in non_image_files:
            with self.subTest(filename=filename):
                self.assertFalse(is_image_file(filename))
    
    def test_is_markdown_file(self):
        """Test Markdown file detection"""
        markdown_files = [
            'document.md',
            'README.md',
            'notes.MD',
            'doc.markdown',
            'CAPS.MD',
        ]
        
        non_markdown_files = [
            'document.txt',
            'script.py',
            'doc',
            '.md',
            'markdown',
            'md.doc',
        ]
        
        for filename in markdown_files:
            with self.subTest(filename=filename):
                self.assertTrue(is_markdown_file(filename))
        
        for filename in non_markdown_files:
            with self.subTest(filename=filename):
                self.assertFalse(is_markdown_file(filename))
    
    def test_get_valid_chars(self):
        """Test valid characters set"""
        valid_chars = get_valid_chars()
        
        # 测试中文字符
        self.assertTrue('\u4e00' in valid_chars)
        self.assertTrue('\u9fff' in valid_chars)
        
        # 测试标点符号
        punctuation = '-_()（）[]【】'
        for char in punctuation:
            with self.subTest(char=char):
                self.assertTrue(char in valid_chars)
        
        # 测试无效字符
        invalid_chars = ['$', '#', '@', '&', '*', '?', '!']
        for char in invalid_chars:
            with self.subTest(char=char):
                self.assertFalse(char in valid_chars)

if __name__ == '__main__':
    unittest.main() 