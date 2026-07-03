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
import copy

import gettext
_ = gettext.gettext

from core.logger import SpawnLogger
from core.platform_utils import PlatformUtils

class ConfigManager:
    def __init__(self):
        self.appdata_dir = PlatformUtils.get_config_dir()
        os.makedirs(self.appdata_dir, exist_ok=True)
        self.config_path = PlatformUtils.normalize_path(os.path.join(self.appdata_dir, 'config.json'))

        self._profile_schema = {}

        self._global_schema = {
            "recent_files": ([], list),
            "recent_files_limit": (15, int, {
                "title": _(u"Recent Files Limit"), #Metadata for a Search
                "description": _(u"Maximum number of recent files to keep."),
                "keywords": ["recent", "files", "history", "limit"],
                "category": _(u"System"),
                "restart_required": False
                }),
            "system": {
                "git": {
                    "enable": (False, bool, {
                        "title": _(u"Git Integration"), 
                        "description": _(u"Enable Git integration."),
                        "keywords": ["git", "version control", "repository", "source control"],
                        "category": "Git",
                        "restart_required": False
                        }),
                    "executable_path": ("", str, {
                        "title": _(u"Git Executable"), 
                        "description": _(u"Path to the Git executable."),
                        "keywords": ["git", "path", "executable"],
                        "category": _(u"System"),
                        "restart_required": False
                        })
                    },
                "sampctl": {
                    "executable_path": ("", str, {
                        "title": _(u"SAMPCTL Executable"), 
                        "description": _(u"Path to the SAMPCTL executable."),
                        "keywords": ["sampctl", "path", "executable", "compiler", "build"],
                        "category": _(u"System"),
                        "restart_required": False
                        })
                    },
                "pawn": {
                    "default_encoding": ("cp1251", str, {
                        "title": _(u"Default Encoding"),
                        "description": _(u"Default encoding used when creating new Pawn source files."),
                        "keywords": ["encoding", "charset", "utf8", "cp1251", "pawn"],
                        "category": "Pawn",
                        "restart_required": False
                        } )
                    }
                },
            "editor": {
                "selection_color": ("#CCE8FF", str, {
                    "title": _(u"Selection Color"), 
                    "description": _(u"Background color of selected text."),
                    "keywords": ["selection", "highlight", "color"],
                    "category": _(u"Editor"),
                    "restart_required": False
                    }),
                "current_line_color": ("#F8FAFD", str, {
                    "title": _(u"Current Line Color"), 
                    "description": _(u"Background color of the current line."),
                    "keywords": ["current line", "caret line", "highlight", "color"],
                    "category": _(u"Editor"),
                    "restart_required": False
                    }),
                "font": {
                    "size": (11, int, {
                        "title": _("Font Size"),
                        "description": _(u"Font size used by the code editor."),
                        "keywords": ["font", "size", "editor", "text"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "line_spacing": (1, int, {
                        "title": _(u"Line Spacing"),
                        "description": _(u"Additional spacing between editor lines."),
                        "keywords": ["spacing", "line", "editor"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "family": (PlatformUtils.default_editor_font(), str, {
                        "title": _(u"Font Family"),
                        "description": _(u"Font family used by the code editor."),
                        "keywords": ["font", "family", "editor"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        })
                },
                "features": {
                    "multicursor": {
                        "enable": (False, bool, {
                            "title": _(u"Multi-Cursor"), 
                            "description": _(u"Enable multi-cursor editing."),
                            "keywords": ["multicursor", "multiple cursors", "editing"],
                            "category": "Editor",
                            "restart_required": False
                            })
                        },
                    "smart_indent": (True, bool, {
                        "title": _(u"Smart Indentation"),
                        "description": _(u"Automatically indents Pawn code while typing."),
                        "keywords": ["indent", "indentation", "format", "tabs", "pawn"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "color_preview": (True, bool, {
                        "title": _(u"Color Preview"),
                        "description": _(u"Displays color markers for Pawn color values in the code editor."),
                        "keywords": ["color", "colour", "rgba", "hex", "preview"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "line_numbers": (True, bool, {
                        "title": _(u"Line Numbers"),
                        "description": _(u"Displays line numbers in the editor."),
                        "keywords": ["line", "numbers", "gutter"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "folding": (True, bool, {
                        "title": _(u"Code Folding"),
                        "description": _(u"Enables folding of code blocks."),
                        "keywords": ["fold", "folding", "collapse", "expand"],
                        "category": _(u"Editor"),
                        "restart_required": False
                        }),
                    "show_change_history": {
                        "enabled": (True, bool, {
                            "title": _(u"Show Change History"),
                            "description": _(u"Displays change markers in the editor margin."),
                            "keywords": ["history", "modified", "margin", "change"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "color_marker_modified": ("#FFD324", str, {
                            "title": _(u"Modified Marker Color"),
                            "description": _(u"Color used for modified line markers."),
                            "keywords": ["marker", "modified", "color", "history"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "color_marker_saved": ("#228B22", str, {
                            "title": _(u"Saved Marker Color"),
                            "description": _(u"Color used for saved line markers."),
                            "keywords": ["marker", "saved", "color", "history"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            })
                        },
                    "brace_matching": {
                        "enabled": (True, bool, {
                            "title": _(u"Brace Matching"),
                            "description": _(u"Highlights matching braces."),
                            "keywords": ["brace", "bracket", "matching"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "color_bracelight": ("#FFFFFF", str, {
                            "title": _(u"Matched Brace Text Color"),
                            "description": _(u"Text color of a matching brace."),
                            "keywords": ["brace", "matching", "text", "color"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "backcolor_bracelight": ("#E0E0FF", str, {
                            "title": _(u"Matched Brace Background"),
                            "description": _(u"Background color of a matching brace."),
                            "keywords": ["brace", "matching", "background", "color"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "color_bracebad": ("#FFFFFF", str, {
                            "title": _(u"Unmatched Brace Text Color"),
                            "description": _(u"Text color of an unmatched brace."),
                            "keywords": ["brace", "error", "text", "color"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            }),
                        "backcolor_bracebad": ("#E51400", str, {
                            "title": _(u"Unmatched Brace Background"),
                            "description": _(u"Background color of an unmatched brace."),
                            "keywords": ["brace", "error", "background", "color"],
                            "category": _(u"Editor"),
                            "restart_required": False
                            })
                        }
                           
                }
            }
        }


        self._schema = {
            "system": {
                "active_profile": ("Default", str),
                "recent_files": ([], list),
                "pawn": {
                    "default_encoding": ("cp1251", str)
                    },
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
                    "line_spacing": (0, int),
                    "family": (PlatformUtils.default_editor_font(), str)
                },
                "features": {
                    "smart_indent": (True, bool),
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

        self.current_config = {}
        self.global_config = {}

        self.settings_index = []

        self.default_config = self._build_defaults(self._global_schema)

        self.load_global()

    def _build_defaults(self,schema):
        if isinstance(schema, dict):
            result = {}

            for key, value in schema.items():
                result[key] = self._build_defaults(value)
            return result

        if isinstance(schema, tuple):
            default, _type, *_ = schema
            return copy.deepcopy(default)

        return copy.deepcopy(schema)

    #For searching settings
    def build_settings_index(self):
        def walk(schema, prefix=""):

            for key, value in schema.items():

                path = f"{prefix}.{key}" if prefix else key

                if self._is_visible_setting(value):

                    metadata = value[2]

                    item = {
                        "path": path,
                        "title": metadata["title"],
                        "description": metadata.get("description", ""),
                        "keywords": metadata.get("keywords", []),
                        "category": metadata.get("category", ""),
                        "restart_required": metadata.get("restart_required", False)
                    }

                    item["search_text"] = " ".join([
                        item["title"],
                        item["description"],
                        item["category"],
                        *item["keywords"]
                    ]).lower()

                    self.settings_index.append(item)

                elif isinstance(value, dict):

                    walk(value, path)

        walk(self._global_schema)

    def _is_visible_setting(self, value):
        if not self._is_setting(value):
            return False

        if len(value) < 3:
            return False

        metadata = value[2]

        return (
            isinstance(metadata, dict)
            and "title" in metadata
        )

    def search_settings(self, query):
        query = " ".join(
            query.lower().split()
        )

        if not query:
            return []

        tokens = query.split()

        results = []

        for item in self.settings_index:

            if not all(
                token in item["search_text"]
                for token in tokens
            ):
                continue

            score = 0

            title = item["title"].lower()

            #
            # Самое важное — название
            #

            if title == query:

                score += 1000

            elif title.startswith(query):

                score += 700

            elif query in title:

                score += 500

            #
            # Категория
            #

            category = item["category"].lower()

            if category.startswith(query):

                score += 120

            elif query in category:

                score += 80

            #
            # Keywords
            #

            for keyword in item["keywords"]:

                keyword = keyword.lower()

                if keyword == query:

                    score += 400

                elif keyword.startswith(query):

                    score += 250

                elif query in keyword:

                    score += 150

            #
            # Description
            #

            if query in item["description"].lower():

                score += 40

            item["score"] = score

            results.append(item)

        #
        # Удаляем дубликаты
        #

        unique = {}

        for item in results:

            unique[item["path"]] = item

        results = list(unique.values())

        #
        # Сортировка
        #

        results.sort(
            key=lambda item: (
                -item["score"],
                item["title"]
            )
        )

        return results[:10]
            
    def _is_setting(self, value):
        return (isinstance(value, tuple) and len(value) >= 2 and isinstance(value[1], type))

    def _get_schema_entry(self, schema, path):
        keys = path.split(".")

        node = schema
        for key in keys:
            if not isinstance(node, dict):
                return None

            node = node.get(key)

            if node is None:
                return None

        return node if self._is_setting(node) else None

    def get_setting_metadata(self, path):
        entry = self._get_schema_entry(
            self._global_schema,
            path
        )

        if entry is None:
            return {}

        if len(entry) >= 3:
            return entry[2]

        return {}

    def get_setting_title(self, path):
        return self.get_setting_metadata(path).get(
            "title",
            path
        )


    def get_setting_description(self, path):

        return self.get_setting_metadata(path).get(
            "description",
            ""
        )


    def get_setting_keywords(self, path):

        return self.get_setting_metadata(path).get(
            "keywords",
            []
        )


    def get_setting_category(self, path):

        return self.get_setting_metadata(path).get(
            "category",
            ""
        )


    def is_restart_required(self, path):

        return self.get_setting_metadata(path).get(
            "restart_required",
            False
        )
    #----------------------

    def save_global(self):
        with open(self.config_path,"w",encoding="utf-8") as f:
            json.dump(
                self.global_config,
                f,
                indent=4,
                ensure_ascii=False
            )

    def load_global(self):
        if not os.path.exists(
            self.config_path
        ):

            self.global_config = (
                self._extract_defaults(
                    self._global_schema
                )
            )

            self.save_global()

            return

        try:

            with open(
                self.config_path,
                "r",
                encoding="utf-8"
            ) as f:

                raw_data = json.load(f)

        except Exception:

            raw_data = {}

        self.global_config = (
            self._validate_level(
                self._global_schema,
                raw_data
            )
        )


    def _validate_level(self, schema_level, user_level):
        validated = {}

        if not isinstance(user_level, dict):
            user_level = {}

        for key, schema_val in schema_level.items():

            if self._is_setting(schema_val):

                default = schema_val[0]
                expected_type = schema_val[1]

                if (
                    key in user_level
                    and isinstance(user_level[key], expected_type)
                ):
                    validated[key] = user_level[key]
                else:
                    validated[key] = default

            elif isinstance(schema_val, dict):

                user_sub_level = user_level.get(key, {})

                validated[key] = self._validate_level(
                    schema_val,
                    user_sub_level
                )

        return validated

    def load(self):
        if not os.path.exists(self.config_path):
            self.current_config = self._extract_defaults(self._global_schema)
            self.save()
            return
        try:
            with open(self.config_path, 'r', encoding="utf-8") as f:
                raw_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raw_data = {}
            SpawnLogger.error(f"Config Manager Load Config: {e}")
            
        self.current_config = self._validate_level(self._global_schema, raw_data)

    def _extract_defaults(self, schema_level):
        defaults = {}

        for key, schema_val in schema_level.items():

            if self._is_setting(schema_val):

                defaults[key] = schema_val[0]

            elif isinstance(schema_val, dict):

                defaults[key] = self._extract_defaults(schema_val)

        return defaults


    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            SpawnLogger.error(f"Config Manager Save Config: {e}")

    def get_global(self, path_str, default=None):
        keys = path_str.split('.')

        data = self.global_config

        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default

        return data

    def set_global(self, path_str, value):
        keys = path_str.split('.')

        schema_data = self._global_schema

        for key in keys[:-1]:

            if isinstance(schema_data, dict) and key in schema_data:
                schema_data = schema_data[key]
            else:
                return False

        last_key = keys[-1]

        if (
            last_key in schema_data
            and
            isinstance(schema_data[last_key], tuple)
        ):

            _, expected_type = schema_data[last_key]

            if not isinstance(value, expected_type):
                return False

        else:
            return False

        data = self.global_config

        for key in keys[:-1]:
            data = data[key]

        data[last_key] = value

        self.save_global()

        return True

    def _get_from_dict(self, data, path_str, default=None):
        keys = path_str.split('.')

        for key in keys:

            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default

        return data

    def _parse_setting(self, setting):
        if not self._is_setting(setting):
            return None

        default = setting[0]
        value_type = setting[1]

        metadata = (
            setting[2]
            if len(setting) >= 3
            else {}
        )

        return default, value_type, metadata

    def _get_schema_entry(self, schema, path_str):
        keys = path_str.split('.')

        schema_data = schema

        for key in keys[:-1]:

            if (
                isinstance(schema_data, dict)
                and key in schema_data
            ):
                schema_data = schema_data[key]
            else:
                return None

        last_key = keys[-1]

        if (
            last_key in schema_data
            and isinstance(schema_data[last_key], tuple)
        ):
            return schema_data[last_key]

        return None

    def _set_in_dict(self, data, path_str, value):
        keys = path_str.split('.')

        for key in keys[:-1]:
            data = data[key]

        data[keys[-1]] = value

    def get(self, path_str, default=None):
        return self._get_from_dict(
            self.global_config,
            path_str,
            default
        )

    def _set_value(self, schema, config, save_func, path_str, value):
        schema_entry = self._get_schema_entry(
            schema,
            path_str
        )

        if schema_entry is None:
            return False

        expected_type = schema_entry[1]

        if not isinstance(value, expected_type):
            return False

        self._set_in_dict(
            config,
            path_str,
            value
        )

        save_func()

        return True

    def set(self, path_str, value):
        return self._set_value(
            self._global_schema,
            self.global_config,
            self.save_global,
            path_str,
            value
        )
