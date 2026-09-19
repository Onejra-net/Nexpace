# Main Window Architecture

```mermaid
flowchart TD

    MainWindow["main_window.py<br/>MainWindow<br/><br/>Responsible for:<br/>• application-level coordination<br/>• PDF state<br/>• notes state<br/>• connecting managers<br/>• handling PDF/page events<br/>• AI prompt generation<br/>• application shutdown"]

    DockManager["window/dock_manager.py<br/>DockManager<br/><br/>Responsible for:<br/>• creating docks<br/>• AI assistant docks<br/>• custom link docks<br/>• dock tab management<br/>• QTabBar close handling"]

    MenuManager["window/menu_manager.py<br/>MenuManager<br/><br/>Responsible for:<br/>• application menus<br/>• View menu<br/>• AI assistant menu<br/>• language menu<br/>• menu actions"]

    WorkspaceManager["window/workspace_manager.py<br/>WorkspaceManager<br/><br/>Responsible for:<br/>• saving workspace<br/>• restoring workspace<br/>• dock state<br/>• window geometry<br/>• last opened PDF"]

    NotesManager["window/notes_manager.py<br/>NotesManager<br/><br/>Responsible for:<br/>• loading notes<br/>• saving notes<br/>• page-specific notes<br/>• notes persistence"]

    MainWindow --> DockManager
    MainWindow --> MenuManager
    MainWindow --> WorkspaceManager
    MainWindow --> NotesManager