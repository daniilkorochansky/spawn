"""Unit tests for ShortcutParser using wx key-code constants only."""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest


class FakeWx(types.ModuleType):
    def __init__(self):
        super().__init__("wx")
        names = {
            "WXK_RETURN": 13,
            "WXK_ESCAPE": 27,
            "WXK_BACK": 8,
            "WXK_DELETE": 127,
            "WXK_INSERT": 1001,
            "WXK_HOME": 1002,
            "WXK_END": 1003,
            "WXK_PAGEUP": 1004,
            "WXK_PAGEDOWN": 1005,
            "WXK_UP": 1006,
            "WXK_DOWN": 1007,
            "WXK_LEFT": 1008,
            "WXK_RIGHT": 1009,
            "WXK_TAB": 9,
            "WXK_SPACE": 32,
            "WXK_NUMPAD_ENTER": 1010,
            "WXK_SHIFT": 2001,
            "WXK_ALT": 2002,
            "WXK_CONTROL": 2003,
            "WXK_COMMAND": 2004,
            "WXK_NONE": 0,
        }
        for name, value in names.items():
            setattr(self, name, value)
        for number in range(1, 25):
            setattr(self, f"WXK_F{number}", 3000 + number)


class FakeKeyEvent:
    def __init__(
        self,
        key_code,
        *,
        control=False,
        alt=False,
        shift=False,
        meta=False,
    ):
        self.key_code = key_code
        self.modifiers = (control, alt, shift, meta)

    def GetKeyCode(self):
        return self.key_code

    def ControlDown(self):
        return self.modifiers[0]

    def AltDown(self):
        return self.modifiers[1]

    def ShiftDown(self):
        return self.modifiers[2]

    def MetaDown(self):
        return self.modifiers[3]


@pytest.fixture
def parser(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    module_path = root / "core" / "shortcuts" / "shortcut_parser.py"
    wx_stub = FakeWx()
    monkeypatch.setitem(sys.modules, "wx", wx_stub)

    spec = importlib.util.spec_from_file_location(
        "_spawn_shortcut_parser_under_test",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.ShortcutParser(), wx_stub


def test_parse_simple_ascii_key(parser):
    shortcut_parser, wx = parser

    assert shortcut_parser.parse("A") == (frozenset(), ord("A"))
    assert shortcut_parser.parse("k") == (frozenset(), ord("K"))


def test_parse_modifiers_and_normalize_modifier_aliases(parser):
    shortcut_parser, _ = parser

    assert shortcut_parser.parse("Ctrl+Shift+K") == (
        frozenset({"CTRL", "SHIFT"}),
        ord("K"),
    )
    assert shortcut_parser.parse("Control+Alt+F2") == (
        frozenset({"CTRL", "ALT"}),
        3002,
    )
    assert shortcut_parser.parse("RawCtrl+Cmd+X") == (
        frozenset({"CTRL", "META"}),
        ord("X"),
    )


def test_parse_special_key_aliases(parser):
    shortcut_parser, wx = parser

    assert shortcut_parser.parse("Enter") == (frozenset(), wx.WXK_RETURN)
    assert shortcut_parser.parse("Esc") == (frozenset(), wx.WXK_ESCAPE)
    assert shortcut_parser.parse("PageUp") == (frozenset(), wx.WXK_PAGEUP)
    assert shortcut_parser.parse("NumpadEnter") == (
        frozenset(),
        wx.WXK_NUMPAD_ENTER,
    )


def test_parse_none_returns_none(parser):
    shortcut_parser, _ = parser
    assert shortcut_parser.parse(None) is None


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "Ctrl++A",
        "+A",
        "Ctrl+",
        "Ctrl+Alt",
        "Ctrl+A+B",
        "Ctrl+Ctrl+A",
        "Ctrl+Control+A",
        "F25",
        "AB",
        "Ж",
        "Ctrl+Ж",
    ],
)
def test_parse_rejects_invalid_shortcuts(parser, value):
    shortcut_parser, _ = parser

    with pytest.raises(ValueError):
        shortcut_parser.parse(value)


def test_parse_rejects_non_string_value(parser):
    shortcut_parser, _ = parser

    with pytest.raises(ValueError, match="must be a string"):
        shortcut_parser.parse(42)


def test_parse_all_function_key_range(parser):
    shortcut_parser, _ = parser

    for number in range(1, 25):
        assert shortcut_parser.parse(f"F{number}") == (
            frozenset(),
            3000 + number,
        )


def test_from_event_normalizes_ascii_letter_case_and_modifiers(parser):
    shortcut_parser, _ = parser
    event = FakeKeyEvent(
        ord("c"),
        control=True,
        shift=True,
        meta=True,
    )

    assert shortcut_parser.from_event(event) == (
        frozenset({"CTRL", "SHIFT", "META"}),
        ord("C"),
    )


def test_from_event_preserves_non_letter_key_code(parser):
    shortcut_parser, wx = parser
    event = FakeKeyEvent(wx.WXK_RETURN, alt=True)

    assert shortcut_parser.from_event(event) == (
        frozenset({"ALT"}),
        wx.WXK_RETURN,
    )


@pytest.mark.parametrize("key_name", ["WXK_SHIFT", "WXK_ALT", "WXK_CONTROL", "WXK_COMMAND", "WXK_NONE"])
def test_from_event_ignores_modifier_and_empty_key_events(parser, key_name):
    shortcut_parser, wx = parser

    assert shortcut_parser.from_event(FakeKeyEvent(getattr(wx, key_name))) is None


def test_format_uses_stable_modifier_order(parser):
    shortcut_parser, _ = parser
    signature = (frozenset({"META", "SHIFT", "ALT", "CTRL"}), ord("Z"))

    assert shortcut_parser.format(signature) == "Ctrl+Alt+Shift+Cmd+Z"


def test_format_special_and_function_keys(parser):
    shortcut_parser, wx = parser

    assert shortcut_parser.format((frozenset({"CTRL"}), wx.WXK_RETURN)) == "Ctrl+Return"
    assert shortcut_parser.format((frozenset(), 3024)) == "F24"


def test_format_ascii_and_unknown_key_codes(parser):
    shortcut_parser, _ = parser

    assert shortcut_parser.format((frozenset(), ord("q"))) == "Q"
    assert shortcut_parser.format((frozenset(), 99999)) == "99999"


def test_format_none_returns_empty_string(parser):
    shortcut_parser, _ = parser
    assert shortcut_parser.format(None) == ""
