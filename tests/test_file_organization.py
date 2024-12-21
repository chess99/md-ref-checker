import os
from src.check_references import ReferenceChecker

def test_root_directory_structure(clean_test_files):
    """Test root directory naming convention"""
    test_dir = os.path.join(clean_test_files, 'test_case_organization')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create root directories with pinyin prefix
    os.makedirs(os.path.join(test_dir, 'wl物理'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学'), exist_ok=True)
    
    # Create subdirectories with Chinese names
    os.makedirs(os.path.join(test_dir, 'wl物理/力学'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学/代数'), exist_ok=True)
    
    # Create assets directory
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'wl物理/index.md'), 'w', encoding='utf-8') as f:
        f.write('# 物理学索引\n\n[[力学/牛顿运动定律]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'wl物理/力学/牛顿运动定律.md'), 'w', encoding='utf-8') as f:
        f.write('# 牛顿运动定律\n\n[[../index]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'assets/physics_diagram.png'), 'w') as f:
        f.write('dummy image content')
    
    root_dirs = [d for d in os.listdir(test_dir) 
                if os.path.isdir(os.path.join(test_dir, d))
                and d not in ['assets', '__pycache__']]
    
    for dir_name in root_dirs:
        # Check if directory name starts with pinyin
        assert any(c.isalpha() and c.islower() for c in dir_name[:2]), \
            f"Root directory {dir_name} should start with pinyin"
        # Check if directory name contains Chinese characters
        assert any('\u4e00' <= c <= '\u9fff' for c in dir_name), \
            f"Root directory {dir_name} should contain Chinese characters"

def test_assets_directory(clean_test_files):
    """Test assets directory structure"""
    test_dir = os.path.join(clean_test_files, 'test_case_organization')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create root directories with pinyin prefix
    os.makedirs(os.path.join(test_dir, 'wl物理'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学'), exist_ok=True)
    
    # Create subdirectories with Chinese names
    os.makedirs(os.path.join(test_dir, 'wl物理/力学'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学/代数'), exist_ok=True)
    
    # Create assets directory
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'wl物理/index.md'), 'w', encoding='utf-8') as f:
        f.write('# 物理学索引\n\n[[力学/牛顿运动定律]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'wl物理/力学/牛顿运动定律.md'), 'w', encoding='utf-8') as f:
        f.write('# 牛顿运动定律\n\n[[../index]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'assets/physics_diagram.png'), 'w') as f:
        f.write('dummy image content')
    
    # Check if assets directory exists
    assets_dir = os.path.join(test_dir, 'assets')
    assert os.path.exists(assets_dir)
    assert os.path.isdir(assets_dir)
    
    # Check if all image files are in assets directory
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                assert os.path.dirname(os.path.join(root, file)) == assets_dir, \
                    f"Image file {file} should be in assets directory"

def test_file_references(clean_test_files):
    """Test file reference handling"""
    test_dir = os.path.join(clean_test_files, 'test_case_organization')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create root directories with pinyin prefix
    os.makedirs(os.path.join(test_dir, 'wl物理'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学'), exist_ok=True)
    
    # Create subdirectories with Chinese names
    os.makedirs(os.path.join(test_dir, 'wl物理/力学'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'sx数学/代数'), exist_ok=True)
    
    # Create assets directory
    os.makedirs(os.path.join(test_dir, 'assets'), exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'wl物理/index.md'), 'w', encoding='utf-8') as f:
        f.write('# 物理学索引\n\n[[力学/牛顿运动定律]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'wl物理/力学/牛顿运动定律.md'), 'w', encoding='utf-8') as f:
        f.write('# 牛顿运动定律\n\n[[../index]]\n![[physics_diagram.png]]')
    
    with open(os.path.join(test_dir, 'assets/physics_diagram.png'), 'w') as f:
        f.write('dummy image content')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Check if all references are valid
    assert len(checker.invalid_links) == 0, \
        f"Found invalid links: {checker.invalid_links}"
    
    # Check if all images are referenced
    unused_images = checker.image_files - checker.referenced_images
    assert len(unused_images) == 0, \
        f"Found unused images: {unused_images}" 