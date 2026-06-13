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

import git
from git.exc import BadName

import datetime

import gettext
_ = gettext.gettext

from core.logger import SpawnLogger

class GitCommitHistoryDialog(wx.Dialog):

    def __init__( self, parent, repo_obj, execute_reset_callback):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Commit History"), pos = wx.DefaultPosition, size = wx.Size( 700,400 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
        self.SetSizeHints( wx.Size( 560,400 ), wx.DefaultSize )

        self.repo = repo_obj
        self.execute_reset = execute_reset_callback
        self.commits_list = []
      
        main_sizer = wx.BoxSizer( wx.VERTICAL )

        self.m_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE|wx.SP_3D)
        
        self.m_panel_top = wx.Panel(self.m_splitter)
        top_sizer = wx.BoxSizer( wx.VERTICAL )

        self.m_listCtrl_Log = wx.ListCtrl( self.m_panel_top, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
        self.m_listCtrl_Log.InsertColumn(0, _(u"Hash"), width=70)
        self.m_listCtrl_Log.InsertColumn(1, _(u"Commit Message"), width=400)
        self.m_listCtrl_Log.InsertColumn(2, _(u"User"), width=120)
        self.m_listCtrl_Log.InsertColumn(3, _(u"Date"), width=100)
        top_sizer.Add( self.m_listCtrl_Log, 1, wx.ALL|wx.EXPAND, 5 )
        self.m_panel_top.SetSizer(top_sizer)
        self.m_listCtrl_Log.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_history_item_selected)
        self.m_listCtrl_Log.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_history_item_right_click)

        self.m_panel_bottom = wx.Panel(self.m_splitter)
        bottom_sizer = wx.BoxSizer(wx.VERTICAL)

        self.m_listBox_Files = wx.ListBox(self.m_panel_bottom, style=wx.LB_SINGLE)
        
        bottom_sizer.Add(self.m_listBox_Files, 1, wx.EXPAND|wx.ALL, 5)
        self.m_panel_bottom.SetSizer(bottom_sizer)

        self.m_splitter.SplitHorizontally(self.m_panel_top, self.m_panel_bottom, 250)
        self.m_splitter.SetMinimumPaneSize(80)

        main_sizer.Add(self.m_splitter, 1, wx.EXPAND| wx.ALL, 10)


        self.SetSizer( main_sizer )
        self.Layout()

        self.Centre( wx.BOTH )

        self.populate_commit_history()

    def populate_commit_history(self):
        self.m_listCtrl_Log.DeleteAllItems()
        self.m_listBox_Files.Clear()
        if hasattr(self, 'hash_map'):
            self.hash_map.clear()
        
        try:
            if not self.repo.head.is_valid():
                return

            commits = list(self.repo.iter_commits(max_count=30))
            
            self.commits_list = commits[1:] #Important! We're cutting off our last commit.
            

            for idx, commit in enumerate(self.commits_list):
                short_hash = commit.hexsha[:7]
                msg = commit.message.strip().split('\n')[0]
                author = commit.author.name

                committed_date = datetime.datetime.fromtimestamp(commit.committed_date).strftime('%d.%m.%Y %H:%M')

                row_idx = self.m_listCtrl_Log.InsertItem(idx, short_hash)
                self.m_listCtrl_Log.SetItem(row_idx, 1, msg)
                self.m_listCtrl_Log.SetItem(row_idx, 2, author)
                self.m_listCtrl_Log.SetItem(row_idx, 3, committed_date)

                self.m_listCtrl_Log.SetItemData(row_idx, idx)
                
                if not hasattr(self, 'hash_map'): self.hash_map = {}
                self.hash_map[short_hash] = commit.hexsha

        except Exception as e:
            SpawnLogger.error(f"Populate (Commit History): {e}")

    def on_history_item_selected(self, event):
        row_idx = event.GetIndex()
        commit_idx = self.m_listCtrl_Log.GetItemText(row_idx,col=0)
        
        self.m_listBox_Files.Clear()

        commit_hash = self.hash_map.get(commit_idx)
        if not commit_hash: return

        try:
            target_commit = self.repo.commit(commit_hash)
            changed_files = []

            if target_commit.parents:
                for file_path, stats in target_commit.stats.files.items():
                    clean_path = str(file_path).replace('\\','/')
                    changed_files.append(f"[M] {clean_path}")
            else:
                diffs = target_commit.diff(git.NULL_TREE)
                for diff_item in diffs:
                    path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                    if path:
                        status_char = f"[{diff_item.change_type}]"
                        clean_path = str(path).replace('\\','/')
                        changed_files.append(f"{status_char} {clean_path}")

            if not changed_files:
                self.m_listBox_Files.Append(_("There are no changed files in this commit."))
            else:
                for display_string in changed_files:
                    self.m_listBox_Files.Append(display_string)

        except Exception as e:
            SpawnLogger.error(f"Get File List (Commit History): {e}")
            self.m_listBox_Files.Append(_(u"Failed to get file list"))

    def on_history_item_right_click(self, event):
        item_obj = event.GetItem()
        if not item_obj:
            return
        
        if not hasattr(self, 'hash_map'): return
        
        item_obj.SetMask(wx.LIST_MASK_TEXT)
        short_hash = item_obj.GetText().strip()
        
        commit_hash = self.hash_map.get(short_hash)

        if not commit_hash:
            SpawnLogger.error(f"Hash Not Found (Commit History): {e}")
            return
        

        menu = wx.Menu()
        ID_RESET_SOFT = 8701
        ID_RESET_HARD = 8702

        menu.Append(ID_RESET_SOFT, u'{soft_reset} {short_hash}'.format(soft_reset=_("Soft Reset to"), short_hash=short_hash))
        menu.Append(ID_RESET_HARD, u'{hard_reset} {short_hash}'.format(hard_reset=_("Hard Reset to"), short_hash=short_hash))

        self.Bind(wx.EVT_MENU, lambda evt, h=commit_hash: self.trigger_reset_action(h, is_hard=False), id=ID_RESET_SOFT)
        self.Bind(wx.EVT_MENU, lambda evt, h=commit_hash: self.trigger_reset_action(h, is_hard=True), id=ID_RESET_HARD)

        self.PopupMenu(menu)
        menu.Destroy()

    def trigger_reset_action(self, commit_hash, is_hard):
       
        self.EndModal(wx.ID_OK)
        self.execute_reset(commit_hash, is_hard)

        

    def __del__( self ):
        pass
