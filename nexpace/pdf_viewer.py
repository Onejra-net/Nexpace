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
    """Facade/coordinator for the PDF viewer."""

    pageChanged = Signal(int)
    fileChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_path = None
        self._pdfjs_ready = False
        self._pending_pdf_data = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.pdfjs_view = PdfWebView(self)
        layout.addWidget(self.pdfjs_view, 1)

        self.status_label = QLabel(tr("no_pdf_open"))
        self.status_label.setContentsMargins(6, 2, 6, 2)
        self.status_label.setMinimumHeight(24)
        self.status_label.setMaximumHeight(28)
        layout.addWidget(self.status_label)

        self.document_loader = PdfDocumentLoader()

        self.scripts = PdfScriptManager(self.pdfjs_view)

        self.navigation = PdfNavigation(
            self.pdfjs_view,
            self.status_label,
            tr,
            self._current_file_name,
        )

        self.navigation.pageChanged.connect(
            self.pageChanged.emit
        )

        self.pdfjs_view.loadFinished.connect(
            self._viewer_loaded
        )

        self.pdfjs_view.urlChanged.connect(
            lambda _url: self._check_viewer_ready()
        )

    def _current_file_name(self):
        """Return the currently opened PDF file name."""
        
        return (
            self.file_path.name
            if self.file_path
            else "PDF"
        )

    def open_dialog(self):
        """Open a file selection dialog for PDF files."""
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("open_pdf_alt"),
            "",
            "PDF (*.pdf)",
        )

        if path:
            return self.open_file(path)

        return False

    def _viewer_loaded(self, ok):
        """Handle PDF.js viewer loading."""
        
        if not self.pdfjs_view.is_viewer_url():
            return

        self._pdfjs_ready = False

        if ok:
            QTimer.singleShot(
                100,
                self._check_viewer_ready,
            )

            self.scripts.inject_dark_scrollbar()

    def _check_viewer_ready(self):
        """Check whether PDF.js is ready to receive a document."""
        
        self.scripts.check_viewer_ready(
            self._viewer_ready_result
        )

    def _viewer_ready_result(self, ready):
        """Handle the result of the PDF.js readiness check."""
        
        if not ready:
            return

        self._pdfjs_ready = True

        self.scripts.install_page_event_hook()
        self.scripts.inject_dark_scrollbar()

        if self._pending_pdf_data is not None:
            data = self._pending_pdf_data
            self._pending_pdf_data = None

            self.scripts.open_bytes_in_viewer(data)

    def open_file(self, path):
        """Open a PDF file."""
        
        try:
            data = self.document_loader.read_bytes(path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("pdf_error"),
                tr("pdf.read_error", exc=exc),
            )
            return False

        self.file_path = Path(path)

        self.navigation.reset()

        if (
            not self._pdfjs_ready
            and not self.pdfjs_view.is_viewer_url()
        ):
            self._pending_pdf_data = data
            self.pdfjs_view.load_viewer()

        elif self._pdfjs_ready:
            self.scripts.open_bytes_in_viewer(data)

        else:
            self._pending_pdf_data = data

        self.status_label.setText(
            tr(
                "pdf.loading",
                pdf_name=self.file_path.name,
            )
        )

        self.fileChanged.emit(
            str(self.file_path)
        )

        return True

    @property
    def _page_count(self):
        return self.navigation._page_count

    @property
    def _current_page(self):
        return self.navigation._current_page

    def current_page(self):
        """Return the current PDF page as zero-based index."""
        
        return self.navigation.current_page()