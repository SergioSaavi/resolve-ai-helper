#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to preview the DaVinci Resolve-inspired UI
Run: python test_resolve_ui.py
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from core.ui import TranscribeWindow

def main():
    """Launch the Resolve-inspired UI for testing."""
    app = QApplication(sys.argv)
    
    # Sample timeline info
    timeline_info = {
        "name": "viktor-shitshow-16-10-25.mp4",
        "duration": "01:25:41:15",
        "fps": "24.00"
    }
    
    # Create and show window
    window = TranscribeWindow(timeline_info)
    window.show()
    
    # Simulate live timeline updates
    def update_timeline():
        """Simulate live updates from Resolve."""
        import random
        timeline_data = {
            "name": "viktor-shitshow-16-10-25.mp4",
            "fps": "24.00",
            "tc": f"01:25:{random.randint(10,59):02d}:15",
            "in_tc": "01:13:52:00",
            "out_tc": "01:27:44:00",
            "range_seconds": 832.0
        }
        window.update_timeline_context(timeline_data)
    
    def update_selection():
        """Simulate media selection."""
        items = [
            {"name": "ST1 Subtitle 204 Clips", "type": "subtitle"}
        ]
        window.update_selection(items)
    
    # Run simulations
    QTimer.singleShot(500, update_timeline)
    QTimer.singleShot(800, update_selection)
    
    # Keep updating timeline
    timer = QTimer()
    timer.timeout.connect(update_timeline)
    timer.start(2000)  # Update every 2 seconds
    
    print("=" * 70)
    print(" DaVinci Resolve-Inspired UI Preview")
    print("=" * 70)
    print()
    print(" 🎨 Design Features:")
    print("   • Dark theme matching DaVinci Resolve (#1a1a1a, #0e0e0e)")
    print("   • Orange accent color (#FF6E00) like Resolve selections")
    print("   • Top toolbar with title and version")
    print("   • Live timeline context panel (updates every 2s)")
    print("   • Timeline information section")
    print("   • Clean settings with Resolve-style controls")
    print("   • Bottom action bar with prominent Transcribe button")
    print()
    print(" 🔴 LIVE: Timeline updates are simulating real Resolve polling")
    print()
    print("=" * 70)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

