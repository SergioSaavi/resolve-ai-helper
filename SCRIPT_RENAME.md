# Script Rename: Production-Ready Name

## ✅ What Changed

**Old name:** `test_exe_place_subtitle.py` ❌
**New name:** `resolve-ai-helper.py` ✅

## 📝 Rationale

The old name sounded like a test/debug script, but this is actually the **main production script** that users run from DaVinci Resolve. The new name:

- ✅ **Clear purpose** - Obviously the main AI helper script
- ✅ **Professional** - Not "test" or "debug" in the name
- ✅ **Descriptive** - Tells users exactly what it is
- ✅ **Matches branding** - Consistent with the project name
- ✅ **Kebab-case** - Modern naming convention for scripts

## 📍 Location

```
resolve_scripts/
  └── resolve-ai-helper.py  ← Main script (persistent, interactive)
  └── launch_transcribe_ui.py (one-shot launcher)
  └── place_test_subtitle.py (simple test)
  └── ... (other utilities)
```

## 🚀 How to Use

### From DaVinci Resolve

1. **Copy the script** to Resolve's scripts folder:
   ```
   %PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\
   ```

2. **In Resolve:**
   - Open your timeline
   - Go to: **Workspace → Scripts → Comp → resolve-ai-helper**
   - The UI launches and stays open for multiple actions

### What It Does

```
┌─────────────────────────────────────────────┐
│  DaVinci Resolve                            │
│  • Run: Workspace → Scripts → resolve-ai...│
└──────────────┬──────────────────────────────┘
               │
               ├─ Launches resolve_ai_helper.exe --interactive
               │
               ├─ Polls timeline every 500ms
               │  └─ Name, FPS, Timecode, In/Out, Selection
               │
               ├─ Sends live updates to UI
               │  └─ UI shows current timeline state
               │
               ├─ Receives JSON responses from UI
               │  └─ Transcribe complete, Test subtitle, etc.
               │
               └─ Imports SRT files back to timeline
                  └─ Auto-creates subtitle track if needed
```

## 🔄 What Was Updated

### Files Changed:
- ✅ `resolve_scripts/test_exe_place_subtitle.py` → `resolve_scripts/resolve-ai-helper.py`
- ✅ `README.md` - Updated all references
- ✅ `UI_PREVIEW.md` - Updated documentation

### What's the Same:
- ✅ All functionality preserved
- ✅ Live polling every 500ms
- ✅ In/Out mark detection (with fix!)
- ✅ Interactive mode
- ✅ JSON protocol
- ✅ SRT import logic

## 📋 Script Features

### Main Features:
1. **Live Timeline Polling** (500ms intervals)
   - Timeline name
   - Frame rate
   - Current timecode
   - In/Out marks (using GetMarkInOut API)
   - Selection info

2. **Interactive Mode**
   - UI stays open for multiple actions
   - Send commands via JSON
   - Receive responses via JSON
   - Non-blocking stdout reading

3. **Auto SRT Import**
   - Detects when transcription completes
   - Imports SRT to timeline
   - Auto-creates subtitle track
   - Places at timeline start

4. **Clean Shutdown**
   - Handles user cancel
   - Sends shutdown command
   - Terminates exe gracefully
   - Cleanup on exit

## 🎯 Usage Examples

### Run from Resolve Scripts Menu
```python
# User clicks: Workspace → Scripts → Comp → resolve-ai-helper
# Script automatically:
# 1. Finds resolve_ai_helper.exe
# 2. Launches in interactive mode
# 3. Starts polling timeline
# 4. Keeps UI open
# 5. Imports results back to timeline
```

### What Users See
```
============================================================
 Resolve AI Helper - Live Integration
============================================================
Launching AI Helper UI (interactive mode): C:\...\resolve_ai_helper.exe
✓ UI launched. Streaming live timeline state...

[UI shows live updates every 500ms]
Timeline: viktor-shitshow-16-10-25.mp4
FPS: 24.00
Timecode: 01:25:41:15
In/Out: 01:13:52:00 → 01:27:44:00 (832.00s)

[User clicks Transcribe in UI]
✓ Subtitle imported successfully. Ready for next action...

[User closes UI]
User cancelled. Closing...
AI Helper closed (exit code 0)
```

## 🔧 Technical Details

### Polling System
- **Interval:** 500ms (2 Hz)
- **API Used:** `GetMarkInOut()` for in/out marks
- **Format:** JSON events over stdin
- **Thread:** Non-blocking stdout reader

### JSON Protocol
```json
// Sent to UI (every 500ms)
{
  "event": "timeline_state",
  "timeline": {
    "name": "Timeline Name",
    "fps": "24.00",
    "tc": "01:25:41:15",
    "in_tc": "01:13:52:00",     // null if not set
    "out_tc": "01:27:44:00",    // null if not set
    "range_seconds": 832.0      // null if not set
  }
}

// Received from UI (on action complete)
{
  "success": true,
  "srt_path": "C:\\path\\to\\output.srt"
}

// User cancel
{
  "success": false,
  "error": "cancel"
}
```

### Error Handling
- ✅ Missing exe detection
- ✅ Resolve connection failures
- ✅ Timeline API errors
- ✅ JSON parsing errors
- ✅ Process crashes
- ✅ SRT import failures

## 📖 Related Documentation

- `README.md` - Project overview and usage
- `UI_PREVIEW.md` - UI design and live features
- `RESOLVE_DESIGN.md` - Resolve-inspired design system
- `resolve_docs.txt` - Complete Resolve API reference

## ✨ Summary

The script has been renamed to reflect its role as the **main production integration script** between DaVinci Resolve and the AI Helper. All functionality is preserved, and all documentation has been updated to use the new name.

**Old:** `test_exe_place_subtitle.py` (sounds like a test)
**New:** `resolve-ai-helper.py` (sounds professional!)

---

**Result:** A professional script name that clearly communicates its purpose! 🎬

