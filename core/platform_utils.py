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

from platformdirs import user_config_dir

from pathlib import Path
import sys
import subprocess
import os

class PlatformUtils:

    @staticmethod
    def get_config_dir():
        return str(Path(user_config_dir("Spawn")))

    @staticmethod
    def normalize_path(path):
        return str(Path(path)).replace("\\", "/")

    @staticmethod
    def detect_eol(binary_data):
        if b"\r\n" in binary_data:
            return "CRLF"

        if b"\n" in binary_data:
            return "LF"

        if b"\r" in binary_data:
            return "CR"

        return "LF"

    @staticmethod
    def decode_text(binary_data):
        try:
            return (binary_data.decode("utf-8"),"utf-8")

        except UnicodeDecodeError:
            try:
                return (binary_data.decode("cp1251"),"cp1251")

            except UnicodeDecodeError:
                return (binary_data.decode("utf-8",errors="replace"),"utf-8")

    @staticmethod
    def encode_text(text,encoding):
        try:
            return text.encode(encoding,errors="strict")
        except UnicodeEncodeError:
            return None

    @staticmethod
    def default_eol():
        if sys.platform.startswith("win"):
            return "CRLF"
        return "LF"

    @staticmethod
    def eol_string(eol):
        mapping = {"CRLF": "\r\n","LF": "\n","CR": "\r"}
        return mapping.get(eol,"\n")

    @staticmethod
    def can_encode(text,encoding):
        try:
            text.encode(encoding,errors="strict")
            return True
        except UnicodeEncodeError:
            return False

    @staticmethod
    def default_editor_font():
        if sys.platform.startswith("win"):
            return "Consolas"

        if sys.platform.startswith("linux"):
            return "DejaVu Sans Mono"

        if sys.platform == "darwin":
            return "Menlo"

        return ""

    @staticmethod
    def decode_process_output(data):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return data.decode("cp1251")
            except UnicodeDecodeError:
                return data.decode("utf-8",errors="replace")

    @staticmethod
    def is_windows():
        return sys.platform.startswith("win")

    @staticmethod
    def get_subprocess_startupinfo():
        if not PlatformUtils.is_windows():
            return None

        startupinfo = (subprocess.STARTUPINFO())
        startupinfo.dwFlags |= (subprocess.STARTF_USESHOWWINDOW)
        return startupinfo

    @staticmethod
    def terminate_process(process):
        if process is None:
            return

        if process.poll() is not None:
            return

        if PlatformUtils.is_windows():

            subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/T",
                    "/PID",
                    str(process.pid)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
                )
        else:
            process.terminate()

    @staticmethod
    def is_executable(path):
        if not os.path.isfile(path):
            return False

        if PlatformUtils.is_windows():
            return True

        return os.access(path, os.X_OK)

    @staticmethod
    def is_linux():
        return sys.platform.startswith("linux")

    @staticmethod
    def executable_extension():
        if PlatformUtils.is_windows():
            return ".exe"

        return ""

    @staticmethod
    def open_directory(path):
        if not os.path.exists(path):
            return False

        try:
            if PlatformUtils.is_windows():
                os.startfile(path)
            else:
                subprocess.Popen(
                    ["xdg-open", path]
                )

            return True

        except Exception:
            return False
