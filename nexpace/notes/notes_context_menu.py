from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMenu

from ..localization import tr


class NotesContextMenu:
    """Create and handle the context menu for the notes editor."""

    def __init__(
        self,
        web_view,
        script_manager,
        main_window,
    ):
        self.web_view = web_view
        self.scripts = script_manager
        self.main_window = main_window

    def show(self, pos):
        """Display the notes context menu."""
        
        menu = QMenu(self.web_view)

        action_cut = menu.addAction(
            tr("cut_ctrl_x")
        )

        action_copy = menu.addAction(
            tr("copy_ctrl_c")
        )

        action_paste = menu.addAction(
            tr("paste_ctrl_v")
        )

        menu.addSeparator()

        action_copy_prompt = menu.addAction(
            tr("copy_prompt_to_clipboard")
        )

        action_copy_pdf = menu.addAction(
            tr("copy_pdf_page_text_only")
        )

        selected = menu.exec(
            self.web_view.mapToGlobal(pos)
        )

        if selected == action_cut:
            self.scripts.cut_selected_text(
                self._handle_cut_result
            )

        elif selected == action_copy:
            self.scripts.get_selected_text(
                self._handle_copy_result
            )

        elif selected == action_paste:
            self._paste_from_clipboard()

        elif selected == action_copy_prompt:
            self._copy_prompt()

        elif selected == action_copy_pdf:
            self._copy_pdf_text()

    def _paste_from_clipboard(self):
        """Paste clipboard HTML or text into Quill."""
        
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        if (
            mime_data.hasHtml()
            and mime_data.html().strip()
        ):
            pasted_content = mime_data.html()

        elif (
            mime_data.hasText()
            and mime_data.text().strip()
        ):
            text = mime_data.text()

            pasted_content = "".join(
                f"<p>{line}</p>"
                if line
                else "<p><br></p>"
                for line in text.splitlines()
            )

        else:
            pasted_content = ""

        if pasted_content:
            self.scripts.paste_html(
                pasted_content
            )

            self._show_status(
                tr("clipboard_pasted")
            )

        else:
            self._show_status(
                tr("clipboard_empty")
            )

    def _copy_prompt(self):
        """Generate and copy the complete AI prompt."""
        
        self.main_window._save_current_note_for_page(
            self.main_window._notes_page
        )

        prompt_text = (
            self.main_window
            .generate_full_ai_prompt_text()
        )

        if prompt_text:
            QGuiApplication.clipboard().setText(
                prompt_text
            )

            self._show_status(
                tr("prompt_copied_to_clipboard")
            )

        else:
            self._show_status(
                tr("open_pdf_file_first")
            )

    def _copy_pdf_text(self):
        """Copy text from the currently visible PDF page."""
        
        text = (
            self.main_window
            .get_pdf_text_for_current_page()
        )

        if text:
            QGuiApplication.clipboard().setText(
                text
            )

            self._show_status(
                tr("pdf_page_text_copied")
            )

        else:
            self._show_status(
                tr("no_text_on_this_pdf_page")
            )

    def _handle_copy_result(self, text):
        """Copy selected Quill text to the clipboard."""
        
        if text:
            QGuiApplication.clipboard().setText(
                text
            )

            self._show_status(
                tr("selected_text_copied")
            )

        else:
            self._show_status(
                tr("no_selected_text_to_copy")
            )

    def _handle_cut_result(self, text):
        """Copy cut Quill text to the clipboard."""
        
        if text:
            QGuiApplication.clipboard().setText(
                text
            )

            self._show_status(
                tr("selected_text_cut")
            )

        else:
            self._show_status(
                tr("no_selected_text_to_cut")
            )

    def _show_status(self, message):
        """Display a temporary message in MainWindow's status bar."""
        
        self.main_window.statusBar().showMessage(
            message,
            3000,
        )