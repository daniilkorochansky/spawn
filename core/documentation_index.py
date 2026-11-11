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
"""SQLite search/index access for the open.mp Dash/Zeal docset."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class DocumentationEntry:
    name: str
    entry_type: str
    path: str


class DocumentationIndex:
    CATEGORY_ORDER = (
        "Callback",
        "Constant",
        "Function",
        "Enum",
        "Guide",
        "Tag",
        "Section",
    )

    CATEGORY_LABELS = {
        "Callback": "Callbacks",
        "Constant": "Constants",
        "Function": "Functions",
        "Enum": "Enums",
        "Guide": "Guides",
        "Tag": "Tags",
        "Section": "Sections",
    }

    def __init__(self, docset_path: str | Path):
        self.docset_path = Path(docset_path).resolve()
        self.documents_path = (
            self.docset_path / "Contents" / "Resources" / "Documents"
        ).resolve()
        self.database_path = (
            self.docset_path / "Contents" / "Resources" / "docSet.dsidx"
        ).resolve()
        if not self.database_path.is_file() or not self.documents_path.is_dir():
            raise FileNotFoundError("The open.mp documentation index is incomplete.")

    def _connect(self):
        uri = self.database_path.as_uri() + "?mode=ro"
        return sqlite3.connect(uri, uri=True, timeout=5.0)

    @staticmethod
    def _entry(row) -> DocumentationEntry:
        return DocumentationEntry(
            name=str(row[0]),
            entry_type=str(row[1]),
            path=str(row[2]),
        )

    def get_entries(self) -> list[DocumentationEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, type, path FROM searchIndex ORDER BY type COLLATE NOCASE, name COLLATE NOCASE"
            ).fetchall()
        return [self._entry(row) for row in rows]

    def get_categories(self) -> dict[str, list[DocumentationEntry]]:
        grouped: dict[str, list[DocumentationEntry]] = {}
        for entry in self.get_entries():
            grouped.setdefault(entry.entry_type, []).append(entry)
        return grouped

    def find_exact(self, name: str) -> DocumentationEntry | None:
        term = (name or "").strip()
        if not term:
            return None

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT name, type, path
                FROM searchIndex
                WHERE name = ? COLLATE NOCASE
                ORDER BY CASE type
                    WHEN 'Callback' THEN 0
                    WHEN 'Function' THEN 1
                    WHEN 'Constant' THEN 2
                    WHEN 'Enum' THEN 3
                    WHEN 'Tag' THEN 4
                    ELSE 5
                END, name COLLATE NOCASE
                LIMIT 1
                """,
                (term,),
            ).fetchone()
        return self._entry(rows) if rows else None

    def search(self, query: str, limit: int = 250) -> list[DocumentationEntry]:
        term = (query or "").strip()
        if not term:
            return self.get_entries()

        # Escape SQL LIKE metacharacters so names containing '_' or '%' are searchable literally.
        escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT name, type, path
                FROM searchIndex
                WHERE name LIKE ? ESCAPE '\\'
                ORDER BY
                    CASE WHEN name = ? COLLATE NOCASE THEN 0
                         WHEN name LIKE ? ESCAPE '\\' THEN 1
                         ELSE 2 END,
                    name COLLATE NOCASE
                LIMIT ?
                """,
                (pattern, term, f"{escaped}%", max(1, int(limit))),
            ).fetchall()
        return [self._entry(row) for row in rows]

    def resolve_entry_url(self, entry: DocumentationEntry) -> str:
        """Resolve a SQLite path to a local file URI, preserving fragment/query."""
        parsed = urlsplit(entry.path)
        relative_path = unquote(parsed.path).replace("\\", "/")
        target = (self.documents_path / relative_path).resolve()

        try:
            target.relative_to(self.documents_path)
        except ValueError as exc:
            raise ValueError("The documentation index contains an unsafe page path.") from exc

        if not target.is_file():
            raise FileNotFoundError(f"Documentation page not found: {entry.path}")

        url = target.as_uri()
        if parsed.query:
            url += "?" + parsed.query
        if parsed.fragment:
            url += "#" + parsed.fragment
        return url

    def resolve_local_url(self, url: str) -> Path | None:
        """Return a safe local file target for WebView navigation checks."""
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "file":
            return None
        raw_path = unquote(parsed.path)
        # file:///C:/... is represented with a leading slash on Windows.
        if raw_path.startswith("/") and len(raw_path) > 3 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        candidate = Path(raw_path).resolve()
        try:
            candidate.relative_to(self.documents_path)
        except ValueError:
            return None
        return candidate
