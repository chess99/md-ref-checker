#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List

from .checker import ReferenceChecker

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='检查 Markdown 文件中的引用完整性'
    )
    
    parser.add_argument(
        '--dir',
        default='.',
        help='要检查的目录路径，默认为当前目录'
    )
    
    parser.add_argument(
        '-v',
        '--verbose',
        type=int,
        choices=[0, 1, 2],
        default=0,
        help='输出详细程度（0-2）'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用彩色输出'
    )
    
    parser.add_argument(
        '--ignore',
        action='append',
        default=[],
        help='要忽略的文件模式（可多次使用）'
    )
    
    return parser.parse_args()

def main() -> int:
    """主函数"""
    args = parse_args()
    
    # 检查目录是否存在
    if not os.path.isdir(args.dir):
        print(f"错误：目录 '{args.dir}' 不存在", file=sys.stderr)
        return 1
        
    # 创建检查器实例
    checker = ReferenceChecker(args.dir)
    
    try:
        # 执行检查
        checker.check_all_references()
        
        # TODO: 根据详细程度输出结果
        # TODO: 添加彩色输出支持
        # TODO: 处理忽略规则
        
        return 0
        
    except Exception as e:
        print(f"错误：{str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 