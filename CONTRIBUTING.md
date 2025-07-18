# Contributing to Ebook Manager

Thank you for your interest in contributing to ebook-manager! This document provides guidelines and information for contributors.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OttScott/ebook-manager.git
   cd ebook-manager
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ebook_manager --cov-report=html

# Run specific test
pytest tests/test_ebook_manager.py::TestEbookManager::test_filter_onefile_per_book -v
```

## Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black ebook_manager/ tests/

# Sort imports
isort ebook_manager/ tests/

# Lint code
flake8 ebook_manager/ tests/

# Type checking
mypy ebook_manager/ --ignore-missing-imports
```

## Testing

- Write tests for new functionality
- Ensure all tests pass before submitting PR
- Maintain or improve test coverage
- Use descriptive test names and docstrings

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** with appropriate tests
3. **Run the test suite** and ensure all tests pass
4. **Run code quality checks** (black, isort, flake8, mypy)
5. **Submit a pull request** with a clear description

## Commit Messages

Use clear, descriptive commit messages:

```
Add --onefile feature for format deduplication

- Implement FORMAT_PRIORITY for file selection
- Add extract_book_identifier for grouping books
- Update CLI to support --onefile flag
- Add comprehensive tests for new functionality
```

## Features and Enhancements

### Core Features
- File detection and filtering
- Format deduplication (--onefile)
- Beets integration
- Batch operations

### Potential Enhancements
- Support for additional ebook formats
- Enhanced metadata extraction
- Better error handling and logging
- Configuration file support
- Integration with other library managers

## Architecture

- `ebook_manager/core.py`: Core functionality (file detection, filtering)
- `ebook_manager/__main__.py`: CLI interface and beets integration
- `ebook_manager/__init__.py`: Package initialization and exports
- `tests/`: Comprehensive test suite

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs if applicable

## Code Style

- Follow PEP 8
- Use black for formatting (line length: 88)
- Use isort for import sorting
- Include docstrings for public functions
- Use type hints where appropriate

Thank you for contributing!
