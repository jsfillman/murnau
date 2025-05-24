#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUtilsInit:
    """Test utils module initialization"""

    def test_utils_module_imports(self):
        """Test that utils module can be imported"""
        from src.murnau import utils

        # Check that the module is accessible
        assert utils is not None

    def test_osc_client_import(self):
        """Test that OSCClient can be imported from utils"""
        from src.murnau.utils import OSCClient

        # Check that OSCClient is available
        assert OSCClient is not None
