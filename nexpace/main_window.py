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
    """Coordinate the main Nexpace window, docks, workspace persistence, notes, and AI integrations."""

    WORKSPACE_VERSION = 7

    def __init__(self):
        super().__init__()
        self.app_version = get_app_version()
        self.setWindowTitle("Nexpace")
        self.resize(1700, 950)
        
        icon_path = get_base_path() / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.pdf_path = None
        self.notes_path = None
        self.notes = {}
        self.loading_notes = False
        self._notes_page = None
        self._note_switch_serial = 0
        self.custom_links = []

        # Managers initialization
        self.menu_manager = MenuManager(self)
        self.workspace_manager = WorkspaceManager(self)
        self.notes_manager = NotesManager(self)
        self.dock_manager = DockManager(self)

        self.setDockNestingEnabled(True)
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.GroupedDragging
        )
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.South)

        # Główne widżety
        self.pdf_panel = PdfViewerPanel()
        self.notes_editor = WebNotesEditor(main_window=self)
        self.links_panel = CustomLinksWidget(self)
        self.links_panel.openLinkRequested.connect(self.open_or_show_link_dock)

        self.page_label = QLabel(tr('page_label'))
        
        self.save_btn = QPushButton(tr('save'))
        self.save_btn.clicked.connect(self.save_notes)

        self.save_as_btn = QPushButton(tr('save_as'))
        self.save_as_btn.clicked.connect(self.save_notes_as)

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

        # 1. Tworzenie i przypisywanie doków bezpośrednio do okna oraz dock_manager
        self.pdf_dock = self.dock_manager.make_dock("📄 PDF", "PDFViewerDock", self.pdf_panel)
        self.notes_dock = self.dock_manager.make_dock(tr('notes'), "NotesDock", notes_widget)
        self.links_manager_dock = self.dock_manager.make_dock(tr('my_links'), "CustomLinksManagerDock", self.links_panel)

        # Synchronizacja referencji w dock_manager
        self.dock_manager.pdf_dock = self.pdf_dock
        self.dock_manager.notes_dock = self.notes_dock
        self.dock_manager.links_manager_dock = self.links_manager_dock

        self.addDockWidget(Qt.LeftDockWidgetArea, self.pdf_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.notes_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.links_manager_dock)

        self.dock_manager.init_ai_docks()

        # Sygnały
        self.pdf_panel.pageChanged.connect(self.page_changed)
        self.pdf_panel.fileChanged.connect(self.pdf_opened)

        # 2. Budowanie menu i synchronizacja doków (dopiero gdy doki istnieją)
        self.menu_manager.build_app_menu()
        self.dock_manager.sync_links_and_docks()

        self.statusBar().showMessage(tr('ready_to_work'))
        QTimer.singleShot(0, self.workspace_manager.restore_workspace)

    def change_language(self, language):
        set_language(language)
        self.apply_language_to_ui()
        if not self.workspace_manager.restoring_workspace: 
            self.workspace_manager.autosave_workspace() 

    def apply_language_to_ui(self):
        self.menu_manager.build_app_menu()
        self.menu_manager.update_language_checks()

        if hasattr(self, "save_btn"):
            self.save_btn.setText(tr("save"))
        if hasattr(self, "save_as_btn"):
            self.save_as_btn.setText(tr("save_as"))
        if hasattr(self, "page_label"):
            self.page_label.setText(tr("page_label"))
        if hasattr(self, "notes_editor"):
            self.notes_editor.update_placeholder()

        if hasattr(self, "notes_dock") and self.notes_dock:
            self.notes_dock.setWindowTitle(tr("notes"))
        if hasattr(self, "links_manager_dock") and self.links_manager_dock:
            self.links_manager_dock.setWindowTitle(tr("my_links"))
        if hasattr(self, "pdf_dock") and self.pdf_dock:
            self.pdf_dock.setWindowTitle(tr("pdf_dock"))

        if hasattr(self, "links_panel"):
            self.links_panel.refresh_ui()

        self.menu_manager.update_view_menu()
        self.statusBar().showMessage(tr("ready_to_work"), 2000)

    # Delegacje metod do menedżerów
    def save_notes(self): 
        self.notes_manager.save_notes()

    def save_notes_as(self): 
        self.notes_manager.save_notes_as()

    def load_notes_from_external_file(self): 
        self.notes_manager.load_notes_from_external_file()

    def load_notes(self): 
        self.notes_manager.load_notes()

    def _save_current_note_for_page(self, page):
        """Delegacja zapisu aktualnej notatki do NotesManager (używana przez kontekstowe menu i akcje AI)."""
        self.notes_manager.save_current_note_for_page(page)

    def open_or_show_link_dock(self, name, url):
        if name in self.dock_manager.link_docks:
            dock = self.dock_manager.link_docks[name]
            dock.show()
            dock.raise_()

    def add_custom_link(self, name, url):
        if any(s["name"] == name for s in self.custom_links):
            QMessageBox.warning(self, tr("warning"), tr('item_name_already_exists'))
            return
        self.custom_links.append({"name": name, "url": url})
        self.dock_manager.sync_links_and_docks()
        self.open_or_show_link_dock(name, url)

    def remove_custom_link(self, name):
        self.custom_links = [s for s in self.custom_links if s["name"] != name]
        if name in self.dock_manager.link_docks:
            dock = self.dock_manager.link_docks.pop(name)
            self.removeDockWidget(dock)
            dock.deleteLater()
        self.dock_manager.sync_links_and_docks()

    def get_pdf_text_for_current_page(self):
        if not self.pdf_path or not self.pdf_path.exists():
            return ""
        try:
            reader = pypdf.PdfReader(self.pdf_path)
            curr_page = self.current_page()
            if 0 <= curr_page < len(reader.pages):
                text = reader.pages[curr_page].extract_text()
                return text.strip() if text else ""
        except Exception as exc:
            print(tr("pypdf_error_print", exc=exc))
        return ""

    def generate_full_ai_prompt_text(self, custom_question=""):
        if not self.pdf_path:
            return ""
        pdf_text = self.get_pdf_text_for_current_page()
        raw_html_note = self.notes_editor.getHtmlSync()
        doc = QTextDocument()
        doc.setHtml(raw_html_note)
        plain_note = doc.toPlainText().strip()
        page_num = self.current_page() + 1
        
        import re
        def clean_text(t):
            if not t: return ""
            t = t.replace("\xa0", " ")
            t = re.sub(r'[ \t\r\n]+', ' ', t)
            return t.strip()

        clean_pdf_text = clean_text(pdf_text)
        if len(clean_pdf_text) > 4000:
            clean_pdf_text = clean_pdf_text[:4000] + tr('text_truncated')

        clean_note_text = clean_text(plain_note)
        prompt_parts = [
            tr("ai.context", page_num=page_num, pdf_name=self.pdf_path.name),
            tr("ai.pdf", pdf_text=clean_pdf_text if clean_pdf_text else tr("no_text")),
            tr("ai.notes", notes=clean_note_text if clean_note_text else tr("no_notes")),
        ]
        if custom_question:
            prompt_parts.append(tr("ai.command", custom_question=custom_question))
        else:
            prompt_parts.append(tr("ai.default_command"))
        return "\n\n".join(prompt_parts)

    def pdf_opened(self, path):
        if self.pdf_path:
            self.notes_manager.save_current_note_for_page(self._notes_page)

        self.pdf_path = Path(path).resolve()
        data_dir = get_base_path() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        path_hash = hashlib.md5(str(self.pdf_path).encode("utf-8")).hexdigest()
        safe_stem = "".join(c for c in self.pdf_path.stem if c.isalnum() or c in (" ", "_", "-")).strip()
        self.notes_path = data_dir / f"{safe_stem}_{path_hash[:8]}.json"

        self._notes_page = None
        self._note_switch_serial += 1
        self.load_notes()
        self.setWindowTitle(f"Nexpace — {self.pdf_path.name}")
        self._request_note_page(self.current_page())

    def current_page(self):
        return self.pdf_panel.current_page()

    def page_changed(self, page):
        self.notes_manager.save_current_note_for_page(self._notes_page)
        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page", page=f"{page + 1}{suffix}"))
        self._request_note_page(page)

    def _request_note_page(self, page):
        if not self.pdf_path:
            return
        page = max(0, int(page))
        self._note_switch_serial += 1
        serial = self._note_switch_serial

        self.loading_notes = True
        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page_loading", page=page + 1, suffix=suffix))
        QTimer.singleShot(50, lambda: self._finish_note_page(page, serial))

    def _finish_note_page(self, page, serial):
        if serial != self._note_switch_serial or not self.pdf_path:
            return

        key = str(page + 1)
        html_content = self.notes.get(key, "")

        self.loading_notes = True
        self.notes_editor.setHtml(html_content)
        self._notes_page = page
        self.loading_notes = False

        total = self.pdf_panel._page_count
        suffix = f" / {total}" if total else ""
        self.page_label.setText(tr("notes.page_done", page=page + 1, suffix=suffix))

    def closeEvent(self, event):
        if self.pdf_path:
            self.notes_manager.save_current_note_for_page(self._notes_page)
        self.workspace_manager.autosave_workspace()     
        event.accept()