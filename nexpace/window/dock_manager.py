
"""
Dockable panel management for Nexpace.

Responsible for:
- Creating and configuring dock widgets
- Initializing default AI service panels
- Organizing dock placement and tab groups
- Handling dock tab close requests
- Synchronizing custom links with browser docks
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QTabBar
from ..browser_panel import BrowserTabPanel



# Dock icons:
AI_DOCK_ICON = "🤖"
CUSTOM_LINK_ICON = "🌐"

# Default AI services:
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
    """
    Coordinator for dockable application panels.

    Manages AI browser docks, custom link docks,
    dock configuration, and tab interactions.
    """

    def __init__(self, main_window):

        # Main window reference:
        self.mw = main_window

        # Dock registries:
        # - AI service docks
        # - Custom link docks
        self.ai_docks = {}
        self.link_docks = {}

        # Primary application dock references:
        self.links_manager_dock = None
        self.pdf_dock = None
        self.notes_dock = None

    def make_dock(self, title, object_name, widget):
        """
        Create a configurable dock widget containing the provided component.
        """

        # Dock initialization:
        dock = QDockWidget(title, self.mw)
        dock.setObjectName(object_name)
        dock.setWidget(widget)

        # Dock behavior:
        # - Allow docking in all areas
        # - Enable moving, floating, and closing
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable
        )

        # Minimum dock dimensions:
        dock.setMinimumSize(220, 160)

        return dock

    def init_ai_docks(self):
        """
        Create and arrange the default AI service browser panels.
        """

        # Track the first AI dock as the tab group reference:
        first_ai_dock = None

        # Create browser docks for predefined AI services:
        for name, url in DEFAULT_AI_SERVICES:
            browser_panel = BrowserTabPanel(url, main_window=self.mw)
            dock_id = f"AIDock_{name}"
            dock = self.make_dock(f"{AI_DOCK_ICON} {name}", dock_id, browser_panel)

            # Add the AI dock to the main window:
            self.mw.addDockWidget(Qt.RightDockWidgetArea, dock)

            # Position the first AI dock relative to the notes panel:
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

            # Group subsequent AI docks into tabs:
            else:
                self.mw.tabifyDockWidget(first_ai_dock, dock)

            # Register the AI dock:
            self.ai_docks[name] = dock

        # Activate the first AI dock:
        if first_ai_dock:
            first_ai_dock.raise_()

        # Configure available dock tab bars:
        for tab_bar in self.mw.findChildren(QTabBar):
            self.configure_tabbar(tab_bar)

    def configure_tabbar(self, tab_bar):
        """
        Enable dock tab closing and register its event handler.
        """

        # Validate the tab bar:
        if not tab_bar:
            return

        # Enable close buttons on tabs:
        tab_bar.setTabsClosable(True)

        # Prevent duplicate signal connections:
        if tab_bar.property("nexpace_close_handler_installed"):
            return

        # Mark the close handler as installed:
        tab_bar.setProperty("nexpace_close_handler_installed", True)

        # Connect tab closing to dock visibility management:
        tab_bar.tabCloseRequested.connect(
            lambda index, bar=tab_bar:
            self.on_tab_close_requested(bar, index)
        )

    def on_tab_close_requested(self, tab_bar, index):
        """
        Hide the dock associated with the requested tab.
        """

        # Validate the tab bar and selected tab index:
        if tab_bar is None:
            return

        if index < 0 or index >= tab_bar.count():
            return

        # Identify the selected dock tab:
        tab_title = tab_bar.tabText(index)

        # Find and hide the matching dock:
        for dock in self.mw.findChildren(QDockWidget):
            if dock.windowTitle() == tab_title:
                dock.hide()
                return

    def sync_links_and_docks(self):
        """
        Synchronize custom link entries with their browser dock panels.
        """

        # Refresh the custom links interface:
        self.mw.links_panel.rebuild_links(self.mw.custom_links)

        # Register browser docks for custom links:
        for service in self.mw.custom_links:
            name = service["name"]
            url = service["url"]
            dock_id = f"LinkDock_{name}"

            # Create a dock only if it does not already exist:
            if name not in self.link_docks:
                browser_panel = BrowserTabPanel(
                    url,
                    main_window=self.mw,
                )
                dock = self.make_dock(
                    f"{CUSTOM_LINK_ICON} {name}",
                    dock_id,
                    browser_panel,
                )
                dock.hide()

                # Add the dock to the main window:
                self.mw.addDockWidget(
                    Qt.RightDockWidgetArea,
                    dock,
                )

                # Group the dock with the custom links manager:
                self.mw.tabifyDockWidget(
                    self.links_manager_dock,
                    dock,
                )

                # Register the custom link dock:
                self.link_docks[name] = dock

        # Configure dock tab controls:
        for tab_bar in self.mw.findChildren(QTabBar):
            self.configure_tabbar(tab_bar)

        # Refresh the application view menu:
        self.mw.menu_manager.update_view_menu()
