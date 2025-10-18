#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Progress window for showing transcription progress
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, timedelta


class ProgressWindow(QDialog):
    """Dialog showing transcription progress with live updates."""
    
    # Signal emitted when user clicks Cancel
    cancel_requested = Signal()
    
    def __init__(self, timeline_name: str):
        """
        Initialize the progress window.
        
        Args:
            timeline_name: Name of the timeline being transcribed
        """
        super().__init__()
        self.timeline_name = timeline_name
        self.start_time = datetime.now()
        self.setWindowTitle("Transcribing...")
        self.resize(720, 480)
        self.setMinimumSize(640, 420)
        self.setModal(True)
        
        # Prevent closing with X button
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint
        )
        
        self.init_ui()
        
        # Timer for elapsed time update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel(f"⏳ Transcribing: {self.timeline_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar { border: 1px solid #2a2a2a; border-radius: 5px; text-align: center; height: 25px; background-color: #1b1b1b; color: #e0e0e0; }
            QProgressBar::chunk { background-color: #2e7d32; border-radius: 3px; }
            """
        )
        layout.addWidget(self.progress_bar)
        
        # Current status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Time info
        time_layout = QHBoxLayout()
        
        self.elapsed_label = QLabel("Time Elapsed: 00:00:00")
        self.elapsed_label.setStyleSheet("color: #b0b0b0;")
        time_layout.addWidget(self.elapsed_label)
        
        time_layout.addStretch()
        
        self.remaining_label = QLabel("Estimated: Calculating...")
        self.remaining_label.setStyleSheet("color: #b0b0b0;")
        time_layout.addWidget(self.remaining_label)
        
        layout.addLayout(time_layout)
        
        # Log area
        log_label = QLabel("Progress Log:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit { background-color: #151515; border: 1px solid #2a2a2a; border-radius: 4px; padding: 5px; font-family: 'Consolas', 'Monaco', monospace; font-size: 10px; color: #e0e0e0; }
            """
        )
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # Stats area
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(
            """
            padding: 10px; background-color: #102a43; border-radius: 4px; font-size: 11px; color: #d0e4ff;
            """
        )
        layout.addWidget(self.stats_label)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(100, 32)
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.cancel_btn.setStyleSheet(
            """
            QPushButton { background-color: #c62828; color: white; font-weight: bold; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #b71c1c; }
            """
        )
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def update_progress(self, message: str, progress: float = None):
        """
        Update the progress display.
        
        Args:
            message: Status message to display
            progress: Progress value from 0.0 to 1.0, or None
        """
        # Update status label
        self.status_label.setText(message)
        
        # Update progress bar
        if progress is not None:
            percentage = int(progress * 100)
            self.progress_bar.setValue(percentage)
            
            # Estimate remaining time
            if progress > 0.05:  # Only estimate after 5% progress
                elapsed = (datetime.now() - self.start_time).total_seconds()
                total_estimated = elapsed / progress
                remaining = total_estimated - elapsed
                
                if remaining > 0:
                    remaining_str = str(timedelta(seconds=int(remaining)))
                    self.remaining_label.setText(f"Estimated: {remaining_str}")
        
        # Add to log
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_stats(self, segments: int = 0, words: int = 0, language: str = ""):
        """
        Update the statistics display.
        
        Args:
            segments: Number of segments processed
            words: Number of words detected
            language: Detected language
        """
        stats_parts = []
        
        if segments > 0:
            stats_parts.append(f"📝 Segments: {segments}")
        
        if words > 0:
            stats_parts.append(f"💬 Words: {words:,}")
        
        if language:
            stats_parts.append(f"🌍 Language: {language}")
        
        if stats_parts:
            self.stats_label.setText(" • ".join(stats_parts))
    
    def update_elapsed_time(self):
        """Update the elapsed time display."""
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed.total_seconds())))
        self.elapsed_label.setText(f"Time Elapsed: {elapsed_str}")
    
    def on_cancel(self):
        """Handle cancel button click."""
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelling...")
        self.update_progress("⚠️ Cancellation requested...", None)
        self.cancel_requested.emit()
    
    def mark_complete(self):
        """Mark transcription as complete."""
        self.timer.stop()
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Transcription Complete!")
        self.cancel_btn.setText("Close")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setStyleSheet("""
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
        """)
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.accept)
    
    def mark_error(self, error_message: str):
        """Mark transcription as failed."""
        self.timer.stop()
        self.status_label.setText(f"❌ Error: {error_message}")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #f44336;")
        self.cancel_btn.setText("Close")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.reject)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Only allow closing if transcription is complete or failed
        if self.cancel_btn.text() in ["Close"]:
            event.accept()
        else:
            event.ignore()

