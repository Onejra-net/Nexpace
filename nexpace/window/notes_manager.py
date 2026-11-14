"""
PDF-associated notes management.

Responsible for:
- Managing page-specific notes
- Validating and saving editor content
- Loading notes from JSON files
- Persisting notes to disk
- Exporting notes to JSON or HTML
- Importing notes from external JSON files
"""

import json
from pathlib import Path

from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QMessageBox, QFileDialog

from ..localization import tr


class NotesManager:
    """
    Coordinator for PDF-associated notes storage.

    Manages note validation, persistence, import,
    and export through the main application window.
    """

    def __init__(self, main_window):

        # Main window reference:
        self.mw = main_window

    def save_current_note_for_page(self, page):
        """
        Validate and persist the note associated with a PDF page.

        Store non-empty HTML content and remove empty or invalid
        note entries before saving the notes collection to disk.
        """

        # Skip saving without an active PDF or valid page:
        # - Prevent saving while notes are being loaded.
        if not self.mw.pdf_path or self.mw.loading_notes or page is None:
            return

        # Retrieve the page-specific HTML content:
        key = str(page + 1)
        html_text = self.mw.notes_editor.getHtmlSync()

        # Remove empty editor content:
        if not html_text or html_text == "<p><br></p>":
            self.mw.notes.pop(key, None)
        else:

            # Reject known malformed or encoded HTML patterns:
            if "%3Cp%3E%3Cp%3E" in html_text or "%253Cp" in html_text:
                self.mw.notes.pop(key, None)
            else:

                # Validate the HTML content as plain text:
                doc = QTextDocument()
                doc.setHtml(html_text)
                plain_text = doc.toPlainText().strip()

                # Preserve notes containing visible text:
                if plain_text:
                    self.mw.notes[key] = html_text
                else:
                    self.mw.notes.pop(key, None)

        # Persist the updated notes collection:
        self.save_notes_to_disk()

    def load_notes(self):
        """
        Load page-specific notes from the associated JSON file.
        """

        # Reset the current notes collection:
        self.mw.notes = {}

        # Load notes from the existing document storage:
        if self.mw.notes_path and self.mw.notes_path.exists():
            try:
                data = json.loads(self.mw.notes_path.read_text(encoding="utf-8"))
                self.mw.notes = data if isinstance(data, dict) else {}

            # Notify the user if the notes file cannot be loaded:
            except Exception:
                QMessageBox.warning(self, tr("notes_title"), tr('notes_file_corrupted'))

    def save_notes_to_disk(self):
        """
        Persist the current notes collection as a JSON file.
        """

        # Require an active PDF and associated notes path:
        if not self.mw.pdf_path or not self.mw.notes_path:
            return

        # Write the notes collection to disk:
        try:
            self.mw.notes_path.write_text(
                json.dumps(self.mw.notes, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # Report file writing errors:
        except Exception as exc:
            self.mw.statusBar().showMessage(tr("notes.save_error", exc=exc), 5000)

    def save_notes(self):
        """
        Save the current page note to the associated notes file.
        """

        # Require an opened PDF document:
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first'))
            return

        # Save the active page note:
        self.save_current_note_for_page(self.mw._notes_page)

        # Display save confirmation:
        self.mw.statusBar().showMessage(tr('notes_saved_successfully'), 3000)

    def save_notes_as(self):
        """
        Export the current notes collection to a JSON or HTML file.
        """

        # Require an opened PDF document:
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first'))
            return

        # Save the current note before exporting:
        self.save_current_note_for_page(self.mw._notes_page)

        # Request the export destination:
        suggested_name = tr("suggested_notes_filename", stem=self.mw.pdf_path.stem)
        file_path, _ = QFileDialog.getSaveFileName(
            self.mw,
            tr('export_save_notes_as'),
            suggested_name,
            tr('json_html_file_filter')
        )

        if not file_path:
            return

        # Export notes using the selected file format:
        try:
            path = Path(file_path)

            # HTML export:
            # - Combine page notes into a single HTML document.
            if path.suffix.lower() == ".html":
                html_out = "<html><head><meta charset='utf-8'></head><body>"
                html_out += f"<h1>{tr('notes.html_title', name=self.mw.pdf_path.name)}</h1><hr>"

                # Append notes in ascending PDF page order:
                for page, content in sorted(self.mw.notes.items(), key=lambda x: int(x[0])):
                    html_out += f"<h2>{tr('notes.html_page', page=page)}</h2>{content}<br>"

                html_out += "</body></html>"
                path.write_text(html_out, encoding="utf-8")

            # JSON export:
            # - Preserve the page-to-HTML mapping.
            else:
                path.write_text(json.dumps(self.mw.notes, ensure_ascii=False, indent=2), encoding="utf-8")

            # Confirm successful export:
            self.mw.statusBar().showMessage(tr("notes.exported", name=path.name), 4000)

        # Report export failures:
        except Exception as exc:
            QMessageBox.critical(self, tr('save_error'), tr("notes.file_write_error", exc=exc))

    def load_notes_from_external_file(self):
        """
        Import page-specific notes from an external JSON file.
        """

        # Require an opened PDF document:
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first_to_link_notes'))
            return

        # Request the JSON import file:
        file_path, _ = QFileDialog.getOpenFileName(
            self.mw,
            tr('load_import_notes_2'),
            "",
            tr('json_file_filter')
        )

        if not file_path:
            return

        # Read and validate the imported notes:
        try:
            path = Path(file_path)
            data = json.loads(path.read_text(encoding="utf-8"))

            # Require a dictionary of page-specific notes:
            if not isinstance(data, dict):
                QMessageBox.warning(self, tr('import_error'), tr('invalid_json_page_dict'))
                return

            # Replace and persist the active notes collection:
            self.mw.notes = data
            self.save_notes_to_disk()

            # Refresh the currently displayed page note:
            if self.mw._notes_page is not None:
                self.mw._finish_note_page(self.mw._notes_page, self.mw._note_switch_serial)

            # Confirm successful import:
            self.mw.statusBar().showMessage(tr("notes.loaded", name=path.name), 4000)

        # Report import failures:
        except Exception as exc:
            QMessageBox.critical(self, tr('read_error'), tr("notes.file_read_error", exc=exc))
