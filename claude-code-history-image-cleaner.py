#!/usr/bin/env python3
"""
Extract and preserve base64 encoded images from Claude CLI history (~/.claude.json)

This script extracts base64 encoded images from the Claude CLI history file,
saves them as individual image files organized by project, and replaces the 
base64 data with file path references. This reduces JSON file size while 
preserving all images for future reference.
"""

import json
import os
import sys
import platform
import base64
import hashlib
import re
from datetime import datetime
import copy
import tempfile

def find_claude_config():
    """Find Claude Code config file across different platforms"""
    possible_paths = []
    
    if platform.system() == "Windows":
        # Windows paths
        userprofile = os.environ.get('USERPROFILE', '')
        appdata = os.environ.get('APPDATA', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        
        possible_paths = [
            os.path.join(userprofile, '.claude.json'),
            os.path.join(appdata, 'claude', 'claude.json'),
            os.path.join(localappdata, 'claude', 'claude.json'),
        ]
    else:
        # Unix/macOS paths
        home = os.path.expanduser('~')
        possible_paths = [
            os.path.join(home, '.claude.json'),
            os.path.join(home, '.config', 'claude', 'claude.json'),
        ]
    
    # Find the first existing file
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If no file found, return the most likely default
    return possible_paths[0] if possible_paths else None

def get_images_directory():
    """Get the cross-platform images directory path"""
    if platform.system() == "Windows":
        userprofile = os.environ.get('USERPROFILE', '')
        return os.path.join(userprofile, '.claude', 'history_images')
    else:
        home = os.path.expanduser('~')
        return os.path.join(home, '.claude', 'history_images')

def create_project_directory(images_base_dir, project_path):
    """Create and return project-specific directory for images"""
    # Create a hash of the project path for consistent directory naming
    project_hash = hashlib.md5(project_path.encode('utf-8')).hexdigest()[:8]
    
    # Use project name if available, otherwise use hash
    project_name = os.path.basename(project_path) if project_path else 'unknown'
    project_dir_name = f"{project_name}_{project_hash}"
    
    # Create session directory with timestamp
    session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_dir = os.path.join(images_base_dir, project_dir_name, session_timestamp)
    
    os.makedirs(project_dir, exist_ok=True)
    return project_dir

def parse_data_uri(data_uri):
    """Parse data URI and return mime type and base64 data"""
    # Match pattern: data:image/TYPE;base64,DATA
    match = re.match(r'data:image/([^;]+);base64,(.+)', data_uri)
    if not match:
        return None, None
    
    mime_type = match.group(1).lower()
    base64_data = match.group(2)
    return mime_type, base64_data

def get_file_extension(mime_type):
    """Get file extension from MIME type"""
    extensions = {
        'png': '.png',
        'jpeg': '.jpg',
        'jpg': '.jpg', 
        'gif': '.gif',
        'webp': '.webp',
        'bmp': '.bmp',
        'svg+xml': '.svg'
    }
    return extensions.get(mime_type, '.png')  # Default to .png

def extract_image_to_file(data_string, output_dir, image_counter):
    """Extract base64 image from data URI or raw base64 string and save to file"""
    try:
        mime_type = None
        base64_data = None
        
        # Handle data URI format
        if data_string.startswith('data:image/'):
            mime_type, base64_data = parse_data_uri(data_string)
            if not mime_type or not base64_data:
                return None
        else:
            # Handle raw base64 string - detect format from binary data
            base64_data = data_string.strip()
            detected_format, file_ext = detect_image_format_from_base64(base64_data)
            if detected_format:
                mime_type = detected_format
            else:
                print(f"Warning: Could not detect image format from base64 data")
                return None
        
        # Decode base64 data
        # Remove any whitespace/newlines from base64 data
        clean_b64 = ''.join(base64_data.split())
        
        # Add padding if necessary
        missing_padding = len(clean_b64) % 4
        if missing_padding:
            clean_b64 += '=' * (4 - missing_padding)
        
        image_data = base64.b64decode(clean_b64)
        
        # Generate filename with proper extension
        if data_string.startswith('data:image/'):
            file_extension = get_file_extension(mime_type)
        else:
            # For raw base64, detect format again to get extension
            detected_format, file_extension = detect_image_format_from_binary(image_data)
            if not file_extension:
                file_extension = '.png'  # Default fallback
        
        filename = f"image_{image_counter:03d}{file_extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Write image file
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f"✓ Extracted {len(image_data)} bytes to {filename}")
        return filepath
        
    except Exception as e:
        print(f"Warning: Failed to extract image: {e}")
        return None

def is_base64_image(s):
    """Check if a string is likely a base64 encoded image"""
    if not isinstance(s, str):
        return False
    
    # Check for data URI scheme (this is extractable)
    if s.startswith('data:image/'):
        return True
    
    # Check if it's a very long string that could be base64 (but not extractable without proper URI)
    if len(s) > 50000:  # Images are typically very large
        # Sample the string to check if it's base64-like
        sample = s[:1000]
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        if all(c in base64_chars or c in '\n\r' for c in sample):
            return True
    
    return False

def detect_image_format_from_binary(binary_data):
    """Detect image format from binary data using magic numbers"""
    if len(binary_data) < 12:  # Need at least 12 bytes for WebP detection
        return None, None
    
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if binary_data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png', '.png'
    
    # JPEG: FF D8 FF
    if binary_data.startswith(b'\xff\xd8\xff'):
        return 'jpeg', '.jpg'
    
    # GIF: 47 49 46 38 (GIF8)
    if binary_data.startswith(b'GIF8'):
        return 'gif', '.gif'
    
    # WebP: 52 49 46 46 .... 57 45 42 50 (RIFF....WEBP)
    if binary_data.startswith(b'RIFF') and b'WEBP' in binary_data[:12]:
        return 'webp', '.webp'
    
    # BMP: 42 4D (BM)
    if binary_data.startswith(b'BM'):
        return 'bmp', '.bmp'
    
    # SVG (text-based, check for XML + svg)
    try:
        text_start = binary_data[:200].decode('utf-8', errors='ignore').lower()
        if '<svg' in text_start and ('xml' in text_start or '<?xml' in text_start):
            return 'svg+xml', '.svg'
    except:
        pass
    
    return None, None

def detect_image_format_from_base64(base64_string):
    """Detect image format from base64 string by decoding and checking headers"""
    try:
        # Remove whitespace and newlines
        clean_b64 = ''.join(base64_string.split())
        
        # Decode first part to check magic numbers
        # We only need the first ~50 bytes to detect format
        partial_b64 = clean_b64[:100]  # ~75 bytes when decoded
        
        # Pad if necessary
        missing_padding = len(partial_b64) % 4
        if missing_padding:
            partial_b64 += '=' * (4 - missing_padding)
        
        binary_data = base64.b64decode(partial_b64)
        return detect_image_format_from_binary(binary_data)
        
    except Exception as e:
        return None, None

def is_extractable_image(s):
    """Check if a string is a data URI or raw base64 that can be extracted as an image"""
    if not isinstance(s, str):
        return False
    
    # Check for data URI scheme (this is definitely extractable)
    if s.startswith('data:image/'):
        return True
    
    # For large base64-like strings, try to detect image format
    if len(s) > 50000:  # Images are typically very large
        # Sample the string to check if it's base64-like
        sample = s[:1000]
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        if all(c in base64_chars or c in '\n\r \t' for c in sample):
            # Try to detect image format from the base64 data
            format_type, _ = detect_image_format_from_base64(s)
            return format_type is not None
    
    return False

def clean_object(obj, stats, project_dir=None, preserve_images=True):
    """Recursively clean base64 images from an object"""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if is_base64_image(v):
                stats['total_removed_size'] += len(v)
                stats['items_cleaned'] += 1
                
                if preserve_images and project_dir and is_extractable_image(v):
                    # Extract image to file (only for data URIs)
                    filepath = extract_image_to_file(v, project_dir, stats['items_cleaned'])
                    if filepath:
                        # Replace with file path reference
                        cleaned[k] = f'[IMAGE_FILE:{filepath}]'
                        stats['images_extracted'] += 1
                    else:
                        # Fallback to old behavior if extraction fails
                        cleaned[k] = '[IMAGE_REMOVED]'
                else:
                    # Old destructive behavior (for non-data-URI base64 or when disabled)
                    cleaned[k] = '[IMAGE_REMOVED]'
            else:
                cleaned[k] = clean_object(v, stats, project_dir, preserve_images)
        return cleaned
    elif isinstance(obj, list):
        return [clean_object(item, stats, project_dir, preserve_images) for item in obj]
    elif isinstance(obj, str) and is_base64_image(obj):
        stats['total_removed_size'] += len(obj)
        stats['items_cleaned'] += 1
        
        if preserve_images and project_dir and is_extractable_image(obj):
            # Extract image to file (only for data URIs)
            filepath = extract_image_to_file(obj, project_dir, stats['items_cleaned'])
            if filepath:
                # Replace with file path reference
                stats['images_extracted'] += 1
                return f'[IMAGE_FILE:{filepath}]'
            else:
                # Fallback to old behavior if extraction fails
                return '[IMAGE_REMOVED]'
        else:
            # Old destructive behavior (for non-data-URI base64 or when disabled)
            return '[IMAGE_REMOVED]'
    else:
        return obj



def parse_arguments():
    """Parse command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract and preserve base64 encoded images from Claude Code history",
        epilog="Examples:\n"
               "  %(prog)s                           # Clean current Claude config\n"
               "  %(prog)s --recover-from-backup     # Recover images from backup and merge changes\n"
               "  %(prog)s --list-backups           # List available backup files\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--recover-from-backup', 
                       metavar='BACKUP_FILE',
                       nargs='?',
                       const='auto',
                       help='Recover images from backup file and merge with current changes (auto-detects if no file specified)')
    parser.add_argument('--list-backups', 
                       action='store_true',
                       help='List available backup files')
    parser.add_argument('--config-file',
                       metavar='FILE',
                       help='Use specific Claude config file instead of auto-detection')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose output')
    
    return parser.parse_args()

def clean_claude_config(claude_json_path=None, verbose=False):
    """Main image cleaning function"""
    # Find Claude config if not specified
    if not claude_json_path:
        claude_json_path = find_claude_config()
    
    # Check if file exists
    if not claude_json_path or not os.path.exists(claude_json_path):
        print(f"Error: Claude config file not found")
        print("Searched in:")
        if platform.system() == "Windows":
            userprofile = os.environ.get('USERPROFILE', '')
            appdata = os.environ.get('APPDATA', '')
            localappdata = os.environ.get('LOCALAPPDATA', '')
            print(f"  - {os.path.join(userprofile, '.claude.json')}")
            print(f"  - {os.path.join(appdata, 'claude', 'claude.json')}")
            print(f"  - {os.path.join(localappdata, 'claude', 'claude.json')}")
        else:
            home = os.path.expanduser('~')
            print(f"  - {os.path.join(home, '.claude.json')}")
            print(f"  - {os.path.join(home, '.config', 'claude', 'claude.json')}")
        sys.exit(1)
    
    print(f"Found Claude config: {claude_json_path}")
    
    # Set up images directory
    images_base_dir = get_images_directory()
    print(f"Images will be saved to: {images_base_dir}")
    
    # Get original file size
    original_size = os.path.getsize(claude_json_path)
    print(f"Original file size: {original_size / 1024 / 1024:.1f} MB")
    
    # Create backup
    backup_path = f"{claude_json_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(claude_json_path, 'r') as f:
        data = json.load(f)
    
    with open(backup_path, 'w') as f:
        json.dump(data, f)
    print(f"Backup saved to: {backup_path}")
    
    # Clean the data
    cleaned_data = data.copy()
    stats = {'total_removed_size': 0, 'items_cleaned': 0, 'images_extracted': 0}
    
    # Clean all projects
    for proj_path in cleaned_data.get('projects', {}):
        if 'history' in cleaned_data['projects'][proj_path]:
            # Create project directory for images
            project_dir = create_project_directory(images_base_dir, proj_path)
            
            for hist_item in cleaned_data['projects'][proj_path]['history']:
                if 'pastedContents' in hist_item:
                    hist_item['pastedContents'] = clean_object(
                        hist_item['pastedContents'], 
                        stats, 
                        project_dir, 
                        preserve_images=True
                    )
    
    print(f"\nItems cleaned: {stats['items_cleaned']}")
    print(f"Images extracted: {stats['images_extracted']}")
    print(f"Total size removed: {stats['total_removed_size'] / 1024 / 1024:.1f} MB")
    
    # Save the cleaned data
    if stats['items_cleaned'] > 0:
        with open(claude_json_path, 'w') as f:
            json.dump(cleaned_data, f)
        print("Cleaned .claude.json saved!")
        
        if stats['images_extracted'] > 0:
            print(f"✅ {stats['images_extracted']} images preserved and extracted to files")
            print(f"📁 Images location: {images_base_dir}")
        
        # Check new file size
        new_size = os.path.getsize(claude_json_path)
        print(f"New file size: {new_size / 1024 / 1024:.1f} MB")
        print(f"Size reduction: {(1 - new_size/original_size) * 100:.1f}%")
    else:
        print("No images found to clean.")
        # Remove unnecessary backup
        os.remove(backup_path)
        print("Backup removed (no changes made)")

def list_backups(claude_json_path=None):
    """List available backup files"""
    if not claude_json_path:
        claude_json_path = find_claude_config()
    
    if not claude_json_path:
        print("Error: Could not find Claude config file")
        return
    
    backup_dir = os.path.dirname(claude_json_path)
    backup_pattern = os.path.basename(claude_json_path) + ".backup.*"
    
    # Find backup files
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.startswith(os.path.basename(claude_json_path) + ".backup."):
            backup_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(backup_path)
            backup_files.append((file, backup_path, file_size))
    
    if not backup_files:
        print("No backup files found")
        return
    
    print(f"Available backup files:")
    backup_files.sort(key=lambda x: x[0])  # Sort by filename (timestamp)
    for filename, full_path, size in backup_files:
        print(f"  {filename} ({size / 1024 / 1024:.1f} MB)")

def clean_object_destructive(obj, stats):
    """Recursively clean base64 images from an object (destructive - no image preservation)"""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if is_base64_image(v):
                stats['total_removed_size'] += len(v)
                stats['items_cleaned'] += 1
                cleaned[k] = '[IMAGE_REMOVED]'
            else:
                cleaned[k] = clean_object_destructive(v, stats)
        return cleaned
    elif isinstance(obj, list):
        return [clean_object_destructive(item, stats) for item in obj]
    elif isinstance(obj, str) and is_base64_image(obj):
        stats['total_removed_size'] += len(obj)
        stats['items_cleaned'] += 1
        return '[IMAGE_REMOVED]'
    else:
        return obj

def create_destructive_version(backup_data):
    """Create a destructively cleaned version of backup data (like old cleaner would have done)"""
    print("🔄 Creating destructive version of backup data...")
    cleaned_data = copy.deepcopy(backup_data)
    stats = {'total_removed_size': 0, 'items_cleaned': 0}
    
    # Clean all projects destructively
    for proj_path in cleaned_data.get('projects', {}):
        if 'history' in cleaned_data['projects'][proj_path]:
            for hist_item in cleaned_data['projects'][proj_path]['history']:
                if 'pastedContents' in hist_item:
                    hist_item['pastedContents'] = clean_object_destructive(
                        hist_item['pastedContents'], 
                        stats
                    )
    
    print(f"   Destructively removed {stats['items_cleaned']} images")
    return cleaned_data

def find_differences(current_data, destructive_backup_data):
    """Find differences between current data and destructively cleaned backup"""
    print("🔍 Analyzing differences between current and backup data...")
    
    differences = {
        'new_projects': [],
        'modified_projects': {},
        'new_history_items': {}
    }
    
    current_projects = current_data.get('projects', {})
    backup_projects = destructive_backup_data.get('projects', {})
    
    # Find new projects
    for proj_path in current_projects:
        if proj_path not in backup_projects:
            differences['new_projects'].append(proj_path)
            print(f"   Found new project: {proj_path}")
    
    # Find modified projects (new history items)
    for proj_path in current_projects:
        if proj_path in backup_projects:
            current_history = current_projects[proj_path].get('history', [])
            backup_history = backup_projects[proj_path].get('history', [])
            
            if len(current_history) > len(backup_history):
                new_items = current_history[len(backup_history):]
                differences['new_history_items'][proj_path] = new_items
                print(f"   Found {len(new_items)} new history items in {proj_path}")
    
    return differences

def merge_data_with_images(backup_data_with_images, current_data, differences):
    """Merge backup data (with extracted images) with current changes"""
    print("🔀 Merging backup images with current changes...")
    
    # Start with the backup data that has images extracted
    merged_data = copy.deepcopy(backup_data_with_images)
    
    # Add new projects
    for proj_path in differences['new_projects']:
        merged_data['projects'][proj_path] = current_data['projects'][proj_path]
        print(f"   Added new project: {proj_path}")
    
    # Add new history items to existing projects
    for proj_path, new_items in differences['new_history_items'].items():
        if proj_path in merged_data['projects']:
            merged_data['projects'][proj_path]['history'].extend(new_items)
            print(f"   Added {len(new_items)} new history items to {proj_path}")
    
    return merged_data

def recover_from_backup(backup_file_path, claude_json_path=None, verbose=False):
    """Recover images from backup and merge with current changes"""
    if not claude_json_path:
        claude_json_path = find_claude_config()
    
    if not os.path.exists(backup_file_path):
        print(f"Error: Backup file not found: {backup_file_path}")
        return False
    
    if not os.path.exists(claude_json_path):
        print(f"Error: Current Claude config not found: {claude_json_path}")
        return False
    
    print(f"🚀 Starting data recovery process...")
    print(f"   Backup file: {backup_file_path} ({os.path.getsize(backup_file_path) / 1024 / 1024:.1f} MB)")
    print(f"   Current file: {claude_json_path} ({os.path.getsize(claude_json_path) / 1024 / 1024:.1f} MB)")
    
    # Load the data
    print("📖 Loading data files...")
    with open(backup_file_path, 'r') as f:
        backup_data = json.load(f)
    
    with open(claude_json_path, 'r') as f:
        current_data = json.load(f)
    
    # Step 1: Create destructive version of backup to compare
    destructive_backup = create_destructive_version(backup_data)
    
    # Step 2: Find differences between current and destructive backup
    differences = find_differences(current_data, destructive_backup)
    
    # Step 3: Process backup with image preservation
    print("🖼️ Processing backup with image preservation...")
    images_base_dir = get_images_directory()
    backup_with_images = copy.deepcopy(backup_data)
    stats = {'total_removed_size': 0, 'items_cleaned': 0, 'images_extracted': 0}
    
    for proj_path in backup_with_images.get('projects', {}):
        if 'history' in backup_with_images['projects'][proj_path]:
            # Create project directory for images
            project_dir = create_project_directory(images_base_dir, proj_path)
            
            for hist_item in backup_with_images['projects'][proj_path]['history']:
                if 'pastedContents' in hist_item:
                    hist_item['pastedContents'] = clean_object(
                        hist_item['pastedContents'], 
                        stats, 
                        project_dir, 
                        preserve_images=True
                    )
    
    print(f"   Extracted {stats['images_extracted']} images from backup")
    
    # Step 4: Merge backup with images + current changes
    merged_data = merge_data_with_images(backup_with_images, current_data, differences)
    
    # Step 5: Create backup of current file before replacing
    recovery_backup_path = f"{claude_json_path}.recovery-backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(recovery_backup_path, 'w') as f:
        json.dump(current_data, f)
    print(f"💾 Current file backed up to: {recovery_backup_path}")
    
    # Step 6: Save merged data
    with open(claude_json_path, 'w') as f:
        json.dump(merged_data, f)
    
    # Report results
    new_size = os.path.getsize(claude_json_path)
    print(f"\n✅ Data recovery completed successfully!")
    print(f"   Images recovered: {stats['images_extracted']}")
    print(f"   New projects added: {len(differences['new_projects'])}")
    print(f"   Projects with new history: {len(differences['new_history_items'])}")
    print(f"   Final file size: {new_size / 1024 / 1024:.1f} MB")
    print(f"   Images location: {images_base_dir}")
    print(f"   Recovery backup: {recovery_backup_path}")
    
    return True

def main():
    """Main entry point"""
    args = parse_arguments()
    
    if args.list_backups:
        list_backups(args.config_file)
        return
    
    if args.recover_from_backup is not None:
        # Find the backup file if not specified or set to 'auto'  
        backup_file = args.recover_from_backup
        if not backup_file or backup_file == 'auto':
            # Try to find the latest large backup file
            claude_json_path = find_claude_config()
            if claude_json_path:
                backup_dir = os.path.dirname(claude_json_path)
                backup_files = []
                for file in os.listdir(backup_dir):
                    if file.startswith(os.path.basename(claude_json_path) + ".backup."):
                        backup_path = os.path.join(backup_dir, file)
                        file_size = os.path.getsize(backup_path)
                        # Look for large backup files (likely containing images)
                        if file_size > 5 * 1024 * 1024:  # > 5MB
                            backup_files.append((file, backup_path, file_size))
                
                if backup_files:
                    # Use the largest backup file
                    backup_files.sort(key=lambda x: x[2], reverse=True)
                    backup_file = backup_files[0][1]
                    print(f"🔍 Auto-detected backup file: {backup_files[0][0]} ({backup_files[0][2] / 1024 / 1024:.1f} MB)")
                else:
                    print("Error: No suitable backup files found. Specify backup file manually.")
                    print("Use --list-backups to see available files.")
                    return
            else:
                print("Error: Could not find Claude config file")
                return
        
        success = recover_from_backup(backup_file, args.config_file, args.verbose)
        if not success:
            sys.exit(1)
        return
    
    # Default operation: clean Claude config
    clean_claude_config(args.config_file, args.verbose)

if __name__ == "__main__":
    main()