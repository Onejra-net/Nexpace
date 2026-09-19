import base64
import json


class PdfScriptManager:
    """Manage JavaScript injected into the PDF.js viewer."""

    def __init__(self, web_view):
        self.web_view = web_view

    def inject_dark_scrollbar(self):
        """Inject dark scrollbar styling into PDF.js."""
        css = """
        const style = document.createElement('style');

        style.innerHTML = `
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }

            ::-webkit-scrollbar-track {
                background: #1e1e1e !important;
            }

            ::-webkit-scrollbar-thumb {
                background: #424242 !important;
                border-radius: 5px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #4f4f4f !important;
            }
        `;

        document.head.appendChild(style);
        """

        self.web_view.page().runJavaScript(css)

    def check_viewer_ready(self, callback):
        """Check whether PDF.js exposes its main application object."""
        code = """
        Boolean(
            window.PDFViewerApplication &&
            typeof window.PDFViewerApplication.open === 'function'
        )
        """

        self.web_view.page().runJavaScript(
            code,
            callback,
        )

    def open_bytes_in_viewer(self, data):
        """Pass PDF bytes to PDF.js."""
        b64 = base64.b64encode(data).decode("ascii")

        code = f"""
        (() => {{
            const binary = atob(
                {json.dumps(b64)}
            );

            const bytes = new Uint8Array(
                binary.length
            );

            for (
                let i = 0;
                i < binary.length;
                i++
            ) {{
                bytes[i] = binary.charCodeAt(i);
            }}

            return PDFViewerApplication.open({{
                data: bytes
            }});
        }})()
        """

        self.web_view.page().runJavaScript(code)

    def install_page_event_hook(self):
        """
        Install a PDF.js event hook that reports page changes
        back to Qt through document.title.
        """
        code = r"""
        (() => {
            const app = window.PDFViewerApplication;

            if (!app) {
                return false;
            }

            const bus =
                app.eventBus ||
                (
                    app.pdfViewer &&
                    app.pdfViewer.eventBus
                );

            if (
                !bus ||
                typeof bus.on !== 'function'
            ) {
                return false;
            }

            function notifyQt(page) {
                const total =
                    (
                        app.pdfDocument &&
                        app.pdfDocument.numPages
                    ) || 0;

                document.title =
                    "QTPDF_PAGE:" +
                    page +
                    ":" +
                    total;
            }

            if (!window.__qtPdfJsPageHook) {
                window.__qtPdfJsPageHook = true;

                bus.on(
                    'pagechanging',
                    (evt) => {
                        const page = Number(
                            evt &&
                            evt.pageNumber
                        );

                        if (page > 0) {
                            notifyQt(page);
                        }
                    }
                );

                bus.on(
                    'pagesinit',
                    () => {
                        const page = Number(
                            (
                                app.pdfViewer &&
                                app.pdfViewer
                                    .currentPageNumber
                            ) ||
                            app.page ||
                            1
                        );

                        if (page > 0) {
                            notifyQt(page);
                        }
                    }
                );
            }

            return true;
        })()
        """

        self.web_view.page().runJavaScript(code)