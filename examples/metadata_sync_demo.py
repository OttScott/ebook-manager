#!/usr/bin/env python3
"""
Demo script showing the improved metadata-based Calibre sync.

This script demonstrates how the new sync logic matches books by
metadata rather than file paths, solving the issue where imported
books were reported as missing.
"""

import json
from unittest.mock import MagicMock, patch

from ebook_manager.core import sync_calibre_with_beets_library


def demo_sync_scenario():
    """Demonstrate a realistic sync scenario."""

    print("🎭 Calibre Sync Demo - Metadata-Based Matching")
    print("=" * 60)
    print()
    print("This demo shows how the sync now works with metadata matching,")
    print("solving the issue where books imported to Calibre were always")
    print("reported as 'missing' on subsequent syncs.")
    print()

    # Simulate a realistic scenario
    print("📚 Scenario: You have books in beets, some are already in Calibre")
    print()

    # Mock data representing a user's actual libraries
    beets_mock_data = (
        "/home/user/Books/Isaac Asimov/Foundation.epub|Isaac Asimov|Foundation|Foundation\n"
        "/home/user/Books/Douglas Adams/Hitchhiker's Guide.epub|Douglas Adams|Hitchhiker's Guide to the Galaxy|The Hitchhiker's Guide to the Galaxy\n"
        "/home/user/Books/Philip K Dick/Androids.pdf|Philip K. Dick|Do Androids Dream|Do Androids Dream of Electric Sheep?\n"
        "/home/user/Books/William Gibson/Neuromancer.mobi|William Gibson|Neuromancer|Neuromancer"
    )

    # Calibre data - some books imported (with different file paths), some missing
    calibre_mock_data = json.dumps(
        [
            {"id": "1", "title": "Foundation", "authors": "Isaac Asimov"},
            {
                "id": "2",
                "title": "The Hitchhiker's Guide to the Galaxy",
                "authors": "Douglas Adams",
            },
            # Note: Philip K. Dick and William Gibson books are missing from Calibre
        ]
    )

    print("📊 Your Libraries:")
    print("  Beets Library:")
    for line in beets_mock_data.strip().split("\n"):
        path, artist, album, title = line.split("|")
        book_title = title if title.strip() else album
        print(f"    📖 {artist} - {book_title}")

    print("  Calibre Library:")
    calibre_books = json.loads(calibre_mock_data)
    for book in calibre_books:
        print(f"    📚 {book['authors']} - {book['title']}")

    print("\n🔄 Running metadata-based sync...")
    print()

    # Mock the sync function to use our demo data
    with patch("ebook_manager.core.find_calibredb") as mock_find, patch(
        "ebook_manager.core.subprocess.run"
    ) as mock_run:

        mock_find.return_value = "/usr/bin/calibredb"

        # Mock beets query
        beets_result = MagicMock()
        beets_result.returncode = 0
        beets_result.stdout = beets_mock_data

        # Mock Calibre query
        calibre_result = MagicMock()
        calibre_result.returncode = 0
        calibre_result.stdout = calibre_mock_data

        mock_run.side_effect = [beets_result, calibre_result]

        # Run the sync
        stats = sync_calibre_with_beets_library()

    print("\n📋 Results Summary:")
    print(f"  ✅ Books found in both libraries: {stats['updated']}")
    print(f"  ❌ Books missing from Calibre: {stats['not_in_calibre']}")
    print(f"  📁 Total books scanned: {stats['scanned']}")

    if stats.get("missing_paths"):
        print(f"\n📥 Books that could be imported to Calibre:")
        for path in stats["missing_paths"]:
            filename = path.split("/")[-1]
            print(f"    📖 {filename}")

    print("\n🎉 Key Improvements:")
    print("  ✅ Books match by title & author (not file path)")
    print("  ✅ Works after Calibre imports/reorganizes files")
    print("  ✅ No more false 'missing' reports")
    print("  ✅ Accurate sync results")

    print("\n💡 What this means:")
    print("  • After importing books to Calibre, they stay 'found'")
    print("  • Sync correctly identifies truly missing books")
    print("  • No repeated import suggestions for existing books")
    print("  • Reliable long-term library synchronization")


def demo_before_and_after():
    """Show the difference between old and new approaches."""

    print("\n" + "=" * 60)
    print("📊 Before vs After Comparison")
    print("=" * 60)

    print("\n❌ OLD (Path-Based) Approach:")
    print("  1. Book in beets: /home/user/Books/Foundation.epub")
    print(
        "  2. Import to Calibre → moves to: ~/Calibre Library/Isaac Asimov/Foundation/Foundation.epub"
    )
    print("  3. Next sync: 'Foundation.epub not found' → reported as missing")
    print("  4. User imports again → creates duplicate")
    print("  5. Repeat forever... 😞")

    print("\n✅ NEW (Metadata-Based) Approach:")
    print("  1. Book in beets: artist='Isaac Asimov', album='Foundation'")
    print(
        "  2. Import to Calibre → stored as: authors='Isaac Asimov', title='Foundation'"
    )
    print("  3. Next sync: Metadata matches → book found! ✅")
    print("  4. No false missing reports")
    print("  5. Perfect sync harmony! 🎵")


if __name__ == "__main__":
    demo_sync_scenario()
    demo_before_and_after()

    print("\n" + "=" * 60)
    print("🚀 Try it yourself:")
    print("  ebook-manager sync-calibre")
    print("=" * 60)
    print("=" * 60)
