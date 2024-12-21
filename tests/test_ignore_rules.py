import unittest
import os
from src.check_references import ReferenceChecker

class TestIgnoreRules(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_ignore')
        self.checker = ReferenceChecker(self.test_dir)
        self.checker.scan_files()
        
    def test_gitignore_patterns(self):
        """测试.gitignore模式"""
        # 测试目录忽略
        self.assertTrue(
            self.checker._should_ignore('ignored_dir/some_file.txt'),
            "应该忽略 ignored_dir 中的文件"
        )
        
        # 测试文件模式忽略
        self.assertTrue(
            self.checker._should_ignore('file.tmp'),
            "应该忽略 .tmp 文件"
        )
        self.assertTrue(
            self.checker._should_ignore('temp.txt'),
            "应该忽略 temp.* 文件"
        )
        
        # 测试正常文件不被忽略
        self.assertFalse(
            self.checker._should_ignore('normal_doc.md'),
            "不应该忽略正常文件"
        )
        
    def test_mdignore_patterns(self):
        """测试.mdignore模式"""
        # 测试文件名前缀忽略
        self.assertTrue(
            self.checker._should_ignore('draft_post.md'),
            "应该忽略 draft_ 开头的文件"
        )
        
        # 测试目录忽略
        self.assertTrue(
            self.checker._should_ignore('_private/secret.md'),
            "应该忽略 _private 目录中的文件"
        )
        
        # 测试文件扩展名模式
        self.assertTrue(
            self.checker._should_ignore('post.draft.md'),
            "应该忽略 .draft.md 文件"
        )
        
    def test_reference_checking_with_ignores(self):
        """测试引用检查时的忽略规则"""
        self.checker.check_all_references()
        
        # 验证对被忽略文件的引用不会被记录为无效引用
        ignored_refs = [
            'ignored_dir/image.png',
            'draft_post',
            '_private/secret',
            'temp.md',
            'post.draft.md'
        ]
        
        for ref in ignored_refs:
            self.assertFalse(
                any(link == ref for _, (link, _, _, _) in self.checker.invalid_links),
                f"对被忽略文件的引用 {ref} 不应该被记录为无效引用"
            )
        
        # 验证正常文件的引用仍然正常工作
        self.assertFalse(
            any(link == "normal_doc" for _, (link, _, _, _) in self.checker.invalid_links),
            "对正常文件的引用应该正常工作"
        )
        
    def test_file_scanning_with_ignores(self):
        """测试文件扫描时的忽略规则"""
        # 验证被忽略的文件不会出现在文件列表中
        ignored_files = [
            'ignored_dir/image.png',
            'draft_post.md',
            '_private/secret.md',
            'temp.md',
            'post.draft.md'
        ]
        
        for file in ignored_files:
            self.assertNotIn(
                file,
                self.checker.files,
                f"被忽略的文件 {file} 不应该出现在文件列表中"
            )
        
        # 验证正常文件仍然在文件列表中
        self.assertIn(
            'normal_doc.md',
            self.checker.files,
            "正常文件应该出现在文件列表中"
        )

if __name__ == '__main__':
    unittest.main() 