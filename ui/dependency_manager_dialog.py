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
import wx.html

import os
import json
import re

import markdown

from core.dependency_worker import DependencyDownloadWorker
from core.logger import SpawnLogger

import gettext
_ = gettext.gettext

wx.ID_INSTALL_DEP = 9000
wx.ID_DEP_ENSURE = 9001
wx.ID_DEP_UNINSTALL = 9002
wx.ID_CLOSE_DEP_MANAGER = 9004

class DependencyManagerDialog ( wx.Dialog ):

    def __init__( self, parent, project_path, sampctl_bin):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Dependency Manager"), pos = wx.DefaultPosition, size = wx.Size( 800,635 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( 800,600 ), wx.DefaultSize )

        self.project_path = project_path
        self.sampctl_bin = sampctl_bin
        self.download_worker = None

        self.Bind(wx.EVT_CLOSE, self.on_close_dialog)

        bSizer_Main = wx.BoxSizer( wx.VERTICAL )

        bSizer_DependencyInstall = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Dependency = wx.StaticText( self, wx.ID_ANY, _(u"Dependency:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Dependency.Wrap( -1 )

        bSizer_DependencyInstall.Add( self.m_staticText_Dependency, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_textCtrl_Dependency = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl_Dependency.SetHint( u"user/repository (plugin://user/repository)" )

        bSizer_DependencyInstall.Add( self.m_textCtrl_Dependency, 1, wx.BOTTOM|wx.TOP, 15 )

        self.m_button_DependencyInstall = wx.Button( self, wx.ID_INSTALL_DEP, _(u"Install"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_DependencyInstall.Add( self.m_button_DependencyInstall, 0, wx.BOTTOM|wx.LEFT|wx.TOP, 15 )
        self.m_button_DependencyInstall.Bind(wx.EVT_BUTTON, self.on_install_click) 


        bSizer_Main.Add( bSizer_DependencyInstall, 0, wx.EXPAND|wx.RIGHT, 5 )

        bSizer_DependencyList = wx.BoxSizer( wx.HORIZONTAL )

        m_listBox_DependencyChoices = []
        self.m_listBox_Dependency = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox_DependencyChoices, wx.LB_HSCROLL )
        self.m_listBox_Dependency.SetMinSize( wx.Size( 200,-1 ) )
        self.m_listBox_Dependency.Bind(wx.EVT_LISTBOX, self.on_dependency_selected)

        bSizer_DependencyList.Add( self.m_listBox_Dependency, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_panel_DependencyInfo = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_SIMPLE|wx.TAB_TRAVERSAL )
        bSizer_Main_DependencyInfo = wx.BoxSizer( wx.VERTICAL )

        bSizer_Submain_DependencyInfo = wx.BoxSizer( wx.VERTICAL )

        bSizer_User = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_User = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, _(u"User: "), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_User.Wrap( -1 )

        #self.m_staticText_User.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_User.Add( self.m_staticText_User, 0, wx.LEFT|wx.TOP, 15 )

        self.m_staticText_UserInfo = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_UserInfo.Wrap( -1 )

        bSizer_User.Add( self.m_staticText_UserInfo, 0, wx.TOP, 15 )


        bSizer_Submain_DependencyInfo.Add( bSizer_User, 0, wx.EXPAND, 5 )

        bSizer_Repository = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Repository = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, _(u"Repository: "), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Repository.Wrap( -1 )

        #self.m_staticText_Repository.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Repository.Add( self.m_staticText_Repository, 0, wx.LEFT, 15 )

        self.m_staticText_RepositoryInfo = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_RepositoryInfo.Wrap( -1 )

        bSizer_Repository.Add( self.m_staticText_RepositoryInfo, 0, 0, 5 )


        bSizer_Submain_DependencyInfo.Add( bSizer_Repository, 0, wx.EXPAND, 5 )

        bSizer_Contributors = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Contributors = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, _(u"Contributors: "), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Contributors.Wrap( -1 )

        #self.m_staticText_Contributors.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Contributors.Add( self.m_staticText_Contributors, 0, wx.LEFT, 15 )

        self.m_staticText_ContributorsInfo = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_ContributorsInfo.Wrap( -1 )

        bSizer_Contributors.Add( self.m_staticText_ContributorsInfo, 0, 0, 5 )


        bSizer_Submain_DependencyInfo.Add( bSizer_Contributors, 0, wx.EXPAND, 5 )

        self.m_staticText_Description = wx.StaticText( self.m_panel_DependencyInfo, wx.ID_ANY, _(u"Description:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Description.Wrap( -1 )

        #self.m_staticText_Description.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        bSizer_Submain_DependencyInfo.Add( self.m_staticText_Description, 0, wx.LEFT|wx.RIGHT|wx.TOP, 15 )

        self.m_htmlWin_Readme = wx.html.HtmlWindow( self.m_panel_DependencyInfo, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_NO_SELECTION|wx.html.HW_SCROLLBAR_AUTO )
        self.m_htmlWin_Readme.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        bSizer_Submain_DependencyInfo.Add( self.m_htmlWin_Readme, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 15 )


        bSizer_Main_DependencyInfo.Add( bSizer_Submain_DependencyInfo, 1, wx.EXPAND, 5 )

        bSizer_InfoButtons = wx.BoxSizer( wx.HORIZONTAL )

        self.m_buttonEnsure = wx.Button( self.m_panel_DependencyInfo, wx.ID_DEP_ENSURE, _(u"Ensure"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonEnsure.Bind(wx.EVT_BUTTON, self.on_ensure_all) 

        bSizer_InfoButtons.Add( self.m_buttonEnsure, 0, wx.BOTTOM, 5 )

        self.m_buttonUninstall = wx.Button( self.m_panel_DependencyInfo, wx.ID_DEP_UNINSTALL, _(u"Uninstall"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonUninstall.Bind(wx.EVT_BUTTON, self.on_uninstall_click)
        bSizer_InfoButtons.Add( self.m_buttonUninstall, 0, wx.LEFT, 5 )


        bSizer_Main_DependencyInfo.Add( bSizer_InfoButtons, 0, wx.ALIGN_RIGHT|wx.BOTTOM|wx.RIGHT, 15 )


        self.m_panel_DependencyInfo.SetSizer( bSizer_Main_DependencyInfo )
        self.m_panel_DependencyInfo.Layout()
        bSizer_Main_DependencyInfo.Fit( self.m_panel_DependencyInfo )
        bSizer_DependencyList.Add( self.m_panel_DependencyInfo, 1, wx.EXPAND |wx.ALL, 5 )


        bSizer_Main.Add( bSizer_DependencyList, 1, wx.EXPAND, 5 )

        sbSizerGroupBoxStatus = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Process") ), wx.VERTICAL )

        bSizer_Downloading = wx.BoxSizer( wx.HORIZONTAL )

        self.m_gaugeProgress = wx.Gauge( sbSizerGroupBoxStatus.GetStaticBox(), wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.m_gaugeProgress.SetValue( 0 )
        bSizer_Downloading.Add( self.m_gaugeProgress, 1, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 15 )


        sbSizerGroupBoxStatus.Add( bSizer_Downloading, 0, wx.EXPAND, 5 )

        bSizer_DownloadingStatus = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText_Status = wx.StaticText( sbSizerGroupBoxStatus.GetStaticBox(), wx.ID_ANY, _(u"Status: "), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_Status.Wrap( -1 )

        bSizer_DownloadingStatus.Add( self.m_staticText_Status, 0, wx.LEFT, 15 )

        self.m_staticText_CurrentDownStatus = wx.StaticText( sbSizerGroupBoxStatus.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, wx.ST_ELLIPSIZE_MIDDLE )
        self.m_staticText_CurrentDownStatus.Wrap( -1 )

        bSizer_DownloadingStatus.Add( self.m_staticText_CurrentDownStatus, 0, wx.RIGHT, 15 )


        sbSizerGroupBoxStatus.Add( bSizer_DownloadingStatus, 1, wx.EXPAND, 5 )


        bSizer_Main.Add( sbSizerGroupBoxStatus, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

        self.m_button_close = wx.Button( self, wx.ID_CLOSE_DEP_MANAGER, _(u"Close"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_Main.Add( self.m_button_close, 0, wx.ALIGN_RIGHT|wx.ALL, 15 )
        self.m_button_close.Bind(wx.EVT_BUTTON, self.close_dialog_clicked)


        self.SetSizer( bSizer_Main )
        self.Layout()

        self.Centre( wx.BOTH )

        self.load_current_dependencies()

    def close_dialog_clicked(self, event):
        if self.download_worker and self.download_worker.is_alive():
            res = wx.MessageBox(
                _(u"A dependency is being processed! Are you sure you want to abort the operation?"),
                _(u"Working with dependency"),
                wx.YES_NO | wx.ICON_WARNING,
                self
                )
            if res == wx.NO:
                return
        self.Destroy()


    def on_dependency_selected(self, event):
        
        selection = self.m_listBox_Dependency.GetStringSelection()
        if not selection:
            return

        if selection.startswith("plugin://"):
            selection = selection.replace("plugin://", "")
        elif selection.startswith("component://"):
            selection = selection.replace("component://", "")
        elif selection.startswith("filterscript://"):
            selection = selection.replace("filterscript://", "")

        if "@" in selection:
            selection = selection.split("@")[0].strip()

        clean_repo = selection.split(":")[0].strip()
        if "/" in clean_repo:
            clean_folder_name = clean_repo.split("/")[-1].strip()
        else:
            clean_folder_name = clean_repo
            
        dep_folder_path = os.path.join(self.project_path, "dependencies", clean_folder_name)
        

        dep_json_path = os.path.join(dep_folder_path, "pawn.json")
       
        if os.path.exists(dep_json_path):
            try:
                with open(dep_json_path, 'r', encoding='utf-8') as f:
                    dep_data = json.load(f)

                user_name = dep_data.get("user", "-")
                self.m_staticText_UserInfo.SetLabel(user_name)
                repo_name = dep_data.get("repo", "-")
                self.m_staticText_RepositoryInfo.SetLabel(repo_name)

                if "contributors" in dep_data and isinstance(dep_data["contributors"], list):
                    contributors = ", ".join(dep_data["contributors"])
                    self.m_staticText_ContributorsInfo.SetLabel(contributors)
            except Exception as e:
                SpawnLogger.error(f"Parsing Selected Item (Dependency Manager): {e}")
                
        readme_html_content = ""
        for name in ["README.md", "readme.md", "Readme.md", "ReadMe.md", "readMe.md"]:
            readme_path = os.path.join(dep_folder_path, name)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors="replace") as f:
                        md_text = f.read()

                    readme_html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
                    break
                except Exception as e:
                    SpawnLogger.error(f"Read README.md (Dependency Manager): {e}")

        style = """
        <style>
        body {
            font-family: Segoe UI;
            font-size: 10pt;
            margin: 8px;
        }

        code {
            font-family: Consolas;
        }
        </style>
        """

        readme_html_content = re.sub(r'<img[^>]*>','',readme_html_content,flags=re.IGNORECASE)
        readme_html_content = re.sub(r'<a\b[^>]*>(.*?)</a>',r'\1',readme_html_content,flags=re.IGNORECASE | re.DOTALL)

        readme_html_content = re.sub(r'<pre><code[^>]*>','<table bgcolor="#F5F5F5" width="100%"><tr><td><pre>',readme_html_content,flags=re.IGNORECASE)
        readme_html_content = re.sub(r'</code></pre>','</pre></td></tr></table>',readme_html_content,flags=re.IGNORECASE)
        
        final_html = f"""
        <html>
        <body>
        {readme_html_content}
        </body>
        </html>
        """
        
        html = style + final_html
        self.m_htmlWin_Readme.SetPage(html)
                

    def on_close_dialog(self, event):
        if self.download_worker and self.download_worker.is_alive():
            res = wx.MessageBox(
                _(u"A dependency is being processed! Are you sure you want to abort the operation?"),
                _(u"Working with dependency"),
                wx.YES_NO | wx.ICON_WARNING,
                self
                )
            if res == wx.NO:
                return
        event.Skip()

    def on_uninstall_click(self, event):
        selection = self.m_listBox_Dependency.GetStringSelection()
        if not selection:
            wx.Bell()
            return

        res = wx.MessageBox(_(u"Do you really want to remove the dependency {selection} from the project?").format(selection=selection),
                            _(u"Deletion confirmation"), wx.YES_NO | wx.ICON_QUESTION)
        if res == wx.NO: return

        self.m_gaugeProgress.SetValue(0)
        self.m_staticText_CurrentDownStatus.SetLabel(_(u"Removing a dependency {selection}").format(selection=selection))

        self.m_textCtrl_Dependency.Enable(False)
        self.m_button_DependencyInstall.Enable(False)
        self.m_buttonEnsure.Enable(False)
        self.m_buttonUninstall.Enable(False)

        self.download_worker = DependencyDownloadWorker(
            project_path=self.project_path,
            sampctl_bin=self.sampctl_bin,
            package_url=selection,
            ui_callback=self.update_download_progress_callback,
            add_command="uninstall"
            )
        self.download_worker.start()

    def on_ensure_all(self, event):
        self.m_gaugeProgress.SetValue(0)
        self.m_staticText_CurrentDownStatus.SetLabel(_(u"Start checking dependencies..."))

        self.download_worker = DependencyDownloadWorker(
            project_path=self.project_path,
            sampctl_bin=self.sampctl_bin,
            package_url="",
            ui_callback=self.update_download_progress_callback,
            add_command="ensure"
            )
        self.download_worker.start()

    def on_install_click(self, event):
        url = self.m_textCtrl_Dependency.GetValue().strip()
        if not url:
            wx.Bell()
            return

        self.m_textCtrl_Dependency.Enable(False)
        self.m_button_DependencyInstall.Enable(False)
        self.m_buttonEnsure.Enable(False)
        self.m_buttonUninstall.Enable(False)
       

        self.m_staticText_CurrentDownStatus.SetLabel(_(u"Installing dependency..."))
        self.download_worker = DependencyDownloadWorker(
            project_path=self.project_path,
            sampctl_bin=self.sampctl_bin,
            package_url=url,
            ui_callback=self.update_download_progress_callback,
            add_command="install"
            )
        self.download_worker.start()

    def update_download_progress_callback(self, percent, text):
        if percent == -1:
            self.m_gaugeProgress.SetValue(0)
            self.m_staticText_CurrentDownStatus.SetLabel(text)
            self.m_textCtrl_Dependency.Enable(True)
            self.m_button_DependencyInstall.Enable(True)
            self.m_buttonEnsure.Enable(True)
            self.m_buttonUninstall.Enable(True)
            
        elif percent == 100:
            self.m_gaugeProgress.SetValue(100)
            self.m_staticText_CurrentDownStatus.SetLabel(_(u"The process has been completed successfully."))
            self.m_textCtrl_Dependency.Enable(True)
            self.m_textCtrl_Dependency.SetValue("")
            self.m_button_DependencyInstall.Enable(True)
            self.m_buttonEnsure.Enable(True)
            self.m_buttonUninstall.Enable(True)

            self.load_current_dependencies()

            main_win = self.GetParent()
            if main_win:
                main_win.refresh_project_tree()
        else:
            #Downloading in progress
            self.m_staticText_CurrentDownStatus.SetLabel(text)
            self.m_gaugeProgress.SetValue(percent)

    def load_current_dependencies(self):
        deps_list = self.m_listBox_Dependency
        deps_list.Clear()
        
        pawn_json_path = os.path.join(self.project_path, "pawn.json")
        dependencies_folder = os.path.join(self.project_path, "dependencies")
        
        if not os.path.exists(pawn_json_path):
            return
        
        try:
            with open(pawn_json_path, 'r', encoding="utf-8", errors="replace") as f:
                pawn_data = json.load(f)

            json_dependencies = pawn_data.get("dependencies", [])
            if not isinstance(json_dependencies, list):
                return

            for raw_string in json_dependencies:
                
                raw_string = str(raw_string).strip()
                if not raw_string:
                    continue

                clean_pkg = raw_string.replace(":", "@")

                version = "latest"
                if "@" in clean_pkg:
                    parts = clean_pkg.split("@")
                    pkg_path = parts[0]
                    version = parts[1]
                else:
                    pkg_path = clean_pkg

                if "/" in pkg_path:
                    path_parts = pkg_path.split("/")
                    author_name = path_parts[0]
                    repo_name = path_parts[1]
                else:
                    author_name = ""
                    repo_name = pkg_path

                actual_dep_dir = os.path.normpath(os.path.join(dependencies_folder, repo_name))
                
                is_installed = os.path.exists(actual_dep_dir) and os.path.isdir(actual_dep_dir) and os.path.exists(os.path.join(actual_dep_dir, "pawn.json"))
              
                if is_installed:
                    deps_list.Append(raw_string)
        except Exception as e:
            SpawnLogger.error(f"Load Dependencies (Dependency Manager): {e}")
        
    def __del__( self ):
        pass


