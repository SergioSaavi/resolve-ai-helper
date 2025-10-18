#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DaVinci Resolve Script: Test EXE Roundtrip by Placing Subtitle

Flow:
1) Find resolve_ai_helper.exe (onedir or onefile) next to this script
2) Run: resolve_ai_helper.exe transcribe --show-ui (press "Place Test Subtitle" in UI)
   OR run generate-test-srt for headless test
3) Parse JSON for srt_path
4) Import that SRT into the current timeline

Use this to validate that Resolve -> EXE -> Resolve roundtrip works
without requiring paid API features for control.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
import tempfile


def find_executable(script_dir: Path) -> Path:
    exe = script_dir / "resolve_ai_helper.exe"
    onedir = script_dir / "resolve_ai_helper" / "resolve_ai_helper.exe"
    if onedir.exists():
        return onedir
    if exe.exists():
        return exe
    return None


def get_resolve_objects():
    # Prefer Resolve-provided globals when launched from the Scripts menu
    resolve_g = globals().get('resolve')
    project_g = globals().get('project')
    timeline_g = globals().get('timeline')
    if resolve_g and (project_g or project_g is None):
        # Some environments omit project/timeline globals
        try:
            if not project_g:
                project_g = resolve_g.GetProjectManager().GetCurrentProject()
            if not timeline_g and project_g:
                timeline_g = project_g.GetCurrentTimeline()
        except Exception:
            pass
        if resolve_g and project_g and timeline_g:
            return resolve_g, project_g, timeline_g
    # Fallback to module import
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            raise RuntimeError("Could not connect to DaVinci Resolve")
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject()
        if not project:
            raise RuntimeError("No project open")
        timeline = project.GetCurrentTimeline()
        if not timeline:
            raise RuntimeError("No timeline open")
        return resolve, project, timeline
    except ImportError:
        raise RuntimeError("This script must be run from inside DaVinci Resolve.")


def import_srt(project, timeline, srt_path: Path) -> bool:
    media_pool = project.GetMediaPool()
    items = media_pool.ImportMedia([str(srt_path)])
    if not items:
        print("Error: ImportMedia failed")
        return False
    srt_item = items[0]
    subtitle_tracks = timeline.GetTrackCount("subtitle")
    if subtitle_tracks == 0:
        timeline.AddTrack("subtitle")
        subtitle_tracks = 1
    start_frame = timeline.GetStartFrame()
    ok = media_pool.AppendToTimeline([
        {
            "mediaPoolItem": srt_item,
            "trackIndex": subtitle_tracks,
            "startFrame": start_frame,
        }
    ])
    if ok:
        print("✓ Subtitle placed from EXE output")
    return bool(ok)


def main():
    print("=" * 60)
    print(" Resolve AI Helper - Test EXE Roundtrip")
    print("=" * 60)

    # Determine script dir in Resolve
    try:
        script_dir = Path(__file__).parent
    except NameError:
        if sys.argv and sys.argv[0]:
            script_dir = Path(sys.argv[0]).parent
        else:
            script_dir = Path(os.path.expandvars(r"%APPDATA%/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Comp"))

    exe_path = find_executable(script_dir)
    if not exe_path:
        print("❌ resolve_ai_helper.exe not found next to this script.")
        return 1

    # Persistent interactive session: keep UI open; talk via stdin/stdout
    print(f"Running UI supervisor (interactive) against: {exe_path}")
    try:
        _, project, timeline = get_resolve_objects()
    except Exception as e:
        print(f"❌ {e}")
        return 1

    # Start interactive exe
    try:
        proc = subprocess.Popen(
            [str(exe_path), "transcribe", "--show-ui", "--interactive", "--timeline-name", "Test"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(f"❌ Failed to start exe: {e}")
        return 1

    print("UI launched. Send commands from Resolve by triggering UI buttons, or script can also write commands.")
    print("Waiting for JSON payloads... close UI or send shutdown to end.")

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                # Process ended
                code = proc.poll()
                if code is not None:
                    print(f"Process exited with code {code}")
                    break
                continue
            line = line.strip()
            if not line:
                continue
            # Parse JSON payload
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                # Ignore non-JSON lines
                continue

            if not payload.get("success") and payload.get("error") == "cancel":
                print("Received cancel payload. Supervisor exiting.")
                break

            srt_path = payload.get("srt_path")
            if srt_path:
                p = Path(srt_path)
                if p.exists():
                    if import_srt(project, timeline, p):
                        print("✓ Imported subtitle from exe payload. Waiting for next action...")
                else:
                    print(f"⚠ SRT path not found: {p}")
    finally:
        try:
            if proc.stdin:
                proc.stdin.write('{"cmd":"shutdown"}\n')
                proc.stdin.flush()
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
