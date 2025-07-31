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

def extract_image_to_file(data_uri, output_dir, image_counter):
    """Extract base64 image from data URI and save to file"""
    try:
        mime_type, base64_data = parse_data_uri(data_uri)
        if not mime_type or not base64_data:
            return None
        
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        
        # Generate filename
        file_extension = get_file_extension(mime_type)
        filename = f"image_{image_counter:03d}{file_extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Write image file
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
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

def is_extractable_image(s):
    """Check if a string is a data URI that can be extracted"""
    if not isinstance(s, str):
        return False
    return s.startswith('data:image/')

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

def main():
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

def generate_fake_base64_image(width=100, height=100, format='png'):
    """Generate a small fake base64 image for testing"""
    # Create a minimal PNG header + data (this creates a tiny valid PNG)
    if format.lower() == 'png':
        # Minimal PNG: signature + IHDR + IDAT + IEND
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk
            b'\x00\x00\x00d\x00\x00\x00d\x08\x02\x00\x00\x00'  # 100x100, RGB
            b'\xff\xcc\xde\x8f'  # CRC
            b'\x00\x00\x00\x0cIDAT'  # IDAT chunk
            b'x\x9cc\xf8\x0f\x00\x00\x01\x00\x01'  # Compressed data
            b'\n\x9d\x8e\x99'  # CRC
            b'\x00\x00\x00\x00IEND'  # IEND chunk
            b'\xaeB`\x82'  # CRC
        )
        mime_type = 'image/png'
    else:
        # For other formats, just use PNG data but with different MIME type
        png_data = (
            b'\x89PNG\r\n\x1a\n'
            b'\x00\x00\x00\rIHDR'
            b'\x00\x00\x00d\x00\x00\x00d\x08\x02\x00\x00\x00'
            b'\xff\xcc\xde\x8f'
            b'\x00\x00\x00\x0cIDAT'
            b'x\x9cc\xf8\x0f\x00\x00\x01\x00\x01'
            b'\n\x9d\x8e\x99'
            b'\x00\x00\x00\x00IEND'
            b'\xaeB`\x82'
        )
        mime_type = f'image/{format.lower()}'
    
    # Encode to base64
    b64_data = base64.b64encode(png_data).decode('ascii')
    return f'data:{mime_type};base64,{b64_data}'

def generate_test_claude_config(output_path, num_projects=3, images_per_project=2):
    """Generate a test Claude config file with fake base64 images"""
    test_data = {
        "projects": {}
    }
    
    # Generate fake projects
    for i in range(num_projects):
        project_path = f"/fake/project/path{i+1}"
        test_data["projects"][project_path] = {
            "history": []
        }
        
        # Generate history items with images
        for j in range(images_per_project):
            fake_image = generate_fake_base64_image(format=['png', 'jpeg', 'gif'][j % 3])
            
            history_item = {
                "timestamp": "2025-07-31T12:00:00Z",
                "pastedContents": [
                    {
                        "type": "image", 
                        "data": fake_image
                    },
                    {
                        "type": "text",
                        "content": f"Test image {j+1} in project {i+1}"
                    }
                ]
            }
            test_data["projects"][project_path]["history"].append(history_item)
    
    # Write test file
    with open(output_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Test config generated: {output_path}")
    print(f"- {num_projects} projects")
    print(f"- {num_projects * images_per_project} total images")
    return output_path

def main():
    # Check for test data generation flag
    if len(sys.argv) > 1 and sys.argv[1] == '--generate-test-data':
        output_path = sys.argv[2] if len(sys.argv) > 2 else 'test_claude_config.json'
        generate_test_claude_config(output_path)
        return
    
    # Check for test file flag
    if len(sys.argv) > 2 and sys.argv[1] == '--test-file':
        claude_json_path = sys.argv[2]
        if not os.path.exists(claude_json_path):
            print(f"Error: Test file not found: {claude_json_path}")
            sys.exit(1)
    else:
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
        print("\nTo generate test data, run:")
        print("  python3 claude-code-history-image-cleaner.py --generate-test-data [output_file.json]")
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

if __name__ == "__main__":
    main()