"""
Markdown Reference Checker

一个用于检查 Markdown 文件中引用完整性的工具。
"""

from .checker import ReferenceChecker
from .cli import main

__version__ = '0.1.0'
__all__ = ['ReferenceChecker', 'main'] 