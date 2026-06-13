# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Spawn — A fast and modern, open-source IDE with a native user interface for SA-MP and open.mp server development.
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

from core.config_manager import ConfigManager


def test_default_values_are_loaded():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)

    assert manager.get("system.git.enable") == False
    assert manager.get("editor.font.size") == 11
    assert manager.get("editor.font.family") == "Consolas"
    assert manager.get("editor.features.color_preview") is True

def test_get_returns_existing_value():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)

    value = manager.get("editor.font.size")

    assert value == 11

def test_get_returns_default_for_missing_key():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    value = manager.get(
        "editor.not_exists",
        "fallback"
    )

    assert value == "fallback"

def test_set_updates_valid_value():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    result = manager.set(
        "editor.font.size",
        14
    )

    assert result is True
    assert manager.get("editor.font.size") == 14

def test_set_rejects_invalid_type():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    result = manager.set(
        "editor.font.size",
        "large"
    )

    assert result is False
    assert manager.get("editor.font.size") == 11

def test_set_rejects_unknown_path():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    result = manager.set(
        "editor.unknown.option",
        True
    )

    assert result is False

def test_extract_defaults():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    defaults = manager._extract_defaults(
        manager._schema
    )

    assert defaults["system"]["git"]["enable"] == False
    assert defaults["editor"]["font"]["size"] == 11
    assert defaults["editor"]["features"]["color_preview"] is True

def test_validate_level_restores_invalid_values():
    
    manager = ConfigManager()
    manager.current_config = manager._extract_defaults(manager._schema)
    user_data = {
        "system": {
            "git": {
                "enable": 123
                }
        }
    }

    validated = manager._validate_level(
        manager._schema,
        user_data
    )

    assert validated["system"]["git"]["enable"] == False
