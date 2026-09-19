from PySide6.QtWebEngineCore import QWebEngineScript

from .scripts.scrollbar_script import SCROLLBAR_SCRIPT


class BrowserScriptManager:
    """Manages JavaScript injected into the embedded browser."""

    def __init__(self, web_page):
        self.web_page = web_page

    def install_global_script(self):
        """Install the scrollbar script at DocumentReady."""
        
        script = QWebEngineScript()

        script.setName("GlobalInjections")
        script.setSourceCode(
            SCROLLBAR_SCRIPT
        )

        script.setInjectionPoint(
            QWebEngineScript.InjectionPoint.DocumentReady
        )

        script.setWorldId(
            QWebEngineScript.ScriptWorldId.MainWorld
        )

        script.setRunsOnSubFrames(True)

        self.web_page.scripts().insert(script)

    def inject_on_load_finished(self, ok):
        """Apply the scrollbar script after a successful page load."""
        
        if not ok:
            return

        self.web_page.runJavaScript(
            SCROLLBAR_SCRIPT
        )