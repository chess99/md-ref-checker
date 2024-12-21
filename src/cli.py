"""
Command line interface for Markdown reference checker
"""

import os
import sys
import argparse
from typing import List, Optional

from .checker.ignore_rules import IgnoreRules
from .checker.file_scanner import FileScanner
from .checker.reference_checker import ReferenceChecker

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Markdown 引用检查工具')
    parser.add_argument('--dir', help='要检查的目录路径', default='.')
    parser.add_argument('-v', '--verbose', help='输出详细信息', action='store_true')
    parser.add_argument('--no-color', help='禁用彩色输出', action='store_true')
    parser.add_argument('--ignore', help='忽略模式', action='append')
    return parser.parse_args()

def main() -> None:
    """主函数"""
    args = parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # 初始化检查器
    ignore_rules = IgnoreRules(args.dir)
    if args.ignore:
        ignore_rules.add_patterns(args.ignore)
    
    file_scanner = FileScanner(args.dir, ignore_rules)
    checker = ReferenceChecker(args.dir)
    
    # 扫描并检查引用
    checker.scan_files()
    checker.check_all_references()
    
    # 打印报告
    verbosity = 2 if args.verbose else 1
    checker.print_report(verbosity=verbosity, no_color=args.no_color)
    
    # 如果有错误，返回非零状态码
    if checker.invalid_links or checker.path_resolver.referenced_images:
        sys.exit(1)

if __name__ == '__main__':
    main() 