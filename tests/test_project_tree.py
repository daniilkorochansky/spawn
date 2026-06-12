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

from unittest.mock import patch

from ui.project_tree import ProjectTreeManager

class FakeTreeCtrl:
    def __init__(self):
        self.nodes = []


    def Freeze(self):
        pass

    def Thaw(self):
        pass

    def DeleteAllItems(self):
        self.nodes.clear()

    def AddRoot(self, text, image=None):
        self.nodes.append(("root", text))
        return "root"

    def AppendItem(self, parent, text, image=None):
        self.nodes.append(("item", text))
        return text

    def SetItemImage(self, *args):
        pass

    def SetItemData(self, *args):
        pass

    def Expand(self, *args):
        pass

@patch("wx.GetTopLevelParent", return_value=None)
def test_populate_tree_shows_only_supported_files(mock_parent, tmp_path):
    (tmp_path / "main.pwn").write_text("")
    (tmp_path / "dialog.inc").write_text("")
    (tmp_path / "pawn.json").write_text("")
    (tmp_path / "server.cfg").write_text("")
    (tmp_path / "readme.txt").write_text("")
    (tmp_path / "config.yaml").write_text("")
    (tmp_path / "pawn.lock").write_text("")

    (tmp_path / "image.png").write_text("")
    (tmp_path / "archive.zip").write_text("")
    (tmp_path / "music.mp3").write_text("")

    tree = FakeTreeCtrl()

    icon_indices = {
        "folder_root": 0,
        "folder_root_opened": 1,
        "folder": 2,
        "folder_opened": 3,
        "file": 4,
        "pawn": 5,
        "pawn_inc": 6,
        "cfg": 7,
    }

    ProjectTreeManager.populate_tree(
        tree,
        str(tmp_path),
        icon_indices,
    )

    labels = [node[1] for node in tree.nodes]

    assert "main.pwn" in labels
    assert "dialog.inc" in labels
    assert "pawn.json" in labels
    assert "server.cfg" in labels
    assert "readme.txt" in labels
    assert "config.yaml" in labels
    assert "pawn.lock" in labels

    assert "image.png" not in labels
    assert "archive.zip" not in labels
    assert "music.mp3" not in labels

@patch("wx.GetTopLevelParent", return_value=None)
def test_populate_tree_sorts_files_alphabetically(mock_parent, tmp_path):
    (tmp_path / "zebra.pwn").write_text("")
    (tmp_path / "alpha.pwn").write_text("")
    (tmp_path / "test.pwn").write_text("")

    tree = FakeTreeCtrl()

    icon_indices = {
        "folder_root": 0,
        "folder_root_opened": 1,
        "folder": 2,
        "folder_opened": 3,
        "file": 4,
        "pawn": 5,
        "pawn_inc": 6,
        "cfg": 7,
    }

    ProjectTreeManager.populate_tree(
        tree,
        str(tmp_path),
        icon_indices,
    )

    file_names = [
        node[1]
        for node in tree.nodes
        if node[1].endswith(".pwn")
    ]

    assert file_names == [
        "alpha.pwn",
        "test.pwn",
        "zebra.pwn",
    ]

@patch("wx.GetTopLevelParent", return_value=None)
def test_populate_tree_ignores_special_directories(mock_parent, tmp_path):
    (tmp_path / "gamemodes").mkdir()
    (tmp_path / "plugins").mkdir()
    (tmp_path / "components").mkdir()
    (tmp_path / "dependencies").mkdir()
    (tmp_path / ".git").mkdir()


    (tmp_path / "main.pwn").write_text("main() {}")

    tree = FakeTreeCtrl()

    icon_indices = {
        "folder_root": 0,
        "folder_root_opened": 1,
        "folder": 2,
        "folder_opened": 3,
        "file": 4,
        "pawn": 5,
        "pawn_inc": 6,
        "cfg": 7,
    }

    ProjectTreeManager.populate_tree(
        tree,
        str(tmp_path),
        icon_indices,
    )

    labels = [node[1] for node in tree.nodes]

    assert "gamemodes" in labels
    assert "main.pwn" in labels

    assert "plugins" not in labels
    assert "components" not in labels
    assert "dependencies" not in labels

@patch("wx.GetTopLevelParent", return_value=None)
def test_populate_tree_scans_subdirectories(mock_parent, tmp_path):
    gamemodes_dir = tmp_path / "gamemodes"
    core_dir = gamemodes_dir / "core"

    gamemodes_dir.mkdir()
    core_dir.mkdir()

    (core_dir / "main.pwn").write_text("")

    tree = FakeTreeCtrl()

    icon_indices = {
        "folder_root": 0,
        "folder_root_opened": 1,
        "folder": 2,
        "folder_opened": 3,
        "file": 4,
        "pawn": 5,
        "pawn_inc": 6,
        "cfg": 7,
    }

    ProjectTreeManager.populate_tree(
        tree,
        str(tmp_path),
        icon_indices,
    )

    labels = [node[1] for node in tree.nodes]

    assert "gamemodes" in labels
    assert "core" in labels
    assert "main.pwn" in labels
