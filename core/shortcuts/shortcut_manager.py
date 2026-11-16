# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Spawn — IDE with a native user interface for SA-MP and open.mp server development.
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

import wx

from core.logger import SpawnLogger
from core.shortcuts.shortcut_parser import ShortcutParser

_TEXT_INPUT_TYPES = tuple(
    control_type
    for control_type in (
        getattr(wx, "TextCtrl", None),
        getattr(wx, "SearchCtrl", None),
        getattr(wx, "ComboBox", None),
        getattr(wx, "ComboCtrl", None),
        getattr(wx, "SpinCtrl", None),
        getattr(wx, "SpinCtrlDouble", None),
    )
    if isinstance(control_type, type)
)

class ShortcutManager:

    def __init__(
        self,
        frame,
        command_registry,
        keybindings_manager
    ):

        self.frame = frame
        self.command_registry = command_registry
        self.keybindings_manager = keybindings_manager

        self.parser = ShortcutParser()

        self._bindings = {}
        self._conflicts = []
        self._bound = False

        self.rebuild()


    def refresh_availability(self):
        for command in self.command_registry.all():

            if command.enabled_when is None:
                continue

            menu_item = command.menu_item

            if menu_item is None:
                continue

            available = self._evaluate_availability(command)

            try:
                menu_item.Enable(available)

            except Exception as exc:
                SpawnLogger.warning(
                    f"Could not update menu state for "
                    f"{command.command_id}: {exc}"
                )

    def _evaluate_availability(self, command):
        checker = command.enabled_when

        if checker is None:
            return True

        try:
            return bool(checker())

        except Exception as exc:
            SpawnLogger.warning(
                f"Shortcut availability check failed "
                f"for {command.command_id}: {exc}"
            )

            return False


    def is_command_available(self, command):
        if not self._evaluate_availability(command):
            return False

        menu_item = command.menu_item

        if menu_item is not None:
            if not menu_item.IsEnabled():
                return False

        return True

    # --------------------------------------------------
    # BIND / UNBIND
    # --------------------------------------------------

    def bind(self):

        if self._bound:
            return

        self._clear_native_menu_accelerators()

        self.frame.Bind(
            wx.EVT_CHAR_HOOK,
            self.on_char_hook
        )

        self._bound = True

        self.frame.Bind(
            wx.EVT_MENU_OPEN,
            self.on_menu_open
        )

        self.refresh_availability()

    def on_menu_open(self, event):
        self.refresh_availability()
        event.Skip()

    def unbind(self):
        if not self._bound:
            return

        self.frame.Unbind(
            wx.EVT_CHAR_HOOK,
            handler=self.on_char_hook
        )

        self._bound = False

        self.frame.Unbind(
            wx.EVT_MENU_OPEN,
            handler=self.on_menu_open
        )

    # --------------------------------------------------
    # REMOVE OLD MENU ACCELERATORS
    # --------------------------------------------------

    def _clear_native_menu_accelerators(self):

        for command in self.command_registry.all():

            menu_item = command.menu_item

            if menu_item is None:
                continue

            try:

                label = menu_item.GetItemLabelText()

                menu_item.SetItemLabel(label)

            except Exception as exc:

                SpawnLogger.warning(
                    f"Could not clear menu accelerator "
                    f"for {command.command_id}: {exc}"
                )

    # --------------------------------------------------
    # BUILD SHORTCUT MAP
    # --------------------------------------------------

    def rebuild(self):

        self._bindings.clear()
        self._conflicts.clear()

        for command in self.command_registry.all():

            shortcut = self.keybindings_manager.get_shortcut(
                command.command_id,
                command.default_shortcut
            )

            if shortcut is None:
                continue

            try:

                signature = self.parser.parse(shortcut)

            except ValueError as exc:

                SpawnLogger.warning(
                    f"Invalid shortcut for "
                    f"{command.command_id}: {exc}"
                )

                continue

            context = command.context.strip().lower()

            key = (context, signature)

            self._bindings.setdefault(
                key,
                []
            ).append(command)

        for (context, signature), commands in self._bindings.items():

            if len(commands) > 1:

                self._conflicts.append({
                    "context": context,
                    "shortcut": self.parser.format(signature),
                    "commands": [
                        command.command_id
                        for command in commands
                    ]
                })

                SpawnLogger.warning(
                    f"Shortcut conflict: {context} / "
                    f"{self.parser.format(signature)} / "
                    f"{', '.join(c.command_id for c in commands)}"
                )

    # --------------------------------------------------
    # CONTEXT DETECTION
    # --------------------------------------------------

    @staticmethod
    def _is_inside(root, focus):

        if root is None or focus is None:
            return False

        return root is focus or root.IsDescendant(focus)

    @staticmethod
    def _is_text_input(focus):
        return (
            focus is not None
            and isinstance(focus, _TEXT_INPUT_TYPES)
        )

    def get_active_context(self):

        focus = wx.Window.FindFocus()

        if focus is None:
            return "global"

        # Project Explorer
        project_panel = getattr(
            self.frame,
            "m_panel_splitter_ProjectTree",
            None
        )

        if self._is_inside(project_panel, focus):
            return "project_explorer"

        # Source Control
        git_panel = getattr(
            self.frame,
            "m_panel_Git",
            None
        )

        if self._is_inside(git_panel, focus):
            return "source_control"

        # Documentation
        documentation_panel = getattr(
            self.frame,
            "documentation_panel",
            None
        )

        if self._is_inside(documentation_panel, focus):
            return "documentation"

        # Editor
        notebook = getattr(
            self.frame,
            "m_auinotebook_Main",
            None
        )

        if notebook is not None:

            current_page = notebook.GetCurrentPage()

            if self._is_inside(current_page, focus):

                if self._is_text_input(focus):
                    return "global"

                return "editor"

        return "global"

    # --------------------------------------------------
    # COMMAND RESOLUTION
    # --------------------------------------------------

    def resolve(self, signature):
        context = self.get_active_context()

        contexts = []

        if context != "global":
            contexts.append(context)

        contexts.append("global")

        for candidate_context in contexts:

            commands = self._bindings.get(
                (candidate_context, signature),
                []
            )

            if not commands:
                continue

            available_commands = [
                command
                for command in commands
                if self.is_command_available(command)
            ]

            if len(available_commands) == 1:
                return available_commands[0]

            # Do not fall back to global when a local
            # shortcut exists but is unavailable or ambiguous.
            return None

        return None

    # --------------------------------------------------
    # DISPATCH
    # --------------------------------------------------

    def dispatch(self, command):
        if command.event_id is None:
            return False

        if not self.is_command_available(command):
            return False

        event = wx.CommandEvent(
            wx.EVT_MENU.typeId,
            command.event_id
        )

        event.SetEventObject(self.frame)

        processed = self.frame.ProcessEvent(event)

        if not processed:

            SpawnLogger.warning(
                f"No EVT_MENU handler found for shortcut command "
                f"{command.command_id} (ID: {command.event_id})"
            )

        return processed

    # --------------------------------------------------
    # KEY EVENT
    # --------------------------------------------------

    def on_char_hook(self, event):
        self.refresh_availability()
        signature = self.parser.from_event(event)

        if signature is None:
            event.Skip()
            return

        command = self.resolve(signature)

        if command is None:
            event.Skip()
            return

        if self.dispatch(command):
            return

        event.Skip()

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def get_conflicts(self):

        return list(self._conflicts)

    def get_effective_shortcut(self, command_id):

        command = self.command_registry.get(command_id)

        if command is None:
            return None

        return self.keybindings_manager.get_shortcut(
            command_id,
            command.default_shortcut
        )
