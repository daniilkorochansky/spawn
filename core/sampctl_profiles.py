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

from collections.abc import Mapping

from core.pawn_config import find_config, load_config


DEFAULT_PROFILE = "Default"

def _extract_profiles(config, section_name):
    raw_profiles = config.get(section_name)

    if raw_profiles is None:
        return [DEFAULT_PROFILE]

    if not isinstance(raw_profiles, list):
        raise ValueError(
            f"'{section_name}' must be a list of named configurations."
        )

    names = [DEFAULT_PROFILE]
    seen = {DEFAULT_PROFILE.casefold()}

    for index, profile in enumerate(raw_profiles):
        if not isinstance(profile, Mapping):
            raise ValueError(
                f"Invalid item at '{section_name}[{index}]'. "
                "Expected an object."
            )

        name = profile.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"'{section_name}[{index}]' must have a non-empty name."
            )

        name = name.strip()
        normalized_name = name.casefold()

        if normalized_name in seen:
            raise ValueError(
                f"Duplicate or reserved profile name '{name}' "
                f"in '{section_name}'."
            )

        seen.add(normalized_name)
        names.append(name)

    return names


def load_sampctl_profiles(project_path):
    """
    Load Build and Runtime profile names from pawn.json or pawn.yaml.

    Default is a Spawn-only option and is not defined in SAMPCTL.
    """

    config_path = find_config(project_path)

    if config_path is None:
        return {
            "builds": [DEFAULT_PROFILE],
            "runtimes": [DEFAULT_PROFILE]
        }

    config = load_config(project_path)

    if not isinstance(config, Mapping):
        raise ValueError("Invalid SAMPCTL package configuration.")

    return {
        "builds": _extract_profiles(config, "builds"),
        "runtimes": _extract_profiles(config, "runtimes")
    }
