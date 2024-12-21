import os
from src.check_references import ReferenceChecker

def test_unidirectional_links(test_files_root):
    """Test unidirectional link detection"""
    test_dir = os.path.join(test_files_root, 'test_case_unidirectional')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test unidirectional links
    unidirectional = set(checker.unidirectional_links)
    
    # Expected unidirectional links:
    # - doc_a -> doc_b (doc_b doesn't link back to doc_a)
    # - doc_a -> doc_c (doc_c doesn't link back to doc_a)
    # - doc_b -> doc_d (doc_d doesn't link back to doc_b)
    expected = {
        ('doc_a.md', 'doc_b.md'),
        ('doc_a.md', 'doc_c.md'),
        ('doc_b.md', 'doc_d.md')
    }
    
    assert unidirectional == expected, \
        f"Expected unidirectional links {expected}, but got {unidirectional}"

def test_bidirectional_links(test_files_root):
    """Test bidirectional link detection"""
    test_dir = os.path.join(test_files_root, 'test_case_unidirectional')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test bidirectional links
    stats = checker.reference_stats
    
    # Test that B and C have bidirectional links
    assert 'doc_c.md' in stats['doc_b.md']['outgoing'], \
        "doc_b.md should link to doc_c.md"
    assert 'doc_b.md' in stats['doc_c.md']['outgoing'], \
        "doc_c.md should link to doc_b.md"

def test_complex_link_patterns(test_files_root):
    """Test complex linking patterns"""
    test_dir = os.path.join(test_files_root, 'test_case_unidirectional')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test reference statistics
    stats = checker.reference_stats
    
    # Test that A has outgoing links but no incoming links
    assert len(stats['doc_a.md']['outgoing']) == 2, \
        "doc_a.md should have 2 outgoing links"
    assert len(stats['doc_a.md']['incoming']) == 0, \
        "doc_a.md should have no incoming links"
    
    # Test that D has incoming links but no outgoing links
    assert len(stats['doc_d.md']['incoming']) == 1, \
        "doc_d.md should have 1 incoming link"
    assert len(stats['doc_d.md']['outgoing']) == 0, \
        "doc_d.md should have no outgoing links"
    
    # Test that B and C have bidirectional relationship
    assert 'doc_c.md' in stats['doc_b.md']['outgoing'], \
        "doc_b.md should link to doc_c.md"
    assert 'doc_b.md' in stats['doc_c.md']['outgoing'], \
        "doc_c.md should link to doc_b.md" 