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
import wx.propgrid
import gettext

_ = gettext.gettext

from ui.keyboard_shortcuts_dialog import KeyboardShortcuts
from core.shortcuts.shortcut_parser import ShortcutParser


class ShortcutCaptureDialog(wx.Dialog):

    def __init__(self, parent, current_shortcut=None):

        super().__init__(
            parent,
            title=_(u"Assign Shortcut"),
            size=wx.Size(380, 160),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.parser = ShortcutParser()
        self.shortcut = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(
            self,
            wx.ID_ANY,
            _(u"Press the desired keyboard combination.")
        )

        sizer.Add(
            label,
            0,
            wx.ALL | wx.ALIGN_CENTER,
            12
        )

        self.capture_ctrl = wx.TextCtrl(
            self,
            wx.ID_ANY,
            current_shortcut or "",
            style=wx.TE_READONLY | wx.TE_CENTRE
        )

        sizer.Add(
            self.capture_ctrl,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT,
            15
        )

        sizer.AddSpacer(12)

        buttons = wx.BoxSizer(wx.HORIZONTAL)

        self.button_clear = wx.Button(
            self,
            wx.ID_ANY,
            _(u"Remove Shortcut")
        )

        self.button_cancel = wx.Button(
            self,
            wx.ID_CANCEL,
            _(u"Cancel")
        )

        buttons.Add(self.button_clear, 0, wx.ALL, 5)
        buttons.AddStretchSpacer()
        buttons.Add(self.button_cancel, 0, wx.ALL, 5)

        sizer.Add(
            buttons,
            0,
            wx.EXPAND | wx.ALL,
            5
        )

        self.SetSizer(sizer)
        self.Layout()
        self.Centre()

        self.capture_ctrl.Bind(
            wx.EVT_CHAR_HOOK,
            self.on_key_capture
        )

        self.button_clear.Bind(
            wx.EVT_BUTTON,
            self.on_clear
        )

        self.button_cancel.Bind(
            wx.EVT_BUTTON,
            self.on_cancel
        )

        wx.CallAfter(self.capture_ctrl.SetFocus)



    def on_key_capture(self, event):

        key_code = event.GetKeyCode()

        if key_code == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return

        modifiers_pressed = (
            event.ControlDown()
            or event.AltDown()
            or event.ShiftDown()
            or event.MetaDown()
        )

        if (
            key_code in (wx.WXK_BACK, wx.WXK_DELETE)
            and not modifiers_pressed
        ):
            self.shortcut = None
            self.EndModal(wx.ID_OK)
            return

        parsed = self.parser.from_event(event)

        if parsed is None:
            return

        self.shortcut = self.parser.format(parsed)

        self.EndModal(wx.ID_OK)

    def on_clear(self, event):

        self.shortcut = None
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):

        self.EndModal(wx.ID_CANCEL)


class KeyboardShortcutsDialog(KeyboardShortcuts):
    CATEGORY_ORDER = [
        "File",
        "Edit",
        "Selection",
        "View",
        "Project",
        "Project Explorer",
        "Build",
        "Server",
        "Source Control",
        "Tools",
        "Documentation",
        "Help"
    ]

    def __init__(
        self,
        parent,
        command_registry,
        keybindings_manager,
        shortcut_manager
    ):

        super().__init__(parent)

        self.command_registry = command_registry
        self.keybindings_manager = keybindings_manager
        self.shortcut_manager = shortcut_manager

        self.parser = ShortcutParser()

        self._selected_profile_id = (
            self.keybindings_manager.get_active_profile_id()
        )

        # Snapshot for Cancel / window close.
        self._snapshot = (
            self.keybindings_manager.get_data_copy()
        )

        self._setup_buttons()
        self._bind_events()

        self._refresh_profiles()
        self._populate_properties()

    def _update_profile_controls(self):
        is_default = self._selected_profile_id == "default"

        self.m_bpButtonRemove.Enable(not is_default)

    # --------------------------------------------------
    # INITIALIZATION
    # --------------------------------------------------

    def _setup_buttons(self):

        button_art = [
            (
                self.m_bpButtonImport,
                wx.ART_FILE_OPEN,
                _(u"Import Keymap")
            ),
            (
                self.m_bpButtonExport,
                wx.ART_FILE_SAVE_AS,
                _(u"Export Keymap")
            ),
            (
                self.m_bpButtonReset,
                wx.ART_UNDO,
                _(u"Reset Keymap")
            )
        ]

        for button, art_id, tooltip in button_art:


            button.SetToolTip(tooltip)

        self.m_bpButtonNew.SetToolTip(
            _(u"Create New Keymap")
        )

        self.m_bpButtonClone.SetToolTip(
            _(u"Duplicate Keymap")
        )

        self.m_bpButtonRemove.SetToolTip(
            _(u"Delete Keymap")
        )

    def _bind_events(self):

        self.m_choiceKeymaps.Bind(
            wx.EVT_CHOICE,
            self.on_profile_changed
        )

        self.m_bpButtonNew.Bind(
            wx.EVT_BUTTON,
            self.on_new_profile
        )

        self.m_bpButtonClone.Bind(
            wx.EVT_BUTTON,
            self.on_clone_profile
        )

        self.m_bpButtonRemove.Bind(
            wx.EVT_BUTTON,
            self.on_remove_profile
        )

        self.m_searchCtrl.Bind(
            wx.EVT_TEXT,
            self.on_search
        )

        self.m_propertyGridManager.Bind(
            wx.propgrid.EVT_PG_DOUBLE_CLICK,
            self.on_property_double_click
        )

        self.m_bpButtonImport.Bind(
            wx.EVT_BUTTON,
            self.on_import
        )

        self.m_bpButtonExport.Bind(
            wx.EVT_BUTTON,
            self.on_export
        )

        self.m_bpButtonReset.Bind(
            wx.EVT_BUTTON,
            self.on_reset_profile
        )

        self.m_buttonApply.Bind(
            wx.EVT_BUTTON,
            self.on_apply
        )

        self.m_buttonCancel.Bind(
            wx.EVT_BUTTON,
            self.on_cancel
        )

        self.Bind(
            wx.EVT_CLOSE,
            self.on_close
        )

    # --------------------------------------------------
    # PROFILES
    # --------------------------------------------------

    def _refresh_profiles(self):

        self.m_choiceKeymaps.Freeze()

        try:

            self.m_choiceKeymaps.Clear()

            selected_index = -1

            for profile in self.keybindings_manager.get_profiles():

                index = self.m_choiceKeymaps.Append(
                    profile["name"],
                    profile["id"]
                )

                if profile["id"] == self._selected_profile_id:
                    selected_index = index

            if selected_index < 0:
                self._selected_profile_id = "default"
                self.keybindings_manager.set_active_profile(
                    "default"
                )

                for index in range(self.m_choiceKeymaps.GetCount()):

                    if (
                        self.m_choiceKeymaps.GetClientData(index)
                        == "default"
                    ):
                        selected_index = index
                        break

            if selected_index >= 0:
                self.m_choiceKeymaps.SetSelection(selected_index)

        finally:
            self.m_choiceKeymaps.Thaw()

        self._update_profile_controls()

    def on_profile_changed(self, event):

        selection = self.m_choiceKeymaps.GetSelection()

        if selection == wx.NOT_FOUND:
            return

        profile_id = self.m_choiceKeymaps.GetClientData(
            selection
        )

        if not profile_id:
            return

        self._selected_profile_id = profile_id

        self.keybindings_manager.set_active_profile(
            profile_id
        )
        self._update_profile_controls()
        self._populate_properties()

    def on_new_profile(self, event):

        dialog = wx.TextEntryDialog(
            self,
            _(u"Enter a name for the new keymap:"),
            _(u"New Keymap")
        )

        try:

            if dialog.ShowModal() != wx.ID_OK:
                return

            name = dialog.GetValue().strip()

            if not name:
                return

            profile_id = self.keybindings_manager.create_profile(
                name
            )

            self.keybindings_manager.set_active_profile(
                profile_id
            )

            self._selected_profile_id = profile_id

            self._refresh_profiles()
            self._populate_properties()

        except Exception as exc:
            self._show_error(exc)

        finally:
            dialog.Destroy()

    def on_clone_profile(self, event):

        profile = self.keybindings_manager.get_profile(
            self._selected_profile_id
        )

        if profile is None:
            return

        dialog = wx.TextEntryDialog(
            self,
            _(u"Enter a name for the duplicated keymap:"),
            _(u"Duplicate Keymap"),
            profile["name"] + " Copy"
        )

        try:

            if dialog.ShowModal() != wx.ID_OK:
                return

            name = dialog.GetValue().strip()

            if not name:
                return

            profile_id = self.keybindings_manager.create_profile(
                name,
                clone_from=self._selected_profile_id
            )

            self.keybindings_manager.set_active_profile(
                profile_id
            )

            self._selected_profile_id = profile_id

            self._refresh_profiles()
            self._populate_properties()

        except Exception as exc:
            self._show_error(exc)

        finally:
            dialog.Destroy()

    def on_remove_profile(self, event):

        if self._selected_profile_id == "default":
            return

        profile = self.keybindings_manager.get_profile(
            self._selected_profile_id
        )

        if profile is None:
            return

        result = wx.MessageBox(
            _(u"Delete keymap '%s'?") % profile["name"],
            _(u"Delete Keymap"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            self
        )

        if result != wx.YES:
            return

        try:

            self.keybindings_manager.delete_profile(
                self._selected_profile_id
            )

            self._selected_profile_id = (
                self.keybindings_manager.get_active_profile_id()
            )

            self._refresh_profiles()
            self._populate_properties()

        except Exception as exc:
            self._show_error(exc)

    # --------------------------------------------------
    # PROPERTY GRID
    # --------------------------------------------------

    def _get_display_shortcut(self, command):

        profile = self.keybindings_manager.get_profile(
            self._selected_profile_id
        )

        if profile is None:
            return _(u"Not assigned")

        bindings = profile["bindings"]

        if command.command_id in bindings:

            shortcut = bindings[command.command_id]

            if shortcut is None:
                return _(u"Not assigned")

        else:
            shortcut = command.default_shortcut

        if shortcut is None:
            return _(u"Not assigned")

        try:
            return self.parser.format(
                self.parser.parse(shortcut)
            )

        except ValueError:
            return shortcut

    def _populate_properties(self):

        query = self.m_searchCtrl.GetValue().strip().lower()

        grid = self.m_propertyGridManager

        grid.Freeze()

        try:

            grid.ClearPage(0)

            page = grid.GetPage(0)

            groups = {}

            for command in self.command_registry.all():

                searchable = " ".join([
                    command.label,
                    command.command_id,
                    command.category,
                    command.context
                ]).lower()

                if query and query not in searchable:
                    continue

                groups.setdefault(
                    command.category,
                    []
                ).append(command)

            ordered_categories = [
                category
                for category in self.CATEGORY_ORDER
                if category in groups
            ]

            ordered_categories.extend(
                category
                for category in groups
                if category not in ordered_categories
            )

            for category in ordered_categories:

                page.Append(
                    wx.propgrid.PropertyCategory(category)
                )

                commands = sorted(
                    groups[category],
                    key=lambda item: item.label.lower()
                )

                for command in commands:

                    prop = page.Append(
                        wx.propgrid.StringProperty(
                            command.label,
                            command.command_id,
                            self._get_display_shortcut(command)
                        )
                    )

                    grid.SetPropertyReadOnly(prop, True)

                    grid.SetPropertyHelpString(
                        prop,
                        f"{command.command_id} | {command.context}"
                    )

            grid.Refresh()

        finally:
            grid.Thaw()

    def on_search(self, event):

        self._populate_properties()

    # --------------------------------------------------
    # SHORTCUT ASSIGNMENT
    # --------------------------------------------------

    def _find_conflicts(self, command, shortcut):

        if shortcut is None:
            return []

        signature = self.parser.parse(shortcut)

        conflicts = []

        for other in self.command_registry.all():

            if other.command_id == command.command_id:
                continue

            if other.context != command.context:
                continue

            other_shortcut = self.keybindings_manager.get_shortcut(
                other.command_id,
                other.default_shortcut,
                profile_id=self._selected_profile_id
            )

            if other_shortcut is None:
                continue

            try:
                other_signature = self.parser.parse(
                    other_shortcut
                )
            except ValueError:
                continue

            if signature == other_signature:
                conflicts.append(other)

        return conflicts

    def on_property_double_click(self, event):

        prop = event.GetProperty()

        if prop is None:
            return

        command_id = prop.GetName()

        command = self.command_registry.get(command_id)

        if command is None:
            return

        current = self._get_display_shortcut(command)

        dialog = ShortcutCaptureDialog(
            self,
            current if current not in (
                _(u"Not assigned"),
                _(u"Not assigned")
            ) else None
        )

        try:

            if dialog.ShowModal() != wx.ID_OK:
                return

            shortcut = dialog.shortcut

            if shortcut is not None:

                conflicts = self._find_conflicts(
                    command,
                    shortcut
                )

                if conflicts:

                    conflict_names = "\n".join(
                        f"{item.label} ({item.command_id})"
                        for item in conflicts
                    )

                    wx.MessageBox(
                        _(u"The shortcut is already assigned to:\n\n%s")
                        % conflict_names,
                        _(u"Shortcut Conflict"),
                        wx.OK | wx.ICON_WARNING,
                        self
                    )

                    return

            # Remove the override if the user selected the default.
            if (
                shortcut is not None
                and command.default_shortcut is not None
                and self.parser.parse(shortcut)
                == self.parser.parse(command.default_shortcut)
            ):

                self.keybindings_manager.reset_binding(
                    command_id,
                    self._selected_profile_id
                )

            else:

                self.keybindings_manager.set_binding(
                    command_id,
                    shortcut,
                    self._selected_profile_id
                )

            self._populate_properties()

        except Exception as exc:
            self._show_error(exc)

        finally:
            dialog.Destroy()

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    def on_reset_profile(self, event):

        profile = self.keybindings_manager.get_profile(
            self._selected_profile_id
        )

        if profile is None:
            return

        result = wx.MessageBox(
            _(u"Reset all shortcuts in '%s' to their defaults?")
            % profile["name"],
            _(u"Reset Keymap"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            self
        )

        if result != wx.YES:
            return

        self.keybindings_manager.reset_profile(
            self._selected_profile_id
        )

        self._populate_properties()

    # --------------------------------------------------
    # IMPORT / EXPORT
    # --------------------------------------------------

    def on_import(self, event):

        dialog = wx.FileDialog(
            self,
            _(u"Import Keymap"),
            wildcard=(
                "YAML files (*.yaml;*.yml)|*.yaml;*.yml|"
                "All files (*.*)|*.*"
            ),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        try:

            if dialog.ShowModal() != wx.ID_OK:
                return

            profile_id = self.keybindings_manager.import_profile(
                dialog.GetPath()
            )

            self._selected_profile_id = profile_id

            self.keybindings_manager.set_active_profile(
                profile_id
            )

            self._refresh_profiles()
            self._populate_properties()

        except Exception as exc:
            self._show_error(exc)

        finally:
            dialog.Destroy()

    def on_export(self, event):

        profile = self.keybindings_manager.get_profile(
            self._selected_profile_id
        )

        if profile is None:
            return

        filename = (
            self._selected_profile_id + ".yaml"
        )

        dialog = wx.FileDialog(
            self,
            _(u"Export Keymap"),
            defaultFile=filename,
            wildcard=(
                "YAML files (*.yaml)|*.yaml|"
                "All files (*.*)|*.*"
            ),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )

        try:

            if dialog.ShowModal() != wx.ID_OK:
                return

            self.keybindings_manager.export_profile(
                self._selected_profile_id,
                dialog.GetPath()
            )

        except Exception as exc:
            self._show_error(exc)

        finally:
            dialog.Destroy()

    # --------------------------------------------------
    # APPLY / CANCEL
    # --------------------------------------------------

    def on_apply(self, event):

        try:
            self.keybindings_manager.save()
            self.shortcut_manager.rebuild()

            parent = self.GetParent()
            if hasattr(parent, "update_shortcut_menu_labels"):
                parent.update_shortcut_menu_labels()

            # New rollback point after successful Apply.
            self._snapshot = (
                self.keybindings_manager.get_data_copy()
            )

            result = wx.MessageBox(
                _(u"Saved successfully"),
                _(u"Keyboard Shortcuts"),
                wx.OK | wx.ICON_INFORMATION,
                self
            )

        except Exception as exc:
            self._show_error(exc)

    def on_cancel(self, event):
        self.keybindings_manager.restore_data(
            self._snapshot
        )

        self.EndModal(wx.ID_CANCEL)

    def on_close(self, event):
        self.keybindings_manager.restore_data(
            self._snapshot
        )

        event.Skip()

    # --------------------------------------------------
    # ERRORS
    # --------------------------------------------------

    def _show_error(self, error):
        wx.MessageBox(
            str(error),
            _(u"Keyboard Shortcuts"),
            wx.OK | wx.ICON_ERROR,
            self
        )
