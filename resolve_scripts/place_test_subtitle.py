#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DaVinci Resolve Script: Place Test Subtitle in Timeline

Purpose: Quickly verify that we can place items into the current timeline
without running the external transcription tool. This script creates a
temporary SRT file with a single 5-second caption and imports it as a
subtitle track at the start of the current timeline.

Usage (inside Resolve): Workspace → Scripts → Comp → place_test_subtitle
"""

import sys
import tempfile
from pathlib import Path


def get_resolve_objects():
    """Get Resolve, Project, Timeline objects from the running app."""
    try:
        # When launched from the Scripts menu, Resolve provides this module
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
            "This script must be run from inside DaVinci Resolve (Workspace → Scripts)."
        )


def write_test_srt(path: Path):
    """Write a simple SRT file with a single caption lasting 5 seconds."""
    content = (
        "1\n"
        "00:00:00,000 --> 00:00:05,000\n"
        "Hello from Resolve AI Helper!\n\n"
    )
    path.write_text(content, encoding="utf-8")


def import_srt_to_timeline(project, timeline, srt_path: Path) -> bool:
    """Import SRT as a subtitle track at the start of the timeline."""
    try:
        media_pool = project.GetMediaPool()
        imported_items = media_pool.ImportMedia([str(srt_path)])
        if not imported_items:
            print("Error: Could not import SRT to media pool")
            return False

        srt_clip = imported_items[0]

        # Ensure at least one subtitle track exists
        subtitle_track_count = timeline.GetTrackCount("subtitle")
        if subtitle_track_count == 0:
            timeline.AddTrack("subtitle")
            subtitle_track_count = 1

        start_frame = timeline.GetStartFrame()
        success = media_pool.AppendToTimeline([
            {
                "mediaPoolItem": srt_clip,
                "trackIndex": subtitle_track_count,
                "startFrame": start_frame,
            }
        ])

        if success:
            print(f"✓ Placed test subtitle on track {subtitle_track_count}")
            return True
        else:
            print("Error: AppendToTimeline failed")
            return False
    except Exception as e:
        print(f"Error importing SRT: {e}")
        return False


def main():
    print("=" * 60)
    print(" Resolve AI Helper - Place Test Subtitle")
    print("=" * 60)
    try:
        _, project, timeline = get_resolve_objects()
        temp_dir = Path(tempfile.gettempdir()) / "resolve-ai-helper"
        temp_dir.mkdir(parents=True, exist_ok=True)
        srt_path = temp_dir / "test_subtitle.srt"
        write_test_srt(srt_path)

        if import_srt_to_timeline(project, timeline, srt_path):
            print("✓ Success! Test subtitle added to the current timeline.")
            print("  You should see a new subtitle clip at the start of the timeline.")
            return 0
        else:
            print("✗ Failed to place test subtitle.")
            return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


