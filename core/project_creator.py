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

import threading
import subprocess
import os
import wx

class ProjectCreateWorker(threading.Thread):
    def __init__(self, target_path, sampctl_path, on_finished_callback):
        super().__init__()
        self.target_path = target_path
        self.sampctl_path = sampctl_path
        self.on_finished = on_finished_callback

    def run(self):
        try:
            
            exec_command = os.path.normpath(self.sampctl_path)
            print(exec_command)
            cmd = (f'cmd.exe /K "cls && echo ========================================== && echo Initializing new server... && echo ========================================== && echo. && "{exec_command}" init"')
            process = subprocess.Popen(
                cmd,
                cwd=self.target_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            process.wait()

            wx.CallAfter(self.on_finished, True, self.target_path)
        except Exception as e:
            wx.CallAfter(self.on_finished, False, self.target_path, str(e))
