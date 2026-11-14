
"""
Main application window and component coordinator.

Responsible for:
- Initializing the main interface and dockable panels
- Coordinating application managers
- Managing custom links and browser docks
- Synchronizing PDF pages with associated notes
- Preparing PDF and note content for AI prompts
- Updating interface localization
- Restoring and saving the application workspace
"""

import hashlib
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextDocument, QIcon
from PySide6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
    QDockWidget, QInputDialog, QFrame, QMenu, QTabBar, QTabWidget,
)

import pypdf

from .localization import get_app_version, get_base_path, set_language, tr
from .browser_panel import BrowserTabPanel
from .custom_links import CustomLinksWidget
from .notes_editor import WebNotesEditor
from .pdf_viewer import PdfViewerPanel

from .window.menu_manager import MenuManager
from .window.workspace_manager import WorkspaceManager
from .window.notes_manager import NotesManager
from .window.dock_manager import DockManager


class MainWindow(QMainWindow):
    """
    Central coordinator of the Nexpace application.

    Integrates the main UI components and delegates specialized
    operations to dedicated application managers.
    """

    # Workspace data format version:
    WORKSPACE_VERSION = 7

    def __init__(self):
        super().__init__()

        # Main window configuration:
        self.app_version = get_app_version()
        self.setWindowTitle("Nexpace")
        self.resize(1700, 950)

        # Application icon:
        icon_path = get_base_path() / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Application state:
        # - Active PDF and associated notes file
        # - Page-specific notes and loading state
        # - Custom browser links
        self.pdf_path = None
        self.notes_path = None
        self.notes = {}
        self.loading_notes = False
        self._notes_page = None
        self._note_switch_serial = 0
        self.custom_links = []

        # Application managers:
        # - Menu, workspace, notes, and dock management
        self.menu_manager = MenuManager(self)
        self.workspace_manager = WorkspaceManager(self)
        self.notes_manager = NotesManager(self)
        self.dock_manager = DockManager(self)

        # Docking system configuration:
        # - Enable nested, tabbed, and animated docks
        # - Allow grouped dock dragging
        self.setDockNestingEnabled(True)
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.GroupedDragging
        )
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.South)

        # Main interface components:
        self.pdf_panel = PdfViewerPanel()
        self.notes_editor = WebNotesEditor(main_window=self)
        self.links_panel = CustomLinksWidget(self)
        self.links_panel.openLinkRequested.connect(self.open_or_show_link_dock)

        # Notes page indicator:
        self.page_label = QLabel(tr('page_label'))

        # Notes saving controls:
        self.save_btn = QPushButton(tr('save'))
        self.save_btn.clicked.connect(self.save_notes)

        self.save_as_btn = QPushButton(tr('save_as'))
        self.save_as_btn.clicked.connect(self.save_notes_as)

        # Notes panel layout:
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_header = QHBoxLayout()
        notes_header.setSpacing(8)
        notes_header.addWidget(self.page_label)
        notes_header.addStretch()
        notes_header.addWidget(self.save_btn)
        notes_header.addWidget(self.save_as_btn)
        notes_header.addSpacing(10)

        notes_layout.addLayout(notes_header)
        notes_layout.addWidget(self.notes_editor)

        # Primary dock creation:
        self.pdf_dock = self.dock_manager.make_dock("📄 PDF", "PDFViewerDock", self.pdf_panel)
        self.notes_dock = self.dock_manager.make_dock(tr('notes'), "NotesDock", notes_widget)
        self.links_manager_dock = self.dock_manager.make_dock(tr('my_links'), "CustomLinksManagerDock", self.links_panel)

        # Register primary docks with DockManager:
        self.dock_manager.pdf_dock = self.pdf_dock
        self.dock_manager.notes_dock = self.notes_dock
        self.dock_manager.links_manager_dock = self.links_manager_dock

        # Initial dock placement:
        self.addDockWidget(Qt.LeftDockWidgetArea, self.pdf_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.notes_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.links_manager_dock)

        # AI dock initialization:
        self.dock_manager.init_ai_docks()

        # PDF event connections:
        self.pdf_panel.pageChanged.connect(self.page_changed)
        self.pdf_panel.fileChanged.connect(self.pdf_opened)

        # Menu and dock synchronization:
        # - Initialize after the primary docks have been created.
        self.menu_manager.build_app_menu()
        self.dock_manager.sync_links_and_docks()

        # Application startup:
        # - Display ready status
        # - Restore the saved workspace on the next event loop cycle
        self.statusBar().showMessage(tr('ready_to_work'))
        QTimer.singleShot(0, self.workspace_manager.restore_workspace)

    def change_language(self, language):
        """
        Change the application language and update the interface.
        """

        # Language state and UI refresh:
        set_language(language)
        self.apply_language_to_ui()

        # Persist language changes outside workspace restoration:
        if not self.workspace_manager.restoring_workspace:
            self.workspace_manager.autosave_workspace()

    def apply_language_to_ui(self):
        """
        Apply the active language to the main interface components.
        """

        # Menu localization:
        self.menu_manager.build_app_menu()
        self.menu_manager.update_language_checks()

        # Notes interface localization:
        if hasattr(self, "save_btn"):
            self.save_btn.setText(tr("save"))
        if hasattr(self, "save_as_btn"):
            self.save_as_btn.setText(tr("save_as"))
        if hasattr(self, "page_label"):
            self.page_label.setText(tr("page_label"))
        if hasattr(self, "notes_editor"):
            self.notes_editor.update_placeholder()

        # Dock title localization:
        if hasattr(self, "notes_dock") and self.notes_dock:
            self.notes_dock.setWindowTitle(tr("notes"))
        if hasattr(self, "links_manager_dock") and self.links_manager_dock:
            self.links_manager_dock.setWindowTitle(tr("my_links"))
        if hasattr(self, "pdf_dock") and self.pdf_dock:
            self.pdf_dock.setWindowTitle(tr("pdf_dock"))

        # Custom links interface localization:
        if hasattr(self, "links_panel"):
            self.links_panel.refresh_ui()

        # View menu and status refresh:
        self.menu_manager.update_view_menu()
        self.statusBar().showMessage(tr("ready_to_work"), 2000)

    # NotesManager delegation:
    # - Expose note operations through the main window interface.

    def save_notes(self):
        self.notes_manager.save_notes()

    def save_notes_as(self):
        self.notes_manager.save_notes_as()

    def load_notes_from_external_file(self):
        self.notes_manager.load_notes_from_external_file()

    def load_notes(self):
        self.notes_manager.load_notes()

    def _save_current_note_for_page(self, page):
        """
        Delegate page-specific note saving to NotesManager.
        """
        self.notes_manager.save_current_note_for_page(page)

    def open_or_show_link_dock(self, name, url):
        """
        Show and raise an existing browser dock identified by its name.
        """

        # Locate and activate an existing dock:
        if name in self.dock_manager.link_docks:
            dock = self.dock_manager.link_docks[name]
            dock.show()
            dock.raise_()

    def add_custom_link(self, name, url):
        """
        Register a custom link and activate its browser dock.
        """

        # Prevent duplicate link names:
        if any(s["name"] == name for s in self.custom_links):
            QMessageBox.warning(self, tr("warning"), tr('item_name_already_exists'))
            return

        # Register and synchronize the new link:
        self.custom_links.append({"name": name, "url": url})
        self.dock_manager.sync_links_and_docks()

        # Activate the associated browser dock:
        self.open_or_show_link_dock(name, url)

    def remove_custom_link(self, name):
        """
        Remove a custom link and its associated browser dock.
        """

        # Remove the link from application state:
        self.custom_links = [s for s in self.custom_links if s["name"] != name]

        # Remove the existing browser dock:
        if name in self.dock_manager.link_docks:
            dock = self.dock_manager.link_docks.pop(name)
            self.removeDockWidget(dock)
            dock.deleteLater()

        # Synchronize remaining links and docks:
        self.dock_manager.sync_links_and_docks()

    def get_pdf_text_for_current_page(self):
        """
        Extract text from the currently selected PDF page.
        """

        # Validate the active PDF path:
        if not self.pdf_path or not self.pdf_path.exists():
            return ""

        # PDF text extraction:
        try:
            reader = pypdf.PdfReader(self.pdf_path)
            curr_page = self.current_page()
            if 0 <= curr_page < len(reader.pages):
                text = reader.pages[curr_page].extract_text()
                return text.strip() if text else ""

        # Report extraction failures:
        except Exception as exc:
            print(tr("pypdf_error_print", exc=exc))

        return ""

    def generate_full_ai_prompt_text(self, custom_question=""):
        """
        Build an AI prompt using the active PDF page and its notes.

        Combine document context, extracted PDF text, plain-text
        notes, and an optional user question into a translated prompt.
        """

        # Require an active PDF:
        if not self.pdf_path:
            return ""

        # Collect current page content:
        pdf_text = self.get_pdf_text_for_current_page()
        raw_html_note = self.notes_editor.getHtmlSync()

        # Convert HTML notes to plain text:
        doc = QTextDocument()
        doc.setHtml(raw_html_note)
        plain_note = doc.toPlainText().strip()
        page_num = self.current_page() + 1

        # Prompt text normalization:
        import re
        def clean_text(t):
            if not t: return ""
            t = t.replace("\xa0", " ")
            t = re.sub(r'[ \t\r\n]+', ' ', t)
            return t.strip()

        # Normalize and limit extracted PDF text:
        clean_pdf_text = clean_text(pdf_text)
        if len(clean_pdf_text) > 4000:
            clean_pdf_text = clean_pdf_text[:4000] + tr('text_truncated')

        # Normalize notes and assemble prompt sections:
        clean_note_text = clean_text(plain_note)
        prompt_parts = [
            tr("ai.context", page_num=page_num, pdf_name=self.pdf_path.name),
            tr("ai.pdf", pdf_text=clean_pdf_text if clean_pdf_text else tr("no_text")),
            tr("ai.notes", notes=clean_note_text if clean_note_text else tr("no_notes")),
        ]

        # Select a custom or default AI instruction:
        if custom_question:
            prompt_parts.append(tr("ai.command", custom_question=custom_question))
        else:
            prompt_parts.append(tr("ai.default_command"))

        # Return the completed prompt:
        return "\n\n".join(prompt_parts)

    def pdf_opened(self, path):
        """
        Initialize document-specific notes when a PDF is opened.
        """

        # Preserve the current note before switching documents:
        if self.pdf_path:
            self.notes_manager.save_current_note_for_page(self._notes_page)

        # Resolve the PDF path and notes storage directory:
        self.pdf_path = Path(path).resolve()
        data_dir = get_base_path() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Generate a unique notes filename from the PDF path:
        path_hash = hashlib.md5(str(self.pdf_path).encode("utf-8")).hexdigest()
        safe_stem = "".join(c for c in self.pdf_path.stem if c.isalnum() or c in (" ", "_", "-")).strip()
        self.notes_path = data_dir / f"{safe_stem}_{path_hash[:8]}.json"

        # Reset note navigation state and load document notes:
        self._notes_page = None
        self._note_switch_serial += 1
        self.load_notes()

        # Update the window title and load the active page note:
        self.setWindowTitle(f"Nexpace — {self.pdf_path.name}")
        self._request_note_page(self.current_page())

    def current_page(self):
        """
        Return the currently selected PDF page index.
        """
        return self.pdf_panel.current_page()

    def page_changed(self, page):
        """
        Save the previous note and request notes for the selected page.
        """

        # Preserve the note associated with the previous page:
        self.notes_manager.save_current_note_for_page(self._notes_page)

        # Update the page indicator:
        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page", page=f"{page + 1}{suffix}"))

        # Request the newly selected page note:
        self._request_note_page(page)

    def _request_note_page(self, page):
        """
        Schedule loading of notes associated with a PDF page.

        Track requests using a serial number to prevent outdated
        page updates from replacing the latest selection.
        """

        # Validate the document and normalize the page index:
        if not self.pdf_path:
            return
        page = max(0, int(page))

        # Register the latest page loading request:
        self._note_switch_serial += 1
        serial = self._note_switch_serial

        # Indicate note loading:
        self.loading_notes = True
        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page_loading", page=page + 1, suffix=suffix))

        # Defer note loading through the Qt event loop:
        QTimer.singleShot(50, lambda: self._finish_note_page(page, serial))

    def _finish_note_page(self, page, serial):
        """
        Apply the requested page note if the request is still current.
        """

        # Ignore outdated requests or missing documents:
        if serial != self._note_switch_serial or not self.pdf_path:
            return

        # Retrieve HTML notes for the selected page:
        key = str(page + 1)
        html_content = self.notes.get(key, "")

        # Update the notes editor and active page state:
        self.loading_notes = True
        self.notes_editor.setHtml(html_content)
        self._notes_page = page
        self.loading_notes = False

        # Update the completed page indicator:
        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page_done", page=page + 1, suffix=suffix))

    def closeEvent(self, event):
        """
        Save the active note and workspace when the window closes.
        """

        # Preserve the current page note:
        if self.pdf_path:
            self.notes_manager.save_current_note_for_page(self._notes_page)

        # Save workspace state and accept the close event:
        self.workspace_manager.autosave_workspace()
        event.accept()
