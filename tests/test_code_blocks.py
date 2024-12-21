import os
from src.check_references import ReferenceChecker

def test_valid_references(test_files_root):
    """测试有效的引用（非代码块中的引用）"""
    test_dir = os.path.join(test_files_root, 'test_case_code_blocks')
    
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

def test_fenced_code_blocks(test_files_root):
    """测试围栏式代码块中的引用"""
    test_dir = os.path.join(test_files_root, 'test_case_code_blocks')
    
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

def test_inline_code_blocks(test_files_root):
    """测试行内代码块中的引用"""
    test_dir = os.path.join(test_files_root, 'test_case_code_blocks')
    
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

def test_mixed_code_blocks(test_files_root):
    """测试混合代码块场景"""
    test_dir = os.path.join(test_files_root, 'test_case_code_blocks')
    
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