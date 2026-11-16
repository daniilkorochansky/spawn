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

from dataclasses import dataclass
from typing import Optional, Callable

@dataclass(frozen=True)
class ShortcutCommand:
    command_id: str
    label: str
    category: str
    context: str
    default_shortcut: Optional[str]
    event_id: int
    menu_item: object = None
    enabled_when: Optional[Callable[[], bool]] = None


class CommandRegistry:
    def __init__(self):
        self._commands = {}

    def register(self, command: ShortcutCommand):

        if command.command_id in self._commands:
            raise ValueError(
                f"Command already registered: {command.command_id}"
            )

        self._commands[command.command_id] = command

    def get(self, command_id: str):
        return self._commands.get(command_id)

    def all(self):
        return list(self._commands.values())

    def get_by_category(self, category: str):
        return [
            command
            for command in self._commands.values()
            if command.category == category
        ]
