#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json, os, subprocess, sys
from pathlib import Path
from datetime import timedelta
from faster_whisper import WhisperModel
try:
    from tqdm import tqdm
    TQDM=True
except Exception:
    TQDM=False

ASS_HEADER = """[Script Info]
Title: Auto Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,110,&H00000000,&H00000000,&H00FFFFFF,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,30,30,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts_srt(s: float) -> str:
    ms = int(round(s*1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def ts_ass(s: float) -> str:
    cs = int(round(s*100))
    h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def ensure_audio(input_path: Path, outdir: Path, force: bool) -> Path:
    wav = outdir / (input_path.stem + "_16k.wav")
    if wav.exists() and not force: return wav
    cmd = ["ffmpeg","-y","-i",str(input_path),"-ac","1","-ar","16000","-vn",str(wav)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return wav
    except Exception:
        return input_path

def write_jsonl(path: Path, rec: dict):
    with path.open('a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False)+"\n")

def build_srt(jsonl: Path, out_srt: Path):
    i=1
    with jsonl.open('r', encoding='utf-8') as inp, out_srt.open('w', encoding='utf-8') as out:
        for line in inp:
            r=json.loads(line);
            if r.get('event')!="segment": continue
            text=r.get('text','').strip();
            if not text: continue
            out.write(f"{i}\n{ts_srt(r['start'])} --> {ts_srt(r['end'])}\n{text}\n\n"); i+=1

def sanitize(s:str)->str: return s.replace('\n',' ').replace('{','(').replace('}',')')

def build_ass(jsonl: Path, out_ass: Path, max_words: int = 5):
    """Build ASS with small chunks (max 5 words at a time)"""
    with out_ass.open('w', encoding='utf-8') as fa:
        fa.write(ASS_HEADER)
        
        with jsonl.open('r', encoding='utf-8') as inp:
            for line in inp:
                r=json.loads(line)
                if r.get('event')!="segment": continue
                
                words=r.get('words') or []
                if not words:
                    # Fallback: split text by words if no word timing
                    text = r.get('text', '').strip()
                    if text:
                        text = sanitize(text)
                        fa.write(f"Dialogue: 0,{ts_ass(r['start'])},{ts_ass(r['end'])},Default,,0,0,0,,{text}\n")
                    continue
                
                # Group words into chunks of max_words
                for i in range(0, len(words), max_words):
                    chunk_words = words[i:i+max_words]
                    
                    # Get timing from first and last word
                    start_time = chunk_words[0].get('start', 0)
                    end_time = chunk_words[-1].get('end', start_time + 1)
                    
                    # Combine words into text
                    text_parts = [w.get('word', '').strip() for w in chunk_words if w.get('word', '').strip()]
                    if not text_parts:
                        continue
                    
                    text = sanitize(' '.join(text_parts))
                    fa.write(f"Dialogue: 0,{ts_ass(start_time)},{ts_ass(end_time)},Default,,0,0,0,,{text}\n")

def main():
    ap=argparse.ArgumentParser(description='GPU Whisper → JSONL + SRT + ASS')
    ap.add_argument('input'); ap.add_argument('--outdir', default='runs/current')
    ap.add_argument('--model', default='medium'); ap.add_argument('--device', default='cuda')
    ap.add_argument('--compute-type', default='float16'); ap.add_argument('--language', default=None)
    ap.add_argument('--chunk-length', type=int, default=30); ap.add_argument('--vad', action='store_true')
    ap.add_argument('--no-words', action='store_true'); ap.add_argument('--audio-first', action='store_true')
    ap.add_argument('--force-audio', action='store_true'); ap.add_argument('--resume', action='store_true')
    args=ap.parse_args()

    inp=Path(args.input).resolve(); outdir=Path(args.outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    work_inp=ensure_audio(inp,outdir,args.force_audio) if args.audio_first else inp

    jsonl=outdir/"transcript.jsonl"; srt=outdir/"captions.srt"; ass=outdir/"captions.ass"

    model=WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    segs, info = model.transcribe(str(work_inp), language=args.language, word_timestamps=not args.no_words,
        vad_filter=args.vad, vad_parameters=dict(min_silence_duration_ms=700), beam_size=5, temperature=0.0,
        chunk_length=args.chunk_length, condition_on_previous_text=False)

    if TQDM:
        bar=tqdm(desc='segments', unit='seg')
        for seg in segs:
            rec={"event":"segment","start":float(seg.start),"end":float(seg.end),"text":seg.text}
            if not args.no_words: rec["words"]= [{"start":float(w.start),"end":float(w.end),"word":w.word} for w in (seg.words or [])]
            write_jsonl(jsonl, rec)
            bar.update(1)
        bar.close()
    else:
        for seg in segs:
            rec={"event":"segment","start":float(seg.start),"end":float(seg.end),"text":seg.text}
            if not args.no_words: rec["words"]= [{"start":float(w.start),"end":float(w.end),"word":w.word} for w in (seg.words or [])]
            write_jsonl(jsonl, rec)
    write_jsonl(jsonl, {"event":"done","language":getattr(info,'language',None),"duration":getattr(info,'duration',None)})

    build_srt(jsonl, srt); build_ass(jsonl, ass)
    print(f"[ok] {jsonl}\n[ok] {srt}\n[ok] {ass}")

if __name__=='__main__': main()

