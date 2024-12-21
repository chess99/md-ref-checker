import unittest
import os
from src.check_references import ReferenceChecker

class TestSpecialChars(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_special_chars')
        self.checker = ReferenceChecker(self.test_dir)
        self.checker.scan_files()
        
    def test_filenames_with_spaces(self):
        """测试包含空格的文件名"""
        self.assertIn(
            'with spaces/doc with spaces.md',
            self.checker.files,
            "应该正确识别包含空格的文件名"
        )
        
        # 测试对包含空格的文件的引用解析
        resolved = self.checker.resolve_link(
            'doc with spaces',
            'special#chars.md',
            is_image=False
        )
        self.assertEqual(
            resolved,
            'with spaces/doc with spaces.md',
            "应该正确解析包含空格的文件引用"
        )
        
    def test_filenames_with_hash(self):
        """测试包含井号的文件名"""
        # 测试井号在文件名中的处理
        self.assertIn(
            'special#chars.md',
            self.checker.files,
            "应该正确识别包含井号的文件名"
        )
        
        # 测试��包含井号的文件的引用解析
        resolved = self.checker.resolve_link(
            'special#chars',
            'doc&with&ampersands.md',
            is_image=False
        )
        self.assertEqual(
            resolved,
            'special#chars.md',
            "应该正确解析包含井号的文件引用"
        )
        
    def test_filenames_with_ampersands(self):
        """测试包含&符号的文件名"""
        # 测试&符号在文件名中的处理
        self.assertIn(
            'doc&with&ampersands.md',
            self.checker.files,
            "应该正确识别包含&符号的文件名"
        )
        
    def test_relative_paths(self):
        """测试相对路径引用"""
        # 测试同级目录引用
        resolved = self.checker.resolve_link(
            'doc with spaces',
            'with spaces/doc with spaces 2.md',
            is_image=False
        )
        self.assertEqual(
            resolved,
            'with spaces/doc with spaces.md',
            "应该正确解析同级目录的引用"
        )
        
        # 测试父级目录引用
        resolved = self.checker.resolve_link(
            '../../special#chars',
            'with spaces/and#hash/doc#with#hash.md',
            is_image=False
        )
        self.assertEqual(
            resolved,
            'special#chars.md',
            "应该正确解析父级目录的引用"
        )
        
    def test_image_references(self):
        """测试特殊字符的图片引用"""
        # 测试包含空格的图片引用
        resolved = self.checker.resolve_link(
            'image with spaces.png',
            'special#chars.md',
            is_image=True
        )
        self.assertEqual(
            resolved,
            'assets/image with spaces.png',
            "应该正确解析包含空格的图片引用"
        )
        
        # 测试包含井号的图片引用
        resolved = self.checker.resolve_link(
            'image#with#hash.png',
            'with spaces/doc with spaces 2.md',
            is_image=True
        )
        self.assertEqual(
            resolved,
            'assets/image#with#hash.png',
            "应该正确解析包含井号的图片引用"
        )
        
    def test_reference_checking(self):
        """测试包含特殊字符的引用检查"""
        self.checker.check_all_references()
        
        # 检查引用统计
        stats = self.checker.reference_stats
        
        # 验证包含特殊字符的文件引用是否正确统计
        self.assertIn(
            'with spaces/doc with spaces.md',
            stats['special#chars.md']['outgoing'],
            "应该正确统计包含特殊字符的引用"
        )
        
        # 验证带别名的引用是否正确处理
        self.assertIn(
            'with spaces/doc with spaces 2.md',
            stats['doc&with&ampersands.md']['outgoing'],
            "应该正确处理带别名且包含特殊字符的引用"
        )
        
    def test_unicode_characters(self):
        """测试Unicode字符"""
        # 创建包含Unicode字符的文件名
        test_file = os.path.join(self.test_dir, '测试文件.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('# Test\n[[doc with spaces]]')
        
        # 重新扫描文件
        self.checker.scan_files()
        
        # 测试Unicode文件名的处理
        self.assertIn(
            '测试文件.md',
            self.checker.files,
            "应该正确识别包含Unicode字符的文件名"
        )
        
        # 测试对Unicode文件的引用解析
        resolved = self.checker.resolve_link(
            '测试文件',
            'doc with spaces.md',
            is_image=False
        )
        self.assertEqual(
            resolved,
            '测试文件.md',
            "应该正确解析包含Unicode字符��文件引用"
        )
        
        # 清理测试文件
        os.remove(test_file)

if __name__ == '__main__':
    unittest.main() 