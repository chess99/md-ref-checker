"""
Tests for reference parser functionality
"""

import unittest
from src.checker.reference_parser import ReferenceParser

class TestReferenceParser(unittest.TestCase):
    def test_basic_references(self):
        """Test basic reference parsing"""
        text = "Here is a [[link]] and another [[reference]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0], ('link', 1, 11, text, False))
        self.assertEqual(refs[1], ('reference', 1, 28, text, False))
    
    def test_image_references(self):
        """Test image reference parsing"""
        text = "Here is an ![[image.png]] and a ![alt](image2.png)"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0], ('image.png', 1, 13, text, True))
        self.assertEqual(refs[1], ('image2.png', 1, 35, text, True))
    
    def test_mixed_references(self):
        """Test mixed reference types"""
        text = "[[doc]] with ![[image.png]] and ![alt](photo.jpg)"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 3)
        self.assertEqual(refs[0], ('doc', 1, 3, text, False))
        self.assertEqual(refs[1], ('image.png', 1, 15, text, True))
        self.assertEqual(refs[2], ('photo.jpg', 1, 37, text, True))
    
    def test_references_with_aliases(self):
        """Test references with aliases"""
        text = "[[file|显示文本]] and ![[image.png|缩略图]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0], ('file', 1, 3, text, False))
        self.assertEqual(refs[1], ('image.png', 1, 24, text, True))
    
    def test_code_block_exclusion(self):
        """Test code block exclusion"""
        text = "```\n[[ignored]]\n```\n[[valid]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0], ('valid', 1, 18, text, False))
    
    def test_inline_code_exclusion(self):
        """Test inline code exclusion"""
        text = "Normal `[[ignored]]` and [[valid]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0], ('valid', 1, 27, text, False))
    
    def test_task_list_handling(self):
        """Test task list handling"""
        text = "- [ ] Task with [[link]]\n- [x] Done with ![[image.png]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0], ('link', 1, 17, text, False))
        self.assertEqual(refs[1], ('image.png', 1, 41, text, True))
    
    def test_list_handling(self):
        """Test list handling"""
        text = "- Item with [[link]]\n* Another with ![[image.png]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0], ('link', 1, 14, text, False))
        self.assertEqual(refs[1], ('image.png', 1, 37, text, True))
    
    def test_table_exclusion(self):
        """Test table syntax exclusion"""
        text = "| [[ignored]] | normal |\n| cell | [[valid]] |"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 0)
    
    def test_html_tag_exclusion(self):
        """Test HTML tag exclusion"""
        text = "<div>[[ignored]]</div> and [[valid]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0], ('valid', 1, 27, text, False))
    
    def test_web_url_exclusion(self):
        """Test web URL exclusion"""
        text = "![alt](https://example.com/image.png) and ![[local.png]]"
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0], ('local.png', 1, 44, text, True))
    
    def test_complex_mixed_content(self):
        """Test complex mixed content"""
        text = """
        # Title with [[link]]
        - [ ] Task with ![[image1.png]]
        ```python
        # [[ignored]] in code
        ```
        1. List with [[ref|alias]]
        > Quote with ![[image2.png|thumb]]
        | [[ignored]] | in table |
        Normal `[[ignored]]` text
        <div>[[ignored]]</div>
        ![](https://example.com/img.jpg)
        Last [[valid]] reference
        """
        refs = ReferenceParser.find_references_in_text(text, 1)
        
        self.assertEqual(len(refs), 5)
        self.assertEqual(refs[0][0], 'link')
        self.assertEqual(refs[1][0], 'image1.png')
        self.assertEqual(refs[2][0], 'ref')
        self.assertEqual(refs[3][0], 'image2.png')
        self.assertEqual(refs[4][0], 'valid')

if __name__ == '__main__':
    unittest.main() 