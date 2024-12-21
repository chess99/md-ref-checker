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
    def find_references_in_text(text: str, line_num: int) -> List[Tuple[str, int, int, str, bool]]:
        """在文本中查找引用。
        
        Args:
            text: 要查找的文本
            line_num: 行号
            
        Returns:
            引用列表，每个元素为 (引用路径, 行号, 列号, 原始文本, 是否为图片引用) 的元组
        """
        references = []
        
        # 匹配图片引用: ![[image.png]] 或 ![[image.png|alt text]]
        for match in re.finditer(r'!\[\[(.*?)(?:\|.*?)?\]\]', text):
            link = match.group(1)
            col = match.start()
            references.append((link, line_num, col, text, True))
        
        # 匹配普通引用: [[doc.md]] 或 [[doc.md|alias]]
        # 不匹配以!开头的图片引用
        for match in re.finditer(r'(?<!!)\[\[(.*?)(?:\|.*?)?\]\]', text):
            link = match.group(1)
            col = match.start()
            references.append((link, line_num, col, text, False))
        
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

    def parse_references(self, content: str) -> List[Tuple[str, bool]]:
        """解析文本中的引用。
        
        Args:
            content: 要解析的文本内容
            
        Returns:
            引用列表，每个元素为 (引用路径, 是否为图片引用) 的元组
        """
        references = []
        lines = content.split('\n')
        in_code_block = False
        
        for line_num, line in enumerate(lines, 1):
            # 检查是否进入或离开代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # 在代码块内跳过处理
            if in_code_block:
                continue
            
            # 解析当前行的引用
            line_refs = self.find_references_in_text(line, line_num)
            for link, _, _, _, is_image in line_refs:
                # 处理别名
                if '|' in link:
                    link = link.split('|')[0].strip()
                references.append((link, is_image))
        
        return references

    def _remove_code_blocks(self, content: str) -> str:
        """移除代码块中的内容，避免解析代码块中的引用

        Args:
            content: 原始内容

        Returns:
            str: 移除代码块后的内容
        """
        # 移除行内代码
        content = re.sub(r'`[^`]+`', '', content)
        
        # 移除围栏代码块
        content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        
        return content

    def _parse_image_references(self, content: str) -> Set[str]:
        """解析图片引用

        Args:
            content: 文档内容

        Returns:
            Set[str]: 图片引用集合
        """
        refs = set()
        for match in re.finditer(r'!\[\[(.*?)(?:\|.*?)?\]\]', content):
            ref = match.group(1).strip()
            if ref and not ref.startswith(('http://', 'https://', 'ftp://')):
                refs.add(ref)
        return refs

    def _parse_doc_references(self, content: str) -> Set[str]:
        """解析文档引用

        Args:
            content: 文档内容

        Returns:
            Set[str]: 文档引用集合
        """
        refs = set()
        for match in re.finditer(r'(?<!!)\[\[(.*?)(?:\|.*?)?\]\]', content):
            ref = match.group(1).strip()
            if ref and not ref.startswith(('http://', 'https://', 'ftp://')):
                refs.add(ref)
        return refs