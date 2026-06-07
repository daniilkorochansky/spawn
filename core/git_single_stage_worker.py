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
import wx

class GitSingleStageWorker(threading.Thread):
    def __init__(self, repo_obj, relative_file_path, is_unstage, on_finished_callback):
        """
        repo_obj: Объект Repo из GitPython
        relative_file_path: Относительный путь
        is_unstage: True если убираем из индекса, False если добавляем
        """
        super().__init__()
        self.repo = repo_obj
        self.rel_path = relative_file_path
        self.is_unstage = is_unstage
        self.on_finished = on_finished_callback

    def run(self):
        max_retries = 3
        success = False
        error_msg = ""

        for attempt in range(max_retries):
            try:
                if self.is_unstage:
                    self.repo.index.reset(commit='HEAD', paths=[self.rel_path], working_tree=False)
                else:
                    self.repo.git.add(self.rel_path)

                success = True
                
                break
            
            except Exception as e:
                error_msg = str(e)
                print(f"Попытка индексации {attempt + 1} сорвалась. Ждём...")
                time.sleep(0.08)

        wx.CallAfter(self.on_finished, success, self.rel_path, error_msg)
