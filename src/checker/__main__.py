"""
Command line interface for Markdown reference checker
"""

import os
import sys
import argparse
from typing import List, Optional
from .checker import ReferenceChecker
from .file_scanner import FileScanner
from .ignore_rules import IgnoreRules

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='检查 Markdown 文件中的引用完整性',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='要检查的目录路径（默认为当前目录）'
    )
    
    parser.add_argument(
        '--ignore',
        '-i',
        action='append',
        default=[],
        help='要忽略的文件或目录的 glob 模式（可多次指定）'
    )
    
    parser.add_argument(
        '--no-unused',
        action='store_true',
        help='不检查未使用的图片文件'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='以 JSON 格式输出结果'
    )
    
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """主函数
    
    Args:
        args: 命令行参数列表
        
    Returns:
        int: 退出码（0 表示成功，非 0 表示失败）
    """
    parser = create_parser()
    options = parser.parse_args(args)
    
    # 规范化路径
    root_dir = os.path.abspath(options.path)
    if not os.path.exists(root_dir):
        print(f'错误：路径不存在：{root_dir}', file=sys.stderr)
        return 1
    
    # 创建忽略规则
    ignore_rules = IgnoreRules(options.ignore)
    
    # 创建文件扫描器和检查器
    file_scanner = FileScanner(root_dir, ignore_rules)
    checker = ReferenceChecker(file_scanner)
    
    # 执行检查
    checker.scan()
    
    # 获取结果
    broken_refs = checker.get_broken_references()
    unused_images = checker.get_unused_images() if not options.no_unused else set()
    stats = checker.get_statistics()
    
    # 输出结果
    if options.json:
        import json
        result = {
            'broken_references': broken_refs,
            'unused_images': list(unused_images),
            'statistics': stats
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 输出损坏的引用
        if broken_refs:
            print('\n损坏的引用：')
            for file, refs in broken_refs.items():
                print(f'\n{file}:')
                for ref in refs:
                    print(f'  - {ref}')
        
        # 输出未使用的图片
        if unused_images:
            print('\n未使用的图片：')
            for image in sorted(unused_images):
                print(f'  - {image}')
        
        # 输出统计信息
        print('\n统计信息：')
        print(f'  Markdown 文件总数：{stats["total_markdown_files"]}')
        print(f'  图片文件总数：{stats["total_image_files"]}')
        print(f'  损坏的引用总数：{stats["broken_references"]}')
        print(f'  包含损坏引用的文件数：{stats["files_with_broken_refs"]}')
        if not options.no_unused:
            print(f'  未使用的图片数：{stats["unused_images"]}')
    
    # 如果有任何问题，返回非零退出码
    return 1 if broken_refs or unused_images else 0

if __name__ == '__main__':
    sys.exit(main()) 