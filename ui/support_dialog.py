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

import os
import sys
import webbrowser

import gettext
_ = gettext.gettext

def get_app_root_dir():
    if 'NUITKA_ONEFILE_PARENT' in os.environ or getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))

    ui_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(ui_dir)

APP_ROOT = get_app_root_dir()

class SupportDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Donate"), pos = wx.DefaultPosition, size = wx.Size( 460,464 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.Size( 460,464 ), wx.Size( 460,464 ) )

        bSizer19 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap_SpawnBanner = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap(os.path.join(APP_ROOT,"assets","banner.png"), wx.BITMAP_TYPE_PNG ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer19.Add( self.m_bitmap_SpawnBanner, 0, wx.BOTTOM, 5 )

        self.m_staticText_SupportDev = wx.StaticText( self, wx.ID_ANY, _(u"Support Development"), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText_SupportDev.Wrap( -1 )

        self.m_staticText_SupportDev.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer19.Add( self.m_staticText_SupportDev, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText_Description = wx.StaticText( self, wx.ID_ANY, _(u"Spawn is a free and open-source IDE for SA-MP and open.mp development."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Description.Wrap( -1 )

        bSizer19.Add( self.m_staticText_Description, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer19.Add( self.m_staticline, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_staticText_YourSupport = wx.StaticText( self, wx.ID_ANY, _(u"Your support helps improve:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_YourSupport.Wrap( -1 )

        bSizer19.Add( self.m_staticText_YourSupport, 0, wx.ALL, 5 )

        self.m_staticText_HelpsImprove = wx.StaticText( self, wx.ID_ANY, _(u"• Stability\n• New Features\n• Bug fixes\n• Long-term Maintenance\n\nThank you for supporting the development."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_HelpsImprove.Wrap( -1 )

        bSizer19.Add( self.m_staticText_HelpsImprove, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer19.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer20 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button_Donate = wx.Button( self, wx.ID_ANY, _(u"Donate"), wx.DefaultPosition, wx.DefaultSize, 0 )

        self.m_button_Donate.SetBitmap( wx.Bitmap(os.path.join(APP_ROOT, "assets", "icons","star.png"), wx.BITMAP_TYPE_PNG ) )
        bSizer20.Add( self.m_button_Donate, 0, wx.ALL, 5 )
        self.m_button_Donate.Bind(wx.EVT_BUTTON, self.on_donate_button)


        bSizer20.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_button_Close = wx.Button( self, wx.ID_ANY, _(u"Close"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer20.Add( self.m_button_Close, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.m_button_Close.SetDefault()
        self.m_button_Close.Bind(wx.EVT_BUTTON, self.on_close_button)


        bSizer19.Add( bSizer20, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer19 )
        self.Layout()

        self.Centre( wx.BOTH )

    def on_close_button(self, event):
        self.EndModal(wx.CANCEL)

    def on_donate_button(self, event):
        webbrowser.open(u"https://github.com/daniilkorochansky/spawn/tree/master#donations")

    def __del__( self ):
        pass


