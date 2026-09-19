from PySide6.QtCore import QObject, Signal


class PdfNavigation(QObject):
    """Track the current PDF.js page."""

    pageChanged = Signal(int)

    def __init__(
        self,
        web_view,
        status_label,
        translator,
        get_file_name,
    ):
        super().__init__(web_view)

        self.web_view = web_view
        self.status_label = status_label
        self.tr = translator
        self.get_file_name = get_file_name

        self._current_page = 0
        self._page_count = 0

        self.web_view.titleChanged.connect(
            self._on_title_changed
        )

    def reset(self):
        """Reset page tracking for a newly opened document."""
        
        self._current_page = 0
        self._page_count = 0

    def current_page(self):
        """Return the current page as a zero-based index."""
        
        return self._current_page

    def _on_title_changed(self, title):
        """
        Receive page information from the JavaScript bridge.

        PDF.js reports page information through document.title
        using the format:

            QTPDF_PAGE:<page>:<total>
        """
        
        if not title.startswith("QTPDF_PAGE:"):
            return

        parts = title.split(":")

        if len(parts) < 3:
            return

        try:
            page_num = int(parts[1])
            total_pages = int(parts[2])
        except ValueError:
            return

        page_index = max(
            0,
            page_num - 1,
        )

        if (
            page_index == self._current_page
            and total_pages == self._page_count
        ):
            return

        self._current_page = page_index
        self._page_count = total_pages

        self.status_label.setText(
            self.tr(
                "pdf.page_count",
                pdf_name=self.get_file_name(),
                page_num=page_num,
                total_pages=total_pages,
            )
        )

        self.pageChanged.emit(page_index)