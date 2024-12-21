import unittest
import os
from check_references import ReferenceChecker

class TestUnidirectionalLinks(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_unidirectional')
        self.checker = ReferenceChecker(self.test_dir)
        self.checker.scan_files()
        
    def test_reference_detection(self):
        """测试引用检测"""
        self.checker.check_all_references()
        
        # 检查引用统计
        stats = self.checker.reference_stats
        
        # 检查 doc_a 的引用情况
        self.assertEqual(
            len(stats['doc_a.md']['outgoing']),
            2,
            "doc_a 应该有2个外部引用"
        )
        self.assertEqual(
            stats['doc_a.md']['incoming'],
            0,
            "doc_a 不应该被其他文档引用"
        )
        
        # 检查 doc_b 和 doc_c 之间的双向引用
        self.assertIn(
            'doc_c.md',
            stats['doc_b.md']['outgoing'],
            "doc_b 应该引用 doc_c"
        )
        self.assertIn(
            'doc_b.md',
            stats['doc_c.md']['outgoing'],
            "doc_c 应该引用 doc_b"
        )
        
        # 检查带别名的引用
        self.assertIn(
            'doc_d.md',
            stats['doc_b.md']['outgoing'],
            "doc_b 应该引用 doc_d（带别名的引用）"
        )
        
    def test_unidirectional_links(self):
        """测试单向链接检测"""
        self.checker.check_all_references()
        
        # 将单向链接转换为集合，便于比较
        unidirectional_set = {
            (source, target) for source, target in self.checker.unidirectional_links
        }
        
        # 预期的单向链接
        expected_unidirectional = {
            ('doc_a.md', 'doc_b.md'),  # A -> B 但 B 没有引用 A
            ('doc_a.md', 'doc_c.md'),  # A -> C 但 C 没有引用 A
            ('doc_b.md', 'doc_d.md'),  # B -> D 但 D 没有引用 B
        }
        
        # 验证单向链接检测结果
        self.assertEqual(
            unidirectional_set,
            expected_unidirectional,
            "单向链接检测结果与预期不符"
        )
        
        # 验证双向链接没有被误报为单向链接
        for source, target in [('doc_b.md', 'doc_c.md'), ('doc_c.md', 'doc_b.md')]:
            self.assertNotIn(
                (source, target),
                unidirectional_set,
                f"双向链接 {source} <-> {target} 不应该出现在单向链接列表中"
            )
            
    def test_alias_references(self):
        """测试带别名的引用"""
        self.checker.check_all_references()
        
        # 检查带别名的引用是否正确解析
        stats = self.checker.reference_stats
        self.assertIn(
            'doc_d.md',
            stats['doc_b.md']['outgoing'],
            "带别名的引用应该正确解析到目标文件"
        )
        
    def test_reference_cycles(self):
        """测试引用循环"""
        self.checker.check_all_references()
        
        # B <-> C 形成一个引用循环，但这是正常的双向引用
        stats = self.checker.reference_stats
        self.assertIn(
            'doc_c.md',
            stats['doc_b.md']['outgoing'],
            "应该检测到 B -> C 的引用"
        )
        self.assertIn(
            'doc_b.md',
            stats['doc_c.md']['outgoing'],
            "应该检测到 C -> B 的引用"
        )

if __name__ == '__main__':
    unittest.main() 