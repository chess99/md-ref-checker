"""
Tests for reference parser functionality
"""

import os
from src.checker.reference_parser import ReferenceParser

def test_basic_reference_parsing():
    """Test basic reference parsing"""
    parser = ReferenceParser()
    
    # Test basic markdown reference
    content = "Here is a [[link]] to another document"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("link", False)
    
    # Test basic image reference
    content = "Here is an ![[image.png]] embedded in the document"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("image.png", True)

def test_multiple_references():
    """Test parsing multiple references"""
    parser = ReferenceParser()
    
    content = """# Document with multiple references
    
Here is a [[link1]] and another [[link2]].
And some images: ![[image1.png]] and ![[image2.jpg]]"""
    
    refs = parser.parse_references(content)
    assert len(refs) == 4
    assert ("link1", False) in refs
    assert ("link2", False) in refs
    assert ("image1.png", True) in refs
    assert ("image2.jpg", True) in refs

def test_reference_with_alias():
    """Test parsing references with aliases"""
    parser = ReferenceParser()
    
    # Test markdown reference with alias
    content = "Here is a [[actual_link|Displayed Text]]"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("actual_link", False)
    
    # Test image reference with alias
    content = "Here is an ![[actual_image.png|alt text]]"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("actual_image.png", True)

def test_reference_in_code_blocks():
    """Test handling references in code blocks"""
    parser = ReferenceParser()
    
    # Test references in inline code
    content = "This is `[[not a reference]]` in code"
    refs = parser.parse_references(content)
    assert len(refs) == 0
    
    # Test references in fenced code blocks
    content = """Here is a code block:
```
[[not a reference]]
![[not an image]]
```
But this [[is a reference]]"""
    
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("is a reference", False)

def test_special_characters():
    """Test parsing references with special characters"""
    parser = ReferenceParser()
    
    # Test spaces in reference
    content = "[[file with spaces]]"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("file with spaces", False)
    
    # Test special characters in reference
    content = "[[file#with#hash]] and [[file&with&ampersand]]"
    refs = parser.parse_references(content)
    assert len(refs) == 2
    assert ("file#with#hash", False) in refs
    assert ("file&with&ampersand", False) in refs
    
    # Test Unicode characters
    content = "[[文件名]] and ![[图片.png]]"
    refs = parser.parse_references(content)
    assert len(refs) == 2
    assert ("文件名", False) in refs
    assert ("图片.png", True) in refs

def test_nested_references():
    """Test handling nested references"""
    parser = ReferenceParser()
    
    # Test nested markdown references
    content = "[[outer [[inner]] reference]]"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("outer [[inner]] reference", False)
    
    # Test nested image references
    content = "![[outer ![[inner]] image]]"
    refs = parser.parse_references(content)
    assert len(refs) == 1
    assert refs[0] == ("outer ![[inner]] image", True)

def test_invalid_references():
    """Test handling invalid reference formats"""
    parser = ReferenceParser()
    
    # Test unclosed references
    content = "[[unclosed reference"
    refs = parser.parse_references(content)
    assert len(refs) == 0
    
    # Test empty references
    content = "[[]] and ![[]]"
    refs = parser.parse_references(content)
    assert len(refs) == 0
    
    # Test malformed references
    content = "[ [not a reference]] and ![not an image]]"
    refs = parser.parse_references(content)
    assert len(refs) == 0