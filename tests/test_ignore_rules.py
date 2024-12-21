"""
Tests for ignore rules functionality
"""

import os
from src.checker.ignore_rules import IgnoreRules

def test_default_patterns(clean_test_files):
    """Test default ignore patterns"""
    test_dir = os.path.join(clean_test_files, 'test_case_ignore')
    os.makedirs(test_dir, exist_ok=True)
    
    # Initialize ignore rules
    ignore_rules = IgnoreRules(test_dir)
    
    # Test default ignored patterns
    default_ignored = [
        '.git/file.txt',
        '.obsidian/workspace',
        '.trash/deleted.md',
        'node_modules/package.json',
        '.DS_Store',
        'Thumbs.db',
    ]
    
    for path in default_ignored:
        assert ignore_rules.should_ignore(path), \
            f"Should ignore {path}"

def test_gitignore_patterns(clean_test_files):
    """Test .gitignore patterns"""
    test_dir = os.path.join(clean_test_files, 'test_case_ignore')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create .gitignore
    with open(os.path.join(test_dir, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write('''ignored_dir/*
*.tmp
temp.*
node_modules/''')
    
    # Create test files
    os.makedirs(os.path.join(test_dir, 'ignored_dir'))
    os.makedirs(os.path.join(test_dir, 'normal_dir'))
    
    with open(os.path.join(test_dir, 'ignored_dir/file.txt'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, 'normal_dir/file.txt'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, 'file.tmp'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, 'temp.txt'), 'w') as f:
        f.write('content')
    
    # Initialize ignore rules
    ignore_rules = IgnoreRules(test_dir)
    
    # Test directory patterns
    assert ignore_rules.should_ignore('ignored_dir/file.txt'), \
        "Should ignore files in ignored_dir"
    
    # Test file patterns
    assert ignore_rules.should_ignore('file.tmp'), \
        "Should ignore .tmp files"
    assert ignore_rules.should_ignore('temp.txt'), \
        "Should ignore temp.* files"
    
    # Test non-ignored files
    assert not ignore_rules.should_ignore('normal_dir/file.txt'), \
        "Should not ignore files in normal directories"

def test_mdignore_patterns(clean_test_files):
    """Test .mdignore patterns"""
    test_dir = os.path.join(clean_test_files, 'test_case_ignore')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create .mdignore
    with open(os.path.join(test_dir, '.mdignore'), 'w', encoding='utf-8') as f:
        f.write('''draft_*
_private/*
*.draft.md''')
    
    # Create test files
    os.makedirs(os.path.join(test_dir, '_private'))
    
    with open(os.path.join(test_dir, 'draft_post.md'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, '_private/secret.md'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, 'post.draft.md'), 'w') as f:
        f.write('content')
    with open(os.path.join(test_dir, 'normal_post.md'), 'w') as f:
        f.write('content')
    
    # Initialize ignore rules
    ignore_rules = IgnoreRules(test_dir)
    
    # Test patterns
    assert ignore_rules.should_ignore('draft_post.md'), \
        "Should ignore draft_* files"
    assert ignore_rules.should_ignore('_private/secret.md'), \
        "Should ignore files in _private/"
    assert ignore_rules.should_ignore('post.draft.md'), \
        "Should ignore *.draft.md files"
    
    # Test non-ignored files
    assert not ignore_rules.should_ignore('normal_post.md'), \
        "Should not ignore normal files"

def test_multiple_ignore_files(clean_test_files):
    """Test multiple ignore files"""
    test_dir = os.path.join(clean_test_files, 'test_case_ignore')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create .gitignore and .mdignore
    with open(os.path.join(test_dir, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write('*.tmp\ntemp.*')
    with open(os.path.join(test_dir, '.mdignore'), 'w', encoding='utf-8') as f:
        f.write('draft_*\n*.draft.md')
    
    # Initialize ignore rules
    ignore_rules = IgnoreRules(test_dir)
    
    # Test combined patterns
    assert ignore_rules.should_ignore('file.tmp'), \
        "Should ignore .gitignore patterns"
    assert ignore_rules.should_ignore('temp.txt'), \
        "Should ignore .gitignore patterns"
    assert ignore_rules.should_ignore('draft_post.md'), \
        "Should ignore .mdignore patterns"
    assert ignore_rules.should_ignore('post.draft.md'), \
        "Should ignore .mdignore patterns"
    
    # Test non-ignored files
    assert not ignore_rules.should_ignore('normal.md'), \
        "Should not ignore normal files"

def test_nested_ignore_files(clean_test_files):
    """Test nested ignore files"""
    test_dir = os.path.join(clean_test_files, 'test_case_ignore')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create directory structure with nested ignore files
    os.makedirs(os.path.join(test_dir, 'docs'))
    os.makedirs(os.path.join(test_dir, 'docs/drafts'))
    
    with open(os.path.join(test_dir, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write('*.tmp')
    with open(os.path.join(test_dir, 'docs/.gitignore'), 'w', encoding='utf-8') as f:
        f.write('drafts/*')
    
    # Initialize ignore rules
    ignore_rules = IgnoreRules(test_dir)
    
    # Test root patterns
    assert ignore_rules.should_ignore('file.tmp'), \
        "Should apply root .gitignore"
    assert ignore_rules.should_ignore('docs/file.tmp'), \
        "Should apply root .gitignore in subdirectories"
    
    # Test nested patterns
    assert ignore_rules.should_ignore('docs/drafts/post.md'), \
        "Should apply nested .gitignore"
    
    # Test non-ignored files
    assert not ignore_rules.should_ignore('docs/normal.md'), \
        "Should not ignore normal files" 