#!/usr/bin/env python3
"""Basic import tests that don't require PyQt6"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicImports:
    """Test basic module imports without GUI dependencies"""

    def test_murnau_package_import(self):
        """Test that the main murnau package can be imported"""
        import src.murnau

        assert hasattr(src.murnau, "__version__")

    def test_dsp_module_import(self):
        """Test that DSP module can be imported"""
        from src.murnau.dsp import get_dsp_path, DSP_FILES

        assert callable(get_dsp_path)
        assert isinstance(DSP_FILES, dict)
        assert "legato_synth" in DSP_FILES

    def test_synth_modules_import(self):
        """Test that synth modules can be imported"""
        from src.murnau.synth import melody, ramp_test

        assert hasattr(melody, "midi_to_freq")
        assert hasattr(melody, "play_note")
        assert hasattr(ramp_test, "test_ramp")

    def test_utils_import(self):
        """Test that utils modules can be imported"""
        from src.murnau.utils.osc_client import OSCClient

        assert OSCClient is not None

    def test_ui_modules_import_gracefully(self):
        """Test that UI modules can be imported or fail gracefully"""
        try:
            from src.murnau.ui import main_window, widgets

            # If import succeeds, check basic attributes
            assert hasattr(main_window, "MurnauUI")
            assert hasattr(widgets, "LabeledKnob")
        except ImportError as e:
            # This is expected in headless environments
            assert "PyQt6" in str(e) or "display" in str(e).lower()

    def test_package_structure(self):
        """Test that package structure is correct"""
        import src.murnau
        import src.murnau.dsp
        import src.murnau.synth
        import src.murnau.utils

        # These should all be importable
        assert src.murnau is not None
        assert src.murnau.dsp is not None
        assert src.murnau.synth is not None
        assert src.murnau.utils is not None
