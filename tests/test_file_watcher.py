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

from unittest.mock import Mock

from core.file_watcher import ProjectFileWatcher

class FakeHandler:
    def __init__(self):
        self.is_paused = False

def test_trigger_debounce_starts_timer():
    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    watcher.timer = Mock()
    watcher.trigger_debounce()
    watcher.timer.Start.assert_called_once_with(300,oneShot=True)

def test_stop_stops_timer():
    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    timer = Mock()
    timer.IsRunning.return_value = True

    watcher.timer = timer
    watcher.observer = None

    watcher.stop()

    timer.Stop.assert_called_once()
    assert watcher.timer is None

def test_stop_stops_observer():
    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    observer = Mock()

    watcher.timer = None
    watcher.observer = observer

    watcher.stop()

    observer.stop.assert_called_once()
    observer.join.assert_called_once()

    assert watcher.observer is None

def test_pause_sets_handler_state():
    handler = FakeHandler()

    observer = Mock()
    observer._handlers = {
        object(): [handler]
    }

    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    watcher.observer = observer
    watcher.timer = None

    watcher.pause()

    assert handler.is_paused is True

def test_debounce_refreshes_project_tree(tmp_path):
    main_window = Mock()

    main_window.current_project_path = str(tmp_path)

    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    watcher.main_window = main_window

    watcher.on_debounce_timer(None)

    main_window.refresh_project_tree.assert_called_once()

def test_debounce_ignores_missing_project():
    main_window = Mock()

    main_window.current_project_path = None

    watcher = ProjectFileWatcher.__new__(
        ProjectFileWatcher
    )

    watcher.main_window = main_window

    watcher.on_debounce_timer(None)

    main_window.refresh_project_tree.assert_not_called()
