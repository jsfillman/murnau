"""Melody playback functionality for Murnau synthesizer"""

import math
import time

from pythonosc import udp_client


def midi_to_freq(midi_note):
    """Convert MIDI note number to frequency

    Args:
        midi_note (int): MIDI note number (0-127)

    Returns:
        float: Frequency in Hz
    """
    return 440.0 * math.pow(2.0, (midi_note - 69.0) / 12.0)


def play_note(client, freq, duration, synth_name="legato_synth_stereo"):
    """Play a note with the given frequency and duration

    Args:
        client: OSC UDP client instance
        freq (float): Frequency in Hz
        duration (float): Duration in seconds
        synth_name (str): Name of the synthesizer
    """
    # Send frequency first
    client.send_message(f"/{synth_name}/freq", freq)

    # Gate on
    client.send_message(f"/{synth_name}/gate", 1.0)

    # Wait for duration
    time.sleep(duration)

    # Gate off
    client.send_message(f"/{synth_name}/gate", 0.0)

    # Small gap between notes
    time.sleep(0.05)


def init_synth(client, synth_name="legato_synth_stereo"):
    """Initialize synth parameters

    Args:
        client: OSC UDP client instance
        synth_name (str): Name of the synthesizer
    """
    # Set waveform to sawtooth
    client.send_message(f"/{synth_name}/wave_type", 2)

    # Set ADSR (moderate values)
    client.send_message(f"/{synth_name}/attack_L", 0.01)
    client.send_message(f"/{synth_name}/decay_L", 0.1)
    client.send_message(f"/{synth_name}/sustain_L", 0.7)
    client.send_message(f"/{synth_name}/release_L", 0.3)

    client.send_message(f"/{synth_name}/attack_R", 0.01)
    client.send_message(f"/{synth_name}/decay_R", 0.1)
    client.send_message(f"/{synth_name}/sustain_R", 0.7)
    client.send_message(f"/{synth_name}/release_R", 0.3)

    # Set filter cutoff high
    client.send_message(f"/{synth_name}/cutoff_L", 5000)
    client.send_message(f"/{synth_name}/cutoff_R", 5000)
    client.send_message(f"/{synth_name}/resonance_L", 0.5)
    client.send_message(f"/{synth_name}/resonance_R", 0.5)

    # Set gain
    client.send_message(f"/{synth_name}/gain", 0.7)


def play_melody(
    melody_data=None,
    osc_ip="127.0.0.1",
    osc_port=5510,
    synth_name="legato_synth_stereo",
):
    """Play a melody using the synthesizer

    Args:
        melody_data (list): List of (midi_note, duration) tuples
        osc_ip (str): IP address for OSC communication
        osc_port (int): Port for OSC communication
        synth_name (str): Name of the synthesizer
    """
    # Default melody if none provided
    if melody_data is None:
        melody_data = [
            (60, 0.5),  # C4
            (64, 0.5),  # E4
            (67, 0.5),  # G4
            (72, 1.0),  # C5
            (67, 0.5),  # G4
            (64, 0.5),  # E4
            (60, 1.0),  # C4
        ]

    # Create OSC client
    client = udp_client.SimpleUDPClient(osc_ip, osc_port)

    # Initialize synth
    print("Initializing synth parameters...")
    init_synth(client, synth_name)
    time.sleep(0.5)  # Wait for parameters to settle

    print("Playing melody...")

    # Play the melody
    for note, duration in melody_data:
        freq = midi_to_freq(note)
        print(f"Playing note: {note} (freq: {freq:.2f}Hz) for {duration}s")
        play_note(client, freq, duration, synth_name)

    print("Melody finished!")


def main():
    """Main entry point for standalone execution"""
    play_melody()


if __name__ == "__main__":
    main()
