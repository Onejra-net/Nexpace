
"""
Quill editor JavaScript integration management.

Responsible for:
- Updating the localized editor placeholder
- Replacing editor content with HTML
- Retrieving selected text from Quill
- Cutting selected text from the editor
- Inserting HTML at the current cursor position
"""

import json

from ..localization import tr


class NotesScriptManager:
    """
    Coordinator for JavaScript operations in Quill.

    Executes scripts in the embedded WebEngine view
    and provides editor operations to Python components.
    """

    def __init__(self, web_view):

        # Quill editor web view reference:
        self.web_view = web_view

    def update_placeholder(self):
        """
        Update the Quill placeholder for the active application language.

        Retry initialization until the editor becomes available
        or the maximum number of attempts is reached.
        """

        # Serialize the translated placeholder for JavaScript:
        placeholder = json.dumps(
            tr("write_your_notes")
        )

        # Placeholder initialization script:
        js = f"""
        (function() {{
            const placeholderText = {placeholder};

            let attempts = 0;
            const maxAttempts = 40;

            // Apply the placeholder when Quill is available.
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

                // Retry while the editor is initializing.
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

        # Execute the placeholder update:
        self.web_view.page().runJavaScript(js)

    def set_html(self, html_content):
        """
        Replace the current Quill document and refresh its statistics.
        """

        # Serialize HTML content for JavaScript:
        safe_html = json.dumps(
            html_content or ""
        )

        # Replace editor content and update statistics:
        js = f"""
        quill.clipboard.dangerouslyPasteHTML(
            {safe_html}
        );

        updateStats();
        """

        self.web_view.page().runJavaScript(js)

    def get_selected_text(self, callback):
        """
        Retrieve the selected plain text from the Quill editor.
        """

        # Selected text extraction script:
        js = """
        (function() {
            let range = quill.getSelection();

            // Ignore empty selections.
            if (!range || range.length === 0) {
                return "";
            }

            // Return the selected text to Python.
            return quill.getText(
                range.index,
                range.length
            );
        })();
        """

        # Execute JavaScript and forward its result to the callback:
        self.web_view.page().runJavaScript(
            js,
            callback,
        )

    def cut_selected_text(self, callback):
        """
        Remove selected Quill text and return it through a callback.
        """

        # Selected text removal script:
        js = """
        (function() {
            let range = quill.getSelection();

            // Ignore empty selections.
            if (!range || range.length === 0) {
                return "";
            }

            // Retrieve the selected text.
            let text = quill.getText(
                range.index,
                range.length
            );

            // Remove the selected content from Quill.
            quill.deleteText(
                range.index,
                range.length
            );

            // Return the removed text to Python.
            return text;
        })();
        """

        # Execute the cut operation and return the result:
        self.web_view.page().runJavaScript(
            js,
            callback,
        )

    def paste_html(self, html_content):
        """
        Insert HTML content at the current Quill cursor position.
        """

        # Serialize HTML content for JavaScript:
        safe_content = json.dumps(
            html_content or ""
        )

        # Determine insertion position and paste HTML:
        js = f"""
        (function() {{
            let range = quill.getSelection();

            // Use the cursor position or append to the document.
            let index =
                range
                    ? range.index
                    : quill.getLength();

            // Insert HTML at the selected position.
            quill.clipboard.dangerouslyPasteHTML(
                index,
                {safe_content}
            );
        }})();
        """

        # Execute the HTML insertion:
        self.web_view.page().runJavaScript(js)
