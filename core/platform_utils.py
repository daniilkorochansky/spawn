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
import shutil
import re
import codecs

CODING_RE = re.compile(rb'^\s*//.*?coding\s*:\s*([a-zA-Z0-9_\-]+)',re.IGNORECASE | re.MULTILINE)

class PlatformUtils:
    SUPPORTED_ENCODINGS = (
    "utf-8",
    "cp1251",
    "cp1252",
    "cp1254",
    "cp1250",
    "cp1257",
    "cp1253",
    "cp1255",
    "cp1256",
    )
    
    @staticmethod
    def detect_declared_encoding_from_text(text):
        if not isinstance(text, str):
            return None

        lines = text.splitlines()[:5]
        for line in lines:
            if not line.lstrip().startswith("//"):
                continue

            match = re.search(r'^\s*//.*?coding\s*:\s*([a-zA-Z0-9_\-]+)',line,re.IGNORECASE)

            if not match:
                continue

            try:
                encoding = codecs.lookup(match.group(1).strip()).name

            except LookupError:
                return None

            if not PlatformUtils.is_supported_encoding(encoding):
                return None

            return encoding

        return None

    @staticmethod
    def is_pawn_file(path):
        return Path(path).suffix.lower() in (".pwn",".inc")

    @staticmethod
    def is_supported_encoding(encoding):
        if not isinstance(encoding, str):
            return False

        return (encoding.lower() in PlatformUtils.SUPPORTED_ENCODINGS)

    @staticmethod
    def detect_declared_encoding(binary_data):

        head = b"\n".join(binary_data.splitlines()[:5])
        match = CODING_RE.search(head)
        if not match:
            return None
        
        encoding = (match.group(1).decode("ascii").strip().lower())
        if not PlatformUtils.is_supported_encoding(encoding):
            return None

        try:
            encoding = (match.group(1).decode("ascii").strip().lower())

            return codecs.lookup(encoding).name

        except (LookupError,UnicodeDecodeError):
            return None

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
        declared = (PlatformUtils.detect_declared_encoding(binary_data))
        if declared:

            try:
                return (binary_data.decode(declared),declared)

            except (LookupError,UnicodeDecodeError):
                pass

        for encoding in PlatformUtils.SUPPORTED_ENCODINGS:
            try:
                return (binary_data.decode(encoding),encoding)

            except UnicodeDecodeError:
                continue

        return (binary_data.decode("utf-8",errors="replace"),"utf-8")

    @staticmethod
    def encode_text(text, encoding):
        if not isinstance(text, str):
            text = str(text)

        try:
            return text.encode(encoding,errors="strict")

        except (LookupError,UnicodeEncodeError):
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

    @staticmethod
    def get_terminal():
        candidates = [
            "gnome-terminal",
            "konsole",
            "xfce4-terminal",
            "xterm"
        ]

        for term in candidates:
            if shutil.which(term):
                return term

        return None

    @staticmethod
    def create_terminal_command(executable, args):
        term = PlatformUtils.get_terminal()
        if os.name == "nt":
            return [
                "cmd.exe",
                "/K",
                executable,
                *args
            ]

        if not term:
            return [executable, *args]

        if term == "gnome-terminal":
            return [term, "--", executable, *args]

        return [term, "-e", executable, *args]
