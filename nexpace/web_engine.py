"""
Shared Qt WebEngine primitives.

This module contains the common WebEngine page subclass used by the PDF,
browser, and notes panels.
"""
from PySide6.QtWebEngineCore import QWebEnginePage


class DebugWebEnginePage(QWebEnginePage):
    """Forward JavaScript console messages to the Python terminal for debugging."""
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        print(f"[JS CONSOLE] L{line_number}: {message}")
