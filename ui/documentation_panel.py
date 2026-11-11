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

from __future__ import annotations

import webbrowser
from pathlib import Path
from urllib.parse import urlsplit

import wx
import wx.html2

from core.documentation_index import DocumentationEntry, DocumentationIndex

class DocumentationPanel(wx.Panel):
    """Search tree + embedded HTML viewer for the open.mp documentation."""

    def __init__(self, parent, main_window, initial_tree_height: int = 250):
        super().__init__(parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.main_window = main_window
        self.index: DocumentationIndex | None = None
        self._populating_tree = False

        self.button_back = wx.Button(self, wx.ID_ANY, "←", size=wx.Size(30, 27))
        self.button_back.SetToolTip("Back")
        self.button_forward = wx.Button(self, wx.ID_ANY, "→", size=wx.Size(30, 27))
        self.button_forward.SetToolTip("Forward")
        self.search_ctrl = wx.SearchCtrl(
            self,
            wx.ID_ANY,
            style=wx.TE_PROCESS_ENTER,
            size=wx.DefaultSize,
        )
        self.search_ctrl.SetDescriptiveText("Search documentation...")
        self.search_ctrl.ShowSearchButton(True)
        self.search_ctrl.Bind(wx.EVT_CHAR, self._on_search_char)

        self.splitter = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            style=wx.SP_3D | wx.SP_LIVE_UPDATE | wx.SP_BORDER,
        )
        self.splitter.SetMinimumPaneSize(90)
        self.tree = wx.TreeCtrl(
            self.splitter,
            wx.ID_ANY,
            style=wx.TR_DEFAULT_STYLE | wx.TR_TWIST_BUTTONS | wx.BORDER_NONE,
        )
        self.web_view = wx.html2.WebView.New(self.splitter)

        self.splitter.SplitHorizontally(
            self.tree,
            self.web_view,
            max(90, int(initial_tree_height)),
        )

        navigation_sizer = wx.BoxSizer(wx.HORIZONTAL)
        navigation_sizer.Add(self.button_back, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        navigation_sizer.Add(self.button_forward, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        navigation_sizer.Add(self.search_ctrl, 1, wx.EXPAND)

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(navigation_sizer, 0, wx.EXPAND | wx.ALL, 4)
        root_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(root_sizer)

        self.button_back.Bind(wx.EVT_BUTTON, self._on_back)
        self.button_forward.Bind(wx.EVT_BUTTON, self._on_forward)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_clear_search)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_selection)
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self._on_webview_navigating)
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self._on_webview_navigated)

        self._refresh_navigation_buttons()
        self.show_not_installed()

    @staticmethod
    def _category_label(entry_type: str) -> str:
        return DocumentationIndex.CATEGORY_LABELS.get(
            entry_type,
            entry_type if entry_type.endswith("s") else f"{entry_type}s",
        )

    def _on_search_char(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if not self.search_ctrl.GetValue().strip():
                self._reset_search()
                return

        event.Skip()

    def show_not_installed(self):
        self.index = None
        self._populating_tree = True
        try:
            self.tree.DeleteAllItems()
            root = self.tree.AddRoot("Open Multiplayer")
            self.tree.Expand(root)
        finally:
            self._populating_tree = False

        self.web_view.SetPage(
            """<!doctype html><html><head><meta charset='utf-8'>
            <style>body{font-family:Segoe UI,Arial,sans-serif;padding:28px;color:#555;}
            h2{color:#222;}p{line-height:1.5;}</style></head><body>
            <h2>Documentation</h2>
            <p>Documentation is not installed.</p>
            <p>Open <b>Help → Documentation</b> to download and install it.</p>
            </body></html>""",
            "about:blank",
        )
        self._refresh_navigation_buttons()

    def _reset_search(self):
        if not self.index:
            return

        self.search_ctrl.ChangeValue("")
        self._populate_tree(self.index.get_entries())

    def set_documentation(self, docset_path: str | Path, initial_term: str | None = None):
        """Load the SQLite index and populate the tree for an installed docset."""
        self.index = DocumentationIndex(docset_path)
        self._populate_tree(self.index.get_entries())

        if initial_term:
            return self.find_and_open(initial_term)
        return self.open_home_page()

    def _populate_tree(self, entries: list[DocumentationEntry]):
        grouped: dict[str, list[DocumentationEntry]] = {}
        for entry in entries:
            grouped.setdefault(entry.entry_type, []).append(entry)

        def order_key(entry_type: str):
            try:
                return (DocumentationIndex.CATEGORY_ORDER.index(entry_type), entry_type.lower())
            except ValueError:
                return (len(DocumentationIndex.CATEGORY_ORDER), entry_type.lower())

        self._populating_tree = True
        self.tree.Freeze()
        try:
            self.tree.DeleteAllItems()
            root = self.tree.AddRoot("Open Multiplayer")
            for entry_type in sorted(grouped, key=order_key):
                category = self.tree.AppendItem(root, self._category_label(entry_type))
                for entry in grouped[entry_type]:
                    item = self.tree.AppendItem(category, entry.name)
                    self.tree.SetItemData(item, entry)
                # Expand categories with few children; keep large sections collapsed.
##                if len(grouped[entry_type]) <= 35:
##                    self.tree.Expand(category)
            self.tree.Expand(root)
        finally:
            self.tree.Thaw()
            self._populating_tree = False

    def _on_search(self, event):
        if not self.index:
            return
        query = self.search_ctrl.GetValue().strip()
        if not query:
            self._reset_search()
            return
        entries = self.index.search(query)
        self._populate_tree(entries)
        if not entries:
            self.main_window.set_documentation_status(
                f"No documentation results for '{query}'."
            )

    def _on_clear_search(self, event):
        self._reset_search()

    def _on_tree_selection(self, event):
        if self._populating_tree or not self.index:
            return
        item_data = self.tree.GetItemData(event.GetItem())

        if isinstance(item_data, DocumentationEntry):
            self.open_entry(item_data)
        event.Skip()

    def _on_back(self, event):
        if self.web_view.CanGoBack():
            self.web_view.GoBack()

    def _on_forward(self, event):
        if self.web_view.CanGoForward():
            self.web_view.GoForward()

    def _on_webview_navigated(self, event):
        self._refresh_navigation_buttons()
        event.Skip()

    def _refresh_navigation_buttons(self):
        if hasattr(self, "web_view"):
            self.button_back.Enable(self.web_view.CanGoBack())
            self.button_forward.Enable(self.web_view.CanGoForward())

    def _on_webview_navigating(self, event):
        url = event.GetURL()
        scheme = urlsplit(url).scheme.lower()

        if scheme in {"http", "https", "mailto"}:
            webbrowser.open(url)
            event.Veto()
            return

        if scheme == "file" and self.index:
            if self.index.resolve_local_url(url) is None:
                event.Veto()
                return
        elif scheme not in {"", "about"}:
            event.Veto()
            return

        event.Skip()

    def prepare_for_update(self):
        """Release the currently displayed local page before replacing the docset."""
        self.web_view.Stop()
        self.web_view.LoadURL("about:blank")
        self.index = None
        self.search_ctrl.SetValue("")
        self._refresh_navigation_buttons()

    def open_entry(self, entry: DocumentationEntry) -> bool:
        if not self.index:
            return False
        try:
            url = self.index.resolve_entry_url(entry)
        except (OSError, ValueError) as exc:
            self.main_window.set_documentation_status(str(exc))
            return False
        self.web_view.LoadURL(url)
        return True

    def open_home_page(self) -> bool:
        if not self.index:
            return False
        home = self.index.documents_path / "index.html"
        if not home.is_file():
            return False
        self.web_view.LoadURL(home.as_uri())
        return True

    def find_and_open(self, term: str) -> bool:
        if not self.index:
            return False
        entry = self.index.find_exact(term)
        if entry is None:
            return False
        self.search_ctrl.SetValue(term)
        self._populate_tree([entry])
        return self.open_entry(entry)

    def get_sash_position(self) -> int:
        return self.splitter.GetSashPosition()

    def set_sash_position(self, position: int):
        if position > 0:
            self.splitter.SetSashPosition(position)
