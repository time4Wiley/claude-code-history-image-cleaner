# Claude Code History Image Cleaner

A Python script to extract and preserve base64 encoded images from Claude Code's history file (`~/.claude.json`), significantly reducing file size while preserving all images for future reference.

## Problem

Claude Code stores conversation history including pasted images as base64 encoded data in `~/.claude.json`. Over time, this file can grow very large (20+ MB), causing:

- Slow CLI startup times
- High memory usage
- Sluggish performance when accessing history

## Solution

This script identifies base64 encoded images in the history, extracts them as individual image files organized by project, and replaces the base64 data with file path references. This reduces JSON file size while preserving all images and conversation data.

## Features

- 🔍 **Smart Detection**: Identifies base64 images by data URI scheme (`data:image/`) and large base64 strings
- 🖼️ **Image Preservation**: Extracts images as individual files organized by project instead of deleting them
- 📁 **Organized Storage**: Saves images to `~/.claude/history_images/` with project-based subdirectories
- 💾 **Automatic Backup**: Creates timestamped backups before making changes
- 📊 **Detailed Reporting**: Shows exactly how much space was saved and images extracted
- 🛡️ **Safe Operation**: Preserves all conversation data and design images
- ⚡ **Significant Reduction**: Typically reduces file size by 90%+ while keeping all images accessible
- 🌐 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## Usage

### Quick Start

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

**Windows (Command Prompt):**
```cmd
# Download the script
curl -O https://raw.githubusercontent.com/time4Wiley/claude-code-history-image-cleaner/master/claude-code-history-image-cleaner.py

# Run it
python claude-code-history-image-cleaner.py
```

### Example Output

```
Found Claude config: C:\Users\YourName\.claude.json
Images will be saved to: C:\Users\YourName\.claude\history_images
Original file size: 24.9 MB
Backup saved to: C:\Users\YourName\.claude.json.backup.20250731_120432

Items cleaned: 56
Images extracted: 12
Total size removed: 23.5 MB
Cleaned .claude.json saved!
✅ 12 images preserved and extracted to files
📁 Images location: C:\Users\YourName\.claude\history_images
New file size: 1.3 MB
Size reduction: 94.8%
```

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
   - Large base64 string detection (>50KB strings with base64 characters) - **removed only**
6. **Extracts** images with data URI scheme to organized directories:
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
- **Images preserved**: All design images safely extracted to organized files

The performance improvement is immediately noticeable, especially on systems with large history files containing many pasted images.

## Testing & Development

The script includes built-in testing capabilities:

**Generate test data:**
```bash
python3 claude-code-history-image-cleaner.py --generate-test-data [test_file.json]
```

**Test with custom file:**
```bash
python3 claude-code-history-image-cleaner.py --test-file path/to/test_file.json
```

This allows you to verify functionality without affecting your real Claude config file.

## Contributing

Feel free to submit issues or pull requests if you find bugs or have improvements!

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Created to solve slow Claude Code startup times caused by accumulated base64 image data in conversation history, while preserving all design images and user content for future reference.