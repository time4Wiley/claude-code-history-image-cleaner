# Claude Code History Image Cleaner

[![PyPI version](https://badge.fury.io/py/claude-code-history-image-cleaner.svg)](https://badge.fury.io/py/claude-code-history-image-cleaner)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/time4Wiley/claude-code-history-image-cleaner)

A sophisticated Python tool to extract and preserve base64 encoded images from Claude Code's history file (`~/.claude.json`), dramatically reducing file size while preserving all images for future reference. Features advanced data recovery capabilities to restore lost images from backups.

## 🚀 Quick Start

```bash
# Install globally (recommended)
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/install.sh
chmod +x install.sh && ./install.sh

# Use from anywhere
claude-image-cleaner                         # Clean and extract images
claude-image-cleaner --recover-from-backup  # Recover lost images from backup
```

## 📋 Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Recovery System](#data-recovery-system)
- [How It Works](#how-it-works)
- [Performance Impact](#performance-impact)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Problem

Claude Code stores conversation history including pasted images as base64 encoded data in `~/.claude.json`. Over time, this file can grow very large (20+ MB), causing:

- Slow CLI startup times
- High memory usage
- Sluggish performance when accessing history

## Solution

This script identifies base64 encoded images in the history, extracts them as individual image files organized by project, and replaces the base64 data with file path references. This reduces JSON file size while preserving all images and conversation data.

## Features

- 🔍 **Smart Detection**: Identifies base64 images by data URI scheme (`data:image/`) and raw base64 with magic number detection
- 🖼️ **Image Preservation**: Extracts images as individual files organized by project instead of deleting them
- 🔧 **Raw Base64 Recovery**: Detects and recovers pasted images on macOS using magic number identification (PNG, JPEG, GIF, WebP, BMP, SVG)
- 📁 **Organized Storage**: Saves images to `~/.claude/history_images/` with project-based subdirectories
- 🌍 **Global CLI Access**: Install once and use from anywhere with the `claude-image-cleaner` command
- 🔄 **Data Recovery System**: Sophisticated backup processing to recover lost images and merge with current changes
- 💾 **Automatic Backup**: Creates timestamped backups before making changes
- 📊 **Detailed Reporting**: Shows exactly how much space was saved and images extracted
- 🛡️ **Safe Operation**: Preserves all conversation data and design images
- ⚡ **Significant Reduction**: Typically reduces file size by 90%+ while keeping all images accessible
- 🌐 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## Installation

### Quick Installation (Recommended)

**macOS/Linux:**
```bash
# Download and install globally
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/claude-code-history-image-cleaner.py
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/install.sh
chmod +x install.sh
./install.sh

# Now use from anywhere
claude-image-cleaner
```

### Alternative: PyPI Installation

For users who prefer pip package management:

```bash
# Install from PyPI
pip install claude-code-history-image-cleaner

# Or with uv (modern Python package manager)
uv add claude-code-history-image-cleaner

# Use the same way
claude-image-cleaner --help
```

### Manual Installation

**macOS/Linux:**
```bash
# Download the script
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/claude-code-history-image-cleaner.py

# Make it executable
chmod +x claude-code-history-image-cleaner.py

# Run it
python3 claude-code-history-image-cleaner.py
```

**Windows (PowerShell):**
```powershell
# Download the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/claude-code-history-image-cleaner.py" -OutFile "claude-code-history-image-cleaner.py"

# Run it
python claude-code-history-image-cleaner.py
```

## Usage

### Basic Commands

```bash
# Clean current Claude config and extract images
claude-image-cleaner

# List available backup files
claude-image-cleaner --list-backups

# Recover images from backup and merge with current changes
claude-image-cleaner --recover-from-backup

# Use specific backup file
claude-image-cleaner --recover-from-backup ~/.claude.json.backup.2025-07-31

# Show all options
claude-image-cleaner --help
```

### Example Output

**Regular Cleaning:**
```
Found Claude config: /Users/you/.claude.json
Images will be saved to: /Users/you/.claude/history_images
Original file size: 24.9 MB
Backup saved to: /Users/you/.claude.json.backup.20250801_120432

Items cleaned: 56
Images extracted: 56
Total size removed: 23.5 MB
Cleaned .claude.json saved!
✅ 56 images preserved and extracted to files
📁 Images location: /Users/you/.claude/history_images
New file size: 1.3 MB
Size reduction: 94.8%
```

**Data Recovery:**
```
🔍 Auto-detected backup file: .claude.json.backup.2025-07-31 (24.8 MB)
🚀 Starting data recovery process...
   Backup file: /Users/you/.claude.json.backup.2025-07-31 (24.8 MB)
   Current file: /Users/you/.claude.json (1.3 MB)
📖 Loading data files...
🔄 Creating destructive version of backup data...
   Destructively removed 56 images
🔍 Analyzing differences between current and backup data...
   Found new project: /Users/you/Projects/new-project
   Found 6 new history items in /Users/you/temp/existing-project
🖼️ Processing backup with image preservation...
✓ Extracted 56 images from backup
🔀 Merging backup images with current changes...
   Added new project: /Users/you/Projects/new-project
   Added 6 new history items to /Users/you/temp/existing-project
💾 Current file backed up to: /Users/you/.claude.json.recovery-backup.20250801_154825

✅ Data recovery completed successfully!
   Images recovered: 56
   New projects added: 1
   Projects with new history: 1
   Final file size: 1.3 MB
   Images location: /Users/you/.claude/history_images
```

## Data Recovery System

The tool includes a sophisticated data recovery system to solve the data loss issue where images were replaced with `[IMAGE_REMOVED]` placeholders but no image files were extracted.

### How Data Recovery Works

1. **Backup Analysis**: Processes your large backup file (containing original images)
2. **Delta Detection**: Compares current config with what the backup would look like after destructive cleaning
3. **Change Identification**: Finds new projects and conversations added since the backup
4. **Image Extraction**: Recovers all images from backup using the lossless preservation system
5. **Smart Merging**: Combines extracted images with new conversations to create a complete, up-to-date config

### Use Cases

- **Lost Images**: Your current config has `[IMAGE_REMOVED]` but you have a backup with original images
- **Partial Recovery**: You want to recover old images while keeping new conversations
- **Migration**: Moving from destructive to preservation-based image handling

### Safety Features

- Creates recovery backup before making changes
- Auto-detects suitable backup files
- Preserves all conversation data and new projects
- Never overwrites without backing up first

## How It Works

1. **Finds** Claude Code config file automatically:
   - **Windows**: `%USERPROFILE%\.claude.json`, `%APPDATA%\claude\claude.json`, or `%LOCALAPPDATA%\claude\claude.json`
   - **macOS/Linux**: `~/.claude.json` or `~/.config/claude/claude.json`
2. **Sets up** images directory structure:
   - **Windows**: `%USERPROFILE%\.claude\history_images\`
   - **macOS/Linux**: `~/.claude/history_images/`
3. **Creates** a timestamped backup
4. **Scans** all project history for `pastedContents`
5. **Identifies** base64 encoded images using:
   - Data URI detection (`data:image/...`) - **extractable as files**
   - Raw base64 detection using magic number identification (PNG, JPEG, GIF, WebP, BMP, SVG) - **extractable as files**
   - Large base64 string detection (>50KB strings with base64 characters) - **removed if unidentifiable**
6. **Extracts** images (both data URI and raw base64) to organized directories:
   - `~/.claude/history_images/project_name_hash/timestamp/image_001.png`
7. **Replaces** image data with file path references: `[IMAGE_FILE:/path/to/image.png]`
8. **Saves** the cleaned file with preserved images

## Requirements

- Python 3.6+
- Claude Code installed
- Works on Windows, macOS, and Linux
- No additional dependencies required

## Extracted Images Structure

When images are extracted, they're organized in a clear directory structure:

```
~/.claude/history_images/
├── project1_a1b2c3d4/
│   └── 20250731_143022/
│       ├── image_001.png
│       ├── image_002.jpg
│       └── image_003.gif
├── project2_e5f6g7h8/
│   └── 20250731_143022/
│       ├── image_004.png
│       └── image_005.jpg
└── unknown_12345678/
    └── 20250731_143022/
        └── image_006.png
```

- **Project folders**: Named using project path + hash for uniqueness
- **Session timestamps**: Each run creates a timestamped subdirectory
- **Sequential naming**: Images numbered sequentially across all projects
- **Proper extensions**: File extensions match image format (.png, .jpg, .gif, etc.)

## Safety

- Always creates a backup before modifying
- **Preserves all images**: Extracts to organized files instead of deleting
- **Zero data loss**: All conversation text/code and design images are retained
- Backup files are kept with timestamp for recovery
- **Rollback friendly**: Can restore original file or re-extract images if needed

## When to Use

Run this script when:
- Claude Code startup feels slow
- Your Claude config file is larger than 5MB
- You've pasted many images/screenshots in Claude conversations

## Restoring from Backup

If needed, restore your original history:

**macOS/Linux:**
```bash
# List backups
ls -la ~/.claude.json.backup.*

# Restore a specific backup
cp ~/.claude.json.backup.20250731_120432 ~/.claude.json
```

**Windows (PowerShell):**
```powershell
# List backups
Get-ChildItem $env:USERPROFILE\.claude.json.backup.*

# Restore a specific backup
Copy-Item "$env:USERPROFILE\.claude.json.backup.20250731_120432" "$env:USERPROFILE\.claude.json"
```

**Windows (Command Prompt):**
```cmd
# List backups
dir %USERPROFILE%\.claude.json.backup.*

# Restore a specific backup
copy "%USERPROFILE%\.claude.json.backup.20250731_120432" "%USERPROFILE%\.claude.json"
```

## Performance Impact

**Real-world test results (2021 M1 Pro MacBook Pro):**
- **File size**: 24.9 MB → 1.3 MB (95% reduction)
- **Claude Code startup time**: 6 seconds → 2-3 seconds (50%+ faster)
- **CLI responsiveness**: Significantly improved
- **Memory usage**: Substantially reduced
- **Images recovered**: All 56 images (including pasted screenshots) successfully extracted and organized
- **Raw base64 detection**: 100% success rate on macOS pasted images using magic number identification

The performance improvement is immediately noticeable, especially on systems with large history files containing many pasted images. The enhanced raw base64 detection ensures that even clipboard-pasted images (which don't use data URI format) are properly recovered and preserved.

## Global CLI Installation

The tool can be installed globally for convenient access from anywhere on your system:

**Installation:**
```bash
# Download installation script
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/install.sh
chmod +x install.sh

# Install globally (creates symlink in /usr/local/bin or ~/.local/bin)
./install.sh
```

**Uninstallation:**
```bash
# Remove the global command
rm /usr/local/bin/claude-image-cleaner  # or ~/.local/bin/claude-image-cleaner
```

The installer automatically detects the best installation location and provides helpful guidance for PATH configuration if needed.

## Architecture

The tool is built with a modular architecture focused on safety and extensibility:

### Core Components

- **Image Detection Engine**: Multi-layer detection using data URI parsing and magic number analysis
- **Format Identification**: Binary header analysis for PNG, JPEG, GIF, WebP, BMP, SVG formats
- **Delta Comparison System**: Sophisticated diffing to identify changes between backup and current state
- **Smart Merging Engine**: Combines recovered images with current conversations while preserving data integrity
- **Project Organization**: Hash-based directory naming for consistent, collision-free storage

### Technical Highlights

- **Magic Number Detection**: Identifies raw base64 images by analyzing binary headers
- **Cross-Platform Path Handling**: Automatic Windows/macOS/Linux config file detection
- **Atomic Operations**: All modifications are backed up before execution
- **Memory Efficient**: Processes large files without loading entire dataset into memory
- **Error Recovery**: Comprehensive backup and rollback capabilities

### Data Flow

1. **Discovery** → Locate Claude config files across platforms
2. **Analysis** → Scan for base64 image data using multiple detection methods
3. **Extraction** → Convert base64 to binary and save with proper file extensions
4. **Organization** → Store in project-specific directories with timestamps
5. **Replacement** → Update JSON with file path references
6. **Verification** → Confirm successful extraction and file integrity

## Troubleshooting

### Common Issues

**"No backup files found"**
```bash
# Check if backup files exist
ls -la ~/.claude.json.backup.*

# Create manual backup if needed
cp ~/.claude.json ~/.claude.json.backup.$(date +%Y%m%d_%H%M%S)
```

**"Command not found: claude-image-cleaner"**
```bash
# Check if PATH includes installation directory
echo $PATH | grep -E "(usr/local/bin|\.local/bin)"

# Add to PATH if missing (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

**"Permission denied" during installation**
```bash
# Use manual installation instead
python3 claude-code-history-image-cleaner.py
```

**Large file processing is slow**
- This is normal for files >20MB with many images
- Progress is shown for each extracted image
- Consider running during off-peak hours

### Recovery Scenarios

**Lost original backup file**
```bash
# List all backup files with sizes
claude-image-cleaner --list-backups

# Use the largest backup (likely contains images)
claude-image-cleaner --recover-from-backup /path/to/largest-backup
```

**Images not extracting**
- Verify file contains base64 image data
- Check disk space in `~/.claude/history_images/`
- Run with `--verbose` flag for detailed logging

**Merge conflicts during recovery**
- Tool automatically preserves both backup images and current conversations
- Creates recovery backup before any changes
- Safe to run multiple times if needed

### Performance Optimization

**For very large files (>50MB)**
- Close Claude Code before running
- Ensure sufficient disk space (roughly same size as original file)
- Consider running in background: `nohup claude-image-cleaner &`

**For frequent use**
- Set up periodic cleaning with `cron` (Linux/macOS) or Task Scheduler (Windows)
- Monitor file size: `ls -lh ~/.claude.json`

## Contributing

Feel free to submit issues or pull requests if you find bugs or have improvements!

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Created to solve slow Claude Code startup times caused by accumulated base64 image data in conversation history, while preserving all design images and user content for future reference.