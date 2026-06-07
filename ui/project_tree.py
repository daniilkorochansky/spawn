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

class ProjectTreeManager:
    @staticmethod
    def populate_tree(tree_ctrl, root_path, icon_indices):
        """Принимает ГОТОВОЕ дерево из GUI и заполняет его файлами"""
        tree_ctrl.Freeze()  # Замораживаем отрисовку, чтобы дерево не моргало
        tree_ctrl.DeleteAllItems()
        
        if not os.path.exists(root_path):
            tree_ctrl.Thaw()
            return

        # Создаем главный корень (имя открытой папки сервера)
        root_name = os.path.basename(root_path) or root_path
        root_node = tree_ctrl.AddRoot(root_name, image=icon_indices["folder_root"])
        tree_ctrl.SetItemImage(root_node, icon_indices["folder_root_opened"], wx.TreeItemIcon_Expanded)
        
        # Привязываем полный путь к корню
        tree_ctrl.SetItemData(root_node, root_path)
        
        # Сканируем директорию
        ProjectTreeManager._scan_directory(tree_ctrl, root_node, root_path, icon_indices)
        
        tree_ctrl.Expand(root_node)
        tree_ctrl.Thaw()

    @staticmethod
    def _scan_directory(tree_ctrl, parent_node, current_path, icon_indices):
        main_win = wx.GetTopLevelParent(tree_ctrl)
        try:
            items = os.listdir(current_path)
            dirs, files = [], []
            
            for item in items:
                if item.startswith('.') or item.lower() == "dependencies" or item.lower() == "components" or item.lower() == "plugins" or item == ".git" or item == "sampctl_build_file.inc":
                    continue
                    
                full_path = os.path.join(current_path, item)
                if os.path.isdir(full_path):
                    dirs.append((item, full_path))
                else:
                    if item.endswith(('.pwn', '.inc', '.json', '.txt', '.cfg', '.ini', '.yaml', '.lock')):
                        files.append((item, full_path))
            
            dirs.sort(key=lambda x: x[0].lower())
            files.sort(key=lambda x: x[0].lower())
            
            for name, path in dirs:
                node = tree_ctrl.AppendItem(parent_node, name, image=icon_indices["folder"])

                tree_ctrl.SetItemImage(node, icon_indices["folder_opened"], wx.TreeItemIcon_Expanded)
                
                tree_ctrl.SetItemData(node, path)
                if main_win and hasattr(main_win, 'apply_git_status_to_tree_item'):
                    main_win.apply_git_status_to_tree_item(tree_ctrl, node, path)
                ProjectTreeManager._scan_directory(tree_ctrl, node, path, icon_indices)
                
            for name, path in files:
                chosen_icon_idx = icon_indices["file"]

                if name.endswith('.pwn'):
                    chosen_icon_idx = icon_indices["pawn"]
                elif name.endswith('.inc'):
                    chosen_icon_idx = icon_indices["pawn_inc"]
                elif name.endswith(('.json', '.ini','.cfg', '.yaml','.lock')):
                    chosen_icon_idx = icon_indices["cfg"]
                node = tree_ctrl.AppendItem(parent_node, name, image=chosen_icon_idx)

                #Git---------------------
                
               
                if main_win and hasattr(main_win, "apply_git_status_to_tree_item"):
                    main_win.apply_git_status_to_tree_item(tree_ctrl, node, path)
                #------------------------
                tree_ctrl.SetItemData(node, path)

                
        except Exception:
            pass
