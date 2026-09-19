"""Browser panel components."""

from .browser_toolbar import BrowserToolbar
from .browser_view import BrowserWebView
from .browser_navigation import BrowserNavigation
from .browser_scripts import BrowserScriptManager
from .browser_context_menu import BrowserContextMenu

__all__ = [
    "BrowserToolbar",
    "BrowserWebView",
    "BrowserNavigation",
    "BrowserScriptManager",
    "BrowserContextMenu",
]