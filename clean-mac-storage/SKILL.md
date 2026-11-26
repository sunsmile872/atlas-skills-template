---
name: clean-mac-storage
description: >-
  Audits, diagnoses, and safely cleans macOS internal storage and memory pressure. Analyzes disk space, identifies large culprits (caches, heavy apps, VMs, Mail attachments, LINE cache, iCloud downloads), and executes approved safe cleanups.
---

# Clean Mac Storage (`clean-mac-storage`)

A dedicated skill for diagnosing, analyzing, and recovering storage and memory on macOS systems safely without data loss.

## When to Activate
Trigger this skill whenever the user asks:
- "internal memory ใกล้เต็ม", "storage เต็ม", "พื้นที่เครื่องใกล้เต็ม"
- "วิเคราะห์พื้นที่ mac", "เครื่องช้า เมมเต็ม", "clean mac storage"
- "ล้างแคช mac", "หาไฟล์ใหญ่ในเครื่อง", "disk space full"

---

## Safety Protocol (CRITICAL RULES)

> [!CAUTION] **STRICT SAFETY POLICY**
> 1. **PROPOSE BEFORE DELETING:** Never delete, move, or purge user files, caches, or applications without explaining what they are and obtaining explicit confirmation from the user.
> 2. **NEVER TOUCH DATABASES:** Never delete chat message databases (`db`, `sqlite`), Apple Notes database records, or active user documents.
> 3. **CATEGORIZE ACTIONS CLEARLY:** Always classify recommendations into:
>    - 🟢 **Safe Cache Cleanup:** Temporary files that can be wiped with zero loss (e.g., `uv cache clean`, Spotify playback cache, `CloudKit remindd` blobs, `~/.Trash`).
>    - 🟡 **Settings / Cloud Eviction:** Offload local copies without deleting the cloud originals (e.g., Mail "Download Attachments: None", Apple Books "Remove Download").
>    - 🔴 **User Application / Data Relocation:** Large VMs (`~/Parallels`), heavy apps (`/Applications`), or offloading to external SSDs (`<EXTERNAL_SSD>`).

---

## Standard Workflow

### Step 1: Automated Storage & Health Audit
Run the bundled audit script to get a real-time status of disk capacity, external drives, heavy applications, and storage hotspots:

```bash
python3 ~/.gemini/config/skills/clean-mac-storage/scripts/audit_storage.py
```
*(Or pass `--json` if programmatic parsing is needed).*

Evaluate the available capacity:
- **Free > 15%:** Healthy.
- **Free 10% – 15%:** Warning (SSD performance and APFS wear-leveling may begin degrading).
- **Free < 10%:** Critical (risk of system lockups, inability to allocate swap/virtual memory).

---

### Step 2: Analyze Hotspots & Culprits

Break down the findings into structured, readable tables matching professional markdown formatting:
1. **Installed Applications (`/Applications`):** Highlight applications $\ge$ 1 GB (e.g., `iMovie`, `Word`, `Excel`, `CapCut`).
2. **Virtual Machines & Containers (`~/Parallels`):**
   - Check `~/Parallels/*.pvm`. If a Windows VM is large (> 25 GB), do NOT just suggest moving it—**audit inside the Windows VM** using `prlctl exec "<VM_NAME>" cmd.exe /c ...` and `robocopy /L /S /XJ` to find what is bloating `C:\`:
     - `C:\Users\<user>\AppData\Roaming\IDM\DwnlData` (Internet Download Manager unfinished download chunks — often 10–50+ GB!)
     - `C:\$Recycle.Bin`, `C:\Windows\Temp`, `C:\Users\<user>\AppData\Local\Temp`
     - `C:\hiberfil.sys` (Windows Hibernation file — disable via `powercfg -h off`)
     - `C:\Program Files\WindowsApps` (Windows 11 Bloatware like `YourPhone`, `OfficeHub`, `MicrosoftTeams`, `GetHelp`, `Windows.Photos`, `ScreenSketch`, `Paint`, `Xbox*`, `WebExperience` Widgets)
3. **Caches:**
   - `~/.cache/uv` (Python wheels) & `~/.cache/huggingface` (ML model weights)
   - `~/Library/Application Support/Google/Chrome-headless` & `GoogleUpdater`
   - `~/Library/Group Containers/group.notability/ImportSessions` (Notability temporary import cache)
   - `~/Library/Caches/com.spotify.client` (Spotify media)
   - `~/Library/Caches/CloudKit` (Sync blobs)
   - `~/Library/Caches/ms-playwright` (Test browsers)
4. **Communication & Documents:**
   - **LINE for Mac:** Check `~/Library/Group Containers/VUTU7AKEUR.jp.naver.line.mac/Real/Library/Data/Caches` (media/link cache) vs `Data/db` (chat history).
   - **Apple Mail:** Check `~/Library/Mail/V10/.../Attachments`.
   - **iCloud Drive / Mobile Documents:** Check `~/Library/Mobile Documents/` (e.g., Notability, Books).

---

### Step 3: Propose Clear, Actionable Options to the User

Present the findings clearly, stating:
- How much space each item is using.
- What will happen if cleaned or adjusted.
- Exactly how much space will be reclaimed.
- Wait for user confirmation before executing any cleanup.

---

### Step 4: Execution Runbook (Upon User Approval)

#### 1. Safe Cache Cleanup (macOS):
```bash
# Python / uv & Hugging Face cache:
uv cache clean 2>/dev/null || rm -rf ~/.cache/uv
rm -rf ~/.cache/huggingface

# Google Headless & Updater caches:
rm -rf ~/Library/Application\ Support/Google/Chrome-headless
rm -rf ~/Library/Application\ Support/Google/GoogleUpdater

# Notability temporary import sessions:
rm -rf ~/Library/Group\ Containers/group.notability/ImportSessions/*

# Spotify client cache (quit gracefully first):
osascript -e 'quit app "Spotify"' 2>/dev/null
rm -rf ~/Library/Caches/com.spotify.client/Data/* ~/Library/Caches/com.spotify.client/Browser/*

# CloudKit remindd & updater caches:
rm -rf ~/Library/Caches/CloudKit/com.apple.remindd/*
rm -rf ~/Library/Caches/antigravity-updater/* ~/Library/Caches/com.apple.python/*

# Playwright browser cache:
rm -rf ~/Library/Caches/ms-playwright

# Empty Trash:
osascript -e 'tell application "Finder" to empty trash'
```

#### 2. LINE for Mac Media Cache:
```bash
# Ensure LINE is closed first:
osascript -e 'quit app "LINE"' 2>/dev/null
# Clean ONLY the Caches directory (NEVER touch db or accounts):
rm -rf "~/Library/Group Containers/VUTU7AKEUR.jp.naver.line.mac/Real/Library/Data/Caches"/*
```

#### 3. Parallels Windows VM Deep Clean & Compaction (Shrink `.pvm` In-Place):
> [!IMPORTANT] **CRITICAL PARALLELS COMPACTION PROTOCOL**
> Deleting files inside Windows NTFS does **not** automatically shrink `.hdd` on macOS unless you run **`defrag C: /L /U` (NTFS ReTrim / SCSI UNMAP)** inside the running VM with `online-compact=on`, followed by **`prl_disk_tool compact`** after stopping the VM!

1. **Fast Folder Size Audit inside Windows VM (via `robocopy /L /XJ` — never hangs on junctions):**
   ```bash
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl start "Windows 11"
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl exec "Windows 11" cmd.exe /c 'for %d in ("C:\$Recycle.Bin" "C:\Program Files" "C:\Program Files (x86)" "C:\ProgramData" "C:\Users" "C:\Windows") do @(echo === %~d === & robocopy "%~d" C:\NULL_DUMMY /L /S /XJ /NFL /NDL /NJH /R:0 /W:0 | findstr /C:"Bytes :")'
   ```
2. **Clean IDM Temp Cache, Recycle Bin, Temp, & Hibernation + Point IDM `TempPath` to External SSD (`Y:\IDM_Temp\`):**
   ```bash
   mkdir -p "<EXTERNAL_SSD>/IDM_Temp/DwnlData/<USER>"
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl exec "Windows 11" --current-user cmd.exe /c 'taskkill /F /IM IDMan.exe 2>nul & reg add "HKCU\Software\DownloadManager" /v TempPath /t REG_SZ /d "Y:\IDM_Temp\\" /f'
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl exec "Windows 11" cmd.exe /c 'rd /s /q "C:\Users\ss\AppData\Roaming\IDM\DwnlData" & mklink /D "C:\Users\ss\AppData\Roaming\IDM\DwnlData" "Y:\IDM_Temp\DwnlData" & powercfg -h off & rd /s /q "C:\$Recycle.Bin" 2>nul & del /f /s /q "C:\Windows\Temp\*" 2>nul & del /f /s /q "C:\Users\ss\AppData\Local\Temp\*" 2>nul'
   ```
3. **Optional Windows 11 Bloatware Removal (`Remove-AppxPackage` & `Remove-AppxProvisionedPackage`):**
   - Safe to remove on a VM: `Microsoft.YourPhone`, `Microsoft.MicrosoftOfficeHub`, `MicrosoftTeams`, `Microsoft.GetHelp`, `microsoft.windowscommunicationsapps`, `MicrosoftWindows.Client.WebExperience`, `Microsoft.Xbox*`, `Microsoft.ZuneVideo`, `Microsoft.ZuneMusic`, `Microsoft.WindowsFeedbackHub`, `Microsoft.Getstarted`, `Microsoft.BingWeather`, `Microsoft.People`, `Microsoft.WindowsMaps`, `Microsoft.Windows.Photos`, `Microsoft.ScreenSketch`, `Microsoft.Paint`.
4. **ReTrim NTFS + Compact `.hdd` Image (Returns Freed GBs to macOS):**
   ```bash
   # Ensure online-compact is enabled on hdd0
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl set "Windows 11" --device-set hdd0 --online-compact on
   # Run NTFS ReTrim inside Windows to send SCSI UNMAP for deleted blocks
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl exec "Windows 11" cmd.exe /c "defrag C: /L /U /V"
   # Stop VM cleanly and compact the .hdd on macOS
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prlctl stop "Windows 11"
   /Applications/Parallels\ Desktop.app/Contents/MacOS/prl_disk_tool compact --hdd "~/Parallels/Windows 11.pvm/Windows 11-0.hdd"
   ```

#### 4. Apple Mail Attachments Optimization:
Guide the user to:
1. Open **Mail** > `Cmd + ,` (Settings).
2. Go to **Accounts** > Select account.
3. Set **Download Attachments** to **None** or **Recent**.

#### 5. Apple Books / iCloud "Remove Download":
In **Apple Books** > Right click book/PDF > **Remove Download** (preserves file on iCloud, frees SSD space).

#### 6. Move Virtual Machines to External Storage (Alternative Offload):
If an external drive (e.g. `<EXTERNAL_SSD>`) has ample space and user prefers full offload:
1. Shut down the VM and quit Parallels.
2. Move `~/Parallels/<VM_NAME>.pvm` to `<EXTERNAL_SSD>/Parallels/`.
3. Open the `.pvm` file from the external drive and choose "I Moved It".

---

### Step 5: Post-Cleanup Verification

Rerun the audit to verify the newly reclaimed space:
```bash
python3 ~/.gemini/config/skills/clean-mac-storage/scripts/audit_storage.py
```
Report the exact gigabytes reclaimed and the final healthy capacity to the user.
