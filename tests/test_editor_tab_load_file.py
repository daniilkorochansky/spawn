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

from ui.editor_tab import CustomEditorTab

class FakeEditor:
    def __init__(self):
        self.text = ""
        self.eol_mode = None
        self.code_page = None

    def SetCodePage(self, value):
        self.code_page = value

    def SetText(self, value):
        self.text = value

    def SetEOLMode(self, value):
        self.eol_mode = value

    def Freeze(self):
        pass

    def Thaw(self):
        pass

    def EmptyUndoBuffer(self):
        pass

    def SetSavePoint(self):
        pass

def test_load_utf8_file(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_bytes(
        b"Hello\nWorld"
    )

    tab = CustomEditorTab.__new__(CustomEditorTab)
    tab.m_scintilla_Editor = FakeEditor()

    tab.load_file(str(file_path))

    assert tab.current_encoding == "utf-8"
    assert tab.native_eol == "LF"
    assert tab.m_scintilla_Editor.text == "Hello\nWorld"

def test_load_crlf_file(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_bytes(
        b"line1\r\nline2\r\n"
    )

    tab = CustomEditorTab.__new__(CustomEditorTab)
    tab.m_scintilla_Editor = FakeEditor()

    tab.load_file(str(file_path))

    assert tab.native_eol == "CRLF"

def test_load_lf_file(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_bytes(
        b"line1\nline2\n"
    )

    tab = CustomEditorTab.__new__(CustomEditorTab)
    tab.m_scintilla_Editor = FakeEditor()

    tab.load_file(str(file_path))

    assert tab.native_eol == "LF"

def test_load_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"

    file_path.write_bytes(b"")

    tab = CustomEditorTab.__new__(CustomEditorTab)
    tab.m_scintilla_Editor = FakeEditor()

    tab.load_file(str(file_path))

    assert tab.current_encoding == "utf-8"
    assert tab.native_eol == "CRLF"
    assert tab.m_scintilla_Editor.text == ""

def test_load_normalizes_crlf_to_lf_for_scintilla(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_bytes(
        b"line1\r\nline2\r\n"
    )

    tab = CustomEditorTab.__new__(CustomEditorTab)
    tab.m_scintilla_Editor = FakeEditor()

    tab.load_file(str(file_path))

    assert tab.m_scintilla_Editor.text == (
        "line1\nline2\n"
    )
