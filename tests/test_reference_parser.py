"""Test reference parser"""

import pytest
from src.checker.reference_parser import ReferenceParser

@pytest.fixture
def parser() -> ReferenceParser:
    """创建引用解析器实例"""
    return ReferenceParser()

def test_parse_markdown_links(parser: ReferenceParser) -> None:
    """测试 Markdown 链接解析"""
    content = """
    # Test Document
    [Link 1](doc1.md)
    [Link 2](./doc2.md)
    [Link 3](../doc3.md)
    [External](https://example.com)
    [Anchor](#section)
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 3
    assert ('doc1.md', False) in refs
    assert ('doc2.md', False) in refs
    assert ('../doc3.md', False) in refs

def test_parse_image_links(parser: ReferenceParser) -> None:
    """测试图片链接解析"""
    content = """
    # Test Document
    ![Image 1](img1.png)
    ![Image 2](./img2.jpg)
    ![Image 3](https://example.com/img.png)
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 2
    assert ('img1.png', True) in refs
    assert ('img2.jpg', True) in refs

def test_parse_wiki_links(parser: ReferenceParser) -> None:
    """测试 Wiki 风格链接解析"""
    content = """
    # Test Document
    [[Page 1]]
    [[Page 2|Alias]]
    ![[Image 1]]
    ![[Image 2|Caption]]
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 4
    assert ('Page 1', False) in refs
    assert ('Page 2', False) in refs
    assert ('Image 1', True) in refs
    assert ('Image 2', True) in refs

def test_ignore_code_blocks(parser: ReferenceParser) -> None:
    """测试代码块忽略"""
    content = """
    # Test Document
    [Real Link](doc.md)
    
    ```python
    # This is a code block
    [Fake Link](code.md)
    ```
    
    `[Inline Code](code.md)`
    
    [Another Real Link](doc2.md)
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 2
    assert ('doc.md', False) in refs
    assert ('doc2.md', False) in refs

def test_ignore_html_comments(parser: ReferenceParser) -> None:
    """测试 HTML 注释忽略"""
    content = """
    # Test Document
    [Real Link](doc.md)
    
    <!-- 
    This is a comment
    [Fake Link](comment.md)
    -->
    
    [Another Real Link](doc2.md)
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 2
    assert ('doc.md', False) in refs
    assert ('doc2.md', False) in refs

def test_mixed_content(parser: ReferenceParser) -> None:
    """测试混合内容"""
    content = """
    # Test Document
    [Link](doc1.md)
    ![Image](img1.png)
    [[Wiki Link]]
    ![[Wiki Image]]
    
    ```python
    # Code block
    [Fake](code.md)
    ```
    
    <!--
    [Comment](comment.md)
    -->
    
    [External](https://example.com)
    [Anchor](#section)
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 4
    assert ('doc1.md', False) in refs
    assert ('img1.png', True) in refs
    assert ('Wiki Link', False) in refs
    assert ('Wiki Image', True) in refs

def test_duplicate_references(parser: ReferenceParser) -> None:
    """测试重复引用"""
    content = """
    # Test Document
    [Link](doc.md)
    [Same Link](doc.md)
    ![Image](img.png)
    ![Same Image](img.png)
    [[Page]]
    [[Page|Alias]]
    """
    refs = parser.parse_references(content)
    
    assert len(refs) == 3
    assert ('doc.md', False) in refs
    assert ('img.png', True) in refs
    assert ('Page', False) in refs