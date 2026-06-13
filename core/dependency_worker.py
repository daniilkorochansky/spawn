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

class DependencyDownloadWorker(threading.Thread):
    def __init__(self, project_path, sampctl_bin, package_url, ui_callback, add_command=""):
        super().__init__()
        self.project_path = project_path
        self.sampctl_bin = sampctl_bin
        self.package_url = package_url
        self.ui_callback = ui_callback
        self.add_command = add_command

    def run(self):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        cmd = [self.sampctl_bin,self.add_command, self.package_url]
        try:
            wx.CallAfter(self.ui_callback, 10, _(u"Preparing to work with dependency..."))

            process = subprocess.Popen(
                cmd,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                bufsize=0
                )

            step = 15
            while True:
                line_bytes = process.stdout.readline()
                if not line_bytes and process.poll() is not None:
                    break

                if line_bytes:
                    try:
                        line_text = line_bytes.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        line_text = line_bytes.decode('cp1251', errors="replace").strip()

                    status = line_text
                    
                    wx.CallAfter(self.ui_callback, 40, status)

            success = (process.returncode == 0)
            if success:
                wx.CallAfter(self.ui_callback, 100, u"")
            else:
                
                wx.CallAfter(self.ui_callback, -1, _(u"The process has been interrupted."))
        except Exception as e:
            SpawnLogger.warning(f"Dependency Worker(Run) Warning: {e}")
            wx.CallAfter(self.ui_callback, -1, f"{e}")
