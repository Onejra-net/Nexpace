from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu

from ..localization import tr
from .actions.ai_prompt_action import AiPromptAction


class BrowserContextMenu:
    """Builds the browser context menu and dispatches its actions."""

    def __init__(self, panel, main_window=None):
        self.panel = panel
        self.main_window = main_window

        self.ai_prompt_action = AiPromptAction(
            panel,
            main_window,
        )

        self.panel.web_view.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.panel.web_view.customContextMenuRequested.connect(
            self.show
        )

    def show(self, pos):
        """Show the browser context menu."""
        
        menu = QMenu(self.panel)

        ai_action = menu.addAction(
            tr("paste_prompt_to_ai_chat")
        )

        menu.addSeparator()

        selected = menu.exec(
            self.panel.web_view.mapToGlobal(pos)
        )

        if selected == ai_action:
            self.ai_prompt_action.execute()