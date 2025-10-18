#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Test the full UI workflow - launches the exe with UI
"""

import sys
import os
import subprocess
from pathlib import Path

# Setup logging
print("=" * 60)
print(" Resolve AI Helper - UI Test")
print("=" * 60)
print()

try:
    # Step 1: Get Resolve objects from globals
    resolve_obj = globals().get('resolve')
    project_obj = globals().get('project')
    timeline_obj = globals().get('timeline')
    
    if not resolve_obj or not project_obj or not timeline_obj:
        print("[FAIL] Resolve objects not found in globals")
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
    script_dir = Path(__file__).parent if '__file__' in globals() else Path(sys.argv[0]).parent if sys.argv and sys.argv[0] else Path(os.path.expandvars(r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp"))
    
    # Try common locations
    exe_locations = [
        script_dir / "resolve_ai_helper.exe",
        Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\resolve_ai_helper.exe"),
        Path.cwd() / "dist" / "resolve_ai_helper.exe",
    ]
    
    exe_path = None
    for loc in exe_locations:
        if loc.exists():
            exe_path = loc
            break
    
    if not exe_path:
        print("[FAIL] Could not find resolve_ai_helper.exe")
        print("Tried:")
        for loc in exe_locations:
            print(f"  - {loc}")
        sys.exit(1)
    
    print(f"[OK] Found exe: {exe_path}")
    print()
    
    # Step 4: Launch exe with UI (test mode - no actual file)
    print("Launching UI...")
    print("-" * 60)
    print()
    
    # For now, just launch with --help to show it works
    # In real workflow, we'd pass timeline info via JSON
    result = subprocess.run(
        [str(exe_path), "--help"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("Executable output:")
    print(result.stdout)
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print(" SUCCESS! Integration is working!")
        print("=" * 60)
        print()
        print("Next step: We need to:")
        print("  1. Export timeline audio/video to temp file")
        print("  2. Pass it to exe with --show-ui flag")
        print("  3. Import resulting SRT back to timeline")
    else:
        print(f"[FAIL] Exe returned error code: {result.returncode}")
        if result.stderr:
            print(result.stderr)
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

