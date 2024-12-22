"""Markdown reference checker package."""
from importlib.metadata import version

from .checker import ReferenceChecker
from .cli import main
from .models import CheckResult, FileStats, Reference
from .parsers import MarkdownParser
from .utils import FileSystem

__version__ = version("md-ref-checker")

__all__ = [
    "Reference",
    "FileStats",
    "CheckResult",
    "ReferenceChecker",
    "MarkdownParser",
    "FileSystem",
    "main",
]
