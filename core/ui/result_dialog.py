#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Result dialog for showing transcription results
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from pathlib import Path


class ResultDialog(QDialog):
    """Dialog showing transcription results."""
    
    def __init__(self, result: dict, success: bool = True):
        """
        Initialize the result dialog.
        
        Args:
            result: Dictionary with transcription results
            success: Whether transcription was successful
        """
        super().__init__()
        self.result = result
        self.success = success
        
        if success:
            self.setWindowTitle("✅ Transcription Complete")
        else:
            self.setWindowTitle("❌ Transcription Failed")
        
        self.resize(600, 480)
        self.setMinimumSize(520, 420)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        if self.success:
            self.create_success_ui(layout)
        else:
            self.create_error_ui(layout)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Done")
        close_btn.setFixedSize(100, 35)
        close_btn.setDefault(True)
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_success_ui(self, layout: QVBoxLayout):
        """Create UI for successful transcription."""
        # Success icon and title
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("✅")
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        title_layout.addWidget(icon_label)
        
        title = QLabel("Transcription Complete!")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #81c784;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Success message
        message = QLabel(
            "Successfully transcribed and imported subtitles into your timeline."
        )
        message.setWordWrap(True)
        message.setStyleSheet("font-size: 12px; color: #c0c0c0;")
        layout.addWidget(message)
        
        # Output file info
        srt_path = self.result.get('srt_path', '')
        if srt_path:
            file_group = QLabel(f"📝 <b>Output File:</b>")
            layout.addWidget(file_group)
            
            file_path_label = QLabel(srt_path)
            file_path_label.setWordWrap(True)
            file_path_label.setStyleSheet(
                """
                padding: 10px; background-color: #151515; border: 1px solid #2a2a2a; border-radius: 4px; font-family: monospace; font-size: 10px; color: #e0e0e0;
                """
            )
            layout.addWidget(file_path_label)
        
        # Statistics
        stats_label = QLabel("📊 <b>Statistics:</b>")
        layout.addWidget(stats_label)
        
        stats_text = self.format_statistics()
        stats_display = QLabel(stats_text)
        stats_display.setTextFormat(Qt.RichText)
        stats_display.setStyleSheet(
            """
            padding: 15px; background-color: #102a43; border-radius: 6px; font-size: 11px; color: #d0e4ff;
            """
        )
        layout.addWidget(stats_display)
        
        # Info tip
        tip = QLabel(
            "ℹ️ <i>The subtitle track has been automatically added to your timeline.</i>"
        )
        tip.setTextFormat(Qt.RichText)
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #90caf9; margin-top: 10px;")
        layout.addWidget(tip)
    
    def create_error_ui(self, layout: QVBoxLayout):
        """Create UI for failed transcription."""
        # Error icon and title
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("❌")
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        title_layout.addWidget(icon_label)
        
        title = QLabel("Transcription Failed")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ef9a9a;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Error message
        error_msg = self.result.get('error', 'Unknown error occurred')
        message = QLabel(
            f"An error occurred during transcription:\n\n<b>{error_msg}</b>"
        )
        message.setTextFormat(Qt.RichText)
        message.setWordWrap(True)
        message.setStyleSheet(
            """
            padding: 15px; background-color: #2a1212; border: 1px solid #5a1a1a; border-radius: 4px; color: #ff9e9e;
            """
        )
        layout.addWidget(message)
        
        # Common solutions
        solutions_label = QLabel("💡 <b>Common Solutions:</b>")
        layout.addWidget(solutions_label)
        
        solutions = """
        <ul style="line-height: 1.6;">
        <li>Ensure FFmpeg is installed and in your PATH</li>
        <li>Check that you have a stable internet connection (for model download)</li>
        <li>Try using a smaller model (tiny or base)</li>
        <li>Ensure the timeline contains valid video content</li>
        <li>Check available disk space (models require ~150MB-1.5GB)</li>
        </ul>
        """
        
        solutions_display = QLabel(solutions)
        solutions_display.setTextFormat(Qt.RichText)
        solutions_display.setWordWrap(True)
        solutions_display.setStyleSheet(
            """
            padding: 15px; background-color: #2a210f; border-radius: 6px; font-size: 11px; color: #ffdd9b;
            """
        )
        layout.addWidget(solutions_display)
        
        # Support link
        support = QLabel(
            'For more help, visit: <a href="https://github.com/your-repo/resolve-ai-helper">GitHub Issues</a>'
        )
        support.setTextFormat(Qt.RichText)
        support.setOpenExternalLinks(True)
        support.setStyleSheet("color: #bbbbbb; margin-top: 10px;")
        layout.addWidget(support)
    
    def format_statistics(self) -> str:
        """Format statistics for display."""
        duration = self.result.get('duration', 0)
        language = self.result.get('language', 'unknown')
        segments = self.result.get('segments_count', 0)
        words = self.result.get('words_count', 0)
        processing_time = self.result.get('processing_time', 0)
        
        # Format duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Format processing time
        proc_minutes = int(processing_time // 60)
        proc_seconds = int(processing_time % 60)
        proc_time_str = f"{proc_minutes}m {proc_seconds}s"
        
        stats_html = f"""
        <table cellpadding="5" style="width: 100%;">
        <tr><td><b>Duration:</b></td><td>{duration_str}</td></tr>
        <tr><td><b>Language:</b></td><td>{language.capitalize()}</td></tr>
        <tr><td><b>Segments:</b></td><td>{segments}</td></tr>
        <tr><td><b>Words:</b></td><td>{words:,}</td></tr>
        <tr><td><b>Processing Time:</b></td><td>{proc_time_str}</td></tr>
        </table>
        """
        
        return stats_html


def show_success_dialog(result: dict):
    """
    Show a success dialog with transcription results.
    
    Args:
        result: Dictionary with transcription results
    
    Returns:
        True if user clicked OK
    """
    dialog = ResultDialog(result, success=True)
    return dialog.exec() == QDialog.Accepted


def show_error_dialog(error: str):
    """
    Show an error dialog.
    
    Args:
        error: Error message to display
    
    Returns:
        True if user clicked OK
    """
    result = {"error": error}
    dialog = ResultDialog(result, success=False)
    return dialog.exec() == QDialog.Accepted

