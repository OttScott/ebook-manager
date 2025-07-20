# Ebook Manager

A standalone command-line utility for advanced ebook collection management. This tool provides powerful features for organizing, importing, and analyzing ebook collections with support for format filtering and deduplication.

## Features

- **Advanced Import**: Batch import ebooks with sophisticated filtering
- **Format Deduplication**: `--onefile` mode selects the best format per book (EPUB > MOBI > AZW > AZW3 > PDF > LRF)
- **Extension Filtering**: `--ext` option to process only specific file formats
- **Collection Analysis**: Analyze and suggest organization structures
- **Beets Integration**: Works seamlessly with the beets-ebooks plugin
- **Batch Operations**: Process entire collections efficiently
- **🚀 Revolutionary Workflows**: Next-generation ebook management approaches

### 🚀 NEW: Calibre-Takes-Control Workflow

The revolutionary **Calibre-takes-control** workflow eliminates the traditional challenges of managing ebooks with both beets and Calibre:

**The Problem**: Traditional workflows create duplicate files and sync issues
**The Solution**: Let Calibre manage files while beets tracks them

✅ **50% less disk usage** - No duplicate files  
✅ **Zero sync issues** - Single source of truth  
✅ **Full functionality** - Both tools work perfectly  
✅ **Maximum efficiency** - Best of both worlds  

```bash
# Try the revolutionary workflow
ebook-manager calibre-takes-control /path/to/books/ --dry-run
```

## Installation

### Quick Install

1. Clone this repository:

   ```bash
   git clone https://github.com/OttScott/ebook-manager.git
   cd ebook-manager
   ```

2. Install the package:

   ```bash
   pip install -e .
   ```

3. Add to PATH (Windows):

   ```bash
   # Run the provided script to add Python Scripts to PATH
   .\add_to_path.ps1   # PowerShell
   # OR
   add_to_path.bat     # Command Prompt
   ```

4. (Optional) Install beets-ebooks plugin for enhanced functionality:

   ```bash
   pip install beets beets-ebooks
   ```

### Verify Installation

```bash
# Test the commands work
ebook-manager --help
ebm --help

# Alternative: Use Python module execution
python -m ebook_manager --help
```

## Configuration

Update the beets executable path by editing the `BEETS_EXE` variable in the installed package, or set an environment variable.

## Usage

### Command-Line Interface

After installation, you can use any of these commands:

```bash
# Full command name
ebook-manager scan C:/Books/

# Short alias (easier to type)
ebm scan C:/Books/

# Python module execution
python -m ebook_manager scan C:/Books/
```

### Basic Commands

```bash
# Scan a collection (dry run)
ebook-manager scan /path/to/books/

# Import all ebooks from a directory
python ebook_manager.py import /path/to/books/

# Import with format filtering
python ebook_manager.py import /path/to/books/ --ext .epub,.pdf

# Import one file per book (deduplication)
python ebook_manager.py import /path/to/books/ --onefile

# Combine filtering and deduplication
python ebook_manager.py import /path/to/books/ --ext .epub,.mobi --onefile

# Import from a single directory (non-recursive)
python ebook_manager.py import-dir "/path/to/specific/author/book/"

# Batch import with progress tracking
python ebook_manager.py batch-import /path/to/books/ --ext .epub --onefile

# Analyze collection structure
python ebook_manager.py analyze /path/to/books/

# Test organization (dry run)
python ebook_manager.py test-organize

# Actually organize files
python ebook_manager.py organize  # 🆕 Now with automatic Calibre sync!
```

### 🆕 Calibre Database Sync

When organizing ebooks with beets, files are moved to new locations. This can break Calibre's database links. The ebook-manager now **automatically syncs Calibre's database** after file organization:

```bash
# This now includes automatic Calibre sync after organizing
ebook-manager organize
```

**What happens:**

1. 📂 Beets organizes files to new locations
2. 🔄 Calibre database is automatically updated to point to new locations  
3. ✅ No broken links - everything stays in sync!

**Manual sync if needed:**

```python
from ebook_manager.core import sync_calibre_after_move

old_paths = ["/old/location/book.epub"]
new_paths = ["/new/location/book.epub"]
stats = sync_calibre_after_move(old_paths, new_paths)
```

See [CALIBRE_SYNC.md](CALIBRE_SYNC.md) for detailed technical documentation.

### 🆕 Calibre Library Integration

Advanced Calibre library integration with automatic path discovery and configuration:

```bash
# Check integration configuration
ebook-manager check-calibre-config

# Enhanced workflow with library auto-discovery
ebook-manager organize-then-import C:/Books/ --ext .epub
```

**New Features:**

- **Library Path Discovery**: Automatically detect Calibre's library location
- **Configuration Analysis**: Get recommendations for optimal beets/Calibre integration
- **Enhanced Workflows**: Seamless integration between beets organization and Calibre import
- **Custom Library Support**: Import to specific Calibre library paths

See [CALIBRE_LIBRARY_INTEGRATION.md](CALIBRE_LIBRARY_INTEGRATION.md) for complete integration guide.

### Format Priority (for --onefile)

When using `--onefile`, the tool selects the highest priority format per book:

1. `.epub` (highest priority)
2. `.mobi`
3. `.azw`
4. `.azw3`
5. `.pdf`
6. `.lrf` (lowest priority)

### Examples

```bash
# Import only EPUB files, one per book
python ebook_manager.py import C:/Books/ --ext .epub --onefile

# Scan collection showing what would be imported
python ebook_manager.py scan C:/Books/ --onefile

# Import a specific author's directory
python ebook_manager.py import-dir "C:/Books/Douglas Adams/Hitchhiker's Guide/"

# Analyze collection to understand structure
python ebook_manager.py analyze C:/Books/
```

## Calibre Integration

The tool includes optional integration with Calibre for additional ebook management capabilities.

### New Commands

- `calibre-scan <directory>` - Scan for ebooks and check Calibre availability
- `calibre-import <directory>` - Import ebooks directly into Calibre
- `dual-import <directory>` - Import into both Beets and Calibre
- `sync-calibre` - Sync Calibre database with current beets library state

### Requirements

- Calibre must be installed on your system
- The tool automatically detects Calibre in the following order:
  1. **PATH detection** (if you chose "Add Calibre to PATH" during installation)
  2. **Common installation paths** (fallback for standard Windows installations)

### Detection Behavior

- ✅ **Best**: If Calibre is in your PATH, it will be found immediately
- ✅ **Fallback**: If not in PATH, common Windows installation locations are checked
- ❌ **Manual**: If neither works, you may need to add Calibre to your PATH manually

### Usage Examples

```bash
# Scan for ebooks and test Calibre detection
ebook-manager calibre-scan C:/Books/

# Import ebooks into Calibre only
ebook-manager calibre-import C:/Books/ --ext .epub --onefile

# Import into both Beets and Calibre
ebook-manager dual-import C:/Books/ --ext .epub,.pdf

# Sync Calibre database with beets library (after organizing)
ebook-manager sync-calibre
```

## Integration with Beets-Ebooks

This utility is designed to work alongside the [beets-ebooks plugin](https://github.com/OttScott/beets-ebooks). The plugin provides the core beets integration, while this utility offers advanced collection management features.

### Workflow

1. **Install both packages**:
   - `beets-ebooks` for plugin functionality
   - `ebook-manager` for advanced utilities

2. **Configure beets** with the ebooks plugin enabled

3. **Use ebook-manager** for advanced operations:
   - Format deduplication with `--onefile`
   - Extension filtering with `--ext`
   - Collection analysis and organization

## Commands Reference

| Command | Description | Options |
|---------|-------------|---------|
| `scan` | Scan collection (dry run) | `--ext`, `--onefile` |
| `import` | Import ebooks to beets | `--ext`, `--onefile` |
| `import-dir` | Import from single directory | `--ext`, `--onefile` |
| `batch-import` | Batch import with progress | `--ext`, `--onefile` |
| `calibre-scan` | Scan and check Calibre availability | `--ext`, `--onefile` |
| `calibre-import` | Import ebooks to Calibre | `--ext`, `--onefile` |
| `dual-import` | Import to both Beets and Calibre | `--ext`, `--onefile` |
| `organize-then-import` | 🌟 Organize with beets, then import to Calibre | `--ext`, `--onefile` |
| `calibre-takes-control` | 🚀 **NEW**: Let Calibre manage files, beets tracks them | `--ext`, `--onefile`, `--dry-run` |
| `sync-calibre` | Sync Calibre DB with beets library | None |
| `check-calibre-config` | Check Calibre integration configuration | None |
| `analyze` | Analyze collection structure | `--ext`, `--onefile` |
| `test-organize` | Test organization (dry run) | None |
| `organize` | Actually organize files | None |
| `process` | Process single file | None |

### 🚀 Revolutionary New Workflow

**`calibre-takes-control`** - The next evolution in ebook management:

- **Single File Storage**: Eliminates duplicate files (50% disk savings)
- **No Sync Issues**: Beets tracks Calibre-managed files automatically
- **Best of Both Tools**: Full functionality from both beets and Calibre
- **Maximum Efficiency**: Calibre manages files, beets provides metadata search

```bash
# Test the revolutionary workflow (recommended first step)
ebook-manager calibre-takes-control /path/to/books/ --dry-run

# Execute the workflow
ebook-manager calibre-takes-control /path/to/books/ --ext .epub --onefile
```

See [CALIBRE_TAKES_CONTROL.md](CALIBRE_TAKES_CONTROL.md) for complete documentation.

## Options

- `--ext EXTENSIONS`: Comma-separated file extensions (e.g., `--ext .epub,.pdf`)
- `--onefile`: Import only one file per book (highest priority format)
- `--dry-run`: Show what would be done without making changes (for `calibre-takes-control`)

## System Requirements

- Python 3.7+
- Beets (for import functionality)
- beets-ebooks plugin (recommended)

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest tests/ -v

# Run example
python examples/onefile_demo.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Related Projects

- [beets-ebooks](https://github.com/OttScott/beets-ebooks): Beets plugin for ebook management
- [Beets](https://beets.io/): The music library manager that inspired this project
