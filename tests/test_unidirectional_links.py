import os
from src.check_references import ReferenceChecker

def test_unidirectional_links(clean_test_files):
    """Test unidirectional link detection"""
    test_dir = os.path.join(clean_test_files, 'test_case_unidirectional')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files
    with open(os.path.join(test_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write('''# Index
        
[[doc1]]
[[doc2]]
[[doc3]]''')
    
    with open(os.path.join(test_dir, 'doc1.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document 1
        
[[index]]
[[doc2]]''')
    
    with open(os.path.join(test_dir, 'doc2.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document 2
        
[[doc1]]''')
    
    with open(os.path.join(test_dir, 'doc3.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document 3
        
[[index]]''')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test unidirectional links
    unidirectional = set(checker.unidirectional_links)
    
    # Expected unidirectional links:
    # - index -> doc2 (doc2 doesn't link back to index)
    # - index -> doc3 (doc3 links back to index, but it's still unidirectional)
    # - doc1 -> doc2 (doc2 links to doc1, creating a cycle)
    expected = {
        ('index.md', 'doc2.md'),
        ('index.md', 'doc3.md'),
        ('doc1.md', 'doc2.md')
    }
    
    assert unidirectional == expected, \
        f"Expected unidirectional links {expected}, but got {unidirectional}"

def test_bidirectional_links(clean_test_files):
    """Test bidirectional link detection"""
    test_dir = os.path.join(clean_test_files, 'test_case_unidirectional')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files with bidirectional links
    with open(os.path.join(test_dir, 'a.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document A
        
[[b]]
[[c]]''')
    
    with open(os.path.join(test_dir, 'b.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document B
        
[[a]]''')
    
    with open(os.path.join(test_dir, 'c.md'), 'w', encoding='utf-8') as f:
        f.write('''# Document C
        
[[a]]''')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test bidirectional links
    stats = checker.reference_stats
    
    # Test that A and B have bidirectional links
    assert 'b.md' in stats['a.md']['outgoing'], \
        "a.md should link to b.md"
    assert 'a.md' in stats['b.md']['outgoing'], \
        "b.md should link to a.md"
    
    # Test that A and C have bidirectional links
    assert 'c.md' in stats['a.md']['outgoing'], \
        "a.md should link to c.md"
    assert 'a.md' in stats['c.md']['outgoing'], \
        "c.md should link to a.md"

def test_complex_link_patterns(clean_test_files):
    """Test complex linking patterns"""
    test_dir = os.path.join(clean_test_files, 'test_case_unidirectional')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files with complex linking patterns
    with open(os.path.join(test_dir, 'hub.md'), 'w', encoding='utf-8') as f:
        f.write('''# Hub Document
        
[[spoke1]]
[[spoke2]]
[[spoke3]]''')
    
    with open(os.path.join(test_dir, 'spoke1.md'), 'w', encoding='utf-8') as f:
        f.write('''# Spoke 1
        
[[hub]]
[[spoke2]]''')
    
    with open(os.path.join(test_dir, 'spoke2.md'), 'w', encoding='utf-8') as f:
        f.write('''# Spoke 2
        
[[spoke3]]''')
    
    with open(os.path.join(test_dir, 'spoke3.md'), 'w', encoding='utf-8') as f:
        f.write('''# Spoke 3
        
[[hub]]
[[spoke1]]''')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test unidirectional links in complex pattern
    unidirectional = set(checker.unidirectional_links)
    
    expected = {
        ('hub.md', 'spoke2.md'),
        ('spoke1.md', 'spoke2.md'),
        ('spoke2.md', 'spoke3.md')
    }
    
    assert unidirectional == expected, \
        f"Expected unidirectional links {expected}, but got {unidirectional}"
    
    # Test reference statistics
    stats = checker.reference_stats
    
    # Hub should have most outgoing links
    assert len(stats['hub.md']['outgoing']) == 3, \
        "Hub should have 3 outgoing links"
    
    # Spoke2 should have no incoming links from hub
    assert 'hub.md' not in stats['spoke2.md']['incoming'], \
        "Spoke2 should not have incoming link from hub"
    
    # Spoke1 and Spoke3 should have bidirectional relationship with hub
    assert 'hub.md' in stats['spoke1.md']['outgoing'], \
        "Spoke1 should link to hub"
    assert 'spoke1.md' in stats['hub.md']['outgoing'], \
        "Hub should link to spoke1"
    assert 'hub.md' in stats['spoke3.md']['outgoing'], \
        "Spoke3 should link to hub"
    assert 'spoke3.md' in stats['hub.md']['outgoing'], \
        "Hub should link to spoke3" 