"""
Command line interface for Markdown reference checker
"""

import os
import sys
import argparse
from .checker import ReferenceChecker

def main() -> None:
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='Markdown 引用检查工具')
    parser.add_argument('--dir', type=str, default='.',
                      help='要检查的目录路径 (默认为当前目录)')
    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2], default=0,
                      help='输出详细程度 (0: 只显示无效引用, 1: 显示无效引用和单向链接, 2: 显示所有信息)')
    parser.add_argument('--no-color', action='store_true',
                      help='禁用彩色输出')
    parser.add_argument('--ignore', type=str, action='append',
                      help='添加要忽略的文件模式（可多次使用）')
    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.exists(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.dir):
        print(f"Error: '{args.dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    checker = ReferenceChecker(args.dir)
    if args.ignore:
        checker.ignore_rules.add_patterns(args.ignore)
    checker.check_all_references()
    checker.print_report(args.verbosity, args.no_color)

if __name__ == '__main__':
    main() 