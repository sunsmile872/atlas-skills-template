import os
import re
import glob
import sqlite3
from typing import Optional, Tuple, List, Dict

def extract_gdrive_id(url_or_id: str) -> Optional[str]:
    url_or_id = url_or_id.strip()
    if "/" not in url_or_id and len(url_or_id) >= 20:
        return url_or_id
    
    # File match
    m_file = re.search(r"/file/d/([a-zA-Z0-9_\-]+)", url_or_id)
    if m_file:
        return m_file.group(1)
        
    # Folder match
    m_folder = re.search(r"/folders/([a-zA-Z0-9_\-]+)", url_or_id)
    if m_folder:
        return m_folder.group(1)
        
    # id parameter
    m_param = re.search(r"[?&]id=([a-zA-Z0-9_\-]+)", url_or_id)
    if m_param:
        return m_param.group(1)
        
    return None

def find_drivefs_databases() -> List[Tuple[str, str]]:
    """Returns list of (db_path, cloud_storage_root)"""
    home = os.path.expanduser("~")
    drivefs_base = os.path.join(home, "Library/Application Support/Google/DriveFS")
    results = []
    if not os.path.exists(drivefs_base):
        return results

    cloud_roots = glob.glob(os.path.join(home, "Library/CloudStorage/GoogleDrive-*"))
    default_cloud_root = cloud_roots[0] if cloud_roots else ""

    for account_dir in os.listdir(drivefs_base):
        full_acc = os.path.join(drivefs_base, account_dir)
        if not os.path.isdir(full_acc):
            continue
        for db_name in ["metadata_sqlite_db", "mirror_metadata_sqlite.db"]:
            db_path = os.path.join(full_acc, db_name)
            if os.path.exists(db_path):
                # Try finding matching CloudStorage root
                matching_root = default_cloud_root
                results.append((db_path, matching_root))
    return results

def resolve_gdrive_item(gdrive_id: str) -> Optional[Dict]:
    """
    Resolves a Google Drive file or folder ID to a local synced path.
    Returns:
    {
        'type': 'file' | 'folder',
        'local_path': str,
        'title': str,
        'children': list of dicts (if folder)
    }
    """
    dbs = find_drivefs_databases()
    target_bytes = gdrive_id.encode("utf-8")

    for db_path, cloud_root in dbs:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.text_factory = bytes
            c = conn.cursor()

            # Find stable_id
            row = c.execute("SELECT stable_id FROM stable_ids WHERE cloud_id LIKE ?", (b"%" + target_bytes + b"%",)).fetchone()
            if not row:
                conn.close()
                continue
            
            sid = row[0]
            item_row = c.execute("SELECT local_title, mime_type, is_folder, file_size FROM items WHERE stable_id = ?", (sid,)).fetchone()
            if not item_row:
                conn.close()
                continue
                
            local_title = item_row[0].decode("utf-8", errors="ignore") if item_row[0] else ""
            mime_type = item_row[1].decode("utf-8", errors="ignore") if item_row[1] else ""
            is_folder = item_row[2] == 1 or "folder" in mime_type

            # Trace parents up to My Drive
            def get_parent_info(cur_sid):
                p_row = c.execute("SELECT parent_stable_id FROM stable_parents WHERE item_stable_id = ?", (cur_sid,)).fetchone()
                t_row = c.execute("SELECT local_title FROM items WHERE stable_id = ?", (cur_sid,)).fetchone()
                title = t_row[0].decode("utf-8", errors="ignore") if t_row and t_row[0] else ""
                return (p_row[0] if p_row else None), title

            cur = sid
            path_components = []
            while cur:
                parent, title = get_parent_info(cur)
                if cur != sid:
                    path_components.append(title)
                if title == "My Drive":
                    break
                cur = parent

            path_components.reverse()
            # Construct filesystem path
            # path_components starts with 'My Drive'
            full_local_path = os.path.join(cloud_root, *path_components, local_title)

            children_list = []
            if is_folder:
                c_rows = c.execute(
                    "SELECT i.stable_id, i.local_title, i.mime_type, s.cloud_id, i.is_folder "
                    "FROM items i "
                    "JOIN stable_parents sp ON i.stable_id = sp.item_stable_id "
                    "LEFT JOIN stable_ids s ON i.stable_id = s.stable_id "
                    "WHERE sp.parent_stable_id = ? AND i.trashed = 0", (sid,)
                ).fetchall()

                for cr in c_rows:
                    c_title = cr[1].decode("utf-8", errors="ignore") if cr[1] else ""
                    c_mime = cr[2].decode("utf-8", errors="ignore") if cr[2] else ""
                    c_cloud_id = cr[3].decode("utf-8", errors="ignore") if cr[3] else ""
                    c_is_folder = cr[4] == 1 or "folder" in c_mime
                    children_list.append({
                        'title': c_title,
                        'mime_type': c_mime,
                        'cloud_id': c_cloud_id,
                        'is_folder': c_is_folder,
                        'local_path': os.path.join(full_local_path, c_title)
                    })

            conn.close()
            return {
                'type': 'folder' if is_folder else 'file',
                'local_path': full_local_path,
                'title': local_title,
                'children': children_list
            }

        except Exception:
            pass

    return None

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        target = sys.argv[1]
        gid = extract_gdrive_id(target) or target
        info = resolve_gdrive_item(gid)
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"Failed to resolve Google Drive ID: {gid}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python3 gdrive_resolver.py <gdrive_url_or_id>")
