#!/usr/bin/env python3
"""
Storage & Memory Audit Script for macOS
Part of the clean-mac-storage skill.
Scans disk capacity, RAM/swap, heavy apps, caches, VMs, chat apps, Mail attachments, and iCloud sync folders.
Outputs clean structured text or JSON.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

HOME = Path.home()

def get_dir_size_fast(path):
    """Calculates size using du -sk with timeout to avoid slow recursive scans."""
    if not os.path.exists(path):
        return 0
    try:
        res = subprocess.run(
            ["du", "-sk", str(path)],
            capture_output=True,
            text=True,
            timeout=8
        )
        if res.returncode == 0:
            lines = res.stdout.strip().split("\n")
            if lines and lines[-1]:
                parts = lines[-1].split("\t")
                if parts and parts[0].isdigit():
                    return int(parts[0]) * 1024
        return 0
    except Exception:
        return 0

def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.1f} {unit}"
        b /= 1024.0
    return f"{b:.1f} PB"

def check_disk_usage():
    data_mount = "/System/Volumes/Data"
    target = data_mount if os.path.exists(data_mount) else "/"
    total, used, free = shutil.disk_usage(target)
    used_pct = (used / total) * 100
    free_pct = (free / total) * 100
    
    status = "HEALTHY"
    if free_pct < 10:
        status = "CRITICAL (< 10% free)"
    elif free_pct < 15:
        status = "WARNING (< 15% free)"
        
    return {
        "mount": target,
        "total": format_bytes(total),
        "used": format_bytes(used),
        "free": format_bytes(free),
        "used_pct": f"{used_pct:.1f}%",
        "free_pct": f"{free_pct:.1f}%",
        "status": status,
        "free_bytes": free
    }

def check_external_drives():
    volumes_dir = Path("/Volumes")
    drives = []
    if volumes_dir.exists():
        for item in volumes_dir.iterdir():
            if item.is_dir() and not item.is_symlink() and item.name not in ["Macintosh HD", "Recovery"]:
                try:
                    total, used, free = shutil.disk_usage(item)
                    if total > 1024 * 1024 * 1024:  # > 1GB
                        drives.append({
                            "name": item.name,
                            "path": str(item),
                            "free": format_bytes(free),
                            "total": format_bytes(total)
                        })
                except Exception:
                    pass
    return drives

def scan_heavy_apps(min_size_mb=400):
    apps_dir = Path("/Applications")
    heavy_apps = []
    if apps_dir.exists():
        for app in sorted(apps_dir.glob("*.app")):
            size = get_dir_size_fast(app)
            size_mb = size / (1024 * 1024)
            if size_mb >= min_size_mb:
                heavy_apps.append({
                    "name": app.name,
                    "path": str(app),
                    "size": format_bytes(size),
                    "size_mb": size_mb
                })
    heavy_apps.sort(key=lambda x: x["size_mb"], reverse=True)
    return heavy_apps

def scan_parallels_vms():
    parallels_dir = HOME / "Parallels"
    prl_disk_tool = Path("/Applications/Parallels Desktop.app/Contents/MacOS/prl_disk_tool")
    vms = []
    if not parallels_dir.exists():
        return vms
    for pvm in sorted(parallels_dir.glob("*.pvm")):
        pvm_size = get_dir_size_fast(pvm)
        hdd_info = None
        hdds = list(pvm.glob("*.hdd"))
        if hdds and prl_disk_tool.exists():
            try:
                res = subprocess.run(
                    [str(prl_disk_tool), "compact", "--info", "--hdd", str(hdds[0])],
                    capture_output=True, text=True, timeout=8
                )
                alloc_blocks = used_blocks = None
                for line in res.stdout.splitlines():
                    if "Allocated blocks:" in line:
                        alloc_blocks = int(line.split(":")[1].strip())
                    elif "Used blocks:" in line:
                        used_blocks = int(line.split(":")[1].strip())
                if alloc_blocks is not None and used_blocks is not None:
                    reclaim_gb = max(0.0, (alloc_blocks - used_blocks) / 1024.0)
                    hdd_info = f"Allocated: {alloc_blocks/1024:.1f} GB | Used blocks: {used_blocks/1024:.1f} GB | Directly reclaimable: {reclaim_gb:.1f} GB"
            except Exception:
                pass
        vms.append({
            "name": pvm.name,
            "path": str(pvm),
            "size": format_bytes(pvm_size),
            "hdd_info": hdd_info
        })
    return vms

def scan_hotspots():
    targets = [
        {"name": "Parallels VMs (~/Parallels)", "path": HOME / "Parallels", "type": "vm"},
        {"name": "Notability Container", "path": HOME / "Library/Containers/com.gingerlabs.Notability", "type": "notes"},
        {"name": "Notability ImportSessions (Temp Cache)", "path": HOME / "Library/Group Containers/group.notability/ImportSessions", "type": "cache"},
        {"name": "Apple Notes Group Container", "path": HOME / "Library/Group Containers/group.com.apple.notes", "type": "notes"},
        {"name": "iCloud Notability Sync", "path": HOME / "Library/Mobile Documents/ZP9ZJ4EF3S~com~gingerlabs~Notability", "type": "icloud_sync"},
        {"name": "Apple Mail V10 Storage", "path": HOME / "Library/Mail/V10", "type": "mail"},
        {"name": "User App Caches (~/Library/Caches)", "path": HOME / "Library/Caches", "type": "cache"},
        {"name": "Google Chrome On-Device AI Model (OptGuideOnDeviceModel)", "path": HOME / "Library/Application Support/Google/Chrome/OptGuideOnDeviceModel", "type": "cache"},
        {"name": "Google Chrome Headless Cache", "path": HOME / "Library/Application Support/Google/Chrome-headless", "type": "cache"},
        {"name": "Google Updater Cache", "path": HOME / "Library/Application Support/Google/GoogleUpdater", "type": "cache"},
        {"name": "macOS MediaAnalysis Cache (mediaanalysisd)", "path": HOME / "Library/Containers/com.apple.mediaanalysisd/Data/Library/Caches", "type": "cache"},
        {"name": "Safari Container Cache", "path": HOME / "Library/Containers/com.apple.Safari/Data/Library/Caches", "type": "cache"},
        {"name": "NPM Package Cache (~/.npm)", "path": HOME / ".npm", "type": "cache"},
        {"name": "iCloud Books Sync", "path": HOME / "Library/Mobile Documents/iCloud~com~apple~iBooks", "type": "icloud_sync"},
        {"name": "LINE Mac Data", "path": HOME / "Library/Group Containers/VUTU7AKEUR.jp.naver.line.mac", "type": "chat_data"},
        {"name": "Trash (~/.Trash)", "path": HOME / ".Trash", "type": "trash"},
        {"name": "Python / Tool Cache (~/.cache)", "path": HOME / ".cache", "type": "cache"},
    ]
    
    results = []
    for t in targets:
        p = t["path"]
        if p.exists():
            size = get_dir_size_fast(p)
            if size > 50 * 1024 * 1024:  # Only report if > 50 MB
                results.append({
                    "name": t["name"],
                    "path": str(p),
                    "type": t["type"],
                    "size": format_bytes(size),
                    "size_bytes": size
                })
    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results

def main():
    as_json = "--json" in sys.argv
    disk = check_disk_usage()
    externals = check_external_drives()
    apps = scan_heavy_apps()
    hotspots = scan_hotspots()
    parallels_vms = scan_parallels_vms()
    
    data = {
        "disk": disk,
        "external_drives": externals,
        "heavy_apps": apps,
        "hotspots": hotspots,
        "parallels_vms": parallels_vms
    }
    
    if as_json:
        print(json.dumps(data, indent=2))
        return

    print("=" * 60)
    print(f"📊 macOS Storage Health Audit: {disk['status']}")
    print(f"   Capacity: {disk['used']} used / {disk['total']} total ({disk['used_pct']} full)")
    print(f"   Available: {disk['free']} free ({disk['free_pct']})")
    print("=" * 60)
    
    if externals:
        print("\n💾 Available External Storage (Potential Offload Targets):")
        for d in externals:
            print(f"   - {d['name']} ({d['path']}): {d['free']} free of {d['total']}")
            
    print("\n🔥 Top Storage Culprits / Hotspots:")
    for h in hotspots:
        print(f"   • {h['name']}: {h['size']}")

    if parallels_vms:
        print("\n🖥️  Parallels Virtual Machines Detail:")
        for vm in parallels_vms:
            info_str = f" ({vm['hdd_info']})" if vm.get("hdd_info") else ""
            print(f"   • {vm['name']}: {vm['size']}{info_str}")
        
    if apps:
        print(f"\n📦 Heavy Installed Applications (>= 400 MB):")
        for a in apps[:8]:
            print(f"   • {a['name']}: {a['size']}")
            
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
