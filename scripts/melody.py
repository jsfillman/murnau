#!/usr/bin/env python3
"""Entry point for melody player"""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.murnau.synth import play_melody  # noqa: E402

if __name__ == "__main__":
    play_melody()
