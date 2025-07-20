#!/usr/bin/env python3
"""
Demo script for the new sync-calibre command.
"""

import sys


def demo_sync_calibre_help():
    """Demonstrate the help for sync-calibre command."""
    print("=" * 60)
    print("Demo: New sync-calibre Command")
    print("=" * 60)
    print()
    print("The ebook-manager now includes a powerful sync-calibre command")
    print("that updates your Calibre database after files have been moved.")
    print()
    print("Usage:")
    print("  ebook-manager sync-calibre")
    print("  python -m ebook_manager sync-calibre")
    print()
    print("What it does:")
    print("  1. Scans your beets library for current file locations")
    print("  2. Compares with Calibre database entries")
    print("  3. Updates any mismatched file paths in Calibre")
    print("  4. Reports detailed statistics")
    print()
    print("Perfect for use after:")
    print("  - ebook-manager organize")
    print("  - Manual file moves")
    print("  - When Calibre shows 'file not found' errors")
    print()
    print("Try it yourself with: ebook-manager sync-calibre")
    print("=" * 60)

if __name__ == "__main__":
    demo_sync_calibre_help()
    demo_sync_calibre_help()
