"""
Ebook Manager - Advanced ebook collection management utility

A standalone command-line utility for advanced ebook collection management
with support for format filtering, deduplication, and beets integration.
"""

__version__ = "0.1.0"
__author__ = "OttScott"
__email__ = "your.email@example.com"

from .__main__ import (
    batch_import_ebooks,
    calibre_takes_control_workflow_cli,
    import_collection,
    import_ebook_to_beets,
    import_single_directory,
    main,
    process_ebook_with_beets,
    scan_collection,
    suggest_organization,
    test_organization,
)
from .core import (
    EBOOK_EXTENSIONS,
    FORMAT_PRIORITY,
    extract_book_identifier,
    filter_onefile_per_book,
    find_ebooks,
    is_ebook_file,
    parse_extensions,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "is_ebook_file",
    "find_ebooks",
    "extract_book_identifier",
    "filter_onefile_per_book",
    "parse_extensions",
    "FORMAT_PRIORITY",
    "EBOOK_EXTENSIONS",
    "main",
    "process_ebook_with_beets",
    "import_ebook_to_beets",
    "scan_collection",
    "import_collection",
    "batch_import_ebooks",
    "test_organization",
    "suggest_organization",
    "import_single_directory",
    "calibre_takes_control_workflow_cli",
]
