#!/usr/bin/env python3
"""Entry point for ramp test"""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.murnau.synth import test_ramp  # noqa: E402

if __name__ == "__main__":
    test_ramp()
