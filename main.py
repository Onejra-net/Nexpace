"""Nexpace application entry point.

The UI implementation lives in thematic modules under ``nexpace``.
"""
import os
import sys

# Match the original Nexpace WebEngine runtime configuration.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-webgpu"

from PySide6.QtWidgets import QApplication

from nexpace.main_window import MainWindow


def main():
    """Create and run the Nexpace desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Nexpace")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
