"""
Browser navigation and state management.

Responsible for:
- Connecting toolbar controls to browser navigation
- Opening URLs in the embedded browser
- Synchronizing the displayed URL
- Updating back and forward button availability
"""

from PySide6.QtCore import QUrl


class BrowserNavigation:
    """
    Coordinator for browser navigation.

    Connects toolbar actions to WebEngine navigation
    and synchronizes navigation state with the interface.
    """

    def __init__(self, web_view, toolbar):

        # Browser component references:
        self.web_view = web_view
        self.toolbar = toolbar

        # Toolbar navigation actions:
        # - Back, forward, and reload
        self.toolbar.btn_back.clicked.connect(
            self.web_view.back
        )

        self.toolbar.btn_forward.clicked.connect(
            self.web_view.forward
        )

        self.toolbar.btn_refresh.clicked.connect(
            self.web_view.reload
        )

        # Browser URL change tracking:
        self.web_view.urlChanged.connect(
            self._on_url_changed
        )

        # Initialize navigation button states:
        self.update_buttons()

    def _on_url_changed(self, url):
        """
        Synchronize the URL display and navigation controls.
        """

        # Update the displayed browser URL:
        self.toolbar.url_bar.setText(
            url.toString()
        )

        # Refresh navigation button availability:
        self.update_buttons()

    def update_buttons(self, *_args):
        """
        Update navigation controls based on browser history.
        """

        # Access the browser navigation history:
        history = self.web_view.history()

        # Enable navigation only when history entries are available:
        self.toolbar.btn_back.setEnabled(
            history.canGoBack()
        )

        self.toolbar.btn_forward.setEnabled(
            history.canGoForward()
        )

    def open(self, url_str):
        """
        Navigate the browser to the specified URL.
        """

        # Load the requested URL:
        self.web_view.setUrl(
            QUrl(url_str)
        )
