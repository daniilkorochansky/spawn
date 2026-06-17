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

import webbrowser
import os

from core.logger import SpawnLogger
from core.platform_utils import PlatformUtils
from core.version import __version__

import gettext
_ = gettext.gettext

class BugReportDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Bug Report"), pos = wx.DefaultPosition, size = wx.Size( 718,466 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_Logs = wx.BoxSizer( wx.VERTICAL )

        self.m_textCtrl_Logs = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        bSizer_Logs.Add( self.m_textCtrl_Logs, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer_Main.Add( bSizer_Logs, 1, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Main.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_Buttons = wx.BoxSizer( wx.HORIZONTAL )


        bSizer_Buttons.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_button_OpenIssues = wx.Button( self, wx.ID_ANY, _(u"Open GitHub Issues"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Buttons.Add( self.m_button_OpenIssues, 0, wx.ALL, 5 )
        self.m_button_OpenIssues.Bind(wx.EVT_BUTTON, self.on_issues)

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizer_Buttons.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_button_OpenFolder = wx.Button( self, wx.ID_ANY, _(u"Open Folder"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Buttons.Add( self.m_button_OpenFolder, 0, wx.ALL, 5 )
        self.m_button_OpenFolder.Bind(wx.EVT_BUTTON, self.on_open_logs_folder)

        self.m_button_CopyLogs = wx.Button( self, wx.ID_ANY, _(u"Copy"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Buttons.Add( self.m_button_CopyLogs, 0, wx.ALL, 5 )
        self.m_button_CopyLogs.Bind(wx.EVT_BUTTON, self.on_copy_logs)

        self.m_button_Close = wx.Button( self, wx.ID_ANY, _(u"Close"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_Close.SetDefault()
        bSizer_Buttons.Add( self.m_button_Close, 0, wx.ALL, 5 )
        self.m_button_Close.Bind(wx.EVT_BUTTON, self.on_close)


        bSizer_Main.Add( bSizer_Buttons, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer_Main )
        self.Layout()

        self.Centre( wx.BOTH )
        
        report = SpawnLogger.generate_bug_report(f"v{__version__}")
        self.m_textCtrl_Logs.SetValue(report)

    def on_copy_logs(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.m_textCtrl_Logs.GetValue()))
            wx.TheClipboard.Close()

            wx.MessageBox(_("Bug report copied to clipboard."),_("Spawn"),wx.OK | wx.ICON_INFORMATION)

    def on_open_logs_folder(self, event):
        log_dir = os.path.join(PlatformUtils.get_config_dir(),"logs")
        os.startfile(log_dir)

    def on_issues(self, event):
        webbrowser.open(u"https://github.com/daniilkorochansky/spawn/issues/new")

    def on_close(self, event):
        self.EndModal(wx.CANCEL)

    def __del__( self ):
        pass


