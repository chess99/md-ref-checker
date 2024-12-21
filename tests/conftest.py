"""Test configuration and fixtures"""

import os
import shutil
import pytest
from typing import Generator, Dict, Any
from src.checker.models import Config

@pytest.fixture
def test_files_dir(request: Any) -> str:
    """测试文件目录路径"""
    return os.path.join(request.config.rootdir, "tests", "test_files")

@pytest.fixture
def temp_dir(tmp_path: Any) -> Generator[str, None, None]:
    """临时目录，每个测试后自动清理"""
    temp_path = str(tmp_path)
    yield temp_path
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

@pytest.fixture
def test_config(test_files_dir: str) -> Config:
    """测试配置"""
    return Config(
        root_dir=test_files_dir,
        search_paths=['.', 'assets', 'images'],
        verbosity=2
    )

def create_test_file(path: str, content: str) -> None:
    """创建测试文件

    Args:
        path: 文件路径
        content: 文件内容
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_test_files(root_dir: str, files: Dict[str, str]) -> None:
    """批量创建测试文件

    Args:
        root_dir: 根目录
        files: 文件路径和内容的映射
    """
    for path, content in files.items():
        full_path = os.path.join(root_dir, path)
        create_test_file(full_path, content)