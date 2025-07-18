# Development Workspace Setup

This document explains the VS Code workspace configuration for the ebook-manager project.

## Workspace Structure

The ebook-manager uses a **separate VS Code workspace** from the beets-ebooks plugin for several reasons:

### Why Separate Workspaces?

1. **Clear Focus**: Each workspace serves a distinct purpose
   - `beets-ebooks` → Plugin development and beets integration
   - `ebook-manager` → Standalone CLI utility development

2. **Different Tooling Needs**:
   - **Plugin**: Heavy mocking, beets-specific testing, plugin architecture
   - **Utility**: CLI testing, subprocess integration, packaging workflows

3. **Independent Dependencies**:
   - **Plugin**: Requires beets, ebooklib, requests as core dependencies
   - **Utility**: Minimal dependencies, beets optional for enhanced functionality

4. **Separate Git Repositories**: Avoids confusion about commits and releases

## Opening the Workspace

```bash
# Option 1: Open workspace file directly
code ebook-manager.code-workspace

# Option 2: Open folder and configure
code .
# Then: File → Open Workspace from File → ebook-manager.code-workspace
```

## Workspace Features

### 🔧 **Configured Tools**
- **Python**: Testing with pytest, linting with flake8
- **Formatting**: Black formatter with auto-format on save
- **Import Organization**: isort for clean import statements
- **Type Checking**: MyPy integration

### 📁 **File Management**
- Hides build artifacts (`__pycache__`, `dist`, `build`)
- Excludes development files from search
- Clean project view focused on source code

### ⚡ **Quick Tasks**
- **Ctrl+Shift+P** → `Tasks: Run Task`
  - "Run Tests" → Full test suite
  - "Format Code" → Black formatting
  - "Lint Code" → Flake8 linting
  - "Build Package" → Create distribution

### 🧪 **Testing Integration**
- Tests discoverable in VS Code Test Explorer
- Run individual tests or full suite
- Debug test execution with breakpoints

## Integration with Beets-Ebooks

While the workspaces are separate, the projects work together:

```bash
# Install both packages for full functionality
pip install beets-ebooks  # Plugin for beets integration
pip install ebook-manager  # Utility for advanced operations

# Use together
beet import-ebooks /path/to/books/     # Plugin import
ebook-manager scan /path/to/books/ --onefile  # Utility analysis
```

## Development Workflow

1. **Plugin Development**: Work in `beets-ebooks` workspace
   - Focus on beets integration
   - Test with mock beets environment
   - Plugin-specific features

2. **Utility Development**: Work in `ebook-manager` workspace  
   - Focus on CLI functionality
   - Test with real file operations
   - Advanced collection management

3. **Integration Testing**: Test both packages together
   - Verify compatibility
   - End-to-end workflows
   - Cross-package functionality

This separation ensures clean development while maintaining powerful integration capabilities.
