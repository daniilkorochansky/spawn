# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Spawn — IDE with a native user interface for SA-MP and open.mp server development.
#   Copyright (C) 2026  Daniil Korochansky
#
#   This file is part of Spawn.
#
#   Spawn is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Spawn is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Spawn.  If not, see <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------------------------------------------------

from pathlib import Path

import pytest

from core.shortcuts.keybindings_manager import KeybindingsManager


@pytest.fixture
def manager(tmp_path):
    return KeybindingsManager(tmp_path)


def test_new_manager_creates_default_profile_and_file(tmp_path):
    manager = KeybindingsManager(tmp_path)

    assert manager.file_path == tmp_path / "keybindings.yaml"
    assert manager.file_path.exists()
    assert manager.get_active_profile_id() == "default"
    assert manager.get_profile("default") == {
        "name": "Default",
        "bindings": {},
    }


def test_set_binding_overrides_default_shortcut(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")

    assert manager.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+Shift+C"


def test_null_binding_disables_shortcut_instead_of_using_default(manager):
    manager.set_binding("edit.copy", None)

    assert manager.get_shortcut("edit.copy", "Ctrl+C") is None


def test_missing_override_uses_default_shortcut(manager):
    assert manager.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+C"


def test_reset_binding_restores_default_shortcut(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")
    manager.reset_binding("edit.copy")

    assert manager.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+C"


def test_reset_profile_clears_all_overrides(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")
    manager.set_binding("edit.paste", None)

    manager.reset_profile()

    assert manager.get_binding_overrides() == {}
    assert manager.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+C"
    assert manager.get_shortcut("edit.paste", "Ctrl+V") == "Ctrl+V"


def test_create_profile_generates_normalized_unique_id(manager):
    first_id = manager.create_profile("My Custom Keymap")
    second_id = manager.create_profile("My Custom Keymap")

    assert first_id == "my_custom_keymap"
    assert second_id == "my_custom_keymap_2"


def test_create_profile_rejects_empty_name(manager):
    with pytest.raises(ValueError, match="cannot be empty"):
        manager.create_profile("   ")


def test_create_profile_rejects_existing_id(manager):
    with pytest.raises(ValueError, match="already exists"):
        manager.create_profile("Another Default", profile_id="default")


def test_clone_profile_copies_bindings_independently(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")
    clone_id = manager.create_profile("Clone", clone_from="default")

    manager.set_binding("edit.copy", "Alt+C", profile_id=clone_id)

    assert manager.get_shortcut("edit.copy", "Ctrl+C", "default") == "Ctrl+Shift+C"
    assert manager.get_shortcut("edit.copy", "Ctrl+C", clone_id) == "Alt+C"


def test_clone_profile_rejects_unknown_source(manager):
    with pytest.raises(KeyError):
        manager.create_profile("Clone", clone_from="does-not-exist")


def test_default_profile_cannot_be_renamed_or_deleted(manager):
    with pytest.raises(ValueError, match="cannot be renamed"):
        manager.rename_profile("default", "Renamed")

    with pytest.raises(ValueError, match="cannot be deleted"):
        manager.delete_profile("default")


def test_renaming_profile_requires_existing_profile_and_nonempty_name(manager):
    profile_id = manager.create_profile("Custom")

    with pytest.raises(ValueError, match="cannot be empty"):
        manager.rename_profile(profile_id, "  ")

    with pytest.raises(KeyError):
        manager.rename_profile("missing", "New name")

    manager.rename_profile(profile_id, "Renamed")
    assert manager.get_profile(profile_id)["name"] == "Renamed"


def test_deleting_active_profile_switches_back_to_default(manager):
    profile_id = manager.create_profile("Temporary")
    manager.set_active_profile(profile_id)

    assert manager.delete_profile(profile_id) is True
    assert manager.get_active_profile_id() == "default"
    assert manager.get_profile(profile_id) is None


def test_deleting_unknown_profile_returns_false(manager):
    assert manager.delete_profile("missing") is False


def test_set_active_profile_rejects_unknown_profile(manager):
    with pytest.raises(KeyError):
        manager.set_active_profile("missing")


def test_set_binding_validates_command_id_and_shortcut(manager):
    with pytest.raises(ValueError, match="Invalid command ID"):
        manager.set_binding("   ", "Ctrl+A")

    with pytest.raises(ValueError, match="Invalid shortcut"):
        manager.set_binding("edit.copy", "   ")

    with pytest.raises(KeyError):
        manager.set_binding("edit.copy", "Ctrl+A", profile_id="missing")


def test_get_binding_overrides_returns_a_deep_copy(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")

    overrides = manager.get_binding_overrides()
    overrides["edit.copy"] = "Alt+C"
    overrides["new.command"] = "F12"

    assert manager.get_binding_overrides() == {"edit.copy": "Ctrl+Shift+C"}


def test_snapshot_and_restore_are_independent(manager):
    manager.set_binding("edit.copy", "Ctrl+Shift+C")
    snapshot = manager.get_data_copy()

    manager.set_binding("edit.copy", "Alt+C")
    manager.create_profile("Temporary")
    manager.restore_data(snapshot)

    assert manager.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+Shift+C"
    assert manager.get_profile_ids() == ["default"]


def test_save_and_reload_preserve_profiles_and_bindings(tmp_path):
    first = KeybindingsManager(tmp_path)
    profile_id = first.create_profile("Work")
    first.set_binding("edit.copy", "Ctrl+Shift+C", profile_id)
    first.set_binding("edit.paste", None, profile_id)
    first.set_active_profile(profile_id)
    first.save()

    second = KeybindingsManager(tmp_path)

    assert second.get_active_profile_id() == profile_id
    assert second.get_shortcut("edit.copy", "Ctrl+C") == "Ctrl+Shift+C"
    assert second.get_shortcut("edit.paste", "Ctrl+V") is None


def test_load_adds_default_profile_and_repairs_invalid_active_profile(tmp_path):
    path = tmp_path / "keybindings.yaml"
    path.write_text(
        "version: 1\n"
        "active_profile: does_not_exist\n"
        "profiles:\n"
        "  work:\n"
        "    name: Work\n"
        "    bindings: {}\n",
        encoding="utf-8",
    )

    manager = KeybindingsManager(tmp_path)

    assert manager.get_active_profile_id() == "default"
    assert manager.get_profile("default")["name"] == "Default"
    assert manager.get_profile("work")["name"] == "Work"


def test_invalid_file_loads_defaults_without_overwriting_original(tmp_path):
    path = tmp_path / "keybindings.yaml"
    original = "version: 999\nprofiles: {}\n"
    path.write_text(original, encoding="utf-8")

    manager = KeybindingsManager(tmp_path)

    assert manager.get_active_profile_id() == "default"
    assert path.read_text(encoding="utf-8") == original


def test_validation_rejects_invalid_structures(manager):
    with pytest.raises(ValueError, match="Invalid keybindings file structure"):
        manager._validate_data(None)

    with pytest.raises(ValueError, match="Unsupported keybindings version"):
        manager._validate_data({"version": 2, "profiles": {}})

    with pytest.raises(ValueError, match="Invalid profiles section"):
        manager._validate_data({"version": 1, "profiles": []})


def test_validation_rejects_empty_shortcut_string(manager):
    invalid_data = {
        "version": 1,
        "active_profile": "default",
        "profiles": {
            "default": {
                "name": "Default",
                "bindings": {"edit.copy": "   "},
            }
        },
    }

    with pytest.raises(ValueError, match="Use null to disable it"):
        manager._validate_data(invalid_data)


def test_export_and_import_profile_round_trip(manager, tmp_path):
    source_id = manager.create_profile("Exported")
    manager.set_binding("edit.copy", "Ctrl+Shift+C", source_id)
    manager.set_binding("edit.paste", None, source_id)
    export_path = tmp_path / "exported.yaml"

    manager.export_profile(source_id, export_path)
    imported_id = manager.import_profile(export_path)

    assert imported_id == "exported_2"
    assert manager.get_profile(imported_id) == {
        "name": "Exported",
        "bindings": {
            "edit.copy": "Ctrl+Shift+C",
            "edit.paste": None,
        },
    }


def test_importing_same_profile_name_generates_unique_id(manager, tmp_path):
    profile_id = manager.create_profile("Shared")
    export_path = tmp_path / "shared.yaml"
    manager.export_profile(profile_id, export_path)

    imported_id = manager.import_profile(export_path)

    assert imported_id == "shared_2"


def test_import_rejects_unsupported_version(manager, tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text(
        "version: 2\nname: Invalid\nbindings: {}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported keymap version"):
        manager.import_profile(path)


def test_import_rejects_invalid_binding_value(manager, tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text(
        "version: 1\nname: Invalid\nbindings:\n  edit.copy: 42\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid shortcut"):
        manager.import_profile(path)
