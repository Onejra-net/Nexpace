from PySide6.QtCore import QUrl


class BrowserNavigation:
    """Coordinates browser navigation actions and navigation state."""

    def __init__(self, web_view, toolbar):
        self.web_view = web_view
        self.toolbar = toolbar

        self.toolbar.btn_back.clicked.connect(
            self.web_view.back
        )

        self.toolbar.btn_forward.clicked.connect(
            self.web_view.forward
        )

        self.toolbar.btn_refresh.clicked.connect(
            self.web_view.reload
        )

        self.web_view.urlChanged.connect(
            self._on_url_changed
        )

        self.update_buttons()

    def _on_url_changed(self, url):
        """Update URL display and navigation buttons."""
        
        self.toolbar.url_bar.setText(
            url.toString()
        )

        self.update_buttons()

    def update_buttons(self, *_args):
        """Enable or disable back/forward buttons."""
        
        history = self.web_view.history()

        self.toolbar.btn_back.setEnabled(
            history.canGoBack()
        )

        self.toolbar.btn_forward.setEnabled(
            history.canGoForward()
        )

    def open(self, url_str):
        """Open the given URL."""
        
        self.web_view.setUrl(
            QUrl(url_str)
        )