"""
Reference parsing functionality for Markdown reference checker
"""

import os
import re
from typing import List, Set, Tuple, Dict
from .utils import normalize_path, normalize_link

class ReferenceParser:
    """Markdown 引用解析器"""
    
    def __init__(self):
        # 匹配图片引用: ![alt](url) 或 ![alt][ref] 或 <img src="url">
        self.image_pattern = re.compile(
            r'!\[([^\]]*)\](?:\(([^)]+)\)|\[([^\]]+)\])|'  # Markdown 格式
            r'<img[^>]+src=[\'"](.*?)[\'"][^>]*>'          # HTML 格式
        )
        
        # 匹配链接引用: [text](url) 或 [text][ref] 或 <a href="url">
        self.link_pattern = re.compile(
            r'\[([^\]]+)\](?:\(([^)]+)\)|\[([^\]]+)\])|'   # Markdown 格式
            r'<a[^>]+href=[\'"](.*?)[\'"][^>]*>'           # HTML 格式
        )
        
        # 匹配引用定义: [ref]: url
        self.ref_def_pattern = re.compile(r'^\s*\[([^\]]+)\]:\s*(\S+)(?:\s+"[^"]*")?$')

    @staticmethod
    def find_references_in_text(text: str, line_offset: int = 1) -> List[Tuple[str, int, bool]]:
        """从文本中查找所有引用
        
        Args:
            text: 要解析的文本内容
            line_offset: 行号偏移量，用于调整返回的行号
            
        Returns:
            List[Tuple[str, int, bool]]: 引用列表，每个元素为 (引用文本, 行号, 是否为图片引用)
        """
        references = []
        
        # 跳过代码块内的内容
        in_code_block = False
        current_line = line_offset
        
        # 分行处理以跟踪行号
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # 检查代码块标记
            if line.startswith('```'):
                in_code_block = not in_code_block
                current_line += 1
                continue
            
            # 在代码块内则跳过
            if in_code_block:
                current_line += 1
                continue
                
            # 跳过表格语法
            if line.startswith('|') and line.endswith('|'):
                current_line += 1
                continue
                
            # 跳过引用块
            if line.startswith('>'):
                current_line += 1
                continue
                
            # 处理行内代码和HTML标签
            text_to_process = line
            
            # 移除HTML标签内容
            text_to_process = re.sub(r'<[^>]+>.*?</[^>]+>', '', text_to_process)
            
            # 处理行内代码
            parts = text_to_process.split('`')
            if len(parts) % 2 == 0:  # 如果有未闭合的行内代码，跳过整行
                current_line += 1
                continue
                
            # 只处理不在行内代码中的部分
            final_text = ''
            for i, part in enumerate(parts):
                if i % 2 == 0:  # 不在行内代码中的部分
                    final_text += part
            
            # 收集所有引用及其位置
            refs_with_pos = []
            
            # 查找图片引用 ![[...]]
            for match in re.finditer(r'!\[\[(.*?)(?:\|.*?)?\]\]', final_text):
                ref = match.group(1).strip()
                if ref and not ref.startswith(('http://', 'https://', 'ftp://')):
                    refs_with_pos.append((ref, match.start(), True))
            
            # 查找普通引用 [[...]]
            for match in re.finditer(r'(?<!!)\[\[(.*?)(?:\|.*?)?\]\]', final_text):
                ref = match.group(1).strip()
                if ref and not ref.startswith(('http://', 'https://', 'ftp://')):
                    refs_with_pos.append((ref, match.start(), False))
            
            # 按位置排序并添加到结果中
            refs_with_pos.sort(key=lambda x: x[1])
            references.extend((ref, current_line, is_image) for ref, _, is_image in refs_with_pos)
            
            current_line += 1
        
        return references

    def parse_file(self, file_path: str) -> Tuple[Set[str], Set[str]]:
        """解析文件中的所有引用
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[Set[str], Set[str]]: (图片引用集合, 链接引用集合)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果 UTF-8 解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception:
                return set(), set()
        except Exception:
            return set(), set()
        
        # 获取文件所在目录作为基准目录
        base_dir = os.path.dirname(file_path)
        
        # 解析引用定义
        ref_defs = self._parse_reference_definitions(content)
        
        # 解析图片引用
        image_refs = set()
        for match in self.image_pattern.finditer(content):
            ref = self._extract_reference(match, ref_defs, base_dir)
            if ref:
                image_refs.add(ref)
        
        # 解析链接引用
        link_refs = set()
        for match in self.link_pattern.finditer(content):
            ref = self._extract_reference(match, ref_defs, base_dir)
            if ref:
                link_refs.add(ref)
        
        return image_refs, link_refs
    
    def _parse_reference_definitions(self, content: str) -> dict:
        """解析引用定义
        
        Args:
            content: 文件内容
            
        Returns:
            dict: 引用定义字典
        """
        ref_defs = {}
        for line in content.splitlines():
            match = self.ref_def_pattern.match(line)
            if match:
                ref_id = match.group(1).lower()  # 引用 ID 不区分大小写
                url = match.group(2)
                ref_defs[ref_id] = url
        return ref_defs
    
    def _extract_reference(self, match: re.Match, ref_defs: dict, base_dir: str) -> str:
        """从匹配结果中提取引用
        
        Args:
            match: 正则匹配结果
            ref_defs: 引用定义字典
            base_dir: 基准目录
            
        Returns:
            str: 标准化后的引用路径
        """
        groups = match.groups()
        
        # Markdown 内联格式: ![alt](url) 或 [text](url)
        if groups[1]:
            url = groups[1].split()[0]  # 移除标题等额外内容
        # Markdown 引用格式: ![alt][ref] 或 [text][ref]
        elif groups[2]:
            ref_id = groups[2].lower()
            url = ref_defs.get(ref_id, '')
        # HTML 格式: <img src="url"> 或 <a href="url">
        elif groups[3]:
            url = groups[3]
        else:
            return ''
        
        # 移除 URL 中的锚点和查询参数
        url = normalize_link(url)
        
        # 如果是相对路径，转换为相对于项目根目录的路径
        if not url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            if url.startswith('/'):
                # 绝对路径（相对于项目根目录）
                url = url.lstrip('/')
            else:
                # 相对路径（相对于当前文件）
                abs_path = os.path.normpath(os.path.join(base_dir, url))
                url = os.path.relpath(abs_path, os.path.dirname(base_dir))
            
            url = normalize_path(url)
        
        return url