import os
from src.check_references import ReferenceChecker

def test_root_directory_structure(test_files_root):
    """Test root directory naming convention"""
    test_dir = os.path.join(test_files_root, 'test_case_organization')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
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

def test_assets_directory(test_files_root):
    """Test assets directory structure"""
    test_dir = os.path.join(test_files_root, 'test_case_organization')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
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

def test_file_references(test_files_root):
    """Test file reference handling"""
    test_dir = os.path.join(test_files_root, 'test_case_organization')
    
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