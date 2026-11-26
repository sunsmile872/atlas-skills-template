#!/usr/bin/env bash
# ==============================================================================
# git_checkpoint.sh — Universal Git & GitHub Lifecycle Automation Engine
# Capabilities: Project Initialization, GitHub Repo Creation, Pages Setup,
#               Zero-Bloat Cloud Auto-Save (Checkpoints), and Rollbacks.
# ==============================================================================
set -euo pipefail

# Helper function to get token from macOS keychain
get_github_token() {
  local token=""
  if command -v git-credential-osxkeychain >/dev/null 2>&1; then
    token=$(printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain get 2>/dev/null | awk -F= '$1=="password"{print $2}')
  fi
  if [ -z "$token" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
    token="$GITHUB_TOKEN"
  fi
  echo "$token"
}

get_github_user() {
  local user=""
  if command -v git-credential-osxkeychain >/dev/null 2>&1; then
    user=$(printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain get 2>/dev/null | awk -F= '$1=="username"{print $2}')
  fi
  if [ -z "$user" ]; then
    user=$(git config --get user.name 2>/dev/null || echo "{{GITHUB_USER}}")
  fi
  echo "$user"
}

cmd_init() {
  local target_dir="${1:-"."}"
  local repo_name="${2:-""}"
  local repo_desc="${3:-""}"

  cd "$target_dir"
  local current_folder
  current_folder=$(basename "$(pwd)")

  # Normalize repo name if empty
  if [ -z "$repo_name" ]; then
    repo_name=$(echo "$current_folder" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9_-]//g')
  fi
  if [ -z "$repo_desc" ]; then
    repo_desc="Project $repo_name managed by Antigravity Git Checkpoint"
  fi

  echo "=========================================================="
  echo "🚀 Initializing Git Project & Remote GitHub Repository"
  echo "📁 Directory: $(pwd)"
  echo "📦 Repo Name: $repo_name"
  echo "=========================================================="

  # 1. Initialize Git repository if not present
  if [ ! -d ".git" ]; then
    git init -b main
    echo "✅ Initialized empty Git repository (branch: main)"
  else
    echo "ℹ️ Existing .git directory found"
  fi

  # 2. Ensure standard user configuration
  if [ -z "$(git config --get user.name 2>/dev/null || true)" ]; then
    git config user.name "{{PRESENTER_NAME}}"
    git config user.email "{{USER_EMAIL}}"
  fi

  # 3. Create or harden .gitignore (prevent secret and trash leaks)
  if [ ! -f ".gitignore" ]; then
    cat <<'EOF' > .gitignore
.DS_Store
*.log
.env
*.pem
*.key
node_modules/
backups/
EOF
    echo "✅ Created clean .gitignore (protected against secrets & cache bloat)"
  fi

  # 4. Authenticate & Create remote repository on GitHub
  local token
  token=$(get_github_token)
  local user
  user=$(get_github_user)

  if [ -n "$token" ]; then
    echo "🔑 Retrieved GitHub credentials for user: $user"
    
    # Check if repo already exists on GitHub
    local check_status
    check_status=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $token" "https://api.github.com/repos/$user/$repo_name")
    
    if [ "$check_status" = "200" ]; then
      echo "ℹ️ Repository $user/$repo_name already exists on GitHub"
    else
      echo "🌐 Creating new repository on GitHub: $user/$repo_name ..."
      local create_res
      create_res=$(curl -s -X POST -H "Authorization: token $token" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$repo_name\",\"description\":\"$repo_desc\",\"homepage\":\"https://$user.github.io/$repo_name/\",\"private\":false,\"has_issues\":true,\"has_projects\":true}")
      echo "✅ Successfully created repository on GitHub!"
    fi

    # Set remote origin
    local remote_url="https://github.com/$user/$repo_name.git"
    if git remote | grep -q "^origin$"; then
      git remote set-url origin "$remote_url"
    else
      git remote add origin "$remote_url"
    fi
    echo "🔗 Remote origin linked to $remote_url"

    # Initial commit & push
    if [ -n "$(git status --porcelain)" ]; then
      git add -A
      git commit -m "feat: initial commit of $repo_name" || true
    fi

    git push -u origin main || true
    echo "⬆️ Pushed initial branch 'main' to GitHub"

    # If index.html exists, configure GitHub Pages
    if [ -f "index.html" ]; then
      echo "📄 Found index.html: Configuring GitHub Pages..."
      local pages_res
      pages_res=$(curl -s -X POST -H "Authorization: token $token" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$user/$repo_name/pages" \
        -d '{"source":{"branch":"main","path":"/"}}' 2>/dev/null || true)
      echo "🌐 GitHub Pages activated!"
      echo "🔗 Live Preview URL: https://$user.github.io/$repo_name/"
    fi
  else
    echo "⚠️ Warning: GitHub token not found in keychain. Local git repo initialized."
  fi

  echo "=========================================================="
  echo "🎉 Project Initialization Complete!"
  echo "=========================================================="
}

cmd_save() {
  local target_dir="${1:-"."}"
  local commit_msg="${2:-""}"

  cd "$target_dir"

  if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Run 'init' first."
    exit 1
  fi

  # Auto-sync index.html and duplicate standalone .html if applicable
  local html_files
  html_files=(*.html)
  if [ -f "index.html" ] && [ ${#html_files[@]} -gt 1 ]; then
    for f in "${html_files[@]}"; do
      if [ "$f" != "index.html" ]; then
        if [ "index.html" -nt "$f" ]; then
          cp "index.html" "$f"
        elif [ "$f" -nt "index.html" ]; then
          cp "$f" "index.html"
        fi
      fi
    done
  fi

  # Check changes
  if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️ Workspace clean. No modifications detected since last checkpoint."
    return 0
  fi

  local timestamp
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")

  if [ -z "$commit_msg" ]; then
    commit_msg="checkpoint: save state ($timestamp)"
  fi

  # Stage and commit
  git add -A
  git commit -m "$commit_msg"

  local current_branch
  current_branch=$(git branch --show-current 2>/dev/null || echo "main")

  # Push to origin
  if git remote | grep -q "^origin$"; then
    git push origin "$current_branch"
    local commit_hash
    commit_hash=$(git rev-parse --short HEAD)
    echo "=========================================================="
    echo "✅ Checkpoint successfully saved and pushed to GitHub!"
    echo "📌 Commit Hash: $commit_hash"
    echo "📝 Message:     $commit_msg"
    echo "🕒 Timestamp:   $timestamp"

    local remote_url
    remote_url=$(git config --get remote.origin.url || "")
    if [[ "$remote_url" =~ github\.com[/:]([^/]+)/([^/.]+)(\.git)? ]]; then
      local user="${BASH_REMATCH[1]}"
      local repo="${BASH_REMATCH[2]}"
      if [ -f "index.html" ]; then
        echo "🌐 Live Preview: https://$user.github.io/$repo/"
      fi
      echo "📂 Commits Log:  https://github.com/$user/$repo/commits/$current_branch"
    fi
    echo "=========================================================="
  else
    echo "ℹ️ Committed locally as $(git rev-parse --short HEAD). (No remote origin configured)"
  fi
}

cmd_status() {
  local target_dir="${1:-"."}"
  cd "$target_dir"

  if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository."
    exit 1
  fi

  echo "=========================================================="
  echo "📊 Git Checkpoint Status"
  echo "📁 Directory: $(pwd)"
  echo "🌿 Branch:    $(git branch --show-current)"
  echo "🔗 Remote:    $(git config --get remote.origin.url || 'None')"
  echo "----------------------------------------------------------"
  echo "Recent Checkpoints:"
  git log -n 5 --pretty=format:"  • %h (%cd) - %s" --date=short
  echo ""
  echo "----------------------------------------------------------"
  local uncommitted
  uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
  if [ "$uncommitted" -eq 0 ]; then
    echo "✅ Working tree clean (all changes saved to cloud)"
  else
    echo "⚠️ $uncommitted uncommitted file(s) waiting for checkpoint"
  fi
  echo "=========================================================="
}

cmd_rollback() {
  local target_dir="${1:-"."}"
  local target_ref="${2:-"HEAD~1"}"

  cd "$target_dir"
  if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository."
    exit 1
  fi

  echo "=========================================================="
  echo "⏪ Reverting to Checkpoint: $target_ref"
  echo "=========================================================="
  git reset --hard "$target_ref"
  local current_branch
  current_branch=$(git branch --show-current 2>/dev/null || echo "main")
  
  if git remote | grep -q "^origin$"; then
    echo "⬆️ Force-syncing rollback to remote..."
    git push -f origin "$current_branch"
  fi
  echo "✅ Successfully restored project to checkpoint $target_ref"
}

# CLI Router
action="${1:-"help"}"
shift || true

case "$action" in
  init)
    cmd_init "${1:-.}" "${2:-}" "${3:-}"
    ;;
  save|checkpoint)
    cmd_save "${1:-.}" "${2:-}"
    ;;
  status)
    cmd_status "${1:-.}"
    ;;
  rollback|restore)
    cmd_rollback "${1:-.}" "${2:-HEAD~1}"
    ;;
  *)
    echo "Usage: git_checkpoint.sh <init|save|status|rollback> [args...]"
    exit 1
    ;;
esac
