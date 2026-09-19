from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from ..localization import tr


class CustomLinkItem(QFrame):
    """A single row representing one custom link."""

    open_requested = Signal(str, str)   # name, url
    delete_requested = Signal(str)      # name

    def __init__(self, name: str, url: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.url = url

        self.setStyleSheet(
            "QFrame { background-color: #252526; border-radius: 6px; padding: 4px; }"
        )

        layout = QHBoxLayout(self)

        self.label = QLabel(
            f"<b>{name}</b><br><span style='color:#777; font-size:10px;'>{url}</span>"
        )
        layout.addWidget(self.label, 1)

        self.open_btn = QPushButton(tr("open"))
        self.open_btn.clicked.connect(self._on_open)
        layout.addWidget(self.open_btn)

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip(tr("delete_link"))
        self.delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(self.delete_btn)

    def _on_open(self):
        self.open_requested.emit(self.name, self.url)

    def _on_delete(self):
        self.delete_requested.emit(self.name)

    def refresh_texts(self):
        
        """Update texts after a language change."""
        self.open_btn.setText(tr("open"))
        self.delete_btn.setToolTip(tr("delete_link"))