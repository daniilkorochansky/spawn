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
import sys
import copy
import json

import wx
import wx.xrc
import wx.dataview

import gettext
_ = gettext.gettext

def get_app_root_dir():
    if 'NUITKA_ONEFILE_PARENT' in os.environ or getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))

    ui_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(ui_dir)

APP_ROOT = get_app_root_dir()

class SettingsCompleter(wx.TextCompleterSimple):
    def __init__(self, config):
        super().__init__()

        self.cfg = config

        self.matches = []
        self.index = 0

    def Start(self, prefix):
        self.matches.clear()

        results = self.cfg.search_settings(prefix)

        for item in results:

            if item["category"]:

                self.matches.append(
                    f'{item["title"]} ({item["category"]})'
                )

            else:

                self.matches.append(
                    item["title"]
                )

        self.index = 0

        return bool(self.matches)

    def GetNext(self):

        if self.index >= len(self.matches):
            return ""

        value = self.matches[self.index]

        self.index += 1

        return value
    

class SettingsDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Settings"), pos = wx.DefaultPosition, size = wx.Size( 1050,624 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER )
        icon = wx.Icon(os.path.join(APP_ROOT, "assets", "settings.ico"), wx.BITMAP_TYPE_ICO) 
        self.SetIcon(icon)

        self.Bind(wx.EVT_CLOSE, self.on_settings_close_request)

        self.setting_controls = {}
        self.path_to_page = {}
        self.control_to_path = {}

        self.ide_cfg = parent.ide_cfg

        self.main_win = parent

        self.icons_folder = os.path.join(APP_ROOT, "assets", "icons")
        
        self.original_config = copy.deepcopy(self.ide_cfg.global_config)
        self.working_config = copy.deepcopy(self.original_config)
        self.modified_settings = set()

        self.tree_navigation = {}

        self.profile_items = []

        font_enumerator = wx.FontEnumerator()
        font_enumerator.EnumerateFacenames(fixedWidthOnly=True)
        self.font_list = font_enumerator.GetFacenames()

        self.SetSizeHints( wx.Size( 870,500 ), wx.DefaultSize )

        self.icons_folder = os.path.join(APP_ROOT, "assets", "icons")

        bSizer_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_Submain = wx.BoxSizer( wx.VERTICAL )

        self.m_splitter_Main = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
        self.m_splitter_Main.Bind( wx.EVT_IDLE, self.m_splitter_MainOnIdle )
        self.m_splitter_Main.SetMinimumPaneSize( 140 )

        self.m_panel_Category = wx.Panel( self.m_splitter_Main, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Category_Main = wx.BoxSizer( wx.VERTICAL )

        self.m_searchCtrl = wx.SearchCtrl( self.m_panel_Category, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_searchCtrl.ShowSearchButton( True )
        self.m_searchCtrl.SetDescriptiveText(_(u"Search settings..."))
        self.m_searchCtrl.ShowCancelButton( False )
        self.m_searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,self.on_search_enter)
        bSizer_Category_Main.Add( self.m_searchCtrl, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_treeListCtrl = wx.TreeCtrl( self.m_panel_Category, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HIDE_ROOT )
        self.m_treeListCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection_changed)
        self.m_treeListCtrl.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.on_tree_collapsing)

        self.tree_images = wx.ImageList(16,16)
        self.idx_profiles = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"settings_profile.png"),wx.BITMAP_TYPE_PNG))
        self.idx_pawn = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"settings_pawn.png"),wx.BITMAP_TYPE_PNG))
        self.idx_editor = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"settings_editor.png"),wx.BITMAP_TYPE_PNG))
        self.idx_git = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"settings_git.png"),wx.BITMAP_TYPE_PNG))
        self.idx_system = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"settings_system.png"),wx.BITMAP_TYPE_PNG))
        self.idx_empty = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"tree_empty.png"),wx.BITMAP_TYPE_PNG))
        self.m_treeListCtrl.AssignImageList(self.tree_images)

        self.icon_indices = {
            "profiles": self.idx_profiles,
            "pawn": self.idx_pawn,
            "editor": self.idx_editor,
            "git": self.idx_git,
            "system": self.idx_system,
            "empty": self.idx_empty
            }

        bSizer_Category_Main.Add( self.m_treeListCtrl, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_panel_Category.SetSizer( bSizer_Category_Main )
        self.m_panel_Category.Layout()
        bSizer_Category_Main.Fit( self.m_panel_Category )
        self.m_panel_Settings = wx.Panel( self.m_splitter_Main, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Settings_Main = wx.BoxSizer( wx.VERTICAL )

        self.m_simplebook = wx.Simplebook( self.m_panel_Settings, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        self.m_panel_Editor = wx.Panel( self.m_simplebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Panel_Editor = wx.BoxSizer( wx.VERTICAL )

        self.m_scrolledWindow_Panel_Editor = wx.ScrolledWindow( self.m_panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow_Panel_Editor.SetScrollRate( 5, 5 )
        bSizer_EditorMain = wx.BoxSizer( wx.VERTICAL )

        bSizer_Editor_General = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_Editor_GeneralTitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"General"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Editor_GeneralTitle.Wrap( -1 )

        self.m_staticText_Editor_GeneralTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Editor_General.Add( self.m_staticText_Editor_GeneralTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_Editor_GeneralSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Common editor behavior and interface options."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Editor_GeneralSubtitle.Wrap( -1 )

        bSizer_Editor_General.Add( self.m_staticText_Editor_GeneralSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline41 = wx.StaticLine( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Editor_General.Add( self.m_staticline41, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_EditorMain.Add( bSizer_Editor_General, 0, wx.EXPAND, 5 )

        self.m_checkBox_LineNumbers = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Line Numbers"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_LineNumbers, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_LineNumbers, "editor.features.line_numbers", self.m_panel_Editor)

        self.m_checkBox_CodeFolding = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Code Folding"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_CodeFolding, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_CodeFolding, "editor.features.folding", self.m_panel_Editor)

        bSizer_Editor_Font = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_FontTitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Font"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_FontTitle.Wrap( -1 )

        self.m_staticText_FontTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Editor_Font.Add( self.m_staticText_FontTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_FontSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Configure editor font family, size and spacing."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_FontSubtitle.Wrap( -1 )

        bSizer_Editor_Font.Add( self.m_staticText_FontSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline411 = wx.StaticLine( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Editor_Font.Add( self.m_staticline411, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_EditorMain.Add( bSizer_Editor_Font, 0, wx.EXPAND|wx.TOP, 15 )

        bSizer_FontFamily = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_FontFamily = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Font Family:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_FontFamily.Wrap( -1 )

        bSizer_FontFamily.Add( self.m_staticText_FontFamily, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice_FontFamilyChoices = self.font_list
        self.m_choice_FontFamily = wx.Choice( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_FontFamilyChoices, 0 )
        self.m_choice_FontFamily.SetSelection( 0 )
        self.m_choice_FontFamily.SetMinSize( wx.Size( 200,-1 ) )

        bSizer_FontFamily.Add( self.m_choice_FontFamily, 0, wx.ALL, 5 )
        self.register_setting(self.m_choice_FontFamily, "editor.font.family", self.m_panel_Editor)


        bSizer_EditorMain.Add( bSizer_FontFamily, 0, wx.EXPAND, 5 )

        bSizer_FontSize = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_FontSize = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Font Size:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_FontSize.Wrap( -1 )

        bSizer_FontSize.Add( self.m_staticText_FontSize, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_spinCtrl_FontSize = wx.SpinCtrl( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 3, 40, 11 )
        self.m_spinCtrl_FontSize.SetMinSize( wx.Size( 50,-1 ) )

        bSizer_FontSize.Add( self.m_spinCtrl_FontSize, 0, wx.ALL, 5 )
        self.register_setting(self.m_spinCtrl_FontSize, "editor.font.size", self.m_panel_Editor)


        bSizer_EditorMain.Add( bSizer_FontSize, 0, wx.EXPAND, 5 )

        bSizer_LineSpacing = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_LineSpacing = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Line Spacing:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_LineSpacing.Wrap( -1 )

        bSizer_LineSpacing.Add( self.m_staticText_LineSpacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_spinCtrl_LineSpacing = wx.SpinCtrl( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, -20, 20, 1 )
        self.m_spinCtrl_LineSpacing.SetMinSize( wx.Size( 50,-1 ) )

        bSizer_LineSpacing.Add( self.m_spinCtrl_LineSpacing, 0, wx.ALL, 5 )
        self.register_setting(self.m_spinCtrl_LineSpacing, "editor.font.line_spacing", self.m_panel_Editor)


        bSizer_EditorMain.Add( bSizer_LineSpacing, 0, wx.EXPAND, 5 )

        bSizer_Editor_CodeEditing = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_CodeEditingTitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Code Editing"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_CodeEditingTitle.Wrap( -1 )

        self.m_staticText_CodeEditingTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Editor_CodeEditing.Add( self.m_staticText_CodeEditingTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_CodeEditingSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Customize typing, indentation and editing behavior."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_CodeEditingSubtitle.Wrap( -1 )

        bSizer_Editor_CodeEditing.Add( self.m_staticText_CodeEditingSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline4111 = wx.StaticLine( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Editor_CodeEditing.Add( self.m_staticline4111, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_EditorMain.Add( bSizer_Editor_CodeEditing, 0, wx.EXPAND|wx.TOP, 15 )

        self.m_checkBox_SmartIndent = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Smart Indentation"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_SmartIndent, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_SmartIndent, "editor.features.smart_indent", self.m_panel_Editor)

        self.m_checkBox_Brace_Matching = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Brace Matching"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_Brace_Matching, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_Brace_Matching, "editor.features.brace_matching.enabled", self.m_panel_Editor)

        sbSizer_BraceMatching = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Colors") ), wx.VERTICAL )

        self.m_staticText_BraceMatch_Colors = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Matching Brace"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_BraceMatch_Colors.Wrap( -1 )

        self.m_staticText_BraceMatch_Colors.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        sbSizer_BraceMatching.Add( self.m_staticText_BraceMatch_Colors, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        self.m_panel_BM_StaticLine = wx.Panel( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_panel_BM_StaticLine.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.m_panel_BM_StaticLine.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

        sbSizer_BraceMatching.Add( self.m_panel_BM_StaticLine, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_BM_Colors_Foreground = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_BM_Foreground = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Foreground:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_BM_Foreground.Wrap( -1 )

        bSizer_BM_Colors_Foreground.Add( self.m_staticText_BM_Foreground, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_BraceMatching = wx.ColourPickerCtrl( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_BM_Colors_Foreground.Add( self.m_colourPicker_BraceMatching, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_BraceMatching, "editor.features.brace_matching.color_bracelight", self.m_panel_Editor)


        sbSizer_BraceMatching.Add( bSizer_BM_Colors_Foreground, 0, wx.EXPAND, 5 )

        bSizer_BM_Colors_Background = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_BM_Background = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Background:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_BM_Background.Wrap( -1 )

        bSizer_BM_Colors_Background.Add( self.m_staticText_BM_Background, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_BraceMatchingBack = wx.ColourPickerCtrl( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_BM_Colors_Background.Add( self.m_colourPicker_BraceMatchingBack, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_BraceMatchingBack, "editor.features.brace_matching.backcolor_bracelight", self.m_panel_Editor)


        sbSizer_BraceMatching.Add( bSizer_BM_Colors_Background, 0, wx.EXPAND, 5 )

        self.m_staticText_BadMatch_Colors = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Bad Brace"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_BadMatch_Colors.Wrap( -1 )

        self.m_staticText_BadMatch_Colors.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        sbSizer_BraceMatching.Add( self.m_staticText_BadMatch_Colors, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        self.m_panel_BM_StaticLine2 = wx.Panel( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_panel_BM_StaticLine2.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.m_panel_BM_StaticLine2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

        sbSizer_BraceMatching.Add( self.m_panel_BM_StaticLine2, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_BM_Colors_Bad_Foreground = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Bad_BM_Foreground = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Foreground:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Bad_BM_Foreground.Wrap( -1 )

        bSizer_BM_Colors_Bad_Foreground.Add( self.m_staticText_Bad_BM_Foreground, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Bad_BraceMatching = wx.ColourPickerCtrl( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_BM_Colors_Bad_Foreground.Add( self.m_colourPicker_Bad_BraceMatching, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Bad_BraceMatching, "editor.features.brace_matching.color_bracebad", self.m_panel_Editor)

        sbSizer_BraceMatching.Add( bSizer_BM_Colors_Bad_Foreground, 0, wx.EXPAND, 5 )

        bSizer_BM_Colors_Bad_Background = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Bad_BM_Background = wx.StaticText( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, _(u"Background:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Bad_BM_Background.Wrap( -1 )

        bSizer_BM_Colors_Bad_Background.Add( self.m_staticText_Bad_BM_Background, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Bad_BraceMatchingBack = wx.ColourPickerCtrl( sbSizer_BraceMatching.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_BM_Colors_Bad_Background.Add( self.m_colourPicker_Bad_BraceMatchingBack, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Bad_BraceMatchingBack, "editor.features.brace_matching.backcolor_bracebad", self.m_panel_Editor)

        sbSizer_BraceMatching.Add( bSizer_BM_Colors_Bad_Background, 1, wx.EXPAND, 5 )


        bSizer_EditorMain.Add( sbSizer_BraceMatching, 0, wx.EXPAND, 5 )

        bSizer_Editor_Display = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_DisplayTitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Display"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_DisplayTitle.Wrap( -1 )

        self.m_staticText_DisplayTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Editor_Display.Add( self.m_staticText_DisplayTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticTextDisplaySubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Configure visual editor features and markers."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextDisplaySubtitle.Wrap( -1 )

        self.m_staticTextDisplaySubtitle.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )

        bSizer_Editor_Display.Add( self.m_staticTextDisplaySubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline41111 = wx.StaticLine( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Editor_Display.Add( self.m_staticline41111, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_EditorMain.Add( bSizer_Editor_Display, 0, wx.EXPAND|wx.TOP, 15 )

        self.m_checkBox_ColorPreview = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Color Preview"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_ColorPreview, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_ColorPreview, "editor.features.color_preview", self.m_panel_Editor)

        self.m_checkBox_ChangeHistory = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Change History"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_ChangeHistory, 0, wx.ALL|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
        self.register_setting(self.m_checkBox_ChangeHistory, "editor.features.show_change_history.enabled", self.m_panel_Editor)

        sbSizer_CH_Colors_Std = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Colors") ), wx.VERTICAL )

        bSizer_CH_Mod_Marker = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Mod_Marker = wx.StaticText( sbSizer_CH_Colors_Std.GetStaticBox(), wx.ID_ANY, _(u"Modified Marker:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Mod_Marker.Wrap( -1 )

        bSizer_CH_Mod_Marker.Add( self.m_staticText_Mod_Marker, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Mod_Marker = wx.ColourPickerCtrl( sbSizer_CH_Colors_Std.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_CH_Mod_Marker.Add( self.m_colourPicker_Mod_Marker, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Mod_Marker, "editor.features.show_change_history.color_marker_modified", self.m_panel_Editor)


        sbSizer_CH_Colors_Std.Add( bSizer_CH_Mod_Marker, 0, wx.EXPAND, 5 )

        bSizer_CH_Saved_Marker = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Saved_Marker = wx.StaticText( sbSizer_CH_Colors_Std.GetStaticBox(), wx.ID_ANY, _(u"Saved Marker:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Saved_Marker.Wrap( -1 )

        bSizer_CH_Saved_Marker.Add( self.m_staticText_Saved_Marker, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Saved_Marker = wx.ColourPickerCtrl( sbSizer_CH_Colors_Std.GetStaticBox(), wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_CH_Saved_Marker.Add( self.m_colourPicker_Saved_Marker, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Saved_Marker, "editor.features.show_change_history.color_marker_saved", self.m_panel_Editor)


        sbSizer_CH_Colors_Std.Add( bSizer_CH_Saved_Marker, 1, wx.EXPAND, 5 )


        bSizer_EditorMain.Add( sbSizer_CH_Colors_Std, 1, wx.EXPAND, 5 )

        bSizer_Cur_Line_Color = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Cur_Line_Color = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Current Line Color:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Cur_Line_Color.Wrap( -1 )

        bSizer_Cur_Line_Color.Add( self.m_staticText_Cur_Line_Color, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Cur_Line_Color = wx.ColourPickerCtrl( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_Cur_Line_Color.Add( self.m_colourPicker_Cur_Line_Color, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Cur_Line_Color, "editor.current_line_color", self.m_panel_Editor)


        bSizer_EditorMain.Add( bSizer_Cur_Line_Color, 0, wx.EXPAND, 5 )

        bSizer_Selection_Color = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Selection_Color = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Selection Color:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Selection_Color.Wrap( -1 )

        bSizer_Selection_Color.Add( self.m_staticText_Selection_Color, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_colourPicker_Selection_Color = wx.ColourPickerCtrl( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer_Selection_Color.Add( self.m_colourPicker_Selection_Color, 0, wx.ALL, 5 )
        self.register_setting(self.m_colourPicker_Selection_Color, "editor.selection_color", self.m_panel_Editor)


        bSizer_EditorMain.Add( bSizer_Selection_Color, 0, wx.EXPAND, 5 )

        bSizer_Editor_Advanced = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_AdvancedTitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Advanced"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_AdvancedTitle.Wrap( -1 )

        self.m_staticText_AdvancedTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Editor_Advanced.Add( self.m_staticText_AdvancedTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_AdvancedSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Advanced editor options and experimental features."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_AdvancedSubtitle.Wrap( -1 )

        bSizer_Editor_Advanced.Add( self.m_staticText_AdvancedSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline411111 = wx.StaticLine( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Editor_Advanced.Add( self.m_staticline411111, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_EditorMain.Add( bSizer_Editor_Advanced, 0, wx.EXPAND|wx.TOP, 15 )

        self.m_checkBox_MultiCursor = wx.CheckBox( self.m_scrolledWindow_Panel_Editor, wx.ID_ANY, _(u"Multi Cursor"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_EditorMain.Add( self.m_checkBox_MultiCursor, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_MultiCursor, "editor.features.multicursor.enable", self.m_panel_Editor)


        self.m_scrolledWindow_Panel_Editor.SetSizer( bSizer_EditorMain )
        self.m_scrolledWindow_Panel_Editor.Layout()
        bSizer_EditorMain.Fit( self.m_scrolledWindow_Panel_Editor )
        bSizer_Panel_Editor.Add( self.m_scrolledWindow_Panel_Editor, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panel_Editor.SetSizer( bSizer_Panel_Editor )
        self.m_panel_Editor.Layout()
        bSizer_Panel_Editor.Fit( self.m_panel_Editor )
        self.m_simplebook.AddPage( self.m_panel_Editor, _(u"Editor"), False )
        self.m_panel_Pawn = wx.Panel( self.m_simplebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Panel_Pawn = wx.BoxSizer( wx.VERTICAL )

        self.m_scrolledWindow_Panel_Pawn = wx.ScrolledWindow( self.m_panel_Pawn, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow_Panel_Pawn.SetScrollRate( 5, 5 )
        bSizer_Pawn_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_Pawn_General = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_Pawn_GeneralTitle = wx.StaticText( self.m_scrolledWindow_Panel_Pawn, wx.ID_ANY, _(u"General"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Pawn_GeneralTitle.Wrap( -1 )

        self.m_staticText_Pawn_GeneralTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Pawn_General.Add( self.m_staticText_Pawn_GeneralTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_Pawn_GeneralSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Pawn, wx.ID_ANY, _(u"General Pawn language options."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Pawn_GeneralSubtitle.Wrap( -1 )

        bSizer_Pawn_General.Add( self.m_staticText_Pawn_GeneralSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline412 = wx.StaticLine( self.m_scrolledWindow_Panel_Pawn, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Pawn_General.Add( self.m_staticline412, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_Pawn_Main.Add( bSizer_Pawn_General, 0, wx.EXPAND, 5 )

        bSizer_DefEncoding = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_DefEncoding = wx.StaticText( self.m_scrolledWindow_Panel_Pawn, wx.ID_ANY, _(u"Default Encoding:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_DefEncoding.Wrap( -1 )

        bSizer_DefEncoding.Add( self.m_staticText_DefEncoding, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice_DefEncodingChoices = ["utf-8","cp1250","cp1251","cp1252","cp1253","cp1254","cp1255","cp1256","cp1257"]
        self.m_choice_DefEncoding = wx.Choice( self.m_scrolledWindow_Panel_Pawn, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_DefEncodingChoices, 0 )
        self.m_choice_DefEncoding.SetSelection( 0 )
        self.m_choice_DefEncoding.SetMinSize( wx.Size( 150,-1 ) )
        self.register_setting(self.m_choice_DefEncoding, "system.pawn.default_encoding", self.m_panel_Pawn)

        bSizer_DefEncoding.Add( self.m_choice_DefEncoding, 0, wx.ALL, 5 )


        bSizer_Pawn_Main.Add( bSizer_DefEncoding, 0, wx.EXPAND, 5 )


        self.m_scrolledWindow_Panel_Pawn.SetSizer( bSizer_Pawn_Main )
        self.m_scrolledWindow_Panel_Pawn.Layout()
        bSizer_Pawn_Main.Fit( self.m_scrolledWindow_Panel_Pawn )
        bSizer_Panel_Pawn.Add( self.m_scrolledWindow_Panel_Pawn, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panel_Pawn.SetSizer( bSizer_Panel_Pawn )
        self.m_panel_Pawn.Layout()
        bSizer_Panel_Pawn.Fit( self.m_panel_Pawn )
        self.m_simplebook.AddPage( self.m_panel_Pawn, u"Pawn", False )
        self.m_panel_Git = wx.Panel( self.m_simplebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Panel_Git = wx.BoxSizer( wx.VERTICAL )

        self.m_scrolledWindow_Panel_Git = wx.ScrolledWindow( self.m_panel_Git, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow_Panel_Git.SetScrollRate( 5, 5 )
        bSizer_Git_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_Git_General = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_Git_GeneralTitle = wx.StaticText( self.m_scrolledWindow_Panel_Git, wx.ID_ANY, _(u"General"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Git_GeneralTitle.Wrap( -1 )

        self.m_staticText_Git_GeneralTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Git_General.Add( self.m_staticText_Git_GeneralTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_Git_GeneralSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_Git, wx.ID_ANY, _(u"Git integration and version control settings."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Git_GeneralSubtitle.Wrap( -1 )

        bSizer_Git_General.Add( self.m_staticText_Git_GeneralSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline4121 = wx.StaticLine( self.m_scrolledWindow_Panel_Git, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Git_General.Add( self.m_staticline4121, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_Git_Main.Add( bSizer_Git_General, 0, wx.EXPAND, 5 )

        self.m_checkBox_EnableGit = wx.CheckBox( self.m_scrolledWindow_Panel_Git, wx.ID_ANY, _(u"Enable Git"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Git_Main.Add( self.m_checkBox_EnableGit, 0, wx.ALL, 5 )
        self.register_setting(self.m_checkBox_EnableGit, "system.git.enable", self.m_panel_Git)


        self.m_scrolledWindow_Panel_Git.SetSizer( bSizer_Git_Main )
        self.m_scrolledWindow_Panel_Git.Layout()
        bSizer_Git_Main.Fit( self.m_scrolledWindow_Panel_Git )
        bSizer_Panel_Git.Add( self.m_scrolledWindow_Panel_Git, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panel_Git.SetSizer( bSizer_Panel_Git )
        self.m_panel_Git.Layout()
        bSizer_Panel_Git.Fit( self.m_panel_Git )
        self.m_simplebook.AddPage( self.m_panel_Git, u"Git", False )
        self.m_panel_System = wx.Panel( self.m_simplebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_Panel_System = wx.BoxSizer( wx.VERTICAL )

        self.m_scrolledWindow_Panel_System = wx.ScrolledWindow( self.m_panel_System, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow_Panel_System.SetScrollRate( 5, 5 )
        bSizer_System_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_System_General = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_System_GeneralTitle = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"General"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_System_GeneralTitle.Wrap( -1 )

        self.m_staticText_System_GeneralTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_System_General.Add( self.m_staticText_System_GeneralTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_System_GeneralSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"General application behavior."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_System_GeneralSubtitle.Wrap( -1 )

        bSizer_System_General.Add( self.m_staticText_System_GeneralSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline4122 = wx.StaticLine( self.m_scrolledWindow_Panel_System, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_System_General.Add( self.m_staticline4122, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_System_Main.Add( bSizer_System_General, 0, wx.EXPAND, 5 )

        bSizer_RecentFilesLimit = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_RecentFilesLimit = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"Recent Files Limit:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_RecentFilesLimit.Wrap( -1 )

        bSizer_RecentFilesLimit.Add( self.m_staticText_RecentFilesLimit, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_spinCtrl_RecentFilesLimit = wx.SpinCtrl( self.m_scrolledWindow_Panel_System, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 5, 25, 15 )
        bSizer_RecentFilesLimit.Add( self.m_spinCtrl_RecentFilesLimit, 0, wx.ALL, 5 )
        self.register_setting(self.m_spinCtrl_RecentFilesLimit, "recent_files_limit", self.m_panel_System)

        bSizer_System_Main.Add( bSizer_RecentFilesLimit, 0, wx.EXPAND, 5 )

        bSizer_System_Paths = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_PathsTitle = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"Paths"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_PathsTitle.Wrap( -1 )

        self.m_staticText_PathsTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_System_Paths.Add( self.m_staticText_PathsTitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_PathsSubtitle = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"Configure executable and resource paths."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_PathsSubtitle.Wrap( -1 )

        bSizer_System_Paths.Add( self.m_staticText_PathsSubtitle, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline41221 = wx.StaticLine( self.m_scrolledWindow_Panel_System, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_System_Paths.Add( self.m_staticline41221, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer_System_Main.Add( bSizer_System_Paths, 0, wx.EXPAND|wx.TOP, 15 )

        bSizer_SampctExe = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_SampctExe = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"SAMPCTL executable:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_SampctExe.Wrap( -1 )

        bSizer_SampctExe.Add( self.m_staticText_SampctExe, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_filePicker_SampctExe = wx.FilePickerCtrl( self.m_scrolledWindow_Panel_System, wx.ID_ANY, wx.EmptyString, _(u"Select a file"), _(u"*.*"), wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST )
        bSizer_SampctExe.Add( self.m_filePicker_SampctExe, 1, wx.ALL, 5 )
        self.register_setting(self.m_filePicker_SampctExe, "system.sampctl.executable_path", self.m_panel_System)
        pickerCtrl = self.m_filePicker_SampctExe.GetPickerCtrl()
        pickerCtrl.SetLabel(_(u"Browse"))


        bSizer_System_Main.Add( bSizer_SampctExe, 0, wx.EXPAND, 5 )

        bSizer_GitExe = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_GitExe = wx.StaticText( self.m_scrolledWindow_Panel_System, wx.ID_ANY, _(u"Git executable:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_GitExe.Wrap( -1 )

        bSizer_GitExe.Add( self.m_staticText_GitExe, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_filePicker_GitExe = wx.FilePickerCtrl( self.m_scrolledWindow_Panel_System, wx.ID_ANY, wx.EmptyString, _(u"Select a file"), _(u"*.*"), wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST )
        bSizer_GitExe.Add( self.m_filePicker_GitExe, 1, wx.ALL, 5 )
        self.register_setting(self.m_filePicker_GitExe, "system.git.executable_path", self.m_panel_System)
        pickerCtrl = self.m_filePicker_SampctExe.GetPickerCtrl()
        pickerCtrl.SetLabel(_(u"Browse"))


        bSizer_System_Main.Add( bSizer_GitExe, 0, wx.EXPAND, 5 )


        self.m_scrolledWindow_Panel_System.SetSizer( bSizer_System_Main )
        self.m_scrolledWindow_Panel_System.Layout()
        bSizer_System_Main.Fit( self.m_scrolledWindow_Panel_System )
        bSizer_Panel_System.Add( self.m_scrolledWindow_Panel_System, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panel_System.SetSizer( bSizer_Panel_System )
        self.m_panel_System.Layout()
        bSizer_Panel_System.Fit( self.m_panel_System )
        self.m_simplebook.AddPage( self.m_panel_System, _(u"System"), False )

        bSizer_Settings_Main.Add( self.m_simplebook, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panel_Settings.SetSizer( bSizer_Settings_Main )
        self.m_panel_Settings.Layout()
        bSizer_Settings_Main.Fit( self.m_panel_Settings )
        self.m_splitter_Main.SplitVertically( self.m_panel_Category, self.m_panel_Settings, 290 )
        bSizer_Submain.Add( self.m_splitter_Main, 1, wx.EXPAND, 5 )


        bSizer_Main.Add( bSizer_Submain, 1, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Main.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_StdButtons = wx.BoxSizer( wx.HORIZONTAL )

##        self.m_buttonReset = wx.Button( self, wx.ID_ANY, _(u"Reset to Defaults"), wx.DefaultPosition, wx.DefaultSize, 0 )
##        bSizer_StdButtons.Add( self.m_buttonReset, 0, wx.ALL, 5 )
##        self.m_buttonReset.SetToolTip(_(u"Reset to default settings"))
##        self.m_buttonReset.Bind(wx.EVT_BUTTON, self.on_reset_to_default)

        self.m_buttonLocalReset = wx.Button( self, wx.ID_ANY, _(u"Reset Changes"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_StdButtons.Add( self.m_buttonLocalReset, 0, wx.ALL, 5 )
        self.m_buttonLocalReset.Enable(False)
        self.m_buttonLocalReset.SetToolTip(_(u"Reset the changes"))
        self.m_buttonLocalReset.Bind(wx.EVT_BUTTON, self.on_reset_changes)

        bSizer_StdButtons.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_buttonOk = wx.Button( self, wx.ID_ANY, _(u"OK"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_StdButtons.Add( self.m_buttonOk, 0, wx.ALL, 5 )
        self.m_buttonOk.Bind(wx.EVT_BUTTON, self.on_ok)

        self.m_buttonCancel = wx.Button( self, wx.ID_ANY, _(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_StdButtons.Add( self.m_buttonCancel, 0, wx.ALL, 5 )
        self.m_buttonCancel.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.m_buttonApply = wx.Button( self, wx.ID_ANY, _(u"Apply"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonApply.Enable( False )
        self.m_buttonApply.Bind(wx.EVT_BUTTON, self.on_apply)

        bSizer_StdButtons.Add( self.m_buttonApply, 0, wx.ALL, 5 )


        bSizer_Main.Add( bSizer_StdButtons, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer_Main )
        self.Layout()

        self.Centre( wx.BOTH )

        self.ide_cfg.build_settings_index()
        
        self.m_searchCtrl.AutoComplete(SettingsCompleter(self.ide_cfg))
        self.apply_config_to_controls()

        self.build_tree_ctrl(self.m_treeListCtrl)
        

    def __del__( self ):
        pass

    def on_reset_changes(self, event):
        self.working_config = copy.deepcopy(self.original_config)
        self.modified_settings.clear()
        self.apply_config_to_controls()
        self.update_buttons()
        

    def on_settings_close_request(self, event):
        self.on_cancel(None)

    def on_tree_collapsing(self, event):
        event.Veto()

    def on_tree_selection_changed(self, event):
        item = event.GetItem()
        data = self.tree_navigation.get(item)

        if data is None:
            return

        page = data["page"]
        self.m_simplebook.SetSelection(self.m_simplebook.FindPage(page))

        section = data["section"]
        if section:
            self.scroll_to_control(section)
        

    def register_tree_item(self, item, page, section_ctrl=None):
        self.tree_navigation[item] = {
            "page": page,
            "section": section_ctrl
            }

    def build_tree_ctrl(self, tree):
        tree.DeleteAllItems()
        root = tree.AddRoot("Settings")
        
        editor = tree.AppendItem(root, _(u"Editor"))
        tree.SetItemImage(editor, self.icon_indices["editor"], wx.TreeItemIcon_Normal)
        self.register_tree_item(editor, self.m_panel_Editor, self.m_staticText_Editor_GeneralTitle)
        
        pawn = tree.AppendItem(root, "Pawn")
        tree.SetItemImage(pawn, self.icon_indices["pawn"], wx.TreeItemIcon_Normal)
        self.register_tree_item(pawn, self.m_panel_Pawn, self.m_staticText_Pawn_GeneralTitle)
        
        git = tree.AppendItem(root, "Git")
        tree.SetItemImage(git, self.icon_indices["git"], wx.TreeItemIcon_Normal)
        self.register_tree_item(git, self.m_panel_Git, self.m_staticText_Git_GeneralTitle)
        
        system = tree.AppendItem(root, _(u"System"))
        tree.SetItemImage(system, self.icon_indices["system"], wx.TreeItemIcon_Normal)
        self.register_tree_item(system, self.m_panel_System, self.m_staticText_System_GeneralTitle)

        editor_general = tree.AppendItem(editor, _(u"General"))
        self.register_tree_item(editor_general, self.m_panel_Editor, self.m_staticText_Editor_GeneralTitle)
        tree.SetItemImage(editor_general, self.icon_indices["empty"], wx.TreeItemIcon_Normal)
        
        font = tree.AppendItem(editor, _(u"Font"))
        self.register_tree_item(font, self.m_panel_Editor, self.m_staticText_FontTitle)
        tree.SetItemImage(font, self.icon_indices["empty"], wx.TreeItemIcon_Normal)
        
        code_editing = tree.AppendItem(editor, _(u"Code Editing"))
        self.register_tree_item(code_editing, self.m_panel_Editor, self.m_staticText_CodeEditingTitle)
        tree.SetItemImage(code_editing, self.icon_indices["empty"], wx.TreeItemIcon_Normal)
        
        display = tree.AppendItem(editor, _(u"Display"))
        self.register_tree_item(display, self.m_panel_Editor, self.m_staticText_DisplayTitle)
        tree.SetItemImage(display, self.icon_indices["empty"], wx.TreeItemIcon_Normal)
        
        advanced = tree.AppendItem(editor, _(u"Advanced"))
        self.register_tree_item(advanced, self.m_panel_Editor, self.m_staticText_AdvancedTitle)
        tree.SetItemImage(advanced, self.icon_indices["empty"], wx.TreeItemIcon_Normal)

        pawn_general = tree.AppendItem(pawn, _(u"General"))
        self.register_tree_item(pawn_general, self.m_panel_Pawn, self.m_staticText_Pawn_GeneralTitle)
        tree.SetItemImage(pawn_general, self.icon_indices["empty"], wx.TreeItemIcon_Normal)

        git_general = tree.AppendItem(git, _(u"General"))
        self.register_tree_item(git_general, self.m_panel_Git, self.m_staticText_Git_GeneralTitle)
        tree.SetItemImage(git_general, self.icon_indices["empty"], wx.TreeItemIcon_Normal)

        system_general = tree.AppendItem(system, _(u"General"))
        self.register_tree_item(system_general, self.m_panel_System, self.m_staticText_System_GeneralTitle)
        tree.SetItemImage(system_general, self.icon_indices["empty"], wx.TreeItemIcon_Normal)
        
        paths = tree.AppendItem(system, _(u"Paths"))
        self.register_tree_item(paths, self.m_panel_System, self.m_staticText_PathsTitle)
        tree.SetItemImage(paths, self.icon_indices["empty"], wx.TreeItemIcon_Normal)

        tree.ExpandAll()
        

    def apply_config_to_controls(self):
        self._loading_settings = True

        config = self.ide_cfg.global_config

        for path, ctrl in self.setting_controls.items():

            value = self.ide_cfg._get_from_dict(
                config,
                path
            )

            if value is None:
                continue

            self._set_control_value(ctrl, value)

        self._loading_settings = False

    def on_cancel(self, event):
        if self.modified_settings:

            res = wx.MessageBox(
                _(u"Discard unsaved changes?"),
                _(u"Settings"),
                wx.YES_NO | wx.ICON_QUESTION
            )

            if res != wx.YES:
                return

        self.EndModal(wx.ID_CANCEL)

    def on_ok(self, event):
        self.on_apply(None)
        self.EndModal(wx.ID_OK)

    def on_apply(self, event):
        for path in self.modified_settings:
            value = self.ide_cfg._get_from_dict(
                self.working_config,
                path
            )

            self.ide_cfg.set(path,value)

        self.original_config = copy.deepcopy(
            self.working_config
        )

        self.modified_settings.clear()
        self.update_buttons()
        self.main_win.check_environment_on_startup()

        notebook = self.main_win.m_auinotebook_Main
        if notebook.GetPageCount() > 0:
            for i in reversed(range(notebook.GetPageCount())):
                tab = notebook.GetPage(i)
                tab.apply_settings()

        

    def scroll_to_control(self, ctrl, margin=20):
        if ctrl is None or ctrl.IsBeingDeleted():
            return

        parent = ctrl.GetParent()

        while parent is not None:

            if isinstance(parent, wx.ScrolledWindow):
                break

            parent = parent.GetParent()

        if parent is None:
            return

        ctrl_pos = parent.ScreenToClient(
            ctrl.ClientToScreen((0, 0))
        )

        _, unit_y = parent.GetScrollPixelsPerUnit()

        if unit_y <= 0:
            unit_y = 1

        parent.Scroll(
            -1,
            max(0, (ctrl_pos.y - margin) // unit_y)
        )

        if ctrl.AcceptsFocus():
            wx.CallAfter(ctrl.SetFocus)

    def update_buttons(self):
        modified = bool(self.modified_settings)

        self.m_buttonApply.Enable(modified)
        self.m_buttonLocalReset.Enable(modified)

    def on_search_enter(self, event):
        text = self.m_searchCtrl.GetValue().lower()
        title = text.split(" (", 1)[0]
        
        for item in self.ide_cfg.settings_index:

            if item["title"].lower() == title:
                self.open_setting(item["path"])
                return

    def register_setting(self,ctrl,path,page):
        self.setting_controls[path] = ctrl
        self.control_to_path[ctrl] = path
        self.path_to_page[path] = page

        if isinstance(ctrl, wx.CheckBox):
            ctrl.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)

        elif isinstance(ctrl, wx.SpinCtrl):
            ctrl.Bind(wx.EVT_SPINCTRL, self.on_setting_changed)
            ctrl.Bind(wx.EVT_TEXT, self.on_setting_changed)

        elif isinstance(ctrl, wx.Choice):
            ctrl.Bind(wx.EVT_CHOICE, self.on_setting_changed)

        elif isinstance(ctrl, wx.TextCtrl):
            ctrl.Bind(wx.EVT_TEXT, self.on_setting_changed)

        elif isinstance(ctrl, wx.ColourPickerCtrl):
            ctrl.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_setting_changed)

        elif isinstance(ctrl, wx.FilePickerCtrl):
            ctrl.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_setting_changed)

        ctrl.SetToolTip(
            self.ide_cfg.get_setting_description(path)
        )

    def _set_control_value(self, ctrl, value):
        if isinstance(ctrl, wx.CheckBox):
            ctrl.SetValue(bool(value))

        elif isinstance(ctrl, wx.SpinCtrl):
            ctrl.SetValue(int(value))

        elif isinstance(ctrl, wx.TextCtrl):
            ctrl.SetValue(str(value))

        elif isinstance(ctrl, wx.Choice):
            ctrl.SetStringSelection(str(value))

        elif isinstance(ctrl, wx.ColourPickerCtrl):
            ctrl.SetColour(wx.Colour(value))

        elif isinstance(ctrl, wx.FilePickerCtrl):
            ctrl.SetPath(value)

    def _get_control_value(self, ctrl):
        if isinstance(ctrl, wx.CheckBox):
            return ctrl.GetValue()

        if isinstance(ctrl, wx.SpinCtrl):
            return ctrl.GetValue()

        if isinstance(ctrl, wx.TextCtrl):
            return ctrl.GetValue()

        if isinstance(ctrl, wx.Choice):
            return ctrl.GetStringSelection()

        if isinstance(ctrl, wx.ColourPickerCtrl):
            return ctrl.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)

        if isinstance(ctrl, wx.FilePickerCtrl):
            return ctrl.GetPath()

        return None

    def on_setting_changed(self, event):
        if getattr(self, "_loading_settings", False):
            return
        
        ctrl = event.GetEventObject()

        path = self.control_to_path.get(ctrl)

        if not path:
            event.Skip()
            return

        value = self._get_control_value(ctrl)

        self.ide_cfg._set_in_dict(
            self.working_config,
            path,
            value
        )

        #
        # Проверяем действительно ли изменилось
        #

        old_value = self.ide_cfg._get_from_dict(
            self.original_config,
            path
        )

        if value == old_value:

            self.modified_settings.discard(path)

        else:

            self.modified_settings.add(path)

        self.update_buttons()

        event.Skip()

    def open_setting(self, path):
        page = self.path_to_page[path]

        ctrl = self.setting_controls[path]
        
        self.m_simplebook.SetSelection(
            self.m_simplebook.FindPage(page)
        )

        self.scroll_to_control(ctrl)

    def m_splitter_MainOnIdle( self, event ):
        self.m_splitter_Main.SetSashPosition( 230 )
        self.m_splitter_Main.Unbind( wx.EVT_IDLE )


