"""Action for generating and injecting the current AI prompt into web chat."""



import json

from PySide6.QtGui import QGuiApplication

from ...localization import tr
from .prompts.ai_prompt import (
    build_ai_prompt_injection_script,
)



class AiPromptAction:
    """Generates, copies, and injects the current AI prompt into web chat."""

    def __init__(self, panel, main_window=None):
        self.panel = panel
        self.main_window = main_window

    def execute(self):
        """Generate the current AI prompt and inject it into the web chat."""
        
        if not self.main_window:
            return

        self.main_window._save_current_note_for_page(
            self.main_window._notes_page
        )

        prompt_text = (
            self.main_window.generate_full_ai_prompt_text()
        )

        if not prompt_text:
            self.main_window.statusBar().showMessage(
                tr("open_pdf_file_first"),
                3000,
            )
            return

        QGuiApplication.clipboard().setText(
            prompt_text
        )

        prompt_json = json.dumps(
            prompt_text
        )

        js_injection = build_ai_prompt_injection_script(
            prompt_json
        )

        self.panel.web_view.page().runJavaScript(
            js_injection,
            self._handle_injection_result,
        )

    def _handle_injection_result(self, result):
        """Handle the result returned by the JavaScript injection."""
        
        if result == "SUCCESS":
            self.main_window.statusBar().showMessage(
                tr("prompt_pasted_into_chat"),
                4000,
            )
        else:
            self.main_window.statusBar().showMessage(
                tr("copied_click_chat_ctrl_v"),
                4000,
            )