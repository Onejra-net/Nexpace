"""
Application localization and resource helpers.

Responsible for:
- Loading translations from JSON
- Managing the current application language
- Translating and formatting UI strings
- Resolving application paths
- Reading the application version
"""

import json
import sys
from pathlib import Path


# Translation file location:
_TRANSLATIONS_FILE = Path(__file__).resolve().parent.parent / "translations.json"

# Translation initialization:
# - Load translations from the JSON file.
# - Use an empty dictionary if loading fails.
try:
    with _TRANSLATIONS_FILE.open("r", encoding="utf-8") as _translation_file:
        TRANSLATIONS = json.load(_translation_file)
except Exception:
    TRANSLATIONS = {}

# Default application language:
CURRENT_LANGUAGE = "en"



def set_language(language):
    """
    Set the active language for subsequent translations.
    """

    # Accept supported languages only:
    global CURRENT_LANGUAGE
    if language in ("pl", "en"):
        CURRENT_LANGUAGE = language


def tr(key, **kwargs):
    """
    Resolve and format a translated UI string.

    Retrieve the translation for the active language,
    fall back to Polish or the original key when unavailable,
    and apply optional formatting parameters.
    """

    # Translation lookup:
    entry = TRANSLATIONS.get(key, {})
    value = entry.get(CURRENT_LANGUAGE, entry.get("pl", key))

    # Placeholder formatting:
    # - Return the original value if formatting fails.
    try:
        return value.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return value


def get_base_path():
    """
    Resolve the application base directory.

    !!! Support both Python source execution and frozen executables !!!
    """

    # Packaged executable directory:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    # Source project directory:
    return Path(__file__).resolve().parent.parent


def get_app_version():
    """
    Retrieve the application version from version.txt.

    Return the development version if the file is missing
    or cannot be read.
    """

    # Version file location:
    version_file = get_base_path() / "version.txt"

    # Read the external version:
    if version_file.exists():
        try:
            return version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    # Fallback development version:
    return "1.0.0-dev"
