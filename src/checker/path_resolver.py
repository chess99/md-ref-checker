"""Path resolver for resolving relative paths to absolute paths"""

import os
from .utils import normalize_path

class PathResolver:
    """路径解析器"""

    def __init__(self, root_dir: str):
        """初始化路径解析器

        Args:
            root_dir: 根目录路径
        """
        self.root_dir = root_dir

    def resolve_link(self, link: str, source_file: str, is_image: bool = False) -> str:
        """解析链接

        Args:
            link: 链接路径
            source_file: 源文件路径
            is_image: 是否为图片链接

        Returns:
            解析后的路径
        """
        # 处理空路径
        if not link or link in ['.', './']:
            return ''

        # 如果是绝对路径，直接返回
        if link.startswith('/'):
            return normalize_path(link.lstrip('/'))

        # 获取源文件所在目录
        source_dir = os.path.dirname(source_file)

        # 处理 Windows 路径
        link = link.replace('\\', '/')
        source_dir = source_dir.replace('\\', '/')

        # 解析相对路径
        if link.startswith('../'):
            parts = source_dir.split('/')
            while link.startswith('../'):
                if parts:
                    parts.pop()
                link = link[3:]
            if parts:
                resolved = '/'.join(parts + [link])
            else:
                resolved = link
        else:
            resolved = os.path.normpath(os.path.join(source_dir, link))

        return normalize_path(resolved)