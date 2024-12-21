"""
Tests for reference parser functionality
"""

import pytest
from src.checker.reference_parser import ReferenceParser

def test_basic_references():
    """Test basic reference parsing"""
    text = "Here is a [[link]] and another [[reference]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 2
    assert refs[0] == ('link', 1, False)
    assert refs[1] == ('reference', 1, False)

def test_image_references():
    """Test image reference parsing"""
    text = "Here is an ![[image.png]] and a ![alt](image2.png)"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 1  # Only match ![[...]] style, not ![...](...)
    assert refs[0] == ('image.png', 1, True)

def test_mixed_references():
    """Test mixed reference types"""
    text = "[[doc]] with ![[image.png]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 2
    assert refs[0] == ('doc', 1, False)
    assert refs[1] == ('image.png', 1, True)

def test_references_with_aliases():
    """Test references with aliases"""
    text = "[[file|显示文本]] and ![[image.png|缩略图]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 2
    assert refs[0] == ('file', 1, False)
    assert refs[1] == ('image.png', 1, True)

def test_code_block_exclusion():
    """Test code block exclusion"""
    text = "```\n[[ignored]]\n```\n[[valid]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 1
    assert refs[0] == ('valid', 4, False)

def test_inline_code_exclusion():
    """Test inline code exclusion"""
    text = "Normal `[[ignored]]` and [[valid]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 1
    assert refs[0] == ('valid', 1, False)

def test_task_list_handling():
    """Test task list handling"""
    text = "- [ ] Task with [[link]]\n- [x] Done with ![[image.png]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 2
    assert refs[0] == ('link', 1, False)
    assert refs[1] == ('image.png', 2, True)

def test_list_handling():
    """Test list handling"""
    text = "- Item with [[link]]\n* Another with ![[image.png]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 2
    assert refs[0] == ('link', 1, False)
    assert refs[1] == ('image.png', 2, True)

def test_table_exclusion():
    """Test table syntax exclusion"""
    text = "| [[ignored]] | normal |\n| cell | [[valid]] |"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 0

def test_html_tag_exclusion():
    """Test HTML tag exclusion"""
    text = "<div>[[ignored]]</div> and [[valid]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 1
    assert refs[0] == ('valid', 1, False)

def test_web_url_exclusion():
    """Test web URL exclusion"""
    text = "![alt](https://example.com/image.png) and ![[local.png]]"
    refs = ReferenceParser.find_references_in_text(text, 1)
    
    assert len(refs) == 1
    assert refs[0] == ('local.png', 1, True)

def test_complex_mixed_content():
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
    
    assert len(refs) == 4  # link, image1.png, ref, valid
    assert refs[0][0] == 'link'
    assert refs[1][0] == 'image1.png'
    assert refs[2][0] == 'ref'
    assert refs[3][0] == 'valid' 