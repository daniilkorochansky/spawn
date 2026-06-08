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

from git import Repo

class GitManager: 
    def __init__(self, project_path, git_exe_path=""):
        self.project_path = project_path
        self.git_exe = git_exe_path
        self.is_repo = False
        self.repo = None
        #Кэш статусов
        self.status_cache = {}

        if self.git_exe and os.path.exists(self.git_exe):
            os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = self.git_exe

        #Первичная проверка
        self.check_repository()

    def check_repository(self):
        if not self.project_path or not os.path.exists(self.project_path):
            self.is_repo = False
            return

        git_dir = os.path.join(self.project_path, ".git")
        if os.path.exists(git_dir) and os.path.isdir(git_dir):
            try:
                self.repo = Repo(self.project_path)
                self.is_repo = True
            except Exception as e:
                print(f"Не удалось открыть репозиторий: {e}")
                self.is_repo = False
        else:
            self.is_repo = False

        return self.is_repo

    def get_active_branch_name(self):
        if not self.is_repo or not self.repo:
            return ""
        try:
            return self.repo.active_branch.name
        except Exception:
            return "detached"
    
    def update_statuses_cache(self):
        #Сканирует репозиторий через GitPython и обновляет словарь кэша

        self.status_cache.clear()
        if not self.is_repo or not self.repo:
            return
        try:
            self.repo.git.status(porcelain=True)
        except Exception:
            pass
        
        try:
            for diff_item in self.repo.index.diff(None):
                path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                if path:
                    clean_path = str(path).strip('"').replace('\\','/').strip().lower()
                    if diff_item.change_type == 'D':
                        self.status_cache[clean_path] = "deleted"
                    else:
                        self.status_cache[clean_path] = "modified"
        except Exception as e:
            print(f"Ошибка чтения изменённых файлов: {e}")

        try:
            if not self.repo.head.is_valid():
                for key_item in self.repo.index.entries.keys():
                    path = key_item[0] if isinstance(key_item, tuple) else key_item

                    if path:
                        clean_path = str(path).strip('"').replace('\\','/').strip().lower()
                        if clean_path not in self.status_cache:
                            self.status_cache[clean_path] = "staged"
            else:
                for diff_item in self.repo.index.diff("HEAD"):
                    path = diff_item.a_path if diff_item.a_path else diff_item.b_path
                    if path:
                        clean_path = str(path).strip('"').replace('\\','/').strip().lower()
                        if clean_path not in self.status_cache:
                            self.status_cache[clean_path] = "staged"
        except Exception as e:
            print(f"[Git Cache] Варнинг HEAD-индекса: {e}")

        try:
            for untracked_file in self.repo.untracked_files:
                if untracked_file:
                    clean_path = str(untracked_file).strip('"').replace('\\','/').strip().lower()
                    if clean_path not in self.status_cache:
                        self.status_cache[clean_path] = "untracked"
        except Exception as e:
            print(f"[Git Cache] Ошибка чтения новых файлов: {e}")

        try:
            ignored_raw = self.repo.git.status("--ignored", "--porcelain")
            for line in ignored_raw.splitlines():
                if line.startswith("!! "):
                    path = line[3:].strip().strip('"')
                    clean_path = path.replace('\\','/').strip().lower()
                    if clean_path not in self.status_cache:
                        self.status_cache[clean_path] = "ignored"
        except Exception as e:
            print(f"[Git Cache] Ошибка чтения .gitignore: {e}")
        #print(f"[Git Ram] Текущий кэш: {self.status_cache}")

    def get_file_status(self, relative_path):
        #Возвращает статус конкретного файла

        clean_path = relative_path.replace('\\','/').strip().lower()
        return self.status_cache.get(clean_path, "normal")

            
