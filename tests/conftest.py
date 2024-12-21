import os
import pytest
import shutil

@pytest.fixture(scope="session")
def test_files_root():
    """Return the root directory for test files"""
    return os.path.join(os.path.dirname(__file__), 'test_files')

@pytest.fixture(autouse=True)
def clean_test_files(request, test_files_root):
    """Clean up test files before and after each test"""
    # Clean up before test
    if os.path.exists(test_files_root):
        shutil.rmtree(test_files_root)
    os.makedirs(test_files_root)
    
    def cleanup():
        # Clean up after test
        if os.path.exists(test_files_root):
            shutil.rmtree(test_files_root)
    
    request.addfinalizer(cleanup)
    return test_files_root

@pytest.fixture
def temp_dir(test_files_root):
    """Create a temporary directory for tests"""
    temp_path = os.path.join(test_files_root, 'temp')
    os.makedirs(temp_path, exist_ok=True)
    return temp_path 