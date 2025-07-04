# Contributing to Export Photos to Nextcloud

Thank you for your interest in contributing to this project! This guide will help you get started.

## Code of Conduct

This project adheres to a simple principle: be respectful and constructive in all interactions. We welcome contributions from everyone, regardless of experience level.

## Getting Started

### Prerequisites

- macOS (required for Apple Photos.app access)
- Python 3.10 or higher
- Git
- osxphotos installed via Homebrew

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/export-photos-to-nextcloud.git
   cd export-photos-to-nextcloud
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install osxphotos**
   ```bash
   brew tap rhetbull/osxphotos
   brew install osxphotos
   ```

5. **Verify Installation**
   ```bash
   ./test_package.sh
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run specific test class
python -m pytest tests/test_export_tool_pytest.py::TestConfiguration -v

# Run tests excluding slow ones
python -m pytest -m "not slow"

# Run comprehensive package validation
./test_package.sh
```

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy export_photos_to_nextcloud_pkg/
```

### Running the Application

```bash
# Using the module
python -m export_photos_to_nextcloud_pkg --help

# Using the console script
export-photos-to-nextcloud --help

# With configuration file
export-photos-to-nextcloud --config config.yaml --dry-run -v
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-config-file-support`
- `bugfix/fix-symlink-creation`
- `docs/update-readme`

### Commit Messages

Follow conventional commits format:
- `feat: add YAML configuration file support`
- `fix: resolve symlink creation on case-sensitive filesystems`
- `docs: update README with configuration examples`
- `test: add tests for configuration file loading`

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Keep line length to 120 characters
- Use meaningful variable and function names

### Adding New Features

1. **Create an Issue**: Describe the feature and get feedback
2. **Write Tests**: Add tests for the new functionality
3. **Implement Feature**: Write the code following our style guide
4. **Update Documentation**: Update README.md and other relevant docs
5. **Test Thoroughly**: Run the full test suite

### Example: Adding a New Feature

```python
def new_feature_function(param: str) -> bool:
    """
    Brief description of what this function does.

    Args:
        param: Description of the parameter

    Returns:
        Description of the return value

    Raises:
        ValueError: When param is invalid
    """
    # Implementation here
    pass
```

## Project Structure

```
export_photos_to_nextcloud/
├── export_photos_to_nextcloud_pkg/    # Main package
│   ├── __init__.py                    # Package initialization
│   ├── __main__.py                    # Module entry point
│   └── main.py                        # Core functionality
├── tests/                             # Test suite
│   └── test_export_tool_pytest.py    # Main test file
├── requirements/                      # Dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   └── requirements-test.txt         # Test dependencies
├── requirements.txt                   # Core dependencies
├── pyproject.toml                    # Project configuration
├── config.yaml.example              # Example configuration
├── test_package.sh                   # Comprehensive test script
└── README.md                         # Documentation
```

## Testing Guidelines

### Test Categories

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Configuration Tests**: Test configuration file handling

### Writing Tests

```python
import pytest
from export_photos_to_nextcloud_pkg import Config, PhotoExporter

def test_config_creation():
    """Test that Config can be created with required parameters."""
    config = Config(
        export_dir=Path("/tmp/export"),
        nc_photos_dir=Path("/tmp/nextcloud"),
        log_file=Path("/tmp/log.txt")
    )
    assert config.export_dir == Path("/tmp/export")
    assert not config.dry_run  # Default value
```

### Test Markers

- `@pytest.mark.slow`: For tests that take a long time
- `@pytest.mark.integration`: For integration tests
- `@pytest.mark.config`: For configuration-related tests

## Documentation

### README Updates

When adding features, update:
- Feature list
- Usage examples
- Command line options
- Configuration file documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
    """
```

## Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test Your Changes**
   ```bash
   ./test_package.sh
   python -m pytest
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use a descriptive title
   - Reference any related issues
   - Describe what the PR does
   - Include testing information

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Ran test_package.sh successfully

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Comments added for complex code
```

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create tagged release
6. Update documentation

## Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for security issues

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Git commit history

Thank you for contributing to making this tool better for everyone!
