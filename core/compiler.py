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

class BackgroundCompiler(threading.Thread):
    def __init__(self, project_path, sampctl_executable, build_target, extra_flags, rich_text_ctrl, on_finished_callback=None):
        super().__init__()
        self.project_path = project_path
        self.sampctl_bin = sampctl_executable if sampctl_executable else "sampctl"
        self.build_target = build_target
        self.extra_flags = extra_flags
        self.console = rich_text_ctrl
        self.on_finished = on_finished_callback
        self.process = None
        print(self.sampctl_bin)

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
            wx.CallAfter(self.append_to_rich_console, f"[Spawn Error] Ошибка вызова компилятора: {e}\n")
            if self.on_finished:
                wx.CallAfter(self.on_finished, False)

    def append_to_rich_console(self, text):
        if self.console:
            self.console.MoveEnd()

            self.console.WriteText(text)
            self.console.ShowPosition(self.console.GetLastPosition())
    
