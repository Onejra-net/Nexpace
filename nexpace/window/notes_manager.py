import json
from pathlib import Path
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QMessageBox, QFileDialog
from ..localization import tr



class NotesManager:
    def __init__(self, main_window):
        self.mw = main_window


    def save_current_note_for_page(self, page):
        if not self.mw.pdf_path or self.mw.loading_notes or page is None:
            return

        key = str(page + 1)
        html_text = self.mw.notes_editor.getHtmlSync()

        if not html_text or html_text == "<p><br></p>":
            self.mw.notes.pop(key, None)
        else:
            if "%3Cp%3E%3Cp%3E" in html_text or "%253Cp" in html_text:
                self.mw.notes.pop(key, None)
            else:
                doc = QTextDocument()
                doc.setHtml(html_text)
                plain_text = doc.toPlainText().strip()
                if plain_text:
                    self.mw.notes[key] = html_text
                else:
                    self.mw.notes.pop(key, None)

        self.save_notes_to_disk()


    def load_notes(self):
        self.mw.notes = {}
        if self.mw.notes_path and self.mw.notes_path.exists():
            try:
                data = json.loads(self.mw.notes_path.read_text(encoding="utf-8"))
                self.mw.notes = data if isinstance(data, dict) else {}
            except Exception:
                QMessageBox.warning(self, tr("notes_title"), tr('notes_file_corrupted'))


    def save_notes_to_disk(self):
        if not self.mw.pdf_path or not self.mw.notes_path:
            return
        try:
            self.mw.notes_path.write_text(
                json.dumps(self.mw.notes, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            self.mw.statusBar().showMessage(tr("notes.save_error", exc=exc), 5000)


    def save_notes(self):
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first'))
            return

        self.save_current_note_for_page(self.mw._notes_page)
        self.mw.statusBar().showMessage(tr('notes_saved_successfully'), 3000)


    def save_notes_as(self):
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first'))
            return

        self.save_current_note_for_page(self.mw._notes_page)

        suggested_name = tr("suggested_notes_filename", stem=self.mw.pdf_path.stem)
        file_path, _ = QFileDialog.getSaveFileName(
            self.mw,
            tr('export_save_notes_as'),
            suggested_name,
            tr('json_html_file_filter')
        )

        if not file_path:
            return

        try:
            path = Path(file_path)
            if path.suffix.lower() == ".html":
                html_out = "<html><head><meta charset='utf-8'></head><body>"
                html_out += f"<h1>{tr('notes.html_title', name=self.mw.pdf_path.name)}</h1><hr>"
                for page, content in sorted(self.mw.notes.items(), key=lambda x: int(x[0])):
                    html_out += f"<h2>{tr('notes.html_page', page=page)}</h2>{content}<br>"
                html_out += "</body></html>"
                path.write_text(html_out, encoding="utf-8")
            else:
                path.write_text(json.dumps(self.mw.notes, ensure_ascii=False, indent=2), encoding="utf-8")

            self.mw.statusBar().showMessage(tr("notes.exported", name=path.name), 4000)
        except Exception as exc:
            QMessageBox.critical(self, tr('save_error'), tr("notes.file_write_error", exc=exc))


    def load_notes_from_external_file(self):
        if not self.mw.pdf_path:
            QMessageBox.information(self, tr("notes_title"), tr('open_pdf_first_to_link_notes'))
            return

        file_path, _ = QFileDialog.getOpenFileName(self.mw, tr('load_import_notes_2'), "", tr('json_file_filter'))
        if not file_path:
            return

        try:
            path = Path(file_path)
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                QMessageBox.warning(self, tr('import_error'), tr('invalid_json_page_dict'))
                return

            self.mw.notes = data
            self.save_notes_to_disk()

            if self.mw._notes_page is not None:
                self.mw._finish_note_page(self.mw._notes_page, self.mw._note_switch_serial)

            self.mw.statusBar().showMessage(tr("notes.loaded", name=path.name), 4000)
        except Exception as exc:
            QMessageBox.critical(self, tr('read_error'), tr("notes.file_read_error", exc=exc))