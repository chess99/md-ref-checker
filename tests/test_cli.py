"""Test cases for the CLI module."""
from typing import TYPE_CHECKING
import pytest
from click.testing import CliRunner
from md_ref_checker.cli import cli

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


def test_help_option(runner):
    """Test the --help option."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Options:" in result.output


def test_check_directory(runner, tmp_path):
    """Test checking a directory."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("""
Here's a valid reference [[doc2]]
And an invalid one [[nonexistent]]
""")
    (tmp_path / "doc2.md").write_text("Some content")
    
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert result.exit_code == 1  # 有错误时返回1
    assert "无效引用" in result.output
    assert "nonexistent" in result.output


def test_check_directory_no_errors(runner, tmp_path):
    """Test checking a directory with no errors."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("[[doc2]]")
    (tmp_path / "doc2.md").write_text("[[doc1]]")
    
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert result.exit_code == 0  # 没有错误时返回0
    assert "✓" in result.output  # 显示成功标记


def test_verbosity_levels(runner, tmp_path):
    """Test different verbosity levels."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("[[doc2]]")
    (tmp_path / "doc2.md").write_text("Some content")
    
    # 测试默认输出
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert "单向链接" not in result.output
    
    # 测试详细输出
    result = runner.invoke(cli, ["-d", str(tmp_path), "-v", "1"])
    assert "单向链接" in result.output
    
    # 测试更详细的输出
    result = runner.invoke(cli, ["-d", str(tmp_path), "-v", "2"])
    assert "引用统计" in result.output


def test_no_color_option(runner, tmp_path):
    """Test the --no-color option."""
    # 创建测试文件
    (tmp_path / "doc1.md").write_text("[[nonexistent]]")
    
    # 默认输出（有颜色）
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert "error" in result.output
    
    # 无颜色输出
    result = runner.invoke(cli, ["-d", str(tmp_path), "--no-color"])
    assert "error" in result.output


def test_ignore_option(runner, tmp_path):
    """Test the --ignore option."""
    # 创建测试文件
    (tmp_path / "doc.md").write_text("[[ignored.md]]")
    (tmp_path / "ignored.md").write_text("Should be ignored")
    
    # 使用--ignore选项
    result = runner.invoke(cli, [
        "-d", str(tmp_path),
        "-i", "ignored.md"
    ])
    assert result.exit_code == 1
    assert "无效引用" in result.output


def test_delete_unused_images(runner, tmp_path):
    """Test the --delete-unused-images option."""
    # 创建测试文件
    (tmp_path / "doc.md").write_text("![[used.png]]")
    (tmp_path / "used.png").touch()
    (tmp_path / "unused.png").touch()
    
    # 检查但不删除
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert "未被引用的图片" in result.output
    assert (tmp_path / "unused.png").exists()
    
    # 检查并删除
    result = runner.invoke(cli, ["-d", str(tmp_path), "-r"])
    assert "已删除" in result.output
    assert not (tmp_path / "unused.png").exists()
    assert (tmp_path / "used.png").exists()


def test_debug_option(runner, tmp_path):
    """Test the --debug option."""
    # 创建测试文件
    (tmp_path / "doc.md").write_text("[[test]]")
    
    # 不带调试信息
    result = runner.invoke(cli, ["-d", str(tmp_path)])
    assert "[DEBUG]" not in result.output
    
    # 带调试信息
    result = runner.invoke(cli, ["-d", str(tmp_path), "-D"])
    assert "[DEBUG]" in result.output
