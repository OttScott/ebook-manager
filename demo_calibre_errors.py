#!/usr/bin/env python3
"""
Demo script to test Calibre import with improved error reporting.
"""

import os
import tempfile

from ebook_manager.core import import_to_calibre


def demo_calibre_import_errors():
    """Demonstrate improved Calibre import error reporting."""
    print("=== Calibre Import Error Reporting Demo ===\n")
    
    # Test 1: Non-existent file
    print("Test 1: Importing non-existent file")
    success, message = import_to_calibre("/nonexistent/file.epub", verbose=True)
    print(f"✓ Success: {success}")
    print(f"✓ Message: {message}")
    print()
    
    # Test 2: Invalid ebook file
    print("Test 2: Importing invalid ebook file")
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        f.write(b"This is not a valid EPUB file")
        temp_file = f.name
    
    try:
        success, message = import_to_calibre(temp_file, verbose=True)
        print(f"✓ Success: {success}")
        print(f"✓ Message: {message[:200]}...")
        if len(message) > 200:
            print("  (truncated for readability)")
    finally:
        os.unlink(temp_file)
    
    print("\n=== Demo completed ===")
    print("The improved error reporting now provides:")
    print("  1. Clear success/failure status")
    print("  2. Detailed error messages from calibredb")
    print("  3. Stdout and stderr information when available")
    print("  4. Command line details when verbose=True")

if __name__ == "__main__":
    demo_calibre_import_errors()
