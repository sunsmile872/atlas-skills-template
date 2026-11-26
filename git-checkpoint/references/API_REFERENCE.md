# 📚 GitHub API & Keychain Reference for `git-checkpoint`

## 1. macOS Keychain Credential Retrieval
The script queries macOS native credential helper:
```bash
printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain get
```
Output format:
```
username={{GITHUB_USER}}
password=ghp_************************************
```

## 2. GitHub REST API: Repository Creation
- **Endpoint**: `POST https://api.github.com/user/repos`
- **Headers**:
  - `Authorization: token <PAT>`
  - `Accept: application/vnd.github.v3+json`
- **Body**:
  ```json
  {
    "name": "<repo-name>",
    "description": "<description>",
    "homepage": "https://<username>.github.io/<repo-name>/",
    "private": false,
    "has_issues": true,
    "has_projects": true
  }
  ```

## 3. GitHub REST API: Enabling GitHub Pages
- **Endpoint**: `POST https://api.github.com/repos/<username>/<repo-name>/pages`
- **Headers**:
  - `Authorization: token <PAT>`
  - `Accept: application/vnd.github.v3+json`
- **Body**:
  ```json
  {
    "source": {
      "branch": "main",
      "path": "/"
    }
  }
  ```
- **Live Preview URL Pattern**:
  `https://<username>.github.io/<repo-name>/`
