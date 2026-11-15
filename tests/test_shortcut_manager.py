"""Tests for ShortcutManager without creating real wxPython windows.

The parser is replaced deliberately: these tests target binding, context,
conflict and dispatch behaviour, not ShortcutParser's syntax rules.
"""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.shortcuts.command_registry import CommandRegistry, ShortcutCommand


class FakeParser:
    def parse(self, shortcut):
        if not isinstance(shortcut, str) or shortcut.startswith("INVALID"):
            raise ValueError("Invalid shortcut")
        return shortcut.strip().lower()

    def format(self, signature):
        return signature

    def from_event(self, event):
        return getattr(event, "signature", None)


class FakeCommandEvent:
    def __init__(self, event_type, event_id):
        self.event_type = event_type
        self.event_id = event_id
        self.event_object = None

    def SetEventObject(self, value):
        self.event_object = value


class FakeWindow:
    focus = None

    @staticmethod
    def FindFocus():
        return FakeWindow.focus


class FakeTextInput:
    pass


class FakeWx(types.ModuleType):
    def __init__(self):
        super().__init__("wx")
        self.EVT_CHAR_HOOK = object()
        self.EVT_MENU_OPEN = object()
        self.EVT_MENU = SimpleNamespace(typeId=501)
        self.Window = FakeWindow
        self.CommandEvent = FakeCommandEvent
        self.TextCtrl = FakeTextInput
        self.SearchCtrl = type("FakeSearchCtrl", (FakeTextInput,), {})
        self.ComboBox = type("FakeComboBox", (FakeTextInput,), {})
        self.ComboCtrl = type("FakeComboCtrl", (FakeTextInput,), {})
        self.SpinCtrl = type("FakeSpinCtrl", (FakeTextInput,), {})
        self.SpinCtrlDouble = type("FakeSpinCtrlDouble", (FakeTextInput,), {})


class FakeLogger:
    warnings = []

    @classmethod
    def warning(cls, message):
        cls.warnings.append(message)


class FakeFrame:
    def __init__(self, process_result=True):
        self.bind_calls = []
        self.unbind_calls = []
        self.events = []
        self.process_result = process_result

    def Bind(self, event_type, handler):
        self.bind_calls.append((event_type, handler))

    def Unbind(self, event_type, handler=None):
        self.unbind_calls.append((event_type, handler))
        return True

    def ProcessEvent(self, event):
        self.events.append(event)
        return self.process_result


class FakeKeybindingsManager:
    def __init__(self, overrides=None):
        self.overrides = overrides or {}

    def get_shortcut(self, command_id, default_shortcut=None):
        return self.overrides.get(command_id, default_shortcut)


class FakeMenuItem:
    def __init__(self, enabled=True, label="Command"):
        self.enabled = enabled
        self.label = label

    def IsEnabled(self):
        return self.enabled

    def GetItemLabelText(self):
        return self.label

    def SetItemLabel(self, value):
        self.label = value

    def Enable(self, enabled=True):
        self.enabled = bool(enabled)


class FakePanel:
    def __init__(self, child=None):
        self.child = child

    def IsDescendant(self, focus):
        return focus is self.child


class FakeEvent:
    def __init__(self, signature=None):
        self.signature = signature
        self.skipped = False

    def Skip(self):
        self.skipped = True


@pytest.fixture
def manager_module(monkeypatch):
    """Load the production module with lightweight wx/parser/logger stubs."""
    root = Path(__file__).resolve().parents[1]
    module_path = root / "core" / "shortcuts" / "shortcut_manager.py"

    if not module_path.is_file():
        pytest.fail(f"Cannot find production module: {module_path}")

    wx_stub = FakeWx()
    parser_module = types.ModuleType("core.shortcuts.shortcut_parser")
    parser_module.ShortcutParser = FakeParser
    logger_module = types.ModuleType("core.logger")
    logger_module.SpawnLogger = FakeLogger

    monkeypatch.setitem(sys.modules, "wx", wx_stub)
    monkeypatch.setitem(sys.modules, "core.shortcuts.shortcut_parser", parser_module)
    monkeypatch.setitem(sys.modules, "core.logger", logger_module)

    spec = importlib.util.spec_from_file_location(
        "_spawn_shortcut_manager_under_test",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_command(
    command_id,
    context="editor",
    shortcut="Ctrl+A",
    event_id=1001,
    menu_item=None,
    enabled_when=None,
):
    return ShortcutCommand(
        command_id=command_id,
        label=command_id,
        category="Test",
        context=context,
        default_shortcut=shortcut,
        event_id=event_id,
        menu_item=menu_item,
        enabled_when=enabled_when,
    )


def make_manager(manager_module, commands, overrides=None, frame=None):
    registry = CommandRegistry()
    for command in commands:
        registry.register(command)

    frame = frame or FakeFrame()
    keybindings = FakeKeybindingsManager(overrides)
    manager = manager_module.ShortcutManager(frame, registry, keybindings)
    manager.parser = FakeParser()
    manager.rebuild()
    return manager, frame


def test_rebuild_creates_context_and_signature_bindings(manager_module):
    command = make_command("edit.select_all", shortcut="Ctrl+A")
    manager, _ = make_manager(manager_module, [command])

    assert manager._bindings[("editor", "ctrl+a")] == [command]


def test_rebuild_omits_commands_with_null_shortcut(manager_module):
    command = make_command("edit.select_all", shortcut="Ctrl+A")
    manager, _ = make_manager(
        manager_module,
        [command],
        overrides={"edit.select_all": None},
    )

    assert manager._bindings == {}


def test_rebuild_ignores_invalid_shortcut(manager_module):
    command = make_command("edit.invalid", shortcut="INVALID shortcut")
    manager, _ = make_manager(manager_module, [command])

    assert manager._bindings == {}
    assert manager.get_conflicts() == []


def test_rebuild_records_conflicts_within_same_context(manager_module):
    first = make_command("edit.first", shortcut="Ctrl+A")
    second = make_command("edit.second", shortcut="ctrl+a")
    manager, _ = make_manager(manager_module, [first, second])

    assert manager.get_conflicts() == [
        {
            "context": "editor",
            "shortcut": "ctrl+a",
            "commands": ["edit.first", "edit.second"],
        }
    ]


def test_conflicts_in_different_contexts_are_not_collisions(manager_module):
    editor_command = make_command("edit.select_all", "editor", "Ctrl+A")
    global_command = make_command("global.select_all", "global", "Ctrl+A")
    manager, _ = make_manager(manager_module, [editor_command, global_command])

    assert manager.get_conflicts() == []


def test_resolve_prefers_command_from_active_context(manager_module):
    editor_command = make_command("editor.action", "editor", "Ctrl+A")
    global_command = make_command("global.action", "global", "Ctrl+A")
    manager, _ = make_manager(manager_module, [editor_command, global_command])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is editor_command


def test_resolve_falls_back_to_global_when_context_has_no_match(manager_module):
    global_command = make_command("global.action", "global", "Ctrl+A")
    manager, _ = make_manager(manager_module, [global_command])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is global_command


def test_resolve_returns_none_for_ambiguous_context_binding(manager_module):
    first = make_command("editor.first", "editor", "Ctrl+A")
    second = make_command("editor.second", "editor", "Ctrl+A")
    global_command = make_command("global.action", "global", "Ctrl+A")
    manager, _ = make_manager(manager_module, [first, second, global_command])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is None


def test_dispatch_sends_menu_event_to_frame(manager_module):
    command = make_command("edit.copy", event_id=4321)
    manager, frame = make_manager(manager_module, [command])

    assert manager.dispatch(command) is True
    assert len(frame.events) == 1
    assert frame.events[0].event_id == 4321
    assert frame.events[0].event_object is frame


def test_dispatch_returns_false_when_command_has_no_event_id(manager_module):
    command = make_command("edit.copy", event_id=None)
    manager, frame = make_manager(manager_module, [command])

    assert manager.dispatch(command) is False
    assert frame.events == []


def test_dispatch_does_not_run_disabled_menu_item(manager_module):
    menu_item = FakeMenuItem(enabled=False)
    command = make_command("edit.copy", menu_item=menu_item)
    manager, frame = make_manager(manager_module, [command])

    assert manager.dispatch(command) is False
    assert frame.events == []


def test_dispatch_returns_false_when_frame_does_not_process_event(manager_module):
    command = make_command("edit.copy")
    frame = FakeFrame(process_result=False)
    manager, _ = make_manager(manager_module, [command], frame=frame)

    assert manager.dispatch(command) is False
    assert len(frame.events) == 1


def test_on_char_hook_dispatches_matching_shortcut(manager_module):
    command = make_command("edit.copy", shortcut="Ctrl+C")
    manager, frame = make_manager(manager_module, [command])
    manager.get_active_context = lambda: "editor"
    event = FakeEvent("ctrl+c")

    manager.on_char_hook(event)

    assert len(frame.events) == 1
    assert event.skipped is False


def test_on_char_hook_skips_unhandled_key(manager_module):
    command = make_command("edit.copy", shortcut="Ctrl+C")
    manager, frame = make_manager(manager_module, [command])
    manager.get_active_context = lambda: "editor"
    event = FakeEvent("ctrl+x")

    manager.on_char_hook(event)

    assert frame.events == []
    assert event.skipped is True


def test_bind_and_unbind_are_idempotent(manager_module):
    manager, frame = make_manager(manager_module, [])

    manager.bind()
    manager.bind()
    assert manager._bound is True
    assert len(frame.bind_calls) == 2
    assert frame.bind_calls[0][0] is manager_module.wx.EVT_CHAR_HOOK
    assert frame.bind_calls[1][0] is manager_module.wx.EVT_MENU_OPEN

    manager.unbind()
    manager.unbind()
    assert manager._bound is False
    assert len(frame.unbind_calls) == 2


def test_get_active_context_returns_global_when_focus_is_missing(manager_module):
    manager, _ = make_manager(manager_module, [])
    manager_module.wx.Window.focus = None

    assert manager.get_active_context() == "global"


def test_get_active_context_detects_project_explorer(manager_module):
    manager, _ = make_manager(manager_module, [])
    focus = object()
    manager_module.wx.Window.focus = focus
    manager.frame.m_panel_splitter_ProjectTree = FakePanel(child=focus)

    assert manager.get_active_context() == "project_explorer"


def test_get_active_context_detects_source_control(manager_module):
    manager, _ = make_manager(manager_module, [])
    focus = object()
    manager_module.wx.Window.focus = focus
    manager.frame.m_panel_Git = FakePanel(child=focus)

    assert manager.get_active_context() == "source_control"


def test_resolve_does_not_fall_back_when_local_command_is_unavailable(manager_module):
    local = make_command(
        "editor.action", "editor", "Ctrl+A", enabled_when=lambda: False
    )
    global_command = make_command("global.action", "global", "Ctrl+A")
    manager, _ = make_manager(manager_module, [local, global_command])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is None


def test_resolve_uses_only_available_command_when_local_binding_is_ambiguous(manager_module):
    unavailable = make_command(
        "editor.unavailable", "editor", "Ctrl+A", enabled_when=lambda: False
    )
    available = make_command(
        "editor.available", "editor", "Ctrl+A", enabled_when=lambda: True
    )
    manager, _ = make_manager(manager_module, [unavailable, available])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is available


def test_resolve_returns_none_when_multiple_local_commands_are_available(manager_module):
    first = make_command(
        "editor.first", "editor", "Ctrl+A", enabled_when=lambda: True
    )
    second = make_command(
        "editor.second", "editor", "Ctrl+A", enabled_when=lambda: True
    )
    manager, _ = make_manager(manager_module, [first, second])
    manager.get_active_context = lambda: "editor"

    assert manager.resolve("ctrl+a") is None


def test_availability_checker_exception_fails_closed_and_logs(manager_module):
    def fail():
        raise RuntimeError("state unavailable")

    command = make_command("editor.action", enabled_when=fail)
    manager, _ = make_manager(manager_module, [command])

    assert manager.is_command_available(command) is False
    assert any("availability check failed" in item.lower() for item in FakeLogger.warnings)


def test_dispatch_does_not_run_command_when_enabled_when_is_false(manager_module):
    command = make_command("editor.action", enabled_when=lambda: False)
    manager, frame = make_manager(manager_module, [command])

    assert manager.dispatch(command) is False
    assert frame.events == []


def test_refresh_availability_updates_menu_items(manager_module):
    enabled_item = FakeMenuItem(enabled=False)
    disabled_item = FakeMenuItem(enabled=True)
    enabled_command = make_command(
        "editor.enabled", menu_item=enabled_item, enabled_when=lambda: True
    )
    disabled_command = make_command(
        "editor.disabled", menu_item=disabled_item, enabled_when=lambda: False
    )
    manager, _ = make_manager(manager_module, [enabled_command, disabled_command])

    manager.refresh_availability()

    assert enabled_item.IsEnabled() is True
    assert disabled_item.IsEnabled() is False


def test_refresh_availability_leaves_commands_without_checker_unchanged(manager_module):
    item = FakeMenuItem(enabled=False)
    command = make_command("editor.action", menu_item=item)
    manager, _ = make_manager(manager_module, [command])

    manager.refresh_availability()

    assert item.IsEnabled() is False


def test_on_menu_open_refreshes_availability_and_skips_event(manager_module):
    item = FakeMenuItem(enabled=False)
    command = make_command(
        "editor.action", menu_item=item, enabled_when=lambda: True
    )
    manager, _ = make_manager(manager_module, [command])
    event = FakeEvent()

    manager.on_menu_open(event)

    assert item.IsEnabled() is True
    assert event.skipped is True


def test_get_active_context_detects_documentation(manager_module):
    manager, _ = make_manager(manager_module, [])
    focus = object()
    manager_module.wx.Window.focus = focus
    manager.frame.documentation_panel = FakePanel(child=focus)

    assert manager.get_active_context() == "documentation"


def test_get_active_context_detects_editor(manager_module):
    manager, _ = make_manager(manager_module, [])
    focus = object()
    manager_module.wx.Window.focus = focus
    manager.frame.m_auinotebook_Main = SimpleNamespace(
        GetCurrentPage=lambda: FakePanel(child=focus)
    )

    assert manager.get_active_context() == "editor"


def test_text_input_inside_editor_uses_global_context(manager_module):
    manager, _ = make_manager(manager_module, [])
    focus = FakeTextInput()
    manager_module.wx.Window.focus = focus
    manager.frame.m_auinotebook_Main = SimpleNamespace(
        GetCurrentPage=lambda: FakePanel(child=focus)
    )

    assert manager.get_active_context() == "global"


def test_get_effective_shortcut_returns_default_and_override(manager_module):
    command = make_command("editor.action", shortcut="Ctrl+A")
    manager, _ = make_manager(
        manager_module, [command], overrides={"editor.action": "Alt+A"}
    )

    assert manager.get_effective_shortcut("editor.action") == "Alt+A"
    assert manager.get_effective_shortcut("missing.command") is None


def test_get_conflicts_returns_a_copy(manager_module):
    first = make_command("editor.first", shortcut="Ctrl+A")
    second = make_command("editor.second", shortcut="Ctrl+A")
    manager, _ = make_manager(manager_module, [first, second])

    conflicts = manager.get_conflicts()
    conflicts.clear()

    assert len(manager.get_conflicts()) == 1
