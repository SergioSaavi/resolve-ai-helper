# Testing Guide for Resolve AI Helper

This guide helps you test the implementation before releasing to users.

## Prerequisites

- Python 3.9+ installed
- DaVinci Resolve installed (Free or Studio)
- FFmpeg installed and in PATH
- Test video file (5-10 minutes recommended)

## Phase 1: Development Environment Testing

### 1.1 Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 1.2 Run Unit Tests

```bash
python tests/test_basic.py
```

**Expected output:**
- All tests should pass (✓)
- FFmpeg warning is OK if not installed yet

### 1.3 Test CLI Directly

```bash
# Check version
python core/cli.py --version

# Check system
python core/cli.py check-system

# List models
python core/cli.py check-models
```

**Expected output:**
- Version number displays
- System check shows FFmpeg and CUDA status
- Models list shows tiny, base, small, medium

### 1.4 Test Headless Transcription (Optional)

If you have a test video:

```bash
python core/cli.py transcribe --input path/to/test.mp4 --model tiny --device cpu
```

**Expected:**
- Progress messages in stderr
- JSON output on success
- SRT file created

## Phase 2: Executable Building

### 2.1 Build the Executable

```bash
python build_exe.py --full
```

**Expected output:**
- Build completes without errors
- Executable created in `dist/resolve_ai_helper.exe`
- Tests pass
- Distribution package created

**Troubleshooting:**
- If build fails, check PyInstaller installation
- Ensure all dependencies are installed
- Check error messages for missing modules

### 2.2 Test Executable

```bash
# Check version
dist\resolve_ai_helper.exe --version

# Check system
dist\resolve_ai_helper.exe check-system --json

# List models
dist\resolve_ai_helper.exe check-models
```

**Expected:**
- Executable runs without errors
- Commands work same as Python version
- No console errors

### 2.3 Test UI (Without Resolve)

```bash
# This will open the UI window
dist\resolve_ai_helper.exe transcribe --input test.mp4 --show-ui --timeline-name "Test"
```

**Expected:**
- Settings window appears
- UI is responsive
- Dropdowns work
- Can close window without errors

## Phase 3: DaVinci Resolve Integration

### 3.1 Install Resolve Script

```bash
# Copy script to Resolve
$dest = "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\"
New-Item -ItemType Directory -Force -Path $dest
Copy-Item resolve_scripts\transcribe_timeline.py $dest
```

### 3.2 Ensure Executable is Findable

Option A: Add to PATH
```bash
# Add dist folder to PATH temporarily
$env:PATH += ";$(Get-Location)\dist"
```

Option B: Copy executable to Resolve scripts folder
```bash
Copy-Item dist\resolve_ai_helper.exe "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\"
```

### 3.3 Test in Resolve

1. **Restart DaVinci Resolve** (important!)

2. **Open a test project:**
   - Create new project or open existing
   - Import a short test video (5-10 minutes)
   - Create a timeline with the video

3. **Run the script:**
   - Go to Workspace → Scripts
   - Look for "transcribe_timeline"
   - Click it

4. **Expected behavior:**
   - Console window appears with status messages
   - Executable should be found
   - Connection to Resolve succeeds
   - Timeline info displays

5. **Expected issues (DEBUG MODE):**
   - Timeline export is currently skipped (DEBUG MODE marker)
   - This is expected - framework is ready but not fully implemented

### 3.4 Test With UI

If executable is found and called:

1. **Settings window should appear:**
   - Timeline name shown
   - Model selection available
   - Device selection available
   - Language selection available

2. **Click Transcribe:**
   - Window closes
   - Progress window appears

3. **Progress tracking:**
   - Progress bar updates
   - Log messages appear
   - Stats update (if successful)

4. **Result handling:**
   - Success dialog on completion
   - Error dialog on failure

## Phase 4: End-to-End Testing

### 4.1 Complete Workflow Test

This is the ultimate test. You'll need to:

1. **Remove DEBUG MODE from Resolve script:**
   - Open `resolve_scripts/transcribe_timeline.py`
   - Find the `# Step 4: Export timeline` section
   - Uncomment the actual export code
   - Remove the debug skip

2. **Prepare test timeline:**
   - Short video (< 5 minutes for faster testing)
   - Clean audio
   - Known language (English recommended)

3. **Run complete workflow:**
   - Scripts → transcribe_timeline
   - Select "tiny" model (fastest)
   - Wait for completion
   - Check timeline for subtitles

4. **Verify results:**
   - Subtitles appear in timeline
   - Timing is roughly correct
   - Text is legible
   - Can be edited in Inspector

### 4.2 Test Different Scenarios

**Test Case 1: Different Models**
- Repeat with tiny, base, small models
- Compare speed and accuracy
- Verify all models download correctly

**Test Case 2: Different Languages**
- Test with non-English audio
- Try auto-detect vs. specified language
- Verify results are reasonable

**Test Case 3: Different Video Lengths**
- Short (< 5 min)
- Medium (10-20 min)
- Long (30+ min)
- Verify no crashes or hangs

**Test Case 4: Error Scenarios**
- No timeline open → Should show error
- Empty timeline → Should show error
- No internet (after models cached) → Should work
- Cancel mid-transcription → Should handle gracefully

**Test Case 5: GPU vs CPU**
- If GPU available, test both modes
- Verify speed difference
- Verify both produce valid output

## Phase 5: Installation Testing

### 5.1 Clean Machine Test (Ideal)

If possible, test on a clean Windows machine:

1. **Only install:**
   - DaVinci Resolve
   - FFmpeg

2. **Follow INSTALL.md exactly:**
   - Step by step
   - Note any issues
   - Time how long it takes

3. **Follow QUICKSTART.md:**
   - Complete first transcription
   - Note any confusing parts
   - Suggest improvements

### 5.2 User Simulation

Pretend you know nothing about the code:

1. Read only the documentation
2. Try to install without looking at source
3. Try to use without technical knowledge
4. Document all pain points

## Testing Checklist

### ✅ Development

- [ ] Unit tests pass
- [ ] CLI version works
- [ ] CLI check-system works
- [ ] CLI check-models works
- [ ] Headless transcription works
- [ ] No import errors

### ✅ Build

- [ ] Executable builds without errors
- [ ] Executable runs standalone
- [ ] UI appears when requested
- [ ] No missing DLL errors
- [ ] Reasonable file size (< 500MB)

### ✅ Resolve Integration

- [ ] Script appears in menu
- [ ] Executable is found
- [ ] Timeline info extracted
- [ ] UI appears from Resolve
- [ ] Settings are applied
- [ ] Progress is shown

### ✅ Transcription

- [ ] Model downloads successfully
- [ ] Progress updates work
- [ ] Transcription completes
- [ ] SRT file is created
- [ ] SRT content is valid
- [ ] Timing is accurate

### ✅ Timeline Import

- [ ] SRT imports to timeline
- [ ] Subtitles are visible
- [ ] Timing matches video
- [ ] Can be edited
- [ ] Exports correctly

### ✅ Error Handling

- [ ] No timeline → Clear error
- [ ] FFmpeg missing → Clear error
- [ ] Model download fails → Clear error
- [ ] Transcription fails → Clear error
- [ ] Cancellation works

### ✅ Documentation

- [ ] README is clear
- [ ] INSTALL.md is complete
- [ ] QUICKSTART.md is helpful
- [ ] No broken links
- [ ] Screenshots present (or marked TODO)

## Known Limitations (Document These)

Current limitations to note:

1. **Timeline export**: Framework ready, needs testing
2. **SRT import**: Needs validation with real Resolve
3. **Cross-platform**: Windows only for now
4. **Model sizes**: Large models not tested
5. **Long videos**: > 2 hours not tested

## Performance Benchmarks

Document performance on your system:

| Video Length | Model | Device | Time | Notes |
|--------------|-------|--------|------|-------|
| 5 min | tiny | CPU | ? min | |
| 5 min | base | CPU | ? min | |
| 5 min | base | GPU | ? min | |
| 30 min | base | CPU | ? min | |
| 30 min | base | GPU | ? min | |

## Reporting Issues

When you find issues:

1. **Note the exact error message**
2. **Document steps to reproduce**
3. **Check logs** in `%USERPROFILE%\.cache\resolve-ai-helper\logs\`
4. **Save screenshots**
5. **Note system info:**
   - Windows version
   - Resolve version
   - GPU model (if applicable)
   - RAM amount

## Next Steps After Testing

Once testing is complete:

1. Fix critical bugs
2. Update documentation based on findings
3. Add screenshots to docs
4. Create demo video
5. Prepare first release
6. Create GitHub release notes

## Getting Help

If stuck during testing:

- Check implementation summary: `IMPLEMENTATION_SUMMARY.md`
- Review code comments
- Check error messages carefully
- Try simplest case first (tiny model, short video, CPU)

---

**Happy Testing! 🧪**

Remember: Finding issues now means users won't find them later!

