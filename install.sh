#!/bin/bash

# Claude Code History Image Cleaner - Global Installation Script
# This script installs the image cleaner as a global CLI tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_FILE="$SCRIPT_DIR/claude-code-history-image-cleaner.py"
TARGET_NAME="claude-image-cleaner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if script exists
if [ ! -f "$SCRIPT_FILE" ]; then
    print_error "Script file not found: $SCRIPT_FILE"
    exit 1
fi

# Make script executable
chmod +x "$SCRIPT_FILE"
print_status "Made script executable"

# Determine installation location
if [ -w "/usr/local/bin" ]; then
    INSTALL_DIR="/usr/local/bin"
elif [ -d "$HOME/.local/bin" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "$HOME/.local/bin is not in your PATH"
        echo "Add this line to your shell profile (.bashrc, .zshrc, etc.):"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
else
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    INSTALL_DIR="$HOME/.local/bin"
    print_status "Created $HOME/.local/bin directory"
    print_warning "Add this line to your shell profile (.bashrc, .zshrc, etc.):"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

TARGET_PATH="$INSTALL_DIR/$TARGET_NAME"

# Check if already installed
if [ -f "$TARGET_PATH" ] || [ -L "$TARGET_PATH" ]; then
    print_warning "Found existing installation at $TARGET_PATH"
    read -p "Do you want to overwrite it? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
    rm -f "$TARGET_PATH"
fi

# Create symlink
ln -sf "$SCRIPT_FILE" "$TARGET_PATH"
print_success "Installed as $TARGET_PATH"

# Verify installation
if [ -x "$TARGET_PATH" ]; then
    print_success "Installation successful!"
    echo
    print_status "You can now use the following commands:"
    echo "  $TARGET_NAME                          # Clean current Claude config"
    echo "  $TARGET_NAME --list-backups           # List available backup files"
    echo "  $TARGET_NAME --recover-from-backup    # Recover images from backup (coming soon)"
    echo "  $TARGET_NAME --help                   # Show all options"
    echo
    
    # Test the installation
    if command -v "$TARGET_NAME" >/dev/null 2>&1; then
        print_success "✅ '$TARGET_NAME' is available in your PATH"
    else
        print_warning "⚠️  '$TARGET_NAME' is not in your PATH. You may need to:"
        echo "1. Restart your terminal, or"
        echo "2. Add $INSTALL_DIR to your PATH"
    fi
else
    print_error "Installation failed - script is not executable"
    exit 1
fi

echo
print_status "To uninstall, run: rm $TARGET_PATH"