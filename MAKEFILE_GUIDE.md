# Makefile Quick Reference

## 🚀 Super Simple Commands

### Get Started
```bash
make install              # Install everything
```

### Most Common Workflows

**1. Get SRT for Premiere (Manual Styling)**
```bash
make transcribe-srt VIDEO=my_video.mp4
# → Gets: runs/TIMESTAMP/captions.srt
# Import to Premiere and style yourself!
```

**2. Full Auto Shorts**
```bash
make full VIDEO=my_video.mp4
# Does everything: transcribe + generate 5 shorts
```

**3. Quick Test (Fast)**
```bash
make quick VIDEO=my_video.mp4
# Fast base model, 3 shorts
```

**4. High Quality (Slow)**
```bash
make quality VIDEO=my_video.mp4
# Medium model, CRF 17, slow preset
```

## 📋 All Commands

### Transcription

| Command | What it does |
|---------|--------------|
| `make transcribe VIDEO=input.mp4` | CPU transcribe → SRT + ASS |
| `make transcribe-gpu VIDEO=input.mp4` | GPU transcribe (faster) |
| `make transcribe-srt VIDEO=input.mp4` | **Just get SRT for Premiere** |

### Building Shorts

| Command | What it does |
|---------|--------------|
| `make build WORKDIR=runs/20241017_123456` | Generate shorts from transcript |
| `make full VIDEO=input.mp4` | Do everything in one command |

### Customization

```bash
# Change number of shorts
make full VIDEO=my_vod.mp4 NUM_SHORTS=10

# Change model quality
make transcribe VIDEO=input.mp4 MODEL=medium

# Change video quality
make build WORKDIR=runs/... CRF=15  # Higher quality (slower)

# GPU transcription
make transcribe-gpu VIDEO=input.mp4
```

### Utilities

| Command | What it does |
|---------|--------------|
| `make list` | Show all your runs |
| `make latest` | Get path to latest run |
| `make clean` | Delete old runs (keep last 3) |
| `make clean-all` | Delete ALL runs |
| `make test-captions` | Preview captions on 10s clip |

## 🎬 Real World Examples

### Example 1: Podcast → Premiere
```bash
# Get SRT file for manual styling
make transcribe-srt VIDEO=podcast_ep45.mp4 MODEL=medium

# Output: runs/20241017_123456/captions.srt
# Import to Premiere, style in Essential Graphics
```

### Example 2: Gaming Stream → Auto Shorts
```bash
# Full workflow
make full VIDEO=gaming_stream.mp4 NUM_SHORTS=15

# Outputs: runs/.../shorts/*.mp4 (15 clips ready to upload)
```

### Example 3: 4-Hour VOD → Many Shorts
```bash
# Transcribe once
make transcribe VIDEO=long_vod.mp4 MODEL=medium
# Output: runs/20241017_120000/

# Generate multiple batches
make build WORKDIR=runs/20241017_120000 NUM_SHORTS=20

# Want more? Edit templates/prompt_highlights.txt and run again
make build WORKDIR=runs/20241017_120000 NUM_SHORTS=20
```

### Example 4: Quick Testing
```bash
# Fast test with tiny model
make transcribe VIDEO=test.mp4 MODEL=tiny DEVICE=cpu

# Test first 10 seconds of captions
make test-captions VIDEO=test.mp4
# Output: test_captions.mp4
```

## ⚙️ Configuration Variables

Override any variable on the command line:

```bash
make transcribe \
  VIDEO=my_video.mp4 \
  MODEL=medium \
  DEVICE=cuda \
  OUTDIR=runs/custom_name
```

### Available Variables

| Variable | Default | Options |
|----------|---------|---------|
| `VIDEO` | video.mp4 | Your video file |
| `MODEL` | base | tiny, base, small, medium, large-v3 |
| `DEVICE` | cpu | cpu, cuda |
| `COMPUTE_TYPE` | int8 | int8, float16, float32 |
| `NUM_SHORTS` | 5 | Any number |
| `CRF` | 17 | 15-23 (lower = better quality) |
| `PRESET` | medium | ultrafast, veryfast, medium, slow, veryslow |
| `OUTDIR` | runs/TIMESTAMP | Custom output directory |

## 🎯 Common Workflows

### For Premiere Users (Manual Styling)
```bash
# Step 1: Get SRT
make transcribe-srt VIDEO=my_project.mp4 MODEL=medium

# Step 2: In Premiere
# - Import video
# - File > Import > runs/.../captions.srt
# - Open Captions workspace
# - Style in Essential Graphics panel
```

### For TikTok/Shorts (Auto Everything)
```bash
# One command, done!
make full VIDEO=my_content.mp4

# Upload: runs/.../shorts/*.mp4
```

### For YouTube (High Quality)
```bash
make quality VIDEO=my_video.mp4
# Uses: medium model, CRF 17, slow preset
```

### For Testing (Fast Iteration)
```bash
make quick VIDEO=test.mp4
# Uses: base model, CPU, 3 shorts
```

## 💡 Pro Tips

1. **Check your runs:**
   ```bash
   make list
   ```

2. **Get latest run path:**
   ```bash
   LATEST=$(make latest)
   echo $LATEST
   ```

3. **Clean up disk space:**
   ```bash
   make clean      # Keep last 3
   make clean-all  # Delete everything
   ```

4. **Test captions before generating all shorts:**
   ```bash
   make test-captions VIDEO=input.mp4
   vlc test_captions.mp4
   ```

5. **Chain commands:**
   ```bash
   make transcribe-srt VIDEO=vid.mp4 && echo "Ready for Premiere!"
   ```

## 📝 Notes

- **SRT files** are always generated (at `runs/.../captions.srt`)
- **ASS files** have the styled captions (black text, white outline, max 5 words)
- Use `transcribe-srt` when you want to style manually in Premiere
- Use `full` when you want auto-generated shorts with burned-in captions
- All runs are timestamped: `runs/20241017_123456/`

## 🆘 Troubleshooting

**"make: command not found"**
- Linux/Mac: Should be pre-installed
- Windows: Use WSL2 or Git Bash

**"Video not found"**
```bash
# Use absolute or relative path
make transcribe VIDEO=./videos/my_video.mp4
```

**"WORKDIR not set"**
```bash
# Get the path first
make list
# Then use it
make build WORKDIR=runs/20241017_123456
```

**GPU errors**
```bash
# Fall back to CPU
make transcribe VIDEO=input.mp4 DEVICE=cpu
```

---

**Need more help?** Run `make help` or check `README.md`

