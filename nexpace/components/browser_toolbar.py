from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from ..localization import tr
from .styles import BUTTON_STYLE, URL_BAR_STYLE


class BrowserToolbar:
    """Toolbar containing browser navigation controls and the URL display."""

    def __init__(self, parent=None):
        self.btn_back = QPushButton(
            tr("nav_back"),
            parent,
        )
        self.btn_back.setStyleSheet(BUTTON_STYLE)
        self.btn_back.setToolTip(
            tr("nav_back_tooltip")
        )

        self.btn_forward = QPushButton(
            tr("nav_forward"),
            parent,
        )
        self.btn_forward.setStyleSheet(BUTTON_STYLE)
        self.btn_forward.setToolTip(
            tr("nav_forward_tooltip")
        )

        self.btn_refresh = QPushButton(
            tr("nav_refresh"),
            parent,
        )
        self.btn_refresh.setStyleSheet(BUTTON_STYLE)
        self.btn_refresh.setToolTip(
            tr("nav_refresh_tooltip")
        )

        self.url_bar = QLineEdit(parent)
        self.url_bar.setReadOnly(True)
        self.url_bar.setStyleSheet(URL_BAR_STYLE)

    def add_to_layout(self, layout: QHBoxLayout):
        """Add toolbar widgets to the supplied layout."""
        
        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_forward)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.url_bar, 1)