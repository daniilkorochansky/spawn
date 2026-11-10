# -*- coding: utf-8 -*-
"""Tests for the SQLite-backed open.mp documentation index."""

import sqlite3
from pathlib import Path

import pytest

from core.documentation_index import DocumentationEntry, DocumentationIndex


def create_docset(root: Path, rows=None, *, create_index=True, create_documents=True):
    """Create a small Dash/Zeal docset suitable for index tests."""
    resources = root / "Contents" / "Resources"
    documents = resources / "Documents"

    if create_documents:
        documents.mkdir(parents=True, exist_ok=True)
        (documents / "index.html").write_text("<html>home</html>", encoding="utf-8")

    if create_index:
        resources.mkdir(parents=True, exist_ok=True)
        database = sqlite3.connect(resources / "docSet.dsidx")
        try:
            database.execute(
                "CREATE TABLE searchIndex "
                "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)"
            )
            database.executemany(
                "INSERT INTO searchIndex (name, type, path) VALUES (?, ?, ?)",
                rows or [("OnPlayerConnect", "Callback", "callbacks.html#OnPlayerConnect")],
            )
            database.commit()
        finally:
            database.close()

    return root


def test_init_rejects_incomplete_docset(tmp_path):
    with pytest.raises(FileNotFoundError, match="index is incomplete"):
        DocumentationIndex(tmp_path / "missing.docset")


def test_get_entries_returns_sorted_entries(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [
            ("ZCMD", "Function", "functions.html#ZCMD"),
            ("OnPlayerConnect", "Callback", "callbacks.html#OnPlayerConnect"),
            ("AddPlayerClass", "Function", "functions.html#AddPlayerClass"),
        ],
    )
    index = DocumentationIndex(docset)

    entries = index.get_entries()

    assert [entry.name for entry in entries] == [
        "OnPlayerConnect",
        "AddPlayerClass",
        "ZCMD",
    ]
    assert all(isinstance(entry, DocumentationEntry) for entry in entries)


def test_get_categories_groups_entries_by_type(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [
            ("OnPlayerConnect", "Callback", "callbacks.html"),
            ("OnPlayerDisconnect", "Callback", "callbacks.html"),
            ("SetPlayerPos", "Function", "functions.html"),
        ],
    )

    categories = DocumentationIndex(docset).get_categories()

    assert set(categories) == {"Callback", "Function"}
    assert [entry.name for entry in categories["Callback"]] == [
        "OnPlayerConnect",
        "OnPlayerDisconnect",
    ]


def test_find_exact_is_case_insensitive_and_prefers_callbacks(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [
            ("PlayerAction", "Function", "functions.html"),
            ("PlayerAction", "Callback", "callbacks.html"),
        ],
    )
    index = DocumentationIndex(docset)

    result = index.find_exact("  playeraction  ")

    assert result is not None
    assert result.entry_type == "Callback"
    assert index.find_exact("  ") is None
    assert index.find_exact("not_a_real_symbol") is None


def test_search_is_case_insensitive_and_orders_exact_match_first(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [
            ("GetPlayerName", "Function", "functions.html"),
            ("PlayerName", "Function", "functions.html"),
            ("SetPlayerName", "Function", "functions.html"),
        ],
    )

    results = DocumentationIndex(docset).search("playername")

    assert [entry.name for entry in results] == [
        "PlayerName",
        "GetPlayerName",
        "SetPlayerName",
    ]


def test_search_escapes_sql_like_wildcards(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [
            ("Set_Player_Name", "Function", "functions.html"),
            ("SetXPlayerXName", "Function", "functions.html"),
            ("Percent%Value", "Constant", "constants.html"),
        ],
    )
    index = DocumentationIndex(docset)

    underscore_results = index.search("_")
    percent_results = index.search("%")

    assert [entry.name for entry in underscore_results] == ["Set_Player_Name"]
    assert [entry.name for entry in percent_results] == ["Percent%Value"]


def test_search_empty_query_returns_all_entries_and_limit_is_clamped(tmp_path):
    docset = create_docset(
        tmp_path / "openmp.docset",
        [(f"Function{i}", "Function", "functions.html") for i in range(3)],
    )
    index = DocumentationIndex(docset)

    assert len(index.search("   ")) == 3
    assert len(index.search("Function", limit=0)) == 1


def test_resolve_entry_url_preserves_query_fragment_and_decodes_path(tmp_path):
    docset = create_docset(tmp_path / "openmp.docset")
    documents = docset / "Contents" / "Resources" / "Documents"
    page = documents / "api reference.html"
    page.write_text("<html>api</html>", encoding="utf-8")
    index = DocumentationIndex(docset)

    url = index.resolve_entry_url(
        DocumentationEntry("Example", "Guide", "api%20reference.html?mode=full#section-a")
    )

    assert url.startswith(page.as_uri())
    assert "?mode=full#section-a" in url


def test_resolve_entry_url_rejects_path_traversal(tmp_path):
    docset = create_docset(tmp_path / "openmp.docset")
    index = DocumentationIndex(docset)

    with pytest.raises(ValueError, match="unsafe page path"):
        index.resolve_entry_url(
            DocumentationEntry("Escape", "Guide", "%2e%2e/outside.html")
        )


def test_resolve_entry_url_rejects_missing_page(tmp_path):
    docset = create_docset(tmp_path / "openmp.docset")
    index = DocumentationIndex(docset)

    with pytest.raises(FileNotFoundError, match="Documentation page not found"):
        index.resolve_entry_url(DocumentationEntry("Missing", "Guide", "missing.html"))


def test_resolve_local_url_allows_only_files_inside_documents(tmp_path):
    docset = create_docset(tmp_path / "openmp.docset")
    documents = docset / "Contents" / "Resources" / "Documents"
    local_page = documents / "guide.html"
    local_page.write_text("guide", encoding="utf-8")
    outside_page = tmp_path / "outside.html"
    outside_page.write_text("outside", encoding="utf-8")
    index = DocumentationIndex(docset)

    assert index.resolve_local_url(local_page.as_uri()) == local_page.resolve()
    assert index.resolve_local_url(outside_page.as_uri()) is None
    assert index.resolve_local_url("https://example.com") is None


def test_resolve_local_url_decodes_percent_encoded_paths(tmp_path):
    docset = create_docset(tmp_path / "openmp.docset")
    documents = docset / "Contents" / "Resources" / "Documents"
    page = documents / "guide page.html"
    page.write_text("guide", encoding="utf-8")
    index = DocumentationIndex(docset)

    assert index.resolve_local_url(page.as_uri()) == page.resolve()
