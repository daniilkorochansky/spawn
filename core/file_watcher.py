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
import wx

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.is_paused = False

    def on_any_event(self, event):
        if self.is_paused:
            return
        
        if any(folder in event.src_path for folder in [".git", "dependencies", "components"]): #На какие папки и файлы не обращать внимание
            return

        if event.is_directory and event.event_type == 'modified':
            return

        wx.CallAfter(self.callback)

class ProjectFileWatcher:
    def __init__(self, main_window):
        self.main_window = main_window
        self.observer = None
        self.timer = None

        self.timer_id = wx.NewIdRef()
        self.main_window.Bind(wx.EVT_TIMER, self.on_debounce_timer, self.timer_id)
 
    def start(self, path):
        self.stop()

        if not path or not os.path.exists(path):
            return

        self.timer = wx.Timer(self.main_window, self.timer_id)

        try:
            handler = ProjectHandler(self.trigger_debounce)
            self.observer = Observer()

            self.observer.schedule(handler, path, recursive=True)
            self.observer.start()
        except Exception as e:
            self.stop()

    def pause(self):
        if self.observer:
            for watch, handlers in self.observer._handlers.items():
                for h in handlers:
                    if hasattr(h, "is_paused"):
                        h.is_paused = True
        if self.timer and self.timer.IsRunning():
            self.timer.Stop()

    def resume(self):
        if self.observer:
            for watch, handlers in self.observer._handlers.items():
                for h in handlers:
                    if hasattr(h, "is_paused"):
                        h.is_paused = False

    def trigger_debounce(self):
        if self.timer:
            self.timer.Start(300, oneShot=True)

    def on_debounce_timer(self, event):
        if not self.main_window:
            return

        current_path = getattr(self.main_window, "current_project_path", None)
        if current_path and os.path.exists(current_path):
            if hasattr(self.main_window, "refresh_project_tree"):
                self.main_window.refresh_project_tree()
            else:
                self.stop()

    def stop(self):
        if self.timer and self.timer.IsRunning():
            self.timer.Stop()
        self.timer = None

        if self.observer:
            try:
                self.observer.stop()
                self.observer.join()
            except Exception:
                pass
            self.observer = None
