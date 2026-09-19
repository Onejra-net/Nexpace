from PySide6.QtWebEngineWidgets import QWebEngineView

from ..web_engine import DebugWebEnginePage


class BrowserWebView(QWebEngineView):
    """QWebEngineView configured with Nexpace's debug web page."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.web_page = DebugWebEnginePage(self)
        self.setPage(self.web_page)