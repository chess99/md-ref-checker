"""
Data models for reference checker
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional
from collections import defaultdict

@dataclass
class Reference:
    """引用"""
    source: str
    target: str
    is_image: bool
    is_valid: bool = True
    resolved_path: Optional[str] = None

@dataclass
class ReferenceStats:
    """引用统计"""
    outgoing: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    incoming: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    referenced_images: Set[str] = field(default_factory=set)
    invalid_references: List[Reference] = field(default_factory=list)

@dataclass
class Config:
    """配置"""
    root_dir: str
    ignore_patterns: List[str] = field(default_factory=list)
    search_paths: List[str] = field(default_factory=lambda: ["."])
    verbosity: int = 1
    no_color: bool = False

class ReferenceError(Exception):
    """引用错误基类"""
    pass

class FileAccessError(ReferenceError):
    """文件访问错误"""
    pass

class ParseError(ReferenceError):
    """解析错误"""
    pass 