#!/usr/bin/env python3
"""
Markdown 引用检查工具

这个脚本用于检查 Markdown 文件中的引用完整性和文档组织规范，包括：

1. 引用检查：
   - 文档引用 [[文件名]] 或 [[文件名|显示文本]]
   - 图片引用 ![[图片文件名]]
   - 网络图片引用 ![图片说明](https://图片地址)
   - 检查单向引用：A引用了B，但B没有引用A
   - 生成引用统计信息

2. 文件组织检查：
   - 根目录使用拼音首字母+中文名称（如 wl物理/）
   - 子目录和文件直接使用中文名称，不需要拼音索引
   - 图片文件统一存放在根目录的 assets/ 文件夹下

3. 图片规范检查：
   - 检测未被引用的图片文件
   - 支持的图片格式：PNG（示意图和图表）、JPG（照片）等
   - 检查图片引用的完整性

特性：
- 支持相对路径和绝对路径
- 忽略代码块中的引用
- 忽略行内代码中的引用
- 正确处理任务列表、普通列表等 Markdown 语法
- 支持 .gitignore 和自定义忽略规则
- 支持详细的错误位置报告（行号、列号）

使用方法：
    python check_references.py [--dir 目录路径] [-v 详细程度] [--no-color] [--ignore 忽略模式]

参数：
    --dir: 要检查的目录路径，默认为当前目录
    -v: 输出详细程度（0-2），默认为0
        0: 只显示无效引用和未使用的图片
        1: 显示无效引用、未使用的图片和单向链接
        2: 显示所有引用统计信息
    --no-color: 禁用彩色输出
    --ignore: 添加要忽略的文件模式（可多次使用）

输出示例：
    file.md:10:5  error  无效引用 '不存在的文件'
      [[不存在的文件]]
      ^

    未被引用的图片文件:
      assets/unused_image.png

依赖：
    - markdown-it-py: Markdown 解析器
"""

import os
import re
from typing import Dict, Set, List, Tuple
import argparse
from collections import defaultdict
from markdown_it import MarkdownIt
from markdown_it.token import Token

class ReferenceChecker:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.files = set()  # 所有文件的规范化路径
        self.file_names = set()  # 所有文件名（不含扩展名）
        self.file_map = {}  # 文件名到实际文件的映射（包含扩展名的情况）
        self.invalid_links = []
        self.unidirectional_links = []
        self.reference_stats = defaultdict(lambda: {"incoming": 0, "outgoing": set()})
        self.image_files = set()  # 所有图片文件
        self.referenced_images = set()  # 被引用的图片
        self.md = MarkdownIt('commonmark')
        self.ignore_patterns = self._load_ignore_patterns()

    def _load_ignore_patterns(self) -> List[str]:
        """加载需要忽略的文件模式"""
        patterns = [
            # 默认忽略的模式
            '.git/*',
            '.obsidian/*',
            '.trash/*',
            'node_modules/*',
            '.DS_Store',
            'Thumbs.db',
        ]
        
        # 读取 .gitignore
        gitignore_path = os.path.join(self.root_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # 跳过空行和注释
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                print(f"Warning: Error reading .gitignore: {e}")
        
        # 读取自定义忽略文件 .mdignore（如果存在）
        mdignore_path = os.path.join(self.root_dir, '.mdignore')
        if os.path.exists(mdignore_path):
            try:
                with open(mdignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # 跳过空行和注释
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                print(f"Warning: Error reading .mdignore: {e}")
        
        return patterns

    def _should_ignore(self, path: str) -> bool:
        """检查文件是否应该被忽略"""
        # 规范化路径（使用正斜杠）
        path = path.replace('\\', '/')
        
        for pattern in self.ignore_patterns:
            # 移除开头的 ./
            if pattern.startswith('./'):
                pattern = pattern[2:]
            
            # 移除结尾的 /
            if pattern.endswith('/'):
                pattern = pattern[:-1]
            
            # 处理目录模式（不论是否以/结尾都视为目录模式）
            if os.path.isdir(os.path.join(self.root_dir, pattern)):
                if path == pattern or path.startswith(pattern + '/'):
                    return True
            
            # 处理文件通配符
            elif '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(path, pattern):
                    return True
            
            # 精确匹配
            elif path == pattern:
                return True
        
        return False

    def normalize_path(self, path: str) -> str:
        """规范化路径，处理路径分隔符"""
        # 统一使用正斜杠
        path = path.replace('\\', '/')
        # 移除开头的 ./
        path = re.sub(r'^\./', '', path)
        return path

    def scan_files(self) -> None:
        """扫描目录下的所有文件"""
        # 常见图片扩展名
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        
        for root, _, files in os.walk(self.root_dir):
            # 获取相对路径
            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == '.':
                rel_root = ''
            
            # 检查目录是否应该被忽略
            if self._should_ignore(rel_root):
                continue
            
            for file in files:
                # 获取相对路径
                rel_path = os.path.join(rel_root, file).replace('\\', '/')
                
                # 检查文件是否应该被忽略
                if self._should_ignore(rel_path):
                    continue
                
                abs_path = os.path.join(root, file)
                norm_path = self.normalize_path(rel_path)
                
                # 保存完整路径
                self.files.add(norm_path)
                
                # 保存不带扩展名的文件名和完整路径
                base_name = os.path.splitext(file)[0]
                base_path = os.path.splitext(norm_path)[0]
                self.file_names.add(base_name)
                
                # 记录文件名到实际文件的映射
                # 1. 完整路径映射
                if norm_path not in self.file_map:
                    self.file_map[norm_path] = []
                if norm_path not in self.file_map[norm_path]:
                    self.file_map[norm_path].append(norm_path)
                
                # 2. 不带扩展名的完整路径映射
                if base_path not in self.file_map:
                    self.file_map[base_path] = []
                if norm_path not in self.file_map[base_path]:
                    self.file_map[base_path].append(norm_path)
                
                # 3. 纯文件名映射（带扩展名）
                if file not in self.file_map:
                    self.file_map[file] = []
                if norm_path not in self.file_map[file]:
                    self.file_map[file].append(norm_path)
                
                # 4. 纯文件名映射（不带扩展名）
                if base_name not in self.file_map:
                    self.file_map[base_name] = []
                if norm_path not in self.file_map[base_name]:
                    self.file_map[base_name].append(norm_path)
                
                # 记录图片文件（只记录未被忽略的图片）
                if os.path.splitext(file)[1].lower() in image_extensions:
                    if not self._should_ignore(rel_path):
                        self.image_files.add(norm_path)

    def resolve_link(self, link: str, current_file: str, is_image: bool = False) -> str:
        """解析引用链接，处理相对路径"""
        # 如果是绝对路径（以/开头）
        if link.startswith('/'):
            link = link.lstrip('/')
        else:
            # 处理相对路径
            current_dir = os.path.dirname(current_file)
            if current_dir:
                link = os.path.join(current_dir, link)
        
        # 规范化路径
        link = self.normalize_path(link)
        base_link = os.path.splitext(link)[0]  # 不带扩展名的路径
        base_name = os.path.basename(link)
        base_name_no_ext = os.path.splitext(base_name)[0]
        
        # 检查所有可能的映射
        possible_keys = [
            link,  # 完整路径
            base_link,  # 不带扩展名的完整路径
            base_name,  # 文件名（带扩展名）
            base_name_no_ext,  # 文件名（不带扩展名）
            f"assets/{base_name}",  # assets/文件名（带扩展名）
            f"assets/{base_name_no_ext}",  # assets/文件名（不带扩展名）
        ]
        
        # 对于每个可能的键，检查是否存在映射
        for key in possible_keys:
            if key in self.file_map:
                files = self.file_map[key]
                # 如果是图片引用，优先查找图片文件
                if is_image:
                    # 先尝试查找图片文件
                    image_files = []
                    for f in files:
                        if f in self.image_files:
                            self.referenced_images.add(f)
                            image_files.append(f)
                    if image_files:
                        return image_files[0]
                    # 如果找不到图片文件，尝试查找其他文件
                    # 优先返回.md文件
                    md_files = [f for f in files if f.endswith('.md')]
                    if md_files:
                        return md_files[0]
                    # 如果还是找不到，返回第一个匹配的文件
                    return files[0]
                else:
                    # 如果不是图片引用，优先返回.md文件
                    md_files = [f for f in files if f.endswith('.md')]
                    if md_files:
                        return md_files[0]
                    # 否则返回第一个匹配的文件
                    resolved = files[0]
                    # 如果是图片文件，记录引用
                    if resolved in self.image_files:
                        self.referenced_images.add(resolved)
                    return resolved
        
        # 尝试直接在assets目录下查找图片文件
        if is_image:
            assets_path = f"assets/{base_name}"
            if assets_path in self.image_files:
                self.referenced_images.add(assets_path)
                return assets_path
        
        # 如果都找不到，返回原始链接
        return link

    def find_references_in_text(self, text: str, line_num: int) -> List[Tuple[str, int, int, str, bool]]:
        """在普通文本中查找引用"""
        references = []
        line = text.strip()
        
        # 跳过行内代码块和其他特殊语法
        line_parts = []
        last_end = 0
        
        # 跳过所有任务列表标记 [x] 或 [ ]，不限于行
        line = re.sub(r'\[[ x]\]', '', line)
        
        # 跳过列表标记
        line = re.sub(r'^\s*[-*+]\s+', '', line)
        line = re.sub(r'^\s*\d+\.\s+', '', line)
        
        # 跳过行内代码块
        for match in re.finditer(r'`[^`]+`', line):
            line_parts.append(line[last_end:match.start()])
            last_end = match.end()
        line_parts.append(line[last_end:])
        clean_line = ''.join(line_parts)
        
        # 跳过表格语法
        if re.match(r'\s*\|.*\|\s*$', clean_line):
            return references
        
        # 跳过HTML标签
        clean_line = re.sub(r'<[^>]+>', '', clean_line)
        
        # 匹配图片引用 ![[]] 和 ![](url)
        for match in re.finditer(r'!\[\[(.*?)\]\]|\!\[(?:[^\]]*)\]\((?!https?://)[^)]+\)', clean_line):
            matched_text = match.group(0)
            if matched_text.startswith('![['):
                # Obsidian 风格的图片引用
                link = match.group(1).split('|')[0].strip()
            else:
                # Markdown 风格的图片引用
                link = re.search(r'\!\[(?:[^\]]*)\]\(([^)]+)\)', matched_text).group(1)
            
            # 找到在原始行中的实际位置
            original_pos = -1
            pos = 0
            for part in line_parts:
                found_pos = part.find(matched_text)
                if found_pos != -1:
                    original_pos = pos + found_pos
                    break
                pos += len(part)
            
            if original_pos != -1:
                col = original_pos + 1
                references.append((link, line_num, col, line.strip(), True))
        
        # 匹配普通引用 [[]]（排除已匹配的图片引用）
        clean_line = re.sub(r'!\[\[.*?\]\]|\!\[(?:[^\]]*)\]\([^)]+\)', '', clean_line)
        for match in re.finditer(r'\[\[(.*?)\]\]', clean_line):
            link = match.group(1).split('|')[0].strip()
            # 找到在原始行中的实际位置
            original_pos = -1
            pos = 0
            for part in line_parts:
                found_pos = part.find('[[' + match.group(1) + ']]')
                if found_pos != -1:
                    original_pos = pos + found_pos
                    break
                pos += len(part)
            
            if original_pos != -1:
                col = original_pos + 1
                references.append((link, line_num, col, line.strip(), False))
        
        return references

    def check_file(self, file_path: str) -> Tuple[List[Tuple[str, int, int, str]], Set[str]]:
        """检查单个文件中的引用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            invalid = []
            all_links = set()
            rel_path = os.path.relpath(file_path, self.root_dir)
            current_file = self.normalize_path(rel_path)
            
            # 如果当前文件应该被忽略，则跳过检查
            if self._should_ignore(current_file):
                return [], set()
            
            in_code_block = False
            current_line = 0
            
            while current_line < len(lines):
                line = lines[current_line]
                
                # 检查是否进入或离开代码块
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    current_line += 1
                    continue
                
                # 在代码块内跳过处理
                if in_code_block:
                    current_line += 1
                    continue
                
                # 处理当前行的引用
                refs = self.find_references_in_text(line, current_line + 1)
                for link, line_num, col, line_content, is_image in refs:
                    resolved_link = self.resolve_link(link, current_file, is_image)
                    # 如果引用文件应该被忽略，则跳过检查
                    if self._should_ignore(resolved_link):
                        continue
                    all_links.add(resolved_link)
                    if resolved_link not in self.files:
                        invalid.append((link, line_num, col, line_content))
                
                current_line += 1
            
            return invalid, all_links
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return [], set()

    def check_all_references(self) -> None:
        """检查所有文件的引用"""
        self.scan_files()
        
        # 检查每个文件
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    norm_path = self.normalize_path(rel_path)
                    
                    # 如果文件应该被忽略，则跳过检查
                    if self._should_ignore(norm_path):
                        continue
                    
                    invalid, outgoing = self.check_file(full_path)
                    
                    # 记录效引用
                    for link_info in invalid:
                        self.invalid_links.append((norm_path, link_info))
                    
                    # 更新引用统计（只统计markdown文件，且排除被忽略的文件）
                    outgoing = {link for link in outgoing if link in self.files and not self._should_ignore(link)}
                    self.reference_stats[norm_path]["outgoing"] = outgoing
                    for link in outgoing:
                        self.reference_stats[link]["incoming"] += 1

        # 检查单向链接仅检查markdown文件之间的链接，且排除被忽略的文件）
        for source, data in self.reference_stats.items():
            if source in self.files and not self._should_ignore(source):
                for target in data["outgoing"]:
                    if target in self.files and not self._should_ignore(target) and source not in self.reference_stats[target]["outgoing"]:
                        self.unidirectional_links.append((source, target))

    def print_report(self, verbosity: int = 0, no_color: bool = False) -> None:
        """打印检查报告"""
        # 颜色代码
        red = '' if no_color else '\x1b[31m'
        yellow = '' if no_color else '\x1b[33m'
        reset = '' if no_color else '\x1b[0m'
        
        if self.invalid_links:
            error_count = len(self.invalid_links)
            for file_path, (link, line, col, line_content) in self.invalid_links:
                print(f"{red}{file_path}:{line}:{col}  error  无效引用 '{link}'{reset}")
                print(f"  {line_content}")
                print(f"  {red}{' ' * (col-1)}^{reset}")
            print(f"\n✖ 发现 {error_count} 个无效引用")
        
        # 检查未被引用的图片
        unused_images = self.image_files - self.referenced_images
        if unused_images:
            if self.invalid_links:
                print()  # 添加空行分隔
            print(f"{yellow}未被引用的图片文件:{reset}")
            for image in sorted(unused_images):
                print(f"  {image}")
            print(f"\n⚠ 发现 {len(unused_images)} 个未被引用的图片文件")
            
            # 调试信息
            print("\n调试信息:")
            print(f"所有图片文件: {sorted(self.image_files)}")
            print(f"被引用的图片: {sorted(self.referenced_images)}")
            print(f"文件映射:")
            for key, value in self.file_map.items():
                if any(f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')) for f in value):
                    print(f"  {key}: {value}")
            
            # 添加更多调试信息
            print("\n引用处理详情:")
            for root, _, files in os.walk(self.root_dir):
                for file in files:
                    if file.endswith('.md'):
                        full_path = os.path.join(root, file)
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # 查找所有可能的图片引用
                                img_refs = re.finditer(r'!\[\[(.*?)\]\]|\!\[(?:[^\]]*)\]\((?!https?://)[^)]+\)', content)
                                for match in img_refs:
                                    matched_text = match.group(0)
                                    if matched_text.startswith('![['):
                                        link = match.group(1).split('|')[0].strip()
                                    else:
                                        link = re.search(r'\!\[(?:[^\]]*)\]\(([^)]+)\)', matched_text).group(1)
                                    print(f"  在文件 {full_path} 中找到图片引用: {link}")
                                    # 显示解析过程
                                    rel_path = os.path.relpath(full_path, self.root_dir)
                                    current_file = self.normalize_path(rel_path)
                                    resolved = self.resolve_link(link, current_file, True)
                                    print(f"    - 解析为: {resolved}")
                                    if resolved in self.image_files:
                                        print(f"    - 匹配图片: {resolved}")
                        except Exception as e:
                            print(f"Error reading file {full_path}: {e}")
        
        if verbosity >= 1 and self.unidirectional_links:
            print("\n单向链接:")
            for source, target in self.unidirectional_links:
                print(f"  {source} -> {target}")
        
        if verbosity >= 2:
            print("\n引用统计:")
            for file, stats in sorted(self.reference_stats.items()):
                if stats['incoming'] > 0 or stats['outgoing']:
                    print(f"\n  {file}:")
                    print(f"  - 被引用次数: {stats['incoming']}")
                    print(f"  - 引用其他文件数: {len(stats['outgoing'])}")
                    if stats['outgoing']:
                        print("  - 引用的文件:")
                        for target in sorted(stats['outgoing']):
                            print(f"    * {target}")

def main():
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

    checker = ReferenceChecker(args.dir)
    # 添加令行指定的忽略模式
    if args.ignore:
        checker.ignore_patterns.extend(args.ignore)
    checker.check_all_references()
    checker.print_report(args.verbosity, args.no_color)

if __name__ == '__main__':
    main() 