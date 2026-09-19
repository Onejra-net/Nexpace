from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QTabBar
from ..browser_panel import BrowserTabPanel

DEFAULT_AI_SERVICES = [
    ("ChatGPT", "https://chatgpt.com/"),
    ("Claude", "https://claude.ai/"),
    ("Gemini", "https://gemini.google.com/"),
    ("Perplexity", "https://www.perplexity.ai/"),
    ("DeepSeek", "https://chat.deepseek.com/"),
    ("Grok", "https://grok.com/"),
    ("Copilot", "https://copilot.microsoft.com/"),
    ("Mistral", "https://chat.mistral.ai/"),
]


class DockManager:
    def __init__(self, main_window):
        self.mw = main_window
        self.ai_docks = {}
        self.link_docks = {}
        self.links_manager_dock = None
        self.pdf_dock = None
        self.notes_dock = None


    def make_dock(self, title, object_name, widget):
        dock = QDockWidget(title, self.mw)
        dock.setObjectName(object_name)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        dock.setMinimumSize(220, 160)
        return dock


    def init_ai_docks(self):
        first_ai_dock = None

        for name, url in DEFAULT_AI_SERVICES:
            browser_panel = BrowserTabPanel(url, main_window=self.mw)
            dock_id = f"AIDock_{name}"
            dock = self.make_dock(f"🤖 {name}", dock_id, browser_panel)

            self.mw.addDockWidget(Qt.RightDockWidgetArea, dock)

            if first_ai_dock is None:
                first_ai_dock = dock

                if self.notes_dock is not None:
                    try:
                        self.mw.splitDockWidget(
                            self.notes_dock,
                            dock,
                            Qt.Vertical,
                        )
                    except Exception:
                        pass
            else:
                self.mw.tabifyDockWidget(first_ai_dock, dock)

            self.ai_docks[name] = dock

        if first_ai_dock:
            first_ai_dock.raise_()

        for tab_bar in self.mw.findChildren(QTabBar):
            self.configure_tabbar(tab_bar)


    def configure_tabbar(self, tab_bar):
        if not tab_bar:
            return

        tab_bar.setTabsClosable(True)

        # Do not connect the same QTabBar more than once:
        if tab_bar.property("nexpace_close_handler_installed"):
            return

        tab_bar.setProperty("nexpace_close_handler_installed", True)

        tab_bar.tabCloseRequested.connect(
            lambda index, bar=tab_bar:
            self.on_tab_close_requested(bar, index)
        )


    def on_tab_close_requested(self, tab_bar, index):
        if tab_bar is None:
            return

        if index < 0 or index >= tab_bar.count():
            return

        tab_title = tab_bar.tabText(index)

        for dock in self.mw.findChildren(QDockWidget):
            if dock.windowTitle() == tab_title:
                dock.hide()
                return


    def sync_links_and_docks(self):
        self.mw.links_panel.rebuild_links(self.mw.custom_links)

        for service in self.mw.custom_links:
            name = service["name"]
            url = service["url"]
            dock_id = f"LinkDock_{name}"

            if name not in self.link_docks:
                browser_panel = BrowserTabPanel(
                    url,
                    main_window=self.mw,
                )
                dock = self.make_dock(
                    f"🌐 {name}",
                    dock_id,
                    browser_panel,
                )
                dock.hide()

                self.mw.addDockWidget(
                    Qt.RightDockWidgetArea,
                    dock,
                )
                self.mw.tabifyDockWidget(
                    self.links_manager_dock,
                    dock,
                )
                self.link_docks[name] = dock

        for tab_bar in self.mw.findChildren(QTabBar):
            self.configure_tabbar(tab_bar)

        self.mw.menu_manager.update_view_menu()