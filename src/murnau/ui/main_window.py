"""Main window for Murnau synthesizer UI"""

import sys
import threading
import time

import mido
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDoubleValidator, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from pythonosc import udp_client

from .widgets import LabeledKnob, PianoKeys, WaveformSelector


class MurnauUI(QMainWindow):
    """Main window for Murnau synthesizer control interface"""

    def __init__(self):
        super().__init__()

        # OSC settings
        self.osc_ip = "127.0.0.1"
        self.osc_port = 5510
        self.synth_name = "legato_synth_stereo"

        # Create OSC client
        self.osc_client = udp_client.SimpleUDPClient(self.osc_ip, self.osc_port)

        # MIDI settings
        self.midi_input = None
        self.midi_thread = None
        self.midi_running = False

        # Active notes for MIDI tracking
        self.active_notes = {}  # note_num -> frequency
        self.current_note = None
        self.LEGATO_THRESHOLD = 0.03  # 30ms threshold for legato transitions
        self.last_gate_off_time = 0

        # Initialize UI
        self.init_ui()

        # Initialize MIDI
        self.init_midi()

        # Initialize parameters
        self.init_parameters()

        # Show the window
        self.show()

        # Set focus to piano keys
        self.piano.setFocus()

        # Start animation effects
        self._animate_ui_elements()

    def init_ui(self):
        """Initialize the main UI"""
        # Set window properties
        self.setWindowTitle("Murnau")
        self.setStyleSheet("background-color: #121212; color: #e0d9c6;")

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)

        # Top section with MIDI and controls
        top_section = QHBoxLayout()

        # Left column - MIDI controls
        left_column = QVBoxLayout()

        # MIDI control section
        midi_group = QGroupBox("MIDI Control")
        midi_layout = QHBoxLayout()

        # MIDI port selector
        self.midi_port_combo = QComboBox()
        self.midi_port_combo.setFont(QFont("Futura", 10))
        self.midi_port_combo.setStyleSheet(self._get_combo_style())

        # MIDI enable/disable button
        self.midi_toggle = QPushButton("Enable MIDI")
        self.midi_toggle.setCheckable(True)
        self.midi_toggle.setFont(QFont("Futura", 10))
        self.midi_toggle.setStyleSheet(self._get_button_style())
        self.midi_toggle.clicked.connect(self.toggle_midi)

        midi_layout.addWidget(QLabel("MIDI Port:"))
        midi_layout.addWidget(self.midi_port_combo)
        midi_layout.addWidget(self.midi_toggle)

        midi_group.setLayout(midi_layout)
        left_column.addWidget(midi_group)

        # Waveform selector below MIDI
        self.waveform_selector = WaveformSelector(midi_cc=1)
        self.waveform_selector.waveformChanged.connect(self.on_waveform_change)
        left_column.addWidget(self.waveform_selector)

        top_section.addLayout(left_column)

        # Right side - Controls
        right_section = QHBoxLayout()

        # Pitch control section
        pitch_group = QGroupBox("Pitch Controls")
        pitch_layout = QVBoxLayout()

        # Create pitch controls
        self._create_pitch_controls(pitch_layout)

        pitch_group.setLayout(pitch_layout)
        right_section.addWidget(pitch_group)

        # Filter section
        filter_group = QGroupBox("Filter")
        filter_layout = QVBoxLayout()

        # Create filter controls
        self._create_filter_controls(filter_layout)

        filter_group.setLayout(filter_layout)
        right_section.addWidget(filter_group)

        # ADSR knobs (Dual)
        adsr_group = QGroupBox("Envelope")
        adsr_layout = QVBoxLayout()

        # Create ADSR controls
        self._create_adsr_controls(adsr_layout)

        adsr_group.setLayout(adsr_layout)
        right_section.addWidget(adsr_group)

        # Gain knob
        gain_group = QGroupBox("Output")
        gain_layout = QHBoxLayout()

        self.gain_slider = LabeledKnob("Gain", 0.0, 1.0, 1.0, midi_cc=7)
        self.gain_slider.valueChanged.connect(self.on_gain_change)
        gain_layout.addWidget(self.gain_slider)

        gain_group.setLayout(gain_layout)
        right_section.addWidget(gain_group)

        top_section.addLayout(right_section)

        # Add top section to main layout
        main_layout.addLayout(top_section)

        # Add spacer to push keyboard to bottom
        main_layout.addStretch()

        # Piano keyboard at the bottom
        keyboard_group = QGroupBox("Keyboard")
        keyboard_layout = QVBoxLayout()

        self.piano = PianoKeys()
        self.piano.noteOn.connect(self.on_note_on)
        self.piano.noteOff.connect(self.on_note_off)
        keyboard_layout.addWidget(self.piano)

        keyboard_group.setLayout(keyboard_layout)
        main_layout.addWidget(keyboard_group)

        # Set window size
        self.resize(800, 600)

        # Initialize MIDI
        self.init_midi()

        # Update MIDI ports
        self.update_midi_ports()

        # Animate UI elements
        self._animate_ui_elements()

    def _create_pitch_controls(self, layout):
        """Create pitch control widgets"""
        # Coarse Tune
        coarse_layout = QHBoxLayout()
        coarse_label = QLabel("Coarse Tune")
        coarse_label.setStyleSheet("color: #E0E0E0;")
        self.coarse_tune = LabeledKnob("Coarse", -24, 24, 0, midi_cc=2, is_integer=True)
        self.coarse_tune.valueChanged.connect(self.on_coarse_tune_change)
        coarse_layout.addWidget(coarse_label)
        coarse_layout.addWidget(self.coarse_tune)
        layout.addLayout(coarse_layout)

        # Fine Tune
        fine_layout = QHBoxLayout()
        fine_label = QLabel("Fine Tune")
        fine_label.setStyleSheet("color: #E0E0E0;")
        self.fine_tune = LabeledKnob("Fine", -100, 100, 0, midi_cc=3)
        self.fine_tune.valueChanged.connect(self.on_fine_tune_change)
        fine_layout.addWidget(fine_label)
        fine_layout.addWidget(self.fine_tune)
        layout.addLayout(fine_layout)

        # Stability
        stability_layout = QHBoxLayout()
        stability_label = QLabel("Stability")
        stability_label.setStyleSheet("color: #E0E0E0;")
        self.stability = LabeledKnob("Stability", 0, 20, 0, midi_cc=4)
        self.stability.valueChanged.connect(self.on_stability_change)
        stability_layout.addWidget(stability_label)
        stability_layout.addWidget(self.stability)
        layout.addLayout(stability_layout)

        # Frequency Ramp Controls
        ramp_group = QGroupBox("Frequency Ramp")
        ramp_layout = QVBoxLayout()

        # Start Frequency Offset
        start_freq_layout = QHBoxLayout()
        start_freq_label = QLabel("Start Offset (Hz)")
        start_freq_label.setStyleSheet("color: #E0E0E0;")
        self.start_freq = QLineEdit()
        self.start_freq.setStyleSheet(self._get_line_edit_style())
        self.start_freq.setValidator(QDoubleValidator(-200, 200, 1))
        self.start_freq.setText("0")
        self.start_freq.editingFinished.connect(self.on_start_freq_change)
        start_freq_layout.addWidget(start_freq_label)
        start_freq_layout.addWidget(self.start_freq)
        ramp_layout.addLayout(start_freq_layout)

        # End Frequency Offset
        end_freq_layout = QHBoxLayout()
        end_freq_label = QLabel("End Offset (Hz)")
        end_freq_label.setStyleSheet("color: #E0E0E0;")
        self.end_freq = QLineEdit()
        self.end_freq.setStyleSheet(self._get_line_edit_style())
        self.end_freq.setValidator(QDoubleValidator(-200, 200, 1))
        self.end_freq.setText("0")
        self.end_freq.editingFinished.connect(self.on_end_freq_change)
        end_freq_layout.addWidget(end_freq_label)
        end_freq_layout.addWidget(self.end_freq)
        ramp_layout.addLayout(end_freq_layout)

        # Ramp Time
        ramp_time_layout = QHBoxLayout()
        ramp_time_label = QLabel("Ramp Time (s)")
        ramp_time_label.setStyleSheet("color: #E0E0E0;")
        self.ramp_time = QLineEdit()
        self.ramp_time.setStyleSheet(self._get_line_edit_style())
        self.ramp_time.setValidator(QDoubleValidator(0, 10, 2))
        self.ramp_time.setText("0")
        self.ramp_time.editingFinished.connect(self.on_ramp_time_change)
        ramp_time_layout.addWidget(ramp_time_label)
        ramp_time_layout.addWidget(self.ramp_time)
        ramp_layout.addLayout(ramp_time_layout)

        ramp_group.setLayout(ramp_layout)
        layout.addWidget(ramp_group)

    def _create_filter_controls(self, layout):
        """Create filter control widgets"""
        # Left channel filter
        left_filter_layout = QHBoxLayout()
        left_filter_label = QLabel("Left Channel")
        left_filter_label.setStyleSheet("color: #E0E0E0;")
        self.cutoff_knob_L = LabeledKnob(
            "Cutoff", 20, 20000, 2000, is_log=True, midi_cc=74
        )
        self.cutoff_knob_L.valueChanged.connect(lambda v: self.send_osc("/cutoff_L", v))
        self.resonance_knob_L = LabeledKnob("Resonance", 0.1, 4, 0.5, midi_cc=71)
        self.resonance_knob_L.valueChanged.connect(
            lambda v: self.send_osc("/resonance_L", v)
        )
        left_filter_layout.addWidget(left_filter_label)
        left_filter_layout.addWidget(self.cutoff_knob_L)
        left_filter_layout.addWidget(self.resonance_knob_L)
        layout.addLayout(left_filter_layout)

        # Right channel filter
        right_filter_layout = QHBoxLayout()
        right_filter_label = QLabel("Right Channel")
        right_filter_label.setStyleSheet("color: #E0E0E0;")
        self.cutoff_knob_R = LabeledKnob(
            "Cutoff", 20, 20000, 2000, is_log=True, midi_cc=75
        )
        self.cutoff_knob_R.valueChanged.connect(lambda v: self.send_osc("/cutoff_R", v))
        self.resonance_knob_R = LabeledKnob("Resonance", 0.1, 4, 0.5, midi_cc=76)
        self.resonance_knob_R.valueChanged.connect(
            lambda v: self.send_osc("/resonance_R", v)
        )
        right_filter_layout.addWidget(right_filter_label)
        right_filter_layout.addWidget(self.cutoff_knob_R)
        right_filter_layout.addWidget(self.resonance_knob_R)
        layout.addLayout(right_filter_layout)

    def _create_adsr_controls(self, layout):
        """Create ADSR control widgets"""
        # Left channel ADSR
        left_adsr_group = QGroupBox("Left Channel")
        left_adsr_layout = QHBoxLayout()
        left_adsr_layout.setSpacing(10)

        self.attack_slider_L = LabeledKnob("Attack", 0.001, 5.0, 0.005, midi_cc=73)
        self.attack_slider_L.valueChanged.connect(self.on_attack_L_change)
        self.attack_slider_L.setFixedSize(70, 100)
        left_adsr_layout.addWidget(self.attack_slider_L)

        self.decay_slider_L = LabeledKnob("Decay", 0.001, 3.0, 0.1, midi_cc=75)
        self.decay_slider_L.valueChanged.connect(self.on_decay_L_change)
        self.decay_slider_L.setFixedSize(70, 100)
        left_adsr_layout.addWidget(self.decay_slider_L)

        self.sustain_slider_L = LabeledKnob("Sustain", 0.0, 1.0, 0.9, midi_cc=31)
        self.sustain_slider_L.valueChanged.connect(self.on_sustain_L_change)
        self.sustain_slider_L.setFixedSize(70, 100)
        left_adsr_layout.addWidget(self.sustain_slider_L)

        self.release_slider_L = LabeledKnob("Release", 0.1, 5.0, 0.5, midi_cc=72)
        self.release_slider_L.valueChanged.connect(self.on_release_L_change)
        self.release_slider_L.setFixedSize(70, 100)
        left_adsr_layout.addWidget(self.release_slider_L)

        left_adsr_group.setLayout(left_adsr_layout)
        layout.addWidget(left_adsr_group)

        # Right channel ADSR
        right_adsr_group = QGroupBox("Right Channel")
        right_adsr_layout = QHBoxLayout()
        right_adsr_layout.setSpacing(10)

        self.attack_slider_R = LabeledKnob("Attack", 0.001, 5.0, 0.005, midi_cc=74)
        self.attack_slider_R.valueChanged.connect(self.on_attack_R_change)
        self.attack_slider_R.setFixedSize(70, 100)
        right_adsr_layout.addWidget(self.attack_slider_R)

        self.decay_slider_R = LabeledKnob("Decay", 0.001, 3.0, 0.1, midi_cc=76)
        self.decay_slider_R.valueChanged.connect(self.on_decay_R_change)
        self.decay_slider_R.setFixedSize(70, 100)
        right_adsr_layout.addWidget(self.decay_slider_R)

        self.sustain_slider_R = LabeledKnob("Sustain", 0.0, 1.0, 0.9, midi_cc=32)
        self.sustain_slider_R.valueChanged.connect(self.on_sustain_R_change)
        self.sustain_slider_R.setFixedSize(70, 100)
        right_adsr_layout.addWidget(self.sustain_slider_R)

        self.release_slider_R = LabeledKnob("Release", 0.1, 5.0, 0.5, midi_cc=77)
        self.release_slider_R.valueChanged.connect(self.on_release_R_change)
        self.release_slider_R.setFixedSize(70, 100)
        right_adsr_layout.addWidget(self.release_slider_R)

        right_adsr_group.setLayout(right_adsr_layout)
        layout.addWidget(right_adsr_group)

    def _get_combo_style(self):
        """Get combo box stylesheet"""
        return """
            QComboBox {
                background-color: #2A2A2A;
                color: #E6E6E6;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """

    def _get_button_style(self):
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #2A2A2A;
                color: #E6E6E6;
                border: 1px solid #3A3A3A;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:checked {
                background-color: #5D5236;
                color: #FFFFFF;
                border: 1px solid #D4BF8A;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """

    def _get_line_edit_style(self):
        """Get line edit stylesheet"""
        return """
            QLineEdit {
                background-color: #2A2A2A;
                color: #E0E0E0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px;
            }
        """

    def _animate_ui_elements(self):
        """Add start-up animations for expressionist feel"""
        # Create animated elements
        self.animations = []

        # Create a timer to animate waveform visualization
        self.wave_animation_timer = QTimer()
        self.wave_animation_timer.timeout.connect(self.waveform_selector.animate_wave)
        self.wave_animation_timer.start(50)  # Update every 50ms for smooth animation

    def init_parameters(self):
        """Initialize synth parameters via OSC"""
        # Send initial parameter values
        self.on_gain_change(1.0)
        self.on_waveform_change(2)  # sawtooth

        # Initialize left channel ADSR
        self.on_attack_L_change(0.005)
        self.on_decay_L_change(0.1)
        self.on_sustain_L_change(0.9)
        self.on_release_L_change(0.5)

        # Initialize right channel ADSR
        self.on_attack_R_change(0.005)
        self.on_decay_R_change(0.1)
        self.on_sustain_R_change(0.9)
        self.on_release_R_change(0.5)

        # Initialize both L/R filter controls
        self.on_cutoff_L_change(2000)
        self.on_cutoff_R_change(2000)
        self.on_resonance_L_change(0.5)
        self.on_resonance_R_change(0.5)

        # Initialize pitch controls
        self.on_coarse_tune_change(0)
        self.on_fine_tune_change(0)
        self.on_stability_change(0)

        # Initialize ramp controls
        self.send_osc("/start_freq_offset", 0)
        self.send_osc("/end_freq_offset", 0)
        self.send_osc("/ramp_time", 0)

    def on_start_freq_change(self):
        """Handle start frequency offset change"""
        try:
            value = float(self.start_freq.text())
            self.send_osc("/start_freq_offset", value)
        except ValueError:
            pass

    def on_end_freq_change(self):
        """Handle end frequency offset change"""
        try:
            value = float(self.end_freq.text())
            self.send_osc("/end_freq_offset", value)
        except ValueError:
            pass

    def on_ramp_time_change(self):
        """Handle ramp time change"""
        try:
            value = float(self.ramp_time.text())
            self.send_osc("/ramp_time", value)
        except ValueError:
            pass

    def update_midi_ports(self):
        """Update MIDI port selection dropdown"""
        current_port = self.midi_port_combo.currentText()

        # Clear current items
        self.midi_port_combo.clear()

        # Get available ports
        try:
            ports = mido.get_input_names()
            if ports:
                self.midi_port_combo.addItems(ports)

                # Restore previous selection if available
                if current_port in ports:
                    index = ports.index(current_port)
                    self.midi_port_combo.setCurrentIndex(index)
            else:
                self.midi_port_combo.addItem("No MIDI devices found")
        except Exception as e:
            self.midi_port_combo.addItem(f"Error: {str(e)}")

    def init_midi(self):
        """Initialize MIDI processing"""
        # To be initialized when user connects
        pass

    def toggle_midi(self):
        """Toggle MIDI connection on/off"""
        if not self.midi_running:
            self.start_midi()
        else:
            self.stop_midi()

    def start_midi(self):
        """Start MIDI processing"""
        if self.midi_running:
            return

        # Get selected port
        port_name = self.midi_port_combo.currentText()
        if (
            not port_name
            or port_name.startswith("No MIDI")
            or port_name.startswith("Error")
        ):
            self.midi_toggle.setText("Error: No valid MIDI port selected")
            self.midi_toggle.setStyleSheet("color: #FF5555; background: transparent;")
            return

        try:
            # Open MIDI input
            self.midi_input = mido.open_input(port_name)
            self.midi_running = True

            # Start MIDI processing thread
            self.midi_thread = threading.Thread(target=self.process_midi, daemon=True)
            self.midi_thread.start()

            # Update UI
            self.midi_toggle.setText("Disconnect MIDI")
            self.midi_toggle.setStyleSheet("color: #8AFF7A; background: transparent;")
            midi_msg = f"MIDI: Connected to {port_name}"
            osc_msg = f"OSC: {self.synth_name} on {self.osc_ip}:{self.osc_port}"
            self.statusBar().showMessage(f"{midi_msg} | {osc_msg}")

        except Exception as e:
            self.midi_toggle.setText(f"Error: {str(e)}")
            self.midi_toggle.setStyleSheet("color: #FF5555; background: transparent;")

    def stop_midi(self):
        """Stop MIDI processing"""
        if not self.midi_running:
            return

        # Close MIDI
        self.midi_running = False
        if self.midi_input:
            self.midi_input.close()
            self.midi_input = None

        # Update UI
        self.midi_toggle.setText("Connect MIDI")
        self.midi_toggle.setStyleSheet("color: #8A7A55; background: transparent;")
        self.statusBar().showMessage(
            f"OSC: {self.synth_name} on {self.osc_ip}:{self.osc_port}"
        )

    def process_midi(self):
        """Process MIDI messages in a background thread"""
        while self.midi_running and self.midi_input:
            try:
                # Get pending messages
                for message in self.midi_input.iter_pending():
                    # Process in the main thread
                    self.handle_midi_message(message)

                # Brief sleep to prevent CPU overload
                time.sleep(0.001)
            except Exception as e:
                print(f"MIDI processing error: {e}")
                break

    def handle_midi_message(self, message):
        """Handle incoming MIDI message"""
        try:
            # Note on
            if message.type == "note_on" and message.velocity > 0:
                # Convert MIDI note to frequency
                freq = 440.0 * (2.0 ** ((message.note - 69) / 12.0))

                # Add to active notes
                self.active_notes[message.note] = freq

                # Determine if we should use legato mode
                now = time.time()
                use_legato = self.current_note is not None and (
                    now - self.last_gate_off_time < self.LEGATO_THRESHOLD
                )

                # Set frequency first
                self.send_osc("/freq", freq)

                # If not in legato mode or no current note, send gate on
                if not use_legato or self.current_note is None:
                    self.send_osc("/gate", 1.0)

                self.current_note = message.note

                # Update piano UI
                if self.piano.handle_midi_note_on(message.note, message.velocity):
                    # UI was updated successfully
                    pass

            # Note off
            elif message.type == "note_off" or (
                message.type == "note_on" and message.velocity == 0
            ):
                # Remove from active notes
                if message.note in self.active_notes:
                    del self.active_notes[message.note]

                # Only react if this is the current sounding note
                if message.note == self.current_note:
                    # Check if we have other active notes
                    if self.active_notes:
                        # Find the highest note (usually most recently pressed)
                        next_note = max(self.active_notes.keys())
                        next_freq = self.active_notes[next_note]

                        # Set the new frequency
                        self.send_osc("/freq", next_freq)
                        self.current_note = next_note
                    else:
                        # No more active notes, turn off gate
                        self.send_osc("/gate", 0.0)
                        self.last_gate_off_time = time.time()
                        self.current_note = None

                # Update piano UI
                self.piano.handle_midi_note_off(message.note)

            # Control changes for parameters
            elif message.type == "control_change":
                self._handle_midi_cc(message.control, message.value)

        except Exception as e:
            print(f"Error handling MIDI message: {e}")

    def _handle_midi_cc(self, cc, value):
        """Handle MIDI control change message"""
        # Map CC values to parameters
        if cc == self.waveform_selector.midi_cc:
            self.waveform_selector.set_from_midi_cc(value)
        elif cc == self.attack_slider_L.midi_cc:
            self.attack_slider_L.set_from_midi_cc(value)
        elif cc == self.decay_slider_L.midi_cc:
            self.decay_slider_L.set_from_midi_cc(value)
        elif cc == self.sustain_slider_L.midi_cc:
            self.sustain_slider_L.set_from_midi_cc(value)
        elif cc == self.release_slider_L.midi_cc:
            self.release_slider_L.set_from_midi_cc(value)
        elif cc == self.attack_slider_R.midi_cc:
            self.attack_slider_R.set_from_midi_cc(value)
        elif cc == self.decay_slider_R.midi_cc:
            self.decay_slider_R.set_from_midi_cc(value)
        elif cc == self.sustain_slider_R.midi_cc:
            self.sustain_slider_R.set_from_midi_cc(value)
        elif cc == self.release_slider_R.midi_cc:
            self.release_slider_R.set_from_midi_cc(value)
        elif cc == self.cutoff_knob_L.midi_cc:
            self.cutoff_knob_L.set_from_midi_cc(value)
        elif cc == self.cutoff_knob_R.midi_cc:
            self.cutoff_knob_R.set_from_midi_cc(value)
        elif cc == self.resonance_knob_L.midi_cc:
            self.resonance_knob_L.set_from_midi_cc(value)
        elif cc == self.resonance_knob_R.midi_cc:
            self.resonance_knob_R.set_from_midi_cc(value)

    def on_gain_change(self, value):
        """Handle gain change"""
        self.send_osc("/gain", value)

    def on_waveform_change(self, index):
        """Handle waveform change"""
        self.send_osc("/wave_type", index)

    def on_attack_L_change(self, value):
        """Handle left channel attack change"""
        self.send_osc("/attack_L", value)

    def on_decay_L_change(self, value):
        """Handle left channel decay change"""
        self.send_osc("/decay_L", value)

    def on_sustain_L_change(self, value):
        """Handle left channel sustain change"""
        self.send_osc("/sustain_L", value)

    def on_release_L_change(self, value):
        """Handle left channel release change"""
        self.send_osc("/release_L", value)

    def on_attack_R_change(self, value):
        """Handle right channel attack change"""
        self.send_osc("/attack_R", value)

    def on_decay_R_change(self, value):
        """Handle right channel decay change"""
        self.send_osc("/decay_R", value)

    def on_sustain_R_change(self, value):
        """Handle right channel sustain change"""
        self.send_osc("/sustain_R", value)

    def on_release_R_change(self, value):
        """Handle right channel release change"""
        self.send_osc("/release_R", value)

    def on_cutoff_L_change(self, value):
        """Handle left channel filter cutoff change"""
        self.send_osc("/cutoff_L", value)

    def on_cutoff_R_change(self, value):
        """Handle right channel filter cutoff change"""
        self.send_osc("/cutoff_R", value)

    def on_resonance_L_change(self, value):
        """Handle left channel filter resonance change"""
        self.send_osc("/resonance_L", value)

    def on_resonance_R_change(self, value):
        """Handle right channel filter resonance change"""
        self.send_osc("/resonance_R", value)

    def on_coarse_tune_change(self, value):
        """Handle coarse tune change"""
        self.send_osc("/coarse_tune", value)

    def on_fine_tune_change(self, value):
        """Handle fine tune change"""
        self.send_osc("/fine_tune", value)

    def on_stability_change(self, value):
        """Handle stability change"""
        self.send_osc("/stability", value)

    def send_osc(self, address, value):
        """Send OSC message"""
        # Add synth name to the address path
        full_address = f"/{self.synth_name}{address}"
        self.osc_client.send_message(full_address, float(value))

    def on_note_on(self, frequency):
        """Handle note on from UI"""
        self.send_osc("/freq", frequency)
        self.send_osc("/gate", 1.0)

    def on_note_off(self):
        """Handle note off from UI"""
        self.send_osc("/gate", 0.0)

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop MIDI processing
        self.stop_midi()

        # Turn off any sound
        self.send_osc("/gate", 0.0)

        # Accept the event
        event.accept()
