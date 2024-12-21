import os
from src.check_references import ReferenceChecker

def test_valid_references(clean_test_files):
    """测试有效的引用（非代码块中的引用）"""
    test_dir = os.path.join(clean_test_files, 'test_case_code_blocks')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'main.md'), 'w', encoding='utf-8') as f:
        f.write('''# Main Document
        
[[valid_doc]]
![[real_image.png]]

```python
[[ignored_doc1]]
![[ignored_image1.png]]
```

Here's a valid reference: [[real_doc]]

```
[[ignored_doc4]]
![[ignored_image4.png]]
```

And another valid reference: ![[real_image2.png]]

~~~
[[ignored_doc5]]
![[ignored_image5.png]]
~~~''')
    
    with open(os.path.join(test_dir, 'valid_doc.md'), 'w', encoding='utf-8') as f:
        f.write('# Valid Document')
    with open(os.path.join(test_dir, 'real_doc.md'), 'w', encoding='utf-8') as f:
        f.write('# Real Document')
    
    # 创建图片文件
    for img in ['real_image.png', 'real_image2.png']:
        with open(os.path.join(test_dir, 'assets', img), 'w', encoding='utf-8') as f:
            f.write(f'dummy content for {img}')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # 检查引用统计
    stats = checker.reference_stats
    
    # 验证正常引用被正确统计
    assert 'valid_doc.md' in stats['main.md']['outgoing'], \
        "应该检测到对 valid_doc 的引用"
    assert 'real_doc.md' in stats['main.md']['outgoing'], \
        "应该检测到对 real_doc 的引用"
    
    # 验证图片引用被正确统计
    assert 'assets/real_image.png' in checker.referenced_images, \
        "应该检测到对 real_image.png 的引用"
    assert 'assets/real_image2.png' in checker.referenced_images, \
        "应该检测到对 real_image2.png 的引用"

def test_fenced_code_blocks(clean_test_files):
    """测试围栏式代码块中的引用"""
    test_dir = os.path.join(clean_test_files, 'test_case_code_blocks')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'main.md'), 'w', encoding='utf-8') as f:
        f.write('''# Main Document
        
```python
[[ignored_doc1]]
![[ignored_image1.png]]
```

```
[[ignored_doc2]]
![[ignored_image2.png]]
```

~~~
[[ignored_doc3]]
![[ignored_image3.png]]
~~~

```javascript
[[ignored_doc4]]
![[ignored_image4.png]]
```''')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # 验证围栏式代码块中的引用被忽略
    stats = checker.reference_stats
    ignored_docs = ['ignored_doc1.md', 'ignored_doc2.md', 'ignored_doc3.md', 'ignored_doc4.md']
    for doc in ignored_docs:
        assert doc not in stats['main.md']['outgoing'], \
            f"围栏式代码块中的引用 {doc} 应该被忽略"
    
    # 验证围栏式代码块中的图片引用被忽略
    ignored_images = [
        'assets/ignored_image1.png',
        'assets/ignored_image2.png',
        'assets/ignored_image3.png',
        'assets/ignored_image4.png'
    ]
    for image in ignored_images:
        assert image not in checker.referenced_images, \
            f"围栏式代码块中的图片引用 {image} 应该被忽略"

def test_inline_code_blocks(clean_test_files):
    """测试行内代码块中的引用"""
    test_dir = os.path.join(clean_test_files, 'test_case_code_blocks')
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'main.md'), 'w', encoding='utf-8') as f:
        f.write('''# Main Document
        
Here's some inline code: `[[ignored_doc1]]` and `![[ignored_image1.png]]`

And some more: ``[[ignored_doc2]]`` and ``![[ignored_image2.png]]``

Mixed with valid references: `[[ignored_doc3]]` but [[valid_doc]] and `![[ignored_image3.png]]` but ![[real_image.png]]''')
    
    with open(os.path.join(test_dir, 'valid_doc.md'), 'w', encoding='utf-8') as f:
        f.write('# Valid Document')
    with open(os.path.join(test_dir, 'assets/real_image.png'), 'w', encoding='utf-8') as f:
        f.write('dummy content')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # 验证行内代码块中的引用被忽略
    stats = checker.reference_stats
    ignored_docs = ['ignored_doc1.md', 'ignored_doc2.md', 'ignored_doc3.md']
    for doc in ignored_docs:
        assert doc not in stats['main.md']['outgoing'], \
            f"行内代码块中的引用 {doc} 应该被忽略"
    
    # 验证行内代码块中的图片引用被忽略
    ignored_images = [
        'assets/ignored_image1.png',
        'assets/ignored_image2.png',
        'assets/ignored_image3.png'
    ]
    for image in ignored_images:
        assert image not in checker.referenced_images, \
            f"行内代码块中的图片引用 {image} 应该被忽略"
    
    # 验证正常引用被正确检测
    assert 'valid_doc.md' in stats['main.md']['outgoing'], \
        "应该检测到对 valid_doc 的引用"
    assert 'assets/real_image.png' in checker.referenced_images, \
        "应该检测到对 real_image.png 的引用"

def test_mixed_code_blocks(clean_test_files):
    """测试混合代码块场景"""
    test_dir = os.path.join(clean_test_files, 'test_case_code_blocks')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'main.md'), 'w', encoding='utf-8') as f:
        f.write('''# Main Document
        
Here's a mix of everything:

```python
[[ignored_doc1]]
`[[also_ignored]]`
![[ignored_image1.png]]
```

Normal reference [[valid_doc]] and ![[real_image.png]]

`Inline code with [[ignored_doc2]] and ![[ignored_image2.png]]`

~~~
Fenced code with [[ignored_doc3]] 
and nested `[[still_ignored]]`
and ![[ignored_image3.png]]
~~~''')
    
    with open(os.path.join(test_dir, 'valid_doc.md'), 'w', encoding='utf-8') as f:
        f.write('# Valid Document')
    with open(os.path.join(test_dir, 'assets/real_image.png'), 'w', encoding='utf-8') as f:
        f.write('dummy content')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # 验证所有代码块中的引用都被忽略
    stats = checker.reference_stats
    ignored_docs = [
        'ignored_doc1.md', 'also_ignored.md', 'ignored_doc2.md',
        'ignored_doc3.md', 'still_ignored.md'
    ]
    for doc in ignored_docs:
        assert doc not in stats['main.md']['outgoing'], \
            f"代码块中的引用 {doc} 应该被忽略"
    
    # 验证所有代码块中的图片引用都被忽略
    ignored_images = [
        'assets/ignored_image1.png',
        'assets/ignored_image2.png',
        'assets/ignored_image3.png'
    ]
    for image in ignored_images:
        assert image not in checker.referenced_images, \
            f"代码块中的图片引用 {image} 应该被忽略"
    
    # 验证正常引用被正确检测
    assert 'valid_doc.md' in stats['main.md']['outgoing'], \
        "应该检测到对 valid_doc 的引用"
    assert 'assets/real_image.png' in checker.referenced_images, \
        "应该检测到对 real_image.png 的引用" 