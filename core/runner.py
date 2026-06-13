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

class BackgroundRunner(threading.Thread):
    """
    Runs an server through sampctl in a background thread.

    This class is responsible for launching the server process,
    streaming console output to a wx.RichTextCtrl, handling server
    shutdown requests, and notifying the IDE when the process exits.

    The server is executed using:

        sampctl run

    All stdout and stderr output is captured and forwarded to the
    integrated Spawn console in real time.

    Attributes:
        project_path (str):
            Path to the project directory where the server will be
            started.

        sampctl_bin (str):
            Absolute path to the sampctl executable.

        console (wx.richtext.RichTextCtrl):
            Output console used to display server logs.

        on_finished (callable | None):
            Optional callback invoked when the server process exits.
            Receives a boolean value indicating whether the shutdown
            was requested by the user.

        process (subprocess.Popen | None):
            Active server process instance.

        _stop_requested (bool):
            Indicates whether a stop request was initiated by the user.

    Features:
        - Background server execution
        - Real-time console output streaming
        - UTF-8 and CP1251 output decoding
        - Graceful server termination support
        - Automatic UI notification on process exit
    """
    def __init__(self, project_path, sampctl_executable, rich_text_ctrl, on_finished_callback=None):
        super().__init__()
        self.project_path = project_path
        self.sampctl_bin = sampctl_executable
        self.console = rich_text_ctrl
        self.on_finished = on_finished_callback
        self.process = None
        self._stop_requested = False

    def run(self):
        startupinfo = None
        if os.name =='nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        cmd = [self.sampctl_bin, "run"]

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
                            decoded_line = buffer.decode('cp1251')
                        wx.CallAfter(self.append_to_rich_console, decoded_line)
                        buffer.clear()
                else:
                    break
            if buffer:
                try:
                    decoded_line = buffer.decode('utf-8')
                except UnicodeDecodeError:
                    decoded_line = buffer.decode('cp1251')
                wx.CallAfter(self.append_to_rich_console, decoded_line)
                    
            if self.on_finished:
                wx.CallAfter(self.on_finished, self._stop_requested)
                
        except Exception as e:
            SpawnLogger.error(f"Server Startup: {e}")
            wx.CallAfter(self.append_to_rich_console, _(u"Server startup error: {e}\n").format(e=e))
            if self.on_finished:
                wx.CallAfter(self.on_finished, False)


    def stop_server(self):
        if self.process and self.process.poll() is None:
            self._stop_requested = True
            try:
                if os.name == 'nt':
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                        )
                else:
                    self.process.terminate()
            except Exception as e:
                SpawnLogger.error(f"Server Stop: {e}")

    def append_to_rich_console(self, text):
        if self.console:
            self.console.MoveEnd()

            self.console.WriteText(text)
            self.console.ShowPosition(self.console.GetLastPosition())
