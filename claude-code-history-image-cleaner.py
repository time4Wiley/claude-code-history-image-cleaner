#!/usr/bin/env python3
"""
Clean base64 encoded images from Claude CLI history (~/.claude.json)

This script removes base64 encoded images from the Claude CLI history file
to reduce file size and improve startup performance.
"""

import json
import os
import sys
from datetime import datetime

def is_base64_image(s):
    """Check if a string is likely a base64 encoded image"""
    if not isinstance(s, str):
        return False
    
    # Check for data URI scheme
    if s.startswith('data:image/'):
        return True
    
    # Check if it's a very long string that could be base64
    if len(s) > 50000:  # Images are typically very large
        # Sample the string to check if it's base64-like
        sample = s[:1000]
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        if all(c in base64_chars or c in '\n\r' for c in sample):
            return True
    
    return False

def clean_object(obj, stats):
    """Recursively clean base64 images from an object"""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if is_base64_image(v):
                stats['total_removed_size'] += len(v)
                stats['items_cleaned'] += 1
                cleaned[k] = '[IMAGE_REMOVED]'
            else:
                cleaned[k] = clean_object(v, stats)
        return cleaned
    elif isinstance(obj, list):
        return [clean_object(item, stats) for item in obj]
    elif isinstance(obj, str) and is_base64_image(obj):
        stats['total_removed_size'] += len(obj)
        stats['items_cleaned'] += 1
        return '[IMAGE_REMOVED]'
    else:
        return obj

def main():
    claude_json_path = os.path.expanduser('~/.claude.json')
    
    # Check if file exists
    if not os.path.exists(claude_json_path):
        print(f"Error: {claude_json_path} not found")
        sys.exit(1)
    
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
    stats = {'total_removed_size': 0, 'items_cleaned': 0}
    
    # Clean all projects
    for proj_path in cleaned_data.get('projects', {}):
        if 'history' in cleaned_data['projects'][proj_path]:
            for hist_item in cleaned_data['projects'][proj_path]['history']:
                if 'pastedContents' in hist_item:
                    hist_item['pastedContents'] = clean_object(hist_item['pastedContents'], stats)
    
    print(f"\nItems cleaned: {stats['items_cleaned']}")
    print(f"Total size removed: {stats['total_removed_size'] / 1024 / 1024:.1f} MB")
    
    # Save the cleaned data
    if stats['items_cleaned'] > 0:
        with open(claude_json_path, 'w') as f:
            json.dump(cleaned_data, f)
        print("Cleaned .claude.json saved!")
        
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