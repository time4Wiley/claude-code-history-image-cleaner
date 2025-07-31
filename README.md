# Claude Code History Image Cleaner

A Python script to remove base64 encoded images from Claude Code's history file (`~/.claude.json`), significantly reducing file size and improving CLI startup performance.

## Problem

Claude Code stores conversation history including pasted images as base64 encoded data in `~/.claude.json`. Over time, this file can grow very large (20+ MB), causing:

- Slow CLI startup times
- High memory usage
- Sluggish performance when accessing history

## Solution

This script identifies and removes base64 encoded images from the history while preserving all other conversation data.

## Features

- 🔍 **Smart Detection**: Identifies base64 images by data URI scheme (`data:image/`) and large base64 strings
- 💾 **Automatic Backup**: Creates timestamped backups before making changes
- 📊 **Detailed Reporting**: Shows exactly how much space was saved
- 🛡️ **Safe Operation**: Preserves all non-image history data
- ⚡ **Significant Reduction**: Typically reduces file size by 90%+ if images are present

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
Original file size: 24.9 MB
Backup saved to: C:\Users\YourName\.claude.json.backup.20250731_120432

Items cleaned: 56
Total size removed: 23.5 MB
Cleaned .claude.json saved!
New file size: 1.3 MB
Size reduction: 94.8%
```

## How It Works

1. **Finds** Claude Code config file automatically:
   - **Windows**: `%USERPROFILE%\.claude.json`, `%APPDATA%\claude\claude.json`, or `%LOCALAPPDATA%\claude\claude.json`
   - **macOS/Linux**: `~/.claude.json` or `~/.config/claude/claude.json`
2. **Creates** a timestamped backup
3. **Scans** all project history for `pastedContents`
4. **Identifies** base64 encoded images using:
   - Data URI detection (`data:image/...`)
   - Large base64 string detection (>50KB strings with base64 characters)
5. **Replaces** image data with `[IMAGE_REMOVED]` placeholder
6. **Saves** the cleaned file

## Requirements

- Python 3.6+
- Claude Code installed
- Works on Windows, macOS, and Linux
- No additional dependencies required

## Safety

- Always creates a backup before modifying
- Only removes image data, preserves all text/code
- Backup files are kept with timestamp for recovery

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

In testing, this reduced:
- File size: 24.9 MB → 1.3 MB (95% reduction)
- Improved CLI responsiveness
- Reduced memory usage

## Contributing

Feel free to submit issues or pull requests if you find bugs or have improvements!

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Created to solve slow Claude Code startup times caused by accumulated base64 image data in conversation history.