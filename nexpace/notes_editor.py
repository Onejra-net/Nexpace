"""
Quill-based notes editor facade.

Responsible for:
- Assembling the notes editor interface
- Coordinating editor components
- Managing JavaScript interactions
- Handling editor loading and context menu events
- Exposing HTML content and text statistics
- Updating editor localization
"""

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
    """
    Main notes editor container.

    Integrates the Quill web view, script management,
    navigation, statistics, and context menu components.
    """

    # Editor statistics signal:
    # - Forwards character and word counts.
    statsChanged = Signal(int, int)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        # Main window reference:
        self.main_window = main_window

        # Main editor layout:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Quill editor web view:
        self.view = NotesWebView(self)

        # Editor statistics status bar:
        self.notepad_statusbar = QLabel(
            tr("chars_words_zero")
        )

        # Status bar appearance:
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

        # Editor interface composition:
        layout.addWidget(
            self.view,
            1,
        )

        layout.addWidget(
            self.notepad_statusbar,
            0,
        )

        # JavaScript interaction management:
        self.scripts = NotesScriptManager(
            self.view
        )

        # Editor navigation and text statistics:
        self.navigation = NotesNavigation(
            self.view,
            self.notepad_statusbar,
            tr,
        )

        # Editor context menu:
        self.context_menu = NotesContextMenu(
            self.view,
            self.scripts,
            self.main_window,
        )

        # Forward editor statistics:
        self.navigation.statsChanged.connect(
            self.statsChanged.emit
        )

        # Editor loading event:
        self.view.loadFinished.connect(
            self._on_page_loaded
        )

        # Custom context menu handling:
        self.view.customContextMenuRequested.connect(
            self.context_menu.show
        )

        # Notes page loading event:
        self.view.loadFinished.connect(
            self._on_notes_page_loaded
        )

        # Initialize the Quill editor:
        self.view.load_editor()

    def _on_notes_page_loaded(self, ok):
        """
        Update editor localization after successful page loading.
        """

        # Apply the translated editor placeholder:
        if ok:
            self.scripts.update_placeholder()

    def _on_page_loaded(self, ok):
        """
        Handle successful editor page loading.
        """

        # Initialize the editor placeholder:
        if ok:
            self.scripts.update_placeholder()

    def update_placeholder(self):
        """
        Refresh the Quill placeholder for the active language.
        """

        # Delegate placeholder updates to the script manager:
        self.scripts.update_placeholder()

    def setHtml(self, html_content):
        """
        Replace the editor content and synchronize the HTML cache.
        """

        # Update the Quill editor content:
        self.scripts.set_html(
            html_content
        )

        # Synchronize the cached HTML:
        self.navigation._cached_html = (
            html_content or ""
        )

    def getHtmlSync(self):
        """
        Return the cached HTML content of the notes editor.
        """

        # Retrieve the latest cached HTML:
        return self.navigation.cached_html()
