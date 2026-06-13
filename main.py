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
import json
import re
import subprocess
import shutil
import traceback
import logging
import platform

import gettext
_ = gettext.gettext

import wx

from ui.spawn_base import SpawnFrame
from ui.editor_tab import CustomEditorTab
from ui.support_dialog import SupportDialog
from ui.about_dialog import SpawnAboutDialog
from ui.project_tree import ProjectTreeManager
from ui.bug_report_dialog import BugReportDialog
from ui.new_project_dialog import NewProjectDialog
from ui.git_commit_history_dialog import GitCommitHistoryDialog
from ui.dependency_manager_dialog import DependencyManagerDialog

from core.project_creator import ProjectCreateWorker
from core.file_watcher import ProjectFileWatcher
from core.config_manager import ConfigManager
from core.compiler import BackgroundCompiler
from core.runner import BackgroundRunner
from core.logger import SpawnLogger

from git import Repo

from core.git_manager import GitManager
from core.git_worker import GitCommitWorker
from core.git_reset_worker import GitResetWorker
from core.git_stage_worker import GitStageAllWorker
from core.git_unstage_worker import GitUnstageAllWorker
from core.git_single_reset_worker import GitSingleResetWorker
from core.git_single_stage_worker import GitSingleStageWorker
from core.git_reset_commit_worker import GitResetCommitWorker

def global_exception_handler(exc_type, exc_value, exc_traceback):
    SpawnLogger.exception("".join(traceback.format_exception(exc_type,exc_value,exc_traceback)))

class SpawnIDE(SpawnFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        SpawnLogger.initialize()

        self.ide_cfg = ConfigManager()
        
        self.find_dialog_data = wx.FindReplaceData()
        self.find_dialog_data.SetFlags(wx.FR_DOWN)
        self.active_find_dialog = None

        self.server_process_thread = None

        self.git_bash_process = None

        self.last_picked_hex_color = "0xFFFFFFFF"
        
        self.m_statusBar.SetFieldsCount(4)
        self.m_statusBar.SetStatusWidths([-1,40,80,140])
        self.m_statusBar.SetStatusText(u"---", 0)
        self.m_statusBar.SetStatusText(u"---", 1)
        self.m_statusBar.SetStatusText(u"---", 2)
        self.m_statusBar.SetStatusText(u"---", 3)
       
##        self.Bind(wx.EVT_MENU, self.on_language_click, id=wx.ID_LANGUAGE_ENGLISH)
##        self.Bind(wx.EVT_MENU, self.on_language_click, id=wx.ID_LANGUAGE_RUSSIAN)

        self.Bind(wx.EVT_CLOSE, self.on_ide_close_request)
        self.Bind(wx.EVT_SHOW, self.on_frame_first_show)
        
        self.Bind(wx.EVT_MENU, self.on_new_file, id=wx.ID_NEW_FILE)
        self.Bind(wx.EVT_TOOL, self.on_new_file, id=wx.ID_TOOLBAR_NEW_FILE)
        self.Bind(wx.EVT_MENU, self.on_close_project_click, id=wx.ID_CLOSE_PROJECT)
        self.Bind(wx.EVT_MENU, self.on_new_project, id=wx.ID_NEW_PROJECT)
        self.Bind(wx.EVT_MENU, self.on_open_project_folder_click, id=wx.ID_OPEN_SERVER_FOLDER)
        self.m_treeCtrl_ProjectTree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_clicked)
        self.m_auinotebook_Main.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_changed)
        self.m_auinotebook_Main.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_tab_closing)
        self.m_auinotebook_Main.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_tab_closed)
        
        self.Bind(wx.EVT_MENU, self.on_save_current_file, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_save_all_files, id=wx.ID_SAVE_ALL)
        self.Bind(wx.EVT_TOOL, self.on_save_all_files, id=wx.ID_TOOLBAR_SAVE_ALL)
        self.Bind(wx.EVT_MENU, self.on_open_single_file, id=wx.ID_OPEN_FILE)
        self.Bind(wx.EVT_TOOL, self.on_open_single_file, id=wx.ID_TOOLBAR_OPEN_FILE)
        self.Bind(wx.EVT_MENU, self.on_ide_close_request, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.on_open_settings_tab_click, id=wx.ID_SETTINGS)
        self.Bind(wx.EVT_MENU, self.on_set_reset_settings_click, id=wx.ID_RESET_SETTINGS)
        
        self.Bind(wx.EVT_MENU, self.on_open_find_dialog, id=wx.ID_FIND_REPLACE)
        self.Bind(wx.EVT_MENU, self.on_execute_go_to_line, id=wx.ID_GO_TO_LINE)
        self.Bind(wx.EVT_MENU, self.on_open_dependency_manager_click, id=wx.ID_SAMPCTL_DEPENDENCIES_MANAGER)

        self.Bind(wx.EVT_MENU, self.on_copy_click, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_cut_click, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.on_paste_click, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.on_select_all_click, id=wx.ID_SELECT_ALL)
        self.Bind(wx.EVT_MENU, self.on_undo_click, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.on_redo_click, id=wx.ID_REDO)

        self.Bind(wx.EVT_MENU, self.on_zoom_in_click, id=wx.ID_ZOOM_IN)
        self.Bind(wx.EVT_MENU, self.on_zoom_out_click, id=wx.ID_ZOOM_OUT)
        self.Bind(wx.EVT_MENU, self.on_zoom_reset_click, id=wx.ID_RESET_ZOOM)

        self.Bind(wx.EVT_MENU, self.on_menu_convert_eol_crlf, id=wx.ID_EOL_CRLF)
        self.Bind(wx.EVT_MENU, self.on_menu_convert_eol_lf, id=wx.ID_EOL_LF)

        self.Bind(wx.EVT_MENU, self.on_menu_reopen_enc_utf8, id=wx.ID_REOPEN_TO_UTF8)
        self.Bind(wx.EVT_MENU, self.on_menu_reopen_enc_cp1251, id=wx.ID_REOPEN_TO_CP1251)
        
        self.Bind(wx.EVT_TOOL, self.on_build_project_execute, id=wx.ID_TOOLBAR_BUILD_PROJECT)
        self.Bind(wx.EVT_MENU, self.on_build_project_execute, id=wx.ID_BUILD_PROJECT)
        self.Bind(wx.EVT_TOOL, self.on_run_server_execute, id=wx.ID_TOOLBAR_RUN_STOP_SERVER)
        self.Bind(wx.EVT_TOOL, self.on_run_server_execute, id=wx.ID_RUN_STOP_SERVER) 

        #Git Binds
        self.Bind(wx.EVT_BUTTON, self.on_git_commit_execute_click, id=wx.ID_GIT_COMMIT)
        self.m_treeCtrl_GitHistory.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_git_tree_item_click)
        self.Bind(wx.EVT_TOOL, self.on_git_manual_refresh, id=wx.ID_GIT_REFRESH)
        self.Bind(wx.EVT_TOOL, self.on_git_reset_all_changes_click, id=wx.ID_GIT_DISCARD_ALL)
        self.Bind(wx.EVT_TOOL, self.on_git_stage_all_click, id=wx.ID_GIT_STAGE_ALL)
        self.Bind(wx.EVT_TOOL, self.on_git_unstage_all_click, id=wx.ID_GIT_UNSTAGE_ALL)
        self.m_treeCtrl_GitHistory.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_git_tree_right_click)
        self.Bind(wx.EVT_TOOL, self.on_git_view_history_click, id=wx.ID_GIT_COMMIT_HISTORY)
        self.Bind(wx.EVT_TOOL, self.on_git_open_terminal_click, id=wx.ID_GIT_TERMINAL)
        #---------

        self.Bind(wx.EVT_MENU, self.on_toggle_project_panel_click, id=wx.ID_TOGGLE_PROJECT_PANEL)
        self.Bind(wx.EVT_MENU, self.on_toggle_output_panel_click, id=wx.ID_TOGGLE_OUTPUT_PANEL)
        self.Bind(wx.EVT_MENU, self.on_toggle_toolbar_panel_click, id=wx.ID_TOGGLE_TOOLBAR)
        
        self.Bind(wx.EVT_MENU, self.on_bug_report_click, id=wx.ID_BUG_REPORT)
        self.Bind(wx.EVT_MENU, self.on_donate_click, id=wx.ID_DONATE)
        self.Bind(wx.EVT_MENU, self.on_about_click, id=wx.ID_ABOUT)

        self.m_treeCtrl_ProjectTree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_project_tree_right_click)
        
        self.current_project_path = None
        self.file_watcher = ProjectFileWatcher(self)

        
        #Init icons for Project and Git Tree
        self.tree_images = wx.ImageList(16,16)
        self.idx_folder = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_folder.png"),wx.BITMAP_TYPE_PNG))
        self.idx_pawn = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_file_code.png"),wx.BITMAP_TYPE_PNG))
        self.idx_cfg = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_cfg.png"),wx.BITMAP_TYPE_PNG))
        self.idx_file = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_file_text.png"),wx.BITMAP_TYPE_PNG))
        self.idx_folder_root = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_folder_root.png"),wx.BITMAP_TYPE_PNG))
        self.idx_folder_root_opened = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_folder_root_opened.png"),wx.BITMAP_TYPE_PNG))
        self.idx_folder_opened = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_folder_opened.png"),wx.BITMAP_TYPE_PNG))
        self.idx_pawn_inc = self.tree_images.Add(wx.Bitmap(os.path.join(self.icons_folder,"pt_code_inc.png"),wx.BITMAP_TYPE_PNG))
        self.m_treeCtrl_ProjectTree.AssignImageList(self.tree_images)

        self.m_treeCtrl_GitHistory.SetImageList(self.m_treeCtrl_ProjectTree.GetImageList())

        self.icon_indices = {
            "folder": self.idx_folder,
            "folder_opened": self.idx_folder_opened,
            "pawn": self.idx_pawn,
            "cfg": self.idx_cfg,
            "file": self.idx_file,
            "folder_root": self.idx_folder_root,
            "folder_root_opened": self.idx_folder_root_opened,
            "pawn_inc": self.idx_pawn_inc
            }
        
        #InfoBar
        infobar = self.m_infoCtrl
        if infobar:
            self.ID_INFOBAR_SETUP_SAMPCTL = 9601
            self.ID_INFOBAR_SETUP_GIT = 9602

            infobar_sizer = infobar.GetSizer()
            if infobar_sizer:
                self.btn_sampctl = wx.Button(infobar, self.ID_INFOBAR_SETUP_SAMPCTL, _(u"Browse..."))
                self.btn_git = wx.Button(infobar, self.ID_INFOBAR_SETUP_GIT, _(u"Browse..."))
                self.btn_sampctl.Hide()
                self.btn_git.Hide()

                infobar_sizer.Add(self.btn_sampctl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
                infobar_sizer.Add(self.btn_git, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
                
            #Deleting close button in InfoBar
            for child in infobar.GetChildren():
                if isinstance(child, wx.BitmapButton):
                    child.Hide()
                    if infobar_sizer:
                        infobar_sizer.Detach(child)
                    break
                
            infobar.Layout()
            
            infobar.Bind(wx.EVT_BUTTON, self.on_infobar_action_click, id=self.ID_INFOBAR_SETUP_SAMPCTL)
            infobar.Bind(wx.EVT_BUTTON, self.on_infobar_action_click, id=self.ID_INFOBAR_SETUP_GIT)
        #-------

        self.Show()
        
        self.toggle_project_ui_state(False)
        self.update_button_is_no_tabs()
        self.update_git_ui_controls_state()

    def on_bug_report_click(self, event):
        dlg = BugReportDialog(self)
        dlg.ShowModal()

    def on_donate_click(self, event):
        dlg = SupportDialog(self)
        dlg.ShowModal()

    def on_about_click(self, event):
        dlg = SpawnAboutDialog(self)
        dlg.ShowModal()
                

    def on_zoom_in_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.ZoomIn()

    def on_zoom_out_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.ZoomOut()

    def on_zoom_reset_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.SetZoom(0)

    def on_toggle_toolbar_panel_click(self, event):
        pane = self.m_mgr.GetPane(self.m_auiToolBar)
        pane.Show(not pane.IsShown())
        self.m_mgr.Update()

    def on_toggle_project_panel_click(self, event):
        pane = self.m_mgr.GetPane(self.m_projectPanel)
        pane.Show(not pane.IsShown())
        self.m_mgr.Update()

    def on_toggle_output_panel_click(self, event):
        pane = self.m_mgr.GetPane(self.m_outputPanel)
        pane.Show(not pane.IsShown())
        self.m_mgr.Update()

    def create_gitignore(self):
        gitignore_content = """
# Compiled Bytecode, precompiled output and assembly
*.amx
*.lst
*.asm

# Vendor directory for dependencies
dependencies/

# compiled settings file
# keep `samp.json` file on version control
# but make sure the `rcon_password` field is set externally
# you can use the environment variable `SAMP_RCON_PASSWORD` to do this.
server.cfg
config.json
bans.json
sampctl_build_file.inc 

# Plugins directory
plugins/

# binaries
*.exe
*.dll
*.so
announce
samp03svr
samp-npc

# logs
logs/
server_log.txt
log.txt
crashinfo.txt

# Ban list
samp.ban

# Common files
*.lock
    """

        gitignore_path = os.path.join(self.current_project_path,".gitignore")
        try:
            with open(gitignore_path,"w",encoding="utf-8",newline="\r\n") as f:
                f.write(gitignore_content)
            return True

        except Exception as e:
            SpawnLogger.error(f"Creating .gitignore: {e}")
            return False

    def on_git_open_terminal_click(self, event):
        if not self.git_manager:
            return

        if not self.git_manager.is_repo:
            return
        
        if (self.git_bash_process and self.git_bash_process.poll() is None):
            wx.MessageBox(_("Git Terminal is already running."),_("Information"))
            return

        git_exe = self.ide_cfg.get("system.git.executable_path","")
        if not git_exe:
            return

        git_bin_dir = os.path.dirname(git_exe)
        git_bash = os.path.join(git_bin_dir,"bash.exe")
        git_bash = os.path.abspath(git_bash)

        self.git_bash_process = subprocess.Popen([git_bash],cwd=self.current_project_path)

    def reopen_with_encoding(self, tab, new_encoding):
        if not getattr(tab, "file_path", None):
            return

        if tab.m_scintilla_Editor.GetModify():
            dlg = wx.MessageDialog(
                self,
                _("The file has unsaved changes.\nDo you want to reopen anyway?"),
                _("Reopen File"),
                wx.YES_NO | wx.ICON_WARNING
            )

            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return

            dlg.Destroy()

        try:
            with open(tab.file_path, "rb") as f:
                binary_data = f.read()

            text_content = binary_data.decode(new_encoding,errors="strict")

            if b"\r\n" in binary_data:
                tab.native_eol = "CRLF"
                tab.m_scintilla_Editor.SetEOLMode(wx.stc.STC_EOL_CRLF)
            else:
                tab.native_eol = "LF"
                tab.m_scintilla_Editor.SetEOLMode(wx.stc.STC_EOL_LF)

            # Inside Scintilla we always work with LF
            text_content = text_content.replace("\r\n","\n")

            text_content = text_content.replace("\r","\n")

            tab.m_scintilla_Editor.Freeze()

            try:
                tab.m_scintilla_Editor.SetText(text_content)

                tab.m_scintilla_Editor.EmptyUndoBuffer()

                tab.m_scintilla_Editor.SetSavePoint()
            except Exception as e:
                SpawnLogger.error(f"Reopening File(SetText): {e}")

            finally:
                tab.m_scintilla_Editor.Thaw()

            tab.current_encoding = new_encoding

            enc_stat = new_encoding.upper()
            eol_stat = tab.native_eol

            self.m_statusBar.SetStatusText(_("File reopened as {encoding}.").format(encoding=enc_stat),0)
            self.m_statusBar.SetStatusText(f"{enc_stat} | {eol_stat}",2)

        except UnicodeDecodeError:
            self.m_statusBar.SetStatusText(_("Cannot reopen file using {encoding}. Decoding failed.").format(encoding=new_encoding.upper()),0)

        except Exception as e:
            SpawnLogger.error(f"Reopening File: {e}")
            self.m_statusBar.SetStatusText(_("Error reopening file"),0)
            

    def on_menu_reopen_enc_utf8(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            self.reopen_with_encoding(tab, "utf-8")

    def on_menu_reopen_enc_cp1251(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            self.reopen_with_encoding(tab, "cp1251")
            

    def on_set_reset_settings_click(self, event):
        confirm = wx.MessageBox(_(u"Are you sure you want to reset all settings to their default values?"), _(u"Warning"), wx.YES_NO | wx.ICON_WARNING, self)
        if confirm == wx.NO:
            return

        self.ide_cfg.reset_settings()
        self.check_environment_on_startup()

    def on_undo_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.Undo()

    def on_redo_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.Redo()

    def on_copy_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.Copy()

    def on_cut_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.Cut()

    def on_paste_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            if wx.TheClipboard.Open():
                try:
                    text_data = wx.TextDataObject()

                    if wx.TheClipboard.GetData(text_data):
                        tab.m_scintilla_Editor.ReplaceSelection(text_data.GetText())
                except Exception as e:
                    SpawnLogger.error(f"Paste: {e}")

                finally:
                    wx.TheClipboard.Close()

    def on_select_all_click(self, event):
        tab = self.m_auinotebook_Main.GetCurrentPage()
        if tab:
            tab.m_scintilla_Editor.SelectAll()
        

    def on_frame_first_show(self, event):
        self.Unbind(wx.EVT_SHOW)
        event.Skip()

        self.check_environment_on_startup()


    # TODO:
    # Temporarily disabled.
    # Needs proper synchronization between
    # Git diff, file on disk and editor state.
    def show_file_diff_markers(self, absolute_path, relative_path):
        if not self.git_manager or not self.git_manager.is_repo:
            return

        clean_rel_path = relative_path.replace('\\','/')
        project_root = os.path.normpath(self.git_manager.repo.working_tree_dir)
        
        try:
            diff_output = self.git_manager.repo.git.diff("--", clean_rel_path, U=0)

            if not diff_output.strip():
                self.m_statusBar.SetStatusText(u"No uncommitted changes found.",0)
                return

            self.open_file_in_tab(absolute_path)

            notebook = self.m_auinotebook_Main
            active_tab = notebook.GetCurrentPage()
            if not active_tab:
                return

            editor = active_tab.m_scintilla_Editor
            editor.MarkerDeleteAll(12)

            diff_lines = diff_output.splitlines()

            current_file_line = 0
            first_changed_line = None
            
            for line in diff_lines:
                if line.startswith('@@'):
                    match_re = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)', line) #We cut out the coordinates of the modified lines
                    if match_re:
                        current_file_line = int(match_re.group(1)) - 1
                    continue
                if line.startswith('---') or line.startswith('+++') or line.startswith('index'):
                    continue

                if line.startswith('+'):
                    if first_changed_line is None:
                        first_changed_line = current_file_line
                        
                    editor.MarkerAdd(current_file_line, 12)
                    current_file_line += 1
                    
                elif line.startswith(' '):
                    current_file_line += 1
                    
                elif line.startswith('-'):
                    continue

            if first_changed_line is not None:
                editor.GotoLine(first_changed_line)
                editor.VerticalCentreCaret()
                
        except Exception as e:
            SpawnLogger.error(f"Git History Sync: {e}")

    def on_git_view_history_click(self, event):
        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None or not self.git_manager.is_repo:
            return

        with GitCommitHistoryDialog(self, self.git_manager.repo, self.execute_git_time_travel_reset) as dlg:
            dlg.ShowModal()

    def execute_git_time_travel_reset(self, commit_hash, is_hard):
        short_hash = commit_hash[:7]

        if is_hard:
            confirm = wx.MessageBox(
                _(u"Attention! You have chosen a hard revert to commit [{short_hash}].\n\n"
                u"This will permanently destroy all current uncommitted edits on disk "
                u"and will forcefully return the files of the entire server to the state of this commit!\n\n"
                u"Are you sure you want to continue?").format(short_hash=short_hash),
                _(u"Warning"),
                wx.YES_NO | wx.ICON_ERROR | wx.NO_DEFAULT, self)
            if confirm == wx.NO: return
        else:
            confirm = wx.MessageBox(
                _(u"You want to do a soft revert before committing [{short_hash}].\n\n"
                u"The HEAD pointer will move into the past, but all your currently written code will remain intact "
                u"and will simply go into the status of changes.\n\nContinue?").format(short_hash=short_hash),
                _(u"Rewind history"), wx.YES_NO|wx.ICON_QUESTION, self
                )
            if confirm == wx.NO: return

        #[statusbar] Git Reset
        self.m_textCtrl_CommitText.Enable(False)
        self.m_button_Commit.Enable(False)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_DISCARD_ALL, False)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_REFRESH, False)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_STAGE_ALL, False)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_UNSTAGE_ALL, False)

        reset_thread = GitResetCommitWorker(
            repo_obj=self.git_manager.repo,
            commit_hash=commit_hash,
            is_hard=is_hard,
            on_finished_callback=self.on_git_reset_commit_async_finished
            )
        reset_thread.start()

    def on_git_reset_commit_async_finished(self, success, is_hard, commit_hash, error_message):
        self.m_textCtrl_CommitText.Enable(True)
        self.m_button_Commit.Enable(True)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_DISCARD_ALL, True)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_REFRESH, True)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_STAGE_ALL, True)
        self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_UNSTAGE_ALL, True)

        short_hash = commit_hash[:7]

        if success:
            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()

            if is_hard:
                notebook = self.m_auinotebook_Main
                for page_idx in range(notebook.GetPageCount() - 1, -1, -1):
                    tab = notebook.GetPage(page_idx)
                    if tab and hasattr(tab, 'file_path') and tab.file_path:
                        abs_file_path = os.path.normpath(tab.file_path)

                        if os.path.exists(abs_file_path) and os.path.isfile(abs_file_path):
                            try:
                                enc = tab.current_encoding
                                with open(abs_file_path, 'r', encoding=enc, errors="replace") as f:
                                    clean_text = f.read().replace("\r\n", "\n")

                                tab.m_scintilla_Editor.SetText(clean_text)
                                tab.m_scintilla_Editor.EmptyUndoBuffer()
                                tab.m_scintilla_Editor.MarkerDeleteAll(13)
                                tab.m_scintilla_Editor.MarkerDeleteAll(14)
                                tab.m_scintilla_Editor.SetSavePoint()
                            except Exception as e:
                                SpawnLogger.error(f"Git Reset Commit: {e}")
                        else:
                            notebook.DeletePage(page_idx)
           
            wx.MessageBox(_(u"The operation was completed successfully!\nThe repository branch has been rewound to the commit [{short_hash}]").format(short_hash=short_hash),
                          _(u"Success"), wx.OK|wx.ICON_INFORMATION, self)
        else:
            SpawnLogger.error(f"Git Reset Commit: {error_message}")
            wx.MessageBox(_(u"Reset failed"), _(u"Git Error"), wx.OK|wx.ICON_ERROR, self)

    def check_environment_on_startup(self):
        self.SendSizeEvent()
        self.Layout()
        
        infobar = self.m_infoCtrl
        if not infobar:
            return

        self.btn_sampctl.Hide()
        self.btn_git.Hide()

        sampctl_path = self.ide_cfg.get("system.sampctl.executable_path", "")
        sampctl_ready = bool(sampctl_path and os.path.exists(sampctl_path) and os.path.isfile(sampctl_path))

        git_ready = True
        if self.ide_cfg.get("system.git.enable", False):
            git_path = self.ide_cfg.get("system.git.executable_path", "")
            git_ready = bool(git_path and os.path.exists(git_path) and os.path.isfile(git_path))
            
        if self.current_project_path and sampctl_ready:
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, True)
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, True)
            self.m_menubar.Enable(wx.ID_SAMPCTL_DEPENDENCIES_MANAGER, True)
            #self.m_menubar.Enable(wx.ID_CLEAN_PROJECT, True)
            self.m_menubar.Enable(wx.ID_RUN_STOP_SERVER, True)
            self.m_menubar.Enable(wx.ID_BUILD_PROJECT, True)

            self.m_auiToolBar.Realize()
            self.m_auiToolBar.Refresh()

            pane = self.m_mgr.GetPane(self.m_auiToolBar)
            if pane.IsShown():
                self.m_auiToolBar.GetContainingSizer().Layout()
            
        if  not self.current_project_path and sampctl_ready:
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, False)
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_SAMPCTL_DEPENDENCIES_MANAGER, False)
            #self.m_menubar.Enable(wx.ID_CLEAN_PROJECT, False)
            self.m_menubar.Enable(wx.ID_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_BUILD_PROJECT, False)

            self.m_auiToolBar.Realize()
            self.m_auiToolBar.Refresh()

            pane = self.m_mgr.GetPane(self.m_auiToolBar)
            if pane.IsShown():
                self.m_auiToolBar.GetContainingSizer().Layout()

        if  not self.current_project_path and not sampctl_ready:
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, False)
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_SAMPCTL_DEPENDENCIES_MANAGER, False)
            #self.m_menubar.Enable(wx.ID_CLEAN_PROJECT, False)
            self.m_menubar.Enable(wx.ID_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_BUILD_PROJECT, False)

        if self.current_project_path and not sampctl_ready:
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, False)
            self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_SAMPCTL_DEPENDENCIES_MANAGER, False)
            #self.m_menubar.Enable(wx.ID_CLEAN_PROJECT, False)
            self.m_menubar.Enable(wx.ID_RUN_STOP_SERVER, False)
            self.m_menubar.Enable(wx.ID_BUILD_PROJECT, False)
            
            self.m_auiToolBar.Realize()
            self.m_auiToolBar.Refresh()

            pane = self.m_mgr.GetPane(self.m_auiToolBar)
            if pane.IsShown():
                self.m_auiToolBar.GetContainingSizer().Layout()

        if not self.current_project_path:
            self.pane_left.Hide()
            self.pane_bottom.Hide()
            self.m_mgr.Update()
        else:
            self.pane_left.Show()
            self.pane_bottom.Show()
            self.m_mgr.Update()

        self.m_menubar.Enable(wx.ID_NEW_PROJECT, sampctl_ready)

        if not sampctl_ready:
            msg = _(u"Please provide the path to the SAMPCTL executable.")
            infobar.Hide()
            self.btn_sampctl.Show()
            
            if infobar.GetParent():
                infobar.GetParent().Layout()
            infobar.ShowMessage(msg, wx.ICON_WARNING)
            self.Layout()
            self.m_mgr.Update()
            return

        if not git_ready:
            msg = _(u"Please provide the path to the Git executable.")
            infobar.Hide()
            self.btn_git.Show()
            
            if infobar.GetParent():
                infobar.GetParent().Layout()
            infobar.ShowMessage(msg, wx.ICON_WARNING)
            self.Layout()
            self.m_mgr.Update()
            return
        infobar.Dismiss()
        

    def on_infobar_action_click(self, event):
        btn_id = event.GetId()
        if btn_id == self.ID_INFOBAR_SETUP_SAMPCTL:
            with wx.FileDialog(self, _(u"Specify the path to the sampctl.exe executable file."),
                               defaultFile="sampctl.exe", wildcard="SAMPCTL (*.exe)|sampctl.exe",
                               style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    self.ide_cfg.set("system.sampctl.executable_path", os.path.normpath(dlg.GetPath()).replace('\\','/'))
                    self.ide_cfg.save()

                    self.check_environment_on_startup()
                    
        elif btn_id == self.ID_INFOBAR_SETUP_GIT:
            with wx.FileDialog(self, _(u"Specify the path to the git.exe executable file."),
                               defaultFile="git.exe", wildcard="GIT (*.exe)|git.exe",
                               style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    self.ide_cfg.set("system.git.executable_path", os.path.normpath(dlg.GetPath()).replace('\\','/'))
                    self.ide_cfg.save()

                    self.check_environment_on_startup()
        

    def update_git_ui_controls_state(self):
        toolbar = self.m_auiToolBar_Git

        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None or not self.git_manager.is_repo or not toolbar:
            if toolbar:
                toolbar.EnableTool(wx.ID_GIT_DISCARD_ALL, False)
                toolbar.EnableTool(wx.ID_GIT_REFRESH, False)
                toolbar.EnableTool(wx.ID_GIT_STAGE_ALL, False)
                toolbar.EnableTool(wx.ID_GIT_UNSTAGE_ALL, False)
                toolbar.EnableTool(wx.ID_GIT_COMMIT_HISTORY, False)
                toolbar.EnableTool(wx.ID_GIT_TERMINAL, False)

                toolbar.Realize()
                toolbar.Refresh()
                toolbar.GetContainingSizer().Layout()
            self.m_textCtrl_CommitText.Enable(False)
            self.m_button_Commit.Enable(False)

            self.m_treeCtrl_GitHistory.DeleteAllItems()
            return
        
        cache = self.git_manager.status_cache
        has_unstaged = any(status in ["modified", "untracked", "deleted"] for status in cache.values())
        has_staged = any(status == "staged" for status in cache.values())
        has_commited_changes = any(status in ["modified", "staged", "deleted"] for status in cache.values())
        has_any_changes = len(cache) > 0

        toolbar.EnableTool(wx.ID_GIT_DISCARD_ALL, has_commited_changes)
        toolbar.EnableTool(wx.ID_GIT_REFRESH, True)
        toolbar.EnableTool(wx.ID_GIT_STAGE_ALL, has_unstaged)
        toolbar.EnableTool(wx.ID_GIT_UNSTAGE_ALL, has_staged)
        toolbar.EnableTool(wx.ID_GIT_COMMIT_HISTORY, True)
        toolbar.EnableTool(wx.ID_GIT_TERMINAL, True)

        toolbar.Realize()
        toolbar.Refresh()
        toolbar.GetContainingSizer().Layout()

        self.m_textCtrl_CommitText.Enable(has_any_changes)
        self.m_button_Commit.Enable(has_any_changes)

        if not has_any_changes:
            self.m_textCtrl_CommitText.SetValue("")

    def on_git_unstage_all_click(self, event):
        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None or not self.git_manager.is_repo:
            return

        has_staged = any(status == "staged" for status in self.git_manager.status_cache.values())
        if not has_staged:
            wx.MessageBox(_(u"There are no indexed files to reset."),
                          _(u"Git Indexing"), wx.OK|wx.ICON_INFORMATION, self)
            return

        self.git_source_control_toggle_ui(False)

        self.m_statusBar.SetStatusText(_(u"[Git] Starting to reset indexing..."),0)

        unstage_worker = GitUnstageAllWorker(
            repo_obj=self.git_manager.repo,
            on_finished_callback=self.on_git_unstage_all_async_finished
            )
        unstage_worker.start()

    def git_source_control_toggle_ui(self, enable):
        if enable:
            self.m_textCtrl_CommitText.Enable(True)
            self.m_button_Commit.Enable(True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_DISCARD_ALL, True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_REFRESH, True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_STAGE_ALL, True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_UNSTAGE_ALL, True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_COMMIT_HISTORY, True)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_TERMINAL, True)
        else:
            self.m_textCtrl_CommitText.Enable(False)
            self.m_button_Commit.Enable(False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_DISCARD_ALL, False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_REFRESH, False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_STAGE_ALL, False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_UNSTAGE_ALL, False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_COMMIT_HISTORY, False)
            self.m_auiToolBar_Git.EnableTool(wx.ID_GIT_TERMINAL, False)

    def on_git_unstage_all_async_finished(self, success, error_message):
        self.git_source_control_toggle_ui(True)

        if success:
            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()
            self.m_statusBar.SetStatusText(_(u"[Git] Indexing reset successfully."),0)
        else:
            SpawnLogger.error(f"Git Reset Indexing: {error_message}")
            wx.MessageBox(_(u"Failed to reset indexing"),
                          _(u"Git Error"), wx.OK|wx.ICON_ERROR, self)
        

    def on_git_stage_all_click(self, event):
        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None or not self.git_manager.is_repo:
            return

        if not self.git_manager.status_cache:
            wx.MessageBox(_(u"There are no modified files in the repository to index."),
                          _(u"Git Indexing"), wx.OK|wx.ICON_INFORMATION, self)
            return

        self.git_source_control_toggle_ui(False)
        self.m_statusBar.SetStatusText(_(u"[Git] Indexing of all changes has begun..."),0)

        stage_worker = GitStageAllWorker(
            repo_obj=self.git_manager.repo,
            on_finished_callback=self.on_git_stage_all_async_finished
            )
        stage_worker.start()

    def on_git_stage_all_async_finished(self, success, error_message):
        self.git_source_control_toggle_ui(True)

        if success:
            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()
            self.m_statusBar.SetStatusText(_(u"[Git] Everything was indexed successfully."),0)
        else:
            SpawnLogger.error(f"Git Index Files: {error_message}")
            wx.MessageBox(_(u"Failed to index files"),
                          _(u"Git Error"), wx.OK|wx.ICON_ERROR, self)

    def on_git_tree_right_click(self, event):
        tree = self.m_treeCtrl_GitHistory

        mouse_pos = event.GetPoint()
        item_id, flags = tree.HitTest(mouse_pos)
        
        if not item_id or not item_id.IsOk():
            return

        tree.SelectItem(item_id)

        file_path = tree.GetItemData(item_id)
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        if not "." in file_name:
            return

        relative_path = os.path.relpath(file_path, self.current_project_path)
        clean_relative_path = relative_path.replace('\\', '/').strip().lower()

        status = "normal"
        if hasattr(self, "git_manager") and self.git_manager and self.git_manager.is_repo:
            status = self.git_manager.get_file_status(clean_relative_path)

        menu = wx.Menu()

        ID_GIT_SINGLE_RESET = 8501
        ID_GIT_SINGLE_STAGE = 8502

        ID_GIT_SHOW_DIFF_LINES = 8503

        if status == "staged":
            menu.Append(ID_GIT_SINGLE_STAGE, _(u"Unstage"))
            self.Bind(wx.EVT_MENU, lambda evt: self.execute_git_single_stage_toggle(file_path, relative_path, is_unstage=True), id=ID_GIT_SINGLE_STAGE)
        else:
            menu.Append(ID_GIT_SINGLE_STAGE, _(u"Stage"))
            self.Bind(wx.EVT_MENU, lambda evt: self.execute_git_single_stage_toggle(file_path, relative_path, is_unstage=False), id=ID_GIT_SINGLE_STAGE)

        menu_label = _(u"Revert File Changes") if status != "deleted" else _(u"Recover Deleted File")
        item_reset = menu.Append(ID_GIT_SINGLE_RESET, menu_label)

        
          # TODO:
          # Temporarily disabled.
          # Needs proper synchronization between
          # Git diff, file on disk and editor state.
##        if status == "modified":
##            menu.Append(ID_GIT_SHOW_DIFF_LINES, _("Show Modified Lines"))
##            self.Bind(wx.EVT_MENU, lambda evt, a=file_path, r=relative_path: self.show_file_diff_markers(a, r), id=ID_GIT_SHOW_DIFF_LINES)

        self.Bind(wx.EVT_MENU, lambda evt: self.execute_git_single_file_reset(file_path, relative_path), id=ID_GIT_SINGLE_RESET)

        self.PopupMenu(menu)
        menu.Destroy()

    def execute_git_single_stage_toggle(self, absolute_path, relative_path, is_unstage):
        """Starts background asynchronous indexing of a single specified file."""
        clean_rel_path = relative_path.replace('\\', '/')
        
        self.git_source_control_toggle_ui(False)

        stage_thread = GitSingleStageWorker(
            repo_obj=self.git_manager.repo,
            relative_file_path=clean_rel_path,
            is_unstage=is_unstage,
            on_finished_callback=self.on_git_single_stage_async_finished
            )
        stage_thread.start()

    def on_git_single_stage_async_finished(self, success, relative_path, error_message):
        """Triggered on completion: refreshes the cache and updates the Project Tree, Git Tree"""
        self.git_source_control_toggle_ui(True)
        
        if success:
            if hasattr(self, 'git_manager') and self.git_manager:
            
                self.git_manager.update_statuses_cache()
            self.refresh_project_tree()
            self.m_statusBar.SetStatusText(_(u"[Git] The file index has been updated successfully."),0)
        else:
            SpawnLogger.error(f"Git Indexing File: {error_message}")
            self.m_statusBar.SetStatusText(_(u"[Git] Error indexing file"),0)

    
    def execute_git_single_file_reset(self, absolute_path, relative_path):
        file_name = os.path.basename(absolute_path)
        clear_rel_track_path = relative_path.replace('\\','/').strip().lower()

        status = "normal"
        if hasattr(self, 'git_manager') and self.git_manager and self.git_manager.is_repo:
            status = self.git_manager.get_file_status(clear_rel_track_path)

        if status == "untracked":
            msg = _(u"File '{file_name}' is completely new and has not yet been committed.\n\nAre you sure you want to completely erase and delete it from your hard drive?").format(file_name=file_name)
            title = _(u"Deleting a new file")
        else:
            msg = _(u"Are you sure you want to discard local edits and revert the file '{file_name}' to the state of the last commit?").format(file_name=file_name)
            title = _(u"Rolling back a file")
        confirm = wx.MessageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT, self)
        if confirm == wx.NO:
            return
        
        self.git_source_control_toggle_ui(False)

        if status == "untracked":
            self.m_statusBar.SetStatusText(_(u"[Git] The file '{file}' has been deleted.").format(file=file_name), 0)

            try:
                if os.path.exists(absolute_path):
                    os.remove(absolute_path)

                self.on_git_single_reset_async_finished(True, clear_rel_track_path, "")
            except Exception as e:
                self.on_git_single_reset_async_finished(False, clear_rel_track_path, str(e))
        else:
            self.m_statusBar.SetStatusText(_(u"[Git] Rollback of file '{file}' has begun...").format(file=file_name), 0)

            single_reset_thread = GitSingleResetWorker(
                repo_obj=self.git_manager.repo,
                relative_file_path=clear_rel_track_path,
                on_finished_callback=self.on_git_single_reset_async_finished
                )
            single_reset_thread.start()

        
    def on_git_single_reset_async_finished(self, success, relative_path, error_message):
        self.git_source_control_toggle_ui(True)

        if success:
            abs_file_path = os.path.normpath(os.path.join(self.current_project_path, relative_path))

            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()

            notebook = self.m_auinotebook_Main
            for page_idx in range(notebook.GetPageCount() - 1, -1, -1):
                tab = notebook.GetPage(page_idx)
                if tab and hasattr(tab, 'file_path') and tab.file_path:
                    if os.path.normpath(tab.file_path).lower() == abs_file_path.lower():
                        if os.path.exists(tab.file_path) and os.path.isfile(tab.file_path):
                            try:
                                current_enc = tab.current_encoding
                                with open(tab.file_path, 'r', encoding=current_enc, errors="replace") as f:
                                    clean_text = f.read().replace("\r\n", "\n")

                                tab.m_scintilla_Editor.SetText(clean_text)
                                tab.m_scintilla_Editor.EmptyUndoBuffer()
                                tab.m_scintilla_Editor.MarkerDeleteAll(13)
                                tab.m_scintilla_Editor.MarkerDeleteAll(14)
                                tab.m_scintilla_Editor.SetSavePoint()
                            except Exception as e:
                                SpawnLogger.error(f"Git Rollback File(SetText): {e}")
                        else:
                            notebook.DeletePage(page_idx)

            self.m_statusBar.SetStatusText(_(u"[Git] File rollback completed successfully."),0)
        else:
            SpawnLogger.error(f"Git Rollback File: {error_message}")
            wx.MessageBox(_(u"Failed to rollback file"), _(u"Git Error"), wx.OK | wx.ICON_ERROR, self)
        

    def on_menu_convert_eol_crlf(self, event):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab.is_untitled:
            if active_tab and hasattr(active_tab, "native_eol"):
                active_tab.native_eol = "CRLF"
                active_tab.m_scintilla_Editor.SetEOLMode(wx.stc.STC_EOL_CRLF)
                active_tab.m_scintilla_Editor.ConvertEOLs(wx.stc.STC_EOL_CRLF)

                enc = active_tab.current_encoding.upper()
                self.m_statusBar.SetStatusText(f"{enc} | CRLF", 2)

    def on_menu_convert_eol_lf(self, event):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab.is_untitled:
            if active_tab and hasattr(active_tab, "native_eol"):
                active_tab.native_eol = "LF"
                active_tab.m_scintilla_Editor.SetEOLMode(wx.stc.STC_EOL_LF)
                active_tab.m_scintilla_Editor.ConvertEOLs(wx.stc.STC_EOL_LF)

                enc = active_tab.current_encoding.upper()
                self.m_statusBar.SetStatusText(f"{enc} | LF", 2)

    def on_git_reset_all_changes_click(self, event):
        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None:
            return

        if not self.current_project_path:
            return

        if not self.git_manager.status_cache:
            self.m_statusBar.SetStatusText(_(u"[Git] There are no uncommitted changes to reset."),0)
            return
        
        confirm = wx.MessageBox(
            _(u"Warning! This action will forcibly erase and destroy absolutely all your uncommitted "
            u"changes in the codebase to the state of the last commit!\n\n"
            u"Are you sure you want to permanently rollback the project code?"),
            _(u"Rollback changes"),
            wx.YES_NO|wx.ICON_QUESTION|wx.NO_DEFAULT,
            self
            )
        if confirm == wx.NO:
            return

        self.git_source_control_toggle_ui(False)
        self.m_statusBar.SetStatusText(_(u"[Git] The rollback of changes has begun..."),0)
        
        reset_worker = GitResetWorker(
            repo_obj=self.git_manager.repo,
            on_finished_callback=self.on_git_reset_async_finished
            )
        reset_worker.start()


    def on_git_reset_async_finished(self, success, error_message):
        self.git_source_control_toggle_ui(True)

        if success:
            rolled_back_files = set()
            if hasattr(self, 'git_manager') and self.git_manager and self.git_manager.status_cache:
                for rel_path in self.git_manager.status_cache.keys():
                    abs_path = os.path.normpath(os.path.join(self.current_project_path, rel_path))
                    rolled_back_files.add(abs_path.lower())

            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()

            notebook = self.m_auinotebook_Main
            total_pages = notebook.GetPageCount()

            for page_idx in range(total_pages):
                tab = notebook.GetPage(page_idx)

                if tab and hasattr(tab, 'file_path') and tab.file_path:
                    norm_tab_path = os.path.normpath(tab.file_path).lower()
                    if norm_tab_path in rolled_back_files:
                        if os.path.exists(tab.file_path) and os.path.isfile(tab.file_path):
                            enc = getattr(tab, 'current_encoding', 'utf-8')
                            try:
                                with open(tab.file_path, 'r', encoding=enc, errors="replace") as f:
                                    clean_text = f.read().replace("\r\n", "\n")

                                tab.m_scintilla_Editor.SetText(clean_text)
                                
                                tab.m_scintilla_Editor.EmptyUndoBuffer()
                                tab.m_scintilla_Editor.MarkerDeleteAll(13)
                                tab.m_scintilla_Editor.MarkerDeleteAll(14)
                                tab.m_scintilla_Editor.SetSavePoint()
                            except Exception as e:
                                SpawnLogger.error(f"Git Overwriting Open Tabs After Reset: {e}")
                                self.m_statusBar.SetStatusText(_(u"[Git] Error overwriting open tabs after reset."),0)
                        else:
                            notebook.DeletePage(page_idx)
           
            self.m_statusBar.SetStatusText(_(u"[Git] The code base has been successfully returned."),0)
        else:
            self.m_statusBar.SetStatusText(_(u"[Git] Error rolling back changes."),0)

        
    def on_git_manual_refresh(self, event):
        if not self.git_enabled or not hasattr(self, 'git_manager') or self.git_manager is None:
            return

        if not self.current_project_path:
            return

        self.m_statusBar.SetStatusText(_(u"[Git] Synchronizing the repository and updating the tree..."),0)
        self.m_treeCtrl_GitHistory.Freeze()

        try:
            if self.git_manager.is_repo:
                self.git_manager.update_statuses_cache()

                branch_name = self.git_manager.get_active_branch_name()
                self.m_statusBar.SetStatusText(_(u"[Git] Repository data has been updated."),0)
                
            self.refresh_project_tree()
        except Exception as e:
            SpawnLogger.error(f"Git Sync: {e}")
            self.m_statusBar.SetStatusText(_(u"[Git] Sync failed"),0)
        finally:
            self.m_treeCtrl_GitHistory.Thaw()
            self.m_treeCtrl_GitHistory.Refresh()
    
    def on_git_tree_item_click(self, event):
        item_id = event.GetItem()
        tree = self.m_treeCtrl_GitHistory

        if not item_id or not item_id.IsOk():
            return

        file_path = tree.GetItemData(item_id)
        if not file_path:
            return

        relative_path = os.path.relpath(file_path, self.current_project_path)
        clean_relative_path = relative_path.replace('\\', '/').strip().lower()

        if hasattr(self, "git_manager") and self.git_manager and self.git_manager.is_repo:
            status = self.git_manager.get_file_status(clean_relative_path)

            if status == "deleted":
                return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.open_file_in_tab(file_path)
        else:
            self.m_statusBar.SetStatusText(_(u"[Git] File not found."),0)
        
    def rebuild_git_changes_tree(self):
        tree = self.m_treeCtrl_GitHistory

        tree.DeleteAllItems()

        if not self.git_enabled:
            return

        
        root_node = tree.AddRoot("Root")

        created_folders = {}


        folder_icon = self.icon_indices.get("folder", 0)
        folder_opened_icon = self.icon_indices.get("folder_opened", 0)
        file_icon = self.icon_indices.get("file", 1)
        pwn_icon = self.icon_indices.get("pawn", 1)
        inc_icon = self.icon_indices.get("pawn_inc", 1)
        cfg_icon = self.icon_indices.get("cfg", 1)

        for rel_path, status in self.git_manager.status_cache.items():
            if status not in ["modified", "untracked", "staged", "deleted"]:
                continue

            parts = rel_path.replace('\\','/').split('/')
            file_name = parts[-1]
            folder_parts = parts[:-1]

            current_parent = root_node
            current_folder_path = ""

            for part in folder_parts:
                if current_folder_path:
                    current_folder_path += "/" + part
                else:
                    current_folder_path = part

                if current_folder_path not in created_folders:
                    node_id = tree.AppendItem(current_parent, part, image=folder_icon, selImage=folder_icon)
                    tree.SetItemImage(node_id, folder_opened_icon, wx.TreeItemIcon_Expanded)
                    tree.SetItemTextColour(node_id, tree.GetForegroundColour())
                    created_folders[current_folder_path] = node_id
                current_parent = created_folders[current_folder_path]

            chosen_icon = file_icon
            if file_name.endswith('.pwn'): chosen_icon = pwn_icon
            if file_name.endswith('.inc'): chosen_icon = inc_icon
            if file_name.endswith(('.json','.cfg','.ini','.yaml')): chosen_icon = cfg_icon

            if status == "modified": marker = "M"
            elif status == "untracked": marker = "U"
            elif status == "staged": marker = "A"
            elif status == "deleted": marker = "D"
            display_name = f"{file_name} [{marker}]"

            file_node = tree.AppendItem(current_parent, display_name, image=chosen_icon, selImage=chosen_icon)

            abs_file_path = os.path.normpath(os.path.join(self.current_project_path, rel_path))
            tree.SetItemData(file_node, abs_file_path)

            bg_color = tree.GetBackgroundColour()
            if status == "untracked":
                tree.SetItemTextColour(file_node, wx.Colour(34,139,34))
            elif status == "modified":
                tree.SetItemTextColour(file_node, wx.Colour(210,140,10))
            elif status == "staged":
                tree.SetItemTextColour(file_node, wx.Colour(0,128,192))
            elif status == "deleted":
                tree.SetItemTextColour(file_node, wx.Colour(200,30,30))

            tree.SetItemBackgroundColour(file_node, bg_color)
        tree.ExpandAll()

    def on_git_commit_execute_click(self, event):
        if not self.current_project_path or not self.git_manager or not self.git_manager.is_repo:
            return

        commit_msg = self.m_textCtrl_CommitText.GetValue().strip()
        if not commit_msg:
            wx.Bell()
            return

        self.git_source_control_toggle_ui(False)
        self.m_statusBar.SetStatusText(_(u"[Git] Indexing and fixing changes..."),0)

        has_staged_files = any(status == "staged" for status in self.git_manager.status_cache.values())

        commit_thread = GitCommitWorker(
            repo_obj=self.git_manager.repo,
            commit_message=commit_msg,
            has_staged=has_staged_files,
            on_finished_callback=self.on_git_commit_async_finished
            )
        commit_thread.start()

    def on_git_commit_async_finished(self, success, error_message):
        self.git_source_control_toggle_ui(True)

        if success:
            self.m_textCtrl_CommitText.SetValue("")
            if hasattr(self, 'git_manager') and self.git_manager:
                self.git_manager.update_statuses_cache()

            self.refresh_project_tree()

            #branch_name = self.git_manager.get_active_branch_name() if self.git_manager else "main"
            self.m_statusBar.SetStatusText(_(u"[Git] Checkpoint created successfully."),0)
        else:
            self.m_statusBar.SetStatusText(_(u"[Git] Error commit."),0)
    
    def apply_git_status_to_tree_item(self, tree_ctrl, item_id, absolute_path):

        if not item_id.IsOk or not self.current_project_path:
            return

        tree_ctrl.SetItemTextColour(item_id, wx.NullColour)
        tree_ctrl.SetItemBackgroundColour(item_id, wx.NullColour)

        relative_path = os.path.relpath(absolute_path, self.current_project_path)
        file_name = os.path.basename(absolute_path)
        file_ext = os.path.splitext(file_name)[-1].lower()

        status = "normal"
        if self.git_enabled and hasattr(self, "git_manager") and self.git_manager and self.git_manager.is_repo:
            status = self.git_manager.get_file_status(relative_path)

        bg_color = tree_ctrl.GetBackgroundColour()
        if status == "untracked":
            text_color = wx.Colour(34,139,34)

        elif status == "modified":
            text_color = wx.Colour(210,140,10)

        elif status == "staged":
            text_color = wx.Colour(0,128,192)

        elif status == "ignored" or file_name == ".spawn.yaml":
            text_color = wx.Colour(128,128,128)
            
        else:
            text_color = wx.Colour(30,30,30)

       
        tree_ctrl.SetItemTextColour(item_id, text_color)
        tree_ctrl.SetItemBackgroundColour(item_id, bg_color)

        font = tree_ctrl.GetItemFont(item_id)
        if font.IsOk():
            if status == "ignored":
                font.SetStyle(wx.FONTSTYLE_ITALIC)
            else:
                font.SetStyle(wx.FONTSTYLE_NORMAL)
            tree_ctrl.SetItemFont(item_id, font)
       
            

    def on_open_dependency_manager_click(self, event):
        if not self.current_project_path:
            return
        
        sampctl_bin_path = self.ide_cfg.get("system.sampctl.executable_path", "")
        with DependencyManagerDialog(self, self.current_project_path, sampctl_bin_path) as dlg:
            dlg.ShowModal()

    def on_execute_go_to_line(self, event=None):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab or not hasattr(active_tab, "m_scintilla_Editor"):
            return
        editor = active_tab.m_scintilla_Editor
        total_lines = editor.GetLineCount()

        dlg = wx.NumberEntryDialog(
            self,
            message=_(u"Enter line number:"),
            prompt=_(u"Go to line"),
            caption=_(u"Go to line"),
            value=editor.GetCurrentLine() + 1,
            min=1,
            max=total_lines
            )
        if dlg.ShowModal() == wx.ID_OK:
            target_line_human = dlg.GetValue()
            target_line_idx = target_line_human - 1

            if 0 <= target_line_idx < total_lines:
                editor.GotoLine(target_line_idx)
                editor.VerticalCentreCaret()
                editor.SetFocus()
        dlg.Destroy()

    def on_open_find_dialog(self, event):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab or not hasattr(active_tab, "m_scintilla_Editor"):
            return

        if self.active_find_dialog:
            self.active_find_dialog.Raise()
            self.active_find_dialog.SetFocus()
            return

        editor = active_tab.m_scintilla_Editor
        start, end = editor.GetSelection()
        if start != end:
            self.find_dialog_data.SetFindString(editor.GetSelectedText())

        self.active_find_dialog = wx.FindReplaceDialog(
            self,
            self.find_dialog_data,
            _(u"Search and replace"),
            style=wx.FR_REPLACEDIALOG
            )
        self.active_find_dialog.Bind(wx.EVT_FIND, self.on_find_dialog_event)
        self.active_find_dialog.Bind(wx.EVT_FIND_NEXT, self.on_find_dialog_event)
        self.active_find_dialog.Bind(wx.EVT_FIND_REPLACE, self.on_find_dialog_event)
        self.active_find_dialog.Bind(wx.EVT_FIND_REPLACE_ALL, self.on_find_dialog_event)
        

        self.active_find_dialog.Bind(wx.EVT_FIND_CLOSE, self.on_find_dialog_close)
        self.active_find_dialog.Show()

    def on_find_dialog_close(self, event):
        if self.active_find_dialog:
            self.active_find_dialog.Destroy()
            self.active_find_dialog = None

    def on_find_dialog_event(self, event):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab or not hasattr(active_tab, "m_scintilla_Editor"):
            return
        editor = active_tab.m_scintilla_Editor

        search_query = event.GetFindString()
        replace_query = event.GetReplaceString() if hasattr(event, "GetReplaceString") else ""

        if not search_query:
            return

        sys_flags = event.GetFlags()
        scintilla_search_flags = 0

        if sys_flags & wx.FR_MATCHCASE:
            scintilla_search_flags |= wx.stc.STC_FIND_MATCHCASE
        if sys_flags & wx.FR_WHOLEWORD:
            scintilla_search_flags |= wx.stc.STC_FIND_WHOLEWORD

        editor.SetSearchFlags(scintilla_search_flags)
        evt_type = event.GetEventType()

        if evt_type in (wx.wxEVT_COMMAND_FIND, wx.wxEVT_COMMAND_FIND_NEXT):
            if sys_flags & wx.FR_DOWN:
                sel_start, sel_end = editor.GetSelection()
                start_pos = sel_end if sel_start != sel_end else editor.GetCurrentPos()
                editor.SetTargetRange(start_pos, editor.GetTextLength())
            else:
                sel_start, sel_end = editor.GetSelection()
                start_pos = sel_start if sel_start != sel_end else editor.GetCurrentPos()
                editor.SetTargetRange(start_pos, 0)
            result_pos = editor.SearchInTarget(search_query)
            if result_pos != -1:
                found_line = editor.LineFromPosition(result_pos)
                editor.EnsureVisibleEnforcePolicy(found_line)
                editor.SetSelection(result_pos, result_pos + len(search_query))
            else:
                wx.Bell()
        elif evt_type == wx.wxEVT_COMMAND_FIND_REPLACE:
            sel_s, sel_e = editor.GetSelection()
            if sel_s != sel_e and editor.GetSelectedText() == search_query:
                editor.BeginUndoAction()
                try:
                    editor.ReplaceSelection(replace_query)
                except Exception as e:
                    SpawnLogger.error(f"Find / Replace: {e}")
                    
                finally:
                    editor.EndUndoAction()
            event.SetEventType(wx.wxEVT_COMMAND_FIND_NEXT)
            self.on_find_dialog_event(event)
        elif evt_type == wx.wxEVT_COMMAND_FIND_REPLACE_ALL:
            editor.Freeze()
            editor.BeginUndoAction()
            count = 0
            current_pos = 0

            try:
                while True:
                    editor.SetTargetRange(current_pos, editor.GetTextLength())
                    res = editor.SearchInTarget(search_query)
                    if res == -1:
                        break

                    editor.SetTargetRange(res, res + len(search_query))
                    editor.ReplaceTarget(replace_query)
                    current_pos = res + len(replace_query)
                    count += 1
            except Exception as e:
                SpawnLogger.error(f"Find / Replace: {e}")
                
            finally:
                editor.EndUndoAction()
                editor.Thaw()
                editor.Refresh()
                        
        

    def on_run_server_execute(self, event):
        if not self.current_project_path:
            return
        if os.name == 'nt':
            for exe_name in ["samp-server.exe", "omp-server.exe"]:
                subprocess.run(
                    ["taskkill", "/F", "/IM", exe_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                    )

        tb = self.m_auiToolBar

        if self.server_process_thread and self.server_process_thread.is_alive():
            self.m_statusBar.SetStatusText(_(u"Stopping the server..."), 0)

            self.server_process_thread.stop_server()
            return

        sampctl_bin_path = self.ide_cfg.get("system.sampctl.executable_path", "")
        if not os.path.exists(sampctl_bin_path):
            self.check_environment_on_startup()
            return

        self.m_richText_ServerConsole.Clear()

        self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, False)
        self.m_menuItem_Ensure.Enable(False)
        self.m_menuItem_ProjectClose.Enable(False)
        self.m_menuItem_CompileProject.Enable(False)
        #self.m_menuItem_CleanProject.Enable(False)
        self.m_menuItem_NewProject.Enable(False)
        self.m_menuItem_OpenProjectFolder.Enable(False)

        self.m_auinotebook_Output.SetSelection(1)
        
        self.m_mgr.Update()

        self.m_richText_ServerConsole.BeginBold()
        self.m_richText_ServerConsole.WriteText(_(u"Initializing and starting the server...\n\n"))
        self.m_richText_ServerConsole.EndBold()

        self.m_statusBar.SetStatusText(_(u"Server is running..."), 0)


        tool_item = tb.FindTool(wx.ID_TOOLBAR_RUN_STOP_SERVER)
        if tool_item:
            tool_item.SetBitmap(wx.Bitmap(os.path.join(self.icons_folder,"tb_server_stop.png"), wx.BITMAP_TYPE_PNG))
            tb.Realize()
            tb.Refresh()
            
            pane = self.m_mgr.GetPane(tb)
            if pane.IsShown():
                tb.GetContainingSizer().Layout()

        self.server_process_thread = BackgroundRunner(
            project_path=self.current_project_path,
            sampctl_executable=sampctl_bin_path,
            rich_text_ctrl=self.m_richText_ServerConsole,
            on_finished_callback=self.on_server_stopped
            )
        self.server_process_thread.start()

    def on_server_stopped(self, manual_stop):
        self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_BUILD_PROJECT, True)
        self.m_menuItem_Ensure.Enable(True)
        self.m_menuItem_ProjectClose.Enable(True)
        self.m_menuItem_CompileProject.Enable(True)
        #self.m_menuItem_CleanProject.Enable(True)
        self.m_menuItem_NewProject.Enable(True)
        self.m_menuItem_OpenProjectFolder.Enable(True)
        self.m_mgr.Update()
        
        tb = self.m_auiToolBar
        tool_item = tb.FindTool(wx.ID_TOOLBAR_RUN_STOP_SERVER)
        if tool_item:
            tool_item.SetBitmap(wx.Bitmap(os.path.join(self.icons_folder,"tb_server_run.png"), wx.BITMAP_TYPE_ANY ))
            tb.Realize()
            tb.Refresh()

            pane = self.m_mgr.GetPane(tb)
            if pane.IsShown():
                tb.GetContainingSizer().Layout()

            
            
        self.m_richText_ServerConsole.MoveEnd()

        if manual_stop:
            self.m_richText_ServerConsole.BeginBold()
            self.m_richText_ServerConsole.WriteText(_(u"\n\nThe server has been stopped successfully."))
            self.m_richText_ServerConsole.EndBold()
            self.m_statusBar.SetStatusText(_(u"The server has been stopped successfully."), 0)
        else:
            self.m_richText_ServerConsole.BeginBold()
            self.m_richText_ServerConsole.WriteText(_(u"\n\nThe server terminated unexpectedly."))
            self.m_richText_ServerConsole.EndBold()
            self.m_statusBar.SetStatusText(_(u"The server terminated unexpectedly."), 0)

        self.m_richText_ServerConsole.ShowPosition(self.m_richText_ServerConsole.GetLastPosition())
        
    def on_build_project_execute(self, event):
        if not self.current_project_path:
            return

        sampctl_bin_path = self.ide_cfg.get("system.sampctl.executable_path", "")
        if not os.path.exists(sampctl_bin_path):
            self.check_environment_on_startup()
            return

        self.on_save_all_files(None)
        self.toggle_project_ui_state(False)
        self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, False)
        self.m_menuItem_Ensure.Enable(False)
        self.m_menuItem_ProjectClose.Enable(False)
        self.m_menuItem_CompileProject.Enable(False)
        #self.m_menuItem_CleanProject.Enable(False)
        self.m_menuItem_RunStopServer.Enable(False)
        self.m_menuItem_NewProject.Enable(False)
        self.m_menuItem_OpenProjectFolder.Enable(False)
        self.m_mgr.Update()
        
        self.m_auinotebook_Output.SetSelection(0)
        
        self.m_richText_BuildOutput.Clear()

        
        
        
        selected_target = ""

        if hasattr(self, "m_choice_Builds") and self.m_choice_Builds:
            selected_target = self.m_choice_Builds.GetStringSelection()

        
        self.m_richText_BuildOutput.BeginBold()
        self.m_richText_BuildOutput.WriteText(_("Starting the server build...\n\n"))
        self.m_richText_BuildOutput.EndBold()

        self.m_statusBar.SetStatusText(_(u"Building the server..."), 0)

        compiler_thread = BackgroundCompiler(
            project_path=self.current_project_path,
            sampctl_executable=sampctl_bin_path,
            build_target=selected_target,
            extra_flags="",
            rich_text_ctrl = self.m_richText_BuildOutput,
            on_finished_callback=self.on_build_project_finished
            )
        compiler_thread.start()

    def on_build_project_finished(self, success):
        self.toggle_project_ui_state(True)

        self.m_auiToolBar.EnableTool(wx.ID_TOOLBAR_RUN_STOP_SERVER, True)
        self.m_menuItem_Ensure.Enable(True)
        self.m_menuItem_ProjectClose.Enable(True)
        self.m_menuItem_CompileProject.Enable(True)
        #self.m_menuItem_CleanProject.Enable(True)
        self.m_menuItem_RunStopServer.Enable(True)
        self.m_menuItem_NewProject.Enable(True)
        self.m_menuItem_OpenProjectFolder.Enable(True)
        self.m_mgr.Update()

        self.m_richText_BuildOutput.MoveEnd()
        self.m_richText_BuildOutput.BeginBold()
        if success:
            self.m_richText_BuildOutput.WriteText(_(u"\n\nThe build was completed successfully."))
            self.m_statusBar.SetStatusText(_(u"The build was completed successfully."), 0)
        else:
            self.m_richText_BuildOutput.WriteText(_(u"\n\nThe build completed with errors."))
            self.m_statusBar.SetStatusText(_(u"The build completed with errors."), 0)

        self.m_richText_BuildOutput.EndBold()

    def on_open_settings_tab_click(self, event):
        notebook = self.m_auinotebook_Main

        global_config_path = getattr(self.ide_cfg, "config_path", "")
        for i in range(notebook.GetPageCount()):
            tab = notebook.GetPage(i)
            if hasattr(tab, 'file_path') and tab.file_path == global_config_path:
                notebook.SetSelection(i)
                return
        self.open_file_in_tab(global_config_path)
        active_tab = notebook.GetCurrentPage()
        if active_tab:
            notebook.SetPageText(notebook.GetSelection(), _(u"Settings"))
            notebook.SetPageToolTip(notebook.GetSelection(), "")

    def on_project_tree_right_click(self, event):
        item_id = event.GetItem()
        if not item_id.IsOk():
            return

        item_data = self.m_treeCtrl_ProjectTree.GetItemData(item_id)
        if not item_data:
            return

        root_item_id = self.m_treeCtrl_ProjectTree.GetRootItem()

        absolute_path = item_data.GetPath() if hasattr(item_data, "GetPath") else str(item_data)
        if not os.path.exists(absolute_path):
            return

        is_directory = os.path.isdir(absolute_path)
        file_ext = os.path.splitext(absolute_path)[-1].lower() if not is_directory else ""

        menu = wx.Menu()
        ID_OPEN_IN_EXPLORER = 8001
        ID_SET_AS_ENTRY_POINT = 8002
        ID_CREATE_NEW_FILE = 8003
        ID_CREATE_NEW_FOLDER = 8004
        ID_DELETE_ITEM = 8005
        ID_RENAME_ITEM = 8006
        ID_TREE_OPEN_FILE = 8007
        ID_GIT_INIT = 8008
        if not is_directory:
            menu.Append(ID_TREE_OPEN_FILE, _(u"Open File"))

        if item_id == root_item_id:
            if not getattr(self, 'git_manager', None) and self.git_enabled:
                menu.Append(ID_GIT_INIT, _(u"Initialize Repository"))
                self.Bind(wx.EVT_MENU, self.on_git_init_repository_click, id=ID_GIT_INIT)
            
        if item_id != root_item_id:
            menu.Append(ID_RENAME_ITEM, _(u"Rename..."))
            
        if is_directory:
            menu.Append(ID_CREATE_NEW_FILE, _(u"Create File..."))
            menu.Append(ID_CREATE_NEW_FOLDER, _(u"Create Folder..."))
            
        else:
            #if file_ext in ['.pwn']:
                #menu.Append(ID_SET_AS_ENTRY_POINT, u"Сделать главный файлом сервера")
            pass
        
        menu.Append(ID_OPEN_IN_EXPLORER, _(u"Open in Explorer"))
        if item_id != root_item_id:
            menu.Append(ID_DELETE_ITEM, _(u"Delete"))

        self._context_selected_path = absolute_path
        self._context_selected_item_id = item_id

        self.Bind(wx.EVT_MENU, self.on_tree_open_in_explorer, id=ID_OPEN_IN_EXPLORER)
        self.Bind(wx.EVT_MENU, self.on_tree_create_file, id=ID_CREATE_NEW_FILE)
        self.Bind(wx.EVT_MENU, self.on_tree_delete_item, id=ID_DELETE_ITEM)
        self.Bind(wx.EVT_MENU, self.on_tree_create_folder, id=ID_CREATE_NEW_FOLDER)
        self.Bind(wx.EVT_MENU, self.on_tree_open_file, id=ID_TREE_OPEN_FILE)
        self.Bind(wx.EVT_MENU, self.on_tree_rename_item, id=ID_RENAME_ITEM)
        self.Bind(wx.EVT_MENU, self.on_tree_set_as_entry, id=ID_SET_AS_ENTRY_POINT)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_git_init_repository_click(self, event):
        if not self.current_project_path: return
        if not self.git_enabled: return

        self.create_gitignore()

        try:
            new_repo = Repo.init(self.current_project_path)
            git_executable = self.ide_cfg.get("system.git.executable_path", "")


            self.git_manager = GitManager(self.current_project_path, git_executable)
            self.git_manager.update_statuses_cache()

            #branch_name = self.git_manager.get_active_branch_name()
            

            self.refresh_project_tree()
        except Exception as e:
            SpawnLogger.error(f"Git Repository Initialization: {e}")
            wx.MessageBox(_(u"Failed to initialize repository"), _(u"Git Error"), wx.ID_OK|wx.ICON_ERROR, self)


    def on_tree_set_as_entry(self, event):
        absolute_file_path = getattr(self, '_context_selected_path','')
        if not absolute_file_path or not self.current_project_path:
            return
        pawn_json_path = os.path.join(self.current_project_path, "pawn.json")
        if not os.path.exists(pawn_json_path):
            wx.MessageBox(_(u"Configuration file 'pawn.json' not found!"), _(u"Error"), wx.OK | wx.ICON_ERROR)
            return
        relative_path = os.path.relpath(absolute_file_path, self.current_project_path)
        clean_json_entry_path = relative_path.replace('\\', '/')

        try:
            with open(pawn_json_path, 'r', encoding="utf-8") as f:
                config_data = json.load(f)
            config_data["entry"] = clean_json_entry_path

            with open(pawn_json_path, 'w', encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            wx.MessageBox(f"Файл '{clean_json_entry_path}' успешно назначен главным файлом сборки сервера!", u"Точка входа изменена", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            SpawnLogger.error(f"Set Entry File: {e}")
            wx.MessageBox(u"Не удалось обновить pawn.json", u"Ошибка", wx.OK | wx.ICON_ERROR)


    def on_tree_open_file(self, event):
        path = getattr(self, '_context_selected_path', '')
        if path and os.path.exists(path) and not os.path.isdir(path):
            self.open_file_in_tab(path)

    def on_tree_create_folder(self, event):
        parent_dir = getattr(self, "_context_selected_path", "")
        if not parent_dir or not os.path.isdir(parent_dir): return

        dlg = wx.TextEntryDialog(self, _(u"Enter a name for the new folder:"), _(u"Creating a folder"))
        if dlg.ShowModal() == wx.ID_OK:
            new_folder_name = dlg.GetValue().strip()
            if new_folder_name:
                full_new_dir = os.path.join(parent_dir, new_folder_name)
                try:
                    os.makedirs(full_new_dir, exist_ok=True)
                    git_executable = self.ide_cfg.get("system.git.executable_path", "")
                    if self.git_enabled and os.path.isfile(git_executable) and self.git_manager.is_repo:
                        self.git_manager.update_statuses_cache()
                    self.refresh_project_tree()
                except Exception as e:
                    SpawnLogger.error(f"Create Folder (Project Tree): {e}")
                    wx.MessageBox(_(u"Failed to create folder"), _(u"Error"), wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_tree_rename_item(self, event):
        old_path = getattr(self, '_context_selected_path','')
        if not old_path or not os.path.exists(old_path): return
        parent_dir = os.path.dirname(old_path)
        old_name = os.path.basename(old_path)
        is_dir = os.path.isdir(old_path)

        title = _(u"Renaming a folder") if is_dir else _(u"Renaming a file")
        dlg = wx.TextEntryDialog(self, _(u"Enter a new name:"), title, old_name)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.GetValue().strip()
            if not new_name or new_name == old_name:
                dlg.Destroy()
                return
            full_new_path = os.path.join(parent_dir, new_name)
            if os.path.exists(full_new_path):
                wx.MessageBox(_(u"An object with this name already exists!"), _(u"Error"), wx.OK | wx.ICON_ERROR)
                dlg.Destroy()
                return

            try:
                if hasattr(self, 'file_watcher'): self.file_watcher.pause()
                os.rename(old_path, full_new_path)
                if not is_dir:
                    for i in range(self.m_auinotebook_Main.GetPageCount()):
                        tab = self.m_auinotebook_Main.GetPage(i)
                        if hasattr(tab, 'file_path') and tab.file_path == old_path:
                            tab.file_path = full_new_path
                            self.m_auinotebook_Main.SetPageText(i, new_name)
                            self.m_auinotebook_Main.SetPageToolTip(i, full_new_path)
                            break
                else:
                    for i in range(self.m_auinotebook_Main.GetPageCount()):
                        tab = self.m_auinotebook_Main.GetPage(i)
                        if hasattr(tab, 'file_path') and tab.file_path.startswith(old_path + os.sep):
                            relative_part = os.path.relpath(tab.file_path, old_path)
                            new_file_path = os.path.join(full_new_path, relative_part)
                            tab.file_path = new_file_path
                            self.m_auinotebook_Main.SetPageToolTip(i, new_file_path)
                            
                self.refresh_project_tree()
            except Exception as e:
                SpawnLogger.error(f"Rename (Project Tree): {e}")
                wx.MessageBox(_(u"Failed to rename"), _(u"Error"), wx.OK | wx.ICON_ERROR)
            finally:
                if hasattr(self, 'file_watcher'): self.file_watcher.resume()
        dlg.Destroy()
        

    def on_tree_open_in_explorer(self, event):
        path = getattr(self, "_context_selected_path", "")
        if not path: return

        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        os.startfile(target_dir)

    def on_tree_delete_item(self, event):
        path = getattr(self, "_context_selected_path", "")
        if not path: return

        item_name = os.path.basename(path)
        msg = _(u"Are you sure you want to permanently delete '{item_name}' from hard drive?").format(item_name=item_name)

        res = wx.MessageBox(msg, _(u"Deletion confirmation"), wx.YES_NO | wx.CANCEL | wx.ICON_WARNING)
        if res == wx.YES:
            try:
                if hasattr(self, 'file_watcher'): self.file_watcher.pause()

                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

                    for i in range(self.m_auinotebook_Main.GetPageCount()):
                        tab = self.m_auinotebook_Main.GetPage(i)
                        if hasattr(tab, 'file_path') and tab.file_path == path:
                            self.m_auinotebook_Main.DeletePage(i)
                            break
                self.update_button_is_no_tabs()
                self.refresh_project_tree()
            except Exception as e:
                SpawnLogger.error(f"Delete (Project Tree): {e}")
                wx.MessageBox(_(u"Error during deletion"), _(u"Error"), wx.OK | wx.ICON_ERROR)
            finally:
                if hasattr(self, 'file_watcher'): self.file_watcher.resume()

    def on_tree_create_file(self, event):
        parent_dir = getattr(self, "_context_selected_path", "")
        if not parent_dir or not os.path.isdir(parent_dir): return

        dlg = wx.TextEntryDialog(self, _(u"Enter a name for the new file:"), _(u"Creating a file"))
        dlg.SetValue("")

        if dlg.ShowModal() == wx.ID_OK:
            new_file_name = dlg.GetValue().strip()
            if new_file_name:
                full_new_path = os.path.join(parent_dir, new_file_name)
                ext = os.path.splitext(new_file_name)[-1].lower()

                file_encoding = "utf-8"
                

                if ext in ['.pwn', '.inc']:
                    default_content = ""
                elif ext == '.json':
                    default_content = ""
                else:
                    default_content = ""

                try:
                    with open(full_new_path, "w", encoding=file_encoding, newline="") as f:
                        f.write(default_content)
                        
                        if self.git_enabled and self.git_manager.is_repo:
                            self.git_manager.update_statuses_cache()
                    self.refresh_project_tree()
                except Exception as e:
                    SpawnLogger.error(f"Create File (Project Tree): {e}")
                    wx.MessageBox(_(u"Failed to create file"), _(u"Error"), wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_new_file(self,event):
        new_tab = CustomEditorTab(self.m_auinotebook_Main, "")
        self.m_auinotebook_Main.AddPage( new_tab, "Untitled", True, wx.NullBitmap )
        new_tab.is_untitled = True
        self.update_button_is_no_tabs()
   
        self.m_statusBar.SetStatusText(u"---", 2)

    def on_open_single_file(self, event):
        with wx.FileDialog(self, _(u"Open file..."),
                           wildcard="All Files (*.pwn;*.inc;*.json;*.ini;*.cfg;*.yaml;*.txt)|*.pwn;*.inc;*.json;*.ini;*.cfg;*.yaml;*.txt|Pawn Files (*.pwn;*.inc)|*.pwn;*.inc|JSON File (*.json)|*.json|INI File (*.ini)|*.ini|Configuration File (*.cfg)|*.cfg|Configuration File (*.yaml)|*.yaml|Text File (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            chosen_file_path = fileDialog.GetPath()
            self.open_file_in_tab(chosen_file_path)

    def on_close_project_click(self, event):
        if not self.current_project_path:
            return

        if self.git_manager:
            self.git_manager.status_cache.clear()
            self.git_manager.is_repo = False
            self.git_manager.repo = None
            self.git_manager = None

        global_config_path = getattr(self.ide_cfg, "config_path", "")

        self.m_auinotebook_Main.Freeze()
        for i in reversed(range(self.m_auinotebook_Main.GetPageCount())):
            tab = self.m_auinotebook_Main.GetPage(i)
            if hasattr(tab, "m_scintilla_Editor"):
                is_modified = tab.m_scintilla_Editor.GetModify()
                is_file_missing = hasattr(tab, "file_path") and tab.file_path and not os.path.exists(tab.file_path)
                if is_modified or is_file_missing:
                    self.m_auinotebook_Main.SetSelection(i)
                    self.m_auinotebook_Main.Thaw()

                    file_name = os.path.basename(tab.file_path) if tab.file_path else u"Untitled"
                    
                    if tab.file_path == global_config_path:
                        msg = _(u"The settings file has been modified. Save it before exiting?")
                    else:
                        msg = _(u"File '{file_name}' changed or deleted. Save it before exiting?").format(file_name=file_name)
                   
                    res = wx.MessageBox(msg, _(u"Closing the project"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)

                    if res == wx.YES:
                        self.on_save_current_file(None)
                        if tab.m_scintilla_Editor.GetModify() or (hasattr(tab,"file_path") and not os.path.exists(tab.file_path)):
                            return
                    elif res == wx.CANCEL:
                        return
                    elif res == wx.NO:
                        tab.m_scintilla_Editor.SetSavePoint()
                        tab.file_path = ""
                    self.m_auinotebook_Main.Freeze()
        
        self.m_auinotebook_Main.Thaw()
        if hasattr(self, "server_process_thread") and self.server_process_thread and self.server_process_thread.is_alive():
            self.server_process_thread.stop_server()
            
        if hasattr(self, "file_watcher"):
            self.file_watcher.stop()
        self.Freeze()
        try:
            for i in range(self.m_auinotebook_Main.GetPageCount() -1, -1, -1):
                tab = self.m_auinotebook_Main.GetPage(i)
                if hasattr(tab, "file_path") and tab.file_path == global_config_path:
                    continue

                self.m_auinotebook_Main.DeletePage(i)
            
            self.update_button_is_no_tabs()
            
            self.m_treeCtrl_ProjectTree.DeleteAllItems()

            if hasattr(self, "m_treeCtrl_Symbols"):
                self.m_treeCtrl_Symbols.DeleteAllItems()

            if hasattr(self, "m_choice_Builds"):
                self.m_choice_Builds.Clear()

            if hasattr(self, "m_richText_ServerConsole"):
                self.m_richText_ServerConsole.Clear()

            if hasattr(self, "m_richText_BuildOutput"):
                self.m_richText_BuildOutput.Clear()

            if hasattr(self, "m_listCtrl_Errors"):
                self.m_listCtrl_Errors.DeleteAllItems()

            if hasattr(self, "m_listCtrl_Warnings"):
                self.m_listCtrl_Warnings.DeleteAllItems()

            self.current_project_path = None

            self.toggle_project_ui_state(False)


            self.m_statusBar.SetStatusText(_(u"The project has been successfully closed."), 0)
            self.m_statusBar.SetStatusText(u"---", 2)
            self.m_statusBar.SetStatusText(u"---", 3)
            self.m_statusBar.SetStatusText(u"---", 1)
            
            self.update_git_ui_controls_state()
            self.check_environment_on_startup()
        except Exception as e:
            SpawnLogger.error(f"Close Project: {e}")

        finally:
            self.Thaw()
            self.Layout()
            
            
        

    def on_ide_close_request(self, event):
        global_config_path = getattr(self.ide_cfg, "config_path", "")
        self.m_auinotebook_Main.Freeze()

        for i in reversed(range(self.m_auinotebook_Main.GetPageCount())):
            tab = self.m_auinotebook_Main.GetPage(i)

            if hasattr(tab, "m_scintilla_Editor"):
                is_modified = tab.m_scintilla_Editor.GetModify()
                is_file_missing = hasattr(tab, "file_path") and tab.file_path and not os.path.exists(tab.file_path)

                if is_modified or is_file_missing:
                    self.m_auinotebook_Main.SetSelection(i)
                    self.m_auinotebook_Main.Thaw()
              
                    file_name = os.path.basename(tab.file_path) if tab.file_path else u"Untitled"
                    if is_file_missing:
                        msg = _(u"File '{file_name}' was deleted from the disk externally. Save a copy of it before closing the file?").format(file_name=file_name)
                    else:
                        if tab.file_path == global_config_path:
                            msg = _(u"Settings changed. Save before exiting?")
                        else:
                            msg = _(u"File '{file_name}' changed. Save it before exiting?").format(file_name=file_name)

                    res = wx.MessageBox(msg, _(u"Saving a project"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                    if res == wx.YES:
                        self.on_save_current_file(None)
                        if tab.m_scintilla_Editor.GetModify() or (hasattr(tab,"file_path") and not os.path.exists(tab.file_path)):
                            event.Veto()
                            return
                    elif res == wx.CANCEL:
                        event.Veto()
                        return
                    elif res == wx.NO:
                        tab.m_scintilla_Editor.SetSavePoint()
                        tab.file_path = ""

                    self.m_auinotebook_Main.Freeze()

        self.m_auinotebook_Main.Thaw()

        if hasattr(self, "file_watcher"):
            self.file_watcher.stop()

        if hasattr(self, "server_process_thread") and self.server_process_thread and self.server_process_thread.is_alive():
            self.server_process_thread.stop_server()
        
        event.Skip()
        self.Destroy()

    def on_tab_closed(self, event):
        if self.m_auinotebook_Main.GetPageCount() < 1:
            self.m_statusBar.SetStatusText(u"---", 3)
            self.m_statusBar.SetStatusText(u"---", 2)
            self.m_statusBar.SetStatusText(u"---", 1)
                
        
    def on_tab_closing(self, event):
        global_config_path = getattr(self.ide_cfg, "config_path", "")
        
        page_idx = event.GetSelection()
        tab = self.m_auinotebook_Main.GetPage(page_idx)

        is_modified = tab.m_scintilla_Editor.GetModify() if hasattr(tab, "m_scintilla_Editor") else False
        is_file_missing = hasattr(tab, "file_path") and tab.file_path and not os.path.exists(tab.file_path)

        if is_modified or is_file_missing:
            file_name = os.path.basename(tab.file_path) if tab.file_path else u"Untitled"

            if is_file_missing:
                msg = _(u"File '{file_name}' was deleted from the disk externally. Save a copy of it before closing the file?").format(file_name=file_name)
            else:
                if tab.file_path == global_config_path:
                    msg = _(u"Settings changed. Save before exiting?")
                else:
                    msg = _(u"File '{file_name}' changed. Save it before exiting?").format(file_name=file_name)

            res = wx.MessageBox(msg, _(u"Closing a file"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            if res == wx.YES:
                self.m_auinotebook_Main.SetSelection(page_idx)
                self.on_save_current_file(None)

                if tab.m_scintilla_Editor.GetModify() or (hasattr(tab, "file_path") and not os.path.exists(tab.file_path)):
                    event.Veto()
            elif res == wx.CANCEL:
                event.Veto()
        wx.CallAfter(self.update_button_is_no_tabs)
        
         
    def on_new_project(self,event):
        with NewProjectDialog(self) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            project_name = dlg.m_textCtrl_ProjectName.GetValue().strip()
            full_project_path = os.path.join(dlg.m_dirPicker_ProjectLocation.GetPath(), project_name)

        if not project_name:
            wx.Bell()
            return
        self.folder_existed_before_create = os.path.exists(full_project_path)

        try:
            if not os.path.exists(full_project_path):
                os.makedirs(full_project_path)
            elif os.listdir(full_project_path):
                confirm = wx.MessageBox(
                    _(u"The specified directory already exists and is not empty!\n"
                      u"Are you sure you want to deploy the server inside this folder?"),
                    _(u"Warning"), wx.YES_NO| wx.ICON_QUESTION, self
                    )
                if confirm == wx.NO: return

            self.Enable(False)
           
            self.m_statusBar.SetStatusText(_(u"Initialization of a new server has begun..."), 0)
            sampctl_exe = self.ide_cfg.get("system.sampctl.executable_path", "")
            worker = ProjectCreateWorker(full_project_path, sampctl_exe, self.on_new_project_async_finished)
            worker.start()
        except Exception as e:
            self.Enable(True)
            self.Raise()
            SpawnLogger.error(f"Server Initialization: {e}")
            wx.MessageBox(u"{msg}".format(msg=_('Failed to start server initialization process')), _(u"Server initialization"), wx.OK|wx.ICON_ERROR, self)

    def on_new_project_async_finished(self, success, target_path):
        self.Enable(True)
        self.Raise()
        target_pawn_json = os.path.join(target_path, "pawn.json")
        print(success)
        if not success or not os.path.exists(target_pawn_json):
            self.m_statusBar.SetStatusText(_(u"Project creation was interrupted or canceled."), 0)

            if not getattr(self, "folder_existed_before_create", False) and os.path.exists(target_path):
                try:
                    if not os.listdir(target_path):
                        os.rmdir(target_path)
                except Exception:
                    SpawnLogger.error(f"New Project: {e}")
                
            wx.MessageBox(_(u"Server initialization aborted: 'pawn.json' file not found."),
                          _(u"Server initialization"), wx.OK | wx.ICON_WARNING, self)
            return

        self.on_close_project_click(None)
        self.load_project(target_path)
        self.m_statusBar.SetStatusText(_(u"The new project has been successfully created and opened."), 0)      

    def refresh_project_tree(self):
        if not self.current_project_path or not os.path.exists(self.current_project_path):
            return
   
        if self.git_enabled:
            if getattr(self, 'git_manager', None) and self.git_manager and self.git_manager.is_repo:
                self.git_manager.update_statuses_cache()
                #branch_name = self.git_manager.get_active_branch_name()
                #print(f"Git: {branch_name}")
       
            
        tree = self.m_treeCtrl_ProjectTree
        expanded_paths = set()

        def save_expanded_state(item_id):
            if not item_id.IsOk():
                return
            if tree.IsExpanded(item_id):
                item_data = tree.GetItemData(item_id)
                if item_data:
                    path = item_data.GetPath() if hasattr(item_data, 'GetPath') else str(item_data)
                    expanded_paths.add(path)
            child_id, cookie = tree.GetFirstChild(item_id)
            while child_id.IsOk():
                save_expanded_state(child_id)
                child_id, cookie = tree.GetNextChild(item_id, cookie)
        root_id = tree.GetRootItem()
        if root_id.IsOk():
            save_expanded_state(root_id)

        tree.Freeze()
        try:
            tree.DeleteAllItems()
            ProjectTreeManager.populate_tree(self.m_treeCtrl_ProjectTree, self.current_project_path, self.icon_indices)

            def restore_expanded_state(item_id):
                if not item_id.IsOk():
                    return

                item_data = tree.GetItemData(item_id)
                if item_data:
                    path = item_data.GetPath() if hasattr(item_data, 'GetPath') else str(item_data)
                    if path in expanded_paths:
                        tree.Expand(item_id)
                        
                child_id, cookie = tree.GetFirstChild(item_id)
                while child_id.IsOk():
                    restore_expanded_state(child_id)
                    child_id, cookie = tree.GetNextChild(item_id, cookie)
            new_root_id = tree.GetRootItem()
            if new_root_id.IsOk():
                restore_expanded_state(new_root_id)
        except Exception as e:
            SpawnLogger.error(f"Refresh (Project Tree): {e}")
        finally:
            tree.Thaw()
            if self.git_enabled and self.git_manager:
                self.rebuild_git_changes_tree()
            self.update_git_ui_controls_state()

        
    def find_actual_file_path_in_tree(self, parent_item, old_absolute_path):
        old_dir, old_file = os.path.split(old_absolute_path)
        old_base, old_ext = os.path.splitext(old_file)

        item, cookie = self.m_treeCtrl_ProjectTree.GetFirstChild(parent_item)
        while item.IsOk():
            path = self.m_treeCtrl_ProjectTree.GetItemData(item)
            if path and os.path.isfile(path):
                current_dir, current_file = os.path.split(path)
                current_base, current_ext = os.path.splitext(current_file)
                if current_file.lower() == old_file.lower() and current_dir.lower() != old_dir.lower():
                    return path

                if current_dir.lower() == old_dir.lower() and current_base.lower() == old_base.lower():
                    pass
            if self.m_treeCtrl_ProjectTree.ItemHasChildren(item):
                res = self.find_actual_file_path_in_tree(item, old_absolute_path)
                if res:
                    return res
            item, cookie = self.m_treeCtrl_ProjectTree.GetNextChild(parent_item, cookie)
        return None
        

    def on_open_project_folder_click(self, event):
        with wx.DirDialog(self, _(u"Select the server folder"), style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return

            chosen_path = dirDialog.GetPath()
            if not os.path.exists(os.path.join(chosen_path, "pawn.json")):
                wx.MessageBox(_(u"The file 'pawn.json' was not found in the selected folder!\n\nMake sure the folder is a server."),_(u"Opening the server folder"), wx.OK|wx.ICON_ERROR)
                return
            
            if self.current_project_path != chosen_path:
                self.on_close_project_click(None)
                self.load_project(chosen_path)

    def toggle_project_ui_state(self, enabled=False):
        project_related_ids = [wx.ID_TOGGLE_PROJECT_PANEL, wx.ID_TOGGLE_OUTPUT_PANEL, wx.ID_CLOSE_PROJECT]
        for element_id in project_related_ids:
            menu_item = self.GetMenuBar().FindItemById(element_id)
            if menu_item:
                menu_item.Enable(enabled)

            tool_item = self.m_auiToolBar.FindTool(element_id)
            if tool_item:
                self.m_auiToolBar.EnableTool(element_id, enabled)
##        if hasattr(self, "m_choice_Builds"):
##            self.m_choice_Builds.Enable(enabled)

        self.m_mgr.Update()
        self.m_auiToolBar.Realize()
        self.m_auiToolBar.Refresh()

        pane = self.m_mgr.GetPane(self.m_auiToolBar)
        if pane.IsShown():
            self.m_auiToolBar.GetContainingSizer().Layout()

    def update_button_is_no_tabs(self):
        has_pages = (self.m_auinotebook_Main.GetPageCount() > 0)
        button_ids = [wx.ID_RESET_ZOOM, wx.ID_GO_TO_LINE, wx.ID_SAVE_ALL, wx.ID_TOOLBAR_SAVE_ALL, wx.ID_FIND_REPLACE,
                      wx.ID_SAVE, wx.ID_EOL_CRLF, wx.ID_REOPEN_TO_UTF8, wx.ID_REOPEN_TO_CP1251,
                      wx.ID_EOL_LF, wx.ID_ZOOM_IN, wx.ID_ZOOM_OUT, wx.ID_CUT, wx.ID_COPY, wx.ID_PASTE, wx.ID_UNDO, wx.ID_REDO
                      ]
        for element_id in button_ids:
            menu_item = self.GetMenuBar().FindItemById(element_id)
            if menu_item:
                menu_item.Enable(has_pages)

            tool_item = self.m_auiToolBar.FindTool(element_id)
            if tool_item:
                self.m_auiToolBar.EnableTool(element_id, has_pages)
        self.m_auiToolBar.Realize()
        self.m_auiToolBar.Refresh()
        
        pane = self.m_mgr.GetPane(self.m_auiToolBar)
        if pane.IsShown():
            self.m_auiToolBar.GetContainingSizer().Layout()

    def load_project(self,path):
        try:
            self.current_project_path = path
            #self.ide_cfg.set_project(path)
            
            self.toggle_project_ui_state(True)
       
            #self.load_build_targets()
            self.file_watcher.start(path)
            
            if self.git_enabled:
                git_executable = self.ide_cfg.get("system.git.executable_path", "")
                
                self.git_manager = GitManager(path, git_executable)
                if self.git_manager.is_repo:
                    self.git_manager.update_statuses_cache()
                    branch_name = self.git_manager.get_active_branch_name()

                    if hasattr(self, 'rebuild_git_changes_tree'):
                        self.rebuild_git_changes_tree()
                    
                    self.m_statusBar.SetStatusText(_(u"The project has been successfully opened. [Git] Branch: {branch}").format(branch=branch_name), 0)
                else:
                    self.m_statusBar.SetStatusText(_(u"The project has been successfully opened."), 0)
                    self.m_treeCtrl_GitHistory.DeleteAllItems()
                    self.git_manager = None
                    
            else:
                self.m_statusBar.SetStatusText(_(u"The project has been successfully opened."), 0)
                self.m_treeCtrl_GitHistory.DeleteAllItems()
                self.git_manager = None
                
            wx.CallAfter(self.refresh_project_tree)
            
            self.update_git_ui_controls_state()
            self.check_environment_on_startup()
        except Exception as e:
            SpawnLogger.error(f"Load Project: {e}")

        #--------------------------
        

    def open_file_in_tab(self, file_path):
        for page_idx in range(self.m_auinotebook_Main.GetPageCount()):
            tab = self.m_auinotebook_Main.GetPage(page_idx)

            if hasattr(tab, 'file_path') and tab.file_path == file_path:
                self.m_auinotebook_Main.SetSelection(page_idx)
                return
            
        new_tab_page = CustomEditorTab(self.m_auinotebook_Main, file_path)

        file_name = os.path.basename(file_path)
        self.m_auinotebook_Main.AddPage( new_tab_page, file_name, True, wx.NullBitmap )

        new_page_idx = self.m_auinotebook_Main.GetPageCount() - 1
        self.m_auinotebook_Main.SetPageToolTip(new_page_idx, file_path)
        self.update_button_is_no_tabs() 

    def on_tree_item_clicked(self,event):
        item = event.GetItem()
        file_path = self.m_treeCtrl_ProjectTree.GetItemData(item)
        if file_path and os.path.isfile(file_path):
            self.open_file_in_tab(file_path)

    def on_tab_changed(self, event):
##        if self.git_enabled:
##            old_page_idx = event.GetOldSelection()
##            if old_page_idx != wx.NOT_FOUND:
##                old_tab = self.m_auinotebook_Main.GetPage(old_page_idx)
##                old_tab.m_scintilla_Editor.MarkerDeleteAll(12) #Remove all Git change markers
        
        page_idx = event.GetSelection()
        if page_idx != wx.NOT_FOUND:
            active_tab = self.m_auinotebook_Main.GetPage(page_idx)
            active_tab.update_zoom_status()

            if hasattr(active_tab, "native_eol") and active_tab.native_eol:
                current_eol = active_tab.native_eol
                current_enc = active_tab.current_encoding
                if "CRLF" in current_eol:
                    eol = "CRLF"
                    self.item_crlf.Check(True)
                    
                    enc_status = current_enc.upper()
                    eol_status = current_eol.upper()
                    self.m_statusBar.SetStatusText(f"{enc_status} | {eol_status}", 2)
                else:
                    eol = "LF"
                    self.item_lf.Check(True)

                    enc_status = current_enc.upper()
                    eol_status = current_eol.upper()
                    self.m_statusBar.SetStatusText(f"{enc_status} | {eol_status}", 2)
        event.Skip()

    def on_save_all_files(self, event):
        original_selection = self.m_auinotebook_Main.GetSelection()
        self.m_auinotebook_Main.Freeze()

        for i in range(self.m_auinotebook_Main.GetPageCount()):
            self.m_auinotebook_Main.SetSelection(i)
            self.on_save_current_file(None)

        if original_selection != wx.NOT_FOUND:
            self.m_auinotebook_Main.SetSelection(original_selection)

        self.m_auinotebook_Main.Thaw()
        self.m_statusBar.SetStatusText(_(u"All open files were saved successfully."), 0)

    @property
    def git_enabled(self):
        config_enable = self.ide_cfg.get("system.git.enable", False)
        git_executable = self.ide_cfg.get("system.git.executable_path", "")
        return bool(config_enable and git_executable and os.path.isfile(git_executable))

    def on_save_current_file(self,event):
        active_tab = self.m_auinotebook_Main.GetCurrentPage()
        if not active_tab:
            return

        if hasattr(self, "file_watcher"):
            self.file_watcher.pause()

        try:

            if hasattr(active_tab, "file_path") and active_tab.file_path and os.path.exists(active_tab.file_path):
                
                current_code_text = active_tab.m_scintilla_Editor.GetText()
                file_eol = getattr(active_tab, "native_eol", "CRLF")
                real_eol = "\r\n" if file_eol == "CRLF" else "\n"

                disk_text = current_code_text.replace("\r\n", "\n")
                disk_text = disk_text.replace("\r", "\n")
                disk_text = disk_text.replace("\n", real_eol)

                file_enc = getattr(active_tab, "current_encoding", "utf-8")
                
                try:
                    raw_bytes = disk_text.encode(file_enc, errors="strict")
                    
                    with open(active_tab.file_path, "wb") as f:
                        f.write(raw_bytes)
                except UnicodeEncodeError:
                    confirm_enc = wx.MessageBox(_(u"The current file contains invalid characters that cannot be saved in CP1251.\n\nConvert to UTF-8?"), _(u"Warning"), wx.YES_NO|wx.ICON_WARNING,self)
                    if confirm_enc == wx.NO:
                        return
                    chosen_encoding = "utf-8"
                    active_tab.native_eol = file_eol

                    raw_bytes = disk_text.encode("utf-8")

                    with open(active_tab.file_path, "wb") as f:
                        f.write(raw_bytes)
                
                    active_tab.current_encoding = chosen_encoding
                    
                    enc_status = chosen_encoding.upper()
                    eol_status = file_eol.upper()
                    self.m_statusBar.SetStatusText(f"{enc_status} | {eol_status}", 2)
                    

                #Git------------------
                if self.git_enabled:
                    if getattr(self, 'git_manager', None) and self.git_manager.is_repo:
                        self.git_manager.update_statuses_cache()
                #---------------------
                self.refresh_project_tree()

                active_tab.m_scintilla_Editor.SetSavePoint()
                self.m_statusBar.SetStatusText(_(u"File saved successfully."), 0)

##                if self.git_enabled:
##                    active_tab.m_scintilla_Editor.MarkerDeleteAll(12) #Remove all Git change markers
                
            else:
                with wx.FileDialog(self, _(u"Save file as..."), defaultDir=self.current_project_path or "", defaultFile="", wildcard="All Files (*.pwn;*.inc;*.json;*.ini;*.cfg;*.yaml;*.txt)|*.pwn;*.inc;*.json;*.ini;*.cfg;*.yaml;*.txt|Pawn Files (*.pwn;*.inc)|*.pwn;*.inc|JSON File (*.json)|*.json|INI File (*.ini)|*.ini|Configuration File (*.cfg)|*.cfg|Configuration File (*.yaml)|*.yaml|Text File (*.txt)|*.txt", style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as saveDialog:
                    if saveDialog.ShowModal() == wx.ID_CANCEL:
                        if hasattr(self, "file_watcher"): self.file_watcher.resume()
                        return
                    actual_path = saveDialog.GetPath()

                    chosen_encoding = "utf-8"
                    active_tab.native_eol = "CRLF"
                    active_tab.m_scintilla_Editor.SetEOLMode(wx.stc.STC_EOL_CRLF)
                    disk_text = active_tab.m_scintilla_Editor.GetText()

                    active_tab.file_path = actual_path
                    active_tab.is_untitled = False
                    active_tab.current_encoding = chosen_encoding
                    
                    with open(actual_path, "w", encoding=active_tab.current_encoding, newline="") as f:
                        f.write(disk_text)

                    enc_status = chosen_encoding.upper()
                    self.m_statusBar.SetStatusText(f"{enc_status} | CRLF", 2)


                    page_idx = self.m_auinotebook_Main.GetPageIndex(active_tab)
                    self.m_auinotebook_Main.SetPageText(page_idx, os.path.basename(actual_path))
                    self.m_auinotebook_Main.SetPageToolTip(page_idx, actual_path)

                    active_tab.apply_lexer_by_extension()

                    active_tab.m_scintilla_Editor.SetSavePoint()
                    #Git------------------
                    if self.git_enabled:
                        if getattr(self, 'git_manager', None) and self.git_manager.is_repo:
                            self.git_manager.update_statuses_cache()
                    #---------------------
                    self.refresh_project_tree()
                    
        except Exception as f:
            SpawnLogger.error(f"Save Current File: {f}")
        finally:
            active_tab.convert_modified_markers_to_saved()
            #Apply saves IDE settings
            global_config_path = getattr(self.ide_cfg, "config_path", "")
            if active_tab.file_path == global_config_path:
                self.ide_cfg.load()

                for i in range(self.m_auinotebook_Main.GetPageCount()):
                    loop_tab = self.m_auinotebook_Main.GetPage(i)
                    if hasattr(loop_tab, "apply_pawn_styles") and loop_tab.file_path.endswith((".pwn", ".inc")):
                        loop_tab.apply_pawn_styles()
                    elif hasattr(loop_tab, "apply_json_styles") and loop_tab.file_path.endswith(".json"):
                        loop_tab.apply_json_styles()
                self.check_environment_on_startup()
                self.m_statusBar.SetStatusText(_(u"Settings saved successfully."), 0)

                if not self.git_enabled:
                    # 1. We're deleting the manager so background processes don't touch Git.
                    if getattr(self, 'git_manager', None) and hasattr(self.git_manager, 'status_cache'):
                        self.git_manager.status_cache.clear()
                        self.git_manager.is_repo = False
                        self.git_manager.repo = None
                        self.git_manager = None
                        
                    self.git_source_control_toggle_ui(False)
                    # 2. Clearing the Git history tree in the interface
                    self.m_treeCtrl_GitHistory.DeleteAllItems()
                
            #------------------------
            if hasattr(self, "file_watcher"):
                self.file_watcher.resume()
            self.refresh_project_tree()

                
                

if __name__ == "__main__":
    sys.excepthook = global_exception_handler
        
    app = wx.App()
    app.instance_checker = wx.SingleInstanceChecker("Spawn")
    if app.instance_checker.IsAnotherRunning():
        sys.exit(0) #We don’t allow two copies to run
    
    SpawnIDE()
    app.MainLoop()
