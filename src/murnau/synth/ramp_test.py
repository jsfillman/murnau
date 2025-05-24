"""Frequency ramp testing functionality for Murnau synthesizer"""

import time

from pythonosc import udp_client


def test_ramp(
    tests=None, osc_ip="127.0.0.1", osc_port=5510, synth_name="legato_synth_stereo"
):
    """Test frequency ramp functionality

    Args:
        tests (list): List of (start_freq, end_freq, ramp_time, hold_time) tuples
        osc_ip (str): IP address for OSC communication
        osc_port (int): Port for OSC communication
        synth_name (str): Name of the synthesizer
    """
    # Default test scenarios if none provided
    if tests is None:
        tests = [
            # (start_freq, end_freq, ramp_time, hold_time)
            (220, 880, 2.0, 0.5),  # 1 octave up over 2 seconds
            (880, 220, 2.0, 0.5),  # 1 octave down over 2 seconds
            (440, 880, 0.5, 0.5),  # Fast up
            (880, 440, 0.5, 0.5),  # Fast down
        ]

    # Create OSC client
    client = udp_client.SimpleUDPClient(osc_ip, osc_port)

    # Initialize synth with basic parameters
    print("Initializing synth...")
    client.send_message(f"/{synth_name}/wave_type", 2)  # sawtooth
    client.send_message(f"/{synth_name}/gain", 0.7)
    client.send_message(f"/{synth_name}/cutoff_L", 5000)
    client.send_message(f"/{synth_name}/cutoff_R", 5000)

    for start_freq, end_freq, ramp_time, hold_time in tests:
        print(f"\nTesting ramp from {start_freq}Hz to {end_freq}Hz over {ramp_time}s")

        # Set ramp parameters
        client.send_message(f"/{synth_name}/start_freq", start_freq)
        client.send_message(f"/{synth_name}/end_freq", end_freq)
        client.send_message(f"/{synth_name}/ramp_time", ramp_time)

        # Start the sound
        client.send_message(f"/{synth_name}/gate", 1.0)

        # Wait for ramp and hold
        time.sleep(ramp_time + hold_time)

        # Stop the sound
        client.send_message(f"/{synth_name}/gate", 0.0)
        time.sleep(0.5)  # Wait for release


def main():
    """Main entry point for standalone execution"""
    test_ramp()


if __name__ == "__main__":
    main()
