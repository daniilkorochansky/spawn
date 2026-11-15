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

class GitResetWorker(threading.Thread):
    def __init__(self, repo_obj, on_finished_callback):
        super().__init__()
        self.repo = repo_obj
        self.on_finished = on_finished_callback


    def run(self):
        try:
            # Discard all tracked changes and staged changes.
            self.repo.git.reset("--hard", "HEAD")

            wx.CallAfter(self.on_finished, True, "")

        except Exception as e:
            error_message = str(e)

            # Verify whether the reset actually completed.
            try:
                if (
                    self.repo.head.is_valid()
                    and not self.repo.is_dirty(untracked_files=False)
                ):
                    wx.CallAfter(self.on_finished, True, "")
                    return

            except Exception as verification_error:
                error_message += (
                    f"; verification failed: {verification_error}"
                )

            wx.CallAfter(
                self.on_finished,
                False,
                error_message
            )

