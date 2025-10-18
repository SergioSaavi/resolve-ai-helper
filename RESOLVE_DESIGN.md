# DaVinci Resolve-Inspired UI Design

## 🎨 Design Philosophy

Since Resolve AI Helper is a **companion tool** for DaVinci Resolve, the UI has been designed to **match Resolve's visual language** for a seamless, native-feeling experience.

## 📐 Design Analysis (From Resolve Screenshot)

### Color Palette
```css
Backgrounds:
- Main background: #1a1a1a (panels, main areas)
- Darker panels:   #0e0e0e (toolbar, action bar)
- Lighter panels:  #1e1e1e (content sections)

Borders & Separators:
- Subtle borders:  #2a2a2a
- Input borders:   #3a3a3a
- Focus borders:   #5a5a5a

Text:
- Primary text:    #d0d0d0 (main content)
- Secondary text:  #909090 (labels)
- Tertiary text:   #707070 (hints, headers)

Accents:
- Primary accent:  #FF6E00 (Resolve orange)
- Warning:         #FF9500 (amber/yellow)
- Success:         #67C23A (green, if needed)
```

### Typography
- **Font Family**: System fonts (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`)
- **Monospace**: `Consolas`, `Courier New` (for timecodes)
- **Sizes**: 
  - Headers: 10px (uppercase, bold, letter-spacing)
  - Body: 11-12px
  - Title: 13px (bold)

### Layout Structure
```
┌─────────────────────────────────────────────┐
│ Top Toolbar (#0e0e0e)                       │ 50px
│ • Title with orange accent                  │
│ • Version badge                             │
├─────────────────────────────────────────────┤
│ Scrollable Content Area (#1a1a1a)          │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Live Timeline Panel (#1e1e1e)           │ │
│ │ • Section header (uppercase)            │ │
│ │ • Key-value pairs                       │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Timeline Info Panel (#1e1e1e)           │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Settings Panel (#1e1e1e)                │ │
│ │ • Comboboxes (dark with orange focus)   │ │
│ │ • Radio buttons (orange when checked)   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
├─────────────────────────────────────────────┤
│ Bottom Action Bar (#0e0e0e)                │ 60px
│ • Test button (secondary, gray)             │
│ • Transcribe button (primary, ORANGE)      │
└─────────────────────────────────────────────┘
```

## 🎯 Key Design Elements

### 1. Top Toolbar
- **Dark background** (#0e0e0e) matching Resolve's top menu bar
- **Orange title** (#FF6E00) for brand consistency
- **Subtle border** at bottom for separation
- **Fixed height** (50px) for consistency

### 2. Content Panels
- **Uniform background** (#1e1e1e) for all sections
- **1px borders** (#2a2a2a) between panels
- **No spacing** between panels (like Resolve's inspector)
- **Section headers** in uppercase with letter-spacing

### 3. Form Controls

**ComboBoxes:**
- Dark background (#0e0e0e)
- Border that highlights orange on hover/focus
- Custom dropdown arrow
- Orange selection in dropdown list

**Radio Buttons:**
- Custom circular indicators
- Orange fill when selected
- Inner white dot for checked state

**Buttons:**
- **Secondary** (Test): Gray with subtle borders
- **Primary** (Transcribe): Resolve orange (#FF6E00)
- Hover states with slightly lighter colors
- 3px border radius (subtle, modern)

### 4. Live Context Display
- **Monospace font** for timecodes (like Resolve)
- **Label-value pairs** with aligned columns
- **Updates in real-time** (every 500ms from polling)
- Shows: Timeline name, FPS, timecode, in/out marks, selection

### 5. Typography Hierarchy
```
SECTION HEADERS     → 10px, uppercase, bold, #707070, letter-spacing: 1px
Labels              → 11px, regular, #909090
Values              → 11px, regular/mono, #d0d0d0
Buttons             → 12px, medium/bold, depends on type
Title               → 13px, bold, #FF6E00
```

## 🔄 Resolve Integration

### Matching UI Paradigms
1. **Inspector-style panels** (right-side panel feeling)
2. **Monospace timecodes** (exactly like timeline)
3. **Orange accents** for active/important elements
4. **Dark theme** optimized for long editing sessions
5. **Compact, efficient** use of space
6. **Professional** appearance

### Live Updates
The UI receives updates from the Resolve script every 500ms:
- Timeline name and FPS
- Current playhead position
- In/Out mark positions and duration
- Selected items in media pool

This creates a **native integration feeling** where the tool feels like part of Resolve itself.

## 📊 Component Styling Reference

### Panel Header Pattern
```python
header = QLabel("SECTION NAME")
header.setStyleSheet("""
    QLabel {
        color: #707070;
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
        background: transparent;
    }
""")
```

### Value Display Pattern
```python
value = QLabel("Value Text")
value.setStyleSheet("""
    QLabel {
        color: #d0d0d0;
        font-size: 11px;
        font-family: 'Consolas', 'Courier New', monospace;
        background: transparent;
    }
""")
```

### Primary Button Pattern (Orange)
```python
button.setStyleSheet("""
    QPushButton {
        background-color: #FF6E00;
        color: #ffffff;
        border: none;
        border-radius: 3px;
        padding: 0 20px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #FF7E10;
    }
    QPushButton:pressed {
        background-color: #E56300;
    }
""")
```

## 🎨 Comparison: Before vs After

### Before (Generic Dark Theme)
- Generic dark colors
- Green accent (not Resolve-like)
- Rounded corners everywhere
- Lots of padding and spacing
- Card-based layout
- Standalone app feeling

### After (Resolve-Inspired)
- Exact Resolve colors (#1a1a1a, #0e0e0e, #1e1e1e)
- Orange accent (#FF6E00) matching Resolve
- Subtle 3px corners (Resolve style)
- Compact, efficient spacing
- Panel-based layout with 1px separators
- **Feels like a Resolve extension**

## 🚀 Benefits

### For Users
✅ **Familiar interface** - Matches Resolve's look and feel
✅ **Less cognitive load** - Same visual language
✅ **Professional appearance** - Looks like official software
✅ **Optimized colors** - Dark theme for video editing
✅ **Live feedback** - See timeline updates in real-time

### For Brand
✅ **Clear companion tool** - Obviously built for Resolve
✅ **High quality** - Professional design standards
✅ **Native feeling** - Feels integrated, not bolted-on
✅ **Attention to detail** - Matches Resolve's UI paradigms

## 🧪 Testing the Design

```bash
# Quick preview
python test_resolve_ui.py

# With real Resolve connection
python -m core.cli transcribe --show-ui --timeline-name "Test"

# Interactive mode (live updates)
python -m core.cli transcribe --show-ui --interactive
```

## 📝 Design Notes

1. **Orange is the new green** - Switched from generic green to Resolve's signature orange
2. **Monospace matters** - Timecodes use Consolas/Courier for authenticity
3. **Spacing is tight** - Resolve uses compact layouts, so we do too
4. **Borders are subtle** - 1px #2a2a2a for barely-there separators
5. **Headers are CAPS** - Section headers use uppercase with letter-spacing
6. **Hierarchy is clear** - Visual weight guides the eye naturally

## 🎯 Future Enhancements

Potential additions that maintain the Resolve aesthetic:
- Timeline-style progress bar for transcription
- Color page-inspired status indicators
- Media pool-style model list
- Deliver page-inspired output settings
- Tabs for multiple features (like Resolve's pages)

---

**Result:** A UI that **feels at home** in DaVinci Resolve! 🎬

