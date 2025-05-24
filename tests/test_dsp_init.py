#!/usr/bin/env python3

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.murnau.dsp import get_dsp_path


class TestDSPInit:
    """Test DSP module initialization functions"""

    @patch("src.murnau.dsp.os.path.join")
    @patch("src.murnau.dsp.os.path.dirname")
    def test_get_dsp_path_valid_file(self, mock_dirname, mock_join):
        """Test getting DSP path for valid file"""
        mock_dirname.return_value = "/fake/dsp/dir"
        mock_join.return_value = "/fake/dsp/dir/test.dsp"

        result = get_dsp_path("test.dsp")

        mock_dirname.assert_called_once()
        mock_join.assert_called_once_with("/fake/dsp/dir", "test.dsp")
        assert result == "/fake/dsp/dir/test.dsp"

    @patch("src.murnau.dsp.os.path.join")
    @patch("src.murnau.dsp.os.path.dirname")
    def test_get_dsp_path_legato_synth(self, mock_dirname, mock_join):
        """Test getting DSP path for legato_synth.dsp"""
        mock_dirname.return_value = "/fake/dsp/dir"
        mock_join.return_value = "/fake/dsp/dir/legato_synth.dsp"

        result = get_dsp_path("legato_synth.dsp")

        assert result == "/fake/dsp/dir/legato_synth.dsp"

    def test_get_dsp_path_none_input(self):
        """Test get_dsp_path with None input"""
        with pytest.raises(TypeError):
            get_dsp_path(None)

    def test_get_dsp_path_empty_string(self):
        """Test get_dsp_path with empty string"""
        result = get_dsp_path("")
        # Should return a valid path even with empty string
        assert isinstance(result, str)