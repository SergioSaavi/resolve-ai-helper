# Quick Start Guide

## 🚀 Setup (One-Time)

```bash
# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## 📹 Basic Usage

### Step 1: Transcribe

**GPU Mode (fast, requires CUDA/cuDNN):**
```bash
uv run python scripts/shorts_transcribe.py video.mp4 \
  --device cuda \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)
```

**CPU Mode (slower but reliable, no GPU needed):**
```bash
uv run python scripts/shorts_transcribe.py video.mp4 \
  --device cpu \
  --compute-type int8 \
  --model base \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)
```

**Output**: `runs/TIMESTAMP/transcript.jsonl` + `captions.ass`

### Step 2: Generate Shorts
```bash
uv run python scripts/shorts_builder.py video.mp4 \
  --workdir runs/TIMESTAMP \
  --num-shorts 5
```

**Output**: `runs/TIMESTAMP/shorts/*.mp4`

## 🎨 Caption Styling

Edit `scripts/shorts_transcribe.py`, find `ASS_HEADER`:

```python
# Change font and size
Style: Default,Montserrat,80,&H00FFFFFF,...

# Change color (ABGR hex)
Style: Default,Inter,64,&H0000FFFF,...  # Yellow
Style: Default,Inter,64,&H00FF00FF,...  # Magenta
```

**Colors**:
- `&H00FFFFFF` = White
- `&H0000FFFF` = Yellow  
- `&H00FF0000` = Blue
- `&H0000FF00` = Green

## 🔧 Common Options

### GPU vs CPU
```bash
# GPU (fast)
--device cuda --compute-type float16

# CPU (slow but works anywhere)
--device cpu --compute-type int8
```

### Model Size
```bash
--model tiny    # Fastest, least accurate
--model base    # Fast, good for testing
--model medium  # Balanced (recommended)
--model large-v3  # Best quality, slow
```

### Aspect Ratios
```bash
--aspect 9:16   # TikTok/Shorts (default)
--aspect 1:1    # Instagram
--aspect 16:9   # YouTube horizontal
```

### Quality Settings
```bash
--crf 18        # Best quality
--crf 20        # Good quality (default)
--crf 23        # Balanced
--preset slow   # Better quality, slower
--preset veryfast  # Faster, good quality (default)
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "CUDA/cuDNN errors" | Use CPU: `--device cpu --compute-type int8 --model base` |
| "faster_whisper not found" | `uv sync` |
| "CUDA out of memory" | Use `--model base` or `--device cpu` |
| "FFmpeg not found" | Install: `sudo apt install ffmpeg` |
| Font not rendering | Install Inter font or change font name |
| Poor highlights | Edit `templates/prompt_highlights.txt` |

**Detailed help**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📚 Full Documentation

- **README.md** - Complete usage guide
- **PLAN.md** - Detailed implementation & customization
- **.env.example** - Configuration template

## 💡 Tips

1. **Use `--audio-first`** for large files (saves memory)
2. **Use `--vad`** to skip silence (better transcription)
3. **Test with `--model base`** first (faster iterations)
4. **Customize prompt** in `templates/prompt_highlights.txt` for your content type

---

**Need help?** Check PLAN.md or README.md for detailed docs.

