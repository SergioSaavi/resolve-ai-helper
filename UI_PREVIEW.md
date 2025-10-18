# DaVinci Resolve-Inspired UI Preview

## 🎨 The New Look

```
┌────────────────────────────────────────────────────────────────┐
│ 🎬 AI Transcription                              v0.1.0        │ ← Orange title
│ ────────────────────────────────────────────────────────────── │ (#FF6E00)
│                                                                │
│ LIVE TIMELINE                                                  │ ← Section headers
│ Timeline:    viktor-shitshow-16-10-25.mp4                     │   (uppercase)
│ FPS:         24.00                                             │
│ Timecode:    01:25:41:15                                       │ ← Monospace
│ In/Out:      01:13:52:00 → 01:27:44:00 (832.00s)             │   timecodes
│ Selection:   ST1 Subtitle 204 Clips                           │
│ ────────────────────────────────────────────────────────────── │
│                                                                │
│ TIMELINE INFORMATION                                           │
│ Name:        viktor-shitshow-16-10-25.mp4                     │
│ Duration:    01:25:41:15                                       │
│ Frame Rate:  24.00                                             │
│ ────────────────────────────────────────────────────────────── │
│                                                                │
│ TRANSCRIPTION SETTINGS                                         │
│                                                                │
│ Whisper Model                                                  │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ base - Recommended (~150MB)                        ▼     │  │ ← Combobox
│ └──────────────────────────────────────────────────────────┘  │   (orange focus)
│                                                                │
│ Processing Device                                              │
│ ⦿ Auto-detect (Recommended)                                   │ ← Radio buttons
│ ○ CPU Only                                                     │   (orange fill)
│ ○ GPU (CUDA)                                                   │
│                                                                │
│ Language                                                       │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Auto-detect                                          ▼     │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ⚠ First run will download the selected model                  │ ← Warning
│                                                                │   (amber)
├────────────────────────────────────────────────────────────────┤
│                                                                │
│                    ┌─────────────┐  ┌──────────────────────┐ │
│                    │ Test        │  │ Transcribe Timeline  │ │ ← Action bar
│                    │ Subtitle    │  │                      │ │   (orange primary)
│                    └─────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## 🎯 Color Scheme (Exact Resolve Match)

### From Your Screenshot Analysis:

**Backgrounds:**
- `#0e0e0e` - Top toolbar, bottom action bar (darkest)
- `#1a1a1a` - Main background, scroll area
- `#1e1e1e` - Content panels (lighter)

**Borders:**
- `#2a2a2a` - Panel separators (subtle 1px lines)
- `#3a3a3a` - Input borders
- `#FF6E00` - Focus/hover borders (orange!)

**Text:**
- `#d0d0d0` - Primary text (values, body)
- `#909090` - Secondary text (labels)
- `#707070` - Headers (uppercase sections)

**Accents:**
- `#FF6E00` - **Primary accent** (Resolve orange!)
  - Selected items in Resolve
  - Active timeline clip
  - Our transcribe button
- `#FF9500` - Warning messages (amber)

## 🔄 Live Features

### Real-time Updates (Every 500ms)
The UI connects to your Resolve script and shows:

```python
# From resolve_scripts/test_exe_place_subtitle.py
# Sends JSON events every 500ms:

{
  "event": "timeline_state",
  "timeline": {
    "name": "viktor-shitshow-16-10-25.mp4",
    "fps": "24.00",
    "tc": "01:25:41:15",              # Current playhead
    "in_tc": "01:13:52:00",           # In mark
    "out_tc": "01:27:44:00",          # Out mark
    "range_seconds": 832.0            # Duration
  }
}
```

### What Gets Updated Live:
✅ Timeline name (when you switch timelines)
✅ FPS (timeline settings)
✅ Timecode (playhead position)
✅ In/Out marks (when you set I/O points)
✅ Selection (when you select media pool items)

## 📊 UI Components Breakdown

### Top Toolbar (50px)
```
┌────────────────────────────────────────────┐
│ 🎬 AI Transcription            v0.1.0     │
└────────────────────────────────────────────┘
     ↑ Orange (#FF6E00)        ↑ Gray
```

### Content Panels (Scrollable)
Each panel has:
- **Background**: `#1e1e1e`
- **Padding**: 20px horizontal, 15px vertical
- **Separator**: 1px solid `#2a2a2a`
- **Header**: UPPERCASE, 10px, `#707070`, letter-spacing: 1px

### Form Controls

**ComboBox (Dropdown):**
- Normal: `#0e0e0e` background, `#3a3a3a` border
- Hover: Orange border (`#FF6E00`)
- Focus: Orange border
- Selected item: Orange background

**Radio Button:**
- Unchecked: Gray circle (`#5a5a5a`)
- Checked: Orange circle (`#FF6E00`) with white dot

**Primary Button (Transcribe):**
- Background: `#FF6E00` (Resolve orange!)
- Hover: `#FF7E10` (lighter)
- Pressed: `#E56300` (darker)

**Secondary Button (Test):**
- Background: `#2a2a2a` (gray)
- Hover: `#353535`

### Bottom Action Bar (60px)
```
┌──────────────────────────────────────────────────────┐
│                    [Test]     [Transcribe Timeline]  │
│                     ↑ Gray         ↑ ORANGE          │
└──────────────────────────────────────────────────────┘
```

## 🆚 Key Differences from Generic UI

| Aspect | Generic UI | Resolve-Inspired |
|--------|-----------|------------------|
| **Background** | `#121212` | `#1a1a1a` (Resolve exact) |
| **Accent** | Green `#4CAF50` | Orange `#FF6E00` (Resolve) |
| **Borders** | Thick 2px | Subtle 1px `#2a2a2a` |
| **Spacing** | Generous 20-30px | Compact 15px |
| **Headers** | Mixed case | UPPERCASE + letter-spacing |
| **Timecodes** | Regular font | Monospace (Consolas) |
| **Layout** | Cards with gaps | Panels with 1px separators |
| **Feeling** | Standalone app | **Native Resolve panel** |

## 🎬 Why This Works

### 1. Color Psychology
- **Orange** = Creative, energetic (video editing industry standard)
- **Dark theme** = Reduces eye strain during long sessions
- **High contrast** = Easy to read, professional

### 2. Visual Consistency
- User opens Resolve (sees orange selections)
- Opens our tool (sees same orange!)
- Brain: "This belongs here" ✓

### 3. Professional Polish
- Monospace timecodes (like Resolve timeline)
- Uppercase section headers (like Resolve inspector)
- 1px panel separators (like Resolve UI)
- Result: Looks official, not third-party

## 🚀 Testing

```bash
# Quick preview (no Resolve needed)
python test_resolve_ui.py

# With Resolve connection
python -m core.cli transcribe --show-ui

# From Resolve Scripts menu
# → Run test_exe_place_subtitle.py
# → See live updates in UI!
```

## ✨ The Result

A UI that:
- ✅ **Matches Resolve's aesthetic** perfectly
- ✅ **Shows live timeline data** every 500ms
- ✅ **Feels native** to DaVinci Resolve
- ✅ **Uses Resolve's colors** (orange accent!)
- ✅ **Follows Resolve's patterns** (panels, typography)
- ✅ **Looks professional** like official software

**It's not just a dark theme - it's a DaVinci Resolve theme!** 🎨🎬

