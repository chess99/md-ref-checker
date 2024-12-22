"""Command line interface for the Markdown reference checker."""

import os
import sys
from importlib.metadata import version
from typing import List

import click

from .checker import ReferenceChecker

__version__ = version("md-ref-checker")


def print_error(msg: str, no_color: bool = False) -> None:
    """Print an error message."""
    if no_color:
        click.echo(msg, err=True)
    else:
        click.secho(msg, fg="red", err=True)


def print_warning(msg: str, no_color: bool = False) -> None:
    """Print a warning message."""
    if no_color:
        click.echo(msg, err=True)
    else:
        click.secho(msg, fg="yellow", err=True)


def print_success(msg: str, no_color: bool = False) -> None:
    """Print a success message."""
    if no_color:
        click.echo(msg)
    else:
        click.secho(msg, fg="green")


def print_debug(msg: str) -> None:
    """Print a debug message."""
    click.secho(f"[DEBUG] {msg}", fg="blue")


@click.command()
@click.version_option(__version__, prog_name="md-ref-checker")
@click.option(
    "-d",
    "--dir",
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    help="要检查的目录路径 (默认为当前目录)",
)
@click.option(
    "-v", "--verbosity", type=click.IntRange(0, 2), default=0, help="输出详细程度 (0-2)"
)
@click.option("-n", "--no-color", is_flag=True, help="禁用彩色输出")
@click.option(
    "-i", "--ignore", multiple=True, help="添加要忽略的文件模式（可多次使用）"
)
@click.option(
    "-r", "--delete-unused-images", is_flag=True, help="删除未被引用的图片文件"
)
@click.option("-D", "--debug", is_flag=True, help="显示调试信息")
def main(
    directory: str,
    verbosity: int,
    no_color: bool,
    ignore: List[str],
    delete_unused_images: bool,
    debug: bool,
) -> None:
    """Markdown 引用检查工具。

    检查 Markdown 文件中的引用完整性和文档组织规范，包括：

    \b
    1. 引用检查：
       - 文档引用 [[文件名]] 或 [[文件名|显示文本]]
       - 标题引用 [[文件名#标题]] 或 [[文件名#标题1#标题2|显示文本]]
       - 图片引用 ![[图片文件名]]
       - 网络图片引用 ![图片说明](https://图片地址)
       - 检查单向引用：A引用了B，但B没有引用A
       - 生成引用统计信息

    \b
    2. 文件组织检查：
       - 根目录使用拼音首字母+中文名称（如 wl物理/）
       - 子目录和文件直接使用中文名称，不需要拼音索引
       - 图片文件统一存放在根目录的 assets/ 文件夹下
    """
    try:
        if debug:
            print_debug("开始检查...")

        # 创建检查器
        checker = ReferenceChecker(directory, debug=debug)

        # 添加额外的忽略模式
        if ignore:
            if debug:
                print_debug(f"添加忽略模式: {ignore}")
            checker.fs.ignore_patterns.extend(ignore)

        # 执行检查
        if debug:
            print_debug("执行目录检查...")
        result = checker.check_directory()

        # 显示无效引用
        if result.invalid_refs:
            error_count = len(result.invalid_refs)
            for ref in result.invalid_refs:
                if debug:
                    print_debug(f"发现无效引用: {ref.target} in {ref.source_file}")
                print_error(
                    f"{ref.source_file}:{ref.line_number}:{ref.column}  error  无效引用 '{ref.target}'",
                    no_color,
                )
                print(f"  {ref.line_content}")
                print_error(f"  {' ' * (ref.column-1)}^", no_color)
            print_error(f"\n✖ 发现 {error_count} 个无效引用", no_color)

        # 显示未被引用的图片
        if result.unused_images:
            if result.invalid_refs:
                print()  # 添加空行分隔
            if debug:
                print_debug(f"发现 {len(result.unused_images)} 个未使用的图片")
            print_warning("未被引用的图片文件:", no_color)
            for image in sorted(result.unused_images):
                print(f"  {image}")
            print_warning(
                f"\n⚠ 发现 {len(result.unused_images)} 个未被引用的图片文件", no_color
            )

        # 显示单向链接（如果verbosity >= 1）
        if verbosity >= 1 and result.unidirectional_links:
            if debug:
                print_debug(f"发现 {len(result.unidirectional_links)} 个单向链接")
            print("\n单向链接:")
            for source, target in result.unidirectional_links:
                print(f"  {source} -> {target}")

        # 显示引用统计（如果verbosity >= 2）
        if verbosity >= 2:
            if debug:
                print_debug("生成引用统计...")
            print("\n引用统计:")
            for file, stats in sorted(checker.file_refs.items()):
                outgoing_count = len(stats)
                incoming_count = sum(
                    1
                    for refs in checker.file_refs.values()
                    for ref in refs
                    if not ref.is_image and ref.target == file
                )
                if incoming_count > 0 or outgoing_count > 0:
                    print(f"\n  {file}:")
                    print(f"  - 被引用次数: {incoming_count}")
                    print(f"  - 引用其他文件数: {outgoing_count}")
                    if outgoing_count > 0:
                        print("  - 引用其他文件:")
                        for ref in sorted(stats, key=lambda r: r.target):
                            if not ref.is_image:
                                print(f"    * {ref.target}")

        # 删除未使用的图片（如果指定了-r选项）
        if delete_unused_images and result.unused_images:
            if debug:
                print_debug("开始删除未使用的图片...")
            print_success("\n删除未使用的图片文件:", no_color)
            for image in sorted(result.unused_images):
                try:
                    os.remove(os.path.join(directory, image))
                    print(f"  {image}")
                except Exception as e:
                    print_error(f"Error deleting {image}: {e}", no_color)
            print_success(
                f"\n✓ 已删除 {len(result.unused_images)} 个未引用的图片文件", no_color
            )

        # 如果有错误，返回非零状态码
        if result.invalid_refs:
            if debug:
                print_debug("检查完成，发现错误")
            sys.exit(1)
        elif not result.unused_images and not result.unidirectional_links:
            if debug:
                print_debug("检查完成，未发现问题")
            print_success("\n✓ 所有引用都是有效的", no_color)

    except Exception as e:
        print_error(f"Error: {e}", no_color)
        if debug:
            import traceback

            print_debug("错误详情:")
            print_debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
