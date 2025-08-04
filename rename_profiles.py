#!/usr/bin/env python3
"""
Script to rename profile folders based on Profile ID from profile_text.txt files
"""

import os
import re
import shutil
from pathlib import Path

def extract_profile_id_from_text(file_path):
    """Extract Profile ID from profile_text.txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for "Profile Id : XXXX" pattern
        match = re.search(r'Profile Id\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Alternative pattern: "Profile ID : XXXX"
        match = re.search(r'Profile ID\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def rename_profile_folders():
    """Rename all profile folders based on Profile ID from text files"""
    profiles_dir = Path("nriva_profiles")
    
    if not profiles_dir.exists():
        print("nriva_profiles directory not found!")
        return
    
    # Get all profile folders
    profile_folders = [f for f in profiles_dir.iterdir() if f.is_dir()]
    
    print(f"Found {len(profile_folders)} profile folders")
    
    renamed_count = 0
    errors = []
    
    for folder in profile_folders:
        current_name = folder.name
        profile_text_file = folder / "profile_text.txt"
        
        if not profile_text_file.exists():
            print(f"Warning: No profile_text.txt found in {current_name}")
            continue
        
        # Extract profile ID from text file
        profile_id = extract_profile_id_from_text(profile_text_file)
        
        if not profile_id:
            print(f"Warning: Could not extract Profile ID from {current_name}")
            continue
        
        # Check if folder name already matches profile ID
        if current_name == profile_id:
            print(f"Folder {current_name} already has correct name")
            continue
        
        # Create new folder name
        new_folder_path = profiles_dir / profile_id
        
        # Check if target folder already exists
        if new_folder_path.exists():
            print(f"Warning: Target folder {profile_id} already exists, skipping {current_name}")
            errors.append(f"Target folder {profile_id} already exists for {current_name}")
            continue
        
        try:
            # Rename the folder
            folder.rename(new_folder_path)
            print(f"Renamed: {current_name} -> {profile_id}")
            renamed_count += 1
            
        except Exception as e:
            print(f"Error renaming {current_name} to {profile_id}: {e}")
            errors.append(f"Error renaming {current_name} to {profile_id}: {e}")
    
    print(f"\nRenaming completed!")
    print(f"Successfully renamed: {renamed_count} folders")
    
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")

if __name__ == "__main__":
    rename_profile_folders() 