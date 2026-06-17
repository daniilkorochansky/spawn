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

from core.platform_utils import PlatformUtils

from pathlib import Path

import time
import subprocess
import tempfile
import os

def test_decode_utf8():
    text, enc = (PlatformUtils.decode_text("Привет".encode("utf-8")))
    assert text == "Привет"
    assert enc == "utf-8"

def test_decode_cp1251():
    text, enc = (PlatformUtils.decode_text("Привет".encode("cp1251")))
    assert text == "Привет"
    assert enc == "cp1251"

def test_detect_crlf():
    assert (PlatformUtils.detect_eol(b"line1\r\nline2")== "CRLF")

def test_encode_cp1251():
    data = PlatformUtils.encode_text("Привет","cp1251")
    assert data is not None

def test_encode_cp1251_invalid():
    data = PlatformUtils.encode_text("😀","cp1251")
    assert data is None

def test_detect_lf():
    assert (PlatformUtils.detect_eol(b"line1\nline2")== "LF")

def test_detect_cr():
    assert (PlatformUtils.detect_eol(b"line1\rline2")== "CR")

def test_eol_string_crlf():
    assert (PlatformUtils.eol_string("CRLF")== "\r\n")

def test_eol_string_lf():
    assert (PlatformUtils.eol_string("LF")== "\n")

def test_get_config_dir():
    path = PlatformUtils.get_config_dir()
    assert path
    assert isinstance(path, str)

def test_get_subprocess_startupinfo():
    startupinfo = (PlatformUtils.get_subprocess_startupinfo())

    if PlatformUtils.is_windows():
        assert startupinfo is not None
    else:
        assert startupinfo is None

def test_decode_process_output_utf8():
    text = (PlatformUtils.decode_process_output("Привет".encode("utf-8")))
    assert text == "Привет"

def test_decode_process_output_cp1251():
    text = (PlatformUtils.decode_process_output("Привет".encode("cp1251")))
    assert text == "Привет"

def test_terminate_process():
    process = subprocess.Popen(
        [
            "python",
            "-c",
            "import time; time.sleep(10)"
        ]
    )

    PlatformUtils.terminate_process(process)
    process.wait(timeout=5)
    assert process.poll() is not None

def test_executable_extension():
    ext = PlatformUtils.executable_extension()

    if PlatformUtils.is_windows():
        assert ext == ".exe"
    else:
        assert ext == ""

def test_normalize_path():
    path = PlatformUtils.normalize_path("folder/subfolder/file.txt")

    assert isinstance(path, str)
    assert len(path) > 0

def test_normalize_path_matches_pathlib():
    source = "folder/test.txt"

    normalized = (PlatformUtils.normalize_path(source))

    expected = str(Path(source))

    assert normalized == expected

def test_is_executable_missing():
    assert (PlatformUtils.is_executable("file_that_does_not_exist") is False)

def test_is_executable_existing_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    try:
        result = (PlatformUtils.is_executable(path))

        if PlatformUtils.is_windows():
            assert result is True
        else:
            assert result is False

    finally:
        os.unlink(path)

def test_is_executable_linux():
    if not PlatformUtils.is_linux():
        return

    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name

    try:
        os.chmod(path, 0o755)
        assert (PlatformUtils.is_executable(path)is True)

    finally:
        os.unlink(path)

def test_is_windows_returns_bool():
    assert isinstance(PlatformUtils.is_windows(),bool)

def test_is_linux_returns_bool():
    assert isinstance(PlatformUtils.is_linux(),bool)
