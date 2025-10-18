#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test to show the UI we built
"""

import sys
from PySide6.QtWidgets import QApplication
from core.ui import TranscribeWindow

def main():
    print("Opening Resolve AI Helper UI...")
    
    app = QApplication(sys.argv)
    
    # Mock timeline info
    timeline_info = {
        "name": "My Timeline",
        "duration": "00:05:30",
        "fps": "24.00"
    }
    
    # Create and show the main transcription window
    window = TranscribeWindow(timeline_info)
    window.show()  # show immediately to measure startup feel
    
    # Connect the signal to see what settings user chooses
    def on_transcribe(settings):
        print("\nUser clicked Transcribe with settings:")
        print(f"  Model: {settings['model']}")
        print(f"  Device: {settings['device']}")
        print(f"  Language: {settings['language']}")
        print(f"  Input: {settings.get('input_file', 'N/A')}")
        app.quit()
    
    window.transcribe_requested.connect(on_transcribe)
    
    window.show()
    
    print("UI window opened! Try selecting settings and clicking Transcribe.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

