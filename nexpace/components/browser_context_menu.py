"""
Browser context menu management.

Responsible for:
- Configuring the custom browser context menu
- Providing the AI prompt insertion action
- Delegating prompt insertion to AiPromptAction
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu

from ..localization import tr
from .actions.ai_prompt_action import AiPromptAction


class BrowserContextMenu:
    """
    Coordinator for browser context menu actions.

    Handles context menu interactions and delegates
    AI prompt operations to the dedicated action component.
    """

    def __init__(self, panel, main_window=None):

        # Browser panel and main window references:
        self.panel = panel
        self.main_window = main_window

        # AI prompt action handler:
        self.ai_prompt_action = AiPromptAction(
            panel,
            main_window,
        )

        # Enable the custom browser context menu:
        self.panel.web_view.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        # Connect context menu requests:
        self.panel.web_view.customContextMenuRequested.connect(
            self.show
        )

    def show(self, pos):
        """
        Display the browser context menu and dispatch the selected action.
        """

        # Context menu initialization:
        menu = QMenu(self.panel)

        # AI prompt insertion action:
        ai_action = menu.addAction(
            tr("paste_prompt_to_ai_chat")
        )

        menu.addSeparator()

        # Display the menu at the requested position:
        selected = menu.exec(
            self.panel.web_view.mapToGlobal(pos)
        )

        # Execute the selected AI prompt action:
        if selected == ai_action:
            self.ai_prompt_action.execute()
