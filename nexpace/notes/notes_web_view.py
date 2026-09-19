import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..localization import tr
from ..web_engine import DebugWebEnginePage


class NotesWebView(QWebEngineView):
    """QWebEngineView configured specifically for the Quill notes editor."""

    QUILL_URL = "https://cdn.jsdelivr.net"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.notes_page = DebugWebEnginePage(self)
        self.setPage(self.notes_page)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

    @staticmethod
    def quill_html():
        """Return the complete HTML document used by the Quill editor."""
        
        placeholder = tr("write_your_notes")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">

            <link
                href="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css"
                rel="stylesheet"
            />

            <script
                src="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js">
            </script>

            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    font-family: system-ui, -apple-system, sans-serif;
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }}

                #editor-container {{
                    height: calc(100% - 42px);
                    background-color: #1e1e1e;
                }}

                .ql-container {{
                    border: none !important;
                    font-size: 14px;
                    color: #d4d4d4;
                    background-color: #1e1e1e;
                }}

                .ql-toolbar.ql-snow {{
                    border: none !important;
                    border-bottom: 1px solid #2d2d2d !important;
                    background-color: #252526;
                }}

                .ql-snow .ql-stroke {{
                    stroke: #cccccc !important;
                }}

                .ql-snow .ql-fill {{
                    fill: #cccccc !important;
                }}

                .ql-snow .ql-picker {{
                    color: #cccccc !important;
                }}

                .ql-snow .ql-picker-options {{
                    background-color: #252526 !important;
                    border-color: #3c3c3c !important;
                }}

                .ql-snow button:hover .ql-stroke,
                .ql-snow button.ql-active .ql-stroke {{
                    stroke: #007acc !important;
                }}

                .ql-snow button:hover .ql-fill,
                .ql-snow button.ql-active .ql-fill {{
                    fill: #007acc !important;
                }}

                .ql-editor.ql-blank::before {{
                    color: #6e6e6e !important;
                    font-style: italic;
                }}

                ::-webkit-scrollbar {{
                    width: 10px;
                    height: 10px;
                }}

                ::-webkit-scrollbar-track {{
                    background: #1e1e1e !important;
                }}

                ::-webkit-scrollbar-thumb {{
                    background: #424242 !important;
                    border-radius: 5px;
                }}

                ::-webkit-scrollbar-thumb:hover {{
                    background: #4f4f4f !important;
                }}
            </style>
        </head>

        <body>
            <div id="editor-container"></div>

            <script>
                const quill = new Quill(
                    '#editor-container',
                    {{
                        theme: 'snow',
                        placeholder: {json.dumps(placeholder)},

                        modules: {{
                            toolbar: [
                                [{{ 'header': [1, 2, 3, false] }}],
                                [
                                    'bold',
                                    'italic',
                                    'underline',
                                    'strike'
                                ],
                                [
                                    {{ 'color': [] }},
                                    {{ 'background': [] }}
                                ],
                                [
                                    {{ 'list': 'ordered' }},
                                    {{ 'list': 'bullet' }}
                                ],
                                ['clean']
                            ]
                        }}
                    }}
                );

                function updateStats() {{
                    const text = quill.getText().trim();
                    const charCount = text.length;
                    const wordCount =
                        text === ""
                            ? 0
                            : text.split(/\\s+/).length;

                    window.location.hash =
                        "stats:" +
                        charCount +
                        ":" +
                        wordCount;
                }}

                quill.on('text-change', function() {{
                    const html = quill.root.innerHTML;

                    updateStats();

                    if (
                        html === '<p><br></p>' ||
                        html === ''
                    ) {{
                        document.title =
                            "QUILL_HTML_URI:EMPTY";
                    }} else {{
                        document.title =
                            "QUILL_HTML_URI:" +
                            encodeURIComponent(html);
                    }}
                }});
            </script>
        </body>
        </html>
        """

    def load_editor(self):
        """Load the Quill editor HTML."""
        self.setHtml(
            self.quill_html(),
            QUrl(self.QUILL_URL),
        )