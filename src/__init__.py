"""
md-ref-checker - A tool for checking references in Markdown files
"""

from .checker import ReferenceChecker
from .cli import main

__version__ = "0.1.0"
__all__ = ["ReferenceChecker", "main"] 