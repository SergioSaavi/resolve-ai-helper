# Quick Start Guide

Get started with Resolve AI Helper in 5 minutes!

## 🎯 Overview

This guide walks you through your first transcription from start to finish.

**What you'll do:**
1. Open a timeline in DaVinci Resolve
2. Run the transcription script
3. Configure settings
4. Wait for processing
5. Get subtitles automatically added to your timeline!

**Time needed:** 5-10 minutes (depending on video length)

---

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ DaVinci Resolve installed and running
- ✅ Resolve AI Helper installed ([Installation Guide](INSTALL.md))
- ✅ FFmpeg installed
- ✅ At least one timeline with video content

Not installed yet? See [INSTALL.md](INSTALL.md)

---

## Step-by-Step Guide

### Step 1: Open Your Timeline

1. Launch **DaVinci Resolve**
2. Open an existing project or create a new one
3. Open a timeline that contains video content
4. Make sure the timeline is **selected/active**

**Tip:** Start with a short video (< 5 minutes) for your first test!

---

### Step 2: Launch the Script

1. Click **Workspace** in the top menu bar
2. Select **Scripts**
3. Click **transcribe_timeline**

![Menu Location](docs/images/menu-location.png)

**If you don't see the script:**
- Did you restart Resolve after installation?
- Check the [Installation Guide](INSTALL.md#step-3-install-resolve-script)

---

### Step 3: Configure Settings

A window will appear with transcription settings:

#### Timeline Information
You'll see details about your current timeline:
- **Name**: Your timeline name
- **Duration**: Length of the timeline
- **FPS**: Frame rate

#### Choose Your Model

| Model | Best For | Speed | Size |
|-------|----------|-------|------|
| **tiny** | Quick tests, drafts | ⚡⚡⚡⚡⚡ | 75MB |
| **base** | Most users ⭐ | ⚡⚡⚡⚡ | 150MB |
| **small** | Professional work | ⚡⚡⚡ | 500MB |
| **medium** | Maximum quality | ⚡⚡ | 1.5GB |

**Recommendation for first time:** Choose **base** model

#### Select Processing Device

- **Auto-detect (recommended)**: Automatically uses GPU if available, falls back to CPU
- **CPU only**: Works everywhere, slower
- **GPU (CUDA)**: Requires NVIDIA GPU, 10x faster

**Recommendation:** Keep on **Auto-detect**

#### Choose Language

- **Auto-detect (recommended)**: Works well for most content
- Or select a specific language if you know it

**Recommendation:** Keep on **Auto-detect**

---

### Step 4: Start Transcription

1. Review your settings
2. Click **Transcribe →** button
3. The settings window will close

**First run only:** The model will download (~75-150MB for base model). This takes 1-5 minutes depending on your internet speed.

---

### Step 5: Monitor Progress

A progress window will appear showing:

- **Progress bar**: Overall completion percentage
- **Current status**: What's happening now
- **Time elapsed**: How long it's been running
- **Estimated remaining**: How much longer (appears after 5%)
- **Live log**: Detailed progress messages
- **Statistics**: Segments and words detected

**What's happening:**
1. Extracting audio from video
2. Loading Whisper model
3. Transcribing audio (this takes the longest)
4. Generating SRT file

**Estimated times (for base model):**
- 5-minute video: 1-2 minutes (GPU) or 5-10 minutes (CPU)
- 30-minute video: 6-12 minutes (GPU) or 30-60 minutes (CPU)
- 1-hour video: 12-24 minutes (GPU) or 60-120 minutes (CPU)

**Can I cancel?**
Yes! Click the **Cancel** button if needed. Already processed segments will be saved.

---

### Step 6: Review Results

When transcription completes, a results dialog appears:

#### Success! ✅

You'll see:
- **Confirmation message**: "Transcription Complete!"
- **Output file location**: Where the SRT was saved
- **Statistics**:
  - Duration transcribed
  - Language detected
  - Number of segments
  - Number of words
  - Processing time

**The subtitles have been automatically imported to your timeline!**

#### What if it fails? ❌

If transcription fails, you'll see:
- **Error message**: What went wrong
- **Common solutions**: How to fix it
- **Support link**: Where to get help

Common errors and solutions:
- **FFmpeg not found**: [Install FFmpeg](INSTALL.md#2-ffmpeg)
- **Model download failed**: Check internet connection
- **CUDA error**: Switch to CPU mode

---

### Step 7: Check Your Timeline

1. The results dialog will close
2. Look at your timeline in DaVinci Resolve
3. You should see a new **subtitle track** with your captions!

**Finding the subtitles:**
- Look for a new track labeled with subtitle icon
- Subtitles start at the beginning of your timeline
- Zoom in to see individual subtitle segments

---

## Next Steps

### Editing Subtitles

**In DaVinci Resolve:**
1. Select a subtitle clip
2. Use the **Inspector** panel to edit
3. Change text, timing, position, and styling

**Export for manual editing:**
The SRT file is saved and can be edited in any text editor or subtitle software like:
- Subtitle Edit (free)
- Aegisub (free)
- Any text editor

**Re-import after editing:**
1. File → Import → Select your edited SRT
2. Drag to timeline

### Styling Subtitles

Make your subtitles look professional:

1. Select subtitle clip
2. Open **Inspector** panel (top right)
3. Adjust settings:
   - **Font**: Choose a readable font
   - **Size**: Adjust for visibility
   - **Color**: Match your brand
   - **Outline**: Add for readability
   - **Position**: Center, top, or bottom
   - **Alignment**: Left, center, right

**Pro tip:** Create a subtitle preset for consistent styling across projects!

### Advanced Features

Want to do more?

- **Multiple languages**: Transcribe in 90+ languages
- **Batch processing**: Process multiple timelines
- **Export options**: Save SRT for other software
- **Model comparison**: Try different models for best results

See [User Guide](docs/USER_GUIDE.md) for advanced features.

---

## Common Questions

### How accurate is the transcription?

Accuracy depends on:
- **Model size**: Larger = more accurate
- **Audio quality**: Clear audio = better results
- **Language**: English works best
- **Accents**: May need manual correction

**Typical accuracy:**
- Clear speech: 90-95%
- Background noise: 70-85%
- Heavy accents: 60-80%

**Always review and edit subtitles for professional work!**

### Can I use this for long videos?

Yes! The tool handles videos of any length:
- Short (< 5 min): A few minutes
- Medium (5-30 min): 10-30 minutes
- Long (30 min - 2 hours): 30-120 minutes
- Very long (2+ hours): May take several hours on CPU

**Tips for long videos:**
- Use GPU if available
- Use smaller model (base or tiny)
- Run overnight for multi-hour content
- Consider splitting very long timelines

### Does this work offline?

After first run: **Yes!**

- **First run**: Requires internet to download model (~75MB-1.5GB)
- **Subsequent runs**: Completely offline
- Models are cached locally

### What about privacy?

**Your data stays on your computer:**
- No cloud processing
- No data sent to external servers
- 100% local processing
- Open source code you can verify

### Can I transcribe multiple timelines?

Yes! Run the script multiple times:
1. Transcribe first timeline
2. Switch to next timeline
3. Run script again

**Coming soon:** Batch processing multiple timelines at once!

---

## Tips & Tricks

### Faster Transcription

1. **Use GPU**: 10x faster than CPU
2. **Smaller model**: Tiny is 2x faster than base
3. **Extract audio first**: Pre-process long videos
4. **Optimize timeline**: Remove unnecessary tracks

### Better Accuracy

1. **Larger model**: Use small or medium
2. **Clean audio**: Remove background noise first
3. **Specify language**: Don't use auto-detect if you know the language
4. **Edit timeline audio**: Use Fairlight to enhance dialogue

### Workflow Integration

1. **Transcribe early**: Do it while editing other aspects
2. **Save presets**: Use same settings for series
3. **Export SRT**: Keep copies for archival/reuse
4. **Version control**: Save different subtitle versions

---

## Troubleshooting

### "No timeline selected"

**Problem**: Script says no timeline is open

**Solution**: 
- Click on a timeline to select it
- Ensure you're in Edit page, not Color/Fairlight
- Timeline must have video content

### Transcription is slow

**Problem**: Taking too long to process

**Solutions**:
- Switch to GPU mode (10x faster)
- Use smaller model (tiny or base)
- Check Task Manager - is CPU maxed out?
- Close other applications

### Subtitles are inaccurate

**Problem**: Wrong words or poor quality

**Solutions**:
- Use larger model (small or medium)
- Check audio quality in timeline
- Specify correct language (don't use auto)
- Edit subtitles manually after

### Import failed

**Problem**: Subtitles didn't appear in timeline

**Solutions**:
- Check if SRT file was created (shown in results)
- Manually import: File → Import → Select SRT
- Drag SRT from Media Pool to timeline
- Check timeline has subtitle track

---

## Getting Help

Need more assistance?

1. **Documentation**: Check [User Guide](docs/USER_GUIDE.md)
2. **Troubleshooting**: See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **Issues**: Report on [GitHub Issues](https://github.com/your-repo/resolve-ai-helper/issues)
4. **Discussions**: Join [GitHub Discussions](https://github.com/your-repo/resolve-ai-helper/discussions)

---

## What's Next?

Now that you've completed your first transcription:

- 📚 Read the [User Guide](docs/USER_GUIDE.md) for advanced features
- 🎨 Learn subtitle styling techniques
- 🚀 Explore different Whisper models
- 🤝 Join our community and share feedback
- ⭐ Star the project on GitHub if you found it useful!

---

**Happy transcribing! 🎬✨**
