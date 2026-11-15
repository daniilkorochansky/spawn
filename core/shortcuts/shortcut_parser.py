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

import re
import wx


class ShortcutParser:

    MODIFIER_ALIASES = {
        "CTRL": "CTRL",
        "CONTROL": "CTRL",
        "RAWCTRL": "CTRL",
        "ALT": "ALT",
        "SHIFT": "SHIFT",
        "CMD": "META",
        "COMMAND": "META",
        "META": "META",
    }

    KEY_ALIASES = {
        "ENTER": wx.WXK_RETURN,
        "RETURN": wx.WXK_RETURN,
        "ESC": wx.WXK_ESCAPE,
        "ESCAPE": wx.WXK_ESCAPE,
        "BACKSPACE": wx.WXK_BACK,
        "BACK": wx.WXK_BACK,
        "DELETE": wx.WXK_DELETE,
        "DEL": wx.WXK_DELETE,
        "INSERT": wx.WXK_INSERT,
        "HOME": wx.WXK_HOME,
        "END": wx.WXK_END,
        "PAGEUP": wx.WXK_PAGEUP,
        "PAGEDOWN": wx.WXK_PAGEDOWN,
        "UP": wx.WXK_UP,
        "DOWN": wx.WXK_DOWN,
        "LEFT": wx.WXK_LEFT,
        "RIGHT": wx.WXK_RIGHT,
        "TAB": wx.WXK_TAB,
        "SPACE": wx.WXK_SPACE,
        "NUMPADENTER": wx.WXK_NUMPAD_ENTER,
    }

    IGNORE_KEY_CODES = {
        wx.WXK_SHIFT,
        wx.WXK_ALT,
        wx.WXK_CONTROL,
        wx.WXK_COMMAND,
    }

    def parse(self, shortcut):

        if shortcut is None:
            return None

        if not isinstance(shortcut, str):
            raise ValueError("Shortcut must be a string.")

        shortcut = shortcut.strip()

        if not shortcut:
            raise ValueError("Shortcut cannot be empty.")

        parts = [
            part.strip()
            for part in shortcut.split("+")
        ]

        if any(not part for part in parts):
            raise ValueError(f"Invalid shortcut: {shortcut}")

        modifiers = set()

        while parts and parts[0].upper() in self.MODIFIER_ALIASES:

            modifier = self.MODIFIER_ALIASES[
                parts.pop(0).upper()
            ]

            if modifier in modifiers:
                raise ValueError(
                    f"Duplicate modifier in shortcut: {shortcut}"
                )

            modifiers.add(modifier)

        if len(parts) != 1:
            raise ValueError(f"Invalid shortcut: {shortcut}")

        key_code = self._parse_key(parts[0])

        return frozenset(modifiers), key_code

    def _parse_key(self, key):

        normalized = key.strip().upper()

        if normalized in self.KEY_ALIASES:
            return self.KEY_ALIASES[normalized]

        if re.fullmatch(r"F([1-9]|1[0-9]|2[0-4])", normalized):

            function_number = int(normalized[1:])

            key_code = getattr(
                wx,
                f"WXK_F{function_number}",
                None
            )

            if key_code is None:
                raise ValueError(f"Unsupported key: {key}")

            return key_code

        if len(key) == 1:

            character = key.upper()

            if ord(character) <= 127:
                return ord(character)

        raise ValueError(f"Unsupported key: {key}")

    def from_event(self, event):

        key_code = event.GetKeyCode()

        if key_code in self.IGNORE_KEY_CODES:
            return None

        if key_code is None or key_code == wx.WXK_NONE:
            return None

        if 0 <= key_code <= 127:

            character = chr(key_code)

            if character.isalpha():
                key_code = ord(character.upper())

        modifiers = set()

        if event.ControlDown():
            modifiers.add("CTRL")

        if event.AltDown():
            modifiers.add("ALT")

        if event.ShiftDown():
            modifiers.add("SHIFT")

        if event.MetaDown():
            modifiers.add("META")

        return frozenset(modifiers), key_code

    def format(self, parsed):

        if parsed is None:
            return ""

        modifiers, key_code = parsed

        names = []

        for modifier in ("CTRL", "ALT", "SHIFT", "META"):

            if modifier in modifiers:

                names.append({
                    "CTRL": "Ctrl",
                    "ALT": "Alt",
                    "SHIFT": "Shift",
                    "META": "Cmd",
                }[modifier])

        special_names = {
            value: name.title()
            for name, value in self.KEY_ALIASES.items()
        }

        special_names.update({
            getattr(wx, f"WXK_F{i}"): f"F{i}"
            for i in range(1, 25)
            if hasattr(wx, f"WXK_F{i}")
        })

        key_name = special_names.get(key_code)

        if key_name is None and 0 <= key_code <= 127:
            key_name = chr(key_code).upper()

        if key_name is None:
            key_name = str(key_code)

        names.append(key_name)

        return "+".join(names)
