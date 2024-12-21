import unittest
import os
import shutil
from src.check_references import ReferenceChecker

class TestStatistics(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_statistics')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test files
        self.create_test_files()
        
        self.checker = ReferenceChecker(self.test_dir)
        self.checker.scan_files()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files for statistics testing"""
        # Create a central document that references many others
        with open(os.path.join(self.test_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write('''# Index
            
[[doc1]]
[[doc2]]
[[doc3]]
![[image1.png]]
![[image2.png]]''')
        
        # Create documents with varying reference patterns
        with open(os.path.join(self.test_dir, 'doc1.md'), 'w', encoding='utf-8') as f:
            f.write('''# Document 1
            
[[index]]
[[doc2]]
![[image1.png]]''')
        
        with open(os.path.join(self.test_dir, 'doc2.md'), 'w', encoding='utf-8') as f:
            f.write('''# Document 2
            
[[doc1]]
[[doc3]]''')
        
        with open(os.path.join(self.test_dir, 'doc3.md'), 'w', encoding='utf-8') as f:
            f.write('''# Document 3
            
[[index]]
![[image2.png]]''')
        
        # Create assets directory and images
        os.makedirs(os.path.join(self.test_dir, 'assets'), exist_ok=True)
        for img in ['image1.png', 'image2.png', 'unused.png']:
            with open(os.path.join(self.test_dir, 'assets', img), 'w') as f:
                f.write(f'dummy content for {img}')
    
    def test_reference_counts(self):
        """Test reference counting"""
        self.checker.check_all_references()
        
        # Test incoming reference counts
        self.assertEqual(self.checker.reference_stats['index.md']['incoming'], 2)  # from doc1 and doc3
        self.assertEqual(self.checker.reference_stats['doc1.md']['incoming'], 2)   # from index and doc2
        self.assertEqual(self.checker.reference_stats['doc2.md']['incoming'], 2)   # from index and doc1
        self.assertEqual(self.checker.reference_stats['doc3.md']['incoming'], 2)   # from index and doc2
    
    def test_outgoing_references(self):
        """Test outgoing reference tracking"""
        self.checker.check_all_references()
        
        # Test outgoing references
        index_outgoing = self.checker.reference_stats['index.md']['outgoing']
        self.assertEqual(len(index_outgoing), 3)  # doc1, doc2, doc3
        self.assertTrue(all(f in index_outgoing for f in ['doc1.md', 'doc2.md', 'doc3.md']))
        
        doc1_outgoing = self.checker.reference_stats['doc1.md']['outgoing']
        self.assertEqual(len(doc1_outgoing), 2)  # index, doc2
        self.assertTrue(all(f in doc1_outgoing for f in ['index.md', 'doc2.md']))
    
    def test_image_references(self):
        """Test image reference statistics"""
        self.checker.check_all_references()
        
        # Test referenced images
        self.assertEqual(len(self.checker.referenced_images), 2)
        self.assertTrue(all(f'assets/{img}' in self.checker.referenced_images 
                          for img in ['image1.png', 'image2.png']))
        
        # Test unused images
        unused_images = self.checker.image_files - self.checker.referenced_images
        self.assertEqual(len(unused_images), 1)
        self.assertTrue('assets/unused.png' in unused_images)
    
    def test_unidirectional_links(self):
        """Test unidirectional link detection"""
        self.checker.check_all_references()
        
        # Find all unidirectional links
        unidirectional = set((source, target) for source, target in self.checker.unidirectional_links)
        
        # Test specific unidirectional relationships
        expected_unidirectional = {
            ('index.md', 'doc2.md'),  # index -> doc2 but doc2 doesn't reference index
            ('index.md', 'doc3.md'),  # index -> doc3 but doc3 doesn't reference doc1
            ('doc2.md', 'doc3.md'),   # doc2 -> doc3 but doc3 doesn't reference doc2
        }
        
        self.assertEqual(unidirectional, expected_unidirectional)
    
    def test_reference_patterns(self):
        """Test reference pattern analysis"""
        self.checker.check_all_references()
        
        # Test circular reference detection (doc1 <-> doc2)
        doc1_refs = self.checker.reference_stats['doc1.md']['outgoing']
        doc2_refs = self.checker.reference_stats['doc2.md']['outgoing']
        self.assertTrue('doc2.md' in doc1_refs and 'doc1.md' in doc2_refs)
        
        # Test hub document detection (index references many)
        index_refs = self.checker.reference_stats['index.md']['outgoing']
        self.assertTrue(len(index_refs) >= 3)

if __name__ == '__main__':
    unittest.main() 