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

from git import Repo

from core.git_manager import GitManager


def test_nonexistent_directory_is_not_repository():
    manager = GitManager("C:/path/that/does/not/exist")

    assert manager.is_repo is False
    assert manager.repo is None


def test_detect_git_repository(tmp_path):
    Repo.init(tmp_path)

    manager = GitManager(str(tmp_path))

    assert manager.is_repo is True
    assert manager.repo is not None


def test_get_active_branch_name(tmp_path):
    Repo.init(tmp_path)

    manager = GitManager(str(tmp_path))

    branch_name = manager.get_active_branch_name()

    assert isinstance(branch_name, str)
    assert len(branch_name) > 0


def test_get_unknown_file_status_returns_normal():
    manager = GitManager("")

    assert manager.get_file_status("main.pwn") == "normal"


def test_untracked_file_status(tmp_path):
    Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"
    file_path.write_text("main() {}")

    manager = GitManager(str(tmp_path))

    manager.update_statuses_cache()

    assert manager.get_file_status("main.pwn") == "untracked"


def test_ignored_directory_status(tmp_path):
    Repo.init(tmp_path)

    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("plugins/\n")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    (plugins_dir / "test.dll").write_text("dummy")

    manager = GitManager(str(tmp_path))

    manager.update_statuses_cache()

    assert manager.get_file_status("plugins/") == "ignored"


def test_path_normalization(tmp_path):
    Repo.init(tmp_path)

    file_path = tmp_path / "Main.pwn"
    file_path.write_text("main() {}")

    manager = GitManager(str(tmp_path))

    manager.update_statuses_cache()

    assert manager.get_file_status("MAIN.PWN") == "untracked"
    assert manager.get_file_status("main.pwn") == "untracked"
    assert manager.get_file_status("Main.pwn") == "untracked"

def test_modified_file_status(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"
    file_path.write_text("main() {}")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    file_path.write_text("main()\n{\n    print(\"Hello\");\n}")

    manager = GitManager(str(tmp_path))

    manager.update_statuses_cache()

    assert manager.get_file_status("main.pwn") == "modified"

def test_staged_file_status(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"
    file_path.write_text("main() {}")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    file_path.write_text("main()\n{\n    print(\"Hello\");\n}")

    repo.index.add(["main.pwn"])

    manager = GitManager(str(tmp_path))

    manager.update_statuses_cache()

    assert manager.get_file_status("main.pwn") == "staged"

def test_detached_head_returns_detached(tmp_path):
    repo = Repo.init(tmp_path)

    file_path = tmp_path / "main.pwn"
    file_path.write_text("main() {}")

    repo.index.add(["main.pwn"])
    repo.index.commit("Initial commit")

    commit_hash = repo.head.commit.hexsha

    repo.git.checkout(commit_hash)

    manager = GitManager(str(tmp_path))

    assert manager.get_active_branch_name() == "detached"
