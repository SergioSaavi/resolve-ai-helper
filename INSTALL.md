# Installation Guide

Complete installation instructions for Resolve AI Helper on Windows.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Method 1: Installer (Recommended)](#method-1-installer-recommended)
  - [Method 2: Manual Installation](#method-2-manual-installation)
- [First-Time Setup](#first-time-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. DaVinci Resolve

**Download and install DaVinci Resolve** (Free or Studio version):
- Download from: https://www.blackmagicdesign.com/products/davinciresolve/
- Both Free and Studio versions are supported
- Minimum version: 17.0 (recommended: latest version)

### 2. FFmpeg

FFmpeg is required for video/audio processing.

#### Windows Installation Options

**Option A: Chocolatey (Easiest)**
```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg -y
```

**Option B: Manual Installation**
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg` (or location of your choice)
3. Add to PATH:
   - Open Start Menu → Search "Environment Variables"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\ffmpeg\bin`
   - Click "OK" on all windows
4. Verify installation:
   ```powershell
   ffmpeg -version
   ```

### 3. System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space (more for larger models)
- **GPU** (optional): NVIDIA GPU with CUDA support for faster transcription

---

## Installation Methods

### Method 1: Installer (Recommended)

**Coming Soon!** The installer will automate the entire process.

For now, use Method 2 (Manual Installation).

### Method 2: Manual Installation

#### Step 1: Download Release

1. Go to [Releases](https://github.com/your-repo/resolve-ai-helper/releases)
2. Download the latest `resolve-ai-helper-vX.X.X-windows.zip`
3. Extract to a permanent location (e.g., `C:\Program Files\resolve-ai-helper\`)

#### Step 2: Add Executable to PATH (Optional but Recommended)

**Why?** This allows the executable to be found from anywhere.

1. Note the path where you extracted (e.g., `C:\Program Files\resolve-ai-helper\`)
2. Add to PATH:
   - Open Start Menu → Search "Environment Variables"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add your extraction path
   - Click "OK" on all windows

**Verify**:
```powershell
resolve_ai_helper --version
```

#### Step 3: Install Resolve Script

Copy the Resolve script to the scripts directory:

```powershell
# Source file
$source = "C:\Program Files\resolve-ai-helper\resolve_scripts\transcribe_timeline.py"

# Destination (Resolve scripts folder)
$dest = "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\"

# Create destination directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $dest

# Copy script
Copy-Item $source $dest
```

**Manual Copy Alternative:**
1. Navigate to extracted folder: `resolve_scripts/`
2. Copy `transcribe_timeline.py`
3. Paste into:
   ```
   C:\Users\YourUsername\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\
   ```

#### Step 4: Restart DaVinci Resolve

Close and reopen DaVinci Resolve for the script to appear in the menu.

---

## First-Time Setup

### 1. Launch DaVinci Resolve

Open DaVinci Resolve and load any project with a timeline.

### 2. Verify Script Installation

1. Go to **Workspace → Scripts**
2. You should see **transcribe_timeline** in the list
3. If not visible, check [Troubleshooting](#troubleshooting)

### 3. Test System

Before transcribing a full video, test your setup:

```powershell
# Open PowerShell and run:
resolve_ai_helper check-system
```

Expected output:
```
System Check:
  Version:     0.1.0
  FFmpeg:      ✓ Available
  CUDA/GPU:    ✓ Available  (or ✗ Not available)
```

### 4. First Transcription

1. Open a timeline in Resolve
2. Go to **Workspace → Scripts → transcribe_timeline**
3. Select **tiny** or **base** model for first test
4. Click **Transcribe**
5. Wait for model download (first run only, ~75-150MB)
6. Transcription will begin

---

## Verification

### Check Installation

Run these commands to verify everything is set up correctly:

```powershell
# 1. Check executable
resolve_ai_helper --version

# 2. Check FFmpeg
ffmpeg -version

# 3. Check system compatibility
resolve_ai_helper check-system

# 4. List available models
resolve_ai_helper check-models
```

### Test Transcription (Optional)

Test with a short video file:

```powershell
# Download a test video or use your own
resolve_ai_helper transcribe --input test_video.mp4 --model tiny --show-ui
```

---

## Troubleshooting

### Script Not Appearing in Resolve

**Problem**: Can't find script in Workspace → Scripts menu

**Solutions**:
1. Verify script location:
   ```powershell
   Test-Path "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\transcribe_timeline.py"
   ```
   Should return `True`

2. Check file permissions (shouldn't be read-only)

3. Restart DaVinci Resolve completely

4. Check Resolve version (minimum 17.0)

### "resolve_ai_helper.exe not found"

**Problem**: Script can't find the executable

**Solutions**:
1. Verify executable location:
   ```powershell
   where.exe resolve_ai_helper
   ```
   
2. If not in PATH, edit `resolve_scripts/transcribe_timeline.py` line ~30:
   ```python
   # Add explicit path
   exe_path = Path(r"C:\Program Files\resolve-ai-helper\resolve_ai_helper.exe")
   ```

3. Ensure executable has execute permissions

### FFmpeg Not Found

**Problem**: "FFmpeg not found" error

**Solutions**:
1. Verify FFmpeg is installed:
   ```powershell
   ffmpeg -version
   ```
   
2. If not found, reinstall FFmpeg (see Prerequisites)

3. Restart terminal after PATH changes

### Model Download Fails

**Problem**: Model download times out or fails

**Solutions**:
1. Check internet connection

2. Check firewall isn't blocking downloads

3. Manually download model:
   - Models cache in: `%USERPROFILE%\.cache\resolve-ai-helper\models\`
   - Download from: https://huggingface.co/guillaumekln/faster-whisper-base

4. Try smaller model first (tiny)

### CUDA/GPU Not Detected

**Problem**: GPU transcription not working

**Solutions**:
1. Verify NVIDIA GPU is installed:
   ```powershell
   nvidia-smi
   ```

2. Install/Update CUDA Toolkit:
   - Download from: https://developer.nvidia.com/cuda-downloads

3. Use CPU mode (slower but works everywhere):
   - Select "CPU only" in the UI

### Permission Errors

**Problem**: "Access Denied" errors

**Solutions**:
1. Run as Administrator (one time):
   - Right-click PowerShell → Run as Administrator
   - Navigate to install location
   - Try installation again

2. Check antivirus isn't blocking executable

3. Choose different installation location with write access

---

## Uninstallation

To remove Resolve AI Helper:

1. **Remove executable**:
   ```powershell
   Remove-Item "C:\Program Files\resolve-ai-helper" -Recurse -Force
   ```

2. **Remove Resolve script**:
   ```powershell
   Remove-Item "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\transcribe_timeline.py"
   ```

3. **Remove cached models** (optional):
   ```powershell
   Remove-Item "$env:USERPROFILE\.cache\resolve-ai-helper" -Recurse -Force
   ```

4. **Remove from PATH** (if added):
   - Open Environment Variables
   - Edit Path
   - Remove resolve-ai-helper entry

---

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for usage guide
- Check [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for advanced features
- Join our community discussions

---

**Still having issues?** Open an issue on [GitHub Issues](https://github.com/your-repo/resolve-ai-helper/issues) with:
- Your Windows version
- DaVinci Resolve version
- Error messages
- Output of `resolve_ai_helper check-system`

