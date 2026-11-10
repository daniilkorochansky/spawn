# -*- coding: utf-8 -*-
"""Tests for open.mp documentation validation, release metadata and recovery."""

import json
import plistlib
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from core.documentation_manager import (
    DocumentationFormatError,
    DocumentationNetworkError,
    DocumentationRelease,
    OpenMPDocumentationManager,
)


def create_valid_docset(path: Path, *, rows=None, bundle_id="openmp"):
    resources = path / "Contents" / "Resources"
    documents = resources / "Documents"
    documents.mkdir(parents=True, exist_ok=True)

    with (path / "Contents" / "Info.plist").open("wb") as stream:
        plistlib.dump({"CFBundleIdentifier": bundle_id}, stream)
    (documents / "index.html").write_text("<html>home</html>", encoding="utf-8")

    database = sqlite3.connect(resources / "docSet.dsidx")
    try:
        database.execute(
            "CREATE TABLE searchIndex "
            "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)"
        )
        database.executemany(
            "INSERT INTO searchIndex (name, type, path) VALUES (?, ?, ?)",
            rows if rows is not None else [("OnPlayerConnect", "Callback", "callbacks.html")],
        )
        database.commit()
    finally:
        database.close()
    return path


@pytest.fixture

def manager(tmp_path):
    return OpenMPDocumentationManager(config_dir=str(tmp_path / "config"))


def test_validate_docset_accepts_valid_openmp_bundle(tmp_path):
    docset = create_valid_docset(tmp_path / "openmp.docset")

    assert OpenMPDocumentationManager.validate_docset(docset) is True


@pytest.mark.parametrize(
    "bundle_id",
    ["com.example.other", ""],
)
def test_validate_docset_rejects_wrong_bundle_identifier(tmp_path, bundle_id):
    docset = create_valid_docset(tmp_path / "openmp.docset", bundle_id=bundle_id)

    assert OpenMPDocumentationManager.validate_docset(docset) is False


def test_validate_docset_rejects_missing_home_page(tmp_path):
    docset = create_valid_docset(tmp_path / "openmp.docset")
    (docset / "Contents" / "Resources" / "Documents" / "index.html").unlink()

    assert OpenMPDocumentationManager.validate_docset(docset) is False


def test_validate_docset_rejects_missing_or_invalid_search_index(tmp_path):
    docset = tmp_path / "openmp.docset"
    resources = docset / "Contents" / "Resources"
    documents = resources / "Documents"
    documents.mkdir(parents=True)
    with (docset / "Contents" / "Info.plist").open("wb") as stream:
        plistlib.dump({"CFBundleIdentifier": "openmp"}, stream)
    (documents / "index.html").write_text("home", encoding="utf-8")
    sqlite3.connect(resources / "docSet.dsidx").close()

    assert OpenMPDocumentationManager.validate_docset(docset) is False


def test_validate_docset_rejects_empty_search_index(tmp_path):
    docset = create_valid_docset(tmp_path / "openmp.docset", rows=[])

    assert OpenMPDocumentationManager.validate_docset(docset) is False


def test_validate_docset_rejects_wrong_search_index_columns(tmp_path):
    docset = create_valid_docset(tmp_path / "openmp.docset")
    database_path = docset / "Contents" / "Resources" / "docSet.dsidx"
    database = sqlite3.connect(database_path)
    try:
        database.execute("DROP TABLE searchIndex")
        database.execute("CREATE TABLE searchIndex (name TEXT, kind TEXT, path TEXT)")
        database.execute("INSERT INTO searchIndex VALUES ('x', 'Function', 'x.html')")
        database.commit()
    finally:
        database.close()

    assert OpenMPDocumentationManager.validate_docset(docset) is False


def test_get_installed_version_handles_missing_and_malformed_manifest(manager):
    assert manager.get_installed_version() is None

    manager.version_file.write_text("not json", encoding="utf-8")
    assert manager.get_installed_version() is None

    manager.version_file.write_text('{"version": "2026.11.9"}', encoding="utf-8")
    assert manager.get_installed_version() == "2026.11.9"


def test_get_installed_version_handles_non_object_manifest(manager):
    manager.version_file.write_text("null", encoding="utf-8")
    assert manager.get_installed_version() is None


def test_write_installed_version_persists_json_atomically(manager):
    manager.write_installed_version("2026.11.10")

    assert json.loads(manager.version_file.read_text(encoding="utf-8")) == {
        "version": "2026.11.10"
    }
    assert not list(manager.documentation_dir.glob(".openmp-version-*.tmp"))


def test_version_key_compares_numeric_components():
    assert OpenMPDocumentationManager._version_key("1.10.0") > (
        OpenMPDocumentationManager._version_key("1.9.9")
    )
    assert OpenMPDocumentationManager._version_key("2026.11.10") > (
        OpenMPDocumentationManager._version_key("2026.11.9")
    )


def test_is_update_available_without_manifest_treats_docset_as_old(manager):
    release = DocumentationRelease("2.0", "https://github.com/example/docset.tgz")

    assert manager.is_update_available(release) is True


def test_is_update_available_compares_installed_version(manager):
    manager.write_installed_version("1.9")

    assert manager.is_update_available(
        DocumentationRelease("1.10", "https://github.com/example/docset.tgz")
    ) is True
    assert manager.is_update_available(
        DocumentationRelease("1.9", "https://github.com/example/docset.tgz")
    ) is False
    assert manager.is_update_available(
        DocumentationRelease("1.8", "https://github.com/example/docset.tgz")
    ) is False


def test_release_size_text_formats_bytes_and_unknown_size():
    assert DocumentationRelease("1", "https://example.com/a", 512).size_text == "512 B"
    assert DocumentationRelease("1", "https://example.com/a", 1536).size_text == "1.5 KB"
    assert DocumentationRelease("1", "https://example.com/a", 0).size_text == "Unknown"


def test_fetch_latest_release_reads_feed_and_head_content_length(manager):
    response = Mock()
    response.content = (
        b"<entry><version>2026.11.10</version>"
        b"<url>https://github.com/example/openmp-docset/releases/download/v1/docset.tgz</url>"
        b"</entry>"
    )
    head_response = Mock(ok=True, headers={"Content-Length": "4096"})

    with patch("core.documentation_manager.requests.Session") as session_class:
        session = session_class.return_value
        session.get.return_value = response
        session.head.return_value = head_response

        release = manager.fetch_latest_release()

    assert release.version == "2026.11.10"
    assert release.download_url.endswith("docset.tgz")
    assert release.size_bytes == 4096
    session.get.assert_called_once()
    session.head.assert_called_once()

def test_fetch_latest_release_uses_range_probe_when_head_has_no_size(manager):
    feed_response = Mock()
    feed_response.content = (
        b"<entry><version>1.2</version>"
        b"<url>https://github.com/example/docset.tgz</url></entry>"
    )
    head_response = Mock(ok=True, headers={})
    probe_response = Mock(
        ok=False,
        status_code=206,
        headers={"Content-Range": "bytes 0-0/12345"},
    )

    with patch("core.documentation_manager.requests.Session") as session_class:
        session = session_class.return_value
        session.get.side_effect = [feed_response, probe_response]
        session.head.return_value = head_response

        release = manager.fetch_latest_release()

    assert release.size_bytes == 12345
    assert session.get.call_count == 2
    probe_response.close.assert_called_once()

def test_fetch_latest_release_rejects_invalid_xml(manager):
    response = Mock(content=b"<not-closed>")
    with patch("core.documentation_manager.requests.Session") as session_class:
        session_class.return_value.get.return_value = response

        with pytest.raises(DocumentationFormatError, match="not valid XML"):
            manager.fetch_latest_release()

def test_fetch_latest_release_rejects_missing_feed_fields(manager):
    response = Mock(content=b"<entry><version>1.0</version></entry>")
    with patch("core.documentation_manager.requests.Session") as session_class:
        session_class.return_value.get.return_value = response

        with pytest.raises(DocumentationFormatError, match="missing version or URL"):
            manager.fetch_latest_release()

def test_fetch_latest_release_rejects_untrusted_download_host(manager):
    response = Mock(
        content=(
            b"<entry><version>1.0</version>"
            b"<url>https://example.com/docset.tgz</url></entry>"
        )
    )
    with patch("core.documentation_manager.requests.Session") as session_class:
        session_class.return_value.get.return_value = response

        with pytest.raises(DocumentationFormatError, match="unexpected download URL"):
            manager.fetch_latest_release()

def test_fetch_latest_release_maps_network_errors(manager):
    with patch("core.documentation_manager.requests.Session") as session_class:
        session_class.return_value.get.side_effect = requests.ConnectionError("offline")

        with pytest.raises(DocumentationNetworkError, match="offline"):
            manager.fetch_latest_release()

def test_fetch_latest_release_maps_http_errors(manager):
    response = Mock(status_code=503)
    error = requests.HTTPError(response=response)
    with patch("core.documentation_manager.requests.Session") as session_class:
        session_class.return_value.get.side_effect = error

        with pytest.raises(DocumentationFormatError, match="HTTP 503"):
            manager.fetch_latest_release()

def test_cleanup_temp_directories_removes_abandoned_staging_dirs(manager):
    abandoned = manager.documentation_dir / ".openmp-docset-install-old"
    abandoned.mkdir()
    (abandoned / "partial.tgz").write_bytes(b"partial")
    unrelated = manager.documentation_dir / "keep-me"
    unrelated.mkdir()

    manager.cleanup_temp_directories()

    assert not abandoned.exists()
    assert unrelated.is_dir()

def test_recover_installation_removes_backup_when_target_is_valid(manager):
    create_valid_docset(manager.docset_path)
    backup = manager.documentation_dir / ".openmp.docset.previous"
    create_valid_docset(backup)

    manager.recover_installation()

    assert manager.is_installed()
    assert not backup.exists()

def test_recover_installation_preserves_invalid_backup(manager):
    backup = manager.documentation_dir / ".openmp.docset.previous"
    backup.mkdir()
    (backup / "incomplete.txt").write_text("not a docset", encoding="utf-8")

    manager.recover_installation()

    assert backup.exists()

def test_recover_installation_restores_valid_backup_when_target_is_missing(manager):
    backup = manager.documentation_dir / ".openmp.docset.previous"
    create_valid_docset(backup)

    manager.recover_installation()

    assert manager.docset_path.is_dir()
    assert manager.is_installed()
    assert not backup.exists()
