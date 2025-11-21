#!/usr/bin/env python3
"""
Script to create upload directory structure
"""

import os

def create_upload_directories():
    """Create necessary upload directories"""
    base_dirs = [
        "uploads/original",
        "uploads/annotated", 
        "uploads/thumbnails",
        "models"
    ]
    
    for dir_path in base_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Create .gitkeep files to preserve empty directories in git
    for dir_path in base_dirs:
        gitkeep_path = os.path.join(dir_path, ".gitkeep")
        with open(gitkeep_path, 'w') as f:
            f.write("# This file ensures the directory is tracked by git\n")
        print(f"✅ Created .gitkeep in: {dir_path}")

if __name__ == "__main__":
    create_upload_directories()