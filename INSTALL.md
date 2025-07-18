# Installation Guide

## Requirements

- **Python 3.9 or higher** (tested with Python 3.11 and 3.13)
- **pip** (Python package installer)
- **beets** with the ebooks plugin configured

**Note:** Make sure you're using the correct Python version when installing. If you have multiple Python installations, the executables will be installed in the Scripts directory of the Python version you use for installation.

## Installing Ebook Manager

There are several ways to install and use the ebook-manager utility:

### Method 1: Install from Source (Recommended for Development)

1. **Clone and install in editable mode:**
   ```bash
   git clone https://github.com/OttScott/ebook-manager.git
   cd ebook-manager
   pip install -e .
   ```

2. **After installation, you can use any of these commands:**
   ```bash
   # Full command name
   ebook-manager scan C:/Books/
   
   # Short alias
   ebm scan C:/Books/
   
   # Python module execution
   python -m ebook_manager scan C:/Books/
   ```

### Method 2: Install from PyPI (When Published)

```bash
pip install ebook-manager
```

### Method 3: Install from Wheel

1. **Build the package:**
   ```bash
   python -m build
   ```

2. **Install the wheel:**
   ```bash
   pip install dist/ebook_manager-*.whl
   ```

## Verification

After installation, verify it works:

```bash
# Test the installation
ebook-manager --help
ebm --help

# Check version
python -c "import ebook_manager; print(ebook_manager.__version__)"
```

## Dependencies

### Required Dependencies
- Python >= 3.7
- pathlib2 (for Python < 3.4)

### Optional Dependencies (for enhanced functionality)
- beets >= 1.6.0
- beets-ebooks plugin

### Development Dependencies
- pytest >= 6.0
- flake8
- black
- isort
- mypy

## Configuration

1. **Update the beets executable path** in the installed package or set an environment variable:
   ```python
   # Option 1: Edit the BEETS_EXE variable in the installed package
   # Option 2: Set environment variable
   export BEETS_EXE="/path/to/your/beet.exe"
   ```

2. **For Windows users**, make sure your Python Scripts directory is in your PATH:
   ```
   C:\Users\YourName\AppData\Roaming\Python\Python3XX\Scripts\
   ```

## Usage Examples

```bash
# Scan a collection
ebook-manager scan C:/Books/

# Import with filtering
ebm import C:/Books/ --ext .epub,.pdf --onefile

# Batch import
ebook-manager batch-import C:/Books/ --ext .epub

# Test organization
ebm test-organize
```

## Troubleshooting

### Multiple Python Versions

If you have multiple Python installations and the commands are not found:

1. **Check which Python was used for installation:**
   ```bash
   python --version
   pip show ebook-manager
   ```

2. **Use the specific Python version:**
   ```bash
   python3.13 -m pip install -e .
   # or
   "E:/Program Files/Python313/python.exe" -m pip install -e .
   ```

3. **The executables will be in the Scripts directory of the Python version used:**
   - Python 3.13: `F:\ottsc\AppData\Roaming\Python\Python313\Scripts\`
   - Python 3.11: `F:\ottsc\AppData\Roaming\Python\Python311\Scripts\`

4. **Windows users can use the PATH setup scripts:**
   ```powershell
   # Run from the project directory
   .\add_to_path.ps1
   ```

### Command not found
- Ensure Python Scripts directory is in your PATH
- Try using `python -m ebook_manager` instead
- Reinstall with `pip install -e .`

### Beets executable not found
- Update `BEETS_EXE` path in the configuration
- Install beets: `pip install beets`
- Install beets-ebooks plugin: `pip install beets-ebooks`
