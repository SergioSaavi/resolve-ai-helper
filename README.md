# Shorts Builder (Python + uv)

**Local VOD → GPU Whisper transcription → captions → LLM highlight selection → FFmpeg multi-short rendering (9:16 with burned-in captions)**

## Features

- **GPU-accelerated transcription** with faster-whisper
- **Styleable ASS captions** with word-level karaoke timing
- **LLM-powered highlight selection** (OpenAI or compatible)
- **Automated vertical short rendering** (9:16, 1:1, or 16:9)

## ⚡ Easiest Way: Use the Makefile

**Don't want to type long commands? Use the Makefile!**

```bash
# Get SRT file for manual Premiere styling
make transcribe-srt VIDEO=my_video.mp4

# Full workflow: transcribe + generate shorts
make full VIDEO=my_video.mp4

# Quick test
make quick VIDEO=my_video.mp4

# High quality
make quality VIDEO=my_video.mp4
```

**See [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) for all commands and examples.**

## Prerequisites

### System Requirements

1. **FFmpeg** (required for video processing)
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org)

2. **uv** (Python package manager)
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **CUDA** (optional, for GPU transcription)
   - Recommended for faster-whisper GPU support
   - CPU mode works but is slower

## Quick Start

### 1. Setup

```bash
# Clone or navigate to project
cd /path/to/shorts-builder

# Create virtual environment and install dependencies (one command!)
uv sync

# Or manually:
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini
# Optional: OPENAI_BASE_URL=http://localhost:11434/v1 (for local LLMs)
```

### 3. Transcribe a Video

```bash
# GPU transcription with VAD (Voice Activity Detection)
uv run python scripts/shorts_transcribe.py input.mp4 \
  --model medium \
  --device cuda \
  --compute-type float16 \
  --chunk-length 30 \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)

# CPU transcription (slower)
uv run python scripts/shorts_transcribe.py input.mp4 \
  --model base \
  --device cpu \
  --compute-type int8 \
  --outdir runs/current
```

**Outputs:**
- `runs/<timestamp>/transcript.jsonl` - Streamed segments with word-level timestamps
- `runs/<timestamp>/captions.srt` - Standard SRT subtitles
- `runs/<timestamp>/captions.ass` - **Styleable ASS subtitles with karaoke effect**

### 4. Generate Shorts

```bash
# Generate 5 shorts from the transcribed video
uv run python scripts/shorts_builder.py input.mp4 \
  --workdir runs/<timestamp> \
  --num-shorts 5 \
  --aspect 9:16 \
  --crf 20 \
  --preset veryfast

# Output: runs/<timestamp>/shorts/*.mp4
```

**Arguments:**
- `--num-shorts` - Number of highlights to generate (default: 5)
- `--aspect` - Video aspect ratio: `9:16`, `1:1`, or `16:9` (default: 9:16)
- `--crf` - Video quality (lower = better, 18-28 recommended, default: 20)
- `--preset` - FFmpeg preset: `ultrafast`, `veryfast`, `medium`, `slow` (default: veryfast)
- `--model` - LLM model to use (default: from OPENAI_MODEL env var)

## Customizing Caption Styles

The ASS subtitle format supports extensive styling. Edit the `ASS_HEADER` section in `scripts/shorts_transcribe.py`:

```python
ASS_HEADER = """[Script Info]
...
[V4+ Styles]
Style: Default,Inter,64,&H00FFFFFF,&H00000000,&H7F000000,&H32000000,0,0,0,0,100,100,0,0,1,4,0,2,60,60,80,1
Style: Emph,Inter,64,&H00FFFF00,&H00000000,&H7F000000,&H32000000,1,0,0,0,100,100,0,0,1,4,0,2,60,60,80,1
"""
```

**Style Parameters:**
- **Fontname**: Font family (e.g., `Inter`, `Arial`, `Montserrat`)
- **Fontsize**: Font size in pixels (e.g., `64`, `80`)
- **PrimaryColour**: Text color in `&HAABBGGRR` format (ABGR hex)
  - `&H00FFFFFF` = White
  - `&H00FFFF00` = Yellow
  - `&H0000FF00` = Green
- **OutlineColour**: Outline color
- **Bold**: `0` = normal, `1` = bold (or `-1`)
- **Alignment**: `2` = bottom center, `5` = middle center, `8` = top center
- **MarginV**: Vertical margin from bottom (in pixels)

The **Emph** style includes `{\k}` tags for word-by-word karaoke highlighting!

## Project Structure

```
shorts-builder/
├── pyproject.toml              # uv dependencies
├── .python-version             # Python 3.11
├── .env.example                # Environment template
├── README.md                   # This file
├── PLAN.md                     # Detailed implementation plan
├── scripts/
│   ├── shorts_transcribe.py    # Whisper → JSONL/SRT/ASS
│   └── shorts_builder.py       # LLM → highlight selection → FFmpeg
├── templates/
│   └── prompt_highlights.txt   # LLM prompt template
└── runs/
    └── <timestamp>/
        ├── transcript.jsonl
        ├── captions.{srt,ass}
        ├── shorts_manifest.json
        └── shorts/*.mp4
```

## Advanced Usage

### Using Local LLMs (Ollama, LM Studio, etc.)

```bash
# In .env:
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2
OPENAI_API_KEY=dummy
```

### Resume Interrupted Transcription

```bash
# Use --resume flag (requires same output directory)
uv run python scripts/shorts_transcribe.py input.mp4 \
  --outdir runs/existing_run \
  --resume
```

### Custom Prompt Template

Edit `templates/prompt_highlights.txt` to customize how the LLM selects highlights.

### Batch Processing

```bash
for video in videos/*.mp4; do
  timestamp=$(date +%Y%m%d_%H%M%S)
  uv run python scripts/shorts_transcribe.py "$video" \
    --outdir "runs/$timestamp" --device cuda --vad
  uv run python scripts/shorts_builder.py "$video" \
    --workdir "runs/$timestamp" --num-shorts 3
done
```

## Troubleshooting

### Quick Fixes

**"CUDA/cuDNN errors" or "Unable to load libcudnn"**
- Use CPU mode: `--device cpu --compute-type int8 --model base`
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for GPU fix

**"No module named 'faster_whisper'"**
- Run `uv sync` to install dependencies

**"CUDA out of memory"**
- Use smaller model: `--model base` or `--model small`
- Switch to CPU: `--device cpu --compute-type int8`

**"FFmpeg not found"**
- Install FFmpeg (see Prerequisites)
- Ensure it's in your PATH: `ffmpeg -version`

**"Invalid API key"**
- Check `.env` file has correct `OPENAI_API_KEY`
- Verify key with: `echo $OPENAI_API_KEY`

**Poor highlight selection**
- Increase context: edit `target_chars` in `shorts_builder.py`
- Modify prompt: edit `templates/prompt_highlights.txt`
- Try different model: `--model gpt-4`

**For detailed troubleshooting**, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Why uv?

- **10-100x faster** than pip for dependency resolution
- **Automatic venv management** - no manual activation needed with `uv run`
- **Better reproducibility** with lock files
- **Single command setup** - `uv sync` does everything

## License

MIT

