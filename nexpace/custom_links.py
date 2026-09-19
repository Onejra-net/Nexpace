from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QInputDialog,
)

from .localization import tr
from .links import CustomLinkItem



class CustomLinksWidget(QWidget):
    """Manage user-defined web links and expose them as dockable panels."""

    openLinkRequested = Signal(str, str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.header = QLabel(tr("my_links_tools"))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.header.setFont(font)
        layout.addWidget(self.header)

        self.add_btn = QPushButton(tr("add_new_link_page"))
        self.add_btn.setStyleSheet("padding: 6px; font-weight: bold;")
        self.add_btn.clicked.connect(self.prompt_add_custom)
        layout.addWidget(self.add_btn)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.links_layout = QVBoxLayout(self.container)
        self.links_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.container)

        layout.addWidget(scroll, 1)

    def refresh_ui(self):
        """Update labels/buttons after language change and rebuild link list."""
        
        self.header.setText(tr("my_links_tools"))
        self.add_btn.setText(tr("add_new_link_page"))
        self.rebuild_links(self.main_window.custom_links)

    def rebuild_links(self, services_list):
        while self.links_layout.count():
            item = self.links_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not services_list:
            empty_lbl = QLabel(tr("no_custom_links_html"))
            self.links_layout.addWidget(empty_lbl)
            return

        for service in services_list:
            item = CustomLinkItem(service["name"], service["url"])
            item.open_requested.connect(self.openLinkRequested.emit)
            item.delete_requested.connect(self.main_window.remove_custom_link)
            self.links_layout.addWidget(item)

    def prompt_add_custom(self):
        url_str, ok = QInputDialog.getText(
            self, tr("add_custom_link"), tr("enter_url")
        )
        if not ok or not url_str.strip():
            return

        url_str = url_str.strip()
        if not (url_str.startswith("http://") or url_str.startswith("https://")):
            url_str = "https://" + url_str

        default_name = QUrl(url_str).host() or url_str
        name_str, ok = QInputDialog.getText(
            self, tr("window_name"), tr("enter_panel_name"), text=default_name
        )
        if not ok or not name_str.strip():
            name_str = default_name

        self.main_window.add_custom_link(name_str.strip(), url_str)