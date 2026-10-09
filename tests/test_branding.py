import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _theme_value(key):
    text = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    m = re.search(r'^\s*%s\s*=\s*"([^"]*)"' % key, text, re.MULTILINE)
    return m.group(1) if m else None


def test_tema_flock_configurado():
    assert _theme_value("primaryColor") == "#7F07C5"
    assert _theme_value("backgroundColor") == "#FFFFFF"
    assert _theme_value("secondaryBackgroundColor") == "#F7F4FA"
    assert _theme_value("textColor") == "#1F1F1F"


def test_assets_de_marca_existen():
    assert (ROOT / "assets" / "flock-logo-color.png").is_file()
    assert (ROOT / "assets" / "flock-isotipo.png").is_file()
