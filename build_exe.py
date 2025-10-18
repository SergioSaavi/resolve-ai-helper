#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script for creating the standalone executable using PyInstaller
"""

import sys
import shutil
from pathlib import Path
import PyInstaller.__main__


def clean_build_dirs():
    """Clean up build and dist directories."""
    print("Cleaning build directories...")
    
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print(f"  ✓ Removed {build_dir}")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print(f"  ✓ Removed {dist_dir}")
    
    print()


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    print("-" * 60)
    
    # PyInstaller arguments (stable, minimal and fast)
    args = [
        'core/cli.py',                     # Entry point
        '--name=resolve_ai_helper',        # Output name
        '--onedir',                        # Directory with fast-start exe
        '--console',                       # Show console window (needed for CLI)
        '--clean',                         # Clean cache before building

        # Ensure Qt core modules are included (no web/qml)
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtGui',

        # Faster-whisper runtime (no models bundled)
        '--hidden-import=faster_whisper',
        '--hidden-import=tqdm',
        '--collect-all=faster_whisper',

        # Exclude known heavy/unused packages
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=notebook',
        '--exclude-module=IPython',
        '--exclude-module=PIL',
        '--exclude-module=torch',
        '--exclude-module=PySide6.QtWebEngineCore',
        '--exclude-module=PySide6.QtWebEngineWidgets',
        '--exclude-module=PySide6.QtWebEngineQuick',

        # Don't confirm overwrite
        '--noconfirm',

        # Mild bytecode optimize only (no strip on Windows)
        '--optimize=2',
    ]
    
    # Add icon if it exists
    icon_path = Path("resources/icon.ico")
    if icon_path.exists():
        args.extend(['--icon', str(icon_path)])
    
    print(f"Running: pyinstaller {' '.join(args)}")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("-" * 60)
        print("✓ Build complete!")
        print(f"  Executable folder: dist/resolve_ai_helper/")
        print(f"  EXE: dist/resolve_ai_helper/resolve_ai_helper.exe")
        return True
        
    except Exception as e:
        print()
        print("-" * 60)
        print(f"✗ Build failed: {e}")
        return False


def get_file_size(file_path: Path) -> str:
    """Get human-readable file size."""
    if not file_path.exists():
        return "N/A"
    
    size = file_path.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} TB"


def test_executable():
    """Test the built executable."""
    exe_path = Path("dist/resolve_ai_helper.exe")
    
    if not exe_path.exists():
        print("✗ Executable not found, cannot test")
        return False
    
    print()
    print("Testing executable...")
    print("-" * 60)
    
    import subprocess
    
    try:
        # Test version command
        result = subprocess.run(
            [str(exe_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ Version check passed: {result.stdout.strip()}")
        else:
            print(f"✗ Version check failed: {result.stderr}")
            return False
        
        # Test system check
        result = subprocess.run(
            [str(exe_path), "check-system", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ System check passed")
            print(f"  Output: {result.stdout[:100]}...")
        else:
            print(f"✗ System check failed: {result.stderr}")
            return False
        
        print()
        print("✓ All tests passed!")
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Test timed out")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def create_distribution_package():
    """Create a single folder ready to copy into Resolve's Comp directory."""
    print()
    print("Creating Comp-ready folder...")
    print("-" * 60)
    
    # One folder to copy into Comp: dist/ResolveAIHelper/
    comp_ready_dir = Path("dist/ResolveAIHelper")
    if comp_ready_dir.exists():
        shutil.rmtree(comp_ready_dir)
    comp_ready_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy onedir runtime
    onedir_src = Path("dist/resolve_ai_helper")
    exe_onefile = Path("dist/resolve_ai_helper.exe")
    if onedir_src.exists():
        shutil.copytree(onedir_src, comp_ready_dir / "resolve_ai_helper")
        print("  ✓ Added resolve_ai_helper/ (onedir exe)")
    elif exe_onefile.exists():
        shutil.copy(exe_onefile, comp_ready_dir / "resolve_ai_helper.exe")
        print("  ✓ Added resolve_ai_helper.exe (onefile)")
    else:
        print("  ✗ No executable found. Build step may have failed.")
        return False
    
    # Copy the single launcher script only
    launcher_src = Path("resolve_scripts/launch_transcribe_ui.py")
    if launcher_src.exists():
        shutil.copy(launcher_src, comp_ready_dir / "launch_transcribe_ui.py")
        print("  ✓ Added launch_transcribe_ui.py")
    else:
        print("  ✗ Launcher script not found.")
        return False
    
    print()
    print(f"✓ Comp-ready folder created: {comp_ready_dir}")
    print("  Copy this entire folder into:")
    print("    C\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Fusion\\Scripts\\Comp")
    print("  In Resolve: Workspace → Scripts → Comp → ResolveAIHelper → launch_transcribe_ui")
    return True


def main():
    """Main build process."""
    print()
    print("=" * 60)
    print(" Resolve AI Helper - Build Script")
    print("=" * 60)
    print()
    
    # Step 1: Clean
    if "--clean" in sys.argv or "--full" in sys.argv:
        clean_build_dirs()
    
    # Step 2: Build
    if not build_executable():
        print("\n✗ Build process failed")
        sys.exit(1)
    
    # Step 3: Test
    if "--test" in sys.argv or "--full" in sys.argv:
        if not test_executable():
            print("\n⚠ Warning: Tests failed, but executable was built")
    
    # Step 4: Package
    if "--package" in sys.argv or "--full" in sys.argv:
        create_distribution_package()
    
    print()
    print("=" * 60)
    print(" Build Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Test the executable: dist/resolve_ai_helper.exe --version")
    print("  2. Test transcription: dist/resolve_ai_helper.exe check-system")
    print("  3. Copy to Resolve scripts location")
    print()


if __name__ == "__main__":
    main()

