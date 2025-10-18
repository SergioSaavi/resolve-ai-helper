#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
DaVinci Resolve Script: Launch Transcription UI

Run this from Workspace → Scripts to open the transcription UI
"""

import sys
import os
import subprocess
import json
import tempfile
from pathlib import Path

print("=" * 60)
print(" Resolve AI Helper - Transcribe Timeline")
print("=" * 60)
print()

try:
    # Step 1: Get Resolve objects from globals
    resolve_obj = globals().get('resolve')
    project_obj = globals().get('project')
    timeline_obj = globals().get('timeline')
    
    if not resolve_obj or not project_obj or not timeline_obj:
        print("[FAIL] Resolve objects not found")
        print("This script must be run from Resolve's Workspace -> Scripts menu")
        sys.exit(1)
    
    print(f"[OK] Project: {project_obj.GetName()}")
    print(f"[OK] Timeline: {timeline_obj.GetName()}")
    print()
    
    # Step 2: Get timeline info
    timeline_name = timeline_obj.GetName()
    start_frame = timeline_obj.GetStartFrame()
    end_frame = timeline_obj.GetEndFrame()
    fps = float(timeline_obj.GetSetting("timelineFrameRate"))
    
    duration_frames = end_frame - start_frame
    duration_seconds = duration_frames / fps
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    print(f"Timeline Info:")
    print(f"  Name: {timeline_name}")
    print(f"  Duration: {duration_str}")
    print(f"  FPS: {fps}")
    print()
    
    # Step 3: Find executable
    # Try script directory first
    try:
        script_dir = Path(__file__).parent
    except NameError:
        if sys.argv and sys.argv[0]:
            script_dir = Path(sys.argv[0]).parent
        else:
            script_dir = Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp")
    
    # Support both legacy onefile placement and new onedir folder
    exe_path = script_dir / "resolve_ai_helper.exe"
    onedir_exe = script_dir / "resolve_ai_helper" / "resolve_ai_helper.exe"
    
    if onedir_exe.exists():
        exe_path = onedir_exe
    elif not exe_path.exists():
        print(f"[FAIL] Executable not found. Checked:\n  - {onedir_exe}\n  - {exe_path}")
        print()
        print("Please copy either the onedir folder 'resolve_ai_helper' or the exe to:")
        print(f"  {script_dir}")
        sys.exit(1)
    
    print(f"[OK] Found exe: {exe_path}")
    print()
    
    # Step 4: Create temp file with timeline info (for future use)
    timeline_info = {
        "name": timeline_name,
        "duration": duration_str,
        "fps": str(fps)
    }
    
    temp_info_file = Path(tempfile.gettempdir()) / "resolve_timeline_info.json"
    with open(temp_info_file, 'w') as f:
        json.dump(timeline_info, f)
    
    print("Launching transcription UI...")
    print("(Timeline export not yet implemented - you'll need to browse for video)")
    print()
    
    # Step 5: Launch exe - it will open with UI
    # Note: Since we don't have a video file yet, the UI will open with file picker
    process = subprocess.Popen(
        [str(exe_path), "transcribe", "--timeline-name", timeline_name, "--show-ui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("UI launched! Check for the Resolve AI Helper window.")
    print()
    print("Note: This is a test launch. Full workflow will include:")
    print("  1. Export timeline to temp file (not yet implemented)")
    print("  2. Pass file to exe automatically")
    print("  3. Import resulting SRT back to timeline")
    
    # Don't wait for process to complete - let UI run independently
    print()
    print("Script complete. UI should be open now.")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

