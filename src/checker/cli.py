import os
import sys
from argparse import ArgumentParser
from .ignore_rules import IgnoreRules
from .file_scanner import FileScanner
from .reference_checker import ReferenceChecker

def parse_args() -> ArgumentParser:
    """解析命令行参数"""
    parser = ArgumentParser(description="检查引用")
    parser.add_argument("dir", help="要检查的目录")
    parser.add_argument("-i", "--ignore", help="忽略的文件或目录模式")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("-n", "--no-color", action="store_true", help="不使用颜色输出")
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
    if checker.invalid_links:
        sys.exit(1) 