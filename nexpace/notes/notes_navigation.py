import urllib.parse

from PySide6.QtCore import QObject, Signal



class NotesNavigation(QObject):
    """Track Quill document changes and notes statistics."""

    htmlChanged = Signal(str)
    statsChanged = Signal(int, int)

    def __init__(
        self,
        web_view,
        status_bar,
        translator,
    ):
        super().__init__(web_view)

        self.web_view = web_view
        self.status_bar = status_bar
        self.tr = translator

        self._cached_html = ""

        self.web_view.titleChanged.connect(
            self._on_title_changed
        )

        self.web_view.urlChanged.connect(
            self._on_url_changed
        )

    def cached_html(self):
        """Return the last HTML received from Quill."""
        
        return self._cached_html

    def reset(self):
        """Clear the cached HTML."""
        
        self._cached_html = ""

    def _on_title_changed(self, title):
        """Handle HTML updates reported through document.title."""
        
        if not title.startswith("QUILL_HTML_URI:"):
            return

        try:
            uri_str = title.split(":", 1)[1]

            if uri_str == "EMPTY":
                self._cached_html = ""
            else:
                self._cached_html = (
                    urllib.parse.unquote(uri_str)
                )

            self.htmlChanged.emit(
                self._cached_html
            )

        except Exception as exc:
            print(
                self.tr(
                    "python_uri_decode_error",
                    e=exc,
                )
            )

    def _on_url_changed(self, url):
        """Handle character and word count updates."""
        
        fragment = url.fragment()

        if not fragment.startswith("stats:"):
            return

        try:
            parts = fragment.split(":")

            if len(parts) < 3:
                return

            chars = int(parts[1])
            words = int(parts[2])

            self.status_bar.setText(
                self.tr(
                    "notes.counter",
                    chars=chars,
                    words=words,
                )
            )

            self.statsChanged.emit(
                chars,
                words,
            )

        except (ValueError, TypeError):
            pass