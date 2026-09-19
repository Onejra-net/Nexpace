"""Qt stylesheets used by the browser toolbar."""


BUTTON_STYLE = """
    QPushButton {
        background-color: #333333;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        font-weight: bold;
        min-width: 32px;
        min-height: 28px;
        padding: 0 6px;
    }

    QPushButton:hover {
        background-color: #444444;
    }

    QPushButton:pressed {
        background-color: #222222;
    }

    QPushButton:disabled {
        color: #666666;
        background-color: #2a2a2a;
    }
"""


URL_BAR_STYLE = """
    QLineEdit {
        background-color: #2d2d2d;
        color: #aaaaaa;
        border: 1px solid #3c3c3c;
        padding: 2px 8px;
        border-radius: 4px;
        selection-background-color: #0e639c;
    }
"""