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
import wx.xrc

import gettext
_ = gettext.gettext

class NewProjectDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"New Project"), pos = wx.DefaultPosition, size = wx.Size( 640,290 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 640,290 ), wx.DefaultSize )

        bSizer_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_SubMain = wx.BoxSizer( wx.VERTICAL )

        bSizer_ProjectName = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_ProjectName = wx.StaticText( self, wx.ID_ANY, _(u"Project name:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_ProjectName.Wrap( -1 )

        bSizer_ProjectName.Add( self.m_staticText_ProjectName, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl_ProjectName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_ProjectName.Add( self.m_textCtrl_ProjectName, 1, wx.ALL, 5 )
        self.m_textCtrl_ProjectName.Bind(wx.EVT_TEXT,self.on_project_name_changed)

        bSizer_SubMain.Add( bSizer_ProjectName, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 15 )

        bSizer_ProjectLocation = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_ProjectLocation = wx.StaticText( self, wx.ID_ANY, _(u"Project location:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_ProjectLocation.Wrap( -1 )

        bSizer_ProjectLocation.Add( self.m_staticText_ProjectLocation, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_dirPicker_ProjectLocation = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a folder"), wx.DefaultPosition, wx.DefaultSize, wx.DIRP_CHANGE_DIR|wx.DIRP_DEFAULT_STYLE|wx.DIRP_SMALL )
        bSizer_ProjectLocation.Add( self.m_dirPicker_ProjectLocation, 1, wx.ALL, 5 )
        self.m_dirPicker_ProjectLocation.Bind(wx.EVT_DIRPICKER_CHANGED,self.on_location_changed)


        bSizer_SubMain.Add( bSizer_ProjectLocation, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 15 )

        bSizer_ProjectResult = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_ProjectResult = wx.StaticText( self, wx.ID_ANY, _(u"Result:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_ProjectResult.Wrap( -1 )

        bSizer_ProjectResult.Add( self.m_staticText_ProjectResult, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl_ProjectResult = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        bSizer_ProjectResult.Add( self.m_textCtrl_ProjectResult, 1, wx.ALL, 5 )


        bSizer_SubMain.Add( bSizer_ProjectResult, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 15 )

        self.m_staticTextSampctlInfo = wx.StaticText( self, wx.ID_ANY, _(u"Note: After clicking Create, the SAMPCTL command-line tool will be launched. Follow the on-screen instructions to complete project creation."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextSampctlInfo.Wrap( -1 )

        bSizer_SubMain.Add( self.m_staticTextSampctlInfo, 1, wx.ALL, 20 )


        bSizer_Main.Add( bSizer_SubMain, 1, wx.EXPAND, 5 )

        m_sdbSizerOkCancel = wx.StdDialogButtonSizer()
        self.m_sdbSizerOkCancelOK = wx.Button( self, wx.ID_OK )
        m_sdbSizerOkCancel.AddButton( self.m_sdbSizerOkCancelOK )
        self.m_sdbSizerOkCancelCancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizerOkCancel.AddButton( self.m_sdbSizerOkCancelCancel )
        m_sdbSizerOkCancel.Realize()

        bSizer_Main.Add( m_sdbSizerOkCancel, 0, wx.ALL|wx.EXPAND, 15 )


        self.SetSizer( bSizer_Main )
        self.Layout()

        self.Centre( wx.BOTH )

    def on_project_name_changed(self, event):
        self.update_result_path()
        event.Skip()

    def on_location_changed(self, event):
        self.update_result_path()
        event.Skip()

    def update_result_path(self):
        project_name = self.m_textCtrl_ProjectName.GetValue().strip()
        base_path = self.m_dirPicker_ProjectLocation.GetPath()

        result = os.path.join(base_path, project_name)

        self.m_textCtrl_ProjectResult.SetValue(result)

    def __del__( self ):
        pass


