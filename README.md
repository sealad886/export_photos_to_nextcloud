# Export Photos to Nextcloud

A modern Python tool for exporting photos from Apple Photos.app and syncing them to Nextcloud with beautiful progress tracking and robust logging.

## Features

- 🚀 **Modern Python CLI** - Built with Click, Rich, and Loguru for beautiful terminal output
- 📸 **OSXPhotos Integration** - Leverages the powerful osxphotos library for photo export
- 🔗 **Smart Symlink Management** - Automatically creates organized symlinks in your Nextcloud directory
- 📊 **Progress Tracking** - Rich progress bars and detailed logging
- 🏃‍♂️ **Dry Run Mode** - Test your configuration before making changes
- 🎨 **AAE Support** - Export Apple adjustment files for edited photos
- 🧹 **Cleanup Options** - Automated photo organization and metadata cleanup
- ⚡ **Fast & Reliable** - Optimized for performance with retry logic and robust error handling

## Installation

### Prerequisites

1. **macOS** - This tool only works on macOS with access to Photos.app
2. **osxphotos** - Install via Homebrew:
   ```bash
   brew tap rhetbull/osxphotos
   brew install osxphotos
   ```

### Install the Module

1. Clone or download this repository
2. Install in development mode:
   ```bash
   cd export_photos_to_nextcloud
   pip install -e .
   ```

Or install with development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
python -m export_photos_to_nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log
```

### Command Line Options

```
Options:
  -e, --export-dir PATH       Export destination directory [required]
  -n, --nc-photos-dir PATH    Nextcloud sync directory [required]
  -l, --log-file PATH         Path to log file [required]
  --dry-run                   Show what would happen, but don't write or link
  --no-symlink                Do not create symlinks into Nextcloud
  -c, --cleanup               Do automated cleanup tasks
  --export-aae                Export AAE adjustments files
  -v, --verbose               Increase verbosity (-v, -vv, -vvv)
  -q, --quiet                 Suppress non-essential output
  --help                      Show this message and exit
  --version                   Show the version and exit
```

### Examples

**Dry run with verbose output:**
```bash
python -m export_photos_to_nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log \
    --dry-run -v
```

**Full export with cleanup and AAE files:**
```bash
python -m export_photos_to_nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log \
    --cleanup --export-aae
```

**Quiet mode with no symlinks:**
```bash
python -m export_photos_to_nextcloud \
    --export-dir ~/PhotosExport \
    --nc-photos-dir ~/Nextcloud/Photos \
    --log-file ~/sync.log \
    --no-symlink --quiet
```

## How It Works

1. **Validates Dependencies** - Checks that osxphotos is installed and working
2. **Sets Up Directories** - Creates export and Nextcloud directories as needed
3. **Exports Photos** - Uses osxphotos to export photos organized by year/month
4. **Creates Symlinks** - Links exported directories into your Nextcloud folder
5. **Generates Report** - Shows a summary of exported files and directory structure

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

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test class
python -m pytest test_export_tool_pytest.py::TestDryRunFunctionality -v

# Run tests excluding slow ones
python -m pytest -m "not slow"
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
mypy export_photos_to_nextcloud/
```

## Requirements

- Python 3.8+
- macOS (for Photos.app access)
- osxphotos
- click
- loguru
- rich

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest`
5. Submit a pull request

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

### Getting Help

Run with `--help` for command line options, or use `-v` for verbose logging to see detailed progress information.
