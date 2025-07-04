# Export Photos to Nextcloud

A modern Python tool for exporting photos from Apple Photos.app and syncing them to Nextcloud with beautiful progress tracking and robust logging.

## Features

- 🚀 **Modern Python CLI** - Built with Click, Rich, and Loguru for beautiful terminal output
- 📸 **OSXPhotos Integration** - Leverages the powerful osxphotos library for photo export
- 🔗 **Smart Symlink Management** - Automatically creates organized symlinks in your Nextcloud directory
- 📊 **Progress Tracking** - Rich progress bars and detailed logging
- 🏃‍♂️ **Dry Run Mode** - Test your configuration before making changes
- 📝 **YAML Configuration** - Configure via YAML file with CLI override support
- 🎨 **AAE Support** - Export Apple adjustment files for edited photos
- 🧹 **Cleanup Options** - Automated photo organization and metadata cleanup
- ⚡ **Fast & Reliable** - Optimized for performance with retry logic and robust error handling

## Installation

### Prerequisites

1. **macOS** - This tool only works on macOS with access to Photos.app
2. **Python 3.10+** - Required for the modern Python features used
3. **osxphotos** - Install via Homebrew:
   ```bash
   brew tap rhetbull/osxphotos
   brew install osxphotos
   ```

### Install the Package

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/export-photos-to-nextcloud.git
   cd export-photos-to-nextcloud
   ```

2. **Install the package**:
   ```bash
   # Basic installation
   pip install -e .

   # With development dependencies
   pip install -e ".[dev]"

   # With test dependencies
   pip install -e ".[test]"
   ```

3. **Verify installation**:
   ```bash
   # Test the package
   ./test_package.sh

   # Check console script
   export-photos-to-nextcloud --help

   # Check module execution
   python -m export_photos_to_nextcloud_pkg --help
   ```

## Usage

### Quick Start

```bash
# Basic usage with required parameters
export-photos-to-nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log

# With configuration file
export-photos-to-nextcloud --config config.yaml --dry-run -v
```

### Configuration File

Create a YAML configuration file to avoid repeating command line arguments:

```yaml
# config.yaml
export_dir: "~/PhotosExport"
nc_photos_dir: "~/Nextcloud/Photos"
log_file: "~/export-photos.log"
dry_run: false
use_symlink: true
cleanup: false
export_aae: false
verbose: 1
quiet: false
```

**Configuration Priority**: Command line arguments override configuration file values.

### Command Line Options

```
Options:
  -c, --config PATH           Path to YAML configuration file
  -e, --export-dir PATH       Export destination directory
  -n, --nc-photos-dir PATH    Nextcloud sync directory
  -l, --log-file PATH         Path to log file
  --dry-run                   Show what would happen, but don't write or link
  --no-symlink                Do not create symlinks into Nextcloud
  --use-symlink               Create symlinks into Nextcloud (default)
  --cleanup                   Do automated cleanup tasks
  --export-aae                Export AAE adjustments files
  -v, --verbose               Increase verbosity (-v, -vv, -vvv)
  -q, --quiet                 Suppress non-essential output
  --help                      Show this message and exit
  --version                   Show the version and exit
```

### Examples

**Using configuration file with overrides:**
```bash
export-photos-to-nextcloud \
    --config config.yaml \
    --dry-run --verbose
```

**Full export with all options:**
```bash
export-photos-to-nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log \
    --cleanup --export-aae --verbose
```

**Dry run for testing:**
```bash
export-photos-to-nextcloud \
    --config config.yaml \
    --dry-run -vv
```

**Module execution:**
```bash
python -m export_photos_to_nextcloud_pkg \
    --config config.yaml \
    --export-dir ~/CustomExport \
    --quiet
```

## How It Works

1. **Validates Dependencies** - Checks that osxphotos is installed and working
2. **Loads Configuration** - Merges YAML config file with command line arguments
3. **Sets Up Directories** - Creates export and Nextcloud directories as needed
4. **Exports Photos** - Uses osxphotos to export photos organized by year/month
5. **Creates Symlinks** - Links exported directories into your Nextcloud folder
6. **Generates Report** - Shows a summary of exported files and directory structure

## Directory Structure

The tool organizes photos like this:

```
PhotosExport/
├── 2023/
│   ├── 01/  # January
│   ├── 02/  # February
│   └── ...
├── 2024/
│   ├── 01/
│   └── ...

Nextcloud/Photos/
├── 2023 -> ~/PhotosExport/2023/  # Symlink
├── 2024 -> ~/PhotosExport/2024/  # Symlink
```

## Configuration File Format

The YAML configuration file supports all command line options:

```yaml
# Required settings
export_dir: "~/PhotosExport"
nc_photos_dir: "~/Nextcloud/Photos"
log_file: "~/export-photos.log"

# Optional settings
dry_run: false
use_symlink: true
cleanup: false
export_aae: false
verbose: 1
quiet: false
```

**Copy the example configuration:**
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test class
python -m pytest tests/test_export_tool_pytest.py::TestConfiguration -v

# Run comprehensive package validation
./test_package.sh
```

### Code Quality

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

## Dependencies

- **Python 3.10+** - Modern Python features and type hints
- **macOS** - Required for Photos.app access
- **osxphotos** - Apple Photos library integration
- **click** - Command line interface framework
- **loguru** - Beautiful logging
- **rich** - Rich text and progress bars
- **pyyaml** - YAML configuration file support

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
├── config.yaml.example              # Example configuration
├── pyproject.toml                    # Project configuration
├── test_package.sh                   # Comprehensive test script
├── CONTRIBUTING.md                   # Contribution guidelines
└── README.md                         # This file
```

## License

MIT License - see LICENSE file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up the development environment
- Running tests and code quality checks
- Submitting pull requests
- Code style and conventions

## Troubleshooting

### Common Issues

**osxphotos not found:**
```bash
brew tap rhetbull/osxphotos
brew install osxphotos
```

**Permission errors:**
- Ensure the export and Nextcloud directories are writable
- Run with `--dry-run` first to test permissions

**Photos.app access:**
- Grant Full Disk Access to Terminal.app in System Preferences > Security & Privacy

**Configuration file errors:**
- Check YAML syntax with `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`
- Ensure all required fields are present

### Getting Help

- **Command Help**: Run with `--help` for all available options
- **Verbose Logging**: Use `-v`, `-vv`, or `-vvv` for detailed progress information
- **Dry Run**: Use `--dry-run` to test configuration without making changes
- **Issues**: Report bugs and request features on GitHub
- **Contributing**: See CONTRIBUTING.md for development guidelines

### Version Information

```bash
# Check version
export-photos-to-nextcloud --version

# Check package info
python -c "import export_photos_to_nextcloud_pkg; print(export_photos_to_nextcloud_pkg.__version__)"
```
