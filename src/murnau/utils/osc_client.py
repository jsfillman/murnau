"""OSC client utility for Murnau synthesizer"""

from pythonosc import udp_client


class OSCClient:
    """Wrapper for OSC UDP client with convenience methods"""

    def __init__(self, ip="127.0.0.1", port=5510, synth_name="legato_synth_stereo"):
        """Initialize OSC client

        Args:
            ip (str): IP address for OSC communication
            port (int): Port for OSC communication
            synth_name (str): Name of the synthesizer
        """
        self.ip = ip
        self.port = port
        self.synth_name = synth_name
        self.client = udp_client.SimpleUDPClient(ip, port)

    def send(self, address, value):
        """Send an OSC message

        Args:
            address (str): OSC address (will be prefixed with synth name)
            value: Value to send
        """
        full_address = f"/{self.synth_name}{address}"
        self.client.send_message(full_address, float(value))

    def send_raw(self, address, value):
        """Send an OSC message without synth name prefix

        Args:
            address (str): Full OSC address
            value: Value to send
        """
        self.client.send_message(address, value)

    def set_synth_name(self, name):
        """Change the synthesizer name

        Args:
            name (str): New synthesizer name
        """
        self.synth_name = name

    def reconnect(self, ip=None, port=None):
        """Reconnect to a different IP/port

        Args:
            ip (str): New IP address (optional)
            port (int): New port (optional)
        """
        if ip is not None:
            self.ip = ip
        if port is not None:
            self.port = port

        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
