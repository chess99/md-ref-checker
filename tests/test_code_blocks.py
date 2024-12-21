import unittest
import os
from check_references import ReferenceChecker

class TestCodeBlocks(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_code_blocks')
        self.checker = ReferenceChecker(self.test_dir)
        
    def test_valid_references(self):
        """测试有效的引用（非代码块中的引用）"""
        self.checker.check_all_references()
        
        # 检查引用统计
        stats = self.checker.reference_stats
        
        # 验证正常引用被正确统计
        self.assertIn(
            'valid_doc.md',
            stats['main.md']['outgoing'],
            "应该检测到对 valid_doc 的引用"
        )
        self.assertIn(
            'real_doc.md',
            stats['main.md']['outgoing'],
            "应该检测到对 real_doc 的引用"
        )
        
        # 验证图片引用被正确统计
        self.assertIn(
            'assets/real_image.png',
            self.checker.referenced_images,
            "应该检测到对 real_image.png 的引用"
        )
        
    def test_fenced_code_blocks(self):
        """测试围栏式代码块中的引用"""
        self.checker.check_all_references()
        stats = self.checker.reference_stats
        
        # 验证围栏式代码块中的引用被忽略
        ignored_docs = ['ignored_doc1.md', 'ignored_doc4.md', 'ignored_doc5.md']
        for doc in ignored_docs:
            self.assertNotIn(
                doc,
                stats['main.md']['outgoing'],
                f"围栏式代码块中的引用 {doc} 应该被忽略"
            )
            
        # 验证围栏式代码块中的图片引用被忽略
        ignored_images = [
            'assets/ignored_image1.png',
            'assets/ignored_image4.png',
            'assets/ignored_image5.png'
        ]
        for image in ignored_images:
            self.assertNotIn(
                image,
                self.checker.referenced_images,
                f"围栏式代码块中的图片引用 {image} 应该被忽略"
            )
            
    def test_inline_code(self):
        """测试行内代码中的引用"""
        self.checker.check_all_references()
        stats = self.checker.reference_stats
        
        # 验证行内代码中的引用被忽略
        self.assertNotIn(
            'ignored_doc2.md',
            stats['main.md']['outgoing'],
            "行内代码中的引用应该被忽略"
        )
        
        # 验证行内代码中的图片引用被忽略
        self.assertNotIn(
            'assets/ignored_image2.png',
            self.checker.referenced_images,
            "行内代码中的图片引用应该被忽略"
        )
        
    def test_indented_code_blocks(self):
        """测试缩进式代码块中的引用"""
        self.checker.check_all_references()
        stats = self.checker.reference_stats
        
        # 验证缩进式代码块中的引用被忽略
        self.assertNotIn(
            'ignored_doc3.md',
            stats['main.md']['outgoing'],
            "缩进式代码块中的引用应该被忽略"
        )
        
        # 验证缩进式代码块中的图片引用被忽略
        self.assertNotIn(
            'assets/ignored_image3.png',
            self.checker.referenced_images,
            "缩进式代码块中的图片引用应该被忽略"
        )
        
    def test_nested_code_blocks(self):
        """测试嵌套代码块中的引用"""
        self.checker.check_all_references()
        stats = self.checker.reference_stats
        
        # 验证嵌套代码块中的引用被忽略
        ignored_docs = ['ignored_doc5.md']
        for doc in ignored_docs:
            self.assertNotIn(
                doc,
                stats['main.md']['outgoing'],
                f"嵌套代码块中的引用 {doc} 应该被忽略"
            )
            
        # 验证嵌套代码块中的图片引用被忽略
        self.assertNotIn(
            'assets/ignored_image5.png',
            self.checker.referenced_images,
            "嵌套代码块中的图片引用应该被忽略"
        )
        
    def test_mixed_content(self):
        """测试混合内容中的引用"""
        self.checker.check_all_references()
        stats = self.checker.reference_stats
        
        # 验证正常引用被正确检测（包括带别名的引用）
        self.assertIn(
            'real_doc.md',
            stats['main.md']['outgoing'],
            "正常引用应该被检测到"
        )
        self.assertIn(
            'valid_doc.md',
            stats['main.md']['outgoing'],
            "带别名的正常引用应该被检测到"
        )
        
        # 验证代码块中的引用被忽略
        ignored_docs = ['ignored_doc6.md', 'ignored_doc7.md', 'ignored_doc8.md', 'ignored_doc9.md']
        for doc in ignored_docs:
            self.assertNotIn(
                doc,
                stats['main.md']['outgoing'],
                f"代码块中的引用 {doc} 应该被忽略"
            )
            
        # 验证代码块中的图片引用被忽略
        ignored_images = ['assets/ignored_image6.png', 'assets/ignored_image7.png']
        for image in ignored_images:
            self.assertNotIn(
                image,
                self.checker.referenced_images,
                f"代码块中的图片引用 {image} 应该被忽略"
            )

if __name__ == '__main__':
    unittest.main() 