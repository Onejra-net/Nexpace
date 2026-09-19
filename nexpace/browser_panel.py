from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from .components.browser_toolbar import BrowserToolbar
from .components.browser_view import BrowserWebView
from .components.browser_navigation import BrowserNavigation
from .components.browser_scripts import BrowserScriptManager
from .components.browser_context_menu import BrowserContextMenu


class BrowserTabPanel(QWidget):
    """Main browser panel facade."""

    def __init__(self, url_str, main_window=None, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        self.toolbar = BrowserToolbar(self)
        self.web_view = BrowserWebView(self)

        self.navigation = BrowserNavigation(
            self.web_view,
            self.toolbar,
        )

        self.scripts = BrowserScriptManager(
            self.web_view.page()
        )

        self.context_menu = BrowserContextMenu(
            self,
            main_window,
        )

        # Compatibility with the old BrowserTabPanel API
        self.btn_back = self.toolbar.btn_back
        self.btn_forward = self.toolbar.btn_forward
        self.btn_refresh = self.toolbar.btn_refresh
        self.url_bar = self.toolbar.url_bar
        self.web_page = self.web_view.web_page

        self._setup_layout()
        self._connect_components()

        self.navigation.open(url_str)

    def _setup_layout(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(6, 4, 6, 4)
        toolbar_layout.setSpacing(4)

        self.toolbar.add_to_layout(
            toolbar_layout
        )

        layout.addLayout(toolbar_layout)
        layout.addWidget(
            self.web_view,
            1,
        )

    def _connect_components(self):
        self.scripts.install_global_script()

        self.web_view.loadFinished.connect(
            self.scripts.inject_on_load_finished
        )