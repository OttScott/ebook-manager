# Calibre Database Sync After File Organization

## Problem Statement

When you use both Calibre and beets to manage your ebook collection, you may encounter a common issue:

1. **Import books to Calibre** - Calibre creates database entries pointing to the original file locations
2. **Organize with beets** - Beets moves files to new organized locations based on metadata  
3. **Broken links** - Calibre's database still points to the old locations, making books appear "missing"

## Solution: Automatic Calibre Sync

The ebook-manager now includes automatic Calibre database synchronization that runs after beets organizes your files.

### How It Works

1. **Before organization**: Capture the current file paths from beets
2. **Run organization**: Let beets move files to their new organized locations  
3. **Get new paths**: Capture the new file paths after organization
4. **Sync Calibre**: Update Calibre's database to point to the new locations

### Key Functions

#### `find_books_in_calibre(old_path: str) -> List[dict]`

Searches Calibre's database for books that reference a specific file path.

```python
books = find_books_in_calibre("/old/path/book.epub")
# Returns: [{"id": "123", "path": "/old/path/book.epub"}]
```

#### `update_calibre_book_path(book_id: str, old_path: str, new_path: str) -> bool`

Updates a specific book's path in Calibre's database by:

1. Adding the book at the new location
2. Removing the old database entry

```python
success = update_calibre_book_path("123", "/old/path/book.epub", "/new/path/book.epub")
```

#### `sync_calibre_after_move(old_paths: List[str], new_paths: List[str]) -> dict`

Main sync function that processes multiple file moves in batch.

```python
old_paths = ["/old/path1.epub", "/old/path2.pdf"]
new_paths = ["/new/path1.epub", "/new/path2.pdf"]

stats = sync_calibre_after_move(old_paths, new_paths)
# Returns: {"updated": 2, "failed": 0, "not_in_calibre": 0}
```

### Automatic Integration

The sync happens automatically when you run:

```bash
ebook-manager organize
```

The `test_organization()` function:

1. Gets current file paths before moving
2. Runs beets move operation  
3. Gets new file paths after moving
4. Calls `sync_calibre_after_move()` if Calibre is available

### Manual Usage

You can also manually sync if needed:

```python
from ebook_manager.core import sync_calibre_after_move

# If you know the old and new paths
old_paths = ["/old/location/book.epub"]
new_paths = ["/new/location/book.epub"] 

stats = sync_calibre_after_move(old_paths, new_paths)
print(f"Updated {stats['updated']} books")
```

### Requirements

- **Calibre installed**: The `calibredb` command must be available
- **File access**: New files must exist at their new locations
- **Database access**: Calibre library must be accessible

### Error Handling

The sync function handles various scenarios:

- **Calibre not found**: Skips sync with informational message
- **File not found**: Skips that specific file with warning  
- **Database errors**: Continues processing other files
- **Path mismatches**: Validates input parameters

### Example Output

```
🔄 Syncing Calibre database after file moves...
  Checking: Foundation.epub
    ✅ Updated Calibre entry (ID: 123)
  Checking: Dune.pdf  
    ℹ️  Not found in Calibre library
  Checking: Hitchhiker's Guide.epub
    ✅ Updated Calibre entry (ID: 456)
    
📊 Calibre sync summary:
  ✅ Updated: 2 entries
  ❌ Failed: 0 entries  
  ℹ️  Not in Calibre: 1 files
```

### Benefits

- **Seamless workflow**: No manual intervention required
- **Data integrity**: Prevents broken links in Calibre
- **Batch processing**: Efficiently handles many files at once
- **Robust error handling**: Continues working even if some files fail
- **Detailed reporting**: Shows exactly what was updated

### Workflow Integration

```bash
# Complete workflow with automatic sync
ebook-manager dual-import /path/to/books/     # Import to both beets and Calibre
ebook-manager organize                        # Organize and auto-sync Calibre
```

This ensures both your beets and Calibre libraries stay perfectly synchronized!
