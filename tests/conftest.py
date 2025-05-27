"""Pytest configuration for Murnau tests"""

import os
import sys
import pytest


def pytest_configure(config):
    """Configure pytest for headless testing"""
    # Set QT_QPA_PLATFORM for headless testing if not already set
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    # Disable Qt logging in tests
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle PyQt6 import issues"""
    # Check if PyQt6 is available and working
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer

        # Try to create a QApplication to test if display is available
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        pyqt_available = True
    except (ImportError, RuntimeError) as e:
        pyqt_available = False
        print(f"PyQt6 not available for testing: {e}")

    # Mark PyQt6 tests to skip if PyQt6 is not available
    skip_pyqt = pytest.mark.skip(reason="PyQt6 not available or no display")

    for item in items:
        # Skip tests that require PyQt6 if it's not available
        if not pyqt_available:
            if "main_window" in item.nodeid or "widgets" in item.nodeid:
                item.add_marker(skip_pyqt)


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create a QApplication instance for tests that need it"""
    try:
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        # Don't quit the app here as it might be needed by other tests
    except ImportError:
        # If PyQt6 is not available, yield None
        yield None
