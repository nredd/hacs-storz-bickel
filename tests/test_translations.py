"""Structural parity checks for translation files.

Checks that every non-English translation file mirrors en.json in key/placeholder structure
"""

from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

TRANSLATIONS_DIR = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "storz_bickel"
    / "translations"
)
PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

NON_ENGLISH_FILES = sorted(
    path for path in TRANSLATIONS_DIR.glob("*.json") if path.stem != "en"
)


def _flatten(node: object, prefix: str = "") -> dict[str, str]:
    if isinstance(node, str):
        return {prefix: node}
    assert isinstance(node, dict), f"unexpected node type at {prefix!r}"
    flat: dict[str, str] = {}
    for key, value in node.items():
        assert isinstance(key, str), f"non-string key at {prefix!r}"
        flat.update(_flatten(value, f"{prefix}.{key}" if prefix else key))
    return flat


def _load_flat(path: Path) -> dict[str, str]:
    return _flatten(json.loads(path.read_text(encoding="utf-8")))


def test_translation_files_exist() -> None:
    assert (TRANSLATIONS_DIR / "en.json").is_file()
    assert (TRANSLATIONS_DIR / "de.json").is_file()


@pytest.mark.parametrize("path", NON_ENGLISH_FILES, ids=lambda p: p.stem)
def test_structure_matches_english(path: Path) -> None:
    """Non-English files have exactly the same nested keys as en.json."""
    english = _load_flat(TRANSLATIONS_DIR / "en.json")
    other = _load_flat(path)
    missing = sorted(set(english) - set(other))
    extra = sorted(set(other) - set(english))
    assert not missing, f"{path.name} is missing keys: {missing}"
    assert not extra, f"{path.name} has keys not in en.json: {extra}"


@pytest.mark.parametrize("path", NON_ENGLISH_FILES, ids=lambda p: p.stem)
def test_placeholders_match_english(path: Path) -> None:
    """Each translated string keeps the English {placeholder} tokens verbatim."""
    english = _load_flat(TRANSLATIONS_DIR / "en.json")
    other = _load_flat(path)
    for key, english_value in english.items():
        if key not in other:
            continue  # covered by test_structure_matches_english
        expected = sorted(PLACEHOLDER_RE.findall(english_value))
        actual = sorted(PLACEHOLDER_RE.findall(other[key]))
        assert actual == expected, (
            f"{path.name}: {key} has placeholders {actual}, expected {expected}"
        )
