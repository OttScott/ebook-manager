"""
Ebook Manager - Advanced ebook collection management utility

A standalone command-line utility for advanced ebook collection management
with support for format filtering, deduplication, and beets integration.
"""

__version__ = "0.1.0"
__author__ = "OttScott"
__email__ = "your.email@example.com"

from .core import (
    is_ebook_file,
    find_ebooks,
    extract_book_identifier,
    filter_onefile_per_book,
    parse_extensions,
    FORMAT_PRIORITY,
    EBOOK_EXTENSIONS,
)

from .__main__ import main

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "main",
    "is_ebook_file",
    "find_ebooks",
    "extract_book_identifier",
    "filter_onefile_per_book",
    "parse_extensions",
    "FORMAT_PRIORITY",
    "EBOOK_EXTENSIONS",
]
