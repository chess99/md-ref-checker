import os
import pytest
import shutil

@pytest.fixture(scope="session")
def test_files_root():
    """Return the root directory for test files"""
    return os.path.join(os.path.dirname(__file__), 'test_files')

@pytest.fixture(autouse=True)
def clean_test_files(request, test_files_root):
    """Clean up temporary test files before and after each test"""
    # Get the test function name
    test_name = request.node.name
    # Create a temporary directory specific to this test
    temp_test_dir = os.path.join(test_files_root, f'temp_{test_name}')
    
    # Clean up before test
    if os.path.exists(temp_test_dir):
        shutil.rmtree(temp_test_dir)
    os.makedirs(temp_test_dir)
    
    def cleanup():
        # Clean up after test
        if os.path.exists(temp_test_dir):
            shutil.rmtree(temp_test_dir)
    
    request.addfinalizer(cleanup)
    return temp_test_dir

@pytest.fixture
def temp_dir(test_files_root):
    """Create a temporary directory for tests that need it"""
    temp_path = os.path.join(test_files_root, 'temp')
    os.makedirs(temp_path, exist_ok=True)
    return temp_path 