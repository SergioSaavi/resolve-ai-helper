"""
Resolve AI Helper - Core Module

Provides AI-powered transcription capabilities for DaVinci Resolve free version.
"""

__version__ = "0.1.0"
__author__ = "Resolve AI Helper Contributors"

from .transcribe import transcribe_video
from .model_manager import ModelManager

__all__ = ["transcribe_video", "ModelManager", "__version__"]

