#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DaVinci Resolve Script: Transcribe Timeline to Subtitles

This script runs inside DaVinci Resolve and:
1. Exports the current timeline to a temporary video file
2. Calls the standalone executable to transcribe it
3. Imports the resulting SRT back into the timeline

Installation:
1. Copy this file to: %APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\
2. Ensure resolve_ai_helper.exe is in your PATH or in the same directory
3. Restart DaVinci Resolve
4. Run from: Workspace → Scripts → transcribe_timeline
"""

import sys
import os
import subprocess
import json
import tempfile
import time
from pathlib import Path


def find_executable():
    """Find the resolve_ai_helper executable."""
    # Check in PATH
    exe_name = "resolve_ai_helper.exe"
    
    # Method 1: Check PATH
    for path in os.environ["PATH"].split(os.pathsep):
        exe_path = Path(path) / exe_name
        if exe_path.exists():
            return exe_path
    
    # Method 2: Check script directory
    script_dir = Path(__file__).parent
    exe_path = script_dir / exe_name
    if exe_path.exists():
        return exe_path
    
    # Method 3: Check parent directory (if distributed together)
    parent_exe = script_dir.parent / exe_name
    if parent_exe.exists():
        return parent_exe
    
    return None


def get_resolve_objects():
    """Get Resolve scripting objects."""
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        
        if not resolve:
            raise RuntimeError("Could not connect to DaVinci Resolve")
        
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        
        if not project:
            raise RuntimeError("No project is currently open")
        
        timeline = project.GetCurrentTimeline()
        
        if not timeline:
            raise RuntimeError("No timeline is currently open")
        
        return resolve, project, timeline
        
    except ImportError:
        raise RuntimeError(
            "DaVinci Resolve scripting module not found.\n"
            "This script must be run from within DaVinci Resolve."
        )


def get_timeline_info(timeline):
    """Extract timeline information."""
    name = timeline.GetName()
    
    # Get timeline settings
    start_frame = timeline.GetStartFrame()
    end_frame = timeline.GetEndFrame()
    fps = float(timeline.GetSetting("timelineFrameRate"))
    
    # Calculate duration
    duration_frames = end_frame - start_frame
    duration_seconds = duration_frames / fps
    
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return {
        "name": name,
        "duration": duration_str,
        "duration_seconds": duration_seconds,
        "fps": f"{fps:.2f}",
        "start_frame": start_frame,
        "end_frame": end_frame
    }


def export_timeline(project, timeline, output_path):
    """
    Export timeline to video file.
    
    Args:
        project: Resolve project object
        timeline: Resolve timeline object
        output_path: Path to export video
    
    Returns:
        True if export succeeded
    """
    # Set up render settings for quick export
    render_settings = {
        "SelectAllFrames": True,
        "TargetDir": str(output_path.parent),
        "CustomName": output_path.stem,
        "ExportVideo": True,
        "ExportAudio": True,
        
        # Use H.264 for compatibility
        "VideoFormat": "mp4",
        "VideoCodec": "h264",
        
        # Quality settings (balanced)
        "VideoQuality": 0,  # 0 = automatic
        "EncodingProfile": "Main",
        "VideoFrameRate": str(timeline.GetSetting("timelineFrameRate")),
        
        # Audio settings
        "AudioCodec": "aac",
        "AudioBitDepth": "16",
        "AudioSampleRate": "48000",
    }
    
    # Apply render settings
    project.SetRenderSettings(render_settings)
    
    # Add to render queue
    project.SetCurrentRenderMode(1)  # Individual clips
    project.LoadRenderPreset("H.264 Master")  # Use standard preset
    
    # Update custom settings
    project.SetRenderSettings(render_settings)
    
    # Add render job
    job_id = project.AddRenderJob()
    
    if not job_id:
        return False
    
    # Start rendering
    project.StartRendering(job_id)
    
    # Wait for render to complete
    print("Exporting timeline...")
    
    while project.IsRenderingInProgress():
        time.sleep(1)
        print(".", end="", flush=True)
    
    print(" Done!")
    
    # Check if file was created
    return output_path.exists()


def call_transcribe_executable(exe_path, video_path, timeline_name):
    """
    Call the transcribe executable.
    
    Args:
        exe_path: Path to resolve_ai_helper.exe
        video_path: Path to video file to transcribe
        timeline_name: Name of the timeline
    
    Returns:
        Dictionary with result, or None on failure
    """
    cmd = [
        str(exe_path),
        "transcribe",
        "--input", str(video_path),
        "--show-ui",
        "--timeline-name", timeline_name
    ]
    
    print(f"Launching transcription tool...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout for long videos
        )
        
        if result.returncode == 0:
            # Parse JSON output
            try:
                response = json.loads(result.stdout)
                return response
            except json.JSONDecodeError:
                print(f"Warning: Could not parse output as JSON")
                print(f"Output: {result.stdout}")
                return None
        else:
            print(f"Error: Executable returned code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Error: Transcription timed out (> 2 hours)")
        return None
    except Exception as e:
        print(f"Error calling executable: {e}")
        return None


def import_srt_to_timeline(project, timeline, srt_path):
    """
    Import SRT file to timeline as subtitle track.
    
    Args:
        project: Resolve project object
        timeline: Resolve timeline object
        srt_path: Path to SRT file
    
    Returns:
        True if import succeeded
    """
    try:
        media_pool = project.GetMediaPool()
        
        # Import SRT to media pool
        imported_items = media_pool.ImportMedia([str(srt_path)])
        
        if not imported_items or len(imported_items) == 0:
            print("Error: Could not import SRT to media pool")
            return False
        
        srt_clip = imported_items[0]
        
        # Get current subtitle track count
        subtitle_track_count = timeline.GetTrackCount("subtitle")
        
        # Add subtitle track if needed
        if subtitle_track_count == 0:
            timeline.AddTrack("subtitle")
            subtitle_track_count = 1
        
        # Add SRT to subtitle track
        # Start at beginning of timeline
        start_frame = timeline.GetStartFrame()
        
        success = media_pool.AppendToTimeline([{
            "mediaPoolItem": srt_clip,
            "trackIndex": subtitle_track_count,
            "startFrame": start_frame
        }])
        
        if success:
            print(f"✓ Subtitles imported to track {subtitle_track_count}")
            return True
        else:
            print("Error: Could not add SRT to timeline")
            return False
            
    except Exception as e:
        print(f"Error importing SRT: {e}")
        return False


def cleanup_temp_files(*paths):
    """Clean up temporary files."""
    for path in paths:
        if path and Path(path).exists():
            try:
                Path(path).unlink()
                print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Warning: Could not delete {path}: {e}")


def main():
    """Main script entry point."""
    print("=" * 60)
    print(" Resolve AI Helper - Transcribe Timeline")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Find executable
        print("Finding resolve_ai_helper executable...")
        exe_path = find_executable()
        
        if not exe_path:
            print("❌ Error: resolve_ai_helper.exe not found!")
            print()
            print("Please ensure the executable is:")
            print("  1. In your system PATH, or")
            print("  2. In the same directory as this script, or")
            print("  3. In the parent directory of this script")
            print()
            print("Download from: https://github.com/your-repo/resolve-ai-helper/releases")
            input("\nPress Enter to exit...")
            return 1
        
        print(f"✓ Found executable: {exe_path}")
        print()
        
        # Step 2: Get Resolve objects
        print("Connecting to DaVinci Resolve...")
        try:
            resolve, project, timeline = get_resolve_objects()
            print("✓ Connected to Resolve")
        except RuntimeError as e:
            print(f"❌ Error: {e}")
            print()
            print("Please ensure:")
            print("  1. DaVinci Resolve is running")
            print("  2. A project is open")
            print("  3. A timeline is open and selected")
            input("\nPress Enter to exit...")
            return 1
        
        # Step 3: Get timeline info
        timeline_info = get_timeline_info(timeline)
        print(f"✓ Timeline: {timeline_info['name']}")
        print(f"  Duration: {timeline_info['duration']}")
        print()
        
        # Step 4: Export timeline
        print("Step 1/3: Exporting timeline...")
        temp_dir = Path(tempfile.gettempdir()) / "resolve-ai-helper"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_path = temp_dir / f"timeline_export_{timestamp}.mp4"
        
        # Note: Resolve export is complex, simplified here
        # In production, use proper render queue
        print(f"  Export path: {video_path}")
        print(f"  ⚠ Note: This may take several minutes for long timelines")
        print()
        
        # For now, we'll skip actual export and assume video_path exists
        # In real implementation, uncomment:
        # if not export_timeline(project, timeline, video_path):
        #     print("❌ Error: Timeline export failed")
        #     input("\nPress Enter to exit...")
        #     return 1
        
        # Temporary: Create a dummy file for testing
        # Remove this in production!
        print("⚠ DEBUG MODE: Skipping actual export")
        print("⚠ In production, timeline will be exported here")
        print()
        
        # Step 5: Call transcribe executable
        print("Step 2/3: Transcribing (this will open a separate window)...")
        result = call_transcribe_executable(exe_path, video_path, timeline_info['name'])
        
        if not result:
            print("❌ Transcription failed or was cancelled")
            cleanup_temp_files(video_path)
            input("\nPress Enter to exit...")
            return 1
        
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            print(f"❌ Transcription error: {error}")
            cleanup_temp_files(video_path)
            input("\nPress Enter to exit...")
            return 1
        
        print("✓ Transcription complete")
        print()
        
        # Step 6: Import SRT
        srt_path = result.get("srt_path")
        if not srt_path or not Path(srt_path).exists():
            print("❌ Error: SRT file not found")
            cleanup_temp_files(video_path)
            input("\nPress Enter to exit...")
            return 1
        
        print("Step 3/3: Importing subtitles to timeline...")
        if import_srt_to_timeline(project, timeline, srt_path):
            print("✓ Subtitles imported successfully!")
        else:
            print("⚠ Warning: Could not import subtitles automatically")
            print(f"  SRT file saved at: {srt_path}")
            print("  You can import it manually in Resolve")
        
        print()
        
        # Step 7: Cleanup
        print("Cleaning up temporary files...")
        cleanup_temp_files(video_path)
        
        print()
        print("=" * 60)
        print(" ✓ Complete!")
        print("=" * 60)
        print()
        print(f"Duration: {result.get('duration', 0):.1f}s")
        print(f"Language: {result.get('language', 'unknown')}")
        print(f"Segments: {result.get('segments_count', 0)}")
        print()
        
        input("Press Enter to close...")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())

