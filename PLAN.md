# Shorts Builder - Implementation Plan & Setup Guide

## Project Overview

**Goal**: Build an automated pipeline to convert long-form VOD videos into viral short-form clips (15-60 seconds) with styleable burned-in captions.

**Tech Stack**:
- **Transcription**: faster-whisper (GPU-accelerated Whisper)
- **Captions**: ASS format (Advanced SubStation Alpha) with karaoke word timing
- **Highlight Selection**: OpenAI GPT-4o-mini (or compatible LLM)
- **Video Rendering**: FFmpeg
- **Package Management**: uv (Astral's fast Python package manager)

## Architecture

```
┌─────────────┐
│  Input VOD  │
│  (MP4/MKV)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  1. TRANSCRIPTION           │
│  shorts_transcribe.py       │
│  • Extract audio (16kHz)    │
│  • Whisper (GPU/CPU)        │
│  • Generate word timestamps │
│  • Export JSONL/SRT/ASS     │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ transcript.  │
    │   jsonl      │
    │ captions.ass │
    └──────┬───────┘
           │
           ▼
┌─────────────────────────────┐
│  2. HIGHLIGHT SELECTION     │
│  shorts_builder.py          │
│  • Sample transcript        │
│  • Call LLM API             │
│  • Parse JSON response      │
│  • Validate + deduplicate   │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │  Highlight   │
    │  timestamps  │
    └──────┬───────┘
           │
           ▼
┌─────────────────────────────┐
│  3. SHORT RENDERING         │
│  shorts_builder.py          │
│  • FFmpeg trim video        │
│  • Scale/crop to 9:16       │
│  • Burn ASS captions        │
│  • Export shorts/*.mp4      │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │  Final MP4   │
    │  shorts with │
    │  captions    │
    └──────────────┘
```

## Installation & Setup

### Step 1: System Prerequisites

#### FFmpeg (Required)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
ffmpeg -version  # Verify installation
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows (Chocolatey):**
```powershell
choco install ffmpeg
```

**Manual Installation:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to system PATH

#### uv Package Manager

```bash
# Unix/Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Verify installation
uv --version
```

#### CUDA Toolkit (Optional, for GPU acceleration)

- **Required for**: `--device cuda` in transcription
- **Download**: [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- **Alternative**: Use CPU mode with `--device cpu --compute-type int8`

### Step 2: Project Setup

```bash
# Navigate to project directory
cd /home/saavi/projects/auto-shorts

# Initialize Python environment and install dependencies
uv sync

# This command will:
# 1. Create .venv/ virtual environment
# 2. Install Python 3.11 (as specified in .python-version)
# 3. Install all dependencies from pyproject.toml
# 4. Generate uv.lock file for reproducibility
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or vim, code, etc.
```

**Required Configuration:**
```env
OPENAI_API_KEY=sk-proj-...your-actual-key...
OPENAI_MODEL=gpt-4o-mini
```

**Optional (for local LLMs like Ollama):**
```env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2
OPENAI_API_KEY=dummy
```

### Step 4: Verify Installation

```bash
# Test imports
uv run python -c "from faster_whisper import WhisperModel; from openai import OpenAI; print('✓ All dependencies loaded')"

# Check FFmpeg
ffmpeg -version

# Test CUDA (if using GPU)
uv run python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Usage Workflow

### Workflow 1: Basic Usage (5 shorts from one video)

```bash
# 1. Transcribe video (GPU)
uv run python scripts/shorts_transcribe.py video.mp4 \
  --model medium \
  --device cuda \
  --compute-type float16 \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)

# Note the output directory path (e.g., runs/20251016_143022)

# 2. Generate shorts
uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/20251016_143022 \
  --num-shorts 5

# 3. Find outputs
ls runs/20251016_143022/shorts/
# Output: 01_intro.mp4, 02_funny_moment.mp4, ...
```

### Workflow 2: CPU Transcription (no GPU)

```bash
# Use smaller model + CPU
uv run python scripts/shorts_transcribe.py video.mp4 \
  --model base \
  --device cpu \
  --compute-type int8 \
  --outdir runs/current

uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/current \
  --num-shorts 3
```

### Workflow 3: Custom Aspect Ratios

```bash
# Square (Instagram)
uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/current \
  --aspect 1:1

# Standard horizontal (YouTube)
uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/current \
  --aspect 16:9
```

### Workflow 4: High-Quality Encoding

```bash
# Better quality, slower encoding
uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/current \
  --crf 18 \
  --preset slow
```

## Script Parameters Reference

### shorts_transcribe.py

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | *required* | Path to input video file |
| `--outdir` | `runs/current` | Output directory for transcripts |
| `--model` | `medium` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3` |
| `--device` | `cuda` | Device: `cuda`, `cpu`, `auto` |
| `--compute-type` | `float16` | Precision: `float16`, `float32`, `int8`, `int8_float16` |
| `--language` | `None` | Force language code (e.g., `en`, `es`, `fr`) or auto-detect |
| `--chunk-length` | `30` | Audio chunk length in seconds |
| `--vad` | `False` | Enable Voice Activity Detection (recommended) |
| `--no-words` | `False` | Disable word-level timestamps (faster but no karaoke) |
| `--audio-first` | `False` | Extract 16kHz WAV first (recommended for large files) |
| `--force-audio` | `False` | Re-extract audio even if exists |
| `--resume` | `False` | Resume from existing transcript.jsonl |

### shorts_builder.py

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | *required* | Path to original video file |
| `--workdir` | *required* | Directory with transcript.jsonl and captions.ass |
| `--num-shorts` | `5` | Number of shorts to generate |
| `--aspect` | `9:16` | Aspect ratio: `9:16`, `1:1`, `16:9` |
| `--crf` | `20` | Quality (18-28, lower=better) |
| `--preset` | `veryfast` | Encoding speed: `ultrafast`, `veryfast`, `medium`, `slow`, `veryslow` |
| `--model` | `$OPENAI_MODEL` | LLM model name |

## ASS Caption Customization Guide

### Understanding ASS Format

The `captions.ass` file uses Advanced SubStation Alpha format with two styles:

1. **Default**: Static text (fallback when no word timestamps)
2. **Emph**: Karaoke-style word-by-word highlighting

### Style Format Breakdown

```
Style: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
```

**Example:**
```
Style: Default,Inter,64,&H00FFFFFF,&H00000000,&H7F000000,&H32000000,0,0,0,0,100,100,0,0,1,4,0,2,60,60,80,1
```

### Common Customizations

#### Change Font & Size

```python
# In scripts/shorts_transcribe.py, ASS_HEADER section:
Style: Default,Montserrat,72,&H00FFFFFF,...  # Larger, different font
```

#### Change Colors (ABGR Format)

Colors are in `&HAABBGGRR` hexadecimal:
- **AA**: Alpha (transparency) - `00` = opaque, `FF` = transparent
- **BB**: Blue component
- **GG**: Green component
- **RR**: Red component

**Examples:**
- `&H00FFFFFF` = White
- `&H0000FFFF` = Yellow
- `&H00FF00FF` = Magenta
- `&H0000FF00` = Green
- `&H00FFFF00` = Cyan

#### Change Position (Alignment)

```
Alignment values:
7  8  9  (top)
4  5  6  (middle)
1  2  3  (bottom)
```

- `2` = Bottom center (default for shorts)
- `8` = Top center
- `5` = Middle center

#### Change Outline & Shadow

```python
Style: Default,Inter,64,&H00FFFFFF,&H00000000,&H7F000000,&H32000000,0,0,0,0,100,100,0,0,1,4,2,2,60,60,80,1
#                                                                                    ^ ^
#                                                                           Outline-┘ └-Shadow
```

- **Outline**: Border width (0-4 typical)
- **Shadow**: Drop shadow offset (0-3 typical)

### Example Custom Styles

**Bold White with Heavy Outline:**
```
Style: Bold,Inter,70,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,50,50,100,1
```

**Subtle Yellow Karaoke:**
```
Style: Karaoke,Inter,60,&H0000FFFF,&H00FFFFFF,&H7F000000,&H32000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,90,1
```

**Top-Aligned Red Alert:**
```
Style: Alert,Inter,68,&H000000FF,&H00000000,&HFF000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,8,60,60,100,1
```

## Output Structure

```
runs/
└── 20251016_143022/          # Timestamped run directory
    ├── transcript.jsonl      # Raw transcript with word timing
    ├── captions.srt          # Standard SRT subtitles
    ├── captions.ass          # Styleable ASS subtitles
    ├── shorts_manifest.json  # Metadata for generated shorts
    └── shorts/
        ├── 01_intro_hook.mp4
        ├── 02_funny_moment.mp4
        ├── 03_epic_reaction.mp4
        ├── 04_insightful_point.mp4
        └── 05_outro_cta.mp4
```

### shorts_manifest.json Structure

```json
{
  "highlights": [
    {
      "index": 1,
      "title": "Intro Hook",
      "start": 12.5,
      "end": 38.2,
      "file": "/path/to/runs/20251016_143022/shorts/01_intro_hook.mp4"
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. "faster_whisper not found"
```bash
# Reinstall dependencies
uv sync --reinstall
```

#### 2. "CUDA out of memory"
```bash
# Use smaller model
--model base

# Or switch to CPU
--device cpu --compute-type int8
```

#### 3. "Font not found" in ASS rendering
```bash
# Install Inter font (or change font in ASS_HEADER)
# Ubuntu: sudo apt-get install fonts-inter
# macOS: brew install --cask font-inter
# Windows: Download from https://rsms.me/inter/
```

#### 4. "OpenAI API rate limit"
```bash
# Use local LLM (Ollama)
ollama serve
ollama pull llama3.2

# In .env:
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2
```

#### 5. Poor highlight quality
- **Increase context**: Edit `target_chars=16000` to `32000` in `shorts_builder.py`
- **Better prompt**: Modify `templates/prompt_highlights.txt`
- **Better model**: Use `gpt-4` or `gpt-4-turbo`

#### 6. Subtitles not visible
- Check aspect ratio matches video: `--aspect 9:16` vs `16:9`
- Verify ASS file generated: `cat runs/<dir>/captions.ass`
- Test subtitle separately: `ffplay -vf subtitles=captions.ass input.mp4`

## Performance Benchmarks

| Configuration | Speed (1hr video) | GPU Memory | Quality |
|---------------|-------------------|------------|---------|
| `medium` + `cuda` + `float16` | ~3-5 min | ~4 GB | Excellent |
| `base` + `cuda` + `float16` | ~1-2 min | ~2 GB | Good |
| `small` + `cpu` + `int8` | ~20-30 min | N/A | Good |
| `medium` + `cpu` + `int8` | ~45-60 min | N/A | Excellent |

## Advanced Techniques

### Batch Processing Multiple Videos

```bash
#!/bin/bash
for video in videos/*.mp4; do
  name=$(basename "$video" .mp4)
  outdir="runs/${name}_$(date +%Y%m%d_%H%M%S)"
  
  echo "Processing: $video → $outdir"
  
  uv run python scripts/shorts_transcribe.py "$video" \
    --outdir "$outdir" \
    --device cuda \
    --vad \
    --audio-first
  
  uv run python scripts/shorts_builder.py "$video" \
    --workdir "$outdir" \
    --num-shorts 3 \
    --crf 22
done
```

### Using with Local LLMs (Ollama)

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3.2

# Configure .env
echo "OPENAI_BASE_URL=http://localhost:11434/v1" >> .env
echo "OPENAI_MODEL=llama3.2" >> .env

# Run normally
uv run python scripts/shorts_builder.py video.mp4 --workdir runs/current
```

### Custom Highlight Logic

Edit `templates/prompt_highlights.txt`:
```
You are an expert editor making viral shorts from a long VOD.
Focus on:
- Technical tutorials (for dev content)
- Emotional moments (for vlogs)
- Controversial takes (for podcasts)
...
```

### Pre-processing Audio

```bash
# Extract high-quality audio first
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# Transcribe audio directly
uv run python scripts/shorts_transcribe.py audio.wav \
  --outdir runs/current

# Use original video for rendering
uv run python scripts/shorts_builder.py input.mp4 \
  --workdir runs/current
```

## Next Steps

1. **Test with sample video**:
   ```bash
   # Download test video
   youtube-dl -f best "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o test.mp4
   
   # Run pipeline
   uv run python scripts/shorts_transcribe.py test.mp4 --outdir runs/test
   uv run python scripts/shorts_builder.py test.mp4 --workdir runs/test --num-shorts 1
   ```

2. **Customize caption styles** (see ASS Customization Guide above)

3. **Tune LLM prompts** for your content type

4. **Automate with cron/GitHub Actions** for scheduled processing

## Resources

- **faster-whisper**: https://github.com/SYSTRAN/faster-whisper
- **FFmpeg filters**: https://ffmpeg.org/ffmpeg-filters.html
- **ASS format**: https://en.wikipedia.org/wiki/SubStation_Alpha
- **uv docs**: https://docs.astral.sh/uv/
- **OpenAI API**: https://platform.openai.com/docs

## Support

For issues or questions:
1. Check this PLAN.md troubleshooting section
2. Review README.md for common usage patterns
3. Inspect generated files: `transcript.jsonl`, `captions.ass`
4. Test components individually (transcription, then building)

---

**Happy shorts building! 🎬**

