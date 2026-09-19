from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .localization import tr
from .notes.notes_context_menu import NotesContextMenu
from .notes.notes_navigation import NotesNavigation
from .notes.notes_scripts import NotesScriptManager
from .notes.notes_web_view import NotesWebView


class WebNotesEditor(QWidget):
    """Facade and coordinator for the Quill-based notes editor."""

    statsChanged = Signal(int, int)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = NotesWebView(self)

        self.notepad_statusbar = QLabel(
            tr("chars_words_zero")
        )

        self.notepad_statusbar.setStyleSheet(
            """
            QLabel {
                background-color: #252526;
                color: #888888;
                padding: 4px 10px;
                font-size: 11px;
                border-top: 1px solid #2d2d2d;
            }
            """
        )

        layout.addWidget(
            self.view,
            1,
        )

        layout.addWidget(
            self.notepad_statusbar,
            0,
        )

        self.scripts = NotesScriptManager(
            self.view
        )

        self.navigation = NotesNavigation(
            self.view,
            self.notepad_statusbar,
            tr,
        )

        self.context_menu = NotesContextMenu(
            self.view,
            self.scripts,
            self.main_window,
        )

        self.navigation.statsChanged.connect(
            self.statsChanged.emit
        )

        self.view.loadFinished.connect(
            self._on_page_loaded
        )

        self.view.customContextMenuRequested.connect(
            self.context_menu.show
        )

        self.view.loadFinished.connect(
            self._on_notes_page_loaded
        )

        self.view.load_editor()

    def _on_notes_page_loaded(self, ok):
        """Apply the current language after the editor finishes loading."""
        
        if ok:
            self.scripts.update_placeholder()

    def _on_page_loaded(self, ok):
        """Handle the notes page lifecycle."""
        
        if ok:
            self.scripts.update_placeholder()

    def update_placeholder(self):
        """Update the Quill placeholder after a language change."""
        
        self.scripts.update_placeholder()

    def setHtml(self, html_content):
        """Replace the current notes document with HTML."""
        
        self.scripts.set_html(
            html_content
        )

        self.navigation._cached_html = (
            html_content or ""
        )

    def getHtmlSync(self):
        """Return the cached notes HTML."""
        
        return self.navigation.cached_html()