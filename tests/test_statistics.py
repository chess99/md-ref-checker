import os
from src.check_references import ReferenceChecker

def test_reference_counting(test_files_root):
    """Test reference counting functionality"""
    test_dir = os.path.join(test_files_root, 'test_case_statistics')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test reference statistics
    stats = checker.reference_stats
    
    # Test outgoing references
    assert len(stats['index.md']['outgoing']) == 5, \
        "Index should have 5 outgoing references"
    assert len(stats['doc1.md']['outgoing']) == 3, \
        "Doc1 should have 3 outgoing references"
    assert len(stats['doc2.md']['outgoing']) == 2, \
        "Doc2 should have 2 outgoing references"
    assert len(stats['doc3.md']['outgoing']) == 2, \
        "Doc3 should have 2 outgoing references"
    
    # Test incoming references
    assert len(stats['index.md']['incoming']) == 2, \
        "Index should have 2 incoming references"
    assert len(stats['doc1.md']['incoming']) == 2, \
        "Doc1 should have 2 incoming references"
    assert len(stats['doc2.md']['incoming']) == 2, \
        "Doc2 should have 2 incoming references"
    assert len(stats['doc3.md']['incoming']) == 2, \
        "Doc3 should have 2 incoming references"

def test_image_references(test_files_root):
    """Test image reference tracking"""
    test_dir = os.path.join(test_files_root, 'test_case_statistics')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test referenced images
    assert 'assets/image1.png' in checker.referenced_images, \
        "image1.png should be referenced"
    assert 'assets/image2.png' in checker.referenced_images, \
        "image2.png should be referenced"
    assert 'assets/unused.png' not in checker.referenced_images, \
        "unused.png should not be referenced"
    
    # Test reference counts
    image_refs = {
        'assets/image1.png': 2,  # Referenced in index.md and doc1.md
        'assets/image2.png': 1,  # Referenced in index.md only
        'assets/unused.png': 0   # Not referenced
    }
    
    for image, count in image_refs.items():
        actual_count = sum(1 for stats in checker.reference_stats.values()
                         if image in stats['outgoing'])
        assert actual_count == count, \
            f"{image} should have {count} references, but found {actual_count}"

def test_circular_references(test_files_root):
    """Test circular reference detection"""
    test_dir = os.path.join(test_files_root, 'test_case_statistics')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # Test circular reference detection
    stats = checker.reference_stats
    
    # Each document should have one incoming and one outgoing reference
    for doc in ['a.md', 'b.md', 'c.md']:
        assert len(stats[doc]['incoming']) == 1, \
            f"{doc} should have 1 incoming reference"
        assert len(stats[doc]['outgoing']) == 1, \
            f"{doc} should have 1 outgoing reference"
    
    # Verify the circular reference chain
    assert 'b.md' in stats['a.md']['outgoing'], \
        "a.md should reference b.md"
    assert 'c.md' in stats['b.md']['outgoing'], \
        "b.md should reference c.md"
    assert 'a.md' in stats['c.md']['outgoing'], \
        "c.md should reference a.md" 