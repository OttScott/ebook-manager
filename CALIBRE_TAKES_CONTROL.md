# Calibre-Takes-Control Workflow

## Overview

The **Calibre-takes-control** workflow is a revolutionary approach to ebook management that combines the best of both beets and Calibre while eliminating the complexity of file synchronization.

## Philosophy

Instead of trying to keep two separate file hierarchies in sync, this workflow:

1. **Lets Calibre manage the files** (single source of truth for storage)
2. **Updates beets to track Calibre's files** (preserves all metadata and search capabilities)
3. **Eliminates duplicate storage** (maximum efficiency)
4. **Prevents sync issues** (no more broken links or file conflicts)

## How It Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Source Files  │ => │      Beets      │ => │     Calibre     │
│  /books/*.epub  │    │  (metadata)     │    │  (file mgmt)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              └────── Points to ──────┘
```

### Workflow Steps

1. **Import to Beets**: Each book is imported to beets first for metadata extraction and processing
2. **Import to Calibre**: The same book is then imported to Calibre, which copies it to its managed library structure
3. **Database Update**: Beets' database is updated to point to Calibre's managed copy instead of the original file
4. **File Cleanup**: The original file is deleted (since beets now tracks Calibre's copy)

### Result

- ✅ **Single File Storage**: Each book exists only once (in Calibre's library)
- ✅ **Full Beets Functionality**: All beets commands and plugins work normally
- ✅ **Full Calibre Functionality**: Calibre manages files as it prefers
- ✅ **No Sync Issues**: Beets automatically tracks Calibre's file locations
- ✅ **Storage Efficiency**: No duplicate files wasting disk space

## Usage

### Basic Command

```bash
python ebook_manager.py calibre-takes-control /path/to/books/
```

### With Options

```bash
# Process only EPUB files
python ebook_manager.py calibre-takes-control /path/to/books/ --ext .epub

# One file per book (highest quality format)
python ebook_manager.py calibre-takes-control /path/to/books/ --onefile

# Dry run to see what would happen
python ebook_manager.py calibre-takes-control /path/to/books/ --dry-run

# Combined options
python ebook_manager.py calibre-takes-control /path/to/books/ --ext .epub,.mobi --onefile --dry-run
```

## Prerequisites

1. **Beets installed and configured** with the `beets-ebooks` plugin
2. **Calibre installed** and accessible via command line
3. **Source directory** containing ebooks to process

## Safety Features

### Dry Run Mode

Always test with `--dry-run` first:

```bash
python ebook_manager.py calibre-takes-control /path/to/books/ --dry-run
```

This shows exactly what would happen without making any changes.

### Error Handling

- If beets import fails, the workflow skips to the next file
- If Calibre import fails, the original file is preserved
- If database update fails, the original file is preserved
- Detailed error reporting helps troubleshoot issues

### Backup Recommendation

Before running the workflow on important collections, consider:

1. **Test on a small subset** using `--dry-run`
2. **Backup your beets database**
3. **Ensure Calibre library is backed up**

## Benefits Over Other Approaches

### vs. Traditional Dual Storage

- **50% less disk usage** (no duplicate files)
- **No sync issues** (single source of truth)
- **Simpler maintenance** (one file hierarchy)

### vs. Organize-Then-Import

- **More efficient storage** (eliminates the beets copy)
- **Calibre-native file management** (optimal for Calibre users)
- **Automatic database consistency** (beets always points to existing files)

### vs. Manual Management

- **Automated process** (handles hundreds of books)
- **Preserves metadata** (both beets and Calibre metadata)
- **Error handling** (graceful failure recovery)

## Example Output

```
🚀 CALIBRE-TAKES-CONTROL WORKFLOW
============================================================
This workflow revolutionizes ebook management by letting
Calibre manage files while beets handles metadata.

✓ Found beets at: /usr/local/bin/beet
✓ Found Calibre at: /usr/local/bin/calibredb

Found 25 ebook(s) to process
One-file mode: selecting highest priority format per book

🔄 WORKFLOW STEPS:
  1. Import each book to beets (for metadata extraction)
  2. Import each book to Calibre (creates managed copy)
  3. Update beets database to point to Calibre's managed file
  4. Delete original file (beets now tracks Calibre's copy)

💡 RESULT: Calibre manages files, beets tracks them

============================================================
🚀 STARTING CALIBRE-TAKES-CONTROL WORKFLOW
============================================================

[Processing books...]

============================================================
📊 WORKFLOW RESULTS
============================================================
📁 Total files processed: 25
📥 Imported to beets: 25/25
📚 Imported to Calibre: 25/25
🔄 Database updates: 25/25
🗑️ Files deleted: 25/25

🎉 SUCCESS!
============================================================
✨ 25 books are now managed by Calibre!
✨ Beets tracks Calibre's managed files!
✨ No duplicate storage - maximum efficiency!

🔥 BENEFITS ACHIEVED:
  • Calibre is the file manager (single source of truth)
  • Beets retains full metadata and search capabilities
  • No sync issues - beets tracks Calibre's files
  • Storage efficiency - no duplicate files
  • Best of both tools combined!
============================================================
```

## Troubleshooting

### Common Issues

1. **"Calibre not found"**
   - Install Calibre from <https://calibre-ebook.com/>
   - Ensure `calibredb` is in your PATH

2. **"Beets import failed"**
   - Check beets configuration
   - Ensure `beets-ebooks` plugin is installed and enabled

3. **"Database update failed"**
   - Usually indicates a beets configuration issue
   - Check beets database permissions

4. **"Could not find Calibre file location"**
   - Calibre may have failed to import the book
   - Check Calibre library for the book

### Recovery

If something goes wrong mid-process:

1. **Check the error messages** - they provide specific guidance
2. **Run with `--dry-run`** to understand what would happen
3. **Restore from backup** if necessary
4. **Process remaining files** by excluding already-processed ones

## Integration with Other Commands

The Calibre-takes-control workflow works well with other ebook-manager commands:

```bash
# Use after workflow to verify everything is working
python ebook_manager.py sync-calibre

# Check configuration before running workflow
python ebook_manager.py check-calibre-config

# Analyze collection first
python ebook_manager.py analyze /path/to/books/
```

## Advanced Usage

### Custom Beets Configuration

The workflow works with any beets configuration, but benefits from:

```yaml
# ~/.config/beets/config.yaml
paths:
    default: $albumartist/$album/$track $title
    ebook: $artist/$album/$title

plugins:
    - edit
    - fetchart
    - ebooks
```

### Calibre Library Management

The workflow respects Calibre's library settings:

- Uses the default Calibre library
- Preserves existing Calibre metadata
- Maintains Calibre's file organization
- Works with multiple libraries (specify with `--library-path`)

## Comparison with Other Workflows

| Feature | Calibre-Takes-Control | Organize-Then-Import | Dual-Import |
|---------|----------------------|---------------------|-------------|
| Storage Efficiency | ✅ Single copy | ❌ Two copies | ❌ Two copies |
| Sync Issues | ✅ None | ⚠️ Possible | ❌ Common |
| Beets Functionality | ✅ Full | ✅ Full | ✅ Full |
| Calibre Functionality | ✅ Full | ✅ Full | ✅ Full |
| File Manager | Calibre | Beets | Both |
| Maintenance | ✅ Minimal | ⚠️ Moderate | ❌ High |
| Disk Usage | ✅ Optimal | ⚠️ 2x | ❌ 2x+ |

## Future Enhancements

Planned improvements:

- **Selective processing** (process only new/changed books)
- **Multiple library support** (specify target Calibre library)
- **Metadata synchronization** (two-way sync between beets and Calibre)
- **GUI integration** (visual workflow management)

---

*This workflow represents the next evolution in ebook management, combining the strengths of both tools while eliminating their traditional limitations.*
