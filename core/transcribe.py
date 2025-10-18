#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core transcription functionality using faster-whisper
"""

import json
import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from .model_manager import ModelManager
from .utils import (
    extract_audio,
    format_srt_timestamp,
    validate_video_file,
    get_temp_dir,
    cleanup_temp_files
)


class TranscriptionResult:
    """Container for transcription results."""
    
    def __init__(
        self,
        srt_path: Path,
        duration: float,
        language: str,
        segments_count: int,
        words_count: int,
        processing_time: float
    ):
        self.srt_path = srt_path
        self.duration = duration
        self.language = language
        self.segments_count = segments_count
        self.words_count = words_count
        self.processing_time = processing_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "srt_path": str(self.srt_path),
            "duration": self.duration,
            "language": self.language,
            "segments_count": self.segments_count,
            "words_count": self.words_count,
            "processing_time": self.processing_time
        }


def transcribe_video(
    video_path: Path,
    output_srt: Optional[Path] = None,
    model_name: str = "base",
    device: str = "auto",
    compute_type: str = "default",
    language: Optional[str] = None,
    word_timestamps: bool = True,
    vad_filter: bool = True,
    progress_callback: Optional[Callable[[str, Optional[float]], None]] = None
) -> TranscriptionResult:
    """
    Transcribe video file to SRT subtitles.
    
    Args:
        video_path: Path to input video file
        output_srt: Path for output SRT file (default: same as video with .srt extension)
        model_name: Whisper model to use (tiny, base, small, medium)
        device: Device to use ("cpu", "cuda", or "auto")
        compute_type: Computation type ("int8", "float16", "float32", or "default")
        language: Language code (e.g., "en", "es") or None for auto-detect
        word_timestamps: Whether to generate word-level timestamps
        vad_filter: Whether to use Voice Activity Detection
        progress_callback: Optional callback(message: str, progress: Optional[float])
    
    Returns:
        TranscriptionResult object
    
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video file format is invalid
        RuntimeError: If transcription fails
    """
    start_time = datetime.now()
    
    # Validate input
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not validate_video_file(video_path):
        raise ValueError(
            f"Invalid video file format: {video_path.suffix}\n"
            "Supported formats: .mp4, .mov, .avi, .mkv, .mxf, .m4v, .webm"
        )
    
    # Set output path
    if output_srt is None:
        output_srt = video_path.with_suffix(".srt")
    else:
        output_srt = Path(output_srt).resolve()
    
    # Ensure output directory exists
    output_srt.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Extract audio
        if progress_callback:
            progress_callback("Extracting audio from video...", 0.0)
        
        temp_dir = get_temp_dir()
        audio_path = temp_dir / f"{video_path.stem}_audio.wav"
        audio_path = extract_audio(video_path, audio_path)
        
        # Step 2: Load model
        if progress_callback:
            progress_callback("Loading Whisper model...", 0.1)
        
        manager = ModelManager()
        
        def model_progress(msg: str):
            if progress_callback:
                progress_callback(msg, None)
        
        model = manager.load_model(
            model_name,
            device=device,
            compute_type=compute_type,
            progress_callback=model_progress
        )
        
        # Step 3: Transcribe
        if progress_callback:
            progress_callback("Transcribing audio (this may take a while)...", 0.2)
        
        segments_list = []
        total_words = 0
        
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=word_timestamps,
            vad_filter=vad_filter,
            vad_parameters=dict(min_silence_duration_ms=700) if vad_filter else None,
            beam_size=5,
            temperature=0.0,
            condition_on_previous_text=False
        )
        
        # Convert generator to list and process
        if progress_callback:
            progress_callback("Processing segments...", 0.3)
        
        for i, segment in enumerate(segments):
            seg_data = {
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text.strip()
            }
            
            if word_timestamps and segment.words:
                seg_data["words"] = [
                    {
                        "start": float(w.start),
                        "end": float(w.end),
                        "word": w.word
                    }
                    for w in segment.words
                ]
                total_words += len(segment.words)
            
            segments_list.append(seg_data)
            
            # Update progress periodically
            if progress_callback and i % 10 == 0:
                progress_callback(
                    f"Processing segments... ({i} completed)",
                    0.3 + (0.5 * min(i / 100, 1.0))  # Progress from 30% to 80%
                )
        
        # Step 4: Generate SRT
        if progress_callback:
            progress_callback("Generating SRT file...", 0.9)
        
        write_srt(segments_list, output_srt)
        
        # Clean up temporary audio file
        cleanup_temp_files(audio_path)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if progress_callback:
            progress_callback("✓ Transcription complete!", 1.0)
        
        return TranscriptionResult(
            srt_path=output_srt,
            duration=float(getattr(info, 'duration', 0)),
            language=getattr(info, 'language', language or 'unknown'),
            segments_count=len(segments_list),
            words_count=total_words,
            processing_time=processing_time
        )
        
    except Exception as e:
        # Clean up on error
        if 'audio_path' in locals():
            cleanup_temp_files(audio_path)
        
        error_msg = f"Transcription failed: {str(e)}"
        if progress_callback:
            progress_callback(f"✗ {error_msg}", None)
        
        raise RuntimeError(error_msg) from e


def write_srt(segments: List[Dict[str, Any]], output_path: Path):
    """
    Write segments to SRT subtitle file.
    
    Args:
        segments: List of segment dictionaries with 'start', 'end', 'text'
        output_path: Path to output SRT file
    """
    with output_path.open('w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, start=1):
            text = seg.get('text', '').strip()
            if not text:
                continue
            
            start = seg.get('start', 0.0)
            end = seg.get('end', 0.0)
            
            # Write SRT format
            f.write(f"{i}\n")
            f.write(f"{format_srt_timestamp(start)} --> {format_srt_timestamp(end)}\n")
            f.write(f"{text}\n\n")


def write_jsonl(segments: List[Dict[str, Any]], output_path: Path):
    """
    Write segments to JSONL file (one JSON object per line).
    
    Args:
        segments: List of segment dictionaries
        output_path: Path to output JSONL file
    """
    with output_path.open('w', encoding='utf-8') as f:
        for seg in segments:
            f.write(json.dumps(seg, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    # Simple test
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <video_file> [output.srt]")
        sys.exit(1)
    
    video = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    def progress(msg: str, pct: Optional[float]):
        if pct is not None:
            print(f"[{pct*100:.0f}%] {msg}")
        else:
            print(f"[INFO] {msg}")
    
    try:
        result = transcribe_video(
            video,
            output,
            model_name="base",
            device="auto",
            progress_callback=progress
        )
        
        print(f"\n✓ Success!")
        print(f"  Output: {result.srt_path}")
        print(f"  Duration: {result.duration:.1f}s")
        print(f"  Language: {result.language}")
        print(f"  Segments: {result.segments_count}")
        print(f"  Processing time: {result.processing_time:.1f}s")
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

