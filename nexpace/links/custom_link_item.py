"""
Custom link list item component.

Responsible for:
- Displaying a custom link name and URL
- Providing link opening and deletion controls
- Emitting link action requests
- Updating interface texts after language changes
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from ..localization import tr


class CustomLinkItem(QFrame):
    """
    UI component representing a single custom link.

    Displays link information and forwards user actions
    through Qt signals.
    """

    # Custom link action signals:
    # - Request opening a link using its name and URL.
    # - Request deleting a link using its name.
    open_requested = Signal(str, str)
    delete_requested = Signal(str)

    def __init__(self, name: str, url: str, parent=None):
        super().__init__(parent)

        # Custom link data:
        self.name = name
        self.url = url

        # Link item appearance:
        self.setStyleSheet(
            "QFrame { background-color: #252526; border-radius: 6px; padding: 4px; }"
        )

        # Link item layout:
        layout = QHBoxLayout(self)

        # Link name and URL display:
        self.label = QLabel(
            f"<b>{name}</b><br><span style='color:#777; font-size:10px;'>{url}</span>"
        )
        layout.addWidget(self.label, 1)

        # Open link button:
        # - Request opening the associated browser panel.
        self.open_btn = QPushButton(tr("open"))
        self.open_btn.clicked.connect(self._on_open)
        layout.addWidget(self.open_btn)

        # Delete link button:
        # - Request removal of the custom link.
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip(tr("delete_link"))
        self.delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(self.delete_btn)

    def _on_open(self):
        """
        Emit a request to open the associated custom link.
        """

        self.open_requested.emit(self.name, self.url)

    def _on_delete(self):
        """
        Emit a request to remove the associated custom link.
        """

        self.delete_requested.emit(self.name)

    def refresh_texts(self):
        """
        Update translated button labels and tooltips.
        """

        # Refresh localized link controls:
        self.open_btn.setText(tr("open"))
        self.delete_btn.setToolTip(tr("delete_link"))
