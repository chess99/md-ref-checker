import unittest
import os
import sys
from io import StringIO
from unittest.mock import patch
from src.check_references import main

class TestCommandLine(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files/test_case_cli')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test files
        self.create_test_files()
        
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files for CLI testing"""
        # Create a valid markdown file
        with open(os.path.join(self.test_dir, 'test1.md'), 'w', encoding='utf-8') as f:
            f.write('# Test Document\n\n[[test2]]\n![[image1.png]]')
        
        # Create referenced markdown file
        with open(os.path.join(self.test_dir, 'test2.md'), 'w', encoding='utf-8') as f:
            f.write('# Test Document 2\n\n[[test1]]')
        
        # Create assets directory and add an image
        os.makedirs(os.path.join(self.test_dir, 'assets'), exist_ok=True)
        with open(os.path.join(self.test_dir, 'assets/image1.png'), 'w') as f:
            f.write('dummy image content')
    
    def test_basic_command(self):
        """Test basic command execution"""
        with patch('sys.argv', ['md-ref-checker', '--dir', self.test_dir]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertNotIn('error', output.lower())
    
    def test_verbosity_levels(self):
        """Test different verbosity levels"""
        for level in range(3):
            with patch('sys.argv', ['md-ref-checker', '--dir', self.test_dir, '-v', str(level)]):
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()
                    if level >= 1:
                        self.assertIn('单向链接', output)
                    if level >= 2:
                        self.assertIn('引用统计', output)
    
    def test_no_color_option(self):
        """Test --no-color option"""
        with patch('sys.argv', ['md-ref-checker', '--dir', self.test_dir, '--no-color']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertNotIn('\x1b[', output)  # ANSI color codes
    
    def test_ignore_pattern(self):
        """Test ignore patterns"""
        # Create a file that should be ignored
        with open(os.path.join(self.test_dir, 'ignore_me.md'), 'w', encoding='utf-8') as f:
            f.write('[[non_existent]]')
        
        with patch('sys.argv', ['md-ref-checker', '--dir', self.test_dir, '--ignore', '*.md']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertNotIn('non_existent', output)
    
    def test_invalid_directory(self):
        """Test behavior with invalid directory"""
        with patch('sys.argv', ['md-ref-checker', '--dir', 'non_existent_dir']):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with self.assertRaises(SystemExit):
                    main()
                self.assertIn('error', fake_err.getvalue().lower())

if __name__ == '__main__':
    unittest.main() 