"""
PDF.js page navigation and state tracking.

Responsible for:
- Tracking the current PDF page and total page count
- Receiving page information from the JavaScript bridge
- Updating the document status label
- Notifying other components of page changes
"""

from PySide6.QtCore import QObject, Signal


class PdfNavigation(QObject):
    """
    Coordinator for PDF page tracking.

    Processes page information received from PDF.js
    and synchronizes navigation state with the application.
    """

    # PDF page change signal:
    # - Emits the current zero-based page index.
    pageChanged = Signal(int)

    def __init__(
        self,
        web_view,
        status_label,
        translator,
        get_file_name,
    ):
        super().__init__(web_view)

        # PDF navigation dependencies:
        self.web_view = web_view
        self.status_label = status_label
        self.tr = translator
        self.get_file_name = get_file_name

        # PDF page state:
        self._current_page = 0
        self._page_count = 0

        # JavaScript bridge event:
        # - Monitor document title changes for page information.
        self.web_view.titleChanged.connect(
            self._on_title_changed
        )

    def reset(self):
        """
        Reset page tracking for a newly opened PDF document.
        """

        # Reset navigation state:
        self._current_page = 0
        self._page_count = 0

    def current_page(self):
        """
        Return the current PDF page as a zero-based index.
        """

        return self._current_page

    def _on_title_changed(self, title):
        """
        Process PDF page information received through document.title.

        Expected JavaScript bridge format:
            QTPDF_PAGE:<page>:<total>
        """

        # Ignore unrelated document title changes:
        if not title.startswith("QTPDF_PAGE:"):
            return

        # Extract page information:
        parts = title.split(":")

        if len(parts) < 3:
            return

        # Validate page and total page values:
        try:
            page_num = int(parts[1])
            total_pages = int(parts[2])
        except ValueError:
            return

        # Convert the page number to a zero-based index:
        page_index = max(
            0,
            page_num - 1,
        )

        # Ignore unchanged navigation state:
        if (
            page_index == self._current_page
            and total_pages == self._page_count
        ):
            return

        # Update the current PDF navigation state:
        self._current_page = page_index
        self._page_count = total_pages

        # Refresh the document status label:
        self.status_label.setText(
            self.tr(
                "pdf.page_count",
                pdf_name=self.get_file_name(),
                page_num=page_num,
                total_pages=total_pages,
            )
        )

        # Notify other components of the page change:
        self.pageChanged.emit(page_index)
