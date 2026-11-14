
"""
Browser toolbar style.

Responsible for:
- Styling browser navigation buttons
- Defining button interaction states
- Styling the read-only URL display
- Maintaining a consistent dark interface
"""


# Browser navigation button styles:
BUTTON_STYLE = """
    /* Default button appearance */
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

    /* Hover state */
    QPushButton:hover {
        background-color: #444444;
    }

    /* Pressed state */
    QPushButton:pressed {
        background-color: #222222;
    }

    /* Disabled state */
    QPushButton:disabled {
        color: #666666;
        background-color: #2a2a2a;
    }
"""


# Browser URL bar styles:
URL_BAR_STYLE = """
    /* Read-only URL display appearance */
    QLineEdit {
        background-color: #2d2d2d;
        color: #aaaaaa;
        border: 1px solid #3c3c3c;
        padding: 2px 8px;
        border-radius: 4px;
        selection-background-color: #0e639c;
    }
"""
