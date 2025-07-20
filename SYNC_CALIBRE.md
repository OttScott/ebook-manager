# Calibre Database Sync

The ebook-manager now includes a powerful feature to sync your Calibre database with your beets library after files have been moved or organized.

## The Problem

When you use beets to organize your ebook files (e.g., with `ebook-manager organize`), the files are moved to new locations based on metadata. However, Calibre's database still points to the old file locations, causing:

- ❌ Broken links in Calibre library
- ❌ "File not found" errors when opening books
- ❌ Metadata inconsistencies between beets and Calibre

## The Solution: `sync-calibre` Command

The new `sync-calibre` command intelligently compares your beets library with your Calibre database and updates any mismatched file paths.

### Usage

```bash
# Basic sync command
ebook-manager sync-calibre

# Or using the full module syntax
python -m ebook_manager sync-calibre
```

### What It Does

1. **Scans your beets library** to get current file locations
2. **Scans your Calibre library** to get database entries
3. **Matches books** by filename and path
4. **Updates Calibre entries** that point to old/incorrect locations
5. **Reports results** with detailed statistics

### Example Output

```
🔄 Calibre Database Sync
==================================================
This will update Calibre's database to match the current
file locations in your beets library.

✓ Found Calibre at: E:\Program Files\Calibre2\calibredb.exe
✓ Found beets at: F:\ottsc\AppData\Roaming\Python\Python313\Scripts\beet.exe

Continue with Calibre database sync? (y/N): y

🔄 Syncing Calibre database with current beets library...
📚 Found 14 ebooks in beets library
📖 Found 156 books in Calibre library
  Checking: Robert Jordan & Brandon Sanderson - Wheel of Time 14 - A Memory of Light (v4.0) (epub).epub
    🔄 Updating path: book_old_location.epub -> book_new_location.epub
    ✅ Updated Calibre entry (ID: 1159)
  Checking: Another Book.pdf
    ✅ Already in sync
  Checking: Third Book.epub
    ℹ️  Not found in Calibre library

============================================================
📊 Calibre sync completed!
  📚 Scanned: 14 ebooks in beets library
  ✅ Updated: 3 Calibre entries
  ❌ Failed: 0 updates
  ℹ️  Not in Calibre: 2 files
============================================================

🎉 Successfully updated 3 Calibre entries!
```

### When to Use This Command

- **After organizing with beets**: Run `ebook-manager organize` followed by `ebook-manager sync-calibre`
- **After manual file moves**: If you've moved ebook files outside of beets
- **When Calibre shows "file not found" errors**: Fix broken links in bulk
- **Regular maintenance**: Periodically sync to keep libraries in harmony

### Automatic Sync During Organization

The sync also happens automatically when you use `ebook-manager organize` (non-dry-run mode), but you can run it manually anytime with the `sync-calibre` command.

### Safety Features

- **Read-only for beets**: Only reads from beets library, never modifies it
- **Smart matching**: Matches books by filename and path to avoid false positives
- **Detailed reporting**: Shows exactly what was updated, failed, or skipped
- **Confirmation required**: Asks for user confirmation before making changes
- **Error handling**: Gracefully handles missing files or database errors

### Requirements

- Calibre must be installed and `calibredb` must be accessible
- Beets must be installed and configured
- Both libraries should contain overlapping ebook collections

### Troubleshooting

**"Calibre not found"**

- Ensure Calibre is installed and in your system PATH
- The tool looks for `calibredb` executable

**"Beets not found"**

- Check the BEETS_EXE path in the configuration
- Ensure beets is properly installed

**"No ebooks found in beets library"**

- Import some ebooks to beets first using other ebook-manager commands
- Check that ebooks are tagged with `ebook:true` in beets

**Updates failing**

- Check file permissions
- Ensure files exist at the new locations
- Check Calibre library isn't locked by another process

This feature bridges the gap between beets and Calibre, keeping both libraries perfectly synchronized! 🎯
