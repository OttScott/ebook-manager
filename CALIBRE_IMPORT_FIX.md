# Calibre Import Fix - Error Resolution

## Problem Analysis

The user reported that Calibre imports were failing during dual-import operations with the error message:

```
✗ Calibre import failed
```

After investigation, we discovered two main issues:

### Issue 1: Invalid Command Line Option

**Root Cause:** The `import_to_calibre` function was using `--ignore-duplicate` option, which is not a valid option for `calibredb add`.

**Solution:** Changed to use the correct option `--automerge ignore` for handling duplicates.

### Issue 2: Poor Error Reporting

**Root Cause:** The `import_to_calibre` function was silently swallowing all exceptions, making it impossible to diagnose why imports were failing.

**Solution:** Completely redesigned the function to return detailed error information.

## Changes Made

### 1. Enhanced `import_to_calibre` Function (core.py)

**Before:**

```python
def import_to_calibre(file_path: str, ...) -> bool:
    # ... 
    try:
        # command execution
        return True/False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False  # Silent failure!
```

**After:**

```python
def import_to_calibre(file_path: str, ..., verbose: bool = False) -> tuple[bool, str]:
    # ...
    try:
        # command execution with verbose logging
        return success, detailed_message
    except subprocess.CalledProcessError as e:
        error_msg = f"calibredb command failed (exit code {e.returncode})"
        if e.stdout:
            error_msg += f"\nstdout: {e.stdout.strip()}"
        if e.stderr:
            error_msg += f"\nstderr: {e.stderr.strip()}"
        return False, error_msg
```

### 2. Fixed Command Line Options

**Before:**

```python
cmd.append("--ignore-duplicate")  # Invalid option!
```

**After:**

```python
cmd.extend(["--automerge", "ignore"])  # Correct option
```

### 3. Updated CLI Wrapper Functions (**main**.py)

**Before:**

```python
def import_ebook_to_calibre(ebook_path: str) -> bool:
    try:
        success = import_to_calibre(ebook_path)
        return success
    except Exception as e:
        print(f"Error importing {ebook_path} to Calibre: {e}")
        return False
```

**After:**

```python
def import_ebook_to_calibre(ebook_path: str) -> bool:
    try:
        success, message = import_to_calibre(ebook_path, verbose=True)
        if not success:
            print(f"    Error importing {os.path.basename(ebook_path)} to Calibre: {message}")
        return success
    except Exception as e:
        print(f"    Unexpected error importing {os.path.basename(ebook_path)} to Calibre: {e}")
        return False
```

### 4. Updated Test Cases

All test cases were updated to handle the new tuple return type `(bool, str)` instead of just `bool`.

## Results

### Before Fix

```
✗ Calibre import failed
```

No information about why the import failed.

### After Fix

```
✗ Calibre import failed
    Error importing book.epub to Calibre: calibredb command failed (exit code 2)
    stderr: calibredb.exe: error: no such option: --ignore-duplicate
```

Clear, actionable error messages that help diagnose the problem.

## Testing

- ✅ All 47 tests pass
- ✅ Flake8 linting passes
- ✅ Black formatting applied
- ✅ Manual testing shows detailed error messages
- ✅ Correct calibredb options now used

## User Impact

Users will now see:

1. **Clear error messages** when Calibre imports fail
2. **Command line details** when verbose mode is enabled
3. **Stdout/stderr output** from calibredb for debugging
4. **Successful imports** that were previously failing due to invalid command options

The dual-import feature should now work correctly with proper error reporting for any remaining issues.
