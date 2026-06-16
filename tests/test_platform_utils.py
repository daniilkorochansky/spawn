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
