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
import wx.adv

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

class SpawnAboutDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"About Spawn"), pos = wx.DefaultPosition, size = wx.Size( 430,340 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 340,330 ), wx.DefaultSize )

        bSizerMain = wx.BoxSizer( wx.VERTICAL )

        bSizer_Brand = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap_Spawn = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap(os.path.join(APP_ROOT,"assets","spawn_about.png"), wx.BITMAP_TYPE_PNG ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Brand.Add( self.m_bitmap_Spawn, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_staticText_Title = wx.StaticText( self, wx.ID_ANY, u"Spawn", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Title.Wrap( -1 )

        self.m_staticText_Title.SetFont( wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        bSizer_Brand.Add( self.m_staticText_Title, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        self.m_staticText_Subtitle = wx.StaticText( self, wx.ID_ANY, _(u"A fast and modern, open-source IDE with a native user\ninterface for SA-MP and open.mp server development."), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText_Subtitle.Wrap( -1 )

        bSizer_Brand.Add( self.m_staticText_Subtitle, 1, wx.ALIGN_CENTER|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5 )


        bSizerMain.Add( bSizer_Brand, 0, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizerMain.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_Basic = wx.BoxSizer( wx.VERTICAL )

        bSizer_Author = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Author = wx.StaticText( self, wx.ID_ANY, _(u"Author: Daniil Korochansky"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Author.Wrap( -1 )

        bSizer_Author.Add( self.m_staticText_Author, 0, wx.ALL, 5 )


        bSizer_Basic.Add( bSizer_Author, 0, wx.EXPAND, 5 )

        bSizer_SpecialThanks = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_SpecialThanks = wx.StaticText( self, wx.ID_ANY, _(u"Special thanks:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_SpecialThanks.Wrap( -1 )

        bSizer_SpecialThanks.Add( self.m_staticText_SpecialThanks, 0, wx.ALL, 5 )

        self.m_hyperlink_UserLink = wx.adv.HyperlinkCtrl( self, wx.ID_ANY, "Southclaws", u"https://github.com/Southclaws", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
        bSizer_SpecialThanks.Add( self.m_hyperlink_UserLink, 0, wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )
        self.m_hyperlink_UserLink.SetToolTip("https://github.com/Southclaws")


        bSizer_Basic.Add( bSizer_SpecialThanks, 1, wx.EXPAND, 5 )

        bSizer_License = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_License = wx.StaticText( self, wx.ID_ANY, _(u"License:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_License.Wrap( -1 )

        bSizer_License.Add( self.m_staticText_License, 0, wx.ALL, 5 )

        self.m_hyperlink_LicenseLink = wx.adv.HyperlinkCtrl( self, wx.ID_ANY, "GNU General Public License v3.0", "https://www.gnu.org/licenses/", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
        bSizer_License.Add( self.m_hyperlink_LicenseLink, 0, wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )
        self.m_hyperlink_LicenseLink.SetToolTip("https://www.gnu.org/licenses/")


        bSizer_Basic.Add( bSizer_License, 0, wx.EXPAND, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer_Basic.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer_Bottom = wx.BoxSizer( wx.HORIZONTAL )

        bSizer_Social = wx.BoxSizer( wx.HORIZONTAL )

        self.m_bpButton_Vkontakte = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.m_bpButton_Vkontakte.SetBitmap( wx.Bitmap(os.path.join(APP_ROOT, "assets", "icons","vk.png"), wx.BITMAP_TYPE_PNG ) )
        bSizer_Social.Add( self.m_bpButton_Vkontakte, 0, wx.ALL, 5 )
        self.m_bpButton_Vkontakte.Bind(wx.EVT_BUTTON, self.on_vk_click)
        self.m_bpButton_Vkontakte.SetToolTip("https://vk.com/spawn_ide")

        self.m_bpButton_Github = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.m_bpButton_Github.SetBitmap( wx.Bitmap(os.path.join(APP_ROOT, "assets", "icons","github.png"), wx.BITMAP_TYPE_PNG ) )
        bSizer_Social.Add( self.m_bpButton_Github, 0, wx.ALL, 5 )
        self.m_bpButton_Github.Bind(wx.EVT_BUTTON, self.on_github_click)
        self.m_bpButton_Github.SetToolTip("https://github.com/daniilkorochansky/spawn")


        bSizer_Bottom.Add( bSizer_Social, 1, wx.EXPAND, 5 )

        self.m_staticText_Version = wx.StaticText( self, wx.ID_ANY, "v1.0.0", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Version.Wrap( -1 )

        self.m_staticText_Version.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
        self.m_staticText_Version.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )

        bSizer_Bottom.Add( self.m_staticText_Version, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button_Close = wx.Button( self, wx.ID_ANY, _(u"Close"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Bottom.Add( self.m_button_Close, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.m_button_Close.Bind(wx.EVT_BUTTON, self.on_close_button)


        bSizer_Basic.Add( bSizer_Bottom, 0, wx.EXPAND, 5 )


        bSizerMain.Add( bSizer_Basic, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )

    def on_close_button(self, event):
        self.EndModal(wx.CANCEL)

    def on_github_click(self, event):
        webbrowser.open("https://github.com/daniilkorochansky/spawn")

    def on_vk_click(self, event):
        webbrowser.open("https://vk.com/spawn_ide")

    def __del__( self ):
        pass


