"""Synthesizer control and utility modules"""

from .melody import init_synth, midi_to_freq, play_note
from .ramp_test import test_ramp

__all__ = ["midi_to_freq", "play_note", "init_synth", "test_ramp"]
