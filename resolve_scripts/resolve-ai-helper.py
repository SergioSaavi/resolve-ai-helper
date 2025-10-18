#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DaVinci Resolve Script: AI Helper - Transcription & More

Flow:
1) Find resolve_ai_helper.exe (onedir or onefile) next to this script
2) Run: resolve_ai_helper.exe transcribe --show-ui --interactive
3) UI stays open, receives live timeline updates every 500ms
4) User actions (transcribe, test subtitle) emit JSON responses
5) This script imports SRT files back into the timeline

Use this as the main integration point between DaVinci Resolve and AI Helper.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
import time
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
        print("✓ Subtitle placed from AI Helper")
    return bool(ok)


def main():
    print("=" * 60)
    print(" Resolve AI Helper - Live Integration")
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
    print(f"Launching AI Helper UI (interactive mode): {exe_path}")
    try:
        _, project, timeline = get_resolve_objects()
    except Exception as e:
        print(f"❌ {e}")
        return 1

    # Start interactive exe
    try:
        proc = subprocess.Popen(
            [str(exe_path), "transcribe", "--show-ui", "--interactive", "--timeline-name", timeline.GetName()],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(f"❌ Failed to start AI Helper: {e}")
        return 1

    print("✓ UI launched. Streaming live timeline state...")

    # --- Timeline polling and event streaming ---
    def frames_to_tc(frames: int, fps: float) -> str:
        if fps <= 0:
            return "00:00:00:00"
        hours = int(frames // (3600 * fps))
        minutes = int((frames % (3600 * fps)) // (60 * fps))
        seconds = int((frames % (60 * fps)) // fps)
        ff = int(frames % fps)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{ff:02d}"

    def send_timeline_state():
        # Refresh timeline reference to detect switches
        try:
            current_tl = project.GetCurrentTimeline()
            if not current_tl:
                return
        except Exception as e:
            return

        try:
            fps = float(current_tl.GetSetting("timelineFrameRate"))
        except Exception as e:
            fps = 24.0
        try:
            name = current_tl.GetName()
        except Exception as e:
            name = "Timeline"
        try:
            current_f = current_tl.GetCurrentTimecode()  # may return string on some versions
            if isinstance(current_f, str):
                tc = current_f
            else:
                tc = frames_to_tc(int(current_f), fps)
        except Exception as e:
            tc = "00:00:00:00"
        try:
            # Use the correct API method: GetMarkInOut()
            # Returns dict like {'video': {'in': 0, 'out': 134}, 'audio': {'in': 0, 'out': 134}}
            # Keys are omitted if marks not set
            marks = current_tl.GetMarkInOut()
            
            # Try to extract video in/out marks (prefer video, fallback to audio)
            video_marks = marks.get('video', {}) if marks else {}
            audio_marks = marks.get('audio', {}) if marks else {}
            
            # Use video marks if available, otherwise audio marks
            in_f = video_marks.get('in') if video_marks else audio_marks.get('in')
            out_f = video_marks.get('out') if video_marks else audio_marks.get('out')
            
            # Only use marks if both in and out are set
            if in_f is not None and out_f is not None and in_f >= 0 and out_f > in_f:
                in_tc = frames_to_tc(int(in_f), fps)
                out_tc = frames_to_tc(int(out_f), fps)
                range_seconds = (out_f - in_f) / max(fps, 0.001)
            else:
                # No in/out marks set
                in_tc = None
                out_tc = None
                range_seconds = None
        except Exception as e:
            in_tc = None
            out_tc = None
            range_seconds = None

        evt = {
            "event": "timeline_state",
            "timeline": {
                "name": name,
                "fps": f"{fps:.2f}",
                "tc": tc,
                "in_tc": in_tc,
                "out_tc": out_tc,
                "range_seconds": range_seconds,
            }
        }
        try:
            if proc.stdin:
                proc.stdin.write(json.dumps(evt) + "\n")
                proc.stdin.flush()
        except Exception as e:
            pass

    # Use a thread to read stdout without blocking the polling loop
    import threading
    import queue
    stdout_q = queue.Queue()
    
    def read_stdout():
        try:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    stdout_q.put(line.strip())
        except Exception:
            pass
    
    reader_thread = threading.Thread(target=read_stdout, daemon=True)
    reader_thread.start()

    try:
        last_sent = 0.0
        poll_count = 0
        while True:
            now = time.time()
            # Poll timeline state every 500ms
            if now - last_sent >= 0.5:
                poll_count += 1
                send_timeline_state()
                last_sent = now

            # Check if process ended
            code = proc.poll()
            if code is not None:
                print(f"AI Helper closed (exit code {code})")
                break

            # Check for JSON responses from exe (non-blocking)
            try:
                while True:
                    line = stdout_q.get_nowait()
                    if not line:
                        continue
                    # Parse JSON payload
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError as e:
                        # Ignore non-JSON lines
                        continue

                    if not payload.get("success") and payload.get("error") == "cancel":
                        print("User cancelled. Closing...")
                        raise StopIteration

                    srt_path = payload.get("srt_path")
                    if srt_path:
                        p = Path(srt_path)
                        if p.exists():
                            if import_srt(project, timeline, p):
                                print("✓ Subtitle imported successfully. Ready for next action...")
                        else:
                            print(f"⚠ SRT file not found: {p}")
            except queue.Empty:
                pass
            except StopIteration:
                break

            # Small sleep to avoid busy loop
            time.sleep(0.05)
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

