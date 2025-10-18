#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions for Resolve AI Helper
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import shutil


def get_cache_dir() -> Path:
    """Get or create the cache directory for models and logs."""
    if sys.platform == "win32":
        cache_base = Path.home() / ".cache"
    elif sys.platform == "darwin":
        cache_base = Path.home() / "Library" / "Caches"
    else:
        cache_base = Path.home() / ".cache"
    
    cache_dir = cache_base / "resolve-ai-helper"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_models_dir() -> Path:
    """Get or create the models directory."""
    models_dir = get_cache_dir() / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_logs_dir() -> Path:
    """Get or create the logs directory."""
    logs_dir = get_cache_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_temp_dir() -> Path:
    """Get or create a temporary directory for video processing."""
    temp_base = Path(tempfile.gettempdir()) / "resolve-ai-helper"
    temp_base.mkdir(parents=True, exist_ok=True)
    return temp_base


def extract_audio(video_path: Path, output_path: Optional[Path] = None, 
                  sample_rate: int = 16000) -> Path:
    """
    Extract audio from video file using FFmpeg.
    
    Args:
        video_path: Path to input video file
        output_path: Optional output path for audio file
        sample_rate: Target sample rate in Hz (default: 16000 for Whisper)
    
    Returns:
        Path to extracted audio file
    
    Raises:
        RuntimeError: If FFmpeg is not found or extraction fails
    """
    if output_path is None:
        output_path = video_path.with_suffix(".wav")
    
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-i", str(video_path),
        "-ac", "1",  # Mono
        "-ar", str(sample_rate),
        "-vn",  # No video
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return output_path
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg not found. Please install FFmpeg and add it to your PATH.\n"
            "Download from: https://ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr}")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_srt_timestamp(seconds: float) -> str:
    """Format timestamp for SRT subtitle format."""
    milliseconds = int((seconds % 1) * 1000)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def validate_video_file(path: Path) -> bool:
    """Check if file exists and is a valid video file."""
    if not path.exists():
        return False
    
    valid_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.mxf', '.m4v', '.webm'}
    return path.suffix.lower() in valid_extensions


def json_response(success: bool, data: Dict[str, Any] = None, 
                  error: str = None) -> str:
    """Create a standardized JSON response for IPC."""
    response = {"success": success}
    
    if data:
        response.update(data)
    
    if error:
        response["error"] = error
    
    return json.dumps(response, ensure_ascii=False)


def parse_json_response(json_str: str) -> Dict[str, Any]:
    """Parse JSON response from executable."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse response: {e}"
        }


def cleanup_temp_files(*paths: Path):
    """Clean up temporary files and directories."""
    for path in paths:
        if path and path.exists():
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            except Exception as e:
                print(f"Warning: Failed to cleanup {path}: {e}", file=sys.stderr)


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available in PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def check_cuda_available() -> bool:
    """Check if CUDA is available for GPU acceleration."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

