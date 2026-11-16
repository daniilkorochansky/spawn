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

wxEVT_SPLIT_CHOICE_SELECT = wx.NewEventType()
EVT_SPLIT_CHOICE_SELECT = wx.PyEventBinder(wxEVT_SPLIT_CHOICE_SELECT, 1)

wxEVT_SPLIT_CHOICE_ACTION = wx.NewEventType()
EVT_SPLIT_CHOICE_ACTION = wx.PyEventBinder(wxEVT_SPLIT_CHOICE_ACTION, 1)

class SplitActionChoice(wx.Control):
    """DPI-aware split choice: left side selects, right side raises an action event."""

    def __init__(
        self, parent, id=wx.ID_ANY, choices=None, bitmap=None,
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.BORDER_NONE,
        validator=wx.DefaultValidator, name="SplitActionChoice"
    ):
        super().__init__(parent, id, pos, size, style, validator, name)

        self._choices = [str(x) for x in choices] if choices else []
        self._selection = 0 if self._choices else wx.NOT_FOUND
        self._source_bitmap = bitmap if bitmap and bitmap.IsOk() else None
        self._bitmap = wx.NullBitmap

        self._action_zone_width = self._dip(32)
        self._hovered = False
        self._hover_action = False
        self._pressed = False
        self._pressed_action = False
        self._captured = False
        self._use_parent_background = True
        self._action_tooltip = ""
        self._selection_tooltip = ""

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._refresh_bitmap()
        self.SetInitialSize(size)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._on_capture_lost)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

        dpi_event = getattr(wx, "EVT_DPI_CHANGED", None)
        if dpi_event is not None:
            self.Bind(dpi_event, self._on_dpi_changed)

    # DPI -----------------------------------------------------------------

    def _dip(self, value):
        try:
            return self.FromDIP(value)
        except (AttributeError, TypeError):
            return value

    def _refresh_bitmap(self):
        if self._source_bitmap is None:
            self._bitmap = self._make_play_bitmap()
            return

        image = self._source_bitmap.ConvertToImage()
        if not image.IsOk():
            self._bitmap = self._source_bitmap
            return

        side = max(1, self._dip(16))
        if image.GetWidth() != side or image.GetHeight() != side:
            image = image.Scale(side, side, wx.IMAGE_QUALITY_HIGH)
        self._bitmap = wx.Bitmap(image)

    def _on_dpi_changed(self, event):
        self._refresh_bitmap()
        self._action_zone_width = self._calc_action_width()
        self.InvalidateBestSize()
        self.Refresh()
        event.Skip()

    def _calc_action_width(self):
        icon_width = self._bitmap.GetWidth() if self._bitmap.IsOk() else self._dip(16)
        return max(self._dip(32), icon_width + self._dip(16))

    def _on_size(self, event):
        self.Refresh()
        event.Skip()

    def DoGetBestSize(self):
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        max_text = self._dip(80)
        for label in self._choices:
            tw, _ = dc.GetTextExtent(label)
            max_text = max(max_text, tw)
        action_width = self._calc_action_width()
        self._action_zone_width = action_width
        return wx.Size(
            max_text + action_width + self._dip(24),
            max(self._dip(28), dc.GetCharHeight() + self._dip(12))
        )

    # Appearance/background ----------------------------------------------

    def SetBackgroundColour(self, colour):
        self._use_parent_background = False
        result = super().SetBackgroundColour(colour)
        self.Refresh()
        return result

    def UseParentBackground(self, use=True):
        self._use_parent_background = bool(use)
        self.Refresh()
        return True

    def _paint_background(self):
        if self._use_parent_background and self.GetParent():
            return self.GetParent().GetBackgroundColour()
        return self.GetBackgroundColour()

    def _on_erase_background(self, event):
        # The buffered paint handler clears the entire client area.
        pass

    def Enable(self, enable=True):
        result = super().Enable(enable)
        self.Refresh()
        return result

    def SetFont(self, font):
        result = super().SetFont(font)
        if hasattr(self, "_choices"):
            self.InvalidateBestSize()
            self.Refresh()
        return result

    def SetForegroundColour(self, colour):
        result = super().SetForegroundColour(colour)
        self.Refresh()
        return result

    def _make_play_bitmap(self):
        side = max(1, self._dip(14))
        bmp = wx.Bitmap(side, side, 32)
        bmp.UseAlpha()
        bmp.Clear()
        dc = wx.MemoryDC(bmp)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            green = wx.Colour(28, 166, 36)
            gc.SetBrush(wx.Brush(green))
            gc.SetPen(wx.Pen(green, 1))
            path = gc.CreatePath()
            path.MoveToPoint(side * .22, side * .10)
            path.AddLineToPoint(side * .90, side * .50)
            path.AddLineToPoint(side * .22, side * .90)
            path.CloseSubpath()
            gc.FillPath(path)
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def SetBitmap(self, bitmap=None):
        """
        Set or remove the action icon dynamically.

        Pass a valid wx.Bitmap to change the icon.
        Pass None or wx.NullBitmap to restore the default play icon.
        """
        if bitmap is None or not bitmap.IsOk():
            self._source_bitmap = None
        else:
            self._source_bitmap = bitmap

        self._refresh_bitmap()
        self._action_zone_width = self._calc_action_width()

        self.InvalidateBestSize()
        self.Layout()
        self.Refresh()

        return True

    def GetBitmap(self):
        return self._bitmap

    def SetActionToolTip(self, text):
        self._action_tooltip = str(text or "")

    def SetSelectionToolTip(self, text):
        self._selection_tooltip = str(text or "")

    # Choice-like API -----------------------------------------------------

    def Append(self, item):
        self._choices.append(str(item))
        if self._selection == wx.NOT_FOUND:
            self._selection = 0
        self.InvalidateBestSize()
        self.Refresh()
        return len(self._choices) - 1

    def AppendItems(self, items):
        if items:
            self._choices.extend(str(x) for x in items)
            if self._selection == wx.NOT_FOUND:
                self._selection = 0
            self.InvalidateBestSize()
            self.Refresh()

    def Insert(self, item, pos):
        pos = max(0, min(int(pos), len(self._choices)))
        self._choices.insert(pos, str(item))
        if self._selection == wx.NOT_FOUND:
            self._selection = 0
        elif pos <= self._selection:
            self._selection += 1
        self.InvalidateBestSize()
        self.Refresh()
        return pos

    def Delete(self, index):
        if not 0 <= index < len(self._choices):
            return
        del self._choices[index]
        if not self._choices:
            self._selection = wx.NOT_FOUND
        elif index < self._selection:
            self._selection -= 1
        elif index == self._selection:
            self._selection = min(index, len(self._choices) - 1)
        self.InvalidateBestSize()
        self.Refresh()

    def Clear(self):
        self._choices.clear()
        self._selection = wx.NOT_FOUND
        self.InvalidateBestSize()
        self.Refresh()

    def SetItems(self, choices, preserve_selection=True):
        previous = self.GetStringSelection()
        self._choices = [str(x) for x in choices] if choices else []
        if preserve_selection and previous in self._choices:
            self._selection = self._choices.index(previous)
        else:
            self._selection = 0 if self._choices else wx.NOT_FOUND
        self.InvalidateBestSize()
        self.Refresh()

    def GetItems(self):
        return list(self._choices)

    def GetCount(self):
        return len(self._choices)

    def IsEmpty(self):
        return not self._choices

    def GetString(self, index):
        return self._choices[index] if 0 <= index < len(self._choices) else ""

    def SetString(self, index, string):
        if 0 <= index < len(self._choices):
            self._choices[index] = str(string)
            self.InvalidateBestSize()
            self.Refresh()

    def FindString(self, string, caseSensitive=False):
        target = str(string)
        if caseSensitive:
            try:
                return self._choices.index(target)
            except ValueError:
                return wx.NOT_FOUND
        target = target.casefold()
        for index, value in enumerate(self._choices):
            if value.casefold() == target:
                return index
        return wx.NOT_FOUND

    def GetSelection(self):
        return self._selection

    def SetSelection(self, index):
        if 0 <= index < len(self._choices) or index == wx.NOT_FOUND:
            self._selection = index
            self.Refresh()

    def GetStringSelection(self):
        return self.GetString(self._selection)

    def SetStringSelection(self, string):
        index = self.FindString(string, caseSensitive=True)
        if index == wx.NOT_FOUND:
            return False
        self.SetSelection(index)
        return True

    # Events and popup ----------------------------------------------------

    def _emit(self, event_type):
        event = wx.CommandEvent(event_type, self.GetId())
        event.SetEventObject(self)
        event.SetInt(self._selection)
        event.SetString(self.GetStringSelection())
        self.GetEventHandler().ProcessEvent(event)

    def _show_popup(self):
        if not self._choices or not self.IsEnabled():
            return

        menu = wx.Menu()
        item_ids = []
        for index, label in enumerate(self._choices):
            item = menu.AppendRadioItem(wx.ID_ANY, label)
            item.Check(index == self._selection)
            item_ids.append(item.GetId())

        def on_menu(event):
            try:
                index = item_ids.index(event.GetId())
            except ValueError:
                return
            if index != self._selection:
                self._selection = index
                self.Refresh()
                self._emit(wxEVT_SPLIT_CHOICE_SELECT)

        menu.Bind(wx.EVT_MENU, on_menu)
        self.PopupMenu(menu, 0, self.GetClientSize().height)
        menu.Destroy()

    def _on_motion(self, event):
        if not self.IsEnabled():
            return
        in_action = event.GetX() >= self.GetClientSize().width - self._action_zone_width
        if not self._hovered or in_action != self._hover_action:
            self._hovered = True
            self._hover_action = in_action
            self._update_tooltip()
            self.Refresh()
        event.Skip()

    def _update_tooltip(self):
        tip = (
            self._action_tooltip if self._hover_action and self._action_tooltip
            else self._selection_tooltip
        )
        if tip:
            self.SetToolTip(tip)

    def _on_leave(self, event):
        self._hovered = False
        self._hover_action = False
        if not self._captured:
            self._pressed = False
            self._pressed_action = False
        self.Refresh()
        event.Skip()

    def _on_left_down(self, event):
        if not self.IsEnabled():
            return
        self.SetFocus()
        self._pressed = True
        self._pressed_action = (
            event.GetX() >= self.GetClientSize().width - self._action_zone_width
        )
        if not self._captured:
            self.CaptureMouse()
            self._captured = self.HasCapture()
        self.Refresh()

    def _on_left_up(self, event):
        if not self._pressed:
            return

        was_action = self._pressed_action
        width, height = self.GetClientSize()
        x, y = event.GetX(), event.GetY()
        inside = 0 <= x < width and 0 <= y < height
        is_action = x >= width - self._action_zone_width

        self._pressed = False
        self._pressed_action = False
        if self._captured and self.HasCapture():
            self.ReleaseMouse()
        self._captured = False

        self._hovered = inside
        self._hover_action = inside and is_action
        self.Refresh()

        if not inside:
            return
        if was_action and is_action:
            self._emit(wxEVT_SPLIT_CHOICE_ACTION)
        elif not was_action and not is_action:
            self._show_popup()

    def _on_capture_lost(self, event):
        self._captured = False
        self._pressed = False
        self._pressed_action = False
        self.Refresh()
        event.Skip()

    def _on_key_down(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            if self.IsEnabled():
                self._emit(wxEVT_SPLIT_CHOICE_ACTION)
            return
        if key == wx.WXK_F4 or (key == wx.WXK_DOWN and event.AltDown()):
            self._show_popup()
            return
        event.Skip()

    # Painting ------------------------------------------------------------

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        width, height = self.GetClientSize()

        dc.SetBackground(wx.Brush(self._paint_background()))
        dc.Clear()

        flags = 0
        if not self.IsEnabled():
            flags |= wx.CONTROL_DISABLED
        elif self._pressed:
            flags |= wx.CONTROL_PRESSED
        elif self._hovered:
            flags |= wx.CONTROL_CURRENT

        wx.RendererNative.Get().DrawPushButton(
            self, dc, wx.Rect(0, 0, width, height), flags
        )

        split_x = width - self._action_zone_width
        if 0 < split_x < width:
            dc.SetPen(wx.Pen(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW),
                max(1, self._dip(1))
            ))
            dc.DrawLine(
                split_x, self._dip(6),
                split_x, max(self._dip(6), height - self._dip(6))
            )

        if self.IsEnabled():
            text_colour = self.GetForegroundColour()
            if not text_colour.IsOk():
                text_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        else:
            text_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        dc.SetFont(self.GetFont())
        dc.SetTextForeground(text_colour)
        text_rect = wx.Rect(
            self._dip(10), 0,
            max(0, width - self._action_zone_width - self._dip(18)),
            height
        )
        dc.DrawLabel(
            self.GetStringSelection(),
            text_rect,
            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
        )

        if self._bitmap.IsOk():
            bitmap = self._bitmap if self.IsEnabled() else self._bitmap.ConvertToDisabled()
            iw, ih = bitmap.GetSize()
            ix = split_x + (self._action_zone_width - iw) // 2
            iy = (height - ih) // 2
            if self._pressed and self._pressed_action:
                ix += self._dip(1)
                iy += self._dip(1)
            dc.DrawBitmap(bitmap, ix, iy, True)

