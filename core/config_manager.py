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
import json

from core.logger import SpawnLogger

class ConfigManager:
    def __init__(self):
        self.appdata_dir = os.path.join(os.environ['APPDATA'], 'Spawn')
        os.makedirs(self.appdata_dir, exist_ok=True)
        self.config_path = os.path.join(self.appdata_dir, 'config.json')

        self.project_root = None
        self.project_config_path = None

        self._schema = {
            "system": {
                "git": {
                    "enable": (False, bool),
                    "executable_path": ("", str)
                    },
                "sampctl": {
                    "executable_path": ("", str)
                    }
                },
            "editor": {
                "font": {
                    "size": (11, int),
                    "line_spacing": (1, int),
                    "family": ("Consolas", str)
                },
                "features": {
                    "color_preview": (True, bool),
                    "line_numbers": (True, bool),
                    "folding": (True, bool),
                    "show_change_history": {
                        "enabled": (True, bool),
                        "color_marker_modified": ("#FFD324", str),
                        "color_marker_saved": ("#228B22", str)
                        },
                    "brace_matching": {
                        "enabled": (True, bool),
                        "color_bracelight": ("#FFFFFF", str),
                        "backcolor_bracelight": ("#E0E0FF", str),
                        "color_bracebad": ("#FFFFFF", str),
                        "backcolor_bracebad": ("#E51400", str)
                        }
                           
                }
            }
        }

        self._project_schema = {
            "sampctl_path": ("", str)
            }

        self.current_config = {}
        self.project_config = {}
        self.load()

    def reset_settings(self):
        self.current_config = self._extract_defaults(self._schema)
        self.save() 

    def set_project(self, project_path):
        if not project_path or not os.path.isdir(project_path):
            self.project_root = None
            self.project_config_path = None
            self.project_config = {}
            return
        self.project_root = project_path
        self.project_config_path = os.path.join(project_path, "spawn.json")
        self.load_project_config()

    def load_project_config(self):
        if not self.project_config_path or not os.path.exists(self.project_config_path):
            self.project_config = {k: v for k, v in self._project_schema.items()}
            return
        try:
            with open(self.project_config_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raw_data = {}
            SpawnLogger.error(f"Config Manager Load Project Config: {e}")

        self.project_config = {}
        for key, (default, expected_type) in self._project_schema.items():
            if key in raw_data and isinstance(raw_data[key], expected_type):
                self.project_config[key] = raw_data[key]
            else:
                self.project_config[key] = default

    def _validate_level(self, schema_level, user_level):
        validated = {}

        if not isinstance(user_level, dict):
            user_level = {}

        for key, schema_val in schema_level.items():
            if isinstance(schema_val, tuple) and len(schema_val) == 2 and isinstance(schema_val[1], type):
                default, expected_type = schema_val

                if key in user_level and isinstance(user_level[key], expected_type):
                    validated[key] = user_level[key]
                else:
                    validated[key] = default
            elif isinstance(schema_val, dict):
                user_sub_level = user_level.get(key, {})
                validated[key] = self._validate_level(schema_val, user_sub_level)
        return validated

    def load(self):
        if not os.path.exists(self.config_path):
            self.current_config = self._extract_defaults(self._schema)
            self.save()
            return
        try:
            with open(self.config_path, 'r', encoding="utf-8") as f:
                raw_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raw_data = {}
            SpawnLogger.error(f"Config Manager Load Config: {e}")
            
        self.current_config = self._validate_level(self._schema, raw_data)

    def _extract_defaults(self, schema_level):
        defaults = {}
        for key, val in schema_level.items():
            if isinstance(val, dict):
                defaults[key] = self._extract_defaults(val)
            else:
                defaults[key] = val[0]
        return defaults

    def save_project_config(self):
        if not self.project_config_path: return
        try:
            with open(self.project_config_path, 'w', encoding="utf-8") as f:
                json.dump(self.project_config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            SpawnLogger.error(f"Config Manager Save Project Config: {e}")

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            SpawnLogger.error(f"Config Manager Save Config: {e}")

    def get(self, path_str, default=None):
##        #Project config
##        if path_str in self.project_config:
##            return self.project_config[path_str]
        #Global config
        keys = path_str.split('.')
        data = self.current_config
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data

    def set(self, path_str, value):
        
##        #Project config
##        if path_str in self._project_schema:
##            _, expected_type = self._project_schema[path_str]
##            if isinstance(value, expected_type):
##                self.project_config[path_str] = value
##                if self.project_config_path:
##                    self.save_project_config()

        #Global config
        keys = path_str.split('.')

        schema_data = self._schema
        for key in keys[:-1]:
            if isinstance(schema_data, dict) and key in schema_data:
                schema_data = schema_data[key]
            else:
                return False
        last_key = keys[-1]
        if last_key in schema_data and isinstance(schema_data[last_key], tuple):
            _, expected_type = schema_data[last_key]
            if not isinstance(value, expected_type):
                return False
        else:
            return False

        data = self.current_config
        for key in keys[:-1]:
            data = data[key]

        data[keys[-1]] = value
        self.save()
        return True
