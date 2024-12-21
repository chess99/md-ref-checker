import unittest
import os
import shutil
from src.check_references import ReferenceChecker

class TestReferenceChecker(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_1')
        self.checker = ReferenceChecker(self.test_dir)
        # 确保在测试前扫描文件系统
        self.checker.scan_files()
        
    def test_image_reference_resolution(self):
        """测试图片引用解析"""
        # 测试正常的图片引用
        resolved = self.checker.resolve_link(
            "20241025-地址组件长期规划.png",
            "test.md",
            is_image=True
        )
        self.assertEqual(resolved, "assets/20241025-地址组件长期规划.png")
        
        # 测试不存在的图片引用
        resolved = self.checker.resolve_link(
            "image_not_exist.png",
            "test.md",
            is_image=True
        )
        self.assertEqual(resolved, "image_not_exist.png")
        
    def test_markdown_reference_resolution(self):
        """测试Markdown文档引用解析"""
        # 测试正常的文档引用
        resolved = self.checker.resolve_link(
            "existing_doc",
            "test.md",
            is_image=False
        )
        self.assertEqual(resolved, "existing_doc.md")
        
        # 测试不存在的文档引用
        resolved = self.checker.resolve_link(
            "non_existing_doc",
            "test.md",
            is_image=False
        )
        self.assertEqual(resolved, "non_existing_doc")
        
    def test_reference_checking(self):
        """测试引用检查功能"""
        self.checker.check_all_references()
        
        # 验证无效引用
        self.assertTrue(any(
            link == "image_not_exist.png"
            for _, (link, _, _, _) in self.checker.invalid_links
        ))
        
        # 验证图片引用统计
        self.assertIn(
            "assets/20241025-地址组件长期规划.png",
            self.checker.referenced_images
        )
        
    def test_file_mapping(self):
        """测试文件映射功能"""
        # 测试图片文件映射
        self.assertIn(
            "assets/20241025-地址组件长期规划.png",
            self.checker.image_files
        )
        
        # 测试文件名到实际文件的映射
        self.assertIn(
            "20241025-地址组件长期规划.png",
            self.checker.file_map
        )
        self.assertIn(
            "assets/20241025-地址组件长期规划.png",
            self.checker.file_map["20241025-地址组件长期规划.png"]
        )

if __name__ == '__main__':
    unittest.main() 