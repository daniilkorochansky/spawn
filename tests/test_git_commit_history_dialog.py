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

from unittest.mock import Mock

from git import Repo
import wx

from ui.git_commit_history_dialog import GitCommitHistoryDialog

class FakeListCtrl:
    def __init__(self):
        self.rows = []

    def DeleteAllItems(self):
        self.rows.clear()

    def InsertItem(self, idx, text):
        self.rows.append([text, "", "", ""])
        return idx

    def SetItem(self, row, col, value):
        self.rows[row][col] = value

    def SetItemData(self, row, data):
        pass

    def GetItemText(self, row, col=0):
        return self.rows[row][col]

class FakeListBox:
    def __init__(self):
        self.items = []

    def Clear(self):
        self.items.clear()

    def Append(self, value):
        self.items.append(value)

class FakeEvent:
    def GetIndex(self):
        return 0

def test_populate_commit_history(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"

    file_path.write_text("v1")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    file_path.write_text("v2")

    repo.index.add(["main.pwn"])
    repo.index.commit("Second commit")

    dialog = GitCommitHistoryDialog.__new__(
        GitCommitHistoryDialog
    )

    dialog.repo = repo
    dialog.commits_list = []
    dialog.m_listCtrl_Log = FakeListCtrl()
    dialog.m_listBox_Files = FakeListBox()

    dialog.populate_commit_history()

    assert len(dialog.commits_list) == 1
    assert len(dialog.m_listCtrl_Log.rows) == 1

def test_hash_map_is_created(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"

    file_path.write_text("v1")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    file_path.write_text("v2")

    repo.index.add(["main.pwn"])
    repo.index.commit("Second commit")

    dialog = GitCommitHistoryDialog.__new__(
        GitCommitHistoryDialog
    )

    dialog.repo = repo
    dialog.commits_list = []
    dialog.m_listCtrl_Log = FakeListCtrl()
    dialog.m_listBox_Files = FakeListBox()

    dialog.populate_commit_history()

    assert len(dialog.hash_map) == 1

def test_trigger_reset_action():
    callback = Mock()

    dialog = GitCommitHistoryDialog.__new__(
        GitCommitHistoryDialog
    )

    dialog.execute_reset = callback
    dialog.EndModal = Mock()

    dialog.trigger_reset_action(
        "abc123",
        True
    )

    dialog.EndModal.assert_called_once_with(
        wx.ID_OK
    )

    callback.assert_called_once_with(
        "abc123",
        True
    )

def test_show_changed_files(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"

    file_path.write_text("test")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    file_path.write_text("test2")

    repo.index.add(["main.pwn"])
    repo.index.commit("Update")

    dialog = GitCommitHistoryDialog.__new__(
        GitCommitHistoryDialog
    )

    dialog.repo = repo
    dialog.commits_list = []
    dialog.m_listCtrl_Log = FakeListCtrl()
    dialog.m_listBox_Files = FakeListBox()

    dialog.populate_commit_history()

    dialog.on_history_item_selected(
        FakeEvent()
    )

    assert len(
        dialog.m_listBox_Files.items
    ) > 0
