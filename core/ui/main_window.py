#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main transcription settings window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QRadioButton, QPushButton,
    QGroupBox, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class TranscribeWindow(QMainWindow):
    """Main window for configuring transcription settings."""
    
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
        self.setWindowTitle("Resolve AI Helper - Transcribe Timeline")
        # Use a size that adapts better to DPI; allow the window to be resized
        self.resize(720, 760)
        self.setMinimumSize(640, 640)
        # Apply a unified dark theme with high contrast
        self.setStyleSheet(
            """
            QWidget { background-color: #121212; color: #f1f1f1; }
            QGroupBox { color: #f1f1f1; border: 1px solid #2a2a2a; }
            QLabel { color: #e0e0e0; }
            QComboBox, QLineEdit, QTextEdit { background-color: #1e1e1e; color: #f1f1f1; border: 1px solid #3a3a3a; }
            QRadioButton { color: #e0e0e0; }
            QPushButton { background-color: #2e7d32; color: #ffffff; border: none; border-radius: 4px; padding: 6px 10px; }
            QPushButton:hover { background-color: #2b7030; }
            QPushButton:disabled { background-color: #444; color: #aaa; }
            """
        )
        self.init_ui()

    def set_keep_open(self, keep: bool):
        self.keep_open = bool(keep)
    
    def init_ui(self):
        """Initialize the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🎬 Transcribe Timeline to Subtitles")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Timeline info section
        timeline_group = self.create_timeline_info_section()
        layout.addWidget(timeline_group)
        
        # Settings section
        settings_group = self.create_settings_section()
        layout.addWidget(settings_group)
        
        # Spacer
        layout.addStretch()
        
        # Warning label
        warning = QLabel("⚠️ First run will download model (~150MB for base model)")
        warning.setStyleSheet("""
            QLabel {
                color: #ff9800;
                padding: 10px;
                background-color: #fff3e0;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(warning)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        # Test placement button (for Resolve roundtrip testing)
        self.test_btn = QPushButton("Place Test Subtitle")
        self.test_btn.setFixedSize(160, 35)
        self.test_btn.clicked.connect(self.on_test_place)
        button_layout.addWidget(self.test_btn)

        self.transcribe_btn = QPushButton("Transcribe →")
        self.transcribe_btn.setFixedSize(120, 35)
        self.transcribe_btn.setDefault(True)
        self.transcribe_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.transcribe_btn.clicked.connect(self.on_transcribe)
        button_layout.addWidget(self.transcribe_btn)
        
        layout.addLayout(button_layout)
    
    def create_timeline_info_section(self) -> QGroupBox:
        """Create the timeline information section."""
        group = QGroupBox("📹 Timeline Information")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Format timeline info
        name = self.timeline_info.get('name', 'Unknown')
        duration = self.timeline_info.get('duration', '00:00:00')
        fps = self.timeline_info.get('fps', '24.00')
        
        info_text = f"""
<table cellpadding="5" style="font-family: monospace;">
<tr><td><b>Name:</b></td><td>{name}</td></tr>
<tr><td><b>Duration:</b></td><td>{duration}</td></tr>
<tr><td><b>FPS:</b></td><td>{fps}</td></tr>
</table>
        """
        
        label = QLabel(info_text)
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet("padding: 10px; background-color: #1b1b1b; border: 1px solid #2a2a2a; border-radius: 4px;")
        layout.addWidget(label)
        
        group.setLayout(layout)
        return group
    
    def create_settings_section(self) -> QGroupBox:
        """Create the transcription settings section."""
        group = QGroupBox("⚙️ Transcription Settings")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Model selection
        model_label = QLabel("Whisper Model:")
        model_label.setStyleSheet("font-weight: bold;")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "tiny - Fastest, less accurate (~75MB)",
            "base - Best balance ⭐ (~150MB)",
            "small - Better quality (~500MB)",
            "medium - Best quality, slower (~1.5GB)"
        ])
        self.model_combo.setCurrentIndex(1)  # Default to base
        self.model_combo.setStyleSheet("QComboBox { padding: 5px; border: 1px solid #3a3a3a; border-radius: 4px; background-color: #1e1e1e; color: #f1f1f1; }")
        
        model_hint = QLabel("ℹ️ Recommended: 'base' for most use cases")
        model_hint.setStyleSheet("color: #666; font-size: 11px; margin-left: 5px;")
        
        layout.addWidget(model_label)
        layout.addWidget(self.model_combo)
        layout.addWidget(model_hint)
        
        # Device selection
        device_label = QLabel("Processing Device:")
        device_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.device_auto = QRadioButton("Auto-detect (recommended)")
        self.device_cpu = QRadioButton("CPU only")
        self.device_gpu = QRadioButton("GPU (CUDA)")
        
        # Create button group for radio buttons
        self.device_group = QButtonGroup()
        self.device_group.addButton(self.device_auto, 0)
        self.device_group.addButton(self.device_cpu, 1)
        self.device_group.addButton(self.device_gpu, 2)
        self.device_auto.setChecked(True)
        
        device_hint = QLabel("ℹ️ GPU greatly speeds up transcription if available")
        device_hint.setStyleSheet("color: #666; font-size: 11px; margin-left: 5px;")
        
        layout.addWidget(device_label)
        layout.addWidget(self.device_auto)
        layout.addWidget(self.device_cpu)
        layout.addWidget(self.device_gpu)
        layout.addWidget(device_hint)
        
        # Language selection
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Auto-detect",
            "English",
            "Spanish",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Chinese",
            "Japanese",
            "Korean",
            "Russian",
            "Arabic"
        ])
        self.lang_combo.setStyleSheet("QComboBox { padding: 5px; border: 1px solid #3a3a3a; border-radius: 4px; background-color: #1e1e1e; color: #f1f1f1; }")
        
        lang_hint = QLabel("ℹ️ Auto-detect works well in most cases")
        lang_hint.setStyleSheet("color: #666; font-size: 11px; margin-left: 5px;")
        
        layout.addWidget(lang_label)
        layout.addWidget(self.lang_combo)
        layout.addWidget(lang_hint)
        
        group.setLayout(layout)
        return group
    
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
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Russian": "ru",
            "Arabic": "ar"
        }
        return lang_map.get(self.lang_combo.currentText(), None)
    
    def on_transcribe(self):
        """Handle transcribe button click."""
        # Extract model name from combo text
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
        # Notify listeners that window is closing so caller can emit cancel JSON
        try:
            self.window_closing.emit()
        except Exception:
            pass
        super().closeEvent(event)
    
    def show_error(self, title: str, message: str):
        """Show an error message box."""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Show an info message box."""
        QMessageBox.information(self, title, message)

