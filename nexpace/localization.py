"""Localization and application-level path/version helpers.

This module owns the bilingual translation lookup and the small helpers that
resolve resources consistently in both source and frozen executable modes.
"""
import json
import sys
from pathlib import Path

_TRANSLATIONS_FILE = Path(__file__).resolve().parent.parent / "translations.json"

try:
    with _TRANSLATIONS_FILE.open("r", encoding="utf-8") as _translation_file:
        TRANSLATIONS = json.load(_translation_file)
except Exception:
    TRANSLATIONS = {}

CURRENT_LANGUAGE = "en"


def set_language(language):
    """Set the application language for subsequently translated UI strings."""
    global CURRENT_LANGUAGE
    if language in ("pl", "en"):
        CURRENT_LANGUAGE = language


def tr(key, **kwargs):
    """Return a translated string and safely format its placeholders."""
    entry = TRANSLATIONS.get(key, {})
    value = entry.get(CURRENT_LANGUAGE, entry.get("pl", key))
    try:
        return value.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return value


def get_base_path():
    """Return the application directory for both source and frozen builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def get_app_version():
    """Read the application version from the external version.txt file."""
    version_file = get_base_path() / "version.txt"
    if version_file.exists():
        try:
            return version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return "1.0.0-dev"
