from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..localization import tr
from ..web_engine import DebugWebEnginePage


class PdfWebView(QWebEngineView):
    """QWebEngineView configured specifically for PDF.js."""

    VIEWER_URL = (
        "https://mozilla.github.io/"
        "pdf.js/legacy/web/viewer.html"
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pdfjs_page = DebugWebEnginePage(self)
        self.setPage(self.pdfjs_page)

        self.setStyleSheet(
            "QWebEngineView { border: none; }"
        )

        settings = self.settings()

        settings.setAttribute(
            QWebEngineSettings.WebAttribute
            .LocalContentCanAccessRemoteUrls,
            True,
        )

        settings.setAttribute(
            QWebEngineSettings.WebAttribute
            .LocalContentCanAccessFileUrls,
            True,
        )

        self.setHtml(
            self.empty_html()
        )

    @staticmethod
    def empty_html():
        """Return the HTML shown before a PDF is opened."""
        return f"""
        <html>
        <body style='
            background-color:#1e1e1e;
            color:#888888;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            margin:0;
            font-family:
                system-ui,
                -apple-system,
                sans-serif;
        '>
            <div style='text-align:center;'>
                <h2 style='
                    color:#aaaaaa;
                    font-weight:normal;
                '>
                    {tr("no_document_open")}
                </h2>

                <p style='font-size:14px;'>
                    {tr("use_file_open_pdf_to_start")}
                </p>
            </div>
        </body>
        </html>
        """

    def is_viewer_url(self):
        """Return True if PDF.js is currently loaded."""
        return (
            self.url().toString()
            == self.VIEWER_URL
        )

    def load_viewer(self):
        """Navigate to the PDF.js viewer."""
        self.setUrl(
            QUrl(self.VIEWER_URL)
        )