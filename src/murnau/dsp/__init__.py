"""Faust DSP files for Murnau synthesizer

This module contains the Digital Signal Processing definitions
written in Faust language that implement the synthesizer engine.
"""

# DSP files are not Python modules, but we include this __init__.py
# to make the directory a proper Python package and to document
# the DSP resources available here.

DSP_FILES = {"legato_synth": "legato_synth.dsp", "oscillator": "oscilator.faust"}


def get_dsp_path(name):
    """Get the full path to a DSP file

    Args:
        name: Name of the DSP file (without extension)

    Returns:
        Path to the DSP file
    """
    import os

    if name is None:
        raise TypeError("DSP file name cannot be None")

    if name in DSP_FILES:
        return os.path.join(os.path.dirname(__file__), DSP_FILES[name])
    else:
        raise ValueError(f"Unknown DSP file: {name}")
