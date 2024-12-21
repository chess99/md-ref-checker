"""
Main checker functionality for Markdown reference checker
"""

import os
from typing import Dict, List, Set, Tuple
from .file_scanner import FileScanner
from .reference_parser import ReferenceParser
from .utils import is_markdown_file, normalize_path

class ReferenceChecker:
    """Markdown 引用检查器"""
    
    def __init__(self, file_scanner: FileScanner):
        self.file_scanner = file_scanner
        self.reference_parser = ReferenceParser()
        self.markdown_files: Set[str] = set()
        self.broken_references: Dict[str, List[str]] = {}
        self.unused_files: Set[str] = set()
        self.scanned = False
    
    def scan(self) -> None:
        """扫描并检查所有引用"""
        # 扫描文件系统
        self.file_scanner.scan()
        
        # 获取所有 Markdown 文件
        self.markdown_files = {f for f in self.file_scanner.files if is_markdown_file(f)}
        
        # 清空之前的结果
        self.broken_references.clear()
        self.unused_files = set(self.file_scanner.image_files)  # 初始时所有图片都是未使用的
        
        # 检查每个 Markdown 文件中的引用
        for md_file in self.markdown_files:
            self._check_file_references(md_file)
        
        self.scanned = True
    
    def _check_file_references(self, file_path: str) -> None:
        """检查单个文件中的引用
        
        Args:
            file_path: 文件路径
        """
        # 获取文件的完整路径
        abs_path = os.path.join(self.file_scanner.root_dir, file_path)
        
        # 解析文件中的引用
        image_refs, link_refs = self.reference_parser.parse_file(abs_path)
        
        # 检查图片引用
        broken_refs = []
        for ref in image_refs:
            # 如果是外部链接，跳过检查
            if ref.startswith(('http://', 'https://', 'ftp://')):
                continue
            
            # 查找对应的文件
            matches = self.file_scanner.get_file_mapping(ref)
            if not matches:
                broken_refs.append(ref)
            else:
                # 标记图片为已使用
                for match in matches:
                    if match in self.unused_files:
                        self.unused_files.remove(match)
        
        # 检查链接引用
        for ref in link_refs:
            # 如果是外部链接或特殊协议，跳过检查
            if ref.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                continue
            
            # 查找对应的文件
            matches = self.file_scanner.get_file_mapping(ref)
            if not matches:
                broken_refs.append(ref)
        
        # 记录损坏的引用
        if broken_refs:
            self.broken_references[file_path] = broken_refs
    
    def get_broken_references(self) -> Dict[str, List[str]]:
        """获取损坏的引用
        
        Returns:
            Dict[str, List[str]]: 文件路径到损坏引用列表的映射
        """
        if not self.scanned:
            self.scan()
        return self.broken_references
    
    def get_unused_images(self) -> Set[str]:
        """获取未使用的图片文件
        
        Returns:
            Set[str]: 未使用的图片文件路径集合
        """
        if not self.scanned:
            self.scan()
        return self.unused_files
    
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        if not self.scanned:
            self.scan()
        
        total_broken_refs = sum(len(refs) for refs in self.broken_references.values())
        
        return {
            'total_markdown_files': len(self.markdown_files),
            'total_image_files': len(self.file_scanner.image_files),
            'broken_references': total_broken_refs,
            'files_with_broken_refs': len(self.broken_references),
            'unused_images': len(self.unused_files)
        } 