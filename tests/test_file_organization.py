import unittest
import os
import shutil
from src.check_references import ReferenceChecker

class TestFileOrganization(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_organization')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test directory structure
        self.create_test_structure()
        
        self.checker = ReferenceChecker(self.test_dir)
        self.checker.scan_files()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_structure(self):
        """Create test directory structure"""
        # Create root directories with pinyin prefix
        os.makedirs(os.path.join(self.test_dir, 'wl物理'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'sx数学'), exist_ok=True)
        
        # Create subdirectories with Chinese names
        os.makedirs(os.path.join(self.test_dir, 'wl物理/力学'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'sx数学/代数'), exist_ok=True)
        
        # Create assets directory
        os.makedirs(os.path.join(self.test_dir, 'assets'), exist_ok=True)
        
        # Create test files
        self.create_test_files()
    
    def create_test_files(self):
        """Create test files"""
        # Create markdown files in root directories
        with open(os.path.join(self.test_dir, 'wl物理/index.md'), 'w', encoding='utf-8') as f:
            f.write('# 物理学索引\n\n[[力学/牛顿运动定律]]\n![[physics_diagram.png]]')
        
        # Create markdown files in subdirectories
        with open(os.path.join(self.test_dir, 'wl物理/力学/牛顿运动定律.md'), 'w', encoding='utf-8') as f:
            f.write('# 牛顿运动定律\n\n[[../index]]\n![[physics_diagram.png]]')
        
        # Create image files in assets directory
        with open(os.path.join(self.test_dir, 'assets/physics_diagram.png'), 'w') as f:
            f.write('dummy image content')
    
    def test_root_directory_structure(self):
        """Test root directory naming convention"""
        root_dirs = [d for d in os.listdir(self.test_dir) 
                    if os.path.isdir(os.path.join(self.test_dir, d))
                    and d not in ['assets', '__pycache__']]
        
        for dir_name in root_dirs:
            # Check if directory name starts with pinyin
            self.assertTrue(any(c.isalpha() and c.islower() for c in dir_name[:2]),
                          f"Root directory {dir_name} should start with pinyin")
            # Check if directory name contains Chinese characters
            self.assertTrue(any('\u4e00' <= c <= '\u9fff' for c in dir_name),
                          f"Root directory {dir_name} should contain Chinese characters")
    
    def test_subdirectory_naming(self):
        """Test subdirectory naming convention"""
        for root, dirs, _ in os.walk(self.test_dir):
            if 'assets' in root or '__pycache__' in root:
                continue
            
            for dir_name in dirs:
                if dir_name == 'assets' or dir_name.startswith('__'):
                    continue
                
                # 如果是根目录下的目录，应该有拼音前缀
                if os.path.dirname(root) == self.test_dir:
                    self.assertTrue(any(c.isalpha() and c.islower() for c in dir_name[:2]),
                                 f"Root directory {dir_name} should start with pinyin")
                    self.assertTrue(any('\u4e00' <= c <= '\u9fff' for c in dir_name),
                                 f"Root directory {dir_name} should contain Chinese characters")
                else:
                    # 如果是子目录，应该只包含中文字符或常见标点符号
                    valid_chars = set('\u4e00\u9fff-_()（）[]【】')
                    for c in dir_name:
                        self.assertTrue('\u4e00' <= c <= '\u9fff' or c in valid_chars,
                                     f"Subdirectory {dir_name} should only contain Chinese characters and common punctuation")
    
    def test_assets_directory(self):
        """Test assets directory structure"""
        # Check if assets directory exists
        assets_dir = os.path.join(self.test_dir, 'assets')
        self.assertTrue(os.path.exists(assets_dir))
        self.assertTrue(os.path.isdir(assets_dir))
        
        # Check if all image files are in assets directory
        for root, _, files in os.walk(self.test_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    self.assertEqual(os.path.dirname(os.path.join(root, file)),
                                  assets_dir,
                                  f"Image file {file} should be in assets directory")
    
    def test_file_references(self):
        """Test file reference handling"""
        self.checker.check_all_references()
        
        # Check if all references are valid
        self.assertEqual(len(self.checker.invalid_links), 0,
                        f"Found invalid links: {self.checker.invalid_links}")
        
        # Check if all images are referenced
        unused_images = self.checker.image_files - self.checker.referenced_images
        self.assertEqual(len(unused_images), 0,
                        f"Found unused images: {unused_images}")

if __name__ == '__main__':
    unittest.main() 