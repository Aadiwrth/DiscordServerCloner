#!/usr/bin/env bash
# Build script for Discord Server Cloner (Linux)

set -e  # Exit immediately if a command fails

APP_NAME="Discord Server Cloner"
APP_VERSION="2.0.0"
MAIN_SCRIPT="main.py"
OUTPUT_DIR="dist"
BUILD_DIR="build"
ICON_PATH="src/interface/assets/discord_logo.png"

# Ensure virtualenv Python
PYTHON_BIN="${VIRTUAL_ENV}/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "=== Building $APP_NAME v$APP_VERSION (Linux) ==="

# Remove obsolete typing package if exists
"$PYTHON_BIN" -m pip uninstall -y typing || true

# Make sure tk and pillow are installed
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --upgrade pillow tk pyinstaller

# Clean pycache
find . -name "__pycache__" -type d -exec rm -rf {} +

# Clean build and dist directories
rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Run PyInstaller
pyinstaller \
    --name "$APP_NAME" \
    --onefile \
    --windowed \
    --icon "$ICON_PATH" \
    --clean \
    --noconfirm \
    --log-level=INFO \
    --add-data "src/interface/assets:src/interface/assets" \
    --add-data "src/interface/language:src/interface/language" \
    --hidden-import "PIL._tkinter_finder" \
    "$MAIN_SCRIPT"

# Verify build success
if [ $? -ne 0 ]; then
    echo "PyInstaller build failed."
    exit 1
fi

# Prepare zip
DIST_PATH="$OUTPUT_DIR/$APP_NAME"
if [ ! -d "$DIST_PATH" ]; then
    DIST_PATH="$OUTPUT_DIR"
fi


EXTRA_FILES="src/interface/assets src/interface/language"

# Create zip
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="${APP_NAME// /_}_${APP_VERSION}_${TIMESTAMP}_linux"
zip -r "$ZIP_NAME.zip" "$DIST_PATH" $EXTRA_FILES

echo "Created distribution package: $ZIP_NAME.zip"
echo "=== Build completed successfully ==="
