#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Model Manager for downloading and caching Whisper models
"""

import sys
from pathlib import Path
from typing import Optional, Callable
from faster_whisper import WhisperModel
from .utils import get_models_dir


class ModelManager:
    """Manages Whisper model downloads and caching."""
    
    AVAILABLE_MODELS = {
        "tiny": {"size": "~75MB", "speed": "fastest", "accuracy": "low"},
        "base": {"size": "~150MB", "speed": "fast", "accuracy": "good"},
        "small": {"size": "~500MB", "speed": "moderate", "accuracy": "better"},
        "medium": {"size": "~1.5GB", "speed": "slow", "accuracy": "best"},
    }
    
    def __init__(self):
        self.models_dir = get_models_dir()
    
    def is_model_cached(self, model_name: str) -> bool:
        """Check if a model is already downloaded and cached."""
        if model_name not in self.AVAILABLE_MODELS:
            return False
        
        # faster-whisper caches models in a standard location
        # We'll let it handle caching, just check if we can load it
        return True  # Let faster-whisper handle detection
    
    def get_model_info(self, model_name: str) -> dict:
        """Get information about a model."""
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available: {', '.join(self.AVAILABLE_MODELS.keys())}"
            )
        return self.AVAILABLE_MODELS[model_name]
    
    def load_model(
        self,
        model_name: str,
        device: str = "auto",
        compute_type: str = "default",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> WhisperModel:
        """
        Load a Whisper model, downloading if necessary.
        
        Args:
            model_name: Name of the model (tiny, base, small, medium)
            device: Device to use ("cpu", "cuda", or "auto")
            compute_type: Computation type ("int8", "float16", "float32", or "default")
            progress_callback: Optional callback for progress updates
        
        Returns:
            WhisperModel instance
        
        Raises:
            ValueError: If model_name is invalid
            RuntimeError: If model loading fails
        """
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available: {', '.join(self.AVAILABLE_MODELS.keys())}"
            )
        
        # Auto-detect device if needed
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                if progress_callback:
                    progress_callback(f"Auto-detected device: {device.upper()}")
            except ImportError:
                device = "cpu"
                if progress_callback:
                    progress_callback("PyTorch not available, using CPU")
        
        # Auto-select compute type based on device
        if compute_type == "default":
            if device == "cuda":
                compute_type = "float16"
            else:
                compute_type = "int8"
        
        if progress_callback:
            model_info = self.get_model_info(model_name)
            progress_callback(
                f"Loading {model_name} model ({model_info['size']})..."
            )
            progress_callback("This may take a moment on first run (downloading model)")
        
        try:
            model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
                download_root=str(self.models_dir)
            )
            
            if progress_callback:
                progress_callback(f"✓ Model loaded successfully on {device.upper()}")
            
            return model
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            if progress_callback:
                progress_callback(f"✗ {error_msg}")
            raise RuntimeError(error_msg)
    
    def list_available_models(self) -> dict:
        """List all available models with their information."""
        return self.AVAILABLE_MODELS.copy()
    
    def estimate_processing_time(
        self,
        duration_seconds: float,
        model_name: str,
        device: str = "cpu"
    ) -> float:
        """
        Estimate processing time for a given video duration.
        
        Args:
            duration_seconds: Duration of video in seconds
            model_name: Model to use
            device: Device type ("cpu" or "cuda")
        
        Returns:
            Estimated processing time in seconds
        """
        # Rough estimates based on typical performance
        # These are conservative estimates
        speed_factors = {
            "tiny": {"cpu": 0.5, "cuda": 0.1},
            "base": {"cpu": 1.0, "cuda": 0.2},
            "small": {"cpu": 2.0, "cuda": 0.4},
            "medium": {"cpu": 4.0, "cuda": 0.8},
        }
        
        if model_name not in speed_factors:
            model_name = "base"
        
        device = device.lower()
        if device not in ["cpu", "cuda"]:
            device = "cpu"
        
        factor = speed_factors[model_name][device]
        return duration_seconds * factor
    
    def get_recommended_model(self, duration_minutes: float, has_gpu: bool = False) -> str:
        """
        Recommend a model based on video duration and hardware.
        
        Args:
            duration_minutes: Video duration in minutes
            has_gpu: Whether GPU is available
        
        Returns:
            Recommended model name
        """
        if duration_minutes < 5:
            # Short videos: use better quality
            return "small" if has_gpu else "base"
        elif duration_minutes < 30:
            # Medium videos: balance speed and quality
            return "base"
        else:
            # Long videos: prioritize speed
            return "tiny" if not has_gpu else "base"


def print_model_info():
    """Print information about available models."""
    manager = ModelManager()
    print("Available Whisper Models:")
    print("-" * 60)
    
    for name, info in manager.list_available_models().items():
        print(f"\n{name.upper()}")
        print(f"  Size:     {info['size']}")
        print(f"  Speed:    {info['speed']}")
        print(f"  Accuracy: {info['accuracy']}")
    
    print("\n" + "-" * 60)
    print("Recommended: 'base' for most use cases")


if __name__ == "__main__":
    # Test/demo the model manager
    print_model_info()

