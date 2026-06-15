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

import os
import subprocess
import threading

import wx

from core.logger import SpawnLogger

import gettext
_ = gettext.gettext

class BackgroundCompiler(threading.Thread):
    """
    Runs a server build through sampctl in a background thread.

    This class is responsible for executing the build process,
    capturing compiler output in real time, forwarding messages
    to the integrated Spawn build console, and notifying the IDE
    when compilation has finished.

    The build is executed using:

        sampctl build

    Additional compiler flags may be passed to customize the
    build process.

    All stdout and stderr output is captured and streamed to the
    build output panel as it becomes available.

    Attributes:
        project_path (str):
            Path to the project directory containing the Pawn
            source code and pawn.json configuration.

        sampctl_bin (str):
            Absolute path to the sampctl executable.

        build_target (str):
            Reserved build target identifier for future build
            configurations.

        extra_flags (str):
            Additional command-line flags passed to the compiler.

        console (wx.richtext.RichTextCtrl):
            Output console used to display build and compiler logs.

        on_finished (callable | None):
            Optional callback invoked when the build process 
            completes. Receives a boolean value indicating  
            whether the build succeeded.

        process (subprocess.Popen | None):
            Active compiler process instance.

    Features:
        - Background server compilation
        - Real-time compiler output streaming
        - UTF-8 and CP1251 output decoding
        - Build success/failure reporting
        - Automatic UI notification on completion
        - Support for additional compiler flags
    """
    def __init__(self, project_path, sampctl_executable, build_target, extra_flags, rich_text_ctrl, on_finished_callback=None):
        super().__init__()
        self.project_path = project_path
        self.sampctl_bin = sampctl_executable if sampctl_executable else "sampctl"
        self.build_target = build_target
        self.extra_flags = extra_flags
        self.console = rich_text_ctrl
        self.on_finished = on_finished_callback
        self.process = None

    def run(self):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        cmd = [self.sampctl_bin, "build"]
        if self.extra_flags:
            cmd.extend(["--", self.extra_flags])

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                bufsize=0
                )

            buffer = bytearray()
            
            while True:
                char_byte = self.process.stdout.read(1)
                if char_byte:
                    buffer.extend(char_byte)
                    if char_byte == b"\n":
                        try:
                            decoded_line = buffer.decode('utf-8')
                        except UnicodeDecodeError:
                            decoded_line = buffer.decode('cp1251', errors="replace")
                        wx.CallAfter(self.append_to_rich_console, decoded_line)
                        buffer.clear()
                    
                return_code = self.process.poll()
                if return_code is not None:
                    remaining_data = self.process.stdout.read()
                    if remaining_data:
                        buffer.extend(remaining_data)
                        for line in buffer.split(b"\n"):
                            if line.strip():
                                try:
                                    decoded_line = line.decode('utf-8')
                                except UnicodeDecodeError:
                                    decoded_line = line.decode('cp1251', errors="replace")
                                wx.CallAfter(self.append_to_rich_console, decoded_line)
                    break
            success = (return_code == 0)
            if self.on_finished:
                wx.CallAfter(self.on_finished, success)
        except Exception as e:
            SpawnLogger.error(f"Compiler Call: {e}")
            wx.CallAfter(self.append_to_rich_console, _(u"Compiler call error: {e}\n").format(e=e))
            if self.on_finished:
                wx.CallAfter(self.on_finished, False)

    def append_to_rich_console(self, text):
        if self.console:
            self.console.MoveEnd()

            self.console.WriteText(text)
            self.console.ShowPosition(self.console.GetLastPosition())
    
