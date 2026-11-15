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
import wx.propgrid

import gettext
_ = gettext.gettext

class KeyboardShortcuts ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Keyboard Shortcuts"), pos = wx.DefaultPosition, size = wx.Size( 566,407 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 340,280 ), wx.DefaultSize )

        bSizerMain = wx.BoxSizer( wx.VERTICAL )

        bSizerSubMain = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticTextKeymap = wx.StaticText( self, wx.ID_ANY, _(u"Keymap:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextKeymap.Wrap( -1 )

        bSizerSubMain.Add( self.m_staticTextKeymap, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choiceKeymapsChoices = [ _(u"Default") ]
        self.m_choiceKeymaps = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceKeymapsChoices, 0 )
        self.m_choiceKeymaps.SetSelection( 0 )
        bSizerSubMain.Add( self.m_choiceKeymaps, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_bpButtonNew = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.m_bpButtonNew.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_PLUS, wx.ART_BUTTON ) )
        bSizerSubMain.Add( self.m_bpButtonNew, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_bpButtonClone = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.m_bpButtonClone.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_BUTTON ) )
        bSizerSubMain.Add( self.m_bpButtonClone, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_bpButtonRemove = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

        self.m_bpButtonRemove.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_BUTTON ) )
        bSizerSubMain.Add( self.m_bpButtonRemove, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizerMain.Add( bSizerSubMain, 0, wx.EXPAND, 5 )

        self.m_searchCtrl = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_searchCtrl.ShowSearchButton( True )
        self.m_searchCtrl.ShowCancelButton( False )
        bSizerMain.Add( self.m_searchCtrl, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_propertyGridManager = wx.propgrid.PropertyGridManager(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PGMAN_DEFAULT_STYLE)
        self.m_propertyGridManager.SetExtraStyle( wx.propgrid.PG_EX_MODE_BUTTONS )

        self.m_propertyGridPage = self.m_propertyGridManager.AddPage( _(u"Shortcuts"), wx.NullBitmap )
        bSizerMain.Add( self.m_propertyGridManager, 1, wx.ALL|wx.EXPAND, 5 )

        bSizerBottom = wx.BoxSizer( wx.HORIZONTAL )

        self.m_bpButtonImport = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizerBottom.Add( self.m_bpButtonImport, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_bpButtonExport = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizerBottom.Add( self.m_bpButtonExport, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_bpButtonReset = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizerBottom.Add( self.m_bpButtonReset, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizerBottom.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_buttonCancel = wx.Button( self, wx.ID_ANY, _(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerBottom.Add( self.m_buttonCancel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_buttonApply = wx.Button( self, wx.ID_ANY, _(u"Apply"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerBottom.Add( self.m_buttonApply, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizerMain.Add( bSizerBottom, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


