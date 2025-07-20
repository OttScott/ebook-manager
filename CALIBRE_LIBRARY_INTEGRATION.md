# Calibre Library Integration Guide

## Overview

This document explains how to configure beets and Calibre integration for optimal ebook collection management, including library path discovery and configuration options.

## Key Questions Answered

### ❓ Can beets move files directly into Calibre's library folder?

**Answer: Yes, but it's not recommended.**

**Technical Details:**

- Beets can be configured to organize files to any directory, including Calibre's library folder
- However, **Calibre expects full control** over its library structure and database integrity
- **Calibre always copies files** during import - it doesn't support "add in place" functionality
- Manual placement bypasses Calibre's metadata extraction and database updates

**Why the current approach is better:**

```
📚 RECOMMENDED WORKFLOW:
1. Beets organizes files with perfect metadata and clean structure  
2. Calibre imports the pre-organized files (creates clean copies)
3. No database conflicts - each tool manages its own domain
4. Two complementary sources: Beets for organization, Calibre for reading
```

### ❓ Can Calibre's library path be discovered or set in ebook-manager's config?

**Answer: Yes, library paths can be discovered and configured.**

## New Configuration Features

### 1. Library Path Discovery

```python
from ebook_manager.core import get_calibre_default_library_path

# Automatically discover Calibre's default library
library_path = get_calibre_default_library_path()
if library_path:
    print(f"✅ Calibre library found: {library_path}")
else:
    print("❌ Calibre library not accessible")
```

### 2. Configuration Analysis

```python
from ebook_manager.core import configure_beets_for_calibre_integration

# Get configuration recommendations
config = configure_beets_for_calibre_integration(
    calibre_library_path="default",
    organize_for_calibre=True
)

print("Recommendations:")
for rec in config["recommendations"]:
    print(f"  {rec}")
```

### 3. Enhanced Workflow Configuration

```python
from ebook_manager.core import enhanced_calibre_workflow_with_config

# Comprehensive workflow setup with auto-discovery
workflow = enhanced_calibre_workflow_with_config(
    directory="/path/to/ebooks",
    auto_discover_library=True
)

if workflow["workflow_ready"]:
    print("🎉 Ready for optimal beets/Calibre integration!")
```

## CLI Commands

### New Command: `check-calibre-config`

Check your current Calibre integration configuration:

```bash
ebook-manager check-calibre-config
```

**Output Example:**

```
🔧 Calibre Integration Configuration
============================================================
📋 Configuration Analysis:
  • Calibre library: default
  • Library discovered: True
  • Workflow ready: True

💡 Recommendations:
  ✅ Calibre detected - use 'organize-then-import' workflow for best results
  📁 Recommended beets path format: $artist/$album/$track $title
  📚 Use beets 'move' command to organize before Calibre import
  🔄 Use 'sync-calibre' command after organization to maintain sync
  🎯 Best Practice: Let beets organize first, then import clean files to Calibre

✅ Your system is ready for optimal beets/Calibre integration!
============================================================
```

## Library Path Configuration Options

### Method 1: Auto-Discovery (Recommended)

The system automatically detects Calibre's default library:

```python
# Automatic detection
config = enhanced_calibre_workflow_with_config(
    directory="/path/to/ebooks",
    auto_discover_library=True  # Default
)
```

### Method 2: Manual Specification

Specify a custom Calibre library path:

```python
# Custom library path
config = enhanced_calibre_workflow_with_config(
    directory="/path/to/ebooks",
    calibre_library="/path/to/custom/calibre/library"
)
```

### Method 3: Environment Variable

Set library path via environment variable:

```bash
export CALIBRE_LIBRARY_PATH="/path/to/calibre/library"
```

## Beets Configuration for Calibre Integration

### Recommended Beets Configuration

```yaml
# ~/.beetsrc or config.yaml
directory: ~/Music  # Your main beets library
library: ~/.config/beets/library.db

plugins: 
  - ebooks  # Enable ebooks plugin

ebooks:
    # Organize ebooks in a Calibre-friendly structure
    path_formats:
        default: $artist/$album/$track $title
        singleton: $artist/$title
        comp: Various Artists/$album/$track $title
        albumtype_soundtrack: Soundtracks/$album/$track $title
    
    # Metadata preferences
    write: yes
    copy: yes
    move: yes
```

### Path Format Recommendations

For optimal Calibre compatibility:

```yaml
ebooks:
    path_formats:
        # Standard format: Author/Book Title/Book Title.ext
        default: $artist/$title/$title
        # Series format: Author/Series Name/Book Title.ext  
        series: $artist/$albumartist/$title
        # Multi-author: Various Authors/Book Title.ext
        comp: Various Authors/$title
```

## Integration Workflows

### Workflow 1: Organize-First (Recommended)

```bash
# 1. Import scattered collection to beets
ebook-manager organize-then-import /path/to/scattered/ebooks/

# 2. The workflow automatically:
#    - Imports to beets with metadata extraction
#    - Organizes files in clean structure  
#    - Imports organized files to Calibre
```

### Workflow 2: Dual Import

```bash
# Import to both systems simultaneously
ebook-manager dual-import /path/to/ebooks/ --ext .epub,.pdf
```

### Workflow 3: Beets-First with Manual Calibre

```bash
# 1. Organize with beets
ebook-manager import /path/to/ebooks/
ebook-manager organize

# 2. Import organized files to Calibre
ebook-manager calibre-import /path/to/organized/ebooks/
```

## Advanced Configuration

### Custom Library Paths in Code

```python
from ebook_manager.core import import_to_calibre

# Import to specific Calibre library
success, message = import_to_calibre(
    file_path="/path/to/book.epub",
    calibre_library="/path/to/custom/library",
    verbose=True
)
```

### Multiple Calibre Libraries

```python
# Support for multiple Calibre libraries
libraries = ["default", "/path/to/fiction", "/path/to/technical"]

for library in libraries:
    import_to_calibre(
        file_path=book_path,
        calibre_library=library if library != "default" else None
    )
```

## Troubleshooting

### Common Issues

1. **"Calibre library not found"**

   ```bash
   # Check Calibre installation
   ebook-manager check-calibre-config
   
   # Verify Calibre in PATH
   calibredb --help
   ```

2. **"Library not accessible"**

   ```bash
   # Check permissions
   ls -la ~/.config/calibre/
   
   # Reset Calibre preferences if needed
   calibre --reset-to-defaults
   ```

3. **"Sync issues after organization"**

   ```bash
   # Use the sync command
   ebook-manager sync-calibre
   ```

### Configuration Validation

```bash
# Validate configuration
ebook-manager check-calibre-config

# Test workflow without actual import
ebook-manager organize-then-import /test/path/ --dry-run  # Future feature
```

## Best Practices

### 1. Library Management Strategy

```
🎯 RECOMMENDED APPROACH:
┌─────────────────────────────────────────┐
│  Scattered Ebooks (Various Locations)   │
└─────────────────────────────────────────┘
                    ↓
         ┌─────────────────────┐
         │   Beets Library     │ ← Master organization
         │   (Clean structure) │
         └─────────────────────┘
                    ↓
         ┌─────────────────────┐
         │  Calibre Library    │ ← Reading & management
         │  (Clean copies)     │
         └─────────────────────┘
```

### 2. Workflow Sequence

1. **Import & Organize** with beets (metadata + structure)
2. **Import to Calibre** from organized location (reading interface)
3. **Maintain sync** with periodic sync commands
4. **Keep beets as master** for organization and metadata

### 3. Metadata Quality

- Use beets for metadata extraction and correction
- Let Calibre import pre-organized files with good metadata
- Avoid manual metadata edits in multiple places

## Future Enhancements

### Planned Features

1. **Advanced Library Discovery**
   - Support for multiple Calibre libraries
   - Custom library path configuration
   - Library-specific import rules

2. **Enhanced Workflow Automation**
   - Automated sync scheduling  
   - Watch folder integration
   - Conflict resolution strategies

3. **Configuration Management**
   - Unified configuration file
   - Profile-based settings
   - Integration with beets config

### Contributing

Found an issue or have suggestions? Contributions welcome!

1. Test the new configuration features
2. Report library path discovery issues  
3. Suggest workflow improvements
4. Contribute documentation updates

---

## Summary

**The answer to your questions:**

1. ✅ **Beets CAN move files into Calibre's folder** - but it's not recommended
2. ✅ **Calibre's library path CAN be discovered and configured** - new functionality implemented
3. 🎯 **Best approach:** Use the "organize-first" workflow for optimal results

The new configuration system provides both automatic discovery and manual specification of Calibre library paths, making integration seamless while maintaining the integrity of both systems.
