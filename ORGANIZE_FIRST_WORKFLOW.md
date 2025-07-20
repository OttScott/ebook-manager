# Organize-First Workflow Guide

## 🌟 Recommended Approach for Calibre Integration

The **organize-first workflow** is the optimal way to manage your ebook collection when using both beets and Calibre. This approach solves the common issues with file duplication and sync problems by organizing books with beets first, then importing the well-organized files to Calibre.

## Why This Workflow is Superior

### Traditional Approach Problems

```
Raw Files → Import to Calibre (creates messy copies)
         → Import to beets (organizes originals)  
         → Sync issues (paths don't match)
         → Metadata conflicts
```

### Organize-First Solution

```
Raw Files → Import to Beets (perfect metadata + organization)
         → Import organized files to Calibre (clean copies)
         → No sync needed! ✅
```

## Benefits

1. **🎯 Perfect Metadata**: Beets excels at metadata extraction and correction
2. **📁 Consistent Organization**: Clean, standardized file/folder structure
3. **🔄 No Sync Issues**: Calibre imports pre-organized files
4. **📚 Single Source of Truth**: Beets library becomes the master
5. **✨ Clean Calibre Library**: Calibre gets perfectly organized books

## Command Usage

```bash
# Basic usage
ebook-manager organize-then-import /path/to/books

# With file filtering
ebook-manager organize-then-import /path/to/books --ext .epub,.pdf

# With format deduplication
ebook-manager organize-then-import /path/to/books --onefile

# Combined options
ebook-manager organize-then-import /path/to/books --ext .epub,.mobi --onefile
```

## Workflow Steps

### Step 1: Import to Beets

- Scans directory for ebook files
- Imports each book to beets library
- Extracts and corrects metadata
- Files remain in original locations initially

### Step 2: Organize with Beets

- Runs `beet move ebook:true` to organize files
- Creates clean folder structure: `Author/Book Title/file.ext`
- Standardizes file naming conventions
- Updates beets database with new paths

### Step 3: Import to Calibre

- Gets organized file paths from beets library
- Imports each well-organized file to Calibre
- Calibre creates copies in its own structure
- No sync issues since metadata is already perfect

## Example Session

```bash
$ ebook-manager organize-then-import ~/Downloads/Books --ext .epub,.pdf --onefile

🔄 Organize-First Workflow
============================================================
This workflow organizes books with beets first, then imports
the well-organized files to Calibre for the best results.

✓ Found beets at: /usr/bin/beet
✓ Found Calibre at: /usr/bin/calibredb

📥 STEP 1: Import and organize with beets
----------------------------------------
Found 15 ebook(s) to import
Filtering by extensions: ['.epub', '.pdf']
One-file mode: selecting highest priority format per book

Proceed with importing 15 ebooks to beets? (y/N): y

🔄 Importing to beets library...
[1/15] Importing: Foundation.epub
  ✅ Imported successfully
[2/15] Importing: Neuromancer.pdf  
  ✅ Imported successfully
...

Beets import result: 15/15 successful

📁 STEP 2: Organize imported books with beets
---------------------------------------------
This will move books to their proper organized locations
based on the metadata beets extracted.

Run beets organization? (Y/n): y

🔄 Organizing books with beets...
Organization results:
Isaac Asimov/Foundation/Foundation.epub
William Gibson/Neuromancer/Neuromancer.pdf
...

✅ Organization complete! Books are now properly organized.

📚 STEP 3: Import organized books to Calibre
--------------------------------------------
Now importing the well-organized books from your beets library
to Calibre. This creates clean copies with perfect metadata.

Found 15 organized books to import to Calibre

Import 15 organized books to Calibre? (y/N): y

🔄 Importing organized books to Calibre...
[1/15] Importing: Foundation.epub
  ✅ Imported successfully
[2/15] Importing: Neuromancer.pdf
  ✅ Imported successfully
...

Calibre import result: 15/15 successful

============================================================
🎉 ORGANIZE-FIRST WORKFLOW COMPLETE!
============================================================
📥 Imported to beets: 15/15 books
📚 Imported to Calibre: 15/15 books

✨ Benefits achieved:
  • Books are perfectly organized with beets metadata
  • File names and folders follow consistent patterns
  • Calibre has clean copies with excellent metadata  
  • No sync issues - Calibre imported pre-organized files
  • Beets library is the master source of truth
============================================================
```

## Comparison with Other Workflows

| Feature | organize-then-import | dual-import | sync-calibre |
|---------|---------------------|-------------|--------------|
| **Metadata Quality** | ⭐⭐⭐ Excellent | ⭐⭐ Good | ⭐⭐ Good |
| **File Organization** | ⭐⭐⭐ Perfect | ⭐ Basic | ⭐ Basic |
| **Sync Issues** | ✅ None | ❌ Common | ⚠️ Handled |
| **Storage Efficiency** | ⭐⭐ 2x storage | ⭐⭐ 2x storage | ⭐⭐ 2x storage |
| **Setup Complexity** | ⭐⭐⭐ Simple | ⭐⭐ Moderate | ⭐ Complex |
| **Maintenance** | ✅ Minimal | ⚠️ Regular sync | ⚠️ Regular sync |

## Best Practices

### Before Running

1. **Backup your files** - Always backup before bulk operations
2. **Test with small batches** - Try with a few books first
3. **Check available space** - Ensure enough disk space (files will be duplicated)
4. **Configure beets properly** - Set up your preferred directory structure

### After Running

1. **Verify organization** - Check that files are properly organized
2. **Test Calibre library** - Open Calibre and verify books imported correctly
3. **Clean up originals** - Optionally remove original unorganized files
4. **Set up backups** - Both beets and Calibre libraries should be backed up

## Troubleshooting

### Common Issues

**"No books found in beets library"**

- Check that beets import completed successfully
- Verify beets configuration is correct
- Run `beet ls ebook:true` to check what's in the library

**"Calibre import failed"**

- Ensure Calibre is installed and accessible
- Check file permissions on organized files
- Verify file formats are supported by Calibre

**"Organization failed"**

- Check beets configuration for path formats
- Ensure adequate disk space for file moves
- Verify write permissions in target directories

### Getting Help

- Run with smaller batches to isolate issues
- Check the output logs for specific error messages
- Verify both beets and Calibre are properly configured
- Consult the main documentation for detailed setup instructions

## Migration from Other Workflows

### From dual-import

1. Use `sync-calibre` to see current state
2. Run organize-first workflow on new books only
3. Gradually migrate existing books as needed

### From manual management

1. Start with organize-first for all new books
2. Consider re-importing existing collection for consistency
3. Use beets as the primary organization tool going forward

---

*This workflow provides the cleanest, most maintainable approach to ebook collection management with both beets and Calibre.*
