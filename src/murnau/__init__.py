"""Murnau - Cinematic Synthesizer Control Interface

A stylish PyQt6 UI for controlling legato_synth via OSC
Inspired by German Expressionist cinema aesthetics
"""

__version__ = "0.1.0"
__author__ = "Murnau Development Team"
__license__ = "MIT"

from .synth.melody import play_melody
from .synth.ramp_test import test_ramp
from .ui.main_window import MurnauUI

__all__ = ["MurnauUI", "play_melody", "test_ramp"]
