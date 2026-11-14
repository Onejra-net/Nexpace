"""
PDF.js web view configuration.

Responsible for:
- Configuring the embedded Qt WebEngine view
- Setting web content access permissions
- Displaying the initial empty document screen
- Loading the external PDF.js viewer
"""

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..localization import tr
from ..web_engine import DebugWebEnginePage


class PdfWebView(QWebEngineView):
    """
    WebEngine view configured for PDF.js.

    Manages the browser environment used to display
    PDF documents within window.
    """

    # External PDF.js viewer location:
    VIEWER_URL = (
        "https://mozilla.github.io/"
        "pdf.js/legacy/web/viewer.html"
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        # WebEngine page initialization:
        self.pdfjs_page = DebugWebEnginePage(self)
        self.setPage(self.pdfjs_page)

        # Web view appearance:
        self.setStyleSheet(
            "QWebEngineView { border: none; }"
        )

        # WebEngine content access settings:
        settings = self.settings()

        # Allow locally loaded content to access remote URLs:
        settings.setAttribute(
            QWebEngineSettings.WebAttribute
            .LocalContentCanAccessRemoteUrls,
            True,
        )

        # Allow locally loaded content to access file URLs:
        settings.setAttribute(
            QWebEngineSettings.WebAttribute
            .LocalContentCanAccessFileUrls,
            True,
        )

        # Display the initial empty document screen:
        self.setHtml(
            self.empty_html()
        )

    @staticmethod
    def empty_html():
        """
        Generate the localized placeholder shown without an open PDF.
        """

        # Initial placeholder HTML:
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
        """
        Check whether the web view URL matches the PDF.js viewer.
        """

        return (
            self.url().toString()
            == self.VIEWER_URL
        )

    def load_viewer(self):
        """
        Navigate to the configured PDF.js viewer URL.
        """

        self.setUrl(
            QUrl(self.VIEWER_URL)
        )
