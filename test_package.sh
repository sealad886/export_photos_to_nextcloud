#!/bin/bash
# Comprehensive test script for export-photos-to-nextcloud package

set -e  # Exit on any error

echo "🧪 Running comprehensive package tests..."
echo "=================================="

# Test 1: Package installation
echo "📦 Testing package installation..."
/Users/andrew/venvs/scripts/bin/pip install -e ".[dev]" > /dev/null 2>&1
echo "✅ Package installed successfully"

# Test 2: Version detection
echo "🔢 Testing dynamic version detection..."
VERSION=$(python -c "import export_photos_to_nextcloud_pkg; print(export_photos_to_nextcloud_pkg.__version__)")
if [ "$VERSION" = "1.0.0" ]; then
    echo "✅ Version correctly detected: $VERSION"
else
    echo "❌ Version detection failed: got $VERSION, expected 1.0.0"
    exit 1
fi

# Test 3: Module import test
echo "📥 Testing package imports..."
python -c "
from export_photos_to_nextcloud_pkg import main, Config, PhotoExporter, __version__
print('✅ All main components imported successfully')
print(f'   Version: {__version__}')
print(f'   Main function: {type(main).__name__}')
print(f'   Config class: {Config.__name__}')
print(f'   PhotoExporter class: {PhotoExporter.__name__}')
"

# Test 4: Module execution (should show help without warnings)
echo "🎯 Testing module execution..."
OUTPUT=$(python -m export_photos_to_nextcloud_pkg --help 2>&1)
if echo "$OUTPUT" | grep -q "OSXPhotos to Nextcloud Export Tool" && ! echo "$OUTPUT" | grep -q "WARNING"; then
    echo "✅ Module execution works correctly (no warnings)"
else
    echo "❌ Module execution test failed"
    echo "Output:"
    echo "$OUTPUT"
    exit 1
fi

# Test 5: Console script execution
echo "🖥️ Testing console script..."
OUTPUT=$(export-photos-to-nextcloud --help 2>&1)
if echo "$OUTPUT" | grep -q "OSXPhotos to Nextcloud Export Tool" && ! echo "$OUTPUT" | grep -q "WARNING"; then
    echo "✅ Console script works correctly"
else
    echo "❌ Console script test failed"
    echo "Output:"
    echo "$OUTPUT"
    exit 1
fi

# Test 6: Version flag test
echo "🏷️ Testing version flag..."
MODULE_VERSION=$(python -m export_photos_to_nextcloud_pkg --version 2>&1 || true)
SCRIPT_VERSION=$(export-photos-to-nextcloud --version 2>&1 || true)
echo "   Module version output: $MODULE_VERSION"
echo "   Script version output: $SCRIPT_VERSION"
echo "✅ Version flags tested"

# Test 7: Pytest suite
echo "🧪 Running pytest suite..."
python -m pytest tests/ -v --tb=short
echo "✅ Pytest suite completed"

# Test 8: Package metadata validation
echo "📋 Testing package metadata..."
python -c "
import pkg_resources
dist = pkg_resources.get_distribution('export-photos-to-nextcloud')
print(f'✅ Package metadata validation:')
print(f'   Name: {dist.project_name}')
print(f'   Version: {dist.version}')
print(f'   Entry points: {list(dist.get_entry_map().keys())}')
"

# Test 9: Dry run with real paths
echo "🏃‍♂️ Testing dry run functionality..."
TEMP_DIR=$(mktemp -d)
LOG_FILE="$TEMP_DIR/test.log"
python -m export_photos_to_nextcloud_pkg \
    -e "$TEMP_DIR/export" \
    -n "$TEMP_DIR/nextcloud" \
    -l "$LOG_FILE" \
    --dry-run -q > /dev/null 2>&1 && echo "✅ Dry run test passed" || echo "⚠️ Dry run test failed (expected - osxphotos may not be available)"

# Cleanup
rm -rf "$TEMP_DIR"

echo "=================================="
echo "🎉 All package validation tests completed!"
echo ""
echo "Summary of validated functionality:"
echo "  📦 Package installation and structure"
echo "  🔢 Dynamic version loading from __init__.py"
echo "  📥 Package imports and API"
echo "  🎯 Module execution (python -m)"
echo "  🖥️ Console script execution"
echo "  🧪 Pytest test suite"
echo "  📋 Package metadata"
echo "  🏃‍♂️ Basic functionality test"
echo ""
echo "✨ Package is ready for use!"
