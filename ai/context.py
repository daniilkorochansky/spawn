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

"""Reserved, opt-in context model for future editor/project integration."""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AIContext:
    """Context payload kept separate from provider and UI layers.

    The first release sends only chat messages. Later features can populate these
    fields without changing the chat transport API.
    """
    current_file: str | None = None
    selected_code: str | None = None
    compiler_output: str | None = None
    project_files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
