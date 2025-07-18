"""
Core functionality for ebook management.

Contains the fundamental functions for file detection, grouping, and filtering.
"""

import os
import re
import shutil
import subprocess
from typing import List, Optional

# Default ebook file extensions
EBOOK_EXTENSIONS = [".epub", ".pdf", ".mobi", ".lrf", ".azw", ".azw3"]

# Priority order for --onefile feature (higher priority = preferred format)
FORMAT_PRIORITY = {
    ".epub": 6,  # Highest priority
    ".mobi": 5,
    ".azw": 4,
    ".azw3": 3,
    ".pdf": 2,
    ".lrf": 1,  # Lowest priority
}


def is_ebook_file(
    filename: str, allowed_extensions: Optional[List[str]] = None
) -> bool:
    """Check if a file is an ebook based on its extension."""
    extensions = allowed_extensions or EBOOK_EXTENSIONS
    return any(filename.lower().endswith(ext) for ext in extensions)


def find_ebooks(
    directory: str, allowed_extensions: Optional[List[str]] = None
) -> List[str]:
    """Find all ebook files in a directory."""
    ebooks = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_ebook_file(file, allowed_extensions):
                ebooks.append(os.path.join(root, file))
    return ebooks


def extract_book_identifier(filepath: str) -> str:
    """Extract a simple book identifier from filename for grouping."""
    filename = os.path.basename(filepath)
    # Remove extension
    name_without_ext = os.path.splitext(filename)[0]

    # Simple approach: try to extract "Author - Title" pattern
    if " - " in name_without_ext:
        parts = name_without_ext.split(" - ", 1)
        if len(parts) == 2:
            author = parts[0].strip()
            title = parts[1].strip()
            # Remove common suffixes like "(1)", "[2005]", etc.
            title = re.sub(r"\s*[\(\[][^)\]]*[\)\]]\s*$", "", title)
            return f"{author} - {title}".lower()

    # Fallback: use the base filename without extension
    return name_without_ext.lower()


def filter_onefile_per_book(ebooks: List[str]) -> List[str]:
    """Filter ebooks to keep only one file per book (highest priority format)."""
    if not ebooks:
        return ebooks

    # Group ebooks by book identifier
    book_groups: dict[str, List[str]] = {}
    for ebook_path in ebooks:
        book_id = extract_book_identifier(ebook_path)
        if book_id not in book_groups:
            book_groups[book_id] = []
        book_groups[book_id].append(ebook_path)

    # Select best format for each book
    filtered_ebooks = []
    for book_id, book_files in book_groups.items():
        if len(book_files) == 1:
            # Only one file for this book
            filtered_ebooks.append(book_files[0])
        else:
            # Multiple files - select the highest priority format
            best_file = max(
                book_files,
                key=lambda f: FORMAT_PRIORITY.get(os.path.splitext(f)[1].lower(), 0),
            )
            filtered_ebooks.append(best_file)

            # Log what we're skipping
            skipped = [f for f in book_files if f != best_file]
            print(f"Book: {book_id}")
            print(f"  Selected: {os.path.basename(best_file)}")
            for skipped_file in skipped:
                print(f"  Skipped:  {os.path.basename(skipped_file)}")

    return filtered_ebooks


def parse_extensions(ext_arg: Optional[str]) -> Optional[List[str]]:
    """Parse extension argument and return list of extensions."""
    if not ext_arg:
        return None

    # Handle comma-separated extensions
    extensions = [ext.strip() for ext in ext_arg.split(",")]

    # Ensure extensions start with a dot
    normalized_extensions = []
    for ext in extensions:
        if not ext.startswith("."):
            ext = "." + ext
        normalized_extensions.append(ext.lower())

    return normalized_extensions


def find_calibredb() -> Optional[str]:
    """Find the calibredb executable on the system."""
    # First try using shutil.which to find in PATH (recommended installation)
    calibredb_path = shutil.which("calibredb")
    if calibredb_path:
        return calibredb_path

    # Also try with .exe extension on Windows
    calibredb_path = shutil.which("calibredb.exe")
    if calibredb_path:
        return calibredb_path

    # Fallback: Common installation paths for different platforms
    common_paths = [
        # Windows paths - multiple drives
        r"C:\Program Files\Calibre2\calibredb.exe",
        r"C:\Program Files (x86)\Calibre2\calibredb.exe",
        r"D:\Program Files\Calibre2\calibredb.exe",
        r"E:\Program Files\Calibre2\calibredb.exe",
        r"F:\Program Files\Calibre2\calibredb.exe",
        # Also try without "2" suffix
        r"C:\Program Files\Calibre\calibredb.exe",
        r"C:\Program Files (x86)\Calibre\calibredb.exe",
        r"D:\Program Files\Calibre\calibredb.exe",
        r"E:\Program Files\Calibre\calibredb.exe",
        r"F:\Program Files\Calibre\calibredb.exe",
    ]

    # Try common installation paths as fallback
    for path in common_paths:
        if os.path.isfile(path):
            return path

    return None


def get_calibre_libraries() -> List[str]:
    """Get list of available Calibre libraries."""
    calibredb = find_calibredb()
    if not calibredb:
        return []

    try:
        # Get the default library path - just test if we can access calibre
        subprocess.run(
            [calibredb, "list_categories"],
            capture_output=True,
            text=True,
            check=True,
        )
        # If this succeeds, we have access to at least the default library
        return ["default"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def import_to_calibre(
    file_path: str, calibre_library: Optional[str] = None, add_duplicates: bool = False
) -> bool:
    """Import a single ebook file to Calibre library."""
    calibredb = find_calibredb()
    if not calibredb:
        return False

    try:
        cmd = [calibredb, "add", os.path.abspath(file_path)]

        # Add library specification if provided
        if calibre_library and calibre_library != "default":
            cmd.extend(["--library-path", calibre_library])

        # Handle duplicates
        if not add_duplicates:
            cmd.append("--ignore-duplicate")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return "Added book ids:" in result.stdout or len(result.stdout.strip()) > 0

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
