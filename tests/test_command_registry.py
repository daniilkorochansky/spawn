# -*- coding: utf-8 -*-

import pytest

from core.shortcuts.command_registry import CommandRegistry, ShortcutCommand


def make_command(
    command_id="edit.copy",
    label="Copy",
    category="Edit",
    context="editor",
    shortcut="Ctrl+C",
    event_id=1001,
):
    return ShortcutCommand(
        command_id=command_id,
        label=label,
        category=category,
        context=context,
        default_shortcut=shortcut,
        event_id=event_id,
    )


def test_register_and_get_command():
    registry = CommandRegistry()
    command = make_command()

    registry.register(command)

    assert registry.get("edit.copy") is command
    assert registry.get("missing.command") is None


def test_register_rejects_duplicate_command_id():
    registry = CommandRegistry()
    registry.register(make_command())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(make_command(label="Copy again"))


def test_all_returns_registered_commands_in_registration_order():
    registry = CommandRegistry()
    first = make_command("edit.copy")
    second = make_command("edit.paste", label="Paste", shortcut="Ctrl+V")

    registry.register(first)
    registry.register(second)

    assert registry.all() == [first, second]


def test_all_returns_a_new_list():
    registry = CommandRegistry()
    command = make_command()
    registry.register(command)

    result = registry.all()
    result.clear()

    assert registry.all() == [command]


def test_get_by_category_filters_commands():
    registry = CommandRegistry()
    copy_command = make_command("edit.copy")
    paste_command = make_command("edit.paste", label="Paste")
    build_command = make_command(
        "build.compile",
        label="Compile",
        category="Build",
        context="global",
        shortcut="F6",
    )

    for command in (copy_command, paste_command, build_command):
        registry.register(command)

    assert registry.get_by_category("Edit") == [copy_command, paste_command]
    assert registry.get_by_category("Build") == [build_command]
    assert registry.get_by_category("Missing") == []


def test_shortcut_command_stores_enabled_when_callback():
    availability = lambda: True
    command = make_command()
    command = ShortcutCommand(
        command_id=command.command_id,
        label=command.label,
        category=command.category,
        context=command.context,
        default_shortcut=command.default_shortcut,
        event_id=command.event_id,
        enabled_when=availability,
    )

    assert command.enabled_when is availability
