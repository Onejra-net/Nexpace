"""
Quill editor content and statistics tracking.

Responsible for:
- Receiving HTML updates from the JavaScript bridge
- Maintaining a local cache of editor content
- Tracking character and word counts
- Updating the editor status bar
- Notifying other components of content and statistics changes
"""

import urllib.parse

from PySide6.QtCore import QObject, Signal


class NotesNavigation(QObject):
    """
    Coordinator for Quill editor state tracking.

    Processes HTML and statistics updates received through
    WebEngine events and synchronizes them with the application.
    """

    # Editor change signals:
    # - HTML content updates
    # - Character and word count updates
    htmlChanged = Signal(str)
    statsChanged = Signal(int, int)

    def __init__(
        self,
        web_view,
        status_bar,
        translator,
    ):
        super().__init__(web_view)

        # Editor navigation dependencies:
        self.web_view = web_view
        self.status_bar = status_bar
        self.tr = translator

        # Cached editor content:
        self._cached_html = ""

        # HTML content bridge:
        # - Receive encoded HTML through document.title changes.
        self.web_view.titleChanged.connect(
            self._on_title_changed
        )

        # Editor statistics bridge:
        # - Receive character and word counts through URL fragments.
        self.web_view.urlChanged.connect(
            self._on_url_changed
        )

    def cached_html(self):
        """
        Return the latest cached HTML received from Quill.
        """

        return self._cached_html

    def reset(self):
        """
        Clear the cached editor HTML.
        """

        self._cached_html = ""

    def _on_title_changed(self, title):
        """
        Process HTML updates received through document.title.

        Expected JavaScript bridge format:
            QUILL_HTML_URI:<encoded_html>
        """

        # Ignore unrelated document title changes:
        if not title.startswith("QUILL_HTML_URI:"):
            return

        try:
            # Extract the encoded HTML payload:
            uri_str = title.split(":", 1)[1]

            # Handle empty editor content:
            if uri_str == "EMPTY":
                self._cached_html = ""

            # Decode and cache the HTML content:
            else:
                self._cached_html = (
                    urllib.parse.unquote(uri_str)
                )

            # Notify other components of the HTML update:
            self.htmlChanged.emit(
                self._cached_html
            )

        # Report HTML decoding errors:
        except Exception as exc:
            print(
                self.tr(
                    "python_uri_decode_error",
                    e=exc,
                )
            )

    def _on_url_changed(self, url):
        """
        Process editor statistics received through URL fragments.

        Expected JavaScript bridge format:
            #stats:<characters>:<words>
        """

        # Extract statistics from the URL fragment:
        fragment = url.fragment()

        # Ignore unrelated URL changes:
        if not fragment.startswith("stats:"):
            return

        try:
            # Parse character and word counts:
            parts = fragment.split(":")

            if len(parts) < 3:
                return

            chars = int(parts[1])
            words = int(parts[2])

            # Update the editor statistics display:
            self.status_bar.setText(
                self.tr(
                    "notes.counter",
                    chars=chars,
                    words=words,
                )
            )

            # Notify other components of statistics changes:
            self.statsChanged.emit(
                chars,
                words,
            )

        # Ignore malformed statistics data:
        except (ValueError, TypeError):
            pass
