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

import wx
import wx.xrc
import wx.aui
import wx.richtext
import wx.stc

import os
import sys

import gettext
_ = gettext.gettext

wx.ID_TOOLBAR_OPEN_FILE = 6000
wx.ID_TOOLBAR_SAVE_ALL = 6001
wx.ID_TOOLBAR_BUILD_PROJECT = 6002
wx.ID_TOOLBAR_RUN_STOP_SERVER = 6003
wx.ID_NEW_PROJECT = 6005
wx.ID_NEW_FILE = 6006
wx.ID_OPEN_FILE = 6007
wx.ID_OPEN_SERVER_FOLDER = 6008
wx.ID_SAVE_ALL = 6009
wx.ID_FIND_REPLACE = 6010
wx.ID_GO_TO_LINE = 6011
wx.ID_QUICK_OUTLINE = 6012
wx.ID_FULLSCREEN = 6013
wx.ID_TOGGLE_ZEN_MODE = 6014
wx.ID_TOGGLE_PROJECT_PANEL = 6015
wx.ID_TOGGLE_OUTPUT_PANEL = 6016
wx.ID_TOGGLE_MINIMAP = 6017
wx.ID_TOGGLE_TOOLBAR = 6018
wx.ID_TOGGLE_STATUSBAR = 6019
wx.ID_RESET_ZOOM = 6020
wx.ID_BUILD_PROJECT = 6021
wx.ID_BUILD_AND_RUN = 6022
wx.ID_CLEAN_PROJECT = 6023
wx.ID_SETTINGS = 6024
wx.ID_DONATE = 6026

wx.ID_MINIMAP_NARROW = 6037
wx.ID_MINIMAP_NORMAL = 6038
wx.ID_MINIMAP_WIDE = 6039
wx.ID_MINIMAP_HIDE = 6040

wx.ID_SAMPCTL_DEPENDENCIES_MANAGER = 6041
wx.ID_PROJECT_SETTINGS = 6042
wx.ID_SAVE = 6043
wx.ID_CLOSE_PROJECT = 6044
wx.ID_TOOLBAR_LINTER_RUN = 6045
wx.ID_ZOOM_IN = 6046
wx.ID_ZOOM_OUT = 6047
wx.ID_CUT = 6048
wx.ID_COPY = 6049
wx.ID_PASTE = 6050
wx.ID_UNDO = 6051
wx.ID_REDO = 6052
wx.ID_TOOLBAR_NEW_FILE = 6053
wx.ID_EXIT = 6054
wx.ID_EOL_CRLF = 6057
wx.ID_EOL_LF = 6058

wx.ID_GIT_COMMIT = 6059
wx.ID_GIT_DISCARD_ALL = 6060
wx.ID_GIT_REFRESH = 6062
wx.ID_GIT_STAGE_ALL = 6055
wx.ID_GIT_UNSTAGE_ALL = 6056
wx.ID_GIT_COMMIT_HISTORY = 6064
wx.ID_GIT_TERMINAL = 6065

wx.ID_RUN_STOP_SERVER = 6063
wx.ID_SELECT_ALL = 6066
wx.ID_RESET_SETTINGS = 6067

wx.ID_LANGUAGE_ENGLISH = 6072
wx.ID_LANGUAGE_RUSSIAN = 6073

wx.ID_REOPEN_TO_UTF8 = 6068
wx.ID_REOPEN_TO_CP1251 = 6069
wx.ID_REOPEN_TO_CP1250 = 6070
wx.ID_REOPEN_TO_CP1252 = 6071
wx.ID_REOPEN_TO_CP1253 = 6079
wx.ID_REOPEN_TO_CP1254 = 6075
wx.ID_REOPEN_TO_CP1255 = 6076
wx.ID_REOPEN_TO_CP1256 = 6077
wx.ID_REOPEN_TO_CP1257 = 6078

wx.ID_SET_TO_UTF8 = 6080
wx.ID_SET_TO_CP1251 = 6081
wx.ID_SET_TO_CP1250 = 6082
wx.ID_SET_TO_CP1252 = 6083
wx.ID_SET_TO_CP1253 = 6084
wx.ID_SET_TO_CP1254 = 6085
wx.ID_SET_TO_CP1255 = 6086
wx.ID_SET_TO_CP1256 = 6087
wx.ID_SET_TO_CP1257 = 6088

wx.ID_TOOLBAR_SAVE = 6089

wx.ID_TOGGLE_COMMENT = 6090
wx.ID_TOGGLE_BLOCK_COMMENT = 6091

wx.ID_MOVE_LINE_UP = 6092
wx.ID_MOVE_LINE_DOWN = 6093

wx.ID_SELECT_ALL = 6094

wx.ID_DUPLICATE_LINE = 6095
wx.ID_DELETE_LINE = 6096

wx.ID_CLOSE_CURRENT_FILE = 6097

wx.ID_BUG_REPORT = 6074

def get_app_root_dir():
    if 'NUITKA_ONEFILE_PARENT' in os.environ or getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))

    ui_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(ui_dir)

APP_ROOT = get_app_root_dir()

class SpawnFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Spawn"), pos = wx.DefaultPosition, size = wx.Size( 1289,760 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        icon = wx.Icon(os.path.join(APP_ROOT, "assets", "spawn.ico"), wx.BITMAP_TYPE_ICO) 
        self.SetIcon(icon)
        
        self.SetSizeHints( wx.Size(800, 600), wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.icons_folder = os.path.join(APP_ROOT, "assets", "icons")

        self.m_auiToolBar = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT|wx.aui.AUI_TB_PLAIN_BACKGROUND )
        
        self.m_tool_NewFile = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_NEW_FILE, _(u"New File"), wx.Bitmap(os.path.join(self.icons_folder,"tb_file_new.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"New File"), wx.EmptyString, None )
        
        self.m_tool_OpenFile = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_OPEN_FILE, _(u"Open File..."), wx.Bitmap(os.path.join(self.icons_folder,"tb_open.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Open File..."), wx.EmptyString, None )

        self.m_tool_Save = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_SAVE, _(u"Save"), wx.Bitmap(os.path.join(self.icons_folder,"tb_save.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Save"), wx.EmptyString, None )

        self.m_tool_SaveAll = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_SAVE_ALL, _(u"Save All"), wx.Bitmap(os.path.join(self.icons_folder,"tb_saveall.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Save All"), wx.EmptyString, None )

        self.m_auiToolBar.AddSeparator()

        self.m_tool_CompileProject = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_BUILD_PROJECT, _(u"Build Server"), wx.Bitmap(os.path.join(self.icons_folder,"tb_project_build.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Build Server"), wx.EmptyString, None )

        m_choice_BuildsChoices = []
        self.m_choice_Builds = wx.Choice( self.m_auiToolBar, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_BuildsChoices, 0 )
        self.m_choice_Builds.SetSelection( 0 )
        self.m_choice_Builds.SetMinSize( wx.Size( 180,-1 ) )
        self.m_choice_Builds.SetMaxSize( wx.Size( 300,-1 ) )
        #self.m_auiToolBar.AddControl( self.m_choice_Builds )
        self.m_choice_Builds.Hide()

        self.m_tool_RunServer = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_RUN_STOP_SERVER, _(u"Run / Stop Server"), wx.Bitmap(os.path.join(self.icons_folder,"tb_server_run.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Run / Stop Server"), wx.EmptyString, None )

        #self.m_tool_RunLinter = self.m_auiToolBar.AddTool( wx.ID_TOOLBAR_LINTER_RUN, _(u"Verify code"), wx.Bitmap( u"assets/icons/tb_linter_run.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Verify code"), wx.EmptyString, None )
##        self.m_auiToolBar.AddStretchSpacer(1)
##        self.m_infoCtrl = wx.InfoBar( self.m_auiToolBar )
##        self.m_infoCtrl.SetMinSize(wx.Size(500, -1))
##        self.m_infoCtrl.SetShowHideEffects( wx.SHOW_EFFECT_SLIDE_TO_LEFT, wx.SHOW_EFFECT_SLIDE_TO_RIGHT )
##        self.m_infoCtrl.SetEffectDuration( 300 )
##        self.m_auiToolBar.AddControl( self.m_infoCtrl )

        self.m_auiToolBar.Realize()
        self.m_mgr.AddPane( self.m_auiToolBar, wx.aui.AuiPaneInfo() .Top() .CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).Movable( False ).Dock().Resizable().FloatingSize( wx.Size( 43,219 ) ).DockFixed( True ).BottomDockable( False ).LeftDockable( False ).RightDockable( False ).Floatable( False ).Layer( 10 ) )

        self.m_menubar = wx.MenuBar( 0 )
        self.m_file = wx.Menu()
        self.m_menuItem_NewProject = wx.MenuItem( self.m_file, wx.ID_NEW_PROJECT, _(u"New Project..."), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_NewProject )

        self.m_menuItem_NewFile = wx.MenuItem( self.m_file, wx.ID_NEW_FILE, _(u"New File")+ u"\t" + u"Ctrl+N", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_NewFile )

        self.m_file.AppendSeparator()

        self.m_menuItem_OpenFile = wx.MenuItem( self.m_file, wx.ID_OPEN_FILE, _(u"Open File...")+ u"\t" + u"Ctrl+O", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_OpenFile )

        self.m_menuItem_OpenProjectFolder = wx.MenuItem( self.m_file, wx.ID_OPEN_SERVER_FOLDER, _(u"Open Server Folder...")+ u"\t" + u"Ctrl+Shift+O", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_OpenProjectFolder )

        self.recent_files_submenu = wx.Menu()
        self.m_file.AppendSubMenu(self.recent_files_submenu, _(u"Open Recent"), wx.EmptyString)

        self.m_file.AppendSeparator()

        self.m_menuItem_Save = wx.MenuItem( self.m_file, wx.ID_SAVE, _(u"Save")+ u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_Save )

        self.m_menuItem_SaveAll = wx.MenuItem( self.m_file, wx.ID_SAVE_ALL, _(u"Save All")+ u"\t" + u"Ctrl+Shift+S", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_SaveAll )

        self.m_file.AppendSeparator()

        self.m_menuItem_CloseFile = wx.MenuItem( self.m_file, wx.ID_CLOSE_CURRENT_FILE, _(u"Close")+ u"\t" + u"Ctrl+W", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_CloseFile )

        self.m_file.AppendSeparator()

        self.m_menuItem_Exit = wx.MenuItem( self.m_file, wx.ID_EXIT, _(u"Exit")+ u"\t" + u"Alt+F4", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_file.Append( self.m_menuItem_Exit )

        self.m_menubar.Append( self.m_file, _(u"File") )

        self.m_edit = wx.Menu()
        self.m_menuItem_Undo = wx.MenuItem( self.m_edit, wx.ID_UNDO, _(u"Undo")+ u"\t" + u"Ctrl+Z", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_Undo )

        self.m_menuItem_Redo = wx.MenuItem( self.m_edit, wx.ID_REDO, _(u"Redo")+ u"\t" + u"Ctrl+Y", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_Redo )

        self.m_edit.AppendSeparator()

        self.m_menuItem_Cut = wx.MenuItem( self.m_edit, wx.ID_CUT, _(u"Cut")+ u"\t" + u"Ctrl+X", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_Cut )

        self.m_menuItem_Copy = wx.MenuItem( self.m_edit, wx.ID_COPY, _(u"Copy")+ u"\t" + u"Ctrl+C", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_Copy )

        self.m_menuItem_Paste = wx.MenuItem( self.m_edit, wx.ID_PASTE, _(u"Paste")+ u"\t" + u"Ctrl+V", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_Paste )

        self.m_edit.AppendSeparator()

        self.m_menuItem_SelectAll = wx.MenuItem( self.m_edit, wx.ID_SELECT_ALL, _(u"Select All")+ u"\t" + u"Ctrl+A", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_SelectAll )

        self.m_edit.AppendSeparator()

        self.m_menuItem_FindReplace = wx.MenuItem( self.m_edit, wx.ID_FIND_REPLACE, _(u"Find / Replace...")+ u"\t" + u"Ctrl+F", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_FindReplace )

        self.m_menuItem_GoToLine = wx.MenuItem( self.m_edit, wx.ID_GO_TO_LINE, _(u"Go to Line...")+ u"\t" + u"Ctrl+G", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_GoToLine )

        self.m_edit.AppendSeparator()

        self.m_menuItem_ToggleComment = wx.MenuItem( self.m_edit, wx.ID_TOGGLE_COMMENT, _(u"Toggle Line Comment")+ u"\t" + u"Ctrl+/", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_ToggleComment )

        self.m_menuItem_ToggleBlockComment = wx.MenuItem( self.m_edit, wx.ID_TOGGLE_BLOCK_COMMENT, _(u"Toggle Block Comment")+ u"\t" + u"Ctrl+Alt+A", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_ToggleBlockComment )

        self.m_edit.AppendSeparator()

        self.m_menuItem_MoveLineUp = wx.MenuItem( self.m_edit, wx.ID_MOVE_LINE_UP, _(u"Move Line Up")+ u"\t" + u"Alt+Up", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_MoveLineUp)

        self.m_menuItem_MoveLineDown = wx.MenuItem( self.m_edit, wx.ID_MOVE_LINE_DOWN, _(u"Move Line Down")+ u"\t" + u"Alt+Down", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_MoveLineDown)

        self.m_menuItem_DuplicateLine = wx.MenuItem( self.m_edit, wx.ID_DUPLICATE_LINE, _(u"Duplicate Line")+ u"\t" + u"Ctrl+D", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_DuplicateLine)

        self.m_menuItem_DeleteLine = wx.MenuItem( self.m_edit, wx.ID_DELETE_LINE, _(u"Delete Line")+ u"\t" + u"Ctrl+Shift+K", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_edit.Append( self.m_menuItem_DeleteLine)

        #self.m_menuItem_QuickOutline = wx.MenuItem( self.m_edit, wx.ID_QUICK_OUTLINE, _(u"Quick Outline...")+ u"\t" + u"Ctrl+P", wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_edit.Append( self.m_menuItem_QuickOutline )
        self.m_edit.AppendSeparator()

        encoding_submenu = wx.Menu()
        self.m_edit.AppendSubMenu(encoding_submenu, _(u"Encoding"), wx.EmptyString)
        encoding_reopen_submenu = wx.Menu()
        self.item_reopen_to_utf8 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_UTF8, u"UTF-8 (Unicode)")
        self.item_reopen_to_cp1250 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1250, u"Windows-1250 (Central European)")
        self.item_reopen_to_cp1251 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1251, u"Windows-1251 (Cyrillic)")
        self.item_reopen_to_cp1252 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1252, u"Windows-1252 (Western European)")
        self.item_reopen_to_cp1253 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1253, u"Windows-1253 (Greek)")
        self.item_reopen_to_cp1254 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1254, u"Windows-1254 (Turkish)")
        self.item_reopen_to_cp1255 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1255, u"Windows-1255 (Hebrew)")
        self.item_reopen_to_cp1256 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1256, u"Windows-1256 (Arabic)")
        self.item_reopen_to_cp1257 = encoding_reopen_submenu.Append(wx.ID_REOPEN_TO_CP1257, u"Windows-1257 (Baltic)")
        encoding_submenu.AppendSubMenu(encoding_reopen_submenu, _(u"Reopen"), wx.EmptyString)
        
##        encoding_convert_submenu = wx.Menu()
##        self.item_convert_to_utf8 = encoding_convert_submenu.Append(wx.ID_CONVERT_TO_UTF8, _(u"UTF-8"))
##        self.item_convert_to_cp1251 = encoding_convert_submenu.Append(wx.ID_CONVERT_TO_CP1251, _(u"Windows-1251 (CP1251)"))
##        encoding_submenu.AppendSubMenu(encoding_convert_submenu, _(u"Convert"), wx.EmptyString)

        eol_submenu = wx.Menu()
        self.item_crlf = eol_submenu.AppendRadioItem(wx.ID_EOL_CRLF, u"Windows (CRLF)")
        self.item_lf = eol_submenu.AppendRadioItem(wx.ID_EOL_LF, u"Unix (LF)")
        self.m_edit.AppendSubMenu(eol_submenu, _(u"Line Endings"), wx.EmptyString)
        self.m_menubar.Append( self.m_edit, _(u"Edit") )

        self.m_view = wx.Menu()
        self.m_menuItem_FullScreen = wx.MenuItem( self.m_view, wx.ID_FULLSCREEN, _(u"Full Screen")+ u"\t" + u"F11", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_FullScreen )

        self.m_menuItem_ZenMode = wx.MenuItem( self.m_view, wx.ID_TOGGLE_ZEN_MODE, _(u"Toggle Zen Mode")+ u"\t" + u"Ctrl+K", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ZenMode )

        self.m_view.AppendSeparator()
        self.m_menuItem_ToggleToolbar = wx.MenuItem( self.m_view, wx.ID_TOGGLE_TOOLBAR, _(u"Toggle Toolbar")+ u"\t" + u"Ctrl+1", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ToggleToolbar )

        self.m_menuItem_ToggleStatusbar = wx.MenuItem( self.m_view, wx.ID_TOGGLE_STATUSBAR, _(u"Toggle StatusBar")+ u"\t" + u"Ctrl+2", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ToggleStatusbar )

        self.m_menuItem_ToggleProjectPanel = wx.MenuItem( self.m_view, wx.ID_TOGGLE_PROJECT_PANEL, _(u"Toggle Project Panel")+ u"\t" + u"Ctrl+3", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ToggleProjectPanel )

        self.m_menuItem_ToggleOutputPanel = wx.MenuItem( self.m_view, wx.ID_TOGGLE_OUTPUT_PANEL, _(u"Toggle Output Panel")+ u"\t" + u"Ctrl+4", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ToggleOutputPanel )

        #self.m_menuItem_ToggleMinimap = wx.MenuItem( self.m_view, wx.ID_TOGGLE_MINIMAP, _(u"Toggle Minimap"), wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_view.Append( self.m_menuItem_ToggleMinimap )

        #self.m_menuItem_ToggleStatusBar = wx.MenuItem( self.m_view, wx.ID_TOGGLE_STATUSBAR, _(u"Toggle Status Bar"), wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_view.Append( self.m_menuItem_ToggleStatusBar )

        self.m_view.AppendSeparator()

        self.m_menuItem_ZoomIn = wx.MenuItem( self.m_view, wx.ID_ZOOM_IN, _(u"Zoom In")+ u"\t" + u"Ctrl+=", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ZoomIn )

        self.m_menuItem_ZoomOut = wx.MenuItem( self.m_view, wx.ID_ZOOM_OUT, _(u"Zoom Out")+ u"\t" + u"Ctrl+-", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ZoomOut )

        self.m_menuItem_ResetZoom = wx.MenuItem( self.m_view, wx.ID_RESET_ZOOM, _(u"Reset Zoom")+ u"\t" + u"Ctrl+0", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_view.Append( self.m_menuItem_ResetZoom )

        self.m_menubar.Append( self.m_view, _(u"View") )

        self.m_project = wx.Menu()
        self.m_menuItem_Ensure = wx.MenuItem( self.m_project, wx.ID_SAMPCTL_DEPENDENCIES_MANAGER, _(u"Dependency Manager..."), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_project.Append( self.m_menuItem_Ensure )

        self.m_project.AppendSeparator()

        #self.m_menuItem_ProjectSettings = wx.MenuItem( self.m_project, wx.ID_PROJECT_SETTINGS, _(u"Project Settings..."), wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_project.Append( self.m_menuItem_ProjectSettings )

        self.m_menuItem_ProjectClose = wx.MenuItem( self.m_project, wx.ID_CLOSE_PROJECT, _(u"Close Project"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_project.Append( self.m_menuItem_ProjectClose )

        self.m_menubar.Append( self.m_project, _(u"Project") )

        self.m_build = wx.Menu()
        self.m_menuItem_CompileProject = wx.MenuItem( self.m_build, wx.ID_BUILD_PROJECT, _(u"Build Server")+ u"\t" + u"F5", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_build.Append( self.m_menuItem_CompileProject )

        #self.m_menuItem_CompileAndRun = wx.MenuItem( self.m_build, wx.ID_BUILD_AND_RUN, _(u"Build and Run")+ u"\t" + u"Ctrl+F5", wx.EmptyString, wx.ITEM_NORMAL )
        #self.m_build.Append( self.m_menuItem_CompileAndRun )

##        self.m_build.AppendSeparator()
##
##        self.m_menuItem_CleanProject = wx.MenuItem( self.m_build, wx.ID_CLEAN_PROJECT, _(u"Clean Project"), wx.EmptyString, wx.ITEM_NORMAL )
##        self.m_build.Append( self.m_menuItem_CleanProject )

        self.m_menubar.Append( self.m_build, _(u"Build") )

        self.m_server = wx.Menu()
        self.m_menuItem_RunStopServer = wx.MenuItem( self.m_server, wx.ID_RUN_STOP_SERVER, _(u"Run / Stop Server")+ u"\t" + u"F6", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_server.Append( self.m_menuItem_RunStopServer )
        self.m_menubar.Append( self.m_server, _(u"Server") )

        

        self.m_tools = wx.Menu()

##        language_submenu = wx.Menu()
##        self.item_english = language_submenu.AppendRadioItem(wx.ID_LANGUAGE_ENGLISH, u"English")
##        self.item_russian = language_submenu.AppendRadioItem(wx.ID_LANGUAGE_RUSSIAN, u"Русский")
##        self.m_tools.AppendSubMenu(language_submenu, _(u"Language"), wx.EmptyString)

##        self.m_tools.AppendSeparator()

        def_encoding_submenu = wx.Menu()
        self.m_tools.AppendSubMenu(def_encoding_submenu, _(u"Default Encoding"), wx.EmptyString)
        def_encoding_set_submenu = wx.Menu()
        self.item_set_to_utf8 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_UTF8, u"UTF-8 (Unicode)")
        self.item_set_to_cp1250 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1250, u"Windows-1250 (Central European)")
        self.item_set_to_cp1251 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1251, u"Windows-1251 (Cyrillic)")
        self.item_set_to_cp1252 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1252, u"Windows-1252 (Western European)")
        self.item_set_to_cp1253 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1253, u"Windows-1253 (Greek)")
        self.item_set_to_cp1254 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1254, u"Windows-1254 (Turkish)")
        self.item_set_to_cp1255 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1255, u"Windows-1255 (Hebrew)")
        self.item_set_to_cp1256 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1256, u"Windows-1256 (Arabic)")
        self.item_set_to_cp1257 = def_encoding_set_submenu.AppendRadioItem(wx.ID_SET_TO_CP1257, u"Windows-1257 (Baltic)")
        def_encoding_submenu.AppendSubMenu(def_encoding_set_submenu, u"Pawn", wx.EmptyString)

        self.m_tools.AppendSeparator()
        
        self.m_menuItem_Settings = wx.MenuItem( self.m_tools, wx.ID_SETTINGS, _(u"Settings..."), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_tools.Append( self.m_menuItem_Settings )
        self.m_menuItem_ResetSettings = wx.MenuItem( self.m_tools, wx.ID_RESET_SETTINGS, _(u"Reset Settings"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_tools.Append( self.m_menuItem_ResetSettings )

        self.m_menubar.Append( self.m_tools, _(u"Tools") )

        self.m_help = wx.Menu()

        self.m_menuItem_BugReport = wx.MenuItem( self.m_help, wx.ID_BUG_REPORT, _(u"Bug Report"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help.Append( self.m_menuItem_BugReport )

        self.m_help.AppendSeparator()

        self.m_menuItem_Donate = wx.MenuItem( self.m_help, wx.ID_DONATE, _(u"Donate"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help.Append( self.m_menuItem_Donate )

        self.m_menuItem_About = wx.MenuItem( self.m_help, wx.ID_ABOUT, _(u"About"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_help.Append( self.m_menuItem_About )

        self.m_menubar.Append( self.m_help, _(u"Help") )

        self.SetMenuBar( self.m_menubar )

        #Status Bar
        self.m_statusBar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.SetStatusBarPane(-1)
        
        self.m_projectPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        
        self.m_mgr.AddPane( self.m_projectPanel, wx.aui.AuiPaneInfo() .Left() .Caption( _(u"Project") ).Dock().Resizable().FloatingSize( wx.Size( 260,59 ) ).BottomDockable( False ).TopDockable( False ).BestSize( wx.Size( 260,-1 ) ).MinSize( wx.Size( 170,-1 ) ).Layer( 5 ) )
        self.pane_left = self.m_mgr.GetPane(self.m_projectPanel)
        self.pane_left.Hide()
        bSizer_ProjectPanel = wx.BoxSizer( wx.VERTICAL )

        self.m_splitter_ProjectPanel = wx.SplitterWindow( self.m_projectPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_LIVE_UPDATE )
        self.m_splitter_ProjectPanel.Bind( wx.EVT_IDLE, self.m_splitter_ProjectPanelOnIdle )
        self.m_splitter_ProjectPanel.SetMinimumPaneSize(260)

        self.m_panel_splitter_ProjectTree = wx.Panel( self.m_splitter_ProjectPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_splitter_ProjectTree = wx.BoxSizer( wx.VERTICAL )

        self.m_treeCtrl_ProjectTree = wx.TreeCtrl( self.m_panel_splitter_ProjectTree, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_TWIST_BUTTONS )
        bSizer_splitter_ProjectTree.Add( self.m_treeCtrl_ProjectTree, 1, wx.EXPAND, 0 )


        self.m_panel_splitter_ProjectTree.SetSizer( bSizer_splitter_ProjectTree )
        self.m_panel_splitter_ProjectTree.Layout()
        bSizer_splitter_ProjectTree.Fit( self.m_panel_splitter_ProjectTree )
        self.m_panel_splitter_ProjectTools = wx.Panel( self.m_splitter_ProjectPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_splitter_ProjectTools = wx.BoxSizer( wx.VERTICAL )

        self.m_auinotebook_splitter_ProjectTools = wx.aui.AuiNotebook( self.m_panel_splitter_ProjectTools, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
##        self.m_panel_SymbolsTab = wx.Panel( self.m_auinotebook_splitter_ProjectTools, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
##        bSizer_SymbolsTab = wx.BoxSizer( wx.VERTICAL )
##
##        self.m_treeCtrl_Symbols = wx.TreeCtrl( self.m_panel_SymbolsTab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_TWIST_BUTTONS )
##        self.m_treeCtrl_Symbols.Enable(False) #Временно
##        bSizer_SymbolsTab.Add( self.m_treeCtrl_Symbols, 1, wx.EXPAND, 0 )
##
##
##        self.m_panel_SymbolsTab.SetSizer( bSizer_SymbolsTab )
##        self.m_panel_SymbolsTab.Layout()
##        bSizer_SymbolsTab.Fit( self.m_panel_SymbolsTab )
##        self.m_auinotebook_splitter_ProjectTools.AddPage( self.m_panel_SymbolsTab, _(u"Symbols"), False, wx.NullBitmap )
##
        bSizer_splitter_ProjectTools.Add( self.m_auinotebook_splitter_ProjectTools, 1, wx.EXPAND, 0 )

        self.m_panel_splitter_ProjectTools.SetSizer( bSizer_splitter_ProjectTools )
        self.m_panel_splitter_ProjectTools.Layout()
        bSizer_splitter_ProjectTools.Fit( self.m_panel_splitter_ProjectTools )
        self.m_splitter_ProjectPanel.SplitHorizontally( self.m_panel_splitter_ProjectTree, self.m_panel_splitter_ProjectTools, 200 )
        bSizer_ProjectPanel.Add( self.m_splitter_ProjectPanel, 1, wx.EXPAND, 0 )

        self.m_projectPanel.SetSizer( bSizer_ProjectPanel )
        self.m_projectPanel.Layout()
        bSizer_ProjectPanel.Fit( self.m_projectPanel )
        
        self.m_outputPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_outputPanel, wx.aui.AuiPaneInfo() .Bottom() .Caption( _(u"Output") ).Dock().Resizable().FloatingSize( wx.Size( 42,239 ) ).LeftDockable( False ).RightDockable( False ).Row( 1 ).BestSize( wx.Size( -1,200 ) ).MinSize( wx.Size( -1,120 ) ) )

        self.pane_bottom = self.m_mgr.GetPane(self.m_outputPanel)
        self.pane_bottom.Hide()

        self.m_outputPanel.Hide()
        bSizer_OutputPanel = wx.BoxSizer( wx.VERTICAL )

        self.m_auinotebook_Output = wx.aui.AuiNotebook( self.m_outputPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_TAB_MOVE )
        self.m_panel_BuildTab = wx.Panel( self.m_auinotebook_Output, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_BuildTab = wx.BoxSizer( wx.VERTICAL )

        self.m_richText_BuildOutput = wx.richtext.RichTextCtrl( self.m_panel_BuildTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
        self.m_richText_BuildOutput.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        bSizer_BuildTab.Add( self.m_richText_BuildOutput, 1, wx.EXPAND, 5 )


        self.m_panel_BuildTab.SetSizer( bSizer_BuildTab )
        self.m_panel_BuildTab.Layout()
        bSizer_BuildTab.Fit( self.m_panel_BuildTab )
        self.m_auinotebook_Output.AddPage( self.m_panel_BuildTab, _(u"Build"), True, wx.Bitmap(os.path.join(self.icons_folder,"bo_build_info.png"), wx.BITMAP_TYPE_ANY ) )
##        self.m_panel_ErrorsTab = wx.Panel( self.m_auinotebook_Output, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
##        bSizer_ErrorsTab = wx.BoxSizer( wx.VERTICAL )
##
##        self.m_listCtrl_Errors = wx.ListCtrl( self.m_panel_ErrorsTab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL )
##        bSizer_ErrorsTab.Add( self.m_listCtrl_Errors, 1, wx.EXPAND, 5 )
##
##
##        self.m_panel_ErrorsTab.SetSizer( bSizer_ErrorsTab )
##        self.m_panel_ErrorsTab.Layout()
##        bSizer_ErrorsTab.Fit( self.m_panel_ErrorsTab )
##        self.m_auinotebook_Output.AddPage( self.m_panel_ErrorsTab, _(u"Errors"), False, wx.Bitmap( u"assets/icons/bo_error.png", wx.BITMAP_TYPE_ANY ) )
##        self.m_panel_WarningsTab = wx.Panel( self.m_auinotebook_Output, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
##        bSizer_WarningsTab = wx.BoxSizer( wx.VERTICAL )
##
##        self.m_listCtrl_Warnings = wx.ListCtrl( self.m_panel_WarningsTab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL )
##        bSizer_WarningsTab.Add( self.m_listCtrl_Warnings, 1, wx.EXPAND, 5 )
##
##
##        self.m_panel_WarningsTab.SetSizer( bSizer_WarningsTab )
##        self.m_panel_WarningsTab.Layout()
##        bSizer_WarningsTab.Fit( self.m_panel_WarningsTab )
##        self.m_auinotebook_Output.AddPage( self.m_panel_WarningsTab, _(u"Warnings"), False, wx.Bitmap( u"assets/icons/bo_warning.png", wx.BITMAP_TYPE_ANY ) )
        self.m_panel_ServerTab = wx.Panel( self.m_auinotebook_Output, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_ServerTab = wx.BoxSizer( wx.VERTICAL )

        self.m_richText_ServerConsole = wx.richtext.RichTextCtrl( self.m_panel_ServerTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
        self.m_richText_ServerConsole.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
      
        #self.m_richText_ServerConsole.SetBackgroundColour( wx.Colour( 0, 0, 0 ) )

        bSizer_ServerTab.Add( self.m_richText_ServerConsole, 1, wx.EXPAND, 5 )


        self.m_panel_ServerTab.SetSizer( bSizer_ServerTab )
        self.m_panel_ServerTab.Layout()
        bSizer_ServerTab.Fit( self.m_panel_ServerTab )
        self.m_auinotebook_Output.AddPage( self.m_panel_ServerTab, _(u"Server"), False, wx.Bitmap(os.path.join(self.icons_folder,"bo_server_console.png"), wx.BITMAP_TYPE_ANY ) )

        self.m_panel_Git = wx.Panel( self.m_auinotebook_splitter_ProjectTools, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_GitMain = wx.BoxSizer( wx.VERTICAL )

        bSizer_GitSubmain = wx.BoxSizer( wx.HORIZONTAL )

        self.m_auiToolBar_Git = wx.aui.AuiToolBar( self.m_panel_Git, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_VERTICAL )
        self.m_tool_GitRefresh = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_REFRESH, _(u"Refresh"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_refresh.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Refresh"), wx.EmptyString, None )
        self.m_auiToolBar_Git.AddSeparator()
        self.m_tool_GitStageAll = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_STAGE_ALL, _(u"Stage All"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_stage_all.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Stage All"), wx.EmptyString, None )
        self.m_tool_GitUnstageAll = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_UNSTAGE_ALL, _(u"Unstage All"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_unstage_all.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Unstage All"), wx.EmptyString, None )
        self.m_auiToolBar_Git.AddSeparator()
        self.m_tool_GitDiscardAll = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_DISCARD_ALL, _(u"Discard All"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_discard_all.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Discard All"), wx.EmptyString, None )

        self.m_auiToolBar_Git.AddStretchSpacer(1)
        
        self.m_tool_GitCommitHistory = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_COMMIT_HISTORY, _(u"Commit History"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_commit_history.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Commit History"), wx.EmptyString, None )

        self.m_auiToolBar_Git.AddSeparator()

        self.m_tool_GitTerminal = self.m_auiToolBar_Git.AddTool( wx.ID_GIT_TERMINAL, _(u"Git Terminal"), wx.Bitmap(os.path.join(self.icons_folder,"tb_git_terminal.png"), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Git Terminal"), wx.EmptyString, None )

        self.m_auiToolBar_Git.Realize()

        bSizer_GitSubmain.Add( self.m_auiToolBar_Git, 0, wx.EXPAND, 5 )

        bSizer_GitHistory = wx.BoxSizer( wx.VERTICAL )

        self.m_treeCtrl_GitHistory = wx.TreeCtrl( self.m_panel_Git, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.TR_TWIST_BUTTONS)
        bSizer_GitHistory.Add( self.m_treeCtrl_GitHistory, 1, wx.EXPAND, 5 )
        

        self.m_textCtrl_CommitText = wx.TextCtrl( self.m_panel_Git, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl_CommitText.SetHint(_(u"What has changed?"))
        bSizer_GitHistory.Add( self.m_textCtrl_CommitText, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_button_Commit = wx.Button( self.m_panel_Git, wx.ID_GIT_COMMIT, _(u"Commit"), wx.DefaultPosition, wx.DefaultSize, 0)

        bSizer_GitHistory.Add( self.m_button_Commit, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


        bSizer_GitSubmain.Add( bSizer_GitHistory, 1, wx.EXPAND, 5 )


        bSizer_GitMain.Add( bSizer_GitSubmain, 1, wx.EXPAND, 5 )


        self.m_panel_Git.SetSizer( bSizer_GitMain )
        self.m_panel_Git.Layout()
        bSizer_GitMain.Fit( self.m_panel_Git )
        self.m_auinotebook_splitter_ProjectTools.AddPage( self.m_panel_Git, _(u"Source Control"), True, wx.Bitmap(os.path.join(self.icons_folder,"nb_git_source_control_icon.png"),wx.BITMAP_TYPE_PNG))

        bSizer_OutputPanel.Add( self.m_auinotebook_Output, 1, wx.EXPAND, 5 )


        self.m_outputPanel.SetSizer( bSizer_OutputPanel )
        self.m_outputPanel.Layout()
        bSizer_OutputPanel.Fit( self.m_outputPanel )

        #Code Editor Notebook
        self.m_auinotebook_Main = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_CLOSE_ON_ALL_TABS|wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_SPLIT)
        self.m_mgr.AddPane( self.m_auinotebook_Main, wx.aui.AuiPaneInfo() .Center() .CaptionVisible( False ).PinButton( True ).Movable( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).BottomDockable( False ).TopDockable( False ).LeftDockable( False ).RightDockable( False ).Floatable( False ).Row( 1 ) )


        self.m_mgr.Update()
        self.Centre( wx.BOTH )

    def __del__( self ):
        self.m_mgr.UnInit()


    def m_splitter_ProjectPanelOnIdle( self, event ):
        self.m_splitter_ProjectPanel.SetSashPosition( 222 )
        self.m_splitter_ProjectPanel.Unbind( wx.EVT_IDLE )

    


class EditorTabPanel ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        # The panel is initialized independently and bound to the passed parent (notebook)
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer_EditorTab = wx.BoxSizer( wx.HORIZONTAL )

        self.m_scintilla_Editor = wx.stc.StyledTextCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_scintilla_Editor.SetUseTabs ( False )
        self.m_scintilla_Editor.SetTabWidth ( 4 )
        self.m_scintilla_Editor.SetIndent ( 4 )
        self.m_scintilla_Editor.SetTabIndents( True )
        self.m_scintilla_Editor.SetBackSpaceUnIndents( True )
        self.m_scintilla_Editor.SetViewEOL( False )
        self.m_scintilla_Editor.SetViewWhiteSpace( False )
      
        self.m_scintilla_Editor.SetIndentationGuides( False )
        self.m_scintilla_Editor.SetReadOnly( False )
        

        bSizer_EditorTab.Add( self.m_scintilla_Editor, 4, wx.EXPAND, 0 )

        self.m_scintilla_Minimap = wx.stc.StyledTextCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
     
        self.m_scintilla_Minimap.Hide()
        
        self.m_menuMinimap = wx.Menu()
        self.m_menuItem_Minimap_ZoomIn = wx.MenuItem( self.m_menuMinimap, wx.ID_ANY, u"Zoom In", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuMinimap.Append( self.m_menuItem_Minimap_ZoomIn )

        self.m_menuItem_Minimap_ZoomOut = wx.MenuItem( self.m_menuMinimap, wx.ID_ANY, u"Zoom Out", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuMinimap.Append( self.m_menuItem_Minimap_ZoomOut )

        self.m_menuItem_Minimap_ZoomReset = wx.MenuItem( self.m_menuMinimap, wx.ID_ANY, u"Zoom Reset", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuMinimap.Append( self.m_menuItem_Minimap_ZoomReset )

        self.m_menuMinimap.AppendSeparator()

        self.m_menu1 = wx.Menu()
        self.m_menuItem_Minimap_Narrow = wx.MenuItem( self.m_menu1, wx.ID_MINIMAP_NARROW, u"Narrow", wx.EmptyString, wx.ITEM_RADIO )
        self.m_menu1.Append( self.m_menuItem_Minimap_Narrow )

        self.m_menuItem_Minimap_Normal = wx.MenuItem( self.m_menu1, wx.ID_MINIMAP_NORMAL, u"Normal", wx.EmptyString, wx.ITEM_RADIO )
        self.m_menu1.Append( self.m_menuItem_Minimap_Normal )

        self.m_menuItem_Minimap_Wide = wx.MenuItem( self.m_menu1, wx.ID_MINIMAP_WIDE, u"Wide", wx.EmptyString, wx.ITEM_RADIO )
        self.m_menu1.Append( self.m_menuItem_Minimap_Wide )

        self.m_menuMinimap.AppendSubMenu( self.m_menu1, u"Width" )

        self.m_menuMinimap.AppendSeparator()

        self.m_menuItem_Minimap_Hide = wx.MenuItem( self.m_menuMinimap, wx.ID_MINIMAP_HIDE, u"Hide Minimap", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuMinimap.Append( self.m_menuItem_Minimap_Hide )

        self.m_scintilla_Minimap.Bind( wx.EVT_RIGHT_DOWN, self.m_scintilla_MinimapOnContextMenu )

        bSizer_EditorTab.Add( self.m_scintilla_Minimap, 1, wx.EXPAND, 0 )


        self.SetSizer( bSizer_EditorTab )
        self.Layout()
        bSizer_EditorTab.Fit( self )



    def m_scintilla_MinimapOnContextMenu( self, event ):
        self.m_scintilla_Minimap.PopupMenu( self.m_menuMinimap, event.GetPosition() )

