"""
PDF.js viewer panel.

Responsible for:
- Assembling the PDF viewer interface
- Coordinating document loading and navigation
- Managing PDF.js initialization and readiness
- Handling JavaScript interactions
- Exposing PDF file and page change events
"""

from pathlib import Path

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from .localization import tr
from .viewer.pdf_document import PdfDocumentLoader
from .viewer.pdf_navigation import PdfNavigation
from .viewer.pdf_scripts import PdfScriptManager
from .viewer.pdf_web_view import PdfWebView


class PdfViewerPanel(QWidget):
    """
    Main PDF viewer container.

    Integrates the PDF.js web view, document loader,
    navigation, and JavaScript management components.
    """

    # PDF viewer signals:
    # - Notify other components of page and document changes.
    pageChanged = Signal(int)
    fileChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # PDF document and viewer state:
        # - Current file path
        # - PDF.js readiness
        # - Document data awaiting viewer initialization
        self.file_path = None
        self._pdfjs_ready = False
        self._pending_pdf_data = None

        # Main viewer layout:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # PDF.js web view:
        self.pdfjs_view = PdfWebView(self)
        layout.addWidget(self.pdfjs_view, 1)

        # Document status bar:
        self.status_label = QLabel(tr("no_pdf_open"))
        self.status_label.setContentsMargins(6, 2, 6, 2)
        self.status_label.setMinimumHeight(24)
        self.status_label.setMaximumHeight(28)
        layout.addWidget(self.status_label)

        # PDF document loading:
        self.document_loader = PdfDocumentLoader()

        # JavaScript interaction management:
        self.scripts = PdfScriptManager(self.pdfjs_view)

        # PDF navigation and status updates:
        self.navigation = PdfNavigation(
            self.pdfjs_view,
            self.status_label,
            tr,
            self._current_file_name,
        )

        # Forward PDF page change events:
        self.navigation.pageChanged.connect(
            self.pageChanged.emit
        )

        # Monitor PDF.js viewer loading:
        self.pdfjs_view.loadFinished.connect(
            self._viewer_loaded
        )

        # Check viewer readiness after URL changes:
        self.pdfjs_view.urlChanged.connect(
            lambda _url: self._check_viewer_ready()
        )

    def _current_file_name(self):
        """
        Return the currently opened PDF file name.
        """

        return (
            self.file_path.name
            if self.file_path
            else "PDF"
        )

    def open_dialog(self):
        """
        Select and open a PDF document through a file dialog.
        """

        # PDF file selection:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("open_pdf_alt"),
            "",
            "PDF (*.pdf)",
        )

        # Open the selected document:
        if path:
            return self.open_file(path)

        return False

    def _viewer_loaded(self, ok):
        """
        Handle PDF.js viewer loading and schedule readiness checks.
        """

        # Ignore pages outside the PDF.js viewer:
        if not self.pdfjs_view.is_viewer_url():
            return

        # Reset viewer readiness:
        self._pdfjs_ready = False

        # Initialize scripts after successful viewer loading:
        if ok:
            QTimer.singleShot(
                100,
                self._check_viewer_ready,
            )

            self.scripts.inject_dark_scrollbar()

    def _check_viewer_ready(self):
        """Request a PDF.js readiness check through the script manager."""

        # Check whether the viewer can receive a document:
        self.scripts.check_viewer_ready(
            self._viewer_ready_result
        )

    def _viewer_ready_result(self, ready):
        """
        Initialize PDF.js integrations once the viewer is ready.
        """

        # Ignore unsuccessful readiness checks:
        if not ready:
            return

        # Mark the viewer as ready:
        self._pdfjs_ready = True

        # Initialize page event handling and scrollbar styling:
        self.scripts.install_page_event_hook()
        self.scripts.inject_dark_scrollbar()

        # Open a document queued during viewer initialization:
        if self._pending_pdf_data is not None:
            data = self._pending_pdf_data
            self._pending_pdf_data = None

            self.scripts.open_bytes_in_viewer(data)

    def open_file(self, path):
        """
        Read a PDF document and open or queue it in the PDF.js viewer.
        """

        # Read the selected PDF document:
        try:
            data = self.document_loader.read_bytes(path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("pdf_error"),
                tr("pdf.read_error", exc=exc),
            )
            return False

        # Register the active document:
        self.file_path = Path(path)

        # Reset PDF navigation state:
        self.navigation.reset()

        # Initialize PDF.js if the viewer has not been loaded:
        if (
            not self._pdfjs_ready
            and not self.pdfjs_view.is_viewer_url()
        ):
            self._pending_pdf_data = data
            self.pdfjs_view.load_viewer()

        # Open the PDF immediately if PDF.js is ready:
        elif self._pdfjs_ready:
            self.scripts.open_bytes_in_viewer(data)

        # Queue the PDF while waiting for viewer readiness:
        else:
            self._pending_pdf_data = data

        # Update the document loading status:
        self.status_label.setText(
            tr(
                "pdf.loading",
                pdf_name=self.file_path.name,
            )
        )

        # Notify other components of the selected PDF:
        self.fileChanged.emit(
            str(self.file_path)
        )

        return True

    @property
    def _page_count(self):
        """
        Expose the page count maintained by PdfNavigation.
        """
        return self.navigation._page_count

    @property
    def _current_page(self):
        """
        Expose the current page index maintained by PdfNavigation.
        """
        return self.navigation._current_page

    def current_page(self):
        """
        Return the current PDF page as a zero-based index.
        """

        return self.navigation.current_page()
