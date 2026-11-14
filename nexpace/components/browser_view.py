
"""
Browser WebEngine view configuration.

Responsible for:
- Initializing the embedded browser view
- Configuring the custom WebEngine page
"""

from PySide6.QtWebEngineWidgets import QWebEngineView

from ..web_engine import DebugWebEnginePage


class BrowserWebView(QWebEngineView):
    """
    WebEngine view configured for the browser.

    Uses DebugWebEnginePage to handle browser page behavior.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Custom WebEngine page initialization:
        self.web_page = DebugWebEnginePage(self)
        self.setPage(self.web_page)
