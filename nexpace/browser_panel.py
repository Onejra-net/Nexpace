"""
Browser panel facade.

Responsible for:
- Assembling the browser UI
- Coordinating browser components
- Initializing navigation
- Configuring JavaScript injection
"""

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
    """
    Main browser panel container.

    Integrates the browser toolbar, web view, navigation,
    script management, and context menu components.
    """

    def __init__(self, url_str, main_window=None, parent=None):
        super().__init__(parent)

        # Main window reference:
        self.main_window = main_window

        # Browser UI components:
        self.toolbar = BrowserToolbar(self)
        self.web_view = BrowserWebView(self)

        # Browser navigation:
        self.navigation = BrowserNavigation(
            self.web_view,
            self.toolbar,
        )

        # JavaScript injection management:
        self.scripts = BrowserScriptManager(
            self.web_view.page()
        )

        # Browser context menu:
        self.context_menu = BrowserContextMenu(
            self,
            main_window,
        )

        # Backward compatibility:
        # - Expose component references through the original panel interface.
        self.btn_back = self.toolbar.btn_back
        self.btn_forward = self.toolbar.btn_forward
        self.btn_refresh = self.toolbar.btn_refresh
        self.url_bar = self.toolbar.url_bar
        self.web_page = self.web_view.web_page

        # Panel initialization:
        self._setup_layout()
        self._connect_components()

        # Initial page navigation:
        self.navigation.open(url_str)

    def _setup_layout(self):
        """Arrange the browser toolbar and web view."""
        
        # Main vertical layout:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar layout:
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(6, 4, 6, 4)
        toolbar_layout.setSpacing(4)

        self.toolbar.add_to_layout(
            toolbar_layout
        )

        # Browser panel composition:
        layout.addLayout(toolbar_layout)
        layout.addWidget(
            self.web_view,
            1,
        )

    def _connect_components(self):
        """Configure script injection and page-load handling."""
        
        # Global JavaScript initialization:
        self.scripts.install_global_script()

        # Inject scripts after page loading completes:
        self.web_view.loadFinished.connect(
            self.scripts.inject_on_load_finished
        )