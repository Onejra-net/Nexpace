"""
Quill notes editor WebEngine configuration.

Responsible for:
- Initializing the embedded Quill editor
- Loading Quill resources from the CDN
- Defining the editor layout, toolbar, and styling
- Tracking text statistics and HTML changes
- Reporting editor updates to Python through WebEngine events
"""

import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

from ..localization import tr
from ..web_engine import DebugWebEnginePage


class NotesWebView(QWebEngineView):
    """
    WebEngine view configured for the Quill notes editor.

    Provides the editor's HTML environment, visual configuration,
    and JavaScript events used for application communication.
    """

    # Quill CDN base URL:
    QUILL_URL = "https://cdn.jsdelivr.net"

    def __init__(self, parent=None):
        super().__init__(parent)

        # WebEngine page initialization:
        self.notes_page = DebugWebEnginePage(self)
        self.setPage(self.notes_page)

        # Enable the custom editor context menu:
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    @staticmethod
    def quill_html():
        """
        Generate the complete Quill editor HTML document.

        Configure editor resources, dark theme, formatting toolbar,
        text statistics, and HTML change notifications.
        """

        # Localized editor placeholder:
        placeholder = tr("write_your_notes")

        # Editor HTML, CSS, and JavaScript:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">

            <!-- Quill editor stylesheet -->
            <link
                href="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css"
                rel="stylesheet"
            />

            <!-- Quill editor JavaScript library -->
            <script
                src="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js">
            </script>

            <style>
                /* Main document appearance */
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    font-family: system-ui, -apple-system, sans-serif;
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }}

                /* Editor container dimensions */
                #editor-container {{
                    height: calc(100% - 42px);
                    background-color: #1e1e1e;
                }}

                /* Quill document styling */
                .ql-container {{
                    border: none !important;
                    font-size: 14px;
                    color: #d4d4d4;
                    background-color: #1e1e1e;
                }}

                /* Formatting toolbar appearance */
                .ql-toolbar.ql-snow {{
                    border: none !important;
                    border-bottom: 1px solid #2d2d2d !important;
                    background-color: #252526;
                }}

                /* Toolbar icons and controls */
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

                /* Active and hovered toolbar actions */
                .ql-snow button:hover .ql-stroke,
                .ql-snow button.ql-active .ql-stroke {{
                    stroke: #007acc !important;
                }}

                .ql-snow button:hover .ql-fill,
                .ql-snow button.ql-active .ql-fill {{
                    fill: #007acc !important;
                }}

                /* Empty editor placeholder */
                .ql-editor.ql-blank::before {{
                    color: #6e6e6e !important;
                    font-style: italic;
                }}

                /* Custom dark scrollbar */
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
            <!-- Quill editor mount point -->
            <div id="editor-container"></div>

            <script>
                // Initialize Quill with the formatting toolbar.
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

                // Calculate and report editor text statistics.
                function updateStats() {{
                    const text = quill.getText().trim();
                    const charCount = text.length;
                    const wordCount =
                        text === ""
                            ? 0
                            : text.split(/\\s+/).length;

                    // Send statistics through the URL fragment.
                    window.location.hash =
                        "stats:" +
                        charCount +
                        ":" +
                        wordCount;
                }}

                // Monitor Quill document changes.
                quill.on('text-change', function() {{
                    const html = quill.root.innerHTML;

                    // Refresh statistics after content changes.
                    updateStats();

                    // Report an empty document to Python.
                    if (
                        html === '<p><br></p>' ||
                        html === ''
                    ) {{
                        document.title =
                            "QUILL_HTML_URI:EMPTY";
                    }} else {{

                        // Encode and report the updated HTML content.
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
        """
        Load the Quill editor document into the WebEngine view.
        """

        # Initialize the editor using the Quill CDN base URL:
        self.setHtml(
            self.quill_html(),
            QUrl(self.QUILL_URL),
        )
