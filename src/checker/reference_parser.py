"""
Reference parsing functionality for Markdown reference checker
"""

import re
from typing import List, Tuple

class ReferenceParser:
    """Markdown引用解析器"""
    
    @staticmethod
    def find_references_in_text(text: str, line_num: int) -> List[Tuple[str, int, int, str, bool]]:
        """在普通文本中查找引用"""
        references = []
        line = text.strip()
        
        # 跳过行内代码块和其他特殊语法
        line_parts = []
        last_end = 0
        
        # 跳过所有任务列表标记 [x] 或 [ ]，不限于行首
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
            original_pos = ReferenceParser._find_original_position(line_parts, matched_text)
            if original_pos != -1:
                col = original_pos + 1
                references.append((link, line_num, col, line.strip(), True))
        
        # 匹配普通引用 [[]]（排除已匹配的图片引用）
        clean_line = re.sub(r'!\[\[.*?\]\]|\!\[(?:[^\]]*)\]\([^)]+\)', '', clean_line)
        for match in re.finditer(r'\[\[(.*?)\]\]', clean_line):
            link = match.group(1).split('|')[0].strip()
            # 找到在原始行中的实际位置
            original_pos = ReferenceParser._find_original_position(line_parts, '[[' + match.group(1) + ']]')
            if original_pos != -1:
                col = original_pos + 1
                references.append((link, line_num, col, line.strip(), False))
        
        return references
    
    @staticmethod
    def _find_original_position(line_parts: List[str], text: str) -> int:
        """在原始行中查找文本的位置"""
        pos = 0
        for part in line_parts:
            found_pos = part.find(text)
            if found_pos != -1:
                return pos + found_pos
            pos += len(part)
        return -1 