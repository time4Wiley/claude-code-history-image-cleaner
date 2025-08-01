"""
Claude Code History Image Cleaner

A sophisticated Python tool to extract and preserve base64 encoded images from 
Claude Code's history file (~/.claude.json), dramatically reducing file size 
while preserving all images for future reference.

Features advanced data recovery capabilities to restore lost images from backups.
"""

__version__ = "1.0.0"
__author__ = "time4Wiley"
__license__ = "MIT"
__email__ = "time4wiley@users.noreply.github.com"

from .main import main

__all__ = ["main"]