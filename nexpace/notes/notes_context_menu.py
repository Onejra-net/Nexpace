"""
Notes editor context menu management.

Responsible for:
- Creating the editor context menu
- Handling text cut, copy, and paste operations
- Managing clipboard interactions with Quill
- Copying AI prompts and PDF page text
- Displaying operation status messages
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMenu

from ..localization import tr


class NotesContextMenu:
    """
    Coordinator for notes editor context menu actions.

    Connects Quill editing operations, clipboard access,
    and application-specific PDF and AI functionality.
    """

    def __init__(
        self,
        web_view,
        script_manager,
        main_window,
    ):

        # Editor and application references:
        self.web_view = web_view
        self.scripts = script_manager
        self.main_window = main_window

    def show(self, pos):
        """
        Display the editor context menu and execute the selected action.
        """

        # Context menu initialization:
        menu = QMenu(self.web_view)

        # Text editing actions:
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

        # Application-specific clipboard actions:
        action_copy_prompt = menu.addAction(
            tr("copy_prompt_to_clipboard")
        )

        action_copy_pdf = menu.addAction(
            tr("copy_pdf_page_text_only")
        )

        # Display the menu at the requested position:
        selected = menu.exec(
            self.web_view.mapToGlobal(pos)
        )

        # Dispatch the selected menu action:
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
        """
        Retrieve clipboard content and paste it into the Quill editor.
        """

        # Access the system clipboard:
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        # Prefer formatted HTML content:
        if (
            mime_data.hasHtml()
            and mime_data.html().strip()
        ):
            pasted_content = mime_data.html()

        # Convert plain text into HTML paragraphs:
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

        # Handle an empty or unsupported clipboard:
        else:
            pasted_content = ""

        # Insert clipboard content into the editor:
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
        """
        Generate and copy the current PDF and notes context as an AI prompt.
        """

        # Save the active page note before generating the prompt:
        self.main_window._save_current_note_for_page(
            self.main_window._notes_page
        )

        # Generate the AI prompt from the current document context:
        prompt_text = (
            self.main_window
            .generate_full_ai_prompt_text()
        )

        # Copy the generated prompt to the system clipboard:
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
        """
        Copy the extracted text of the current PDF page to the clipboard.
        """

        # Retrieve text from the active PDF page:
        text = (
            self.main_window
            .get_pdf_text_for_current_page()
        )

        # Copy available PDF text:
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
        """Handle selected text returned by the Quill copy operation."""

        # Copy the selected text to the system clipboard:
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
        """
        Handle selected text returned by the Quill cut operation.
        """

        # Store the removed text in the system clipboard:
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
        """
        Display a temporary operation message in the application status bar.
        """

        # Show the message for three seconds:
        self.main_window.statusBar().showMessage(
            message,
            3000,
        )
