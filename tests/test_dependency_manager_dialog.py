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

from ui.dependency_manager_dialog import DependencyManagerDialog

import json

class FakeListBox:
    def __init__(self):
        self.items = []

    def Clear(self):
        self.items.clear()

    def Append(self, item):
        self.items.append(item)

def test_load_current_dependencies(tmp_path):
    pawn_json = {
        "dependencies": [
            "Southclaws/zcmd",
            "pawn-lang/YSI-Includes"
        ]
    }

    (tmp_path / "pawn.json").write_text(
        json.dumps(pawn_json),
        encoding="utf-8"
    )

    zcmd_dir = tmp_path / "dependencies" / "zcmd"
    zcmd_dir.mkdir(parents=True)

    (zcmd_dir / "pawn.json").write_text(
        "{}",
        encoding="utf-8"
    )

    dialog = DependencyManagerDialog.__new__(
        DependencyManagerDialog
    )

    dialog.project_path = str(tmp_path)
    dialog.m_listBox_Dependency = FakeListBox()

    dialog.load_current_dependencies()

    assert dialog.m_listBox_Dependency.items == [
        "Southclaws/zcmd"
    ]

def test_load_current_dependencies_empty_list(tmp_path):
    pawn_json = {
        "dependencies": []
    }

    (tmp_path / "pawn.json").write_text(
        json.dumps(pawn_json),
        encoding="utf-8"
    )

    dialog = DependencyManagerDialog.__new__(
        DependencyManagerDialog
    )

    dialog.project_path = str(tmp_path)
    dialog.m_listBox_Dependency = FakeListBox()

    dialog.load_current_dependencies()

    assert dialog.m_listBox_Dependency.items == []

def test_load_current_dependencies_without_pawn_json(tmp_path):
    dialog = DependencyManagerDialog.__new__(
        DependencyManagerDialog
    )

    dialog.project_path = str(tmp_path)
    dialog.m_listBox_Dependency = FakeListBox()

    dialog.load_current_dependencies()

    assert dialog.m_listBox_Dependency.items == []

def test_load_dependency_with_version(tmp_path):
    pawn_json = {
        "dependencies": [
            "Southclaws/zcmd:1.0.0"
        ]
    }

    (tmp_path / "pawn.json").write_text(
        json.dumps(pawn_json),
        encoding="utf-8"
    )

    dep_dir = tmp_path / "dependencies" / "zcmd"
    dep_dir.mkdir(parents=True)

    (dep_dir / "pawn.json").write_text(
        "{}",
        encoding="utf-8"
    )

    dialog = DependencyManagerDialog.__new__(
        DependencyManagerDialog
    )

    dialog.project_path = str(tmp_path)
    dialog.m_listBox_Dependency = FakeListBox()

    dialog.load_current_dependencies()

    assert dialog.m_listBox_Dependency.items == [
        "Southclaws/zcmd:1.0.0"
    ]
