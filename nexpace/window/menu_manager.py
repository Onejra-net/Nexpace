from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from ..localization import tr



class MenuManager:
    def __init__(self, main_window):
        self.mw = main_window
        self.view_menu = None
        self.settings_menu = None
        self.language_menu = None
        self.action_language_pl = None
        self.action_language_en = None


    def build_app_menu(self):
        self.mw.menuBar().clear()

        # File:
        file_menu = self.mw.menuBar().addMenu(tr("file"))

        open_action = QAction(tr('open_pdf_2'), self.mw)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.mw.pdf_panel.open_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction(tr("save_2"), self.mw)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.mw.save_notes)
        file_menu.addAction(save_action)

        save_as_action = QAction(tr('save_as_2'), self.mw)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.mw.save_notes_as)
        file_menu.addAction(save_as_action)

        load_external_action = QAction(tr('load_import_notes'), self.mw)
        load_external_action.triggered.connect(self.mw.load_notes_from_external_file)
        file_menu.addAction(load_external_action)

        file_menu.addSeparator()

        reset_action = QAction(tr('reset_panel_layout_alt'), self.mw)
        reset_action.triggered.connect(self.mw.workspace_manager.reset_workspace)
        file_menu.addAction(reset_action)

        file_menu.addSeparator()

        exit_action = QAction(tr('exit_alt'), self.mw)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.mw.close)
        file_menu.addAction(exit_action)

        # View:
        self.view_menu = self.mw.menuBar().addMenu(tr("view"))
        self.update_view_menu()

        # Settings:
        self.settings_menu = self.mw.menuBar().addMenu(tr("settings"))
        self.language_menu = self.settings_menu.addMenu(tr("language"))

        self.action_language_pl = QAction(tr("language_pl"), self.mw)
        self.action_language_pl.setCheckable(True)
        self.action_language_en = QAction(tr("language_en"), self.mw)
        self.action_language_en.setCheckable(True)

        self.language_menu.addAction(self.action_language_pl)
        self.language_menu.addAction(self.action_language_en)

        self.action_language_pl.triggered.connect(lambda: self.mw.change_language("pl"))
        self.action_language_en.triggered.connect(lambda: self.mw.change_language("en"))
        self.update_language_checks()

        # Help:
        help_menu = self.mw.menuBar().addMenu(tr("help"))
        about_action = QAction(tr("about_2"), self.mw)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)


    def update_view_menu(self):
        if not self.view_menu:
            return

        self.view_menu.clear()
        self.view_menu.addAction(self.mw.pdf_dock.toggleViewAction())
        self.view_menu.addAction(self.mw.notes_dock.toggleViewAction())

        ai_menu = self.view_menu.addMenu(tr('ai_assistants'))
        for name, dock in self.mw.dock_manager.ai_docks.items():
            ai_menu.addAction(dock.toggleViewAction())

        self.view_menu.addSeparator()
        self.view_menu.addAction(self.mw.dock_manager.links_manager_dock.toggleViewAction())

        if self.mw.dock_manager.link_docks:
            links_menu = self.view_menu.addMenu(tr('link_windows'))
            for name, dock in self.mw.dock_manager.link_docks.items():
                links_menu.addAction(dock.toggleViewAction())


    def update_language_checks(self):
        from ..localization import CURRENT_LANGUAGE
        if self.action_language_pl:
            self.action_language_pl.setChecked(CURRENT_LANGUAGE == "pl")
        if self.action_language_en:
            self.action_language_en.setChecked(CURRENT_LANGUAGE == "en")


    def show_about_dialog(self):
        dialog = QDialog(self.mw)
        dialog.setWindowTitle(tr("about_nexpace"))
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)
        about_text = f"""
        <h2>Nexpace</h2>
        <p>{tr("about_version", version=self.mw.app_version)}</p>
        <p>{tr("about_description")}</p>
        <p>{tr("about_features")}</p>
        <hr>
        <p>2026 {tr("about_website")}</p>
        <p style='color:#888; font-size:11px;'>{tr("about_license")}</p>
        """

        label = QLabel(about_text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()