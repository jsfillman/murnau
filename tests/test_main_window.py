#!/usr/bin/env python3

import os
import sys
import threading
from unittest.mock import Mock, patch, MagicMock

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.murnau.ui.main_window import MurnauUI


class TestMurnauUIInit:
    """Test MurnauUI initialization"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_init_creates_osc_client(self, mock_udp_client, qtbot):
        """Test that initialization creates OSC client with correct parameters"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Verify OSC client creation
        mock_udp_client.assert_called_once_with("127.0.0.1", 5510)
        assert window.osc_client == mock_client
        assert window.osc_ip == "127.0.0.1"
        assert window.osc_port == 5510
        assert window.synth_name == "legato_synth_stereo"

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_init_sets_default_values(self, mock_udp_client, qtbot):
        """Test that initialization sets correct default values"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Check MIDI settings
        assert window.midi_input is None
        assert window.midi_thread is None
        assert window.midi_running is False

        # Check note tracking
        assert window.active_notes == {}
        assert window.current_note is None

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_init_ui_components(self, mock_udp_client, qtbot):
        """Test that UI components are properly initialized"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Check main window properties
        assert window.windowTitle() == "Murnau"

        # Check central widget is set
        assert window.centralWidget() is not None


class TestMurnauUIComponents:
    """Test UI component creation"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_midi_components_created(self, mock_udp_client, qtbot):
        """Test MIDI UI components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Check MIDI components
        assert hasattr(window, "midi_port_combo")
        assert hasattr(window, "midi_toggle")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_waveform_components_created(self, mock_udp_client, qtbot):
        """Test waveform components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        assert hasattr(window, "waveform_selector")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_pitch_components_created(self, mock_udp_client, qtbot):
        """Test pitch control components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        assert hasattr(window, "coarse_tune")
        assert hasattr(window, "fine_tune")
        assert hasattr(window, "stability")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_filter_components_created(self, mock_udp_client, qtbot):
        """Test filter control components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Left channel
        assert hasattr(window, "cutoff_knob_L")
        assert hasattr(window, "resonance_knob_L")
        # Right channel
        assert hasattr(window, "cutoff_knob_R")
        assert hasattr(window, "resonance_knob_R")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_adsr_components_created(self, mock_udp_client, qtbot):
        """Test ADSR control components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Left channel ADSR
        assert hasattr(window, "attack_slider_L")
        assert hasattr(window, "decay_slider_L")
        assert hasattr(window, "sustain_slider_L")
        assert hasattr(window, "release_slider_L")
        
        # Right channel ADSR
        assert hasattr(window, "attack_slider_R")
        assert hasattr(window, "decay_slider_R")
        assert hasattr(window, "sustain_slider_R")
        assert hasattr(window, "release_slider_R")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_output_components_created(self, mock_udp_client, qtbot):
        """Test output control components are created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        assert hasattr(window, "gain_slider")

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_piano_component_created(self, mock_udp_client, qtbot):
        """Test piano keyboard component is created"""
        window = MurnauUI()
        qtbot.addWidget(window)

        assert hasattr(window, "piano")


class TestMurnauUIParameters:
    """Test parameter handling"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_init_parameters_sends_osc(self, mock_udp_client, qtbot):
        """Test that parameter initialization sends OSC messages"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # init_parameters is called during construction, check messages were sent
        assert mock_client.send_message.call_count > 0

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_parameter_change_handlers(self, mock_udp_client, qtbot):
        """Test parameter change handler methods"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Test gain change
        window.on_gain_change(0.5)
        mock_client.send_message.assert_called_with("/legato_synth_stereo/gain", 0.5)

        # Test waveform change
        window.on_waveform_change(1)
        mock_client.send_message.assert_called_with("/legato_synth_stereo/wave_type", 1)

        # Test attack change
        window.on_attack_L_change(0.1)
        mock_client.send_message.assert_called_with("/legato_synth_stereo/attack_L", 0.1)

        # Test cutoff change
        window.on_cutoff_L_change(1000)
        mock_client.send_message.assert_called_with("/legato_synth_stereo/cutoff_L", 1000)


class TestMurnauUIOSC:
    """Test OSC communication"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_send_osc_basic(self, mock_udp_client, qtbot):
        """Test basic OSC message sending"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Test sending OSC message
        window.send_osc("/test", 42)
        mock_client.send_message.assert_called_with("/legato_synth_stereo/test", 42)

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_send_osc_with_exception(self, mock_udp_client, qtbot):
        """Test OSC sending with exception handling"""
        mock_client = Mock()
        mock_client.send_message.side_effect = Exception("Connection error")
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Should not raise exception
        window.send_osc("/test", 42)


class TestMurnauUINotes:
    """Test note handling"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_on_note_on(self, mock_udp_client, qtbot):
        """Test note on handling"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Test note on
        test_freq = 440.0
        window.on_note_on(test_freq)

        # Check OSC messages
        mock_client.send_message.assert_any_call("/legato_synth_stereo/freq", test_freq)
        mock_client.send_message.assert_any_call("/legato_synth_stereo/gate", 1.0)

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_on_note_off(self, mock_udp_client, qtbot):
        """Test note off handling"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Test note off
        window.on_note_off()

        # Check OSC message
        mock_client.send_message.assert_called_with("/legato_synth_stereo/gate", 0.0)


class TestMurnauUIMIDI:
    """Test MIDI functionality"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    def test_init_midi_with_ports(self, mock_get_input_names, mock_udp_client, qtbot):
        """Test MIDI initialization with available ports"""
        mock_get_input_names.return_value = ["MIDI Port 1", "MIDI Port 2"]

        window = MurnauUI()
        qtbot.addWidget(window)

        # Check that MIDI ports are loaded
        assert window.midi_port_combo.count() >= 2

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    def test_init_midi_no_ports(self, mock_get_input_names, mock_udp_client, qtbot):
        """Test MIDI initialization with no available ports"""
        mock_get_input_names.return_value = []

        window = MurnauUI()
        qtbot.addWidget(window)

        # Should handle gracefully
        assert window.midi_port_combo.count() >= 1

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    def test_init_midi_exception(self, mock_get_input_names, mock_udp_client, qtbot):
        """Test MIDI initialization with exception"""
        mock_get_input_names.side_effect = Exception("MIDI error")

        window = MurnauUI()
        qtbot.addWidget(window)

        # Should not raise exception and handle gracefully
        assert hasattr(window, 'midi_port_combo')

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.open_input")
    def test_start_midi_success(self, mock_open_input, mock_udp_client, qtbot):
        """Test successful MIDI start"""
        mock_input = Mock()
        mock_open_input.return_value = mock_input

        window = MurnauUI()
        qtbot.addWidget(window)

        # Add a test port and select it
        window.midi_port_combo.addItem("Test Port")
        window.midi_port_combo.setCurrentText("Test Port")

        window.start_midi()

        # Check MIDI setup
        mock_open_input.assert_called_once_with("Test Port")
        assert window.midi_input == mock_input
        assert window.midi_running is True

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.open_input")
    def test_start_midi_failure(self, mock_open_input, mock_udp_client, qtbot):
        """Test MIDI start failure"""
        mock_open_input.side_effect = Exception("MIDI connection error")

        window = MurnauUI()
        qtbot.addWidget(window)

        # Add a test port and select it
        window.midi_port_combo.addItem("Test Port")
        window.midi_port_combo.setCurrentText("Test Port")

        # Should not raise exception
        window.start_midi()

        # Check error state
        assert window.midi_input is None
        assert window.midi_running is False

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_stop_midi(self, mock_udp_client, qtbot):
        """Test MIDI stop"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Set up MIDI state
        mock_input = Mock()
        window.midi_input = mock_input
        window.midi_running = True

        window.stop_midi()

        # Check cleanup
        assert window.midi_running is False
        mock_input.close.assert_called_once()

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_handle_midi_note_on(self, mock_udp_client, qtbot):
        """Test MIDI note on message handling"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Create mock MIDI message
        mock_msg = Mock()
        mock_msg.type = "note_on"
        mock_msg.note = 60
        mock_msg.velocity = 100

        window.handle_midi_message(mock_msg)

        # Check that note was processed
        assert mock_client.send_message.call_count > 0

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_handle_midi_note_off(self, mock_udp_client, qtbot):
        """Test MIDI note off message handling"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Clear init calls
        mock_client.reset_mock()

        # Create mock MIDI message
        mock_msg = Mock()
        mock_msg.type = "note_off"
        mock_msg.note = 60
        mock_msg.velocity = 0

        window.handle_midi_message(mock_msg)

        # Check that message was processed
        # Note: the actual behavior depends on implementation


class TestMurnauUIStyles:
    """Test UI styling methods"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_get_combo_style(self, mock_udp_client, qtbot):
        """Test combo box style generation"""
        window = MurnauUI()
        qtbot.addWidget(window)

        style = window._get_combo_style()
        
        # Check that style contains expected properties
        assert isinstance(style, str)
        assert len(style) > 0

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_get_button_style(self, mock_udp_client, qtbot):
        """Test button style generation"""
        window = MurnauUI()
        qtbot.addWidget(window)

        style = window._get_button_style()
        
        # Check that style contains expected properties
        assert isinstance(style, str)
        assert len(style) > 0


class TestMurnauUIEvents:
    """Test event handling"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_close_event_stops_midi(self, mock_udp_client, qtbot):
        """Test that closing window stops MIDI"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Set up MIDI state
        mock_input = Mock()
        window.midi_input = mock_input
        window.midi_running = True

        # Create close event
        event = QCloseEvent()
        window.closeEvent(event)

        # Check that MIDI was stopped
        assert window.midi_running is False
        mock_input.close.assert_called_once()

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_toggle_midi_button(self, mock_udp_client, qtbot):
        """Test MIDI toggle button functionality"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Test toggle functionality exists
        assert hasattr(window, 'toggle_midi')
        
        # Should not raise exception when called
        window.toggle_midi()


class TestMurnauUIIntegration:
    """Integration tests for MurnauUI"""

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_full_ui_creation(self, mock_udp_client, qtbot):
        """Test complete UI creation without errors"""
        window = MurnauUI()
        qtbot.addWidget(window)

        # Check that window is properly created
        assert window.centralWidget() is not None

        # The window shows itself in __init__, so it should be visible
        assert window.isVisible() is True

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    @patch("src.murnau.ui.main_window.mido.get_input_names")
    def test_ui_with_midi_initialization(self, mock_get_input_names, mock_udp_client, qtbot):
        """Test UI creation with MIDI initialization"""
        mock_get_input_names.return_value = ["Test MIDI Port"]

        window = MurnauUI()
        qtbot.addWidget(window)

        # MIDI should be initialized
        assert hasattr(window, 'midi_port_combo')

    @patch("src.murnau.ui.main_window.udp_client.SimpleUDPClient")
    def test_parameter_initialization(self, mock_udp_client, qtbot):
        """Test that parameters are initialized"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        window = MurnauUI()
        qtbot.addWidget(window)

        # Parameters should be initialized during construction
        assert mock_client.send_message.call_count > 0