"""
Application workspace persistence management.

Responsible for:
- Automatically saving the workspace state
- Preserving window geometry and dock layout
- Storing the last PDF, custom links, and language
- Restoring the previous application session
- Resetting the default dock arrangement
"""

import base64
import json
from pathlib import Path

from PySide6.QtCore import Qt, QByteArray, QTimer
from PySide6.QtWidgets import QTabBar

from .. import localization
from ..localization import set_language


class WorkspaceManager:
    """
    Coordinator for workspace persistence and restoration.

    Manages workspace serialization, periodic autosaving,
    session restoration, and default layout recovery.
    """

    # Qt workspace state format version:
    WORKSPACE_VERSION = 7

    def __init__(self, main_window):

        # Main window reference:
        self.mw = main_window

        # Workspace storage:
        self.workspace_path = localization.get_base_path() / "workspace.json"

        # Workspace restoration state:
        self.restoring_workspace = False

        # Periodic workspace autosave:
        # - Save the current application state every 500 ms.
        self.timer = QTimer(main_window)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.autosave_workspace)
        self.timer.start()

    def workspace_state(self):
        """
        Serialize the current Qt dock layout into bytes.
        """

        return bytes(self.mw.saveState(self.WORKSPACE_VERSION).data())

    def autosave_workspace(self):
        """
        Persist the current workspace configuration to a JSON file.
        """

        # Prevent autosaving during workspace restoration:
        if self.restoring_workspace:
            return

        try:
            # Capture window geometry and dock layout:
            state = self.workspace_state()
            geometry = bytes(self.mw.saveGeometry().data())

            # Serialize workspace configuration:
            # - Encode binary Qt state as Base64 for JSON storage.
            data = {
                "version": self.WORKSPACE_VERSION,
                "geometry": base64.b64encode(geometry).decode("ascii"),
                "dock_state": base64.b64encode(state).decode("ascii"),
                "last_pdf_path": str(self.mw.pdf_path) if self.mw.pdf_path else None,
                "custom_links": self.mw.custom_links,
                "language": localization.CURRENT_LANGUAGE,
            }

            # Write to a temporary file before replacing the workspace:
            tmp = self.workspace_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.workspace_path)

        # Report workspace saving failures:
        except Exception as exc:
            print(f"[workspace] autosave failed: {exc}")

    def restore_workspace(self):
        """
        Restore the saved workspace configuration and application state.
        """

        # Skip restoration when no saved workspace exists:
        if not self.workspace_path.exists():
            return

        try:
            # Read and decode the saved workspace:
            data = json.loads(self.workspace_path.read_text(encoding="utf-8"))
            geometry = base64.b64decode(data.get("geometry", ""))
            state = base64.b64decode(data.get("dock_state", ""))
            last_pdf = data.get("last_pdf_path")
            saved_links = data.get("custom_links")
            saved_language = data.get("language")

            # Suspend autosaving during restoration:
            self.restoring_workspace = True

            # Restore the saved application language:
            if saved_language in ("pl", "en"):
                set_language(saved_language)

            # Restore custom links and their browser docks:
            if saved_links and isinstance(saved_links, list):
                self.mw.custom_links = saved_links
                self.mw.dock_manager.sync_links_and_docks()

            # Restore window geometry and dock arrangement:
            if geometry:
                self.mw.restoreGeometry(QByteArray(geometry))
            if state:
                self.mw.restoreState(QByteArray(state), self.WORKSPACE_VERSION)

            # Reopen the last available PDF document:
            if last_pdf and Path(last_pdf).exists():
                self.mw.pdf_panel.open_file(last_pdf)

        # Report workspace restoration failures:
        except Exception as exc:
            print(f"[workspace] restore failed: {exc}")

        finally:
            # Resume workspace autosaving:
            self.restoring_workspace = False

            # Reconfigure dock tab controls after restoration:
            for tab_bar in self.mw.findChildren(QTabBar):
                self.mw.dock_manager.configure_tabbar(tab_bar)

            # Refresh the interface using the restored language:
            try:
                self.mw.apply_language_to_ui()
            except Exception as exc:
                print(f"[workspace] language UI refresh failed: {exc}")

    def reset_workspace(self, save=True):
        """
        Restore the default dock layout and optionally save its state.
        """

        # Suspend autosaving during layout reset:
        self.restoring_workspace = True

        try:
            # Restore primary application dock visibility:
            self.mw.pdf_dock.show()
            self.mw.notes_dock.show()
            self.mw.dock_manager.links_manager_dock.show()

            # Show default AI docks:
            for dock in self.mw.dock_manager.ai_docks.values():
                dock.show()

            # Hide custom browser docks:
            for dock in self.mw.dock_manager.link_docks.values():
                dock.hide()

            # Restore primary dock placement:
            self.mw.addDockWidget(Qt.LeftDockWidgetArea, self.mw.pdf_dock)
            self.mw.addDockWidget(Qt.RightDockWidgetArea, self.mw.notes_dock)
            self.mw.addDockWidget(Qt.RightDockWidgetArea, self.mw.dock_manager.links_manager_dock)

            # Rebuild the default AI dock arrangement:
            first_ai = None
            for dock in self.mw.dock_manager.ai_docks.values():

                # Position the first AI dock below the notes panel:
                if first_ai is None:
                    first_ai = dock
                    self.mw.splitDockWidget(self.mw.notes_dock, dock, Qt.Vertical)

                # Group remaining AI docks into tabs:
                else:
                    self.mw.tabifyDockWidget(first_ai, dock)

        finally:
            # Resume workspace autosaving:
            self.restoring_workspace = False

            # Restore dock tab close handlers:
            for tab_bar in self.mw.findChildren(QTabBar):
                self.mw.dock_manager.configure_tabbar(tab_bar)

        # Persist the reset layout if requested:
        if save:
            self.autosave_workspace()
