"""
Core functionality for ebook management.

Contains the fundamental functions for file detection, grouping, and filtering.
"""

import os
import re
import shutil
import subprocess
import json
from typing import List, Optional

# Default ebook file extensions (including comic book formats)
EBOOK_EXTENSIONS = [
    ".epub",
    ".pdf",
    ".mobi",
    ".lrf",
    ".azw",
    ".azw3",
    ".cbr",
    ".cbz",
]

# Priority order for --onefile feature (higher priority = preferred format)
FORMAT_PRIORITY = {
    ".epub": 8,  # Highest priority for traditional ebooks
    ".mobi": 7,
    ".azw": 6,
    ".azw3": 5,
    ".pdf": 4,
    ".cbz": 3,  # Comic book ZIP (preferred over CBR due to wider support)
    ".cbr": 2,  # Comic book RAR
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
                key=lambda f: FORMAT_PRIORITY.get(
                    os.path.splitext(f)[1].lower(), 0
                ),
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
    file_path: str,
    calibre_library: Optional[str] = None,
    add_duplicates: bool = False,
    verbose: bool = False,
) -> tuple[bool, str]:
    """Import a single ebook file to Calibre library.

    Returns:
        tuple: (success: bool, message: str) - success status and diagnostic message
    """
    calibredb = find_calibredb()
    if not calibredb:
        return False, "Calibre (calibredb) executable not found"

    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    try:
        cmd = [calibredb, "add", os.path.abspath(file_path)]

        # Add library specification if provided
        if calibre_library and calibre_library != "default":
            cmd.extend(["--library-path", calibre_library])

        # Handle duplicates
        if not add_duplicates:
            cmd.extend(["--automerge", "ignore"])

        if verbose:
            print(f"  Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        success = (
            "Added book ids:" in result.stdout
            or len(result.stdout.strip()) > 0
        )
        message = (
            result.stdout.strip()
            if result.stdout.strip()
            else "Import completed"
        )

        if verbose and result.stderr:
            message += f" (stderr: {result.stderr.strip()})"

        return success, message

    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        if isinstance(e, subprocess.CalledProcessError):
            error_msg = f"calibredb command failed (exit code {e.returncode})"
            if e.stdout:
                error_msg += f"\nstdout: {e.stdout.strip()}"
            if e.stderr:
                error_msg += f"\nstderr: {e.stderr.strip()}"
        else:
            error_msg = f"Command error: {e}"
        return False, error_msg


def find_books_in_calibre(old_path: str) -> List[dict]:
    """Find books in Calibre library by file path."""
    calibredb = find_calibredb()
    if not calibredb:
        return []

    try:
        # Get all books with their formats (which contain file paths)
        result = subprocess.run(
            [calibredb, "list", "--fields", "id,title,formats"],
            capture_output=True,
            text=True,
            check=True,
        )

        books = []
        old_path_normalized = os.path.normpath(old_path.lower())

        # Parse the output to find books with matching file paths
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]:  # Skip header line
            if not line.strip():
                continue

            # Split by tab or comma, handling possible embedded commas in titles
            parts = line.split("\t") if "\t" in line else line.split(",", 2)
            if len(parts) >= 3:
                book_id = parts[0].strip()
                title = parts[1].strip()
                formats = parts[2].strip()

                # Check if any format path matches our old path
                if formats and formats.lower() != "none":
                    # formats contains paths like: /path/to/file.epub,/path/to/file.pdf
                    format_paths = [f.strip() for f in formats.split(",")]
                    for format_path in format_paths:
                        if (
                            format_path
                            and os.path.normpath(format_path.lower())
                            == old_path_normalized
                        ):
                            books.append(
                                {
                                    "id": book_id,
                                    "path": format_path,
                                    "title": title,
                                }
                            )
                            break

        return books

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error finding books in Calibre: {e}")
        return []


def update_calibre_book_path(
    book_id: str, old_path: str, new_path: str
) -> bool:
    """Update a book's file path in Calibre database.

    Args:
        book_id: Calibre book ID
        old_path: Original file path (for reference)
        new_path: New file path to update to
    """
    calibredb = find_calibredb()
    if not calibredb:
        return False

    try:
        # First, check if the file actually exists at the new location
        if not os.path.exists(new_path):
            print(f"Warning: New file path does not exist: {new_path}")
            return False

        # Use calibredb to add the book at the new location and remove the old one
        # This is safer than trying to directly modify the database
        result = subprocess.run(
            [calibredb, "add", "--duplicates", new_path],
            capture_output=True,
            text=True,
            check=True,
        )

        if "Added book ids:" in result.stdout:
            # If successful, remove the old entry
            subprocess.run(
                [calibredb, "remove", book_id],
                capture_output=True,
                text=True,
                check=False,  # Don't fail if removal fails
            )
            return True

        return False

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def sync_calibre_after_move(
    old_paths: List[str], new_paths: List[str]
) -> dict:
    """Sync Calibre database after files have been moved by beets."""
    if len(old_paths) != len(new_paths):
        raise ValueError("old_paths and new_paths must have the same length")

    calibredb = find_calibredb()
    if not calibredb:
        return {"updated": 0, "failed": 0, "not_in_calibre": 0}

    stats = {"updated": 0, "failed": 0, "not_in_calibre": 0}

    print("🔄 Syncing Calibre database after file moves...")

    for old_path, new_path in zip(old_paths, new_paths):
        print(f"  Checking: {os.path.basename(old_path)}")

        # Find books that reference the old path
        books = find_books_in_calibre(old_path)

        if not books:
            stats["not_in_calibre"] += 1
            print("    ℹ️  Not found in Calibre library")
            continue

        # Update each book found
        for book in books:
            if update_calibre_book_path(book["id"], old_path, new_path):
                stats["updated"] += 1
                print(f"    ✅ Updated Calibre entry (ID: {book['id']})")
            else:
                stats["failed"] += 1
                print(
                    f"    ❌ Failed to update Calibre entry (ID: {book['id']})"
                )

    return stats


def sync_calibre_with_beets_library() -> dict:
    """
    Sync Calibre database with current beets library state.

    This function compares the current beets library with Calibre's database
    and identifies books that need to be imported to Calibre. Since Calibre
    copies files to its own structure on import, we now match by metadata
    (title/author) rather than file paths.

    Returns:
        dict: Statistics about the sync operation including missing_paths list
    """
    from typing import Any, Dict

    calibredb = find_calibredb()
    if not calibredb:
        return {
            "error": "Calibre not found",
            "updated": 0,
            "failed": 0,
            "not_in_calibre": 0,
            "missing_paths": [],
        }

    stats: Dict[str, Any] = {
        "updated": 0,
        "failed": 0,
        "not_in_calibre": 0,
        "scanned": 0,
        "missing_paths": [],
    }

    print("🔄 Syncing Calibre database with current beets library...")

    try:
        # Get all ebooks currently in beets library with metadata
        result = subprocess.run(
            ["beet", "ls", "-f", "$path|$artist|$album|$title", "ebook:true"],
            capture_output=True,
            text=True,
            check=True,
        )

        if not result.stdout.strip():
            print("ℹ️  No ebooks found in beets library")
            return stats

        # Parse beets library entries
        beets_books: Dict[str, Dict[str, str]] = {}
        for line in result.stdout.strip().split("\n"):
            if line and "|" in line:
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    path, artist, album, title = parts
                    # Use album as title if title is empty (common for audiobooks)
                    book_title = (
                        title.strip() if title.strip() else album.strip()
                    )
                    author = artist.strip()

                    if book_title and author:
                        # Create normalized keys for matching
                        title_key = (
                            book_title.lower()
                            .replace(" ", "")
                            .replace("-", "")
                            .replace("_", "")
                        )
                        author_key = (
                            author.lower()
                            .replace(" ", "")
                            .replace("-", "")
                            .replace("_", "")
                        )
                        match_key = f"{author_key}|{title_key}"

                        beets_books[match_key] = {
                            "path": path.strip(),
                            "author": author,
                            "title": book_title,
                            "metadata": f"{author} - {book_title}",
                        }

        stats["scanned"] = len(beets_books)
        print(f"📚 Found {len(beets_books)} ebooks in beets library")

        # Get all books from Calibre library with metadata
        calibre_result = subprocess.run(
            [calibredb, "list", "--fields", "title,authors", "--for-machine"],
            capture_output=True,
            text=True,
            check=True,
        )

        if not calibre_result.stdout.strip():
            print("ℹ️  No books found in Calibre library")
            # All beets books are missing from Calibre
            missing_paths: List[str] = stats["missing_paths"]
            for book_info in beets_books.values():
                missing_paths.append(book_info["path"])
            stats["not_in_calibre"] = len(beets_books)
            return stats

        # Parse Calibre library entries
        try:
            calibre_books_data = json.loads(calibre_result.stdout)

            calibre_books: Dict[str, Dict[str, str]] = {}
            for book in calibre_books_data:
                title = book.get("title", "").strip()
                authors = book.get("authors", "").strip()

                if title and authors:
                    # Create normalized keys for matching
                    title_key = (
                        title.lower()
                        .replace(" ", "")
                        .replace("-", "")
                        .replace("_", "")
                    )
                    author_key = (
                        authors.lower()
                        .replace(" ", "")
                        .replace("-", "")
                        .replace("_", "")
                    )
                    match_key = f"{author_key}|{title_key}"
                    calibre_books[match_key] = {
                        "id": book.get("id", ""),
                        "title": title,
                        "authors": authors,
                    }

            print(f"📖 Found {len(calibre_books)} books in Calibre library")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error parsing Calibre library data: {e}")
            error_msg = f"Failed to parse Calibre data: {e}"
            return {
                "error": error_msg,
                "updated": 0,
                "failed": 0,
                "not_in_calibre": 0,
                "missing_paths": [],
            }

        # Compare libraries by metadata
        found_count = 0
        missing_paths = stats["missing_paths"]
        for match_key, beets_book in beets_books.items():
            if match_key in calibre_books:
                found_count += 1
                print(f"  ✅ Found in Calibre: {beets_book['metadata']}")
            else:
                stats["not_in_calibre"] = stats["not_in_calibre"] + 1
                missing_paths.append(beets_book["path"])
                print(f"  ❌ Missing from Calibre: {beets_book['metadata']}")

        stats["updated"] = found_count
        print("\n📋 Sync Results:")
        print(f"  ✅ Found in Calibre: {found_count} books")
        print(f"  ❌ Missing from Calibre: {stats['not_in_calibre']} books")

        return stats

    except subprocess.CalledProcessError as e:
        print(f"❌ Error accessing libraries: {e}")
        return {
            "error": str(e),
            "updated": 0,
            "failed": 0,
            "not_in_calibre": 0,
            "missing_paths": [],
        }
    except (OSError, ValueError) as e:
        print(f"❌ Error during sync: {e}")
        return {
            "error": str(e),
            "updated": 0,
            "failed": 0,
            "not_in_calibre": 0,
            "missing_paths": [],
        }


def get_calibre_default_library_path() -> Optional[str]:
    """Get Calibre's default library path."""
    calibredb = find_calibredb()
    if not calibredb:
        return None

    try:
        # Test if Calibre library is accessible by running a simple command
        subprocess.run(
            [calibredb, "list", "--limit", "1", "--fields", "id"],
            capture_output=True,
            text=True,
            check=True,
        )

        # If this works, we have access to the default library
        # For now, return a status indicating default Calibre library is accessible
        # Future enhancement: Parse actual library path from Calibre preferences
        return "default"  # Indicates default library is accessible

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def configure_beets_for_calibre_integration(
    calibre_library_path: Optional[str] = None,
    organize_for_calibre: bool = False,
) -> dict:
    """
    Configure beets to work optimally with Calibre integration.

    Args:
        calibre_library_path: Optional specific Calibre library path
        organize_for_calibre: Whether to organize files in a Calibre-friendly structure

    Returns:
        dict: Configuration recommendations and status
    """
    recommendations: List[str] = []

    config_info = {
        "status": "analyzed",
        "recommendations": recommendations,
        "calibre_path": None,
        "beets_organized": False,
        "integration_mode": "organize_first",  # The recommended approach
    }

    # Check Calibre availability
    calibre_path = get_calibre_default_library_path()
    config_info["calibre_path"] = calibre_path

    if calibre_path:
        recommendations.append(
            "✅ Calibre detected - use 'organize-then-import' workflow for best results"
        )
    else:
        recommendations.append(
            "⚠️ Calibre not found - install Calibre for enhanced functionality"
        )

    # Beets organization recommendations
    if organize_for_calibre:
        recommendations.extend(
            [
                "📁 Recommended beets path format: $artist/$album/$track $title",
                "📚 Use beets 'move' command to organize before Calibre import",
                "🔄 Use 'sync-calibre' command after organization to maintain sync",
            ]
        )

    # Integration mode explanation
    recommendations.append(
        "🎯 Best Practice: Let beets organize first, then import clean files to Calibre"
    )

    return config_info


def enhanced_calibre_workflow_with_config(
    directory: str,
    calibre_library: Optional[str] = None,
    auto_discover_library: bool = True,
) -> dict:
    """
    Enhanced workflow with automatic library path discovery.

    Args:
        directory: Source directory for ebooks
        calibre_library: Optional specific Calibre library path
        auto_discover_library: Whether to auto-discover Calibre library path

    Returns:
        dict: Workflow results and configuration info
    """
    workflow_info = {
        "calibre_library": "default",
        "library_discovered": False,
        "configuration": {},
        "workflow_ready": False,
    }

    # Auto-discover library if requested
    if auto_discover_library and not calibre_library:
        discovered_path = get_calibre_default_library_path()
        if discovered_path:
            workflow_info["calibre_library"] = discovered_path
            workflow_info["library_discovered"] = True
    elif calibre_library:
        workflow_info["calibre_library"] = calibre_library
        workflow_info["library_discovered"] = True

    # Get configuration recommendations
    calibre_lib_path = workflow_info["calibre_library"]
    config = configure_beets_for_calibre_integration(
        calibre_library_path=(
            calibre_lib_path if isinstance(calibre_lib_path, str) else None
        ),
        organize_for_calibre=True,
    )
    workflow_info["configuration"] = config

    # Determine if workflow is ready
    workflow_info["workflow_ready"] = (
        find_calibredb() is not None and workflow_info["library_discovered"]
    )

    return workflow_info


def find_calibre_file_path_for_book(
    book_title: str, book_author: str
) -> Optional[str]:
    """Find the file path where Calibre stores a specific book.

    Args:
        book_title: The book title to search for
        book_author: The book author to search for

    Returns:
        The file path to the Calibre-managed file, or None if not found
    """
    calibredb = find_calibredb()
    if not calibredb:
        return None

    try:
        # Search for the book by title and author
        search_query = f'title:"{book_title}" and author:"{book_author}"'
        result = subprocess.run(
            [
                calibredb,
                "list",
                "--search",
                search_query,
                "--fields",
                "formats",
                "--for-machine",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if not result.stdout.strip():
            return None

        books = json.loads(result.stdout)

        if books and len(books) > 0:
            # Get the formats (file paths) for the first matching book
            formats = books[0].get("formats", [])
            if formats:
                # Return the first format's path (Calibre stores multiple formats)
                # formats: list like ["/path/to/library/Author/Book/book.epub"]
                return formats[0] if isinstance(formats, list) else formats

        return None

    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return None


def update_beets_file_path(old_path: str, new_path: str) -> bool:
    """Update a file path in beets database.

    Args:
        old_path: Original file path in beets database
        new_path: New file path to update to (Calibre-managed location)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Use beets modify command to update the path
        # This updates the database entry to point to the new location
        old_path_query = f'path:"{old_path}"'
        new_path_value = f"path={new_path}"
        result = subprocess.run(
            ["beet", "modify", old_path_query, new_path_value],
            capture_output=True,
            text=True,
            check=True,
        )

        return (
            "1 items modified" in result.stdout
            or "modified" in result.stdout.lower()
        )

    except subprocess.CalledProcessError:
        return False


def delete_file_safely(file_path: str, dry_run: bool = False) -> bool:
    """Safely delete a file with optional dry-run mode.

    Args:
        file_path: Path to file to delete
        dry_run: If True, don't actually delete, just check if deletion would succeed

    Returns:
        True if deletion succeeded (or would succeed in dry-run), False otherwise
    """
    if not os.path.exists(file_path):
        return False

    if dry_run:
        # Just check if we can delete (file exists and is writable)
        return os.access(file_path, os.W_OK)

    try:
        os.remove(file_path)
        return True
    except (OSError, IOError):
        return False


def calibre_takes_control_workflow(
    source_directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Execute the Calibre-takes-control workflow.

    This workflow:
    1. Imports books to both beets and Calibre
    2. After Calibre import, updates beets database to point to Calibre-managed files
    3. Deletes the original/beets copies, letting Calibre be the file manager

    Args:
        source_directory: Directory containing ebooks to import
        allowed_extensions: File extensions to process
        onefile: Whether to use one-file-per-book filtering
        dry_run: If True, don't actually modify files or databases

    Returns:
        Dictionary with workflow statistics and results
    """
    stats = {
        "total_files": 0,
        "beets_imported": 0,
        "calibre_imported": 0,
        "database_updated": 0,
        "files_deleted": 0,
        "errors": [],
        "dry_run": dry_run,
    }

    calibredb = find_calibredb()
    if not calibredb:
        stats["errors"].append("Calibre not found")
        return stats

    # Find ebooks to process
    ebooks = find_ebooks(source_directory, allowed_extensions)

    if onefile:
        ebooks = filter_onefile_per_book(ebooks)

    stats["total_files"] = len(ebooks)

    if not ebooks:
        stats["errors"].append("No ebook files found")
        return stats

    for ebook_path in ebooks:
        try:
            # Step 1: Import to beets first (to get metadata)
            if not dry_run:
                beets_result = subprocess.run(
                    ["beet", "import-ebooks", os.path.abspath(ebook_path)],
                    capture_output=True,
                    text=True,
                    check=False,  # Don't fail on beets import errors
                )

                if (
                    beets_result.returncode == 0
                    and "Successfully imported" in beets_result.stdout
                ):
                    stats["beets_imported"] += 1
                else:
                    stats["errors"].append(
                        f"Beets import failed for {os.path.basename(ebook_path)}"
                    )
                    continue
            else:
                stats["beets_imported"] += 1  # Assume success in dry-run

            # Step 2: Import to Calibre
            if not dry_run:
                calibre_success, calibre_message = import_to_calibre(
                    ebook_path, verbose=False
                )

                if not calibre_success:
                    filename = os.path.basename(ebook_path)
                    stats["errors"].append(
                        f"Calibre import failed for {filename}: {calibre_message}"
                    )
                    continue

                stats["calibre_imported"] += 1
            else:
                stats["calibre_imported"] += 1  # Assume success in dry-run

            # Step 3: Get book metadata from beets to find Calibre location
            if not dry_run:
                # Get book title and author from beets
                path_query = f'path:"{ebook_path}"'
                beets_info = subprocess.run(
                    ["beet", "ls", "-f", "$title|$artist", path_query],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if "|" in beets_info.stdout:
                    title, author = beets_info.stdout.strip().split("|", 1)

                    # Find where Calibre stored the file
                    calibre_path = find_calibre_file_path_for_book(
                        title.strip(), author.strip()
                    )

                    if calibre_path and os.path.exists(calibre_path):
                        # Step 4: Update beets database to point to Calibre location
                        if update_beets_file_path(ebook_path, calibre_path):
                            stats["database_updated"] += 1

                            # Step 5: Delete original file
                            # (now that beets points to Calibre)
                            if delete_file_safely(ebook_path):
                                stats["files_deleted"] += 1
                            else:
                                stats["errors"].append(
                                    f"Failed to delete original file: "
                                    f"{ebook_path}"
                                )
                        else:
                            filename = os.path.basename(ebook_path)
                            stats["errors"].append(
                                f"Failed to update beets database for {filename}"
                            )
                    else:
                        filename = os.path.basename(ebook_path)
                        stats["errors"].append(
                            f"Could not find Calibre file location for {filename}"
                        )
                else:
                    filename = os.path.basename(ebook_path)
                    stats["errors"].append(
                        f"Could not get metadata from beets for {filename}"
                    )
            else:
                # Dry-run: assume success
                stats["database_updated"] += 1
                stats["files_deleted"] += 1

        except Exception as e:
            stats["errors"].append(
                f"Error processing {os.path.basename(ebook_path)}: {str(e)}"
            )

    return stats


def get_all_calibre_books() -> List[dict]:
    """
    Get all books from the Calibre database with full metadata.

    Returns:
        List of dictionaries containing book metadata including file paths
    """
    calibredb = find_calibredb()
    if not calibredb:
        return []

    try:
        # Get comprehensive book list with all metadata
        result = subprocess.run(
            [
                calibredb,
                "list",
                "--fields",
                "id,title,authors,formats,pubdate,tags,series,series_index,uuid",
                "--for-machine",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            books = json.loads(result.stdout)

            # Enhance each book with actual file paths from formats
            enhanced_books = []
            for book in books:
                enhanced_book = book.copy()

                # Get file paths from the formats field
                formats = book.get("formats", [])
                if formats:
                    # Formats contains the actual file paths
                    enhanced_book["file_paths"] = [
                        fmt for fmt in formats if os.path.exists(fmt)
                    ]
                else:
                    enhanced_book["file_paths"] = []

                enhanced_books.append(enhanced_book)

            return enhanced_books

        return []

    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        Exception,
    ) as e:
        print(f"Error getting Calibre books: {e}")
        return []


def import_calibre_database_to_beets(
    beets_exe: str,
    dry_run: bool = False,
    skip_existing: bool = True,
    update_metadata: bool = True,
) -> dict:
    """
    Import the entire Calibre database into beets library.

    This creates a complete sync between Calibre and beets where:
    - All Calibre books are imported to beets
    - Beets tracks Calibre-managed files directly
    - Metadata is preserved from Calibre
    - No file duplication occurs

    Args:
        dry_run: Show what would be done without making changes
        skip_existing: Skip books already in beets library
        update_metadata: Update metadata for existing books

    Returns:
        Dictionary with import statistics and results
    """
    print("📚 CALIBRE DATABASE IMPORT TO BEETS")
    print("=" * 60)
    print("This will import your existing Calibre library into beets,")
    print("creating a unified library where beets tracks Calibre's files.")
    print()

    # Check requirements
    calibredb = find_calibredb()
    if not calibredb:
        return {
            "error": "Calibre not found",
            "total_books": 0,
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "updated": 0,
        }

    # Check beets
    if not os.path.exists(beets_exe):
        return {
            "error": "Beets not found",
            "total_books": 0,
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "updated": 0,
        }

    print(f"✓ Found Calibre at: {calibredb}")
    print(f"✓ Found beets at: {beets_exe}")

    # Get all Calibre books
    print("\n🔍 Reading Calibre database...")
    calibre_books = get_all_calibre_books()

    if not calibre_books:
        return {
            "error": "No books found in Calibre database",
            "total_books": 0,
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "updated": 0,
        }

    print(f"📖 Found {len(calibre_books)} books in Calibre database")

    # Get existing books in beets (if skip_existing is True)
    existing_books = set()
    if skip_existing:
        try:
            result = subprocess.run(
                [beets_exe, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )
            existing_paths = [
                os.path.normpath(p.strip())
                for p in result.stdout.strip().split("\n")
                if p.strip()
            ]
            existing_books = set(existing_paths)
            print(
                f"📋 Found {len(existing_books)} existing books in beets library"
            )
        except subprocess.CalledProcessError:
            print("⚠️  Could not query existing beets library")

    # Statistics
    stats = {
        "total_books": len(calibre_books),
        "imported": 0,
        "skipped": 0,
        "failed": 0,
        "updated": 0,
        "errors": [],
    }

    if dry_run:
        print("\n🧪 DRY RUN MODE: No files will be modified")

    print(f"\n🔄 Processing {len(calibre_books)} Calibre books...")
    print("-" * 60)

    for i, book in enumerate(calibre_books, 1):
        title = book.get("title", "Unknown Title")
        authors = book.get("authors", "Unknown Author")
        book_id = book.get("id", "Unknown")
        file_paths = book.get("file_paths", [])

        print(
            f"\n[{i}/{len(calibre_books)}] {title} by {authors} (ID: {book_id})"
        )

        if not file_paths:
            print("  ❌ No accessible file paths found")
            stats["failed"] += 1
            stats["errors"].append(f"No file paths for: {title}")
            continue

        # Process each format
        imported_any = False
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"  ⚠️  File not found: {os.path.basename(file_path)}")
                continue

            normalized_path = os.path.normpath(file_path)

            # Check if already in beets
            if skip_existing and normalized_path in existing_books:
                print(f"  ⏭️  Already in beets: {os.path.basename(file_path)}")
                stats["skipped"] += 1
                continue

            # Import to beets
            if not dry_run:
                try:
                    result = subprocess.run(
                        [beets_exe, "import-ebooks", file_path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    if "Successfully imported" in result.stdout:
                        print(f"  ✅ Imported: {os.path.basename(file_path)}")
                        stats["imported"] += 1
                        imported_any = True
                    else:
                        print(
                            f"  ❌ Import failed: {os.path.basename(file_path)}"
                        )
                        stats["failed"] += 1
                        stats["errors"].append(f"Import failed: {file_path}")

                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Import error: {os.path.basename(file_path)}")
                    stats["failed"] += 1
                    stats["errors"].append(
                        f"Import error for {file_path}: {e}"
                    )
            else:
                # Dry run
                print(f"  🧪 Would import: {os.path.basename(file_path)}")
                stats["imported"] += 1
                imported_any = True

        if not imported_any and file_paths:
            stats["failed"] += 1

    return stats


def reverse_calibre_sync(beets_exe: str) -> dict:
    """
    Reverse sync: Import books from Calibre that aren't in beets.

    This is useful for maintaining lock-step synchronization where
    Calibre is the primary library and beets follows along.

    Returns:
        Dictionary with sync statistics
    """
    print("🔄 REVERSE CALIBRE SYNC")
    print("=" * 50)
    print("Importing books from Calibre that aren't yet in beets...")
    print()

    return import_calibre_database_to_beets(
        beets_exe, dry_run=False, skip_existing=True, update_metadata=False
    )


def bidirectional_calibre_sync(beets_exe: str, dry_run: bool = False) -> dict:
    """
    Bidirectional sync between Calibre and beets libraries.

    This creates complete synchronization where:
    1. Books in Calibre but not in beets are imported to beets
    2. Books in beets but not in Calibre are imported to Calibre
    3. Path updates are synchronized
    4. Both libraries stay in perfect sync

    Args:
        dry_run: Show what would be done without making changes

    Returns:
        Dictionary with comprehensive sync statistics
    """
    print("🔀 BIDIRECTIONAL CALIBRE-BEETS SYNC")
    print("=" * 60)
    print("This creates complete synchronization between your")
    print("Calibre and beets libraries in both directions.")
    print()

    if dry_run:
        print("🧪 DRY RUN MODE: No files will be modified")
        print()

    # Phase 1: Calibre → beets
    print("📥 PHASE 1: Import books from Calibre to beets")
    print("-" * 40)
    calibre_to_beets_stats = import_calibre_database_to_beets(
        beets_exe, dry_run=dry_run, skip_existing=True, update_metadata=False
    )

    print("\n" + "=" * 40)
    print("📊 Phase 1 Results:")
    print(
        f"  📚 Calibre books processed: {calibre_to_beets_stats.get('total_books', 0)}"
    )
    print(
        f"  ✅ Imported to beets: {calibre_to_beets_stats.get('imported', 0)}"
    )
    print(f"  ⏭️  Already in beets: {calibre_to_beets_stats.get('skipped', 0)}")
    print(f"  ❌ Failed imports: {calibre_to_beets_stats.get('failed', 0)}")

    # Phase 2: beets → Calibre
    print("\n📤 PHASE 2: Import books from beets to Calibre")
    print("-" * 40)

    # Get books in beets but not in Calibre
    beets_to_calibre_stats = sync_calibre_with_beets_library()

    if "missing_paths" in beets_to_calibre_stats:
        missing_books = beets_to_calibre_stats["missing_paths"]
        print(f"📖 Found {len(missing_books)} books in beets not in Calibre")

        if missing_books and not dry_run:
            imported_to_calibre = 0
            failed_to_calibre = 0

            for i, book_path in enumerate(missing_books, 1):
                filename = os.path.basename(book_path)
                print(
                    f"[{i}/{len(missing_books)}] Importing to Calibre: {filename}"
                )

                if os.path.exists(book_path):
                    success, message = import_to_calibre(
                        book_path, verbose=False
                    )
                    if success:
                        imported_to_calibre += 1
                        print("  ✅ Imported successfully")
                    else:
                        failed_to_calibre += 1
                        print(f"  ❌ Import failed: {message}")
                else:
                    failed_to_calibre += 1
                    print(f"  ❌ File not found: {book_path}")

        elif dry_run and missing_books:
            print(f"🧪 Would import {len(missing_books)} books to Calibre")
            imported_to_calibre = len(missing_books)
            failed_to_calibre = 0
        else:
            imported_to_calibre = 0
            failed_to_calibre = 0
    else:
        imported_to_calibre = 0
        failed_to_calibre = 0

    # Combined results
    combined_stats = {
        "total_calibre_books": calibre_to_beets_stats.get("total_books", 0),
        "calibre_to_beets_imported": calibre_to_beets_stats.get("imported", 0),
        "calibre_to_beets_skipped": calibre_to_beets_stats.get("skipped", 0),
        "calibre_to_beets_failed": calibre_to_beets_stats.get("failed", 0),
        "beets_to_calibre_imported": imported_to_calibre,
        "beets_to_calibre_failed": failed_to_calibre,
        "sync_successful": (
            calibre_to_beets_stats.get("failed", 0) == 0
            and failed_to_calibre == 0
        ),
        "dry_run": dry_run,
    }

    return combined_stats
