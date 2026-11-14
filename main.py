"""
Nexpace application entry point.

Initializes the Qt runtime and launches the main application window.
The UI and application logic are organized within the `nexpace` package.
"""

import os
import sys

# Qt WebEngine:
# - Disable WebGPU to mitigate potential rendering compatibility issues.
# - Apply before importing Qt WebEngine-dependent components.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-webgpu"
from PySide6.QtWidgets import QApplication

from nexpace.main_window import MainWindow



def main():
    # Application setup:
    app = QApplication(sys.argv)
    app.setApplicationName("Nexpace")

    # Main interface:
    window = MainWindow()
    window.show()

    # Application event loop:
    sys.exit(app.exec())


if __name__ == "__main__":
    main()