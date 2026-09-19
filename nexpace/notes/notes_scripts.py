import json

from ..localization import tr


class NotesScriptManager:
    """Manage JavaScript operations for the Quill notes editor."""

    def __init__(self, web_view):
        self.web_view = web_view

    def update_placeholder(self):
        """Update the Quill placeholder using the current application language."""
        
        placeholder = json.dumps(
            tr("write_your_notes")
        )

        js = f"""
        (function() {{
            const placeholderText = {placeholder};

            let attempts = 0;
            const maxAttempts = 40;

            function applyPlaceholder() {{
                if (
                    typeof quill !== 'undefined' &&
                    quill.root
                ) {{
                    quill.root.setAttribute(
                        'data-placeholder',
                        placeholderText
                    );
                    return;
                }}

                if (attempts < maxAttempts) {{
                    attempts++;
                    setTimeout(
                        applyPlaceholder,
                        50
                    );
                }}
            }}

            applyPlaceholder();
        }})();
        """

        self.web_view.page().runJavaScript(js)

    def set_html(self, html_content):
        """Replace the current Quill document with HTML."""
        
        safe_html = json.dumps(
            html_content or ""
        )

        js = f"""
        quill.clipboard.dangerouslyPasteHTML(
            {safe_html}
        );

        updateStats();
        """

        self.web_view.page().runJavaScript(js)

    def get_selected_text(self, callback):
        """Return the currently selected plain text from Quill."""
        
        js = """
        (function() {
            let range = quill.getSelection();

            if (!range || range.length === 0) {
                return "";
            }

            return quill.getText(
                range.index,
                range.length
            );
        })();
        """

        self.web_view.page().runJavaScript(
            js,
            callback,
        )

    def cut_selected_text(self, callback):
        """Cut the current Quill selection and return its text."""
        
        js = """
        (function() {
            let range = quill.getSelection();

            if (!range || range.length === 0) {
                return "";
            }

            let text = quill.getText(
                range.index,
                range.length
            );

            quill.deleteText(
                range.index,
                range.length
            );

            return text;
        })();
        """

        self.web_view.page().runJavaScript(
            js,
            callback,
        )

    def paste_html(self, html_content):
        """Insert HTML at the current Quill cursor position."""
        
        safe_content = json.dumps(
            html_content or ""
        )

        js = f"""
        (function() {{
            let range = quill.getSelection();

            let index =
                range
                    ? range.index
                    : quill.getLength();

            quill.clipboard.dangerouslyPasteHTML(
                index,
                {safe_content}
            );
        }})();
        """

        self.web_view.page().runJavaScript(js)