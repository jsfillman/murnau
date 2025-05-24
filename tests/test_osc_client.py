#!/usr/bin/env python3

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.murnau.utils.osc_client import OSCClient


class TestOSCClient:
    """Test OSCClient utility class"""

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_init_creates_client(self, mock_udp_client):
        """Test OSCClient initialization"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        osc = OSCClient("192.168.1.1", 5511, "test_synth")

        mock_udp_client.assert_called_once_with("192.168.1.1", 5511)
        assert osc.client == mock_client
        assert osc.synth_name == "test_synth"

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_init_default_values(self, mock_udp_client):
        """Test OSCClient with default values"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        osc = OSCClient()

        mock_udp_client.assert_called_once_with("127.0.0.1", 5510)
        assert osc.synth_name == "legato_synth_stereo"

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_send_message(self, mock_udp_client):
        """Test sending OSC message with synth name prefix"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        osc = OSCClient(synth_name="test_synth")
        osc.send("/freq", 440.0)

        mock_client.send_message.assert_called_once_with("/test_synth/freq", 440.0)

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_send_raw_message(self, mock_udp_client):
        """Test sending raw OSC message without synth name prefix"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        osc = OSCClient(synth_name="test_synth")
        osc.send_raw("/raw/message", 123)

        mock_client.send_message.assert_called_once_with("/raw/message", 123)

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_set_synth_name(self, mock_udp_client):
        """Test changing synth name"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client

        osc = OSCClient(synth_name="old_synth")
        osc.set_synth_name("new_synth")

        assert osc.synth_name == "new_synth"

        # Test that new name is used
        osc.send("/test", 42)
        mock_client.send_message.assert_called_with("/new_synth/test", 42)

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_reconnect(self, mock_udp_client):
        """Test reconnecting with new IP and port"""
        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_udp_client.side_effect = [mock_client1, mock_client2]

        osc = OSCClient("127.0.0.1", 5510)
        assert osc.client == mock_client1

        osc.reconnect("192.168.1.100", 5511)

        # Should create new client
        assert mock_udp_client.call_count == 2
        mock_udp_client.assert_any_call("192.168.1.100", 5511)
        assert osc.client == mock_client2

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_send_with_exception(self, mock_udp_client):
        """Test send message with client exception"""
        mock_client = Mock()
        mock_client.send_message.side_effect = Exception("Connection error")
        mock_udp_client.return_value = mock_client

        osc = OSCClient()
        
        # Should raise exception (OSC client doesn't handle exceptions)
        with pytest.raises(Exception, match="Connection error"):
            osc.send("/test", 42)

    @patch("src.murnau.utils.osc_client.udp_client.SimpleUDPClient")
    def test_send_raw_with_exception(self, mock_udp_client):
        """Test send raw message with client exception"""
        mock_client = Mock()
        mock_client.send_message.side_effect = Exception("Connection error")
        mock_udp_client.return_value = mock_client

        osc = OSCClient()
        
        # Should raise exception (OSC client doesn't handle exceptions)
        with pytest.raises(Exception, match="Connection error"):
            osc.send_raw("/test", 42)