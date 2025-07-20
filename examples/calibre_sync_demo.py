#!/usr/bin/env python3
"""
Example demonstrating Calibre database sync after file moves.

This example shows how the ebook-manager handles syncing Calibre's database
when files are moved by beets organization.
"""

# Import the sync functions
from ebook_manager.core import find_calibredb


def demonstrate_calibre_sync():
    """Demonstrate how Calibre sync works after file moves."""

    print("🔍 Checking for Calibre installation...")
    calibredb = find_calibredb()

    if not calibredb:
        print("❌ Calibre not found! This is just a demonstration.")
        print("   In real usage, you'd need Calibre installed.")
        print("   Download from: https://calibre-ebook.com/download")
        return

    print(f"✅ Found Calibre at: {calibredb}")
    print()

    # Simulate file moves that would happen during beets organization
    print("📚 Simulating ebook organization scenario:")
    print()

    # Before organization - files scattered in different places
    old_paths = [
        "/Downloads/Unsorted/Isaac Asimov - Foundation.epub",
        "/Downloads/Books/Douglas Adams - Hitchhiker's Guide.epub",
        "/Desktop/Frank Herbert - Dune.pdf",
    ]

    # After organization - files properly organized by beets
    new_paths = [
        "/Music/Books/Isaac Asimov/Foundation/Isaac Asimov - Foundation.epub",
        "/Music/Books/Douglas Adams/Hitchhiker's Guide to the Galaxy/Douglas Adams - Hitchhiker's Guide to the Galaxy.epub",  # noqa: E501
        "/Music/Books/Frank Herbert/Dune/Frank Herbert - Dune.pdf",
    ]

    print("📂 Before organization:")
    for path in old_paths:
        print(f"   {path}")

    print()
    print("📂 After beets organization:")
    for path in new_paths:
        print(f"   {path}")

    print()
    print("🔄 This is where Calibre sync becomes important!")
    print("   - Calibre's database still points to the old locations")
    print("   - Books would appear as 'missing' in Calibre")
    print("   - Our sync function fixes this automatically")

    print()
    print("🛠️ Running Calibre sync (simulation)...")

    # In real usage, this would be called automatically after beets moves files
    # For this demo, we'll just show what would happen
    print("   → Searching Calibre database for old file paths...")
    print("   → Updating database entries to point to new locations...")
    print("   → Removing old database entries...")
    print("   → Adding new database entries...")

    # This would be the actual call in real usage:
    # stats = sync_calibre_after_move(old_paths, new_paths)

    # Simulate the result
    stats = {"updated": 3, "failed": 0, "not_in_calibre": 0}

    print()
    print("📊 Sync Results:")
    print(f"   ✅ Updated: {stats['updated']} books")
    print(f"   ❌ Failed: {stats['failed']} books")
    print(f"   ℹ️  Not in Calibre: {stats['not_in_calibre']} books")

    print()
    print("🎉 Calibre database is now up to date!")
    print("   All books point to their new organized locations.")


def show_integration_with_beets():
    """Show how this integrates with the beets workflow."""

    print("=" * 60)
    print("INTEGRATION WITH BEETS WORKFLOW")
    print("=" * 60)
    print()

    print("1️⃣ Import books to beets:")
    print("   ebook-manager import /path/to/books/")
    print()

    print("2️⃣ Import to Calibre (optional):")
    print("   ebook-manager calibre-import /path/to/books/")
    print("   # or dual import:")
    print("   ebook-manager dual-import /path/to/books/")
    print()

    print("3️⃣ Organize with beets:")
    print("   ebook-manager organize")
    print("   # This automatically calls sync_calibre_after_move()!")
    print()

    print("✨ Result: Both beets and Calibre libraries are organized and in sync!")


if __name__ == "__main__":
    print("📖 EBOOK MANAGER - CALIBRE SYNC DEMONSTRATION")
    print("=" * 60)
    print()

    demonstrate_calibre_sync()
    print()
    show_integration_with_beets()

    print()
    print("💡 Key Benefits:")
    print("   • Automatic sync after file organization")
    print("   • No broken links in Calibre")
    print("   • Seamless integration with beets workflow")
    print("   • Works with any number of files")
    print("   • Detailed progress reporting")
