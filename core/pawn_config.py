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

import os

from ruamel.yaml import YAML

CONFIG_FILES = ("pawn.json", "pawn.yaml")

_yaml = YAML(typ="rt")
_yaml.preserve_quotes = True
_yaml.indent(mapping=4, sequence=4, offset=2)


def find_config(project_path):
    """Find the project's configuration file."""

    found = [
        os.path.join(project_path, name)
        for name in CONFIG_FILES
        if os.path.isfile(os.path.join(project_path, name))
    ]

    if len(found) > 1:
        raise ValueError(
            "Both pawn.json and pawn.yaml exist in the project."
        )

    return found[0] if found else None


def load_config(project_path):
    """Load project configuration from JSON or YAML."""

    config_path = find_config(project_path)

    if not config_path:
        raise FileNotFoundError(
            "pawn.json or pawn.yaml was not found."
        )

    extension = os.path.splitext(config_path)[1].lower()

    with open(config_path, "r", encoding="utf-8") as f:
        if extension == ".json":
            import json
            return json.load(f)

        return _yaml.load(f)


def save_config(project_path, data):
    """Save configuration using its original format."""

    config_path = find_config(project_path)

    if not config_path:
        raise FileNotFoundError(
            "pawn.json or pawn.yaml was not found."
        )

    extension = os.path.splitext(config_path)[1].lower()

    with open(config_path, "w", encoding="utf-8") as f:
        if extension == ".json":
            import json
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            _yaml.dump(data, f)

    return config_path
