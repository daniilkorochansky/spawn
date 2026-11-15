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

import copy
import os
import re

from collections.abc import MutableMapping
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from core.logger import SpawnLogger


class KeybindingsManager:

    FORMAT_VERSION = 1
    DEFAULT_PROFILE_ID = "default"

    def __init__(self, appdata_dir):

        self.appdata_dir = Path(appdata_dir)
        self.appdata_dir.mkdir(parents=True, exist_ok=True)

        self.file_path = self.appdata_dir / "keybindings.yaml"

        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.indent(
            mapping=2,
            sequence=4,
            offset=2
        )

        self.data = self._default_data()
        self.load()

    # --------------------------------------------------
    # DEFAULT DATA
    # --------------------------------------------------

    @staticmethod
    def _default_data():

        return {
            "version": 1,
            "active_profile": "default",
            "profiles": {
                "default": {
                    "name": "Default",
                    "bindings": {}
                }
            }
        }

    # --------------------------------------------------
    # LOAD / SAVE
    # --------------------------------------------------

    def load(self):

        if not self.file_path.exists():

            self.data = self._default_data()

            try:
                self.save()
            except OSError:
                pass

            return self.data

        try:

            with self.file_path.open(
                "r",
                encoding="utf-8"
            ) as f:

                loaded = self.yaml.load(f)

            self._validate_data(loaded)
            self.data = loaded

        except (OSError, YAMLError, ValueError, TypeError) as exc:

            SpawnLogger.error(
                f"Keybindings Manager Load: {exc}"
            )

            # Keep the original file intact.
            # Do not overwrite potentially recoverable user profiles.
            self.data = self._default_data()

        return self.data

    def save(self):

        self._validate_data(self.data)

        temp_path = self.file_path.with_name(
            self.file_path.name + ".tmp"
        )

        try:

            with temp_path.open(
                "w",
                encoding="utf-8",
                newline="\n"
            ) as f:

                self.yaml.dump(self.data, f)

            os.replace(temp_path, self.file_path)

        except Exception as exc:

            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

            SpawnLogger.error(
                f"Keybindings Manager Save: {exc}"
            )

            raise

    # --------------------------------------------------
    # DATA VALIDATION
    # --------------------------------------------------

    def _validate_data(self, data):

        if not isinstance(data, MutableMapping):
            raise ValueError("Invalid keybindings file structure.")

        version = data.get("version", self.FORMAT_VERSION)

        if (
            type(version) is not int
            or version != self.FORMAT_VERSION
        ):
            raise ValueError(
                f"Unsupported keybindings version: {version}"
            )

        profiles = data.get("profiles")

        if not isinstance(profiles, MutableMapping):
            raise ValueError("Invalid profiles section.")

        for profile_id, profile in profiles.items():

            if not isinstance(profile_id, str) or not profile_id.strip():
                raise ValueError("Invalid profile ID.")

            if not isinstance(profile, MutableMapping):
                raise ValueError(
                    f"Invalid profile definition: {profile_id}"
                )

            name = profile.get("name", profile_id)

            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid profile name: {profile_id}"
                )

            profile["name"] = name.strip() or profile_id

            bindings = profile.setdefault("bindings", {})

            if not isinstance(bindings, MutableMapping):
                raise ValueError(
                    f"Invalid bindings section: {profile_id}"
                )

            for command_id, shortcut in bindings.items():

                if not isinstance(command_id, str) or not command_id.strip():
                    raise ValueError(
                        f"Invalid command ID in profile: {profile_id}"
                    )

                if shortcut is not None and not isinstance(shortcut, str):
                    raise ValueError(
                        f"Invalid shortcut for command: {command_id}"
                    )

                if isinstance(shortcut, str) and not shortcut.strip():
                    raise ValueError(
                        f"Empty shortcut for command: {command_id}. Use null to disable it."
                    )

        if self.DEFAULT_PROFILE_ID not in profiles:

            profiles[self.DEFAULT_PROFILE_ID] = {
                "name": "Default",
                "bindings": {}
            }

        active_profile = data.get("active_profile")

        if (
            not isinstance(active_profile, str)
            or active_profile not in profiles
        ):
            data["active_profile"] = self.DEFAULT_PROFILE_ID

        data["version"] = self.FORMAT_VERSION

    # --------------------------------------------------
    # PROFILE ACCESS
    # --------------------------------------------------

    def get_profiles(self):

        return [
            {
                "id": profile_id,
                "name": profile["name"]
            }
            for profile_id, profile in self.data["profiles"].items()
        ]

    def get_profile_ids(self):

        return list(self.data["profiles"].keys())

    def get_profile(self, profile_id=None):

        if profile_id is None:
            profile_id = self.get_active_profile_id()

        return self.data["profiles"].get(profile_id)

    def get_active_profile_id(self):

        return self.data["active_profile"]

    def get_active_profile(self):

        return self.get_profile(
            self.get_active_profile_id()
        )

    def get_binding_overrides(self, profile_id=None):

        profile = self.get_profile(profile_id)

        if profile is None:
            return {}

        return copy.deepcopy(profile["bindings"])

    def get_shortcut(
        self,
        command_id,
        default_shortcut=None,
        profile_id=None
    ):

        profile = self.get_profile(profile_id)

        if profile is None:
            return default_shortcut

        bindings = profile["bindings"]

        if command_id in bindings:
            return bindings[command_id]

        return default_shortcut

    # --------------------------------------------------
    # PROFILE MANAGEMENT
    # --------------------------------------------------

    def generate_profile_id(self, name):

        base = re.sub(
            r"[^a-z0-9_-]+",
            "_",
            name.strip().lower()
        ).strip("_")

        if not base:
            base = "profile"

        profile_id = base
        counter = 2

        while profile_id in self.data["profiles"]:

            profile_id = f"{base}_{counter}"
            counter += 1

        return profile_id

    def create_profile(
        self,
        name,
        profile_id=None,
        clone_from=None
    ):

        name = name.strip()

        if not name:
            raise ValueError("Profile name cannot be empty.")

        if profile_id is None:
            profile_id = self.generate_profile_id(name)

        if profile_id in self.data["profiles"]:
            raise ValueError(
                f"Profile already exists: {profile_id}"
            )

        bindings = {}

        if clone_from is not None:

            source = self.get_profile(clone_from)

            if source is None:
                raise KeyError(clone_from)

            bindings = copy.deepcopy(source["bindings"])

        self.data["profiles"][profile_id] = {
            "name": name,
            "bindings": bindings
        }

        return profile_id

    def rename_profile(self, profile_id, new_name):

        if profile_id == self.DEFAULT_PROFILE_ID:
            raise ValueError("The Default profile cannot be renamed.")

        profile = self.get_profile(profile_id)

        if profile is None:
            raise KeyError(profile_id)

        new_name = new_name.strip()

        if not new_name:
            raise ValueError("Profile name cannot be empty.")

        profile["name"] = new_name

    def delete_profile(self, profile_id):

        if profile_id == self.DEFAULT_PROFILE_ID:
            raise ValueError("The Default profile cannot be deleted.")

        if profile_id not in self.data["profiles"]:
            return False

        del self.data["profiles"][profile_id]

        if self.get_active_profile_id() == profile_id:
            self.data["active_profile"] = self.DEFAULT_PROFILE_ID

        return True

    def set_active_profile(self, profile_id):

        if profile_id not in self.data["profiles"]:
            raise KeyError(profile_id)

        self.data["active_profile"] = profile_id

    # --------------------------------------------------
    # BINDINGS MANAGEMENT
    # --------------------------------------------------

    def set_binding(
        self,
        command_id,
        shortcut,
        profile_id=None
    ):

        if not isinstance(command_id, str) or not command_id.strip():
            raise ValueError("Invalid command ID.")

        if shortcut is not None:

            if not isinstance(shortcut, str) or not shortcut.strip():
                raise ValueError("Invalid shortcut.")

            shortcut = shortcut.strip()

        profile = self.get_profile(profile_id)

        if profile is None:
            raise KeyError(profile_id)

        profile["bindings"][command_id] = shortcut

    def reset_binding(self, command_id, profile_id=None):

        profile = self.get_profile(profile_id)

        if profile is None:
            raise KeyError(profile_id)

        profile["bindings"].pop(command_id, None)

    def reset_profile(self, profile_id=None):

        profile = self.get_profile(profile_id)

        if profile is None:
            raise KeyError(profile_id)

        profile["bindings"].clear()

    # --------------------------------------------------
    # WORKING COPY
    # --------------------------------------------------

    def get_data_copy(self):

        return copy.deepcopy(self.data)

    def restore_data(self, snapshot):

        snapshot = copy.deepcopy(snapshot)
        self._validate_data(snapshot)
        self.data = snapshot

    # --------------------------------------------------
    # IMPORT / EXPORT
    # --------------------------------------------------

    def export_profile(self, profile_id, file_path):
        profile = self.get_profile(profile_id)

        if profile is None:
            raise KeyError(profile_id)

        export_data = {
            "version": self.FORMAT_VERSION,
            "name": profile["name"],
            "bindings": copy.deepcopy(profile["bindings"])
        }

        yaml_export = YAML()
        yaml_export.indent(
            mapping=2,
            sequence=4,
            offset=2
        )

        file_path = Path(file_path)

        with file_path.open(
            "w",
            encoding="utf-8"
        ) as f:

            yaml_export.dump(export_data, f)

    def import_profile(self, file_path):
        file_path = Path(file_path)

        with file_path.open(
            "r",
            encoding="utf-8"
        ) as f:

            imported = self.yaml.load(f)

        if not isinstance(imported, MutableMapping):
            raise ValueError("Invalid keymap file.")

        version = imported.get("version")

        if version != self.FORMAT_VERSION:
            raise ValueError(
                f"Unsupported keymap version: {version}"
            )

        name = imported.get("name")
        bindings = imported.get("bindings")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid keymap name.")

        if not isinstance(bindings, MutableMapping):
            raise ValueError("Invalid keymap bindings.")

        for command_id, shortcut in bindings.items():

            if not isinstance(command_id, str) or not command_id.strip():
                raise ValueError("Invalid command ID.")

            if shortcut is not None and not isinstance(shortcut, str):
                raise ValueError(
                    f"Invalid shortcut for {command_id}."
                )

            if isinstance(shortcut, str) and not shortcut.strip():
                raise ValueError(
                    f"Empty shortcut for {command_id}."
                )

        profile_id = self.generate_profile_id(name)

        self.data["profiles"][profile_id] = {
            "name": name.strip(),
            "bindings": copy.deepcopy(dict(bindings))
        }

        return profile_id
