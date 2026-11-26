#!/usr/bin/env python3
"""
Google Drive Local Sync Helper for patient-guide-maker
Resolves Google Drive folder URLs to local macOS DriveFS paths and safely copies files for automatic background cloud sync.
"""

import sys
import os
import shutil
import sqlite3
import argparse
import re
from pathlib import Path

def resolve_drive_folder_id(url_or_id):
    # Extract 28-33 char drive ID
    match = re.search(r'[-\w]{25,}', url_or_id)
    return match.group(0) if match else url_or_id

def find_local_drive_path(folder_id):
    drivefs_base = Path.home() / "Library/Application Support/Google/DriveFS"
    if not drivefs_base.exists():
        return None
        
    db_files = list(drivefs_base.glob("**/metadata_sqlite_db"))
    for db_path in db_files:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.text_factory = bytes
            c = conn.cursor()
            
            # Find stable_id in stable_ids table
            c.execute("SELECT stable_id FROM stable_ids WHERE cloud_id = ?", (folder_id.encode('utf-8'),))
            res = c.fetchone()
            if not res:
                # Also check in items id
                c.execute("SELECT stable_id FROM items WHERE id = ?", (folder_id.encode('utf-8'),))
                res = c.fetchone()
                
            if res:
                target_stable_id = res[0]
                # Reconstruct full folder path
                path_parts = []
                curr = target_stable_id
                while curr:
                    c.execute("SELECT local_title FROM items WHERE stable_id = ?", (curr,))
                    r = c.fetchone()
                    if not r or not r[0]:
                        break
                    path_parts.append(r[0].decode('utf-8', errors='replace'))
                    c.execute("SELECT parent_stable_id FROM stable_parents WHERE item_stable_id = ?", (curr,))
                    p = c.fetchone()
                    curr = p[0] if p else None
                conn.close()
                
                rel_path = "/".join(reversed(path_parts))
                # Check CloudStorage mount
                cloud_storage = Path.home() / "Library/CloudStorage"
                for drive_dir in cloud_storage.glob("GoogleDrive-*"):
                    cand = drive_dir / rel_path
                    if cand.exists():
                        return cand
        except Exception:
            pass
            
    return None

def main():
    parser = argparse.ArgumentParser(description="Sync files to Google Drive via local DriveFS.")
    parser.add_argument("--file", required=True, help="File to sync/upload")
    parser.add_argument("--drive-url", help="Google Drive folder URL or ID")
    parser.add_argument("--dest-name", help="Optional rename for destination file")
    
    args = parser.parse_args()
    
    src = Path(args.file).resolve()
    if not src.exists():
        print(f"Error: Source file {src} does not exist", file=sys.stderr)
        sys.exit(1)
        
    folder_id = resolve_drive_folder_id(args.drive_url)
    dest_dir = find_local_drive_path(folder_id)
    
    if not dest_dir or not dest_dir.exists():
        print(f"Error: Could not resolve local path for Drive folder ID '{folder_id}'", file=sys.stderr)
        print("Please check that Google Drive for Desktop is running and mounted.", file=sys.stderr)
        sys.exit(1)
        
    target_filename = args.dest_name if args.dest_name else src.name
    dest_file = dest_dir / target_filename
    
    shutil.copy2(src, dest_file)
    print(f"✅ Successfully copied to Google Drive sync folder: {dest_file}")
    print("Google Drive for Desktop will automatically sync this file to the cloud in the background.")

if __name__ == "__main__":
    main()
