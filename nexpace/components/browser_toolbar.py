"""
Browser navigation toolbar.

Responsible for:
- Creating back, forward, and refresh controls
- Displaying the current browser URL
- Applying shared toolbar styles and localized labels
- Providing toolbar widgets for layout integration
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from ..localization import tr
from .styles import BUTTON_STYLE, URL_BAR_STYLE


class BrowserToolbar:
    """
    Container for browser navigation controls.

    Provides navigation buttons and a read-only URL bar
    for integration with the browser panel.
    """

    def __init__(self, parent=None):

        # Back navigation button:
        self.btn_back = QPushButton(
            tr("nav_back"),
            parent,
        )
        self.btn_back.setStyleSheet(BUTTON_STYLE)
        self.btn_back.setToolTip(
            tr("nav_back_tooltip")
        )

        # Forward navigation button:
        self.btn_forward = QPushButton(
            tr("nav_forward"),
            parent,
        )
        self.btn_forward.setStyleSheet(BUTTON_STYLE)
        self.btn_forward.setToolTip(
            tr("nav_forward_tooltip")
        )

        # Page refresh button:
        self.btn_refresh = QPushButton(
            tr("nav_refresh"),
            parent,
        )
        self.btn_refresh.setStyleSheet(BUTTON_STYLE)
        self.btn_refresh.setToolTip(
            tr("nav_refresh_tooltip")
        )

        # Current URL display:
        # - Read-only to prevent direct address editing.
        self.url_bar = QLineEdit(parent)
        self.url_bar.setReadOnly(True)
        self.url_bar.setStyleSheet(URL_BAR_STYLE)

    def add_to_layout(self, layout: QHBoxLayout):
        """Add browser controls to the provided horizontal layout."""

        # Toolbar widget arrangement:
        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_forward)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.url_bar, 1)