#!/usr/bin/env python3
"""
Helper script for project-handoff skill.
Extracts git repository metadata, branch info, remotes, package info,
and active directory tree structure to aid in assembling PROJECT_HANDOFF.md.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return ""

def get_git_info(workspace_dir):
    info = {
        "is_git": False,
        "remote_url": "",
        "current_branch": "",
        "status": "",
        "recent_commits": []
    }
    git_dir = Path(workspace_dir) / ".git"
    if not git_dir.exists():
        # Check if parent is git
        top_level = run_cmd("git rev-parse --show-toplevel", cwd=workspace_dir)
        if not top_level:
            return info
        workspace_dir = top_level

    info["is_git"] = True
    info["remote_url"] = run_cmd("git config --get remote.origin.url", cwd=workspace_dir)
    info["current_branch"] = run_cmd("git rev-parse --abbrev-ref HEAD", cwd=workspace_dir)
    info["status"] = run_cmd("git status --short", cwd=workspace_dir)
    
    log = run_cmd("git log -n 5 --pretty=format:'%h - %s (%cr)'", cwd=workspace_dir)
    if log:
        info["recent_commits"] = log.split("\n")
    return info

def get_package_info(workspace_dir):
    pkg_file = Path(workspace_dir) / "package.json"
    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "type": "node",
                    "name": data.get("name", ""),
                    "scripts": data.get("scripts", {}),
                    "dependencies": list(data.get("dependencies", {}).keys()),
                    "devDependencies": list(data.get("devDependencies", {}).keys())
                }
        except Exception:
            pass

    pyproject = Path(workspace_dir) / "pyproject.toml"
    if pyproject.exists():
        return {"type": "python", "file": "pyproject.toml"}
    
    reqs = Path(workspace_dir) / "requirements.txt"
    if reqs.exists():
        return {"type": "python", "file": "requirements.txt"}

    return {"type": "unknown"}

def get_directory_tree(workspace_dir, max_depth=2):
    exclude_dirs = {".git", "node_modules", "dist", ".next", ".cache", "venv", ".venv", "__pycache__"}
    tree = []
    
    root_path = Path(workspace_dir).resolve()
    
    for root, dirs, files in os.walk(root_path):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        
        rel_path = Path(root).relative_to(root_path)
        depth = len(rel_path.parts)
        if depth > max_depth:
            continue
            
        indent = "  " * depth
        if rel_path != Path("."):
            tree.append(f"{indent}├── {rel_path.name}/")
        
        if depth < max_depth:
            for f in sorted(files):
                if not f.startswith(".") and f != "package-lock.json":
                    tree.append(f"{indent}  ├── {f}")
                    
    return "\n".join(tree[:60])

def main():
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    workspace_dir = os.path.abspath(workspace_dir)
    
    git_info = get_git_info(workspace_dir)
    pkg_info = get_package_info(workspace_dir)
    tree = get_directory_tree(workspace_dir)
    
    output = {
        "workspace": workspace_dir,
        "git": git_info,
        "package": pkg_info,
        "tree": tree
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
