#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic tests for Resolve AI Helper
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import __version__
from core.model_manager import ModelManager
from core.utils import (
    get_cache_dir,
    get_models_dir,
    format_duration,
    format_srt_timestamp,
    check_ffmpeg_available
)


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    print(f"[OK] Version: {__version__}")


def test_cache_directories():
    """Test cache directory creation."""
    cache_dir = get_cache_dir()
    assert cache_dir.exists()
    assert cache_dir.is_dir()
    print(f"[OK] Cache dir: {cache_dir}")
    
    models_dir = get_models_dir()
    assert models_dir.exists()
    assert models_dir.is_dir()
    print(f"[OK] Models dir: {models_dir}")


def test_model_manager():
    """Test model manager."""
    manager = ModelManager()
    
    # Test model listing
    models = manager.list_available_models()
    assert len(models) > 0
    assert "base" in models
    print(f"[OK] Found {len(models)} models")
    
    # Test model info
    info = manager.get_model_info("base")
    assert "size" in info
    assert "speed" in info
    print(f"[OK] Base model info: {info}")


def test_format_functions():
    """Test formatting functions."""
    # Test duration formatting
    duration_str = format_duration(3661.5)  # 1 hour, 1 minute, 1.5 seconds
    assert duration_str == "01:01:01"
    print(f"[OK] Duration format: {duration_str}")
    
    # Test SRT timestamp formatting
    srt_ts = format_srt_timestamp(90.5)  # 1 minute, 30.5 seconds
    assert srt_ts == "00:01:30,500"
    print(f"[OK] SRT timestamp: {srt_ts}")


def test_ffmpeg():
    """Test FFmpeg availability."""
    available = check_ffmpeg_available()
    if available:
        print("[OK] FFmpeg is available")
    else:
        print("[WARN] FFmpeg not found (required for transcription)")


def test_imports():
    """Test all major imports."""
    try:
        from core.transcribe import transcribe_video
        from core.model_manager import ModelManager
        from core.utils import json_response
        from core.cli import main
        print("[OK] All core imports successful")
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        raise


def test_ui_imports():
    """Test UI imports."""
    try:
        from core.ui import TranscribeWindow, ProgressWindow, ResultDialog
        print("[OK] UI imports successful")
    except ImportError as e:
        print(f"[FAIL] UI import failed: {e}")
        print("  Note: PySide6 may not be installed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print(" Running Basic Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_version,
        test_cache_directories,
        test_model_manager,
        test_format_functions,
        test_ffmpeg,
        test_imports,
        test_ui_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f" Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

