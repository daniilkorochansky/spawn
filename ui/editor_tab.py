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
import re

import wx.stc as stc
import wx

import ui.spawn_base as gui

from core.config_manager import ConfigManager
from core.logger import SpawnLogger
from core.platform_utils import PlatformUtils

import gettext
_ = gettext.gettext

class CustomEditorTab(gui.EditorTabPanel):
    def __init__(self, parent, file_path=""):
        super().__init__(parent)

        self.m_scintilla_Editor.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.on_savepoint_left)
        self.m_scintilla_Editor.Bind(stc.EVT_STC_SAVEPOINTREACHED, self.on_savepoint_reached)
        self.m_scintilla_Editor.Bind(stc.EVT_STC_UPDATEUI, self.on_editor_update_ui)
        self.m_scintilla_Editor.Bind( wx.EVT_RIGHT_DOWN, self.m_scintilla_EditorOnContextMenu)
        self.m_scintilla_Editor.Bind(stc.EVT_STC_MARGINCLICK, self.on_editor_margin_click)
        self.m_scintilla_Editor.Bind(stc.EVT_STC_ZOOM, self.on_zoom_changed)

        self.COLOR_PREVIEW_INDICATOR_ID = 16

        self.ide_cfg = ConfigManager()

        self.base_win = wx.GetTopLevelParent(self)

        self.file_path = file_path
        self.is_untitled = (file_path == "")
        self.current_encoding = ""
        self.native_eol = "LF"

        doc_pointer = self.m_scintilla_Editor.GetDocPointer()
        self.m_scintilla_Minimap.SetDocPointer(doc_pointer)

        self.modified_markers_handles = []
        self.saved_markers_handles = []
        self.MARKER_MODIFIED_ID = 13
        self.MARKER_SAVED_ID = 14

        self.MARKER_GIT_MODIFIED_ID = 12
        
        self.m_scintilla_Editor.Bind(stc.EVT_STC_MODIFIED, self.on_editor_modified_tracker)

        if wx.Platform == '__WXMSW__':
            try:
                self.m_scintilla_Editor.SetTechnology(stc.STC_TECHNOLOGY_DIRECTWRITE)
            except:
                SpawnLogger.error(f"Editor Set Technology: {e}")

        #Initialize Editor Settings
        self.color_preview = True
        self.brace_matching = True
        self.show_change_history = True
        #--------------------------
        self.update_zoom_status()
        
        if self.file_path:
            self.load_file(self.file_path)
            self.apply_lexer_by_extension()
        else:
            self.set_plain_text_mode()

    def on_zoom_changed(self, event):
        self.update_zoom_status()
        event.Skip()

    def update_zoom_status(self):
        zoom = self.m_scintilla_Editor.GetZoom()
        zoom_percentage = 100 + (zoom * 10)
        self.base_win.m_statusBar.SetStatusText(str(zoom_percentage) + "%", 1)

    def on_editor_modified_tracker(self, event):
        if self.show_change_history and not self.is_untitled:
            editor = self.m_scintilla_Editor
            mod_type = event.GetModificationType()

            if editor.IsFrozen():
                event.Skip()
                return
            if mod_type & stc.STC_MOD_INSERTTEXT:
                #If text was inserted, then we set line change markers, and erase Diff markers if there were any
                pos = event.GetPosition()
                length = event.GetLength()
                start_line = editor.LineFromPosition(pos)
                end_line = editor.LineFromPosition(pos + length)

                if end_line >= editor.GetLineCount():
                    end_line = editor.GetLineCount() - 1

                for current_line in range(start_line, end_line + 1):
                    if current_line < editor.GetLineCount():
                        new_paste_marker = editor.MarkerAdd(current_line, self.MARKER_MODIFIED_ID)
                        self.modified_markers_handles.append(new_paste_marker)
                        editor.MarkerDelete(current_line, self.MARKER_GIT_MODIFIED_ID)
                #------------------------------------------------------------------------------------------------
            
            if mod_type & (stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT):

                modified_target_line = editor.LineFromPosition(event.GetPosition())
                git_marker_modified_mask = editor.MarkerGet(modified_target_line)
                has_git_modified_marker = bool(git_marker_modified_mask & (1 << self.MARKER_GIT_MODIFIED_ID))

                if has_git_modified_marker:
                    editor.MarkerDelete(modified_target_line, self.MARKER_GIT_MODIFIED_ID)
                
                current_pos = event.GetPosition()
                line_idx = editor.LineFromPosition(current_pos)
                if 0 <= line_idx < editor.GetLineCount():
                    def mark_line_as_modified(target_line):
                        if 0 <= target_line < editor.GetLineCount():
                            if not (editor.MarkerGet(target_line) & (1 << self.MARKER_MODIFIED_ID)):
                                for h in list(self.saved_markers_handles):
                                    if editor.MarkerLineFromHandle(h) == target_line:
                                        editor.MarkerDeleteHandle(h)
                                        self.saved_markers_handles.remove(h)
                                        break
                                
                                new_handle = editor.MarkerAdd(target_line, self.MARKER_MODIFIED_ID)
                                self.modified_markers_handles.append(new_handle)

         
                    inserted_text = event.GetText() if hasattr(event, 'GetText') else ""
                    if mod_type & stc.STC_MOD_INSERTTEXT and ("\n" in inserted_text or "\r" in inserted_text):
                        line_start_pos = editor.PositionFromLine(line_idx)
                        if current_pos == line_start_pos:
                            mark_line_as_modified(line_idx)
                        else:
                            mark_line_as_modified(line_idx)
                            mark_line_as_modified(line_idx + 1)
                    else:
                        mark_line_as_modified(line_idx)

        event.Skip()
            

    def convert_modified_markers_to_saved(self):
        editor = self.m_scintilla_Editor 
        editor.Freeze()
        try:
            for h in list(self.modified_markers_handles):
                line_idx = editor.MarkerLineFromHandle(h)
                if line_idx != -1:
                    editor.MarkerDeleteHandle(h)
                    new_saved_handle = editor.MarkerAdd(line_idx, self.MARKER_SAVED_ID)
                    self.saved_markers_handles.append(new_saved_handle)
            self.modified_markers_handles.clear()
        except Exception as e:
            SpawnLogger.error(f"Convert Modified Markers: {e}")
            
        finally:
            editor.Thaw()
            editor.Refresh()

    def convert_hex_to_html(self, hex_str):
        hex_pure = hex_str[2:]
        if len(hex_pure) >= 2:
            return f"#{hex_pure[:6].upper()}"
        return None

    def on_editor_margin_click(self, event):
        if event.GetMargin() == 2:
            editor = self.m_scintilla_Editor

            click_pos = event.GetPosition()
            line_clicked = editor.LineFromPosition(click_pos)

            if editor.GetFoldLevel(line_clicked) & stc.STC_FOLDLEVELHEADERFLAG:
                editor.ToggleFold(line_clicked)
        event.Skip()

    def m_scintilla_EditorOnContextMenu( self, event ):
        wx.ID_EDITOR_UNDO = 7001
        wx.ID_EDITOR_REDO = 7002
        wx.ID_EDITOR_CUT = 7003
        wx.ID_EDITOR_COPY = 7004
        wx.ID_EDITOR_PASTE = 7005
        wx.ID_EDITOR_GO_TO_DEFINITION = 7007
        wx.ID_EDITOR_PICK_COLOR = 7008
        wx.ID_EDITOR_LAST_COLOR = 7009
        wx.ID_EDITOR_COLORIZE_SELECTION = 7010
        wx.ID_EDITOR_SELECT_ALL = 7011

        self.m_menuEditor = wx.Menu()
        self.m_menuItem_Editor_Undo = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_UNDO, _(u"Undo"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_Undo )
        self.m_menuItem_Editor_Redo = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_REDO, _(u"Redo"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_Redo )
        self.m_menuEditor.AppendSeparator()
        self.m_menuItem_Editor_Cut = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_CUT, _(u"Cut"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_Cut )
        self.m_menuItem_Editor_Copy = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_COPY, _(u"Copy"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_Copy )
      
        
        self.m_menuItem_Editor_Paste = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_PASTE, _(u"Paste"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_Paste )
        self.m_menuEditor.AppendSeparator()
        self.m_menuItem_Editor_SelectAll = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_SELECT_ALL, _(u"Select All"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_SelectAll )
        self.m_menuEditor.AppendSeparator()
        #self.m_menuItem_Editor_GoToDefinition = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_GO_TO_DEFINITION, _(u"Go to Definition")+ u"\t" + u"F12", wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_menuEditor.Append( self.m_menuItem_Editor_GoToDefinition )
        self.m_menuItem_Editor_ColorizeSelection = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_COLORIZE_SELECTION, _(u"Colorize Selected Text..."), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_ColorizeSelection )
        self.m_menuEditor.AppendSeparator()
        self.m_menuItem_Editor_PickColor = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_PICK_COLOR, _(u"Paste Color from Palette..."), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_PickColor )
        
        last_color = getattr(self.base_win, "last_picked_hex_color", "0xFFFFFFFF")

        self.m_menuItem_Editor_LastColor = wx.MenuItem( self.m_menuEditor, wx.ID_EDITOR_LAST_COLOR, _(u"Paste Last Color ({last_color})").format(last_color=last_color), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuEditor.Append( self.m_menuItem_Editor_LastColor )

        start, end = self.m_scintilla_Editor.GetSelection()
        if start == end:
            self.m_menuEditor.Enable(wx.ID_EDITOR_COLORIZE_SELECTION, False)

        if not getattr(self.base_win, "last_picked_hex_color", None):
            self.m_menuEditor.Enable(wx.ID_EDITOR_LAST_COLOR, False)

        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_pick_color_menu_click, id=wx.ID_EDITOR_PICK_COLOR)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_paste_last_color_menu_click, id=wx.ID_EDITOR_LAST_COLOR)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_colorize_selection_click, id=wx.ID_EDITOR_COLORIZE_SELECTION)

        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_undo_click, id=wx.ID_EDITOR_UNDO)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_redo_click, id=wx.ID_EDITOR_REDO)
        
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_cut_click, id=wx.ID_EDITOR_CUT)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_copy_click, id=wx.ID_EDITOR_COPY)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_paste_click, id=wx.ID_EDITOR_PASTE)
        self.m_scintilla_Editor.Bind(wx.EVT_MENU, self.on_editor_select_all_click, id=wx.ID_EDITOR_SELECT_ALL)

        self.m_scintilla_Editor.PopupMenu( self.m_menuEditor, event.GetPosition() )
        self.m_menuEditor.Destroy()

    def on_editor_cut_click(self, event):
        self.m_scintilla_Editor.Cut()

    def on_editor_copy_click(self, event):
        self.m_scintilla_Editor.Copy()

    def on_editor_paste_click(self, event):
        if wx.TheClipboard.Open():
            try:
                text_data = wx.TextDataObject()

                if wx.TheClipboard.GetData(text_data):
                    self.m_scintilla_Editor.ReplaceSelection(text_data.GetText())

            except Exception as e:
                SpawnLogger.error(f"Paste: {e}")

            finally:
                wx.TheClipboard.Close()
                
    def on_editor_select_all_click(self, event):
        self.m_scintilla_Editor.SelectAll()

    def on_editor_undo_click(self, event):
        self.m_scintilla_Editor.Undo()

    def on_editor_redo_click(self, event):
        self.m_scintilla_Editor.Redo()

    def on_colorize_selection_click(self, event):
        editor = self.m_scintilla_Editor
        
        start, end = editor.GetSelection()
        if start == end:
            return

        selected_text = editor.GetSelectedText()
        color_data = wx.ColourData()
        color_data.SetChooseFull(True)

        with wx.ColourDialog(self, color_data) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                selected_color = dialog.GetColourData().GetColour()
                r = selected_color.Red()
                g = selected_color.Green()
                b = selected_color.Blue()

                tag_color = f"{{{r:02X}{g:02X}{b:02X}}}"
                
                if self.base_win:
                    self.base_win.last_picked_hex_color = f"0x{r:02X}{g:02X}{b:02X}FF"

                colorized_result = f"{tag_color}{selected_text}"
                editor.ReplaceSelection(colorized_result)
                editor.SetFocus()


    def on_pick_color_menu_click(self, event):
        editor = self.m_scintilla_Editor

        color_data = wx.ColourData()
        color_data.SetChooseFull(True)

        with wx.ColourDialog(self, color_data) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                selected_color = dialog.GetColourData().GetColour()

                r = selected_color.Red()
                g = selected_color.Green()
                b = selected_color.Blue()

                hex_color = f"0x{r:02X}{g:02X}{b:02X}FF"

                if self.base_win:
                    self.base_win.last_picked_hex_color = hex_color
                editor.ReplaceSelection(hex_color)

    def on_paste_last_color_menu_click(self, event):
        
        last_color = getattr(self.base_win, "last_picked_hex_color", "0xFFFFFFFF")
        self.m_scintilla_Editor.ReplaceSelection(last_color)

    def on_editor_update_ui(self, event):
        editor = self.m_scintilla_Editor

        pos = editor.GetCurrentPos()
        line = editor.LineFromPosition(pos) + 1
        col = editor.GetColumn(pos) + 1
        self.base_win.m_statusBar.SetStatusText(u"{strline} {line}, {cl} {col}".format(strline=_(u"Ln"),line=line, cl=_(u"Col"), col=col), 3)

        #Brace Matching
        if self.brace_matching:
            brace_at_caret = -1
            brace_opposite = -1
            char_after = editor.GetCharAt(pos)
            char_before = pos > 0 and editor.GetCharAt(pos - 1) or 0
            valid_braces = [ord('('), ord(')'), ord('['), ord(']'), ord('{'), ord('}')]

            if char_after in valid_braces:
                brace_at_caret = pos
            elif char_before in valid_braces:
                brace_at_caret = pos - 1

            if brace_at_caret != -1:
                brace_opposite = editor.BraceMatch(brace_at_caret)
                if brace_opposite != -1:
                    editor.BraceHighlight(brace_at_caret, brace_opposite)
                else:
                    editor.BraceBadLight(brace_at_caret)
            else:
                editor.BraceHighlight(-1, -1)
        #--------------

        total_chars = editor.GetTextLength()
        editor.SetIndicatorCurrent(self.COLOR_PREVIEW_INDICATOR_ID)
        editor.IndicatorClearRange(0, total_chars)

        current_pos = editor.GetCurrentPos()

        line_num = editor.LineFromPosition(current_pos)
        line_text = editor.GetLine(line_num)
        line_start_pos = editor.PositionFromLine(line_num)
        pos_in_line = current_pos - line_start_pos
        if self.color_preview:
            detected_html_color = None
            highlight_start = 0
            highlight_length = 0
            line_bytes = editor.GetLineRaw(line_num)
            for m in re.finditer(rb"0x([0-9A-Fa-f]{6,8})", line_bytes):
                start_idx, end_idx = m.start(), m.end()
                if start_idx <= pos_in_line <= end_idx:
                    hex_content = m.group(1).decode('utf-8')
                    detected_html_color = f"#{hex_content[:6].upper()}"
                    highlight_start = line_start_pos + start_idx
                    highlight_length = end_idx - start_idx
                    break

            if not detected_html_color:
                
                for m in re.finditer(rb"\{([0-9A-Fa-f]{6})\}", line_bytes):
                    start_idx, end_idx = m.start(), m.end()
                    if start_idx <= pos_in_line <= end_idx:
                        hex_content = m.group(1).decode('utf-8')
                        detected_html_color = f"#{hex_content.upper()}"

                        highlight_start = line_start_pos + start_idx
                        highlight_length = end_idx - start_idx
                        break
                        
            if detected_html_color:
                try:
                    editor.IndicatorSetStyle(self.COLOR_PREVIEW_INDICATOR_ID, stc.STC_INDIC_TEXTFORE)
                    editor.IndicatorSetForeground(self.COLOR_PREVIEW_INDICATOR_ID, wx.Colour(detected_html_color))

                    editor.IndicatorFillRange(highlight_start, highlight_length)
                except Exception as e:
                    SpawnLogger.error(f"Init Color Preview Indicator: {e}")
        event.Skip()

    def on_savepoint_left(self,event):
        notebook = self.GetParent()
        page_idx = notebook.GetPageIndex(self)
        title = notebook.GetPageText(page_idx)
        if not title.endswith("*"):
            notebook.SetPageText(page_idx, title + "*")

        event.Skip()

    def on_savepoint_reached(self, event):
        notebook = self.GetParent()
        page_idx = notebook.GetPageIndex(self)
        title = notebook.GetPageText(page_idx)
        if title.endswith("*"):
            notebook.SetPageText(page_idx, title[:-1])

        event.Skip()

##    def configure_minimap_base(self):
##        font = wx.Font(2, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas")
##        self.m_scintilla_Minimap.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
##        self.m_scintilla_Minimap.StyleSetSize(stc.STC_STYLE_DEFAULT, 2)
##
##        self.m_scintilla_Minimap.StyleResetDefault()
##        self.m_scintilla_Minimap.StyleClearAll()
##
##        for style_idx in range(0,256):
##            self.m_scintilla_Minimap.StyleSetFont(style_idx, font)
##            self.m_scintilla_Minimap.StyleSetSize(style_idx, 2)
##
##        self.m_scintilla_Minimap.SetExtraAscent(0)
##        self.m_scintilla_Minimap.SetExtraDescent(0)
##
##        if hasattr(self.m_scintilla_Minimap, "SetLineSpacing"):
##            self.m_scintilla_Minimap.SetLineSpacing(0)
##
##        self.m_scintilla_Minimap.SetProperty("fold", "0")
##
##        self.m_scintilla_Minimap.StyleSetSize(0, 2)
##        self.m_scintilla_Minimap.SetMarginWidth(0,0)
##        self.m_scintilla_Minimap.SetMarginWidth(1,0)
##        self.m_scintilla_Minimap.SetMarginWidth(2,0)
##        self.m_scintilla_Minimap.SetHScrollBar(None)
##        self.m_scintilla_Minimap.SetVScrollBar(None)
##
##        self.m_scintilla_Minimap.SetCaretLineVisible(False)
##        self.m_scintilla_Minimap.SetCaretWidth(0)
##        
##
##        self.m_scintilla_Minimap.SetSelBackground(True, "#FFFFFF")
##        self.m_scintilla_Minimap.SetSelForeground(True, "#000000")


    def apply_lexer_by_extension(self):
        if not self.file_path:
            self.set_plain_text_mode()
            return

        ext = os.path.splitext(self.file_path)[-1].lower()

        if ext in ['.pwn', '.inc']:
            self.m_scintilla_Editor.SetLexer(stc.STC_LEX_CPP)
            #self.m_scintilla_Minimap.SetLexer(stc.STC_LEX_CPP)
            self.apply_pawn_styles()
        elif ext in ['.json']:
            self.m_scintilla_Editor.SetLexer(stc.STC_LEX_JSON)
            #self.m_scintilla_Minimap.SetLexer(stc.STC_LEX_JSON)
            self.apply_json_styles()
        else:
            self.set_plain_text_mode()

    def set_plain_text_mode(self):
        editor = self.m_scintilla_Editor
        editor.SetLexer(stc.STC_LEX_NULL)
        editor.StyleResetDefault()

        font_size = self.ide_cfg.get("editor.font.size", 11)
        font_family = self.ide_cfg.get("editor.font.family", "Consolas")
        font = wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family)
        editor.StyleSetFont(stc.STC_STYLE_DEFAULT, font)

        editor.StyleClearAll()
        editor.Refresh()

        editor.MarkerDeleteAll(self.MARKER_MODIFIED_ID)
        editor.MarkerDeleteAll(self.MARKER_SAVED_ID)
        editor.MarkerDeleteAll(self.MARKER_GIT_MODIFIED_ID)

        editor.SetMarginWidth(1, 0)
        editor.SetMarginWidth(2, 0)

    def apply_pawn_styles(self):
        editor = self.m_scintilla_Editor
        
        self.color_preview = self.ide_cfg.get("editor.features.color_preview", True)
        self.brace_matching = self.ide_cfg.get("editor.features.brace_matching.enabled", True)
        self.show_change_history = self.ide_cfg.get("editor.features.show_change_history.enabled", True)
        
        pawn_keywords = "public stock forward native new enum const static if else switch case default for while do break continue return sizeof state goto char hook"
        pawn_types = "bool Float Text PlayerText Text3D Menu DB DBResult Bit Group File SV_GSTREAM SV_STREAM"
        pawn_preprocessor = "define include pragma endinput if else elseif endif assert tryinclude error emit undef"
        
        editor.SetLexer(stc.STC_LEX_CPP)

        font_size = self.ide_cfg.get("editor.font.size", 11)
        font_family = self.ide_cfg.get("editor.font.family", "Consolas")
        font = wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family)
        editor.StyleResetDefault()
        
        editor.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        line_spacing = self.ide_cfg.get("editor.font.line_spacing", 0)
        if line_spacing < 0:
            editor.SetExtraAscent(0)
            editor.SetExtraDescent(line_spacing)
        else:
            editor.SetExtraAscent(line_spacing)
            editor.SetExtraDescent(0)

        editor.StyleSetForeground(stc.STC_STYLE_DEFAULT, "#1E1E1E")
                  
        editor.StyleClearAll()

        editor.SetKeyWords(0, pawn_keywords)
        editor.SetKeyWords(1, pawn_types)
        editor.SetKeyWords(2, pawn_preprocessor)
        
        editor.StyleSetForeground(stc.STC_C_COMMENT, "#6A9955")
        editor.StyleSetForeground(stc.STC_C_COMMENTLINE, "#6A9955")
        editor.StyleSetForeground(stc.STC_C_COMMENTDOC, "#6A9955")
        editor.StyleSetForeground(stc.STC_C_WORD, "#005CC5")
        #editor.StyleSetBold(stc.STC_C_WORD, True)
        editor.StyleSetForeground(stc.STC_C_WORD2, "#6F42C1")
        editor.StyleSetForeground(stc.STC_C_PREPROCESSOR, "#AF00DB")
        editor.StyleSetForeground(stc.STC_C_STRING, "#C41A16")
        editor.StyleSetForeground(stc.STC_C_CHARACTER, "#A31515")
        editor.StyleSetForeground(stc.STC_C_NUMBER, "#098658")
        editor.StyleSetForeground(stc.STC_C_IDENTIFIER,"#1E1E1E")
        editor.StyleSetForeground(stc.STC_C_OPERATOR, "#333333")

        editor.SetTabWidth(4)
        editor.SetUseTabs(False)

        editor.SetCaretForeground("#1E1E1E")
        editor.SetCaretLineVisible(True)
        editor.SetCaretLineBackground("#F8FAFD")

        color_bracelight = self.ide_cfg.get("editor.features.brace_matching.color_bracelight", "#FFFFFF")
        backcolor_bracelight = self.ide_cfg.get("editor.features.brace_matching.backcolor_bracelight", "#E0E0FF")
        color_bracebad = self.ide_cfg.get("editor.features.brace_matching.color_bracebad", "#FFFFFF")
        backcolor_bracebad = self.ide_cfg.get("editor.features.brace_matching.backcolor_bracebad", "#E51400")

        editor.StyleSetFont(stc.STC_STYLE_BRACELIGHT, wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family))
        editor.StyleSetForeground(stc.STC_STYLE_BRACELIGHT, color_bracelight)
        editor.StyleSetBackground(stc.STC_STYLE_BRACELIGHT, backcolor_bracelight)
        editor.StyleSetFont(stc.STC_STYLE_BRACEBAD, wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family))
        editor.StyleSetForeground(stc.STC_STYLE_BRACEBAD, color_bracebad)
        editor.StyleSetBackground(stc.STC_STYLE_BRACEBAD, backcolor_bracebad)

        is_line_numbers = self.ide_cfg.get("editor.features.line_numbers", False)
        if is_line_numbers:
            editor.SetMarginType( 0, stc.STC_MARGIN_NUMBER )
            editor.SetMarginWidth( 0, editor.TextWidth( stc.STC_STYLE_LINENUMBER, "_999999" ) )

        editor.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        editor.SetMarginWidth(1, 4)
        editor.SetMarginMask(1, (1 << 13) | (1 << 14))
        editor.SetMarginSensitive(1, False)

        marker_modified_color = self.ide_cfg.get("editor.features.show_change_history.color_marker_modified", "#FFD324")
        marker_saved_color = self.ide_cfg.get("editor.features.show_change_history.color_marker_saved", "#228B22")
        
        editor.MarkerDefine(self.MARKER_MODIFIED_ID, stc.STC_MARK_FULLRECT)
        editor.MarkerSetForeground(self.MARKER_MODIFIED_ID, marker_modified_color)
        editor.MarkerSetBackground(self.MARKER_MODIFIED_ID, marker_modified_color)
        editor.MarkerDefine(self.MARKER_SAVED_ID, stc.STC_MARK_FULLRECT)
        editor.MarkerSetForeground(self.MARKER_SAVED_ID, marker_saved_color)
        editor.MarkerSetBackground(self.MARKER_SAVED_ID, marker_saved_color)

        editor.MarkerDefine(self.MARKER_GIT_MODIFIED_ID, wx.stc.STC_MARK_BACKGROUND)
        editor.MarkerSetBackground(self.MARKER_GIT_MODIFIED_ID, "#FFF3CD")

        editor.SetSelBackground( True, "#CCE8FF" )
        editor.SetSelForeground( True, "#1E1E1E" )
        editor.StyleSetForeground(stc.STC_STYLE_LINENUMBER,"#808080")
        editor.StyleSetBackground(stc.STC_STYLE_LINENUMBER,"#F3F3F3")
        editor.SetFoldMarginColour(True, "#F7F7F7")
        editor.SetFoldMarginHiColour(True, "#F7F7F7")

        editor.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        editor.SetMarginWidth(2, 16)
        editor.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        editor.SetMarginSensitive(2, True)

        v = ('#F3F3F3', '#606060')
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, *v)
        editor.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, *v)

        is_folding = self.ide_cfg.get("editor.features.folding", False)
        if is_folding:
            editor.SetProperty("fold", "1")
            editor.SetProperty("fold.comment", "1")
            editor.SetProperty("fold.compact", "0")
            editor.SetFoldFlags(stc.STC_FOLDFLAG_LINEBEFORE_CONTRACTED)

        editor.Refresh()

    def apply_json_styles(self):
        editor = self.m_scintilla_Editor
        editor.SetLexer(stc.STC_LEX_JSON)
        
        font_size = self.ide_cfg.get("editor.font.size", 11)
        font_family = self.ide_cfg.get("editor.font.family", "Consolas")
        font = wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family)
        editor.StyleResetDefault()
        
        editor.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        line_spacing = self.ide_cfg.get("editor.font.line_spacing", 0)
        if line_spacing < 0:
            editor.SetExtraAscent(0)
            editor.SetExtraDescent(line_spacing)
        else:
            editor.SetExtraAscent(line_spacing)
            editor.SetExtraDescent(0)
            
        editor.StyleClearAll()

        editor.StyleSetForeground(stc.STC_JSON_PROPERTYNAME, "#0451A5")
        editor.StyleSetBold(stc.STC_JSON_PROPERTYNAME, True)

        editor.StyleSetForeground(stc.STC_JSON_STRING, "#A31515")
        editor.StyleSetForeground(stc.STC_JSON_NUMBER, "#098658")
        editor.StyleSetForeground(stc.STC_JSON_KEYWORD, "#0000FF")
        editor.StyleSetForeground(stc.STC_JSON_OPERATOR, "#000000")

        editor.SetTabWidth(4)
        editor.SetUseTabs(False)

        editor.SetCaretForeground("#000000")
        editor.SetCaretLineVisible(True)
        editor.SetCaretLineBackground("#E8E8E8")

        editor.SetMarginWidth(1, 0)
        editor.SetMarginMask(1, 0)
            
        editor.Refresh()

    def load_file(self, path):
        try:
            with open(path, "rb") as f:
                binary_data = f.read()
                if not binary_data:
                    self.m_scintilla_Editor.SetCodePage(wx.stc.STC_CP_UTF8)
                    self.m_scintilla_Editor.SetText("")
                    
                    if PlatformUtils.is_pawn_file(path):
                        self.current_encoding = self.ide_cfg.get("system.pawn.default_encoding","cp1251")
                    else:
                        self.current_encoding = "utf-8"

                        
                    self.native_eol = PlatformUtils.default_eol()
                    if self.native_eol == "CRLF":
                        self.m_scintilla_Editor.SetEOLMode(stc.STC_EOL_CRLF)
                    else:
                        self.m_scintilla_Editor.SetEOLMode(stc.STC_EOL_LF)
                        
                    return

            text_content, self.current_encoding = (PlatformUtils.decode_text(binary_data))
            
            self.native_eol = (PlatformUtils.detect_eol(binary_data))   
            if self.native_eol == "CRLF":
                self.m_scintilla_Editor.SetEOLMode(stc.STC_EOL_CRLF)
            else:
                self.m_scintilla_Editor.SetEOLMode(stc.STC_EOL_LF)

            text_content = text_content.replace("\r\n", "\n") #I need Scintila to not put spaces between lines. And when I save the file, everything goes back to normal using native_eol.
            text_content = text_content.replace("\r", "\n")

            self.m_scintilla_Editor.SetCodePage(wx.stc.STC_CP_UTF8)
           
            self.m_scintilla_Editor.Freeze()

            try:
                self.m_scintilla_Editor.SetText(text_content)
                self.m_scintilla_Editor.EmptyUndoBuffer()
                self.m_scintilla_Editor.SetSavePoint()
            except Exception as e:
                SpawnLogger.error(f"Load File: {e}")
                
            finally:
                self.m_scintilla_Editor.Thaw()

            #self.current_encoding = "utf-8"
        except Exception as e:
            SpawnLogger.error(f"Load File: {e}")
            self.m_scintilla_Editor.SetText(f"// Disk buffer error")
            
    
