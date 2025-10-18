#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
DaVinci Resolve Script: Transcribe Timeline to Subtitles (DEBUG VERSION)

This version logs everything to a file for debugging.
"""

import sys
import os
import subprocess
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime

# Resolve doesn't provide __file__, so we need to get the script path differently
try:
    script_dir = Path(__file__).parent
except NameError:
    # When running from Resolve, __file__ is not defined
    # Use sys.argv[0] or a default location
    if sys.argv and sys.argv[0]:
        script_dir = Path(sys.argv[0]).parent
    else:
        # Fallback to default Resolve Comp scripts location
        script_dir = Path(os.path.expandvars(r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp"))


# Setup logging
log_file = Path.home() / ".cache" / "resolve-ai-helper" / "logs" / f"resolve_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

def log(message):
    """Log message to file and print."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

log("=" * 60)
log(" Resolve AI Helper - DEBUG MODE")
log("=" * 60)
log(f"Log file: {log_file}")
log("")

try:
    log("Step 1: Finding executable...")
    log(f"Script directory: {script_dir}")
    
    exe_name = "resolve_ai_helper.exe"
    exe_path = script_dir / exe_name
    
    if exe_path.exists():
        log(f"[OK] Found executable: {exe_path}")
    else:
        log(f"[FAIL] Executable not found at: {exe_path}")
        log("Checking PATH...")
        
        # Check PATH
        for path in os.environ.get("PATH", "").split(os.pathsep):
            test_path = Path(path) / exe_name
            if test_path.exists():
                exe_path = test_path
                log(f"[OK] Found in PATH: {exe_path}")
                break
        else:
            log("[FAIL] Executable not found in PATH either")
            log("")
            log("ERROR: resolve_ai_helper.exe not found!")
            log("Please ensure it's in the same folder as this script.")
            log(f"\nLog saved to: {log_file}")
            sys.exit(1)
    
    log("")
    log("Step 2: Getting Resolve objects...")
    
    try:
        # When running from Workspace → Scripts menu, Resolve provides global objects!
        # Check if they're available
        resolve_obj = globals().get('resolve')
        project_obj = globals().get('project')
        timeline_obj = globals().get('timeline')
        
        if not resolve_obj:
            raise RuntimeError("'resolve' global not found. Script must be run from Resolve's Workspace → Scripts menu!")
        
        log("[OK] Found 'resolve' global object")
        
        # Try to get version
        try:
            version_list = resolve_obj.GetVersion()
            if version_list:
                version_str = '.'.join(map(str, version_list))
                log(f"  Resolve version: {version_str}")
        except:
            log("  (version method not available)")
        
        # Check project
        if not project_obj:
            log("[INFO] No 'project' global, getting from resolve...")
            project_manager = resolve_obj.GetProjectManager()
            project_obj = project_manager.GetCurrentProject()
            if not project_obj:
                raise RuntimeError("No project open")
        
        log(f"[OK] Project: {project_obj.GetName()}")
        
        # Check timeline
        if not timeline_obj:
            log("[INFO] No 'timeline' global, getting from project...")
            timeline_obj = project_obj.GetCurrentTimeline()
            if not timeline_obj:
                raise RuntimeError("No timeline open")
        
        log(f"[OK] Timeline: {timeline_obj.GetName()}")
        
    except ImportError as e:
        log(f"[FAIL] Import error: {e}")
        log("This script must be run from within DaVinci Resolve")
        log(f"\nLog saved to: {log_file}")
        sys.exit(1)
    except Exception as e:
        log(f"[FAIL] Error: {e}")
        log(f"\nLog saved to: {log_file}")
        sys.exit(1)
    
    log("")
    log("Step 3: Getting timeline info...")
    
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
    
    log(f"  Name: {timeline_name}")
    log(f"  Duration: {duration_str}")
    log(f"  FPS: {fps}")
    
    log("")
    log("Step 4: Testing executable...")
    
    # Test if executable runs
    test_cmd = [str(exe_path), "--version"]
    log(f"Running: {' '.join(test_cmd)}")
    
    try:
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        log(f"Exit code: {result.returncode}")
        log(f"Output: {result.stdout.strip()}")
        if result.stderr:
            log(f"Errors: {result.stderr.strip()}")
        
        if result.returncode != 0:
            log("[FAIL] Executable test failed!")
            log(f"\nLog saved to: {log_file}")
            sys.exit(1)
        
        log("[OK] Executable works!")
        
    except Exception as e:
        log(f"[FAIL] Error running executable: {e}")
        log(f"\nLog saved to: {log_file}")
        sys.exit(1)
    
    log("")
    log("=" * 60)
    log(" All checks passed!")
    log("=" * 60)
    log("")
    log("The integration is working correctly.")
    log("Next steps:")
    log("  1. Timeline export needs to be implemented")
    log("  2. Full transcription workflow needs testing")
    log(f"\nFull log saved to: {log_file}")
    log("\nScript complete. Check the log file for details.")
    
except Exception as e:
    log(f"\n[FAIL] UNEXPECTED ERROR: {e}")
    import traceback
    log(traceback.format_exc())
    log(f"\nFull log saved to: {log_file}")
    sys.exit(1)

