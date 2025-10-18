#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main transcription settings window - DaVinci Resolve inspired design
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QRadioButton, QPushButton,
    QGroupBox, QButtonGroup, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class TranscribeWindow(QMainWindow):
    """Main window for configuring transcription settings - Resolve-inspired design."""
    
    # Signal emitted when user clicks Transcribe
    transcribe_requested = Signal(dict)  # Emits settings dict
    # Signal emitted when user clicks test placement
    test_place_requested = Signal()
    # Signal emitted when window is closing (for streaming/cancel semantics)
    window_closing = Signal()
    
    def __init__(self, timeline_info: dict):
        """
        Initialize the main window.
        
        Args:
            timeline_info: Dictionary with 'name', 'duration', 'fps'
        """
        super().__init__()
        self.timeline_info = timeline_info
        self.keep_open = False
        self.setWindowTitle("AI Transcription - Resolve Helper")
        self.resize(800, 720)
        self.setMinimumSize(750, 650)
        
        # Apply DaVinci Resolve color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #1a1a1a; 
                color: #d0d0d0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QLabel { 
                color: #d0d0d0; 
            }
        """)
        
        self.init_ui()

    def set_keep_open(self, keep: bool):
        self.keep_open = bool(keep)
    
    def init_ui(self):
        """Initialize the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top toolbar (Resolve-style)
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #1a1a1a; border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(1)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Live timeline context
        context_panel = self.create_timeline_context()
        content_layout.addWidget(context_panel)
        
        # Timeline info section
        timeline_panel = self.create_timeline_info_section()
        content_layout.addWidget(timeline_panel)
        
        # Settings section
        settings_panel = self.create_settings_section()
        content_layout.addWidget(settings_panel)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Bottom action bar (Resolve-style)
        action_bar = self.create_action_bar()
        layout.addWidget(action_bar)
    
    def create_toolbar(self) -> QWidget:
        """Create top toolbar similar to Resolve."""
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #0e0e0e;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Title with icon
        title = QLabel("🎬 AI Transcription")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #FF6E00; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Version badge
        version = QLabel("v0.1.0")
        version.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 10px;
                background: transparent;
                border: none;
                padding: 4px 8px;
            }
        """)
        layout.addWidget(version)
        
        return toolbar
    
    def create_timeline_context(self) -> QWidget:
        """Create live timeline context panel."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2a2a2a;
                padding: 0px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("LIVE TIMELINE")
        header.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        layout.addWidget(header)
        
        # Context info grid
        grid = QWidget()
        grid_layout = QVBoxLayout(grid)
        grid_layout.setSpacing(6)
        grid_layout.setContentsMargins(0, 5, 0, 0)
        
        self.ctx_name = self.create_context_row("Timeline:", "—")
        self.ctx_fps = self.create_context_row("FPS:", "—")
        self.ctx_tc = self.create_context_row("Timecode:", "—")
        self.ctx_range = self.create_context_row("In/Out:", "—")
        self.ctx_sel = self.create_context_row("Selection:", "—")
        
        for row in [self.ctx_name, self.ctx_fps, self.ctx_tc, self.ctx_range, self.ctx_sel]:
            grid_layout.addWidget(row)
        
        layout.addWidget(grid)
        
        return panel
    
    def create_context_row(self, label: str, value: str) -> QWidget:
        """Create a context info row."""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        
        label_widget = QLabel(label)
        label_widget.setFixedWidth(90)
        label_widget.setStyleSheet("""
            QLabel {
                color: #909090;
                font-size: 11px;
                background: transparent;
            }
        """)
        
        value_widget = QLabel(value)
        value_widget.setObjectName("value")
        value_widget.setStyleSheet("""
            QLabel {
                color: #d0d0d0;
                font-size: 11px;
                font-family: 'Consolas', 'Courier New', monospace;
                background: transparent;
            }
        """)
        
        row_layout.addWidget(label_widget)
        row_layout.addWidget(value_widget)
        row_layout.addStretch()
        
        # Store value widget for updates
        row.value_label = value_widget
        
        return row
    
    def create_timeline_info_section(self) -> QWidget:
        """Create the timeline information section."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("TIMELINE INFORMATION")
        header.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        layout.addWidget(header)
        
        # Info grid
        info_grid = QWidget()
        info_grid.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_grid)
        info_layout.setSpacing(6)
        info_layout.setContentsMargins(0, 5, 0, 0)
        
        name = self.timeline_info.get('name', 'Unknown')
        duration = self.timeline_info.get('duration', '00:00:00')
        fps = self.timeline_info.get('fps', '24.00')
        
        name_row = self.create_context_row("Name:", name)
        dur_row = self.create_context_row("Duration:", duration)
        fps_row = self.create_context_row("Frame Rate:", fps)
        
        for row in [name_row, dur_row, fps_row]:
            info_layout.addWidget(row)
        
        layout.addWidget(info_grid)
        
        return panel
    
    def create_settings_section(self) -> QWidget:
        """Create the transcription settings section."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("TRANSCRIPTION SETTINGS")
        header.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        layout.addWidget(header)
        
        # Model selection
        model_label = QLabel("Whisper Model")
        model_label.setStyleSheet("color: #d0d0d0; font-size: 11px; margin-top: 5px; background: transparent;")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "tiny - Fastest (~75MB)",
            "base - Recommended (~150MB)",
            "small - Better Quality (~500MB)",
            "medium - Best Quality (~1.5GB)"
        ])
        self.model_combo.setCurrentIndex(1)
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #0e0e0e;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 6px 10px;
                color: #d0d0d0;
                font-size: 11px;
                min-height: 24px;
            }
            QComboBox:hover {
                border: 1px solid #FF6E00;
            }
            QComboBox:focus {
                border: 1px solid #FF6E00;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #909090;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e;
                border: 1px solid #3a3a3a;
                selection-background-color: #FF6E00;
                selection-color: #ffffff;
                color: #d0d0d0;
                outline: none;
            }
        """)
        
        layout.addWidget(model_label)
        layout.addWidget(self.model_combo)
        
        # Device selection
        device_label = QLabel("Processing Device")
        device_label.setStyleSheet("color: #d0d0d0; font-size: 11px; margin-top: 10px; background: transparent;")
        
        device_container = QWidget()
        device_container.setStyleSheet("background: transparent;")
        device_layout = QVBoxLayout(device_container)
        device_layout.setSpacing(8)
        device_layout.setContentsMargins(0, 5, 0, 0)
        
        self.device_auto = QRadioButton("Auto-detect (Recommended)")
        self.device_cpu = QRadioButton("CPU Only")
        self.device_gpu = QRadioButton("GPU (CUDA)")
        
        radio_style = """
            QRadioButton {
                color: #d0d0d0;
                font-size: 11px;
                spacing: 8px;
                background: transparent;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                border: 1px solid #5a5a5a;
                background: #0e0e0e;
            }
            QRadioButton::indicator:hover {
                border: 1px solid #FF6E00;
            }
            QRadioButton::indicator:checked {
                border: 1px solid #FF6E00;
                background: #FF6E00;
            }
            QRadioButton::indicator:checked:after {
                content: '';
                width: 6px;
                height: 6px;
                border-radius: 3px;
                background: white;
                position: absolute;
                top: 4px;
                left: 4px;
            }
        """
        
        for radio in [self.device_auto, self.device_cpu, self.device_gpu]:
            radio.setStyleSheet(radio_style)
            device_layout.addWidget(radio)
        
        self.device_group = QButtonGroup()
        self.device_group.addButton(self.device_auto, 0)
        self.device_group.addButton(self.device_cpu, 1)
        self.device_group.addButton(self.device_gpu, 2)
        self.device_auto.setChecked(True)
        
        layout.addWidget(device_label)
        layout.addWidget(device_container)
        
        # Language selection
        lang_label = QLabel("Language")
        lang_label.setStyleSheet("color: #d0d0d0; font-size: 11px; margin-top: 10px; background: transparent;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Auto-detect",
            "English", "Spanish", "French", "German", "Italian",
            "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic"
        ])
        self.lang_combo.setStyleSheet(self.model_combo.styleSheet())
        
        layout.addWidget(lang_label)
        layout.addWidget(self.lang_combo)
        
        # Warning message
        warning = QLabel("⚠ First run will download the selected model")
        warning.setStyleSheet("""
            QLabel {
                color: #FF9500;
                font-size: 10px;
                padding: 8px;
                background-color: rgba(255, 149, 0, 0.1);
                border: 1px solid rgba(255, 149, 0, 0.2);
                border-radius: 3px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(warning)
        
        return panel
    
    def create_action_bar(self) -> QWidget:
        """Create bottom action bar with buttons."""
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet("""
            QFrame {
                background-color: #0e0e0e;
                border-top: 1px solid #2a2a2a;
            }
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        layout.addStretch()
        
        # Test button (secondary)
        self.test_btn = QPushButton("Test Subtitle")
        self.test_btn.setFixedHeight(36)
        self.test_btn.setMinimumWidth(120)
        self.test_btn.clicked.connect(self.on_test_place)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #d0d0d0;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #353535;
                border: 1px solid #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
        """)
        layout.addWidget(self.test_btn)
        
        # Transcribe button (primary, Resolve orange)
        self.transcribe_btn = QPushButton("Transcribe Timeline")
        self.transcribe_btn.setFixedHeight(36)
        self.transcribe_btn.setMinimumWidth(160)
        self.transcribe_btn.setDefault(True)
        self.transcribe_btn.clicked.connect(self.on_transcribe)
        self.transcribe_btn.setStyleSheet("""
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
        layout.addWidget(self.transcribe_btn)
        
        return bar
    
    def get_device_selection(self) -> str:
        """Get the selected device."""
        if self.device_auto.isChecked():
            return "auto"
        elif self.device_cpu.isChecked():
            return "cpu"
        else:
            return "cuda"
    
    def get_language_code(self) -> str:
        """Get the selected language code."""
        lang_map = {
            "Auto-detect": None,
            "English": "en", "Spanish": "es", "French": "fr",
            "German": "de", "Italian": "it", "Portuguese": "pt",
            "Chinese": "zh", "Japanese": "ja", "Korean": "ko",
            "Russian": "ru", "Arabic": "ar"
        }
        return lang_map.get(self.lang_combo.currentText(), None)
    
    def on_transcribe(self):
        """Handle transcribe button click."""
        model_text = self.model_combo.currentText()
        model_name = model_text.split(" - ")[0].strip()
        
        settings = {
            "model": model_name,
            "device": self.get_device_selection(),
            "language": self.get_language_code(),
            "timeline_name": self.timeline_info.get('name', 'Unknown')
        }
        
        self.transcribe_requested.emit(settings)
        if not self.keep_open:
            self.close()

    def on_test_place(self):
        """Handle test placement button click."""
        self.test_place_requested.emit()
        if not self.keep_open:
            self.close()

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.window_closing.emit()
        except Exception:
            pass
        super().closeEvent(event)

    # --- Live context updates from supervisor events ---
    def update_timeline_context(self, timeline: dict):
        """Update live timeline context."""
        name = timeline.get('name') or '—'
        fps = timeline.get('fps') or '—'
        tc = timeline.get('tc') or '—'
        in_tc = timeline.get('in_tc')
        out_tc = timeline.get('out_tc')
        range_seconds = timeline.get('range_seconds')
        
        self.ctx_name.value_label.setText(name)
        self.ctx_fps.value_label.setText(fps)
        self.ctx_tc.value_label.setText(tc)
        
        if in_tc and out_tc:
            dur = f" ({range_seconds:.2f}s)" if isinstance(range_seconds, (int, float)) else ""
            self.ctx_range.value_label.setText(f"{in_tc} → {out_tc}{dur}")
        else:
            self.ctx_range.value_label.setText("—")

    def update_selection(self, items: list):
        """Update selection info."""
        if not items:
            self.ctx_sel.value_label.setText("—")
            return
        names = [i.get('name') or i.get('type') or 'Item' for i in items][:2]
        more = '' if len(items) <= 2 else f" +{len(items)-2}"
        self.ctx_sel.value_label.setText(f"{', '.join(names)}{more}")
    
    def show_error(self, title: str, message: str):
        """Show an error message box."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Show an info message box."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)
