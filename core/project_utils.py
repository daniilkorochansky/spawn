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

from pathlib import Path

PROJECT_GITIGNORE_FILES = (
    "pawn.lock",
    "log.txt",
    "bans.json",
    ".spawn/",
    ".editorconfig",
    ".spawn",
)

def ensure_project_gitignore(project_path: str) -> None:
    project_dir = Path(project_path)
    gitignore_path = project_dir / ".gitignore"

    if not gitignore_path.is_file():
        return

    try:
        text = gitignore_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return

    lines = {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    missing = [
        filename
        for filename in PROJECT_GITIGNORE_FILES
        if filename not in lines
    ]

    if not missing:
        return

    try:
        with gitignore_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as file:
            if text and not text.endswith(("\n", "\r")):
                file.write("\n")

            file.write("\n# Spawn / server files\n")

            for filename in missing:
                file.write(f"{filename}\n")

    except OSError:
        pass
