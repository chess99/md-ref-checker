"""Test reference checker"""

import os
from typing import TYPE_CHECKING
import pytest
from src.checker.models import Config
from src.checker.reference_checker import ReferenceChecker

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def test_dir(request: "FixtureRequest") -> str:
    """测试目录路径"""
    return os.path.join(request.config.rootdir, "tests", "test_files")

@pytest.fixture
def checker(test_dir: str) -> ReferenceChecker:
    """引用检查器实例"""
    config = Config(root_dir=test_dir)
    return ReferenceChecker(config)

def test_check_references_basic(checker: ReferenceChecker) -> None:
    """测试基本引用检查"""
    stats = checker.check_references()
    
    # 验证引用统计
    assert len(stats.invalid_references) == 0
    assert len(stats.outgoing["case1/doc1.md"]) == 1
    assert len(stats.incoming["case1/doc2.md"]) == 1

def test_check_references_with_invalid_links(checker: ReferenceChecker) -> None:
    """测试包含无效引用的情况"""
    stats = checker.check_references()
    
    # 验证无效引用
    invalid_refs = [ref for ref in stats.invalid_references if ref.source == "case2/invalid.md"]
    assert len(invalid_refs) > 0
    assert any(ref.target == "non-existent.md" for ref in invalid_refs)

def test_check_references_with_images(checker: ReferenceChecker) -> None:
    """测试图片引用检查"""
    stats = checker.check_references()
    
    # 验证图片引用
    assert "case3/image.png" in stats.referenced_images
    assert len(stats.referenced_images) > 0

def test_check_references_with_assets(checker: ReferenceChecker) -> None:
    """测试 assets 目录中的图片引用"""
    stats = checker.check_references()
    
    # 验证 assets 目录中的图片引用
    assert "assets/test.png" in stats.referenced_images

def test_print_report(checker: ReferenceChecker, capsys: "CaptureFixture[str]") -> None:
    """测试报告打印"""
    stats = checker.check_references()
    checker.print_report()
    
    captured = capsys.readouterr()
    assert "Summary:" in captured.out
    assert "Total files:" in captured.out
    assert "Invalid references:" in captured.out