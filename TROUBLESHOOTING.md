# Troubleshooting Guide

## CUDA/cuDNN Errors

### Error: "Unable to load libcudnn_ops.so"

**Symptoms:**
```
Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so}
Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
```

**Cause:** Missing or incompatible cuDNN libraries for CUDA acceleration.

### Quick Fix: Use CPU Mode

The fastest solution is to use CPU transcription (slower but reliable):

```bash
# Small model, CPU mode (fastest CPU option)
uv run python scripts/shorts_transcribe.py video.mp4 \
  --device cpu \
  --compute-type int8 \
  --model base \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)

# Medium model, CPU mode (better quality, slower)
uv run python scripts/shorts_transcribe.py video.mp4 \
  --device cpu \
  --compute-type int8 \
  --model medium \
  --vad \
  --audio-first \
  --outdir runs/$(date +%Y%m%d_%H%M%S)
```

**Performance:** 
- Base model: ~15-30 min for 1 hour video
- Medium model: ~45-60 min for 1 hour video

### Permanent Fix: Install cuDNN (WSL2/Linux)

If you want GPU acceleration:

#### Option 1: Install cuDNN via apt (Ubuntu 22.04+)

```bash
# Check CUDA version
nvidia-smi

# Install cuDNN for CUDA 12.x
sudo apt-get update
sudo apt-get install libcudnn9 libcudnn9-cuda-12

# Or for CUDA 11.x
sudo apt-get install libcudnn8 libcudnn8-cuda-11
```

#### Option 2: Manual cuDNN Installation

1. Download cuDNN from [NVIDIA Developer](https://developer.nvidia.com/cudnn)
2. Extract and copy libraries:
```bash
tar -xvf cudnn-linux-x86_64-*.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

3. Update library path:
```bash
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

#### Option 3: Use Docker (Easiest GPU setup)

```bash
docker run --gpus all -it -v $(pwd):/workspace nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
cd /workspace
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv sync
```

### Verify GPU Setup

```bash
# Check CUDA
nvidia-smi

# Check cuDNN
ldconfig -p | grep cudnn

# Test with faster-whisper
uv run python -c "from faster_whisper import WhisperModel; m=WhisperModel('base', device='cuda'); print('GPU OK')"
```

## Common Issues

### Issue: "FFmpeg not found"

```bash
# Ubuntu/WSL2
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

### Issue: "OpenAI API rate limit"

**Solution:** Use local LLM with Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2

# Configure .env
echo "OPENAI_BASE_URL=http://localhost:11434/v1" >> .env
echo "OPENAI_MODEL=llama3.2" >> .env
```

### Issue: "Out of memory" (CPU mode)

**Solutions:**
- Use smaller model: `--model tiny` or `--model base`
- Process shorter videos
- Reduce chunk length: `--chunk-length 15`

### Issue: Poor transcription quality

**Solutions:**
1. Use larger model: `--model medium` or `--model large-v3`
2. Specify language: `--language en` (or your language code)
3. Enable VAD: `--vad` (removes silence, better accuracy)
4. Use GPU mode (better quality due to float16 precision)

### Issue: Subtitles not visible in rendered shorts

**Check:**
1. Verify ASS file generated: `cat runs/*/captions.ass`
2. Check font installed: `fc-list | grep -i inter`
3. Test subtitle separately:
   ```bash
   ffplay -vf "subtitles=runs/TIMESTAMP/captions.ass" video.mp4
   ```

**Fix:**
- Install Inter font: `sudo apt install fonts-inter`
- Or change font in `scripts/shorts_transcribe.py` ASS_HEADER to `Arial` or `DejaVu Sans`

### Issue: LLM returns no highlights

**Causes:**
- Video too short (< 3 minutes)
- Transcript has no good segments
- Prompt mismatch with content type

**Solutions:**
1. Check transcript: `cat runs/*/transcript.jsonl`
2. Customize prompt: Edit `templates/prompt_highlights.txt`
3. Reduce requirements: Lower `--num-shorts` to 1-2
4. Use better model: `--model gpt-4` instead of `gpt-4o-mini`

### Issue: Scripts run but no output

**Debug:**
```bash
# Verbose output
set -x
uv run python scripts/shorts_transcribe.py video.mp4 --outdir runs/test --device cpu

# Check outputs
ls -lah runs/test/
cat runs/test/transcript.jsonl
```

## Performance Comparison

| Configuration | Speed (1hr video) | Quality | Memory | Use Case |
|---------------|-------------------|---------|--------|----------|
| GPU + medium + float16 | 3-5 min | ⭐⭐⭐⭐⭐ | ~4 GB VRAM | Production |
| GPU + base + float16 | 1-2 min | ⭐⭐⭐⭐ | ~2 GB VRAM | Fast iteration |
| CPU + medium + int8 | 45-60 min | ⭐⭐⭐⭐ | ~2 GB RAM | No GPU |
| CPU + base + int8 | 15-30 min | ⭐⭐⭐ | ~1 GB RAM | Testing |
| CPU + tiny + int8 | 5-10 min | ⭐⭐ | ~512 MB RAM | Ultra-fast draft |

## Getting Help

1. **Check logs:**
   ```bash
   uv run python scripts/shorts_transcribe.py video.mp4 --outdir runs/debug 2>&1 | tee debug.log
   ```

2. **Verify installation:**
   ```bash
   uv run python -c "from faster_whisper import WhisperModel; from openai import OpenAI; print('OK')"
   ```

3. **Test individual components:**
   ```bash
   # Test transcription only
   uv run python -c "from faster_whisper import WhisperModel; m=WhisperModel('base', device='cpu'); print('Whisper OK')"
   
   # Test FFmpeg
   ffmpeg -version
   
   # Test OpenAI API
   uv run python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); c=OpenAI(); print('API OK')"
   ```

## Still Having Issues?

- Check README.md for usage examples
- Check PLAN.md for detailed documentation
- Verify all prerequisites installed (FFmpeg, Python 3.9+, uv)
- Try with a short test video first (< 5 minutes)

