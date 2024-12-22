"""Markdown reference checker package."""
from importlib.metadata import version

from .models import Reference, FileStats, CheckResult
from .checker import ReferenceChecker
from .parsers import MarkdownParser
from .utils import FileSystem
from .cli import main

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
