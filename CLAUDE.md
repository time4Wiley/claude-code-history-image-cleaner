# Claude Code History Image Cleaner - Development Guide

This document provides comprehensive guidance for Claude AI when working on the Claude Code History Image Cleaner project.

## Project Overview

The Claude Code History Image Cleaner is a sophisticated Python tool designed to solve a critical performance issue with Claude Code CLI: the accumulation of base64 encoded images in the `~/.claude.json` history file causes slow startup times and high memory usage.

### Core Mission

1. **Performance Optimization**: Reduce Claude Code startup time from 6+ seconds to 2-3 seconds
2. **Image Preservation**: Extract and organize all images instead of destructive deletion
3. **Data Recovery**: Provide sophisticated backup processing to recover lost images
4. **Zero Data Loss**: Ensure no conversation content or images are ever lost

## Architecture & Design Principles

### Key Design Decisions

1. **Preservation over Destruction**: Early versions deleted images; current version extracts and organizes them
2. **Magic Number Detection**: Added to handle raw base64 images (common on macOS clipboard pastes)
3. **Delta Comparison**: Sophisticated diffing system to merge backup images with current conversations
4. **Atomic Operations**: All operations are backed up before execution
5. **Cross-Platform Support**: Windows, macOS, and Linux compatibility from day one

### Code Organization

```
claude-code-history-image-cleaner.py
├── Platform Detection (find_claude_config)
├── Image Detection Engine
│   ├── Data URI parsing (parse_data_uri)
│   ├── Magic number detection (detect_image_format_from_binary)
│   └── Base64 analysis (detect_image_format_from_base64)
├── File Organization (create_project_directory)
├── Image Extraction (extract_image_to_file)
├── Data Cleaning
│   ├── Lossless cleaning (clean_object)
│   └── Destructive cleaning (clean_object_destructive)
├── Data Recovery System
│   ├── Delta detection (find_differences)
│   ├── Backup processing (create_destructive_version)
│   └── Smart merging (merge_data_with_images)
└── CLI Interface (argparse + main)
```

### Core Components

#### 1. Image Detection Engine
- **Multi-layered approach**: Data URI → Magic numbers → Size heuristics
- **Format support**: PNG, JPEG, GIF, WebP, BMP, SVG
- **Raw base64 handling**: Critical for macOS clipboard images

#### 2. Delta Comparison System
- **Purpose**: Merge backup images with current conversations
- **Process**: Create destructive version → Compare → Identify changes
- **Safety**: Always backup before merging

#### 3. Project Organization
- **Hash-based naming**: Prevents collisions, ensures uniqueness
- **Timestamp subdirectories**: Multiple runs don't overwrite
- **Sequential numbering**: Clear image organization

## Development Guidelines

### Code Style & Patterns

1. **Function Naming**: Descriptive, action-oriented (`extract_image_to_file`, `find_differences`)
2. **Error Handling**: Graceful degradation with informative messages
3. **Progress Reporting**: User feedback for long-running operations
4. **Safety First**: Always backup before destructive operations

### Key Implementation Patterns

#### Magic Number Detection
```python
# Always check sufficient bytes before magic number analysis
if len(binary_data) < 12:
    return None, None

# Use specific, reliable signatures
if binary_data.startswith(b'\x89PNG\r\n\x1a\n'):
    return 'png', '.png'
```

#### Safe File Operations
```python
# Always create backup before modification
backup_path = f"{claude_json_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w') as f:
    json.dump(data, f)
```

#### Cross-Platform Paths
```python
# Use os.path.join for all path operations
if platform.system() == "Windows":
    userprofile = os.environ.get('USERPROFILE', '')
    return os.path.join(userprofile, '.claude', 'history_images')
```

### Testing Strategy

#### Manual Testing Approach
- **Real data testing**: Always test with actual Claude config files
- **Cross-platform verification**: Test on Windows, macOS, Linux
- **Size validation**: Verify significant file size reduction
- **Image integrity**: Ensure extracted images are viewable

#### Edge Cases to Test
- Empty config files
- Config files with no images
- Very large files (>50MB)
- Corrupted base64 data
- Non-standard image formats
- Mixed data URI and raw base64

### Security Considerations

#### Safe Operations
- **Input validation**: Check file existence and permissions
- **Path sanitization**: Prevent directory traversal attacks
- **Backup verification**: Ensure backups are created successfully
- **Error boundaries**: Fail safely without corrupting data

#### Data Privacy
- **Local processing only**: Never upload data to external services
- **No logging of sensitive data**: Avoid logging file contents
- **Cleanup on failure**: Remove partial extractions on error

## Common Development Tasks

### Adding New Image Format Support

1. **Add magic number detection**:
   ```python
   # In detect_image_format_from_binary()
   if binary_data.startswith(b'\x42\x4D'):  # BMP signature
       return 'bmp', '.bmp'
   ```

2. **Update file extension mapping**:
   ```python
   # In get_file_extension()
   extensions = {
       'bmp': '.bmp',  # Add new format
   }
   ```

3. **Test with real files**: Ensure detection works with actual images

### Improving Performance

1. **Profile memory usage**: Monitor memory consumption with large files
2. **Optimize JSON parsing**: Consider streaming for very large files
3. **Batch operations**: Group file I/O operations when possible
4. **Progress reporting**: Add progress bars for long operations

### Enhancing Error Handling

1. **Specific error messages**: Tell users exactly what went wrong
2. **Recovery suggestions**: Provide actionable next steps
3. **Graceful degradation**: Continue processing other images if one fails
4. **Detailed logging**: Use verbose mode for debugging

## Advanced Features

### Data Recovery System

The data recovery system is the most sophisticated component:

1. **Backup Analysis**: Parse large backup files containing original images
2. **Destructive Simulation**: Create what backup would look like after old cleaning
3. **Delta Detection**: Compare current state with simulated destructive backup
4. **Smart Merging**: Combine backup images with current conversations
5. **Safety Validation**: Verify merge integrity before saving

### CLI Design Philosophy

- **Progressive disclosure**: Basic commands are simple, advanced features are available
- **Auto-detection**: Minimize required parameters
- **Safety by default**: Always backup, never overwrite without warning
- **Clear feedback**: Users always know what's happening

## Deployment & Distribution

### Installation Strategy
- **Global CLI**: Symlink approach for system-wide access
- **Zero dependencies**: Uses only Python standard library
- **Cross-platform installer**: Shell script with Windows considerations

### Release Process
1. **Test thoroughly**: Real-world testing with large files
2. **Update documentation**: Ensure README reflects all features
3. **Version tagging**: Use semantic versioning
4. **GitHub releases**: Include installation instructions

## Troubleshooting Guide

### Common Issues
- **Permission errors**: Guide users to manual installation
- **Path issues**: Provide PATH configuration help
- **Large file hangs**: Explain normal processing time
- **Missing backups**: Help users locate suitable backup files

### Debug Information to Collect
- Platform and Python version
- File sizes (original, backup, final)
- Error messages with full context
- Directory permissions
- Available disk space

## Future Enhancements

### Potential Improvements
1. **Progress bars**: Visual feedback for long operations
2. **Configuration file**: User-customizable settings
3. **Image compression**: Reduce extracted image sizes
4. **Batch processing**: Handle multiple config files
5. **Web UI**: Browser-based interface for non-technical users

### Architectural Considerations
- **Plugin system**: Extensible image format support
- **Database storage**: SQLite for complex query needs
- **Cloud backup**: Optional cloud storage integration
- **Multi-user support**: Enterprise deployment considerations

## Maintenance

### Regular Tasks
- **Test with new Claude Code versions**: Ensure compatibility
- **Monitor GitHub issues**: Respond to user reports
- **Update documentation**: Keep README current
- **Security reviews**: Check for vulnerabilities

### Version Compatibility
- **Python versions**: Maintain 3.6+ compatibility
- **Claude Code changes**: Adapt to config format changes
- **OS updates**: Test on new platform versions

## Key Success Metrics

- **Performance improvement**: Measure Claude Code startup time reduction
- **Image recovery rate**: Percentage of images successfully extracted
- **User adoption**: GitHub stars, issues, usage reports
- **Zero data loss**: No reports of conversation or image loss
- **Cross-platform success**: Working reports from all supported platforms

## Remember

This tool handles user's valuable conversation history and images. **Safety and data preservation are paramount**. When in doubt, always err on the side of caution, create backups, and provide clear user feedback about what operations are being performed.