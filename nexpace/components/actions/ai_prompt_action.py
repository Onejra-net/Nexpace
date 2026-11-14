"""
AI prompt generation and browser injection.

Responsible for:
- Saving the active PDF page note
- Generating the current AI prompt
- Copying the prompt to the system clipboard
- Preparing and executing the JavaScript injection
- Handling injection results and status messages
"""

import json

from PySide6.QtGui import QGuiApplication

from ...localization import tr
from .prompts.ai_prompt import (
    build_ai_prompt_injection_script,
)



class AiPromptAction:
    """
    Coordinator for AI prompt insertion into web chats.

    Prepares the current document context, copies the generated
    prompt, and attempts to inject it into the active browser.
    """

    def __init__(self, panel, main_window=None):
        # Browser panel and main window references:
        self.panel = panel
        self.main_window = main_window

    def execute(self):
        """
        Generate, copy, and attempt to inject the current AI prompt.
        """

        # Require an active main window:
        if not self.main_window:
            return

        # Save the current page note before generating the prompt:
        self.main_window._save_current_note_for_page(
            self.main_window._notes_page
        )

        # Generate the AI prompt from the current document context:
        prompt_text = (
            self.main_window.generate_full_ai_prompt_text()
        )

        # Stop if no prompt can be generated:
        if not prompt_text:
            self.main_window.statusBar().showMessage(
                tr("open_pdf_file_first"),
                3000,
            )
            return

        # Copy the prompt to the system clipboard:
        QGuiApplication.clipboard().setText(
            prompt_text
        )

        # Serialize the prompt for JavaScript:
        prompt_json = json.dumps(
            prompt_text
        )

        # Build the AI chat injection script:
        js_injection = build_ai_prompt_injection_script(
            prompt_json
        )

        # Execute the script and process its result:
        self.panel.web_view.page().runJavaScript(
            js_injection,
            self._handle_injection_result,
        )

    def _handle_injection_result(self, result):
        """
        Report whether the AI prompt injection succeeded.
        """

        # Confirm successful prompt insertion:
        if result == "SUCCESS":
            self.main_window.statusBar().showMessage(
                tr("prompt_pasted_into_chat"),
                4000,
            )

        # Provide manual paste instructions if injection fails:
        else:
            self.main_window.statusBar().showMessage(
                tr("copied_click_chat_ctrl_v"),
                4000,
            )
