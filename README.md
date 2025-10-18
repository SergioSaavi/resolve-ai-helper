# Resolve AI Helper

**Bring AI-powered transcription to DaVinci Resolve's free version!**

Resolve AI Helper is an open-source tool that adds automatic subtitle generation to DaVinci Resolve using OpenAI's Whisper AI, bypassing the limitations of the free version.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)
![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)

## ✨ Features

- 🎯 **One-Click Transcription**: Select timeline → Run script → Get subtitles
- 🚀 **GPU Acceleration**: Utilize CUDA for 10x faster transcription
- 🎨 **Modern UI**: Beautiful PySide6 interface with live progress tracking
- 🌍 **Multi-Language**: Supports 90+ languages with auto-detection
- 📝 **SRT Export**: Industry-standard subtitle format
- 🆓 **100% Free**: Works with DaVinci Resolve free version
- 🔓 **Open Source**: MIT license, community-driven development

## 🎬 How It Works

```
┌────────────────────────────────────────────────────────────┐
│                 DaVinci Resolve (Free)                     │
│  Workspace → Scripts                                       │
│  • resolve-ai-helper.py        (main script, persistent)   │
│  • launch_transcribe_ui.py     (one‑shot launcher)         │
└───────────────┬────────────────────────────────────────────┘
                │  JSON over stdin/stdout (pipes)
                ▼
┌────────────────────────────────────────────────────────────┐
│           Standalone Executable (PySide6 UI)               │
│  • Fast onedir build                                       │
│  • Interactive mode (--interactive)                        │
│    - Listens for JSON commands on stdin                    │
│    - Emits single‑line JSON responses on stdout            │
│  • Whisper via faster‑whisper (models download on first run)│
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│              Timeline / Media Pool (in Resolve)            │
│  • Supervisor imports SRT into subtitle track              │
└────────────────────────────────────────────────────────────┘
```

Why this approach
- Resolve Free cannot host custom UI; our UI runs externally.
- Resolve remains the single source of truth for all timeline actions; the supervisor script imports SRTs and controls the loop.
- Interactive mode lets the UI stay open for multiple actions without relaunching.

## 🚀 Quick Start

### Prerequisites

- **DaVinci Resolve** (Free or Studio) - [Download](https://www.blackmagicdesign.com/products/davinciresolve)
- **FFmpeg** - [Installation Guide](INSTALL.md#installing-ffmpeg)
- **Windows 10/11** (macOS/Linux support coming soon)

### Installation

1. **Download the latest release** from [Releases](https://github.com/your-repo/resolve-ai-helper/releases)

2. **Extract the ZIP file** to a location of your choice

3. **Run the installer** (or manual setup - see [INSTALL.md](INSTALL.md))

4. **Copy to Resolve (Comp scripts folder)**
   - Copy the entire folder `dist/ResolveAIHelper/` into:
     `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\`
   - Inside that folder you will have:
     - `resolve_ai_helper/` (the onedir exe folder)
     - `launch_transcribe_ui.py` (one‑shot)
     - You can also copy `resolve_scripts/resolve-ai-helper.py` (main script, recommended)

5. **Restart DaVinci Resolve**

### Usage

1. Open your timeline in DaVinci Resolve
Option A — Persistent (recommended for multi‑actions)
1. Workspace → Scripts → Comp → `resolve-ai-helper`
2. The UI opens once in interactive mode
3. Click actions in the UI (e.g., "Test Subtitle", or Transcribe)
4. Each action emits JSON; the supervisor imports the SRT to the timeline
5. Close the UI (or press Cancel) to stop the supervisor

Option B — One‑shot
1. Workspace → Scripts → Comp → `launch_transcribe_ui`
2. Configure settings in the UI → run once → window closes → supervisor logic not used

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

## 📖 Documentation

- **[Installation Guide](INSTALL.md)** - Detailed setup instructions
- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[User Guide](docs/USER_GUIDE.md)** - Complete feature documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🎛️ Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| **tiny** | ~75MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick drafts, testing |
| **base** | ~150MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | **Most users** (recommended) |
| **small** | ~500MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Professional work |
| **medium** | ~1.5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Maximum quality |

**Recommendation**: Start with `base` - it offers the best balance of speed and accuracy for most videos.

## 💻 System Requirements

### Minimum
- **OS**: Windows 10 (64-bit)
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Processor**: Intel Core i3 or equivalent

### Recommended
- **OS**: Windows 11 (64-bit)
- **RAM**: 8GB or more
- **GPU**: NVIDIA GPU with CUDA support (10x faster)
- **Storage**: 5GB free space (for multiple models)
- **Processor**: Intel Core i5 or equivalent

## 🛠️ Building from Source

Want to contribute or customize? Build from source:

```bash
# Clone repository
git clone https://github.com/your-repo/resolve-ai-helper.git
cd resolve-ai-helper

# Install dependencies
uv sync
# or: pip install -e .

# Run development version
python core/cli.py --version

# Build executable (fast onedir)
python build_exe.py --clean --full
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup.

## 🗺️ Roadmap

### ✅ Phase 1: Core Transcription (Current)
- [x] Whisper integration
- [x] PySide6 UI
- [x] Resolve script integration
- [x] Windows support

### 🚧 Phase 2: Enhanced Features (In Progress)
- [ ] LLM-powered highlight detection
- [ ] Multi-language subtitle tracks
- [ ] Subtitle styling options
- [ ] Batch processing multiple timelines
- [ ] Rich Resolve supervisor (queue, retries, logging)

## 🔌 Interactive JSON Protocol (advanced)

The exe accepts JSON commands on stdin when launched with `--interactive` and prints one JSON response per command on stdout.

Requests (stdin)
```json
{"cmd":"test_place"}
{"cmd":"transcribe","input":"C:\\path\\video.mp4","model":"base","device":"auto","language":null}
{"cmd":"cancel"}
{"cmd":"shutdown"}
```

Responses (stdout)
```json
{"success":true,"srt_path":"C:\\...\\file.srt"}
{"success":false,"error":"cancel"}
{"success":false,"error":"<message>"}
```

Notes
- Models are NOT bundled; the first run downloads to the user cache: `%USERPROFILE%\.cache\resolve-ai-helper\models`.
- The exe prints exactly one response per command; the supervisor should read lines and parse JSON.

### 🔮 Phase 3: Cross-Platform (Planned)
- [ ] macOS support
- [ ] Linux support
- [ ] GitHub Actions CI/CD
- [ ] Auto-updates

### 💡 Phase 4: Advanced AI (Future)
- [ ] Speaker diarization
- [ ] Auto-translation
- [ ] Sentiment analysis for editing
- [ ] Smart b-roll suggestions

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Report Bugs**: Open an issue with details
- 💡 **Suggest Features**: Share your ideas in discussions
- 🔧 **Submit PRs**: Fix bugs or add features
- 📖 **Improve Docs**: Help make documentation better
- ⭐ **Star the Project**: Show your support!

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

### Third-Party Licenses
- **faster-whisper**: MIT License
- **PySide6**: LGPL
- **PyInstaller**: GPL with exception

## 🙏 Acknowledgments

- **OpenAI** - For creating Whisper
- **Blackmagic Design** - For DaVinci Resolve
- **faster-whisper team** - For the optimized implementation
- All our amazing contributors!

## 📞 Support

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/your-repo/resolve-ai-helper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/resolve-ai-helper/discussions)
- **Email**: support@your-email.com (for security issues)

## ⚠️ Disclaimer

This is an independent project and is not affiliated with, endorsed by, or connected to Blackmagic Design or OpenAI. DaVinci Resolve is a trademark of Blackmagic Design Pty Ltd.

---

<div align="center">

**Made with ❤️ by the open-source community**

[⭐ Star on GitHub](https://github.com/your-repo/resolve-ai-helper) | [📖 Documentation](docs/) | [🐛 Report Bug](https://github.com/your-repo/resolve-ai-helper/issues)

</div>
