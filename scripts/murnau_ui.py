#!/usr/bin/env python3
"""Entry point for Murnau UI application"""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtGui import QIcon, QPixmap  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from src.murnau.ui import MurnauUI  # noqa: E402


def main():
    """Main entry point for Murnau UI"""
    # Allow custom synth name and OSC port
    synth_name = "legato_synth_stereo"
    osc_port = 5510

    if len(sys.argv) > 1:
        synth_name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            osc_port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid OSC port: {sys.argv[2]}. Using default 5510.")

    # Create QApplication with custom style
    app = QApplication(sys.argv)

    # Show app icon
    try:
        app_icon = QPixmap("assets/images/Murnau-App.png")
        if not app_icon.isNull():
            app.setWindowIcon(QIcon(app_icon))
    except Exception as e:
        print(f"Could not load app icon: {e}")

    # Create and display our window
    window = MurnauUI()
    window.synth_name = synth_name
    window.osc_port = osc_port

    # Apply expressionist style darkening effect to the app
    app.setStyle("Fusion")

    # Exit when app is closed
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
