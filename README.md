# Ebook Manager

A standalone command-line utility for advanced ebook collection management. This tool provides powerful features for organizing, importing, and analyzing ebook collections with support for format filtering and deduplication.

## Features

- **Advanced Import**: Batch import ebooks with sophisticated filtering
- **Format Deduplication**: `--onefile` mode selects the best format per book (EPUB > MOBI > AZW > AZW3 > PDF > LRF)
- **Extension Filtering**: `--ext` option to process only specific file formats
- **Collection Analysis**: Analyze and suggest organization structures
- **Beets Integration**: Works seamlessly with the beets-ebooks plugin
- **Batch Operations**: Process entire collections efficiently

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
python ebook_manager.py organize
```

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
| `analyze` | Analyze collection structure | `--ext`, `--onefile` |
| `test-organize` | Test organization (dry run) | None |
| `organize` | Actually organize files | None |
| `process` | Process single file | None |

## Options

- `--ext EXTENSIONS`: Comma-separated file extensions (e.g., `--ext .epub,.pdf`)
- `--onefile`: Import only one file per book (highest priority format)

## Requirements

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
