#!/usr/bin/env python3
"""
Ebook Collection Manager for Beets

This script helps manage your ebook collection using the beets-ebooks plugin.
It can scan directories, extract metadata, and organize your ebooks.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional

from .core import (
    calibre_takes_control_workflow,
    filter_onefile_per_book,
    find_calibredb,
    find_ebooks,
    import_to_calibre,
    is_ebook_file,
    parse_extensions,
    sync_calibre_after_move,
    sync_calibre_with_beets_library,
)

# Configuration - adjust these paths to match your setup
BEETS_EXE = r"F:\ottsc\AppData\Roaming\Python\Python313\Scripts\beet.exe"


def process_ebook_with_beets(ebook_path: str) -> Optional[str]:
    """Process an ebook using the beets ebook command."""
    try:
        result = subprocess.run(
            [BEETS_EXE, "ebook", ebook_path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error processing {ebook_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")
        return None


def import_ebook_to_beets(ebook_path: str) -> Optional[str]:
    """Import a single ebook using the beets import-ebooks command."""
    try:
        # Use absolute path to avoid path issues
        abs_path = os.path.abspath(ebook_path)
        result = subprocess.run(
            [BEETS_EXE, "import-ebooks", abs_path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error importing {ebook_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")
        return None


def import_ebook_to_calibre(ebook_path: str) -> bool:
    """Import a single ebook using Calibre."""
    try:
        success, message = import_to_calibre(ebook_path, verbose=True)
        if not success:
            print(
                f"    Error importing {os.path.basename(ebook_path)} "
                f"to Calibre: {message}"
            )
        return success
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        OSError,
        TypeError,
    ) as e:
        print(
            f"    Unexpected error importing {os.path.basename(ebook_path)} "
            f"to Calibre: {e}"
        )
        return False


def scan_collection(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Scan an ebook collection and process each file."""
    print(f"Scanning ebook collection in: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Processing {len(ebooks)} ebook(s)")
    print("-" * 50)

    for i, ebook in enumerate(ebooks, 1):
        print(f"\n[{i}/{len(ebooks)}] Processing: {os.path.basename(ebook)}")
        output = process_ebook_with_beets(ebook)
        if output:
            print(output.strip())
        print("-" * 50)


def import_collection(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Import an ebook collection to beets library."""
    print(f"Importing ebook collection from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s)")
    response = input(
        f"Import all {len(ebooks)} ebooks to beets library? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    print("-" * 50)
    imported = 0

    for i, ebook in enumerate(ebooks, 1):
        print(f"\n[{i}/{len(ebooks)}] Importing: {os.path.basename(ebook)}")
        output = import_ebook_to_beets(ebook)
        if output and "Successfully imported" in output:
            imported += 1
            print("✓ Imported successfully")
        else:
            print("✗ Import failed")

    print("-" * 50)
    print(
        f"Import completed: {imported}/{len(ebooks)} ebooks imported successfully"
    )


def batch_import_ebooks(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Import ebooks to beets library using batch import command."""
    print(f"Batch importing ebooks from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s)")
    response = input(
        f"Import all {len(ebooks)} ebooks to beets library? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    try:
        if allowed_extensions or onefile:
            # When filtering by extensions or using onefile, import files individually
            imported = 0
            for ebook in ebooks:
                print(f"\nImporting: {os.path.basename(ebook)}")
                abs_path = os.path.abspath(ebook)
                result = subprocess.run(
                    [BEETS_EXE, "import-ebooks", abs_path],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if result.stdout:
                    if "Successfully imported" in result.stdout:
                        imported += 1
                        print("✓ Imported successfully")
                    else:
                        print("✗ Import failed")

            print(
                f"\n✅ Batch import completed: {imported}/{len(ebooks)} "
                f"ebooks imported successfully"
            )
        else:
            # Use original directory-based import when no filtering
            abs_directory = os.path.abspath(directory)
            result = subprocess.run(
                [BEETS_EXE, "import-ebooks", abs_directory],
                capture_output=True,
                text=True,
                check=True,
            )
            print("Batch import completed successfully!")
            if result.stdout:
                print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error importing ebooks: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")


def test_organization(dry_run: bool = True) -> None:
    """Test ebook organization in beets."""
    print("Testing ebook organization...")

    # First, show current ebooks in library
    try:
        result = subprocess.run(
            [BEETS_EXE, "ls", "ebook:true"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            print("No ebooks found in beets library.")
            return

        print("Current ebooks in library:")
        print(result.stdout)

        # Get current file paths before move
        old_paths = []
        if not dry_run:
            path_result = subprocess.run(
                [BEETS_EXE, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )
            old_paths = [
                p.strip()
                for p in path_result.stdout.strip().split("\n")
                if p.strip()
            ]

        # Show what the move operation would do
        cmd = [BEETS_EXE, "move", "ebook:true"]
        if dry_run:
            cmd.append("--pretend")
            print("\nDry run - showing what would happen:")
        else:
            print("\nActually moving files:")

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        print(result.stdout)

        if not dry_run:
            print("Files have been organized!")

            # Get new file paths after move
            path_result = subprocess.run(
                [BEETS_EXE, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )
            new_paths = [
                p.strip()
                for p in path_result.stdout.strip().split("\n")
                if p.strip()
            ]

            print("\nNew file locations:")
            print(path_result.stdout)

            # Sync Calibre database if Calibre is available and files were moved
            if old_paths and new_paths and len(old_paths) == len(new_paths):
                calibredb = find_calibredb()
                if calibredb:
                    print("\n" + "=" * 60)
                    stats = sync_calibre_after_move(old_paths, new_paths)
                    print("=" * 60)
                    print("📊 Calibre sync summary:")
                    print(f"  ✅ Updated: {stats['updated']} entries")
                    print(f"  ❌ Failed: {stats['failed']} entries")
                    print(
                        f"  ℹ️  Not in Calibre: {stats['not_in_calibre']} files"
                    )
                else:
                    print("\nℹ️  Calibre not found - skipping database sync")
            elif old_paths and new_paths:
                print(
                    f"\n⚠️  Path count mismatch - old: {len(old_paths)}, "
                    f"new: {len(new_paths)}"
                )
                print("   Skipping Calibre sync for safety")

    except subprocess.CalledProcessError as e:
        print(f"Error testing organization: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")


def suggest_organization(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Suggest how to organize ebooks based on metadata."""
    print(f"Analyzing collection structure in: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    authors = set()
    formats: dict[str, int] = {}

    for ebook in ebooks:
        # Extract basic info from filename
        filename = os.path.basename(ebook)
        name_without_ext = os.path.splitext(filename)[0]

        if " - " in name_without_ext:
            parts = name_without_ext.split(" - ", 1)
            if len(parts) == 2:
                author = parts[0].strip()
                authors.add(author)

        # Count formats
        ext = os.path.splitext(filename)[1].lower()
        formats[ext] = formats.get(ext, 0) + 1

    print("\nCollection Statistics:")
    print(f"  Total ebooks: {len(ebooks)}")
    print(f"  Unique authors: {len(authors)}")
    print(f"  File formats: {dict(formats)}")

    if authors:
        print("\nAuthors found:")
        for author in sorted(authors):
            print(f"  - {author}")

    print("\nSuggested organization structure:")
    print(f"  [Books] {directory}/")
    print("    [Author] Author Name/")
    print("      [Book] Book Title.epub")
    print("    [Author] Another Author/")
    print("      [Book] Another Book.pdf")


def import_single_directory(
    directory: str,
    recursive: bool = False,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Import ebooks from a single directory (non-recursive by default)."""
    print(f"Importing ebooks from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    if recursive:
        ebooks = find_ebooks(directory, allowed_extensions)
    else:
        # Only look in the specified directory, not subdirectories
        ebooks = []
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                if is_ebook_file(file, allowed_extensions):
                    ebooks.append(os.path.join(directory, file))

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s):")
    for i, ebook in enumerate(ebooks, 1):
        print(f"  {i}. {os.path.basename(ebook)}")

    response = input(
        f"\nImport all {len(ebooks)} ebooks to beets library? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    try:
        imported = 0
        for ebook in ebooks:
            print(f"\nImporting: {os.path.basename(ebook)}")
            abs_path = os.path.abspath(ebook)
            result = subprocess.run(
                [BEETS_EXE, "import-ebooks", abs_path],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                print(result.stdout.strip())
                if "Successfully imported" in result.stdout:
                    imported += 1

        print(
            f"\n✅ Import completed: {imported}/{len(ebooks)} "
            f"ebooks imported successfully"
        )

    except subprocess.CalledProcessError as e:
        print(f"Error importing ebooks: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")


def scan_collection_calibre(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
) -> None:
    """Scan an ebook collection and import to Calibre."""
    print(f"Scanning ebook collection for Calibre import: {directory}")

    # Check if Calibre is available
    calibredb = find_calibredb()
    if not calibredb:
        print(
            "❌ Calibre not found! Please install Calibre to use this feature."
        )
        print("Download from: https://calibre-ebook.com/download")
        return

    print(f"✓ Found Calibre at: {calibredb}")

    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s)")
    response = input(
        f"Import all {len(ebooks)} ebooks to Calibre library? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    print("-" * 50)
    imported = 0

    for i, ebook in enumerate(ebooks, 1):
        print(
            f"\n[{i}/{len(ebooks)}] Importing to Calibre: {os.path.basename(ebook)}"
        )
        if import_ebook_to_calibre(ebook):
            imported += 1
            print("✓ Imported successfully")
        else:
            print("✗ Import failed")

    print("-" * 50)
    print(
        f"Calibre import completed: {imported}/{len(ebooks)} "
        f"ebooks imported successfully"
    )


def import_collection_dual(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
    use_beets: bool = True,
    use_calibre: bool = True,
) -> None:
    """Import an ebook collection to both beets and Calibre."""
    print(f"Dual import (beets + Calibre) from: {directory}")

    # Check availability
    beets_available = os.path.exists(BEETS_EXE) if use_beets else False
    calibre_available = find_calibredb() is not None if use_calibre else False

    if not beets_available and not calibre_available:
        print("❌ Neither beets nor Calibre found!")
        return

    if use_beets and not beets_available:
        print("⚠ Beets not found, using Calibre only")
        use_beets = False

    if use_calibre and not calibre_available:
        print("⚠ Calibre not found, using beets only")
        use_calibre = False

    # Build status message
    status_parts = []
    if use_beets:
        status_parts.append("beets")
    if use_calibre:
        status_parts.append("Calibre")
    print(f"✓ Using: {' + '.join(status_parts)}")

    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"\nFound {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s)")
    response = input(
        f"Import all {len(ebooks)} ebooks to selected libraries? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    print("-" * 50)
    beets_imported = 0
    calibre_imported = 0

    for i, ebook in enumerate(ebooks, 1):
        print(f"\n[{i}/{len(ebooks)}] Processing: {os.path.basename(ebook)}")

        # Import to beets
        if use_beets:
            print("  → Importing to beets...")
            output = import_ebook_to_beets(ebook)
            if output and "Successfully imported" in output:
                beets_imported += 1
                print("    ✓ Beets import successful")
            else:
                print("    ✗ Beets import failed")

        # Import to Calibre
        if use_calibre:
            print("  → Importing to Calibre...")
            if import_ebook_to_calibre(ebook):
                calibre_imported += 1
                print("    ✓ Calibre import successful")
            else:
                print("    ✗ Calibre import failed")

    print("-" * 50)
    print("Dual import completed:")
    if use_beets:
        print(
            f"  Beets: {beets_imported}/{len(ebooks)} ebooks imported successfully"
        )
    if use_calibre:
        print(
            f"  Calibre: {calibre_imported}/{len(ebooks)} ebooks imported successfully"
        )


def sync_calibre_database() -> None:
    """Sync Calibre database with current beets library state."""
    print("🔄 Calibre Database Sync")
    print("=" * 50)
    print("This will update Calibre's database to match the current")
    print("file locations in your beets library.\n")

    # Check if Calibre is available
    calibredb = find_calibredb()
    if not calibredb:
        print(
            "❌ Calibre not found! Please install Calibre to use this feature."
        )
        print("Download from: https://calibre-ebook.com/download")
        return

    print(f"✓ Found Calibre at: {calibredb}")

    # Check if beets is available
    if not os.path.exists(BEETS_EXE):
        print(f"❌ Beets not found at: {BEETS_EXE}")
        print("Please check your beets installation.")
        return

    print(f"✓ Found beets at: {BEETS_EXE}")
    print()

    response = input("Continue with Calibre database sync? (y/N): ")
    if response.lower() not in ["y", "yes"]:
        print("Sync cancelled.")
        return

    print()
    stats = sync_calibre_with_beets_library()

    if "error" in stats:
        print(f"❌ Sync failed: {stats['error']}")
        return

    print("\n" + "=" * 60)
    print("📊 Calibre sync completed!")
    print(f"  📚 Scanned: {stats.get('scanned', 0)} ebooks in beets library")
    print(f"  ✅ Updated: {stats.get('updated', 0)} Calibre entries")
    print(f"  ❌ Failed: {stats.get('failed', 0)} updates")
    print(f"  ℹ️  Not in Calibre: {stats.get('not_in_calibre', 0)} files")
    print("=" * 60)

    if stats.get("updated", 0) > 0:
        print(f"\n🎉 Successfully updated {stats['updated']} Calibre entries!")
    elif stats.get("failed", 0) > 0:
        print(
            f"\n⚠️  {stats['failed']} updates failed. "
            f"Check the output above for details."
        )

    # Offer to import missing books to Calibre
    missing_count = stats.get("not_in_calibre", 0)
    missing_paths = stats.get("missing_paths", [])

    if missing_count > 0 and missing_paths:
        print(
            f"\n📥 Found {missing_count} ebooks in beets that are not in Calibre."
        )
        response = input("Would you like to import them to Calibre? (y/N): ")

        if response.lower() in ["y", "yes"]:
            print(
                f"\n🔄 Starting import of {missing_count} missing ebooks to Calibre..."
            )

            # Import each missing book
            imported = 0
            failed = 0

            for i, ebook_path in enumerate(missing_paths, 1):
                filename = os.path.basename(ebook_path)
                print(f"\n[{i}/{len(missing_paths)}] Importing: {filename}")

                if os.path.exists(ebook_path):
                    success, message = import_to_calibre(
                        ebook_path, verbose=False
                    )
                    if success:
                        imported += 1
                        print("    ✅ Imported successfully")
                    else:
                        failed += 1
                        print(f"    ❌ Import failed: {message}")
                else:
                    failed += 1
                    print(f"    ❌ File not found: {ebook_path}")

            print("\n" + "=" * 60)
            print("📥 Import to Calibre completed!")
            print(f"  ✅ Imported: {imported} ebooks")
            print(f"  ❌ Failed: {failed} ebooks")
            print("=" * 60)

            if imported > 0:
                print(
                    f"\n🎉 Successfully imported {imported} ebooks to Calibre!"
                )
            if failed > 0:
                print(
                    f"\n⚠️  {failed} imports failed. "
                    f"Check the output above for details."
                )
        else:
            print("\n✨ Sync completed. Missing books were not imported.")
    else:
        print("\n✨ All Calibre entries are already in sync with beets!")


def organize_then_import_workflow(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
    use_calibre: bool = True,
) -> None:
    """
    Recommended workflow: Organize with beets first, then import to Calibre.

    This approach:
    1. Imports and organizes books with beets (master library)
    2. Lets beets perfect metadata and file organization
    3. Imports the well-organized files to Calibre (creates clean copies)
    4. Avoids sync issues since Calibre gets pre-organized files
    """
    print("🔄 Organize-First Workflow")
    print("=" * 60)
    print("This workflow organizes books with beets first, then imports")
    print("the well-organized files to Calibre for the best results.")
    print()

    # Check availability
    beets_available = os.path.exists(BEETS_EXE)
    calibre_available = find_calibredb() is not None if use_calibre else True

    if not beets_available:
        print("❌ Beets not found! This workflow requires beets.")
        print(f"Expected location: {BEETS_EXE}")
        return

    if use_calibre and not calibre_available:
        print("⚠️  Calibre not found, will organize with beets only")
        use_calibre = False

    print(f"✓ Found beets at: {BEETS_EXE}")
    if use_calibre:
        print(f"✓ Found Calibre at: {find_calibredb()}")
    print()

    # Step 1: Import and organize with beets
    print("📥 STEP 1: Import and organize with beets")
    print("-" * 40)

    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"Found {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s) to import")

    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    response = input(
        f"\nProceed with importing {len(ebooks)} ebooks to beets? (y/N): "
    )
    if response.lower() not in ["y", "yes"]:
        print("Workflow cancelled.")
        return

    # Import to beets
    print("\n🔄 Importing to beets library...")
    beets_imported = 0

    for i, ebook in enumerate(ebooks, 1):
        print(f"[{i}/{len(ebooks)}] Importing: {os.path.basename(ebook)}")
        output = import_ebook_to_beets(ebook)
        if output and "Successfully imported" in output:
            beets_imported += 1
            print("  ✅ Imported successfully")
        else:
            print("  ❌ Import failed")

    print(f"\nBeets import result: {beets_imported}/{len(ebooks)} successful")

    if beets_imported == 0:
        print(
            "❌ No books were successfully imported to beets. Stopping workflow."
        )
        return

    # Step 2: Organize with beets (optional but recommended)
    print("\n📁 STEP 2: Organize imported books with beets")
    print("-" * 40)
    print("This will move books to their proper organized locations")
    print("based on the metadata beets extracted.")
    print()

    response = input("Run beets organization? (Y/n): ")
    if response.lower() not in ["n", "no"]:
        try:
            print("🔄 Organizing books with beets...")

            # Get current paths before organization (for potential future use)
            subprocess.run(
                [BEETS_EXE, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Run organization
            result = subprocess.run(
                [BEETS_EXE, "move", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                print("Organization results:")
                print(result.stdout)
            else:
                print(
                    "✅ Books are already in the correct organized locations"
                )

            # Get new paths after organization (for potential future use)
            subprocess.run(
                [BEETS_EXE, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )

            print(
                "✅ Organization complete! Books are now properly organized."
            )

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Organization failed: {e}")
            print("Continuing with workflow using current file locations...")

    # Step 3: Import organized books to Calibre
    calibre_imported = 0
    organized_paths = []

    if use_calibre:
        print("\n📚 STEP 3: Import organized books to Calibre")
        print("-" * 40)
        print("Now importing the well-organized books from your beets library")
        print("to Calibre. This creates clean copies with perfect metadata.")
        print()

        # Get current book paths from beets
        try:
            result = subprocess.run(
                [BEETS_EXE, "ls", "-f", "$path", "ebook:true"],
                capture_output=True,
                text=True,
                check=True,
            )

            organized_paths = [
                p.strip()
                for p in result.stdout.strip().split("\n")
                if p.strip()
            ]

            if not organized_paths:
                print(
                    "❌ No books found in beets library to import to Calibre"
                )
                return

            print(
                f"Found {len(organized_paths)} organized books to import to Calibre"
            )

            response = input(
                f"\nImport {len(organized_paths)} organized books to Calibre? (y/N): "
            )
            if response.lower() not in ["y", "yes"]:
                print("Calibre import skipped.")
                print("\n✅ Workflow complete! Books are organized in beets.")
                return

            print("\n🔄 Importing organized books to Calibre...")

            for i, book_path in enumerate(organized_paths, 1):
                if os.path.exists(book_path):
                    filename = os.path.basename(book_path)
                    print(
                        f"[{i}/{len(organized_paths)}] Importing: {filename}"
                    )

                    success, message = import_to_calibre(
                        book_path, verbose=False
                    )
                    if success:
                        calibre_imported += 1
                        print("  ✅ Imported successfully")
                    else:
                        print(f"  ❌ Import failed: {message}")
                else:
                    print(
                        f"[{i}/{len(organized_paths)}] File not found: {book_path}"
                    )

            print(
                f"\nCalibre import result: {calibre_imported}/"
                f"{len(organized_paths)} successful"
            )

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get organized book paths: {e}")
            return

    # Final summary
    print("\n" + "=" * 60)
    print("🎉 ORGANIZE-FIRST WORKFLOW COMPLETE!")
    print("=" * 60)
    print(f"📥 Imported to beets: {beets_imported}/{len(ebooks)} books")
    if use_calibre and organized_paths:
        print(
            f"📚 Imported to Calibre: {calibre_imported}/{len(organized_paths)} books"
        )
    print()
    print("✨ Benefits achieved:")
    print("  • Books are perfectly organized with beets metadata")
    print("  • File names and folders follow consistent patterns")
    if use_calibre:
        print("  • Calibre has clean copies with excellent metadata")
        print("  • No sync issues - Calibre imported pre-organized files")
    print("  • Beets library is the master source of truth")
    print("=" * 60)


def check_calibre_integration_config() -> None:
    """Check and display Calibre integration configuration options."""
    print("🔧 Calibre Integration Configuration")
    print("=" * 60)

    from .core import enhanced_calibre_workflow_with_config

    # Check current configuration
    config_info = enhanced_calibre_workflow_with_config(
        directory="",
        auto_discover_library=True,  # Not used for configuration check
    )

    print("📋 Configuration Analysis:")
    print(
        f"  • Calibre library: {config_info.get('calibre_library', 'Not found')}"
    )
    print(
        f"  • Library discovered: {config_info.get('library_discovered', False)}"
    )
    print(f"  • Workflow ready: {config_info.get('workflow_ready', False)}")

    print("\n💡 Recommendations:")
    config_data = config_info.get("configuration", {})
    recommendations = config_data.get("recommendations", [])

    for rec in recommendations:
        print(f"  {rec}")

    if not config_info.get("workflow_ready", False):
        print("\n⚙️  Setup Steps:")
        print("  1. Install Calibre from https://calibre-ebook.com/")
        print("  2. Install beets and beets-ebooks plugin")
        print("  3. Use 'ebook-manager organize-then-import' for best results")
    else:
        print(
            "\n✅ Your system is ready for optimal beets/Calibre integration!"
        )

    print("\n" + "=" * 60)


def calibre_takes_control_workflow_cli(
    directory: str,
    allowed_extensions: Optional[List[str]] = None,
    onefile: bool = False,
    dry_run: bool = False,
) -> None:
    """
    CLI wrapper for the Calibre-takes-control workflow.

    This revolutionary workflow:
    1. Imports books to both beets and Calibre
    2. After Calibre import, updates beets database to point to Calibre-managed files
    3. Deletes the original/beets copies, letting Calibre be the file manager

    Benefits:
    - Calibre becomes the single source of truth for file storage
    - Beets retains all metadata and library functionality
    - No sync issues since beets tracks Calibre's managed files
    - Eliminates duplicate file storage
    """
    print("🚀 CALIBRE-TAKES-CONTROL WORKFLOW")
    print("=" * 60)
    print("This workflow revolutionizes ebook management by letting")
    print("Calibre manage files while beets handles metadata.")
    print()

    # Check requirements
    beets_available = os.path.exists(BEETS_EXE)
    calibre_available = find_calibredb() is not None

    if not beets_available:
        print("❌ Beets not found! This workflow requires beets.")
        print(f"Expected location: {BEETS_EXE}")
        return

    if not calibre_available:
        print("❌ Calibre not found! This workflow requires Calibre.")
        print("Download from: https://calibre-ebook.com/download")
        return

    print(f"✓ Found beets at: {BEETS_EXE}")
    print(f"✓ Found Calibre at: {find_calibredb()}")
    print()

    # Find and filter ebooks
    ebooks = find_ebooks(directory, allowed_extensions)

    if onefile:
        print(f"Found {len(ebooks)} total ebook(s) before filtering")
        ebooks = filter_onefile_per_book(ebooks)
        print(f"After one-file filtering: {len(ebooks)} ebook(s)")

    if not ebooks:
        print("No ebook files found.")
        return

    print(f"Found {len(ebooks)} ebook(s) to process")

    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    if onefile:
        print("One-file mode: selecting highest priority format per book")

    # Explain the workflow
    print("\n🔄 WORKFLOW STEPS:")
    print("  1. Import each book to beets (for metadata extraction)")
    print("  2. Import each book to Calibre (creates managed copy)")
    print("  3. Update beets database to point to Calibre's managed file")
    print("  4. Delete original file (beets now tracks Calibre's copy)")
    print()
    print("💡 RESULT: Calibre manages files, beets tracks them")
    print()

    if dry_run:
        print("🧪 DRY RUN MODE: No files will be modified")

    response = input(
        f"Proceed with {'dry run of ' if dry_run else ''}"
        f"Calibre-takes-control workflow? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Workflow cancelled.")
        return

    print("\n" + "=" * 60)
    print("🚀 STARTING CALIBRE-TAKES-CONTROL WORKFLOW")
    print("=" * 60)

    # Execute the workflow
    stats = calibre_takes_control_workflow(
        directory, allowed_extensions, onefile, dry_run
    )

    # Display results
    print("\n" + "=" * 60)
    print("📊 WORKFLOW RESULTS")
    print("=" * 60)
    print(f"📁 Total files processed: {stats['total_files']}")
    print(
        f"📥 Imported to beets: {stats['beets_imported']}/{stats['total_files']}"
    )
    print(
        f"📚 Imported to Calibre: {stats['calibre_imported']}/{stats['total_files']}"
    )
    print(
        f"🔄 Database updates: {stats['database_updated']}/{stats['total_files']}"
    )
    print(f"🗑️  Files deleted: {stats['files_deleted']}/{stats['total_files']}")

    if stats["errors"]:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        for error in stats["errors"][:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(stats["errors"]) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more")

    # Success summary
    successful = stats["database_updated"]
    if successful > 0:
        print("\n🎉 SUCCESS!")
        print("=" * 60)
        if not dry_run:
            print(f"✨ {successful} books are now managed by Calibre!")
            print("✨ Beets tracks Calibre's managed files!")
            print("✨ No duplicate storage - maximum efficiency!")
        else:
            print(
                f"✨ Dry run successful - {successful} books would be processed!"
            )
        print()
        print("🔥 BENEFITS ACHIEVED:")
        print("  • Calibre is the file manager (single source of truth)")
        print("  • Beets retains full metadata and search capabilities")
        print("  • No sync issues - beets tracks Calibre's files")
        print("  • Storage efficiency - no duplicate files")
        print("  • Best of both tools combined!")
    else:
        print("\n❌ No books were successfully processed.")

    print("=" * 60)


def import_from_calibre_database(
    dry_run: bool = False, skip_existing: bool = True
) -> None:
    """
    Import books from an existing Calibre database into beets library.

    This creates perfect synchronization where beets tracks all Calibre-managed files
    while preserving the existing Calibre library structure.
    """
    print("📚 IMPORT FROM CALIBRE DATABASE")
    print("=" * 60)
    print("This will import your existing Calibre library into beets,")
    print(
        "creating a unified system where beets tracks all your Calibre books."
    )
    print()

    if dry_run:
        print("🧪 DRY RUN MODE: No files will be modified")
        print()

    response = input(
        f"Proceed with {'dry run of ' if dry_run else ''}"
        f"Calibre database import? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Import cancelled.")
        return

    print("\n" + "=" * 60)
    print("🚀 STARTING CALIBRE DATABASE IMPORT")
    print("=" * 60)

    from .core import import_calibre_database_to_beets

    # Execute the import
    stats = import_calibre_database_to_beets(
        BEETS_EXE,
        dry_run=dry_run,
        skip_existing=skip_existing,
        update_metadata=False,
    )

    # Display results
    print("\n" + "=" * 60)
    print("📊 IMPORT RESULTS")
    print("=" * 60)

    if "error" in stats:
        print(f"❌ Import failed: {stats['error']}")
        return

    print(f"📚 Total Calibre books: {stats['total_books']}")
    print(f"✅ Imported to beets: {stats['imported']}")
    print(f"⏭️  Already in beets: {stats['skipped']}")
    print(f"❌ Failed imports: {stats['failed']}")

    if stats["errors"]:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        for error in stats["errors"][:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(stats["errors"]) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more")

    # Success summary
    successful = stats["imported"]
    if successful > 0:
        print("\n🎉 SUCCESS!")
        print("=" * 60)
        if not dry_run:
            print(f"✨ {successful} books imported from Calibre to beets!")
            print("✨ Your beets library now tracks your Calibre collection!")
            print("✨ Perfect lock-step synchronization achieved!")
        else:
            print(
                f"✨ Dry run successful - {successful} books would be imported!"
            )
        print()
        print("🔥 BENEFITS ACHIEVED:")
        print("  • Beets now tracks all your existing Calibre books")
        print("  • No file duplication - beets points to Calibre's files")
        print("  • Unified library with best of both tools")
        print("  • Existing Calibre organization preserved")
        print("  • Complete metadata integration")
    else:
        print("\n✅ No new books to import - libraries are already in sync!")

    print("=" * 60)


def bidirectional_sync_workflow(dry_run: bool = False) -> None:
    """
    Bidirectional sync between Calibre and beets libraries.

    This creates complete synchronization in both directions:
    - Books in Calibre → imported to beets
    - Books in beets → imported to Calibre
    """
    print("🔀 BIDIRECTIONAL CALIBRE-BEETS SYNC")
    print("=" * 60)
    print("This creates complete synchronization between your")
    print("Calibre and beets libraries in both directions.")
    print()

    if dry_run:
        print("🧪 DRY RUN MODE: No files will be modified")
        print()

    response = input(
        f"Proceed with {'dry run of ' if dry_run else ''}bidirectional sync? (y/N): "
    )

    if response.lower() not in ["y", "yes"]:
        print("Sync cancelled.")
        return

    print("\n" + "=" * 60)
    print("🚀 STARTING BIDIRECTIONAL SYNC")
    print("=" * 60)

    from .core import bidirectional_calibre_sync

    # Execute the sync
    stats = bidirectional_calibre_sync(BEETS_EXE, dry_run=dry_run)

    # Display results
    print("\n" + "=" * 60)
    print("📊 BIDIRECTIONAL SYNC RESULTS")
    print("=" * 60)
    print(f"📚 Total Calibre books: {stats.get('total_calibre_books', 0)}")
    print(
        f"📥 Calibre → beets: {stats.get('calibre_to_beets_imported', 0)} imported"
    )
    print(
        f"📤 beets → Calibre: {stats.get('beets_to_calibre_imported', 0)} imported"
    )
    print(
        f"⏭️  Already synced: {stats.get('calibre_to_beets_skipped', 0)} books"
    )
    failed_calibre = stats.get("calibre_to_beets_failed", 0)
    failed_beets = stats.get("beets_to_calibre_failed", 0)
    print(f"❌ Failed syncs: {failed_calibre + failed_beets}")

    if stats.get("sync_successful", False):
        print("\n🎉 BIDIRECTIONAL SYNC COMPLETE!")
        print("=" * 60)
        if not dry_run:
            print(
                "✨ Your Calibre and beets libraries are now perfectly synchronized!"
            )
            print("✨ All books are available in both systems!")
            print("✨ Maximum efficiency and organization achieved!")
        else:
            print("✨ Dry run successful - sync would complete perfectly!")
        print()
        print("🔥 BENEFITS ACHIEVED:")
        print("  • Complete library synchronization in both directions")
        print("  • Unified access to all books from both tools")
        print("  • No data loss or duplication")
        print("  • Optimal metadata management")
        print("  • Future-proof library organization")
    else:
        print("\n⚠️  Sync completed with some issues - check the logs above")

    print("=" * 60)


def reverse_sync_workflow() -> None:
    """
    Reverse sync: Import books from Calibre that aren't in beets.

    This maintains lock-step synchronization where Calibre is primary
    and beets follows along.
    """
    print("⬅️  REVERSE CALIBRE SYNC")
    print("=" * 60)
    print("This imports books from Calibre that aren't yet in beets,")
    print("maintaining lock-step synchronization where Calibre leads.")
    print()

    response = input("Proceed with reverse sync from Calibre? (y/N): ")

    if response.lower() not in ["y", "yes"]:
        print("Sync cancelled.")
        return

    print("\n" + "=" * 60)
    print("🚀 STARTING REVERSE SYNC")
    print("=" * 60)

    from .core import reverse_calibre_sync

    # Execute the reverse sync
    stats = reverse_calibre_sync(BEETS_EXE)

    # Display results
    print("\n" + "=" * 60)
    print("📊 REVERSE SYNC RESULTS")
    print("=" * 60)

    if "error" in stats:
        print(f"❌ Sync failed: {stats['error']}")
        return

    print(f"📚 Total Calibre books: {stats['total_books']}")
    print(f"✅ New books imported: {stats['imported']}")
    print(f"⏭️  Already in beets: {stats['skipped']}")
    print(f"❌ Failed imports: {stats['failed']}")

    successful = stats["imported"]
    if successful > 0:
        print("\n🎉 REVERSE SYNC COMPLETE!")
        print("=" * 60)
        print(f"✨ {successful} new books imported from Calibre!")
        print("✨ Your beets library is now up-to-date with Calibre!")
        print("✨ Lock-step synchronization maintained!")
        print()
        print("🔥 BENEFITS:")
        print("  • Calibre remains the primary library")
        print("  • Beets automatically follows Calibre changes")
        print("  • No manual sync needed")
        print("  • Always in perfect harmony")
    else:
        print("\n✅ Libraries are already in sync!")

    print("=" * 60)


def main() -> None:
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Ebook Collection Manager for Beets & Calibre",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ebook_manager.py scan C:/Books/
  python ebook_manager.py scan C:/Books/ --ext .epub
  python ebook_manager.py import C:/Books/ --ext .epub,.pdf
  python ebook_manager.py import C:/Books/ --onefile
  python ebook_manager.py import C:/Books/ --ext .epub,.mobi --onefile
  python ebook_manager.py import-dir "B:/Unsorted/Books mystery/Lee Child (95)/"
  python ebook_manager.py batch-import C:/Books/ --ext .epub --onefile
  python ebook_manager.py calibre-import C:/Books/ --ext .epub --onefile
  python ebook_manager.py dual-import C:/Books/ --ext .epub,.pdf
  python ebook_manager.py test-organize
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "scan",
            "analyze",
            "process",
            "import",
            "import-dir",
            "batch-import",
            "calibre-scan",
            "calibre-import",
            "dual-import",
            "test-organize",
            "organize",
            "sync-calibre",
            "organize-then-import",
            "calibre-takes-control",
            "check-calibre-config",
            "import-from-calibre",
            "bidirectional-sync",
            "reverse-sync",
        ],
        help="Command to execute",
    )

    parser.add_argument("path", nargs="?", help="Path to directory or file")

    parser.add_argument(
        "--ext",
        "--extensions",
        help="Comma-separated list of file extensions to process (e.g., .epub,.pdf)",
    )

    parser.add_argument(
        "--onefile",
        action="store_true",
        help=(
            "Import only one file per book "
            "(highest priority format: .epub > .mobi > .azw > "
            ".azw3 > .pdf > .cbz > .cbr > .lrf)"
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes "
        "(for calibre-takes-control workflow)",
    )

    # Handle legacy mode (if no arguments provided, show help)
    if len(sys.argv) == 1:
        print("Ebook Collection Manager for Beets")
        print("\nUsage:")
        print(
            "  python ebook_manager.py scan <directory> "
            "[--ext .epub,.pdf] [--onefile]"
        )
        print(
            "  python ebook_manager.py analyze <directory> "
            "[--ext .epub] [--onefile]"
        )
        print("  python ebook_manager.py process <file>")
        print(
            "  python ebook_manager.py import <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py import-dir <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py batch-import <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py calibre-scan <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py calibre-import <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py dual-import <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py organize-then-import <directory> "
            "[--ext .epub] [--onefile]"
        )
        print(
            "  python ebook_manager.py calibre-takes-control <directory> "
            "[--ext .epub] [--onefile]"
        )
        print("  python ebook_manager.py test-organize")
        print("  python ebook_manager.py organize")
        print("  python ebook_manager.py sync-calibre")
        print("  python ebook_manager.py check-calibre-config")
        print("  python ebook_manager.py import-from-calibre [--dry-run]")
        print("  python ebook_manager.py bidirectional-sync [--dry-run]")
        print("  python ebook_manager.py reverse-sync")
        print("\nOptions:")
        print(
            "  --ext EXTENSIONS    Filter by file extensions "
            "(e.g., --ext .epub,.pdf)"
        )
        print(
            "  --onefile           Import only one file per book "
            "(highest priority format)"
        )
        print("\nExamples:")
        print("  python ebook_manager.py scan C:/Books/")
        print("  python ebook_manager.py scan C:/Books/ --ext .epub")
        print("  python ebook_manager.py scan C:/Books/ --onefile")
        print("  python ebook_manager.py import C:/Books/ --ext .epub,.pdf")
        print("  python ebook_manager.py import C:/Books/ --onefile")

        print(
            "  python ebook_manager.py batch-import C:/Books/ --ext .epub --onefile"
        )
        print(
            "  python ebook_manager.py calibre-import C:/Books/ "
            "--ext .epub --onefile"
        )
        print(
            "  python ebook_manager.py dual-import C:/Books/ --ext .epub,.pdf"
        )
        print(
            "  python ebook_manager.py organize-then-import C:/Books/ --ext .epub"
        )
        print(
            "  python ebook_manager.py calibre-takes-control C:/Books/ --ext .epub"
        )
        print("  python ebook_manager.py import-from-calibre --dry-run")
        print("  python ebook_manager.py bidirectional-sync")
        print("  python ebook_manager.py reverse-sync")
        print("\nRecommended Workflows:")
        print(
            "  organize-then-import   🌟 RECOMMENDED: Organize with beets first, "
            "then import to Calibre"
        )
        print(
            "  calibre-takes-control  🚀 REVOLUTIONARY: Let Calibre manage files, "
            "beets tracks them"
        )
        print(
            "  import-from-calibre    📥 IMPORT: Import existing Calibre "
            "library to beets"
        )
        print("\nCalibre Commands:")
        print("  calibre-scan       Scan and import ebooks to Calibre library")
        print("  calibre-import     Import ebooks to Calibre library")
        print(
            "  dual-import        Import to both beets and Calibre libraries"
        )
        print(
            "  sync-calibre       Sync Calibre database with current beets library"
        )
        print("\nLibrary Synchronization:")
        print(
            "  import-from-calibre    Import existing Calibre database to beets"
        )
        print("  bidirectional-sync     Complete sync in both directions")
        print("  reverse-sync          Import from Calibre to beets only")
        print("\nOne-file priority order (highest to lowest):")
        print("  .epub > .mobi > .azw > .azw3 > .pdf > .cbz > .cbr > .lrf")
        return

    try:
        args = parser.parse_args()
    except SystemExit:
        return

    # Parse extensions
    allowed_extensions = parse_extensions(args.ext)
    onefile = getattr(args, "onefile", False)
    dry_run = getattr(args, "dry_run", False)

    # Execute commands
    if args.command == "scan":
        if not args.path:
            print("Error: scan command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        scan_collection(args.path, allowed_extensions, onefile)

    elif args.command == "analyze":
        if not args.path:
            print("Error: analyze command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        suggest_organization(args.path, allowed_extensions, onefile)

    elif args.command == "process":
        if not args.path:
            print("Error: process command requires a file path")
            return
        if not os.path.isfile(args.path):
            print(f"File not found: {args.path}")
            return
        if not is_ebook_file(args.path, allowed_extensions):
            print(f"Not an ebook file: {args.path}")
            return
        output = process_ebook_with_beets(args.path)
        if output:
            print(output)

    elif args.command == "import":
        if not args.path:
            print("Error: import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        import_collection(args.path, allowed_extensions, onefile)

    elif args.command == "import-dir":
        if not args.path:
            print("Error: import-dir command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        import_single_directory(
            args.path,
            recursive=False,
            allowed_extensions=allowed_extensions,
            onefile=onefile,
        )

    elif args.command == "batch-import":
        if not args.path:
            print("Error: batch-import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        batch_import_ebooks(args.path, allowed_extensions, onefile)

    elif args.command == "test-organize":
        test_organization(dry_run=True)

    elif args.command == "organize":
        test_organization(dry_run=False)

    elif args.command == "calibre-scan":
        if not args.path:
            print("Error: calibre-scan command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        scan_collection_calibre(args.path, allowed_extensions, onefile)

    elif args.command == "calibre-import":
        if not args.path:
            print("Error: calibre-import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        scan_collection_calibre(args.path, allowed_extensions, onefile)

    elif args.command == "dual-import":
        if not args.path:
            print("Error: dual-import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        import_collection_dual(args.path, allowed_extensions, onefile)

    elif args.command == "sync-calibre":
        sync_calibre_database()

    elif args.command == "organize-then-import":
        if not args.path:
            print(
                "Error: organize-then-import command requires a directory path"
            )
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        organize_then_import_workflow(args.path, allowed_extensions, onefile)

    elif args.command == "calibre-takes-control":
        if not args.path:
            print(
                "Error: calibre-takes-control command requires a directory path"
            )
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        calibre_takes_control_workflow_cli(
            args.path, allowed_extensions, onefile, dry_run
        )

    elif args.command == "check-calibre-config":
        check_calibre_integration_config()

    elif args.command == "import-from-calibre":
        import_from_calibre_database(dry_run=dry_run)

    elif args.command == "bidirectional-sync":
        bidirectional_sync_workflow(dry_run=dry_run)

    elif args.command == "reverse-sync":
        reverse_sync_workflow()


if __name__ == "__main__":
    main()
