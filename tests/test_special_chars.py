import os
from src.check_references import ReferenceChecker

def test_filenames_with_spaces(clean_test_files):
    """测试包含空格的文件名"""
    test_dir = os.path.join(clean_test_files, 'test_case_special_chars')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'with spaces'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'with spaces/doc with spaces.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with spaces')
    with open(os.path.join(test_dir, 'special#chars.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with hash')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    assert 'with spaces/doc with spaces.md' in checker.files, \
        "应该正确识别包含空格的文件名"
    
    # 测试对包含空格的文件的引用解析
    resolved = checker.resolve_link(
        'doc with spaces',
        'special#chars.md',
        is_image=False
    )
    assert resolved == 'with spaces/doc with spaces.md', \
        "应该正确解析包含空格的文件引用"

def test_filenames_with_hash(clean_test_files):
    """测试包含井号的文件名"""
    test_dir = os.path.join(clean_test_files, 'test_case_special_chars')
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'special#chars.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with hash')
    with open(os.path.join(test_dir, 'doc&with&ampersands.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with ampersands')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    assert 'special#chars.md' in checker.files, \
        "应该正确识别包含井号的文件名"
    
    # 测试对包含井号的文件的引用解析
    resolved = checker.resolve_link(
        'special#chars',
        'doc&with&ampersands.md',
        is_image=False
    )
    assert resolved == 'special#chars.md', \
        "应该正确解析包含井号的文件引用"

def test_filenames_with_ampersands(clean_test_files):
    """测试包含&符号的文件名"""
    test_dir = os.path.join(clean_test_files, 'test_case_special_chars')
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'doc&with&ampersands.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with ampersands')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    assert 'doc&with&ampersands.md' in checker.files, \
        "应该正确识别包含&符号的文件名"

def test_relative_paths(clean_test_files):
    """测试相对路径引用"""
    test_dir = os.path.join(clean_test_files, 'test_case_special_chars')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'with spaces'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'with spaces/and#hash'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'with spaces/doc with spaces.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with spaces')
    with open(os.path.join(test_dir, 'with spaces/doc with spaces 2.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with spaces 2')
    with open(os.path.join(test_dir, 'with spaces/and#hash/doc#with#hash.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with hash')
    with open(os.path.join(test_dir, 'special#chars.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with hash')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    # 测试同级目录引用
    resolved = checker.resolve_link(
        'doc with spaces',
        'with spaces/doc with spaces 2.md',
        is_image=False
    )
    assert resolved == 'with spaces/doc with spaces.md', \
        "应该正确解析同级目录的引用"
    
    # 测试父级目录引用
    resolved = checker.resolve_link(
        '../../special#chars',
        'with spaces/and#hash/doc#with#hash.md',
        is_image=False
    )
    assert resolved == 'special#chars.md', \
        "应该正确解析父级目录的引用"

def test_image_references(clean_test_files):
    """测试特殊字符的图片引用"""
    test_dir = os.path.join(clean_test_files, 'test_case_special_chars')
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # 创建测试文件
    with open(os.path.join(test_dir, 'special#chars.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with hash')
    with open(os.path.join(test_dir, 'with spaces/doc with spaces 2.md'), 'w', encoding='utf-8') as f:
        f.write('# Document with spaces 2')
    with open(os.path.join(test_dir, 'assets/image with spaces.png'), 'w', encoding='utf-8') as f:
        f.write('dummy image content')
    with open(os.path.join(test_dir, 'assets/image#with#hash.png'), 'w', encoding='utf-8') as f:
        f.write('dummy image content')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    # 测试包含空格的图片引用
    resolved = checker.resolve_link(
        'image with spaces.png',
        'special#chars.md',
        is_image=True
    )
    assert resolved == 'assets/image with spaces.png', \
        "应该正确解析包含空格的图片引用"
    
    # 测试包含井号的图片引用
    resolved = checker.resolve_link(
        'image#with#hash.png',
        'with spaces/doc with spaces 2.md',
        is_image=True
    )
    assert resolved == 'assets/image#with#hash.png', \
        "应该正确解析包含井号的图片引用" 