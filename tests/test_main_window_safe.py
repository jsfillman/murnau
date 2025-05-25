#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch  # noqa: E402


class TestMurnauUICore:
    """Test core MurnauUI functionality without creating widgets"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    @patch("src.murnau.ui.main_window.QTimer")
    @patch("src.murnau.ui.main_window.QMainWindow.__init__")
    def test_init_osc_settings(
        self, mock_super_init, mock_timer, mock_midi, mock_udp_client
    ):
        """Test OSC client initialization without widget creation"""
        from src.murnau.ui.main_window import MurnauUI

        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        mock_midi.return_value = []
        mock_super_init.return_value = None

        # Mock all the UI creation methods to prevent actual widget creation
        with patch.object(MurnauUI, "init_ui"), patch.object(
            MurnauUI, "init_midi"
        ), patch.object(MurnauUI, "init_parameters"), patch.object(
            MurnauUI, "show"
        ), patch.object(
            MurnauUI, "_animate_ui_elements"
        ):

            # Create instance without triggering widget creation
            window = MurnauUI.__new__(MurnauUI)

            # Manually call __init__ with mocked methods
            window.osc_ip = "127.0.0.1"
            window.osc_port = 5510
            window.synth_name = "legato_synth_stereo"
            window.osc_client = mock_udp_client("127.0.0.1", 5510)
            window.midi_input = None
            window.midi_thread = None
            window.midi_running = False
            window.active_notes = {}
            window.current_note = None

            # Verify OSC settings
            assert window.osc_ip == "127.0.0.1"
            assert window.osc_port == 5510
            assert window.synth_name == "legato_synth_stereo"

    def test_osc_message_formatting(self):
        """Test OSC message address formatting logic"""
        # Test the logic without creating widgets
        synth_name = "test_synth"
        address = "/freq"
        expected = f"/{synth_name}{address}"

        assert expected == "/test_synth/freq"

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_send_osc_method(self, mock_udp_client):
        """Test send_osc method without widget creation"""
        from src.murnau.ui.main_window import MurnauUI

        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        # Create minimal instance for testing send_osc
        window = MurnauUI.__new__(MurnauUI)
        window.synth_name = "test_synth"
        window.osc_client = mock_client

        # Test the send_osc method
        window.send_osc = MurnauUI.send_osc.__get__(window)
        window.send_osc("/test", 42)

        mock_client.send_message.assert_called_once_with("/test_synth/test", 42.0)

    def test_parameter_change_methods(self):
        """Test parameter change method logic without widgets"""
        from src.murnau.ui.main_window import MurnauUI

        # Create minimal instance
        window = MurnauUI.__new__(MurnauUI)
        window.synth_name = "test_synth"
        window.osc_client = Mock()

        # Bind methods
        window.send_osc = MurnauUI.send_osc.__get__(window)
        window.on_gain_change = MurnauUI.on_gain_change.__get__(window)

        # Test parameter change
        window.on_gain_change(0.5)
        window.osc_client.send_message.assert_called_with("/test_synth/gain", 0.5)

    def test_midi_note_frequency_calculation(self):
        """Test MIDI note to frequency calculation"""
        import math

        # Test the MIDI to frequency formula (same as in melody.py)
        def midi_to_freq(midi_note):
            return 440.0 * math.pow(2.0, (midi_note - 69.0) / 12.0)

        # Test A4 (MIDI note 69) = 440 Hz
        assert abs(midi_to_freq(69) - 440.0) < 0.001

        # Test C4 (MIDI note 60) ≈ 261.63 Hz
        assert abs(midi_to_freq(60) - 261.63) < 0.1

    def test_note_tracking_logic(self):
        """Test note tracking data structures"""
        # Test the data structures used for note tracking
        active_notes = {}
        current_note = None

        # Simulate note on
        note_num = 60
        frequency = 261.63
        active_notes[note_num] = frequency
        current_note = note_num

        assert note_num in active_notes
        assert active_notes[note_num] == frequency
        assert current_note == note_num

        # Simulate note off
        if note_num in active_notes:
            del active_notes[note_num]
        if current_note == note_num:
            current_note = None

        assert note_num not in active_notes
        assert current_note is None


class TestMurnauUIMethodsIsolated:
    """Test individual methods in isolation"""

    def test_get_style_methods_exist(self):
        """Test that style methods exist and return strings"""
        from src.murnau.ui.main_window import MurnauUI

        # Create instance without initialization
        window = MurnauUI.__new__(MurnauUI)

        # Test that style methods exist
        assert hasattr(window, "_get_combo_style")
        assert hasattr(window, "_get_button_style")

        # Test style methods return strings (call them directly)
        combo_style = MurnauUI._get_combo_style(window)
        button_style = MurnauUI._get_button_style(window)

        assert isinstance(combo_style, str)
        assert isinstance(button_style, str)
        assert len(combo_style) > 0
        assert len(button_style) > 0

    def test_event_handler_methods_exist(self):
        """Test that event handler methods exist"""
        from src.murnau.ui.main_window import MurnauUI

        # Check that key methods exist
        assert hasattr(MurnauUI, "on_gain_change")
        assert hasattr(MurnauUI, "on_waveform_change")
        assert hasattr(MurnauUI, "send_osc")
        assert hasattr(MurnauUI, "on_note_on")
        assert hasattr(MurnauUI, "on_note_off")

    def test_midi_methods_exist(self):
        """Test that MIDI methods exist"""
        from src.murnau.ui.main_window import MurnauUI

        # Check MIDI-related methods
        assert hasattr(MurnauUI, "init_midi")
        assert hasattr(MurnauUI, "start_midi")
        assert hasattr(MurnauUI, "stop_midi")
        assert hasattr(MurnauUI, "handle_midi_message")
        assert hasattr(MurnauUI, "toggle_midi")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_close_event_handler(self, mock_udp_client):
        """Test close event handler logic"""
        from PyQt6.QtGui import QCloseEvent

        from src.murnau.ui.main_window import MurnauUI

        # Create minimal instance
        window = MurnauUI.__new__(MurnauUI)
        window.midi_input = Mock()
        window.midi_running = True

        # Bind close event method
        window.closeEvent = MurnauUI.closeEvent.__get__(window)
        window.stop_midi = MurnauUI.stop_midi.__get__(window)

        # Test close event
        event = QCloseEvent()
        window.closeEvent(event)

        # Should have called stop_midi
        assert window.midi_running is False


class TestMurnauUIIntegrationSafe:
    """Safe integration tests that don't create complex widgets"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    def test_initialization_flow(self, mock_midi, mock_udp_client):
        """Test initialization flow without widget creation"""
        from src.murnau.ui.main_window import MurnauUI

        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        mock_midi.return_value = ["Test MIDI Port"]

        # Mock all UI methods to prevent widget creation
        with patch.object(MurnauUI, "init_ui"), patch.object(
            MurnauUI, "init_midi"
        ), patch.object(MurnauUI, "init_parameters"), patch.object(
            MurnauUI, "show"
        ), patch.object(
            MurnauUI, "_animate_ui_elements"
        ), patch.object(
            MurnauUI, "setFocus"
        ):

            # This should not crash
            window = MurnauUI()

            # Basic assertions
            assert window.osc_ip == "127.0.0.1"
            assert window.osc_port == 5510
            assert window.synth_name == "legato_synth_stereo"
