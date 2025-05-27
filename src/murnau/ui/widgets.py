"""Custom UI widgets for Murnau synthesizer interface"""

import math

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import (
    QDial,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CustomDial(QDial):
    """Custom styled knob with value label"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value_text = "0.00"
        self.setFixedSize(60, 60)

    def set_value_text(self, text):
        self.value_text = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the value text in the center
        painter.setFont(QFont("Futura", 8))
        painter.setPen(QPen(QColor("#000000")))

        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.value_text)


class LabeledKnob(QWidget):
    """Knob control with label and value display"""

    valueChanged = pyqtSignal(float)

    def __init__(
        self,
        name,
        min_val,
        max_val,
        default,
        is_log=False,
        parent=None,
        midi_cc=None,
        is_integer=False,
    ):
        super().__init__(parent)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.is_log = is_log
        self.midi_cc = midi_cc
        self.is_integer = is_integer

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Create label with name
        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Futura", 9))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #E6E6E6;")

        # Add MIDI CC label if assigned
        if midi_cc is not None:
            self.name_label.setText(f"{name}\n(CC{midi_cc})")

        # Create custom knob
        self.knob = CustomDial()
        self.knob.setMinimum(0)
        self.knob.setMaximum(1000)
        self.knob.setNotchesVisible(True)
        self.knob.setWrapping(False)
        self.knob.setStyleSheet(
            """
            QDial {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 30px;
            }
            QDial::groove {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #8A7A55, stop:1 #5D5236);
                border-radius: 30px;
            }
            QDial::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #E5D5A0, stop:1 #C0AA70);
                border: 1px solid #555555;
                width: 14px;
                height: 14px;
                border-radius: 7px;
            }
        """
        )

        # Set default position based on input value
        default_pos = self.value_to_knob(default)
        self.knob.setValue(default_pos)

        # Update the value text
        if self.is_integer:
            self.knob.set_value_text(f"{int(default)}")
        else:
            self.knob.set_value_text(f"{default:.2f}")

        # Connect signal
        self.knob.valueChanged.connect(self.handle_knob_change)

        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.knob)

        # Set layout properties
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def value_to_knob(self, value):
        """Convert actual value to knob position"""
        if self.is_log:
            # Logarithmic scaling for values like frequency
            normalized = (value - self.min_val) / (self.max_val - self.min_val)
            return int(normalized * 1000)
        else:
            # Linear scaling
            normalized = (value - self.min_val) / (self.max_val - self.min_val)
            return int(normalized * 1000)

    def knob_to_value(self, position):
        """Convert knob position to actual value"""
        if self.is_log:
            # Logarithmic scaling
            normalized = position / 1000
            return self.min_val + normalized * (self.max_val - self.min_val)
        else:
            # Linear scaling
            normalized = position / 1000
            return self.min_val + normalized * (self.max_val - self.min_val)

    def handle_knob_change(self, position):
        """Handle knob value change"""
        value = self.knob_to_value(position)
        if self.is_integer:
            self.knob.set_value_text(f"{int(value)}")
        else:
            self.knob.set_value_text(f"{value:.2f}")
        self.valueChanged.emit(value)

    def set_value(self, value):
        """Set knob from outside"""
        position = self.value_to_knob(value)
        self.knob.setValue(position)

    def set_from_midi_cc(self, cc_value):
        """Set from MIDI CC value (0-127)"""
        if self.midi_cc is not None:
            # Convert from 0-127 range to knob range
            normalized = cc_value / 127.0
            value = self.min_val + normalized * (self.max_val - self.min_val)
            self.set_value(value)
            return value
        return None


class WaveformSelector(QWidget):
    """Waveform selector with visual icons and animation"""

    waveformChanged = pyqtSignal(int)

    class WaveVizFrame(QFrame):
        """Inner class for waveform visualization"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMinimumHeight(100)
            self.setFrameShape(QFrame.Shape.Box)
            self.setFrameShadow(QFrame.Shadow.Sunken)
            self.setStyleSheet(
                """
                background-color: #0F0F0F;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
            """
            )
            self.wave_type = 2  # Default sawtooth
            self.offset = 0  # For animation

        def setWaveType(self, wave_type):
            self.wave_type = wave_type
            self.update()

        def animate(self):
            self.offset = (self.offset + 1) % 50  # Cycle through 0-49
            self.update()

        def paintEvent(self, event):
            super().paintEvent(event)

            qp = QPainter(self)
            qp.setRenderHint(QPainter.RenderHint.Antialiasing)

            width = self.width()
            height = self.height()
            middle = height / 2

            # Use a gradient pen for more expressionist look
            gradient = QLinearGradient(0, 0, width, height)
            gradient.setColorAt(0, QColor("#D4BF8A"))
            gradient.setColorAt(1, QColor("#8A7A55"))

            # Draw grid lines for reference
            qp.setPen(QPen(QColor("#2A2A2A"), 1))
            qp.drawLine(0, int(middle), width, int(middle))  # Horizontal center line
            for x in range(0, width, int(width / 8)):  # Vertical grid lines
                qp.drawLine(x, 0, x, height)

            # Switch to gradient pen for waveform
            qp.setPen(QPen(QBrush(gradient), 2))

            # Points to connect with lines instead of individual points
            points = []

            # Animate by shifting start position
            start_x = -self.offset

            if self.wave_type == 0:  # Sine
                # Draw sine wave
                for x in range(start_x, width + 10):
                    if x < 0:
                        continue
                    y = middle - middle * 0.7 * math.sin(
                        (x + self.offset) / width * 4 * math.pi
                    )
                    points.append((x, int(y)))

            elif self.wave_type == 1:  # Triangle
                # Draw triangle wave
                period = width / 2
                for x in range(start_x, width + 10):
                    if x < 0:
                        continue
                    phase = ((x + self.offset) % period) / period
                    if (x + self.offset) % (2 * period) < period:
                        y = middle - middle * 0.7 * (2 * phase - 1)
                    else:
                        y = middle - middle * 0.7 * (1 - 2 * phase)
                    points.append((x, int(y)))

            elif self.wave_type == 2:  # Sawtooth
                # Draw sawtooth wave
                period = width / 2
                for x in range(start_x, width + 10):
                    if x < 0:
                        continue
                    phase = ((x + self.offset) % period) / period
                    y = middle - middle * 0.7 * (2 * phase - 1)
                    points.append((x, int(y)))

            elif self.wave_type == 3:  # Square
                # Draw square wave
                period = width / 2
                for x in range(start_x, width + 10):
                    if x < 0:
                        continue
                    if (x + self.offset) % period < period / 2:
                        y = middle - middle * 0.7
                    else:
                        y = middle + middle * 0.7
                    points.append((x, int(y)))

            # Draw connected lines for smoother look
            if len(points) > 1:
                for i in range(1, len(points)):
                    qp.drawLine(
                        points[i - 1][0], points[i - 1][1], points[i][0], points[i][1]
                    )

    def __init__(self, parent=None, midi_cc=1):
        super().__init__(parent)
        self.midi_cc = midi_cc

        # Main layout
        layout = QVBoxLayout(self)

        # Create label
        self.name_label = QLabel(f"Waveform (CC{midi_cc})")
        self.name_label.setFont(QFont("Futura", 11))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #E6E6E6;")

        # Waveform buttons layout
        wave_buttons_layout = QHBoxLayout()

        # Waveform buttons
        self.wave_buttons = []
        waveforms = [
            ("Sine", "○"),
            ("Triangle", "△"),
            ("Sawtooth", "◸"),
            ("Square", "□"),
        ]

        for i, (name, symbol) in enumerate(waveforms):
            button = QPushButton(symbol)
            button.setToolTip(name)
            button.setMinimumSize(40, 40)
            button.setMaximumSize(40, 40)
            button.setCheckable(True)
            button.setProperty("wave_index", i)
            button.setFont(QFont("Arial", 16))

            # Set sawtooth as default
            if i == 2:  # Sawtooth
                button.setChecked(True)

            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2A2A2A;
                    color: #D4BF8A;
                    border: 1px solid #555555;
                    border-radius: 5px;
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
            )

            button.clicked.connect(self.button_clicked)

            self.wave_buttons.append(button)
            wave_buttons_layout.addWidget(button)

        # Create waveform visualization using custom frame
        self.wave_viz = self.WaveVizFrame()

        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addLayout(wave_buttons_layout)
        layout.addWidget(self.wave_viz)

        # Current waveform index
        self.current_index = 2  # Default to sawtooth
        self.wave_viz.setWaveType(self.current_index)

        # Set layout properties
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Animation for waveform changes
        self._animation_timer = QTimer()
        self._animation_timer.setSingleShot(True)
        self._animation_timer.timeout.connect(self._reset_wave_viz_style)

    def button_clicked(self):
        """Handle button click"""
        button = self.sender()
        wave_index = button.property("wave_index")

        # Uncheck all buttons
        for btn in self.wave_buttons:
            if btn != button:
                btn.setChecked(False)

        # Update current index and emit signal
        self.current_index = wave_index
        self.wave_viz.setWaveType(wave_index)
        self.waveformChanged.emit(wave_index)

        # Update visualization
        self._animate_wave_change()

    def _animate_wave_change(self):
        """Animate waveform change"""
        # Add a flash effect to the wave visualization frame
        self.wave_viz.setStyleSheet(
            """
            background-color: #252525;
            border: 1px solid #D4BF8A;
            border-radius: 4px;
        """
        )
        self._animation_timer.start(300)

    def _reset_wave_viz_style(self):
        """Reset wave viz style after animation"""
        self.wave_viz.setStyleSheet(
            """
            background-color: #0F0F0F;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
        """
        )

    def set_from_midi_cc(self, cc_value):
        """Set waveform from MIDI CC value (0-127)"""
        if self.midi_cc is not None:
            # Map 0-127 to 0-3 range for waveforms
            wave = min(3, int(cc_value / 32))
            self.set_waveform(wave)
            return wave
        return None

    def set_waveform(self, index):
        """Set waveform from outside"""
        if 0 <= index <= 3:
            self.current_index = index

            # Update button states
            for i, button in enumerate(self.wave_buttons):
                button.setChecked(i == index)

            # Update the wave visualization
            self.wave_viz.setWaveType(index)

            # Animation and update
            self._animate_wave_change()
            self.waveformChanged.emit(index)

    def animate_wave(self):
        """Animate the waveform visualization"""
        self.wave_viz.animate()

    def update(self):
        """Update the widget"""
        super().update()
        self.wave_viz.update()


class PianoKeys(QWidget):
    """Piano key widget for playing notes"""

    noteOn = pyqtSignal(float)
    noteOff = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMinimumWidth(500)

        # Expanded keyboard range
        self.notes = [
            261.63,
            277.18,
            293.66,
            311.13,
            329.63,
            349.23,
            369.99,
            392.00,
            415.30,
            440.00,
            466.16,
            493.88,
            523.25,
        ]
        self.note_names = [
            "C4",
            "C#4",
            "D4",
            "D#4",
            "E4",
            "F4",
            "F#4",
            "G4",
            "G#4",
            "A4",
            "A#4",
            "B4",
            "C5",
        ]
        self.is_black_key = [
            False,
            True,
            False,
            True,
            False,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            False,
        ]
        self.active_keys = set()  # Track multiple active keys for polyphonic display
        self.last_midi_note = None

        # Key shadows for expressionist effect
        self.key_shadows = []
        for i in range(len(self.notes)):
            self.key_shadows.append(QColor(10, 10, 10, 100))

        # Set focus policy to enable key press events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        """Draw piano keys with expressionist perspective distortion"""
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # First draw all white keys
        white_keys = [i for i, is_black in enumerate(self.is_black_key) if not is_black]
        white_key_width = width / len(white_keys)

        # Draw white key background
        qp.setBrush(QBrush(QColor("#232323")))
        qp.setPen(Qt.PenStyle.NoPen)
        qp.drawRect(0, 0, width, height)

        # Draw each white key
        white_key_index = 0
        for i in range(len(self.notes)):
            if not self.is_black_key[i]:
                # Set color based on active state
                if i in self.active_keys:
                    # Gold gradient for active keys
                    gradient = QLinearGradient(0, 0, 0, height)
                    gradient.setColorAt(0, QColor("#D4BF8A"))
                    gradient.setColorAt(1, QColor("#8A7A55"))
                    qp.setBrush(QBrush(gradient))
                else:
                    # Ivory gradient for inactive keys
                    gradient = QLinearGradient(0, 0, 0, height)
                    gradient.setColorAt(0, QColor("#E6E6E6"))
                    gradient.setColorAt(1, QColor("#BBBBBB"))
                    qp.setBrush(QBrush(gradient))

                # Draw key with slight perspective distortion
                x = int(white_key_index * white_key_width)
                y = 0
                w = int(white_key_width - 1)

                # Draw shadow first
                shadow_color = QColor(0, 0, 0, 50)
                qp.setPen(Qt.PenStyle.NoPen)
                qp.setBrush(QBrush(shadow_color))
                shadow_offset = 3
                qp.drawRect(x + shadow_offset, y + shadow_offset, w, height)

                # Draw key
                qp.setPen(QPen(QColor("#555555"), 1))
                if i in self.active_keys:
                    qp.setBrush(QBrush(gradient))
                else:
                    qp.setBrush(QBrush(gradient))
                qp.drawRect(x, y, w, height)

                # Draw note name
                if i in self.active_keys:
                    qp.setPen(QPen(QColor("#FFFFFF"), 1))
                else:
                    qp.setPen(QPen(QColor("#333333"), 1))
                qp.setFont(QFont("Futura", 9, QFont.Weight.Bold))
                qp.drawText(int(x + 5), height - 8, self.note_names[i])

                white_key_index += 1

        # Then draw all black keys on top
        for i in range(len(self.notes)):
            if self.is_black_key[i]:
                # Find the white keys before and after
                prev_white = -1
                next_white = -1

                for j in range(i - 1, -1, -1):
                    if not self.is_black_key[j]:
                        prev_white = j
                        break

                for j in range(i + 1, len(self.notes)):
                    if not self.is_black_key[j]:
                        next_white = j
                        break

                if prev_white >= 0 and next_white >= 0:
                    # Calculate position based on surrounding white keys
                    prev_index = white_keys.index(prev_white)

                    x = int((prev_index + 0.7) * white_key_width)
                    y = 0
                    w = int(white_key_width * 0.6)
                    h = int(height * 0.65)

                    # Set color based on active state
                    if i in self.active_keys:
                        gradient = QLinearGradient(0, 0, 0, h)
                        gradient.setColorAt(0, QColor("#8A7A55"))
                        gradient.setColorAt(1, QColor("#5D5236"))
                        qp.setBrush(QBrush(gradient))
                    else:
                        gradient = QLinearGradient(0, 0, 0, h)
                        gradient.setColorAt(0, QColor("#222222"))
                        gradient.setColorAt(1, QColor("#111111"))
                        qp.setBrush(QBrush(gradient))

                    # Draw shadow
                    shadow_color = QColor(0, 0, 0, 70)
                    qp.setPen(Qt.PenStyle.NoPen)
                    qp.setBrush(QBrush(shadow_color))
                    shadow_offset = 2
                    qp.drawRect(x + shadow_offset, y + shadow_offset, w, h)

                    # Draw key
                    qp.setPen(QPen(QColor("#444444"), 1))
                    qp.setBrush(QBrush(gradient))
                    qp.drawRect(x, y, w, h)

    def mousePressEvent(self, event):
        """Handle mouse press to play note"""
        self._handle_mouse_position(event.position().x(), event.position().y(), True)

    def mouseMoveEvent(self, event):
        """Handle mouse drag over keys"""
        # Only process if mouse button is pressed
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse_position(
                event.position().x(), event.position().y(), True
            )

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop note"""
        self.active_keys.clear()
        self.noteOff.emit()
        self.update()

    def _handle_mouse_position(self, x, y, trigger_note=True):
        """Process mouse position and determine which key is activated"""
        width = self.width()
        height = self.height()

        # First check black keys (they're on top)
        white_keys = [i for i, is_black in enumerate(self.is_black_key) if not is_black]
        white_key_width = width / len(white_keys)

        # Check black keys first (they're on top)
        for i in range(len(self.notes)):
            if self.is_black_key[i]:
                # Find surrounding white keys
                prev_white = -1
                for j in range(i - 1, -1, -1):
                    if not self.is_black_key[j]:
                        prev_white = j
                        break

                if prev_white >= 0:
                    prev_index = white_keys.index(prev_white)
                    black_key_x = int((prev_index + 0.7) * white_key_width)
                    black_key_width = int(white_key_width * 0.6)
                    black_key_height = int(height * 0.65)

                    if (
                        x >= black_key_x
                        and x < black_key_x + black_key_width
                        and y < black_key_height
                    ):
                        if i not in self.active_keys and trigger_note:
                            self.active_keys.add(i)
                            self.noteOn.emit(self.notes[i])
                        self.update()
                        return

        # If no black key was clicked, check white keys
        white_key_index = 0
        for i in range(len(self.notes)):
            if not self.is_black_key[i]:
                key_x = int(white_key_index * white_key_width)
                if x >= key_x and x < key_x + white_key_width:
                    if i not in self.active_keys and trigger_note:
                        self.active_keys.add(i)
                        self.noteOn.emit(self.notes[i])
                    self.update()
                    return
                white_key_index += 1

    def keyPressEvent(self, event):
        """Handle keyboard input for notes"""
        key_mapping = {
            Qt.Key.Key_Z: 0,  # C4
            Qt.Key.Key_S: 1,  # C#4
            Qt.Key.Key_X: 2,  # D4
            Qt.Key.Key_D: 3,  # D#4
            Qt.Key.Key_C: 4,  # E4
            Qt.Key.Key_V: 5,  # F4
            Qt.Key.Key_G: 6,  # F#4
            Qt.Key.Key_B: 7,  # G4
            Qt.Key.Key_H: 8,  # G#4
            Qt.Key.Key_N: 9,  # A4
            Qt.Key.Key_J: 10,  # A#4
            Qt.Key.Key_M: 11,  # B4
            Qt.Key.Key_Comma: 12,  # C5
        }

        # Prevent key repeat events
        if event.isAutoRepeat():
            return

        if event.key() in key_mapping:
            note_idx = key_mapping[event.key()]
            if note_idx not in self.active_keys:
                self.active_keys.add(note_idx)
                self.noteOn.emit(self.notes[note_idx])
                self.update()

    def keyReleaseEvent(self, event):
        """Handle keyboard release for notes"""
        # Prevent key repeat events
        if event.isAutoRepeat():
            return

        key_mapping = {
            Qt.Key.Key_Z: 0,  # C4
            Qt.Key.Key_S: 1,  # C#4
            Qt.Key.Key_X: 2,  # D4
            Qt.Key.Key_D: 3,  # D#4
            Qt.Key.Key_C: 4,  # E4
            Qt.Key.Key_V: 5,  # F4
            Qt.Key.Key_G: 6,  # F#4
            Qt.Key.Key_B: 7,  # G4
            Qt.Key.Key_H: 8,  # G#4
            Qt.Key.Key_N: 9,  # A4
            Qt.Key.Key_J: 10,  # A#4
            Qt.Key.Key_M: 11,  # B4
            Qt.Key.Key_Comma: 12,  # C5
        }

        if event.key() in key_mapping:
            note_idx = key_mapping[event.key()]
            if note_idx in self.active_keys:
                self.active_keys.remove(note_idx)

                # Only emit noteOff if all keys are released
                if not self.active_keys:
                    self.noteOff.emit()
                # Otherwise, play the last pressed note
                else:
                    self.noteOn.emit(self.notes[max(self.active_keys)])

                self.update()

    def handle_midi_note_on(self, note, velocity):
        """Handle MIDI note on event"""
        # Convert MIDI note number to our note array
        note_idx = note - 60  # MIDI note 60 = C4

        if 0 <= note_idx < len(self.notes):
            self.active_keys.add(note_idx)
            self.last_midi_note = note_idx
            self.update()
            return True
        return False

    def handle_midi_note_off(self, note):
        """Handle MIDI note off event"""
        note_idx = note - 60  # MIDI note 60 = C4

        if note_idx in self.active_keys:
            self.active_keys.remove(note_idx)
            if note_idx == self.last_midi_note:
                self.last_midi_note = (
                    None if not self.active_keys else max(self.active_keys)
                )
            self.update()
            return True
        return False
