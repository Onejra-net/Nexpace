"""
Browser JavaScript injection management.

Responsible for:
- Registering global browser scripts
- Configuring script execution timing and context
- Applying custom scrollbar styling
- Reapplying scripts after successful page loads
"""

from PySide6.QtWebEngineCore import QWebEngineScript

from .scripts.scrollbar_script import SCROLLBAR_SCRIPT


class BrowserScriptManager:
    """
    Coordinator for browser JavaScript injection.

    Registers persistent WebEngine scripts and executes
    additional injections after page loading.
    """

    def __init__(self, web_page):

        # Browser WebEngine page reference:
        self.web_page = web_page

    def install_global_script(self):
        """
        Register the scrollbar script for automatic document injection.
        """

        # WebEngine script initialization:
        script = QWebEngineScript()

        # Script identification and source:
        script.setName("GlobalInjections")
        script.setSourceCode(
            SCROLLBAR_SCRIPT
        )

        # Script execution timing:
        # - Inject when the document becomes ready.
        script.setInjectionPoint(
            QWebEngineScript.InjectionPoint.DocumentReady
        )

        # JavaScript execution context:
        # - Run in the page's main JavaScript world.
        script.setWorldId(
            QWebEngineScript.ScriptWorldId.MainWorld
        )

        # Apply the script to embedded frames:
        script.setRunsOnSubFrames(True)

        # Register the script with the WebEngine page:
        self.web_page.scripts().insert(script)

    def inject_on_load_finished(self, ok):
        """
        Execute the scrollbar script after a successful page load.
        """

        # Ignore unsuccessful page loads:
        if not ok:
            return

        # Apply scrollbar styling to the loaded page:
        self.web_page.runJavaScript(
            SCROLLBAR_SCRIPT
        )
