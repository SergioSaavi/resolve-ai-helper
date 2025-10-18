#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json, os, re, subprocess, sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from dotenv import load_dotenv
from datetime import timedelta

# OpenAI SDK (supports OPENAI_BASE_URL for compatibles)
from openai import OpenAI

load_dotenv()

@dataclass
class Highlight:
    start: float
    end: float
    title: str
    reason: str = ""

SCHEMA_HINT = {
  "type": "object",
  "properties": {
    "highlights": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "start": {"type": "number"},
          "end": {"type": "number"},
          "title": {"type": "string"},
          "reason": {"type": "string"}
        },
        "required": ["start","end","title"]
      }
    }
  },
  "required": ["highlights"]
}

def load_transcript_jsonl(path: Path) -> List[Dict]:
    items=[]
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return [x for x in items if x.get('event')=='segment']

def sample_transcript_lines(segments: List[Dict], target_chars: int = 20000) -> str:
    # Build timestamped lines with more context for better boundary detection
    lines=[f"{s['start']:.2f} - {s['end']:.2f}: {s['text'].strip()}" for s in segments if s.get('text')]
    if not lines: return ""
    joined="\n".join(lines)
    if len(joined) <= target_chars:
        return joined
    # Downsample lines evenly but keep more context
    step=max(1, int(len(lines) * (len(joined)/target_chars)))
    slim=lines[::step]
    out="\n".join(slim)
    return out[:target_chars]

def extend_to_complete_sentence(segments: List[Dict], start: float, end: float, max_extension: float = 8.0) -> float:
    """Extend the end time to complete the sentence if it's cut off mid-thought"""
    # Find segments near the end point
    for seg in segments:
        seg_start = seg.get('start', 0)
        seg_end = seg.get('end', 0)
        
        # If this segment overlaps with our end point
        if seg_start <= end < seg_end:
            text = seg.get('text', '').strip()
            # If the text doesn't end with proper punctuation, extend to the segment end
            if text and not text[-1] in '.!?':
                extension = seg_end - end
                if extension <= max_extension:
                    print(f"[extend] Adding {extension:.1f}s to complete sentence: '{text[:50]}...'")
                    return seg_end
        
        # If segment starts right after our end point (within 0.5s)
        if end <= seg_start < end + 0.5:
            prev_seg = None
            for s in segments:
                if s.get('end', 0) <= end and s.get('end', 0) > end - 2:
                    prev_seg = s
                    break
            
            if prev_seg:
                prev_text = prev_seg.get('text', '').strip()
                # If previous segment doesn't end with punctuation, include next segment
                if prev_text and not prev_text[-1] in '.!?':
                    extension = seg.get('end', end) - end
                    if extension <= max_extension:
                        print(f"[extend] Including next segment to complete thought")
                        return seg.get('end', end)
    
    return end

def call_llm_for_highlights(transcript_sample: str, max_shorts: int, model: str) -> List[Highlight]:
    client=OpenAI(base_url=os.getenv('OPENAI_BASE_URL'))
    prompt_path=Path('templates/prompt_highlights.txt')
    tmpl=prompt_path.read_text(encoding='utf-8')
    prompt=tmpl.replace('{{max_shorts}}', str(max_shorts)).replace('{{transcript_sample}}', transcript_sample)
    # Ask for JSON strictly; model should comply. We'll parse and validate.
    try:
        msg=client.chat.completions.create(
            model=model, temperature=0.2,
            messages=[{"role":"user","content":prompt}]
        )
        raw=msg.choices[0].message.content.strip()
        print(f"[debug] LLM response: {raw[:200]}...")
        # Extract JSON block if the model wrapped it in markdown
        if '```' in raw:
            # Extract from markdown code block
            m=re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
            if m:
                raw=m.group(1)
        # Now extract the JSON object
        m=re.search(r"\{[\s\S]*\}", raw)
        data=json.loads(m.group(0) if m else raw)
    except Exception as e:
        print(f"[error] LLM API call failed: {e}")
        print(f"[error] Raw response: {raw if 'raw' in locals() else 'No response'}")
        raise
    # Validate simple schema
    out=[]
    for h in data.get('highlights', [])[:max_shorts]:
        try:
            s=float(h['start']); e=float(h['end']);
            duration=e-s
            if e<=s:
                print(f"[skip] {h.get('title','?')}: end <= start ({s} to {e})")
                continue
            if duration<15:
                print(f"[skip] {h.get('title','?')}: too short ({duration:.1f}s, need 15-60s)")
                continue
            if duration>60:
                print(f"[skip] {h.get('title','?')}: too long ({duration:.1f}s, need 15-60s)")
                continue
            print(f"[ok] Selected: {h.get('title','?')} ({duration:.1f}s)")
            out.append(Highlight(start=s, end=e, title=str(h.get('title','Highlight')), reason=str(h.get('reason',''))))
        except Exception as ex:
            print(f"[skip] Error parsing highlight: {ex}")
            continue
    # Dedup overlaps (simple): sort by start, drop heavy overlaps
    out.sort(key=lambda x: x.start)
    dedup=[]
    for h in out:
        if dedup and (h.start < dedup[-1].end - 2):
            # overlap > ~2s → keep earlier
            continue
        dedup.append(h)
    return dedup

def ts_ass(s: float) -> str:
    """Convert seconds to ASS timestamp format"""
    cs = int(round(s*100))
    h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def create_clip_ass(source_ass: Path, start: float, end: float, output_ass: Path):
    """Create a clip-specific ASS file with adjusted timestamps relative to clip start"""
    with source_ass.open('r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where events section starts
    events_start = -1
    header_lines = []
    for i, line in enumerate(lines):
        if line.startswith('[Events]'):
            events_start = i
            # Capture everything up to and including the Format line
            for j in range(i, min(i+3, len(lines))):
                header_lines.append(lines[j])
                if lines[j].startswith('Format:'):
                    events_start = j + 1
                    break
            break
    
    if events_start == -1:
        # No events found, just copy file
        output_ass.write_text(source_ass.read_text(encoding='utf-8'), encoding='utf-8')
        return
    
    # Adjust MarginV in styles for better positioning (not at absolute bottom)
    adjusted_header = []
    for line in header_lines:
        if line.startswith('Style:'):
            # Fix font, sizing and positioning for small word chunks
            parts = line.split(',')
            if len(parts) > 21:
                parts[1] = 'DejaVu Sans'  # Change font to available system font
                parts[2] = '110'  # Very large font size (max 5 words)
                parts[3] = '&H00000000'  # Black text
                parts[5] = '&H00FFFFFF'  # White outline
                parts[17] = '7'  # Thick outline
                parts[21] = '180'  # MarginV - move captions higher (0-based index 21)
                line = ','.join(parts)
        adjusted_header.append(line)
    
    # Filter and adjust dialogue lines
    dialogue_lines = []
    for line in lines[events_start:]:
        if line.startswith('Dialogue:'):
            parts = line.split(',', 9)  # Split into: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
            if len(parts) >= 10:
                try:
                    # Parse timestamps (format: H:MM:SS.CS)
                    start_time = parts[1]
                    end_time = parts[2]
                    
                    # Convert to seconds
                    def parse_ass_time(ts):
                        h, m, s = ts.split(':')
                        s, cs = s.split('.')
                        return int(h)*3600 + int(m)*60 + int(s) + int(cs)/100.0
                    
                    line_start = parse_ass_time(start_time)
                    line_end = parse_ass_time(end_time)
                    
                    # Only include if within clip range
                    if line_end < start or line_start > end:
                        continue
                    
                    # Adjust timestamps relative to clip start
                    new_start = max(0, line_start - start)
                    new_end = min(end - start, line_end - start)
                    
                    # Skip if caption duration too short (< 0.05s) after trimming
                    if new_end - new_start < 0.05:
                        continue
                    
                    # Rebuild line with adjusted timestamps
                    parts[1] = ts_ass(new_start)
                    parts[2] = ts_ass(new_end)
                    dialogue_lines.append(','.join(parts))
                except Exception:
                    continue
    
    # Write new ASS file
    with output_ass.open('w', encoding='utf-8') as f:
        # Write header (everything before events)
        for line in lines[:events_start-len(header_lines)]:
            # Adjust MarginV in header styles too and fix font
            if line.startswith('Style:'):
                parts = line.split(',')
                if len(parts) > 21:
                    parts[1] = 'DejaVu Sans'  # Change font to available system font
                    parts[2] = '110'  # Very large font size
                    parts[3] = '&H00000000'  # Black text
                    parts[5] = '&H00FFFFFF'  # White outline
                    parts[17] = '7'  # Thick outline
                    parts[21] = '180'  # MarginV - move captions higher (0-based index 21)
                    line = ','.join(parts)
            f.write(line)
        # Write events header
        for line in adjusted_header:
            f.write(line)
        # Write adjusted dialogue lines
        for line in dialogue_lines:
            f.write(line)

def burn_short(input_video: Path, captions_ass: Path, start: float, end: float, aspect: str, crf: int, preset: str, out_path: Path):
    # Add large buffer for manual editing in Premiere
    start_buffer = 2.0  # 2 seconds before
    end_buffer = 3.0    # 3 seconds after
    buffered_start = max(0, start - start_buffer)
    buffered_end = end + end_buffer
    
    # Create clip-specific ASS file with timestamps adjusted for the buffered start
    clip_ass = out_path.parent / f"{out_path.stem}_captions.ass"
    create_clip_ass(captions_ass, buffered_start, buffered_end, clip_ass)
    
    # Build VF chain: scale+crop for 9:16, then subtitles
    vf = []
    if aspect=="9:16":
        # Better scaling algorithm for quality
        vf.append("scale=w=-2:h=1920:flags=lanczos")
        vf.append("crop=1080:1920")
    elif aspect=="1:1":
        vf.append("scale=1080:-2:flags=lanczos,crop=1080:1080")
    elif aspect=="16:9":
        vf.append("scale=1920:-2:flags=lanczos,setsar=1")
    
    # Add subtitle filter - ASS file already has proper styling
    vf.append(f"subtitles={clip_ass.as_posix()}")
    vf_str=",".join(vf)
    
    # Improved FFmpeg command with better quality settings
    cmd=[
        'ffmpeg','-y',
        '-ss',str(buffered_start),  # Seek BEFORE input for faster processing
        '-i',str(input_video),
        '-to',str(buffered_end - buffered_start),  # Duration from start
        '-vf',vf_str,
        '-c:v','libx264',
        '-preset',preset,
        '-crf',str(crf),
        '-profile:v','high',  # High profile for better quality
        '-level','4.2',
        '-pix_fmt','yuv420p',  # Ensure compatibility
        '-c:a','aac',
        '-b:a','128k',  # Better audio quality
        '-ar','44100',  # Standard audio rate
        '-movflags','+faststart',  # Web optimization
        str(out_path)
    ]
    
    print(f"[info] Generating {out_path.name}...")
    subprocess.run(cmd, check=True)
    
    # Clean up temporary ASS file
    # clip_ass.unlink()  # Keep for debugging

def main():
    ap=argparse.ArgumentParser(description='Build multiple shorts from transcript + LLM-selected highlights')
    ap.add_argument('input', help='Path to original VOD video')
    ap.add_argument('--workdir', required=True, help='Directory containing transcript.jsonl and captions.ass from shorts_transcribe.py')
    ap.add_argument('--num-shorts', type=int, default=5)
    ap.add_argument('--aspect', default='9:16', choices=['9:16','1:1','16:9'])
    ap.add_argument('--crf', type=int, default=20)
    ap.add_argument('--preset', default='veryfast')
    ap.add_argument('--model', default=os.getenv('OPENAI_MODEL','gpt-4o-mini'))
    args=ap.parse_args()

    input_video=Path(args.input).resolve()
    workdir=Path(args.workdir).resolve()
    jsonl=workdir/'transcript.jsonl'
    ass=workdir/'captions.ass'
    outdir=workdir/'shorts'; outdir.mkdir(parents=True, exist_ok=True)

    segs=load_transcript_jsonl(jsonl)
    sample=sample_transcript_lines(segs, target_chars=20000)  # More context for better decisions
    highs=call_llm_for_highlights(sample, args.num_shorts, args.model)
    
    # Extend highlights to complete sentences if needed
    extended_highs = []
    for h in highs:
        extended_end = extend_to_complete_sentence(segs, h.start, h.end)
        if extended_end != h.end:
            h = Highlight(start=h.start, end=extended_end, title=h.title, reason=h.reason)
        extended_highs.append(h)
    highs = extended_highs

    manifest=[]
    for i,h in enumerate(highs, start=1):
        safe_title=re.sub(r'[^a-zA-Z0-9_-]+','_', h.title).strip('_') or f'highlight_{i}'
        out_path=outdir/f"{i:02d}_{safe_title}.mp4"
        burn_short(input_video, ass, h.start, h.end, args.aspect, args.crf, args.preset, out_path)
        manifest.append({"index":i,"title":h.title,"start":h.start,"end":h.end,"file":str(out_path)})
        print(f"[ok] {out_path}")

    (workdir/'shorts_manifest.json').write_text(json.dumps({"highlights":[m for m in manifest]}, indent=2), encoding='utf-8')
    print(f"[ok] Manifest: {workdir/'shorts_manifest.json'}")

if __name__=='__main__': main()

