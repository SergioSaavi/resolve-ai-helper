#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command-line interface for Resolve AI Helper
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

# Add parent directory to path for direct execution
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from threading import Thread
import sys as _sys
import json as _json
import queue as _queue

# Handle both direct execution and module import
try:
    from . import __version__
    # Intentionally avoid importing heavy modules (faster-whisper/torch) at
    # module import time to keep UI startup snappy. We'll lazy-import within
    # functions right before use.
    from .utils import json_response
except ImportError:
    # Direct execution fallback
    from core import __version__
    from core.utils import json_response


def cmd_transcribe(args):
    """Handle the transcribe command."""
    # If showing UI without input file, call the UI function
    if args.show_ui and not args.input:
        return cmd_transcribe_ui(args)
    
    # For all other cases, input is required
    if not args.input:
        return json_response(False, error="--input is required when not using --show-ui")
    
    input_path = Path(args.input).resolve()
    
    if not input_path.exists():
        return json_response(False, error=f"Input file not found: {input_path}")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = input_path.with_suffix(".srt")
    
    try:
        # Lazy import to avoid heavy startup cost
        if args.show_ui:
            pass  # transcribe_with_ui will import on demand
        else:
            if __package__:
                from .transcribe import transcribe_video  # noqa: F401
            else:
                from core.transcribe import transcribe_video  # noqa: F401

        if args.show_ui:
            # Show GUI for transcription with input file
            result = transcribe_with_ui(
                input_path,
                output_path,
                args.timeline_name
            )
        else:
            # Headless transcription
            result = transcribe_headless(
                input_path,
                output_path,
                args.model,
                args.device,
                args.language
            )
        
        if result:
            return json_response(True, data=result.to_dict())
        else:
            return json_response(False, error="Transcription cancelled")
            
    except Exception as e:
        return json_response(False, error=str(e))


def transcribe_with_ui(
    input_path: Path,
    output_path: Path,
    timeline_name: str
) -> Optional[object]:
    """
    Transcribe with GUI interface.
    
    Args:
        input_path: Path to input video
        output_path: Path for output SRT
        timeline_name: Name of the timeline
    
    Returns:
        TranscriptionResult or None if cancelled
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Estimate duration for timeline info (simplified)
    timeline_info = {
        "name": timeline_name or input_path.stem,
        "duration": "Unknown",  # Would need to probe video
        "fps": "24.00"
    }
    
    # Lazy import UI components (lightweight) only when needed
    if __package__:
        from .ui import TranscribeWindow, ProgressWindow, ResultDialog  # type: ignore
    else:
        from core.ui import TranscribeWindow, ProgressWindow, ResultDialog  # type: ignore

    # Show settings window
    settings_window = TranscribeWindow(timeline_info)
    settings = None
    test_requested = {"value": False}
    
    def on_transcribe_requested(s):
        nonlocal settings
        settings = s
    
    settings_window.transcribe_requested.connect(on_transcribe_requested)

    def on_test_place():
        test_requested["value"] = True

    settings_window.test_place_requested.connect(on_test_place)
    
    if settings_window.exec() != settings_window.Accepted and settings is None:
        return None
    
    # If test requested, generate test SRT and show result dialog
    if test_requested["value"]:
        try:
            # Generate test SRT via internal helper
            from pathlib import Path as _Path
            import tempfile as _tempfile
            temp_dir = _Path(_tempfile.gettempdir()) / "resolve-ai-helper"
            temp_dir.mkdir(parents=True, exist_ok=True)
            from .cli import cmd_generate_test_srt  # self-call
            class _Args: pass
            a = _Args()
            a.output = str(temp_dir / "test_from_ui.srt")
            resp_json = cmd_generate_test_srt(a)
            # Parse and show success dialog
            import json as _json
            resp = _json.loads(resp_json)
            srt_path = resp.get("srt_path") if resp.get("success") else None
            result_dialog = ResultDialog({"srt_path": srt_path, "duration": 5, "language": "en", "segments_count": 2, "words_count": 6}, success=True)
            result_dialog.exec()
        except Exception as e:
            error_dialog = ResultDialog({"error": str(e)}, success=False)
            error_dialog.exec()
        return None

    # Settings window closed, check if we have settings
    if settings is None:
        return None
    
    # Show progress window
    progress_window = ProgressWindow(timeline_info['name'])
    
    # Track cancellation
    cancelled = False
    
    def on_cancel():
        nonlocal cancelled
        cancelled = True
    
    progress_window.cancel_requested.connect(on_cancel)
    
    # Transcription result container
    result_container = {'result': None, 'error': None}
    
    # Run transcription in a way that allows UI updates
    def progress_callback(message: str, progress: Optional[float]):
        if cancelled:
            raise InterruptedError("Transcription cancelled by user")
        
        progress_window.update_progress(message, progress)
        QApplication.processEvents()  # Allow UI to update
    
    try:
        progress_window.show()
        QApplication.processEvents()
        
        # Lazy import the heavy transcribe function at the moment it's needed
        if __package__:
            from .transcribe import transcribe_video  # type: ignore
        else:
            from core.transcribe import transcribe_video  # type: ignore

        result = transcribe_video(
            input_path,
            output_path,
            model_name=settings['model'],
            device=settings['device'],
            language=settings['language'],
            progress_callback=progress_callback
        )
        
        # Update final stats
        progress_window.update_stats(
            segments=result.segments_count,
            words=result.words_count,
            language=result.language
        )
        
        progress_window.mark_complete()
        progress_window.exec()
        
        # Show result dialog
        result_dialog = ResultDialog(result.to_dict(), success=True)
        result_dialog.exec()
        
        result_container['result'] = result
        
    except InterruptedError:
        progress_window.mark_error("Transcription cancelled by user")
        progress_window.exec()
        return None
        
    except Exception as e:
        error_msg = str(e)
        progress_window.mark_error(error_msg)
        progress_window.exec()
        
        # Show error dialog
        error_dialog = ResultDialog({"error": error_msg}, success=False)
        error_dialog.exec()
        
        result_container['error'] = error_msg
    
    return result_container['result']


def transcribe_headless(
    input_path: Path,
    output_path: Path,
    model: str,
    device: str,
    language: Optional[str]
) -> object:
    """
    Transcribe without GUI (headless mode).
    
    Args:
        input_path: Path to input video
        output_path: Path for output SRT
        model: Model name
        device: Device to use
        language: Language code or None
    
    Returns:
        TranscriptionResult
    """
    def progress_callback(message: str, progress: Optional[float]):
        if progress is not None:
            print(f"[{progress*100:.0f}%] {message}", file=sys.stderr)
        else:
            print(f"[INFO] {message}", file=sys.stderr)
    
    # Lazy import heavy dependency here
    if __package__:
        from .transcribe import transcribe_video  # type: ignore
    else:
        from core.transcribe import transcribe_video  # type: ignore

    result = transcribe_video(
        input_path,
        output_path,
        model_name=model,
        device=device,
        language=language,
        progress_callback=progress_callback
    )
    
    return result


def cmd_check_models(args):
    """Handle the check-models command."""
    # Lazy import to avoid pulling in faster-whisper unless requested
    if __package__:
        from .model_manager import ModelManager, print_model_info  # type: ignore
    else:
        from core.model_manager import ModelManager, print_model_info  # type: ignore

    manager = ModelManager()
    models_info = manager.list_available_models()
    
    result = {
        "models": models_info,
        "cache_dir": str(manager.models_dir)
    }
    
    if args.json:
        return json_response(True, data=result)
    else:
        print_model_info()
        return ""


def cmd_check_system(args):
    """Handle the check-system command."""
    if __package__:
        from .utils import check_ffmpeg_available, check_cuda_available  # type: ignore
    else:
        from core.utils import check_ffmpeg_available, check_cuda_available  # type: ignore

    ffmpeg_available = check_ffmpeg_available()
    cuda_available = check_cuda_available()
    
    result = {
        "ffmpeg": ffmpeg_available,
        "cuda": cuda_available,
        "version": __version__
    }
    
    if args.json:
        return json_response(True, data=result)
    else:
        print("System Check:")
        print(f"  Version:     {__version__}")
        print(f"  FFmpeg:      {'[OK] Available' if ffmpeg_available else '[X] Not found'}")
        print(f"  CUDA/GPU:    {'[OK] Available' if cuda_available else '[X] Not available'}")
        return ""


def cmd_transcribe_ui(args):
    """Handle transcribe command with UI."""
    # Launch GUI
    app = QApplication(sys.argv)
    
    # Prepare timeline info for UI
    timeline_info = {
        "name": args.timeline_name or "Timeline",
        "duration": "Unknown",
        "fps": "Unknown"
    }
    
    # Create and show main window (import UI lazily)
    if __package__:
        from .ui import TranscribeWindow, ProgressWindow, ResultDialog  # type: ignore
    else:
        from core.ui import TranscribeWindow, ProgressWindow, ResultDialog  # type: ignore

    main_window = TranscribeWindow(timeline_info)
    
    # Store transcription settings
    transcription_result = {"completed": False}
    test_requested = {"value": False}
    test_response_json = {"value": None}
    cancel_requested = {"value": False}
    
    def on_transcribe_requested(settings):
        """Handle transcribe button click."""
        # Get input file from settings
        input_file = settings.get('input_file')
        if not input_file:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File", "Please select a video file first!")
            return
        
        input_path = Path(input_file)
        if not input_path.exists():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(main_window, "File Not Found", f"File not found: {input_path}")
            return
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.srt')
        
        # Close the settings window only in non-interactive mode
        if not interactive:
            main_window.close()
        
        # Show progress window
        progress_window = ProgressWindow(timeline_info['name'])
        progress_window.show()
        
        def progress_callback(message: str, progress: Optional[float]):
            progress_window.update_progress(message, progress or 0.0)
            QApplication.processEvents()
        
        try:
            # Perform transcription
            # Import heavy transcribe only when user starts the job
            if __package__:
                from .transcribe import transcribe_video  # type: ignore
            else:
                from core.transcribe import transcribe_video  # type: ignore

            result = transcribe_video(
                input_path,
                output_path,
                model_name=settings['model'],
                device=settings['device'],
                language=settings.get('language'),
                progress_callback=progress_callback
            )
            
            # Update progress with stats
            progress_window.update_stats(
                segments=result.segments_count,
                words=result.words_count,
                language=result.language
            )
            
            # Close progress window
            progress_window.close()
            
            # Show result dialog
            result_dialog = ResultDialog(result.__dict__, success=True)
            result_dialog.exec()
            
            # Emit JSON on stdout when interactive
            if interactive:
                print(json_response(True, data=result.__dict__), flush=True)
            
            transcription_result["completed"] = True
            transcription_result["result"] = result
            
        except Exception as e:
            progress_window.close()
            result_dialog = ResultDialog({"error": str(e)}, success=False)
            result_dialog.exec()
            if interactive:
                print(json_response(False, error=str(e)), flush=True)
        
        if not interactive:
            app.quit()
    
    def on_test_place():
        """Generate a tiny SRT and return JSON immediately for Resolve."""
        test_requested["value"] = True
        class _Args: pass
        a = _Args()
        a.output = None
        resp_json = cmd_generate_test_srt(a)
        test_response_json["value"] = resp_json
        # Emit JSON immediately in interactive mode and keep UI open
        if interactive:
            print(resp_json, flush=True)
        else:
            main_window.close()
            app.quit()
    
    main_window.transcribe_requested.connect(on_transcribe_requested)
    main_window.test_place_requested.connect(on_test_place)

    # Optional: emit a cancel JSON if user closes the window without action
    def on_window_closed():
        if not transcription_result["completed"] and not test_requested["value"]:
            cancel_requested["value"] = True
    main_window.window_closing.connect(on_window_closed)

    # Interactive mode: keep UI open and listen for JSON commands on stdin
    interactive = getattr(args, 'interactive', False)
    if interactive:
        main_window.set_keep_open(True)
        commands_q = _queue.Queue()

        def stdin_reader():
            try:
                for line in _sys.stdin:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        cmd = _json.loads(line)
                        commands_q.put(cmd)
                    except Exception:
                        # Ignore malformed lines
                        continue
            except Exception:
                pass

        reader_t = Thread(target=stdin_reader, daemon=True)
        reader_t.start()

        from PySide6.QtCore import QTimer
        # Signals to update UI from events
        from PySide6.QtCore import Signal, QObject
        class _EventBus(QObject):
            timeline_event = Signal(dict)
            selection_event = Signal(list)
        bus = _EventBus()
        bus.timeline_event.connect(main_window.update_timeline_context)
        bus.selection_event.connect(main_window.update_selection)

        def poll_commands():
            try:
                while True:
                    cmd = commands_q.get_nowait()
                    # Event messages from supervisor
                    if cmd.get('event') == 'timeline_state':
                        bus.timeline_event.emit(cmd.get('timeline') or {})
                        continue
                    if cmd.get('event') == 'selection':
                        bus.selection_event.emit(cmd.get('items') or [])
                        continue
                    # Command messages intended for actions
                    ctype = cmd.get('cmd')
                    if ctype == 'test_place':
                        on_test_place()
                    elif ctype == 'transcribe':
                        # Build settings dict to reuse on_transcribe_requested
                        settings = {
                            'input_file': cmd.get('input'),
                            'model': cmd.get('model', 'base'),
                            'device': cmd.get('device', 'auto'),
                            'language': cmd.get('language'),
                        }
                        on_transcribe_requested(settings)
                    elif ctype == 'transcribe_range':
                        # For now treat same as transcribe; supervisor will export range to a file
                        settings = {
                            'input_file': cmd.get('input'),
                            'model': cmd.get('model', 'base'),
                            'device': cmd.get('device', 'auto'),
                            'language': cmd.get('language'),
                        }
                        on_transcribe_requested(settings)
                    elif ctype == 'cancel':
                        print(json_response(False, error='cancel'))
                    elif ctype == 'shutdown':
                        app.quit()
                        return
            except _queue.Empty:
                pass

        timer = QTimer(main_window)
        timer.timeout.connect(poll_commands)
        timer.start(200)

        # Keep strong references so GC doesn't stop polling
        main_window._interactive = True
        main_window._cmd_queue = commands_q
        main_window._stdin_thread = reader_t
        main_window._event_bus = bus
        main_window._event_timer = timer
    main_window.show()
    
    app.exec()
    
    # Return result:
    if transcription_result["completed"]:
        return json_response(
            True,
            data=transcription_result["result"].__dict__,
            message="Transcription completed successfully"
        )
    else:
        if test_requested["value"] and test_response_json["value"]:
            return test_response_json["value"]
        if cancel_requested["value"]:
            return json_response(False, error="cancel")
        return json_response(False, error="Transcription cancelled by user")


def cmd_generate_test_srt(args):
    """Generate a tiny SRT file via the exe to test Resolve roundtrip."""
    import tempfile
    from pathlib import Path as _Path

    # Determine output path
    if args.output:
        srt_path = _Path(args.output).resolve()
        srt_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = _Path(tempfile.gettempdir()) / "resolve-ai-helper"
        temp_dir.mkdir(parents=True, exist_ok=True)
        srt_path = temp_dir / "test_from_exe.srt"

    # Write a minimal SRT
    content = (
        "1\n"
        "00:00:00,000 --> 00:00:02,500\n"
        "Hello from resolve_ai_helper.exe!\n\n"
        "2\n"
        "00:00:02,700 --> 00:00:05,000\n"
        "This verifies the exe → Resolve roundtrip.\n\n"
    )
    with srt_path.open('w', encoding='utf-8') as f:
        f.write(content)

    return json_response(True, data={"srt_path": str(srt_path)})


def cmd_version(args):
    """Handle the version command."""
    return __version__


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Resolve AI Helper - AI-powered transcription for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe with GUI
  resolve_ai_helper transcribe --input video.mp4 --show-ui --timeline-name "My Video"
  
  # Transcribe headless
  resolve_ai_helper transcribe --input video.mp4 --model base --device auto
  
  # Check available models
  resolve_ai_helper check-models
  
  # Check system requirements
  resolve_ai_helper check-system
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Resolve AI Helper v{__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        'transcribe',
        help='Transcribe video to subtitles'
    )
    transcribe_parser.add_argument(
        '--input',
        required=False,
        help='Path to input video file (optional with --show-ui)'
    )
    transcribe_parser.add_argument(
        '--output',
        help='Path to output SRT file (default: same as input with .srt extension)'
    )
    transcribe_parser.add_argument(
        '--model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium'],
        help='Whisper model to use (default: base)'
    )
    transcribe_parser.add_argument(
        '--device',
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help='Device to use (default: auto)'
    )
    transcribe_parser.add_argument(
        '--language',
        help='Language code (e.g., en, es, fr) or auto-detect if not specified'
    )
    transcribe_parser.add_argument(
        '--show-ui',
        action='store_true',
        help='Show GUI for configuration and progress'
    )
    transcribe_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Keep UI open and accept JSON commands over stdin'
    )
    transcribe_parser.add_argument(
        '--timeline-name',
        help='Name of the timeline (for UI display)'
    )
    transcribe_parser.set_defaults(func=cmd_transcribe)
    
    # Check models command
    models_parser = subparsers.add_parser(
        'check-models',
        help='List available Whisper models'
    )
    models_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    models_parser.set_defaults(func=cmd_check_models)
    
    # Check system command
    system_parser = subparsers.add_parser(
        'check-system',
        help='Check system requirements'
    )
    system_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    system_parser.set_defaults(func=cmd_check_system)

    # Generate test SRT command (for Resolve integration testing)
    test_srt_parser = subparsers.add_parser(
        'generate-test-srt',
        help='Generate a small SRT file and print its path as JSON'
    )
    test_srt_parser.add_argument(
        '--output',
        help='Optional output path for the generated SRT'
    )
    test_srt_parser.set_defaults(func=cmd_generate_test_srt)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        result = args.func(args)
        if result:
            print(result)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

