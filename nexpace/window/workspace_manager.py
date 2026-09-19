import base64
import json
from pathlib import Path
from PySide6.QtCore import Qt, QByteArray, QTimer
from PySide6.QtWidgets import QTabBar

from .. import localization
from ..localization import set_language



class WorkspaceManager:
    WORKSPACE_VERSION = 7

    def __init__(self, main_window):
        self.mw = main_window
        self.workspace_path = localization.get_base_path() / "workspace.json"
        self.restoring_workspace = False

        self.timer = QTimer(main_window)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.autosave_workspace)
        self.timer.start()


    def workspace_state(self):
        return bytes(self.mw.saveState(self.WORKSPACE_VERSION).data())


    def autosave_workspace(self):
        if self.restoring_workspace:
            return
        try:
            state = self.workspace_state()
            geometry = bytes(self.mw.saveGeometry().data())

            data = {
                "version": self.WORKSPACE_VERSION,
                "geometry": base64.b64encode(geometry).decode("ascii"),
                "dock_state": base64.b64encode(state).decode("ascii"),
                "last_pdf_path": str(self.mw.pdf_path) if self.mw.pdf_path else None,
                "custom_links": self.mw.custom_links,
                "language": localization.CURRENT_LANGUAGE,
            }
            tmp = self.workspace_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.workspace_path)
        except Exception as exc:
            print(f"[workspace] autosave failed: {exc}")


    def restore_workspace(self):
        if not self.workspace_path.exists():
            return
        try:
            data = json.loads(self.workspace_path.read_text(encoding="utf-8"))
            geometry = base64.b64decode(data.get("geometry", ""))
            state = base64.b64decode(data.get("dock_state", ""))
            last_pdf = data.get("last_pdf_path")
            saved_links = data.get("custom_links")
            saved_language = data.get("language")

            self.restoring_workspace = True

            if saved_language in ("pl", "en"):
                set_language(saved_language)

            if saved_links and isinstance(saved_links, list):
                self.mw.custom_links = saved_links
                self.mw.dock_manager.sync_links_and_docks()

            if geometry:
                self.mw.restoreGeometry(QByteArray(geometry))
            if state:
                self.mw.restoreState(QByteArray(state), self.WORKSPACE_VERSION)

            if last_pdf and Path(last_pdf).exists():
                self.mw.pdf_panel.open_file(last_pdf)

        except Exception as exc:
            print(f"[workspace] restore failed: {exc}")
        finally:
            self.restoring_workspace = False
            for tab_bar in self.mw.findChildren(QTabBar):
                self.mw.dock_manager.configure_tabbar(tab_bar)

            try:
                self.mw.apply_language_to_ui()
            except Exception as exc:
                print(f"[workspace] language UI refresh failed: {exc}")


    def reset_workspace(self, save=True):
        self.restoring_workspace = True
        try:
            self.mw.pdf_dock.show()
            self.mw.notes_dock.show()
            self.mw.dock_manager.links_manager_dock.show()

            for dock in self.mw.dock_manager.ai_docks.values():
                dock.show()
            for dock in self.mw.dock_manager.link_docks.values():
                dock.hide()

            self.mw.addDockWidget(Qt.LeftDockWidgetArea, self.mw.pdf_dock)
            self.mw.addDockWidget(Qt.RightDockWidgetArea, self.mw.notes_dock)
            self.mw.addDockWidget(Qt.RightDockWidgetArea, self.mw.dock_manager.links_manager_dock)

            first_ai = None
            for dock in self.mw.dock_manager.ai_docks.values():
                if first_ai is None:
                    first_ai = dock
                    self.mw.splitDockWidget(self.mw.notes_dock, dock, Qt.Vertical)
                else:
                    self.mw.tabifyDockWidget(first_ai, dock)
        finally:
            self.restoring_workspace = False
            for tab_bar in self.mw.findChildren(QTabBar):
                self.mw.dock_manager.configure_tabbar(tab_bar)

        if save:
            self.autosave_workspace()