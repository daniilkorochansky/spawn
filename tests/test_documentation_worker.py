# -*- coding: utf-8 -*-
"""Tests for safe archive handling and installation in DocumentationWorker."""

import sqlite3
import tarfile
import types
import sys
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

# The worker uses wx.CallAfter only to dispatch callbacks. Keep these tests usable
# in headless test environments where wxPython is not installed.
try:
    import wx  # noqa: F401
except ImportError:
    wx_stub = types.ModuleType("wx")
    wx_stub.CallAfter = lambda callback, *args, **kwargs: callback(*args, **kwargs)
    sys.modules["wx"] = wx_stub

from core.documentation_manager import DocumentationFormatError, DocumentationRelease
import core.documentation_worker as documentation_worker_module
from core.documentation_worker import DocumentationWorker


@pytest.fixture(autouse=True)
def synchronous_wx_callafter(monkeypatch):
    """Run wx callbacks immediately so tests do not need a wx event loop."""
    monkeypatch.setattr(
        documentation_worker_module.wx,
        "CallAfter",
        lambda callback, *args, **kwargs: callback(*args, **kwargs),
    )


def create_valid_docset(path: Path):
    resources = path / "Contents" / "Resources"
    documents = resources / "Documents"
    documents.mkdir(parents=True, exist_ok=True)
    (path / "Contents" / "Info.plist").write_bytes(
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b"<!DOCTYPE plist PUBLIC '-//Apple//DTD PLIST 1.0//EN' "
        b"'http://www.apple.com/DTDs/PropertyList-1.0.dtd'>"
        b"<plist version='1.0'><dict><key>CFBundleIdentifier</key>"
        b"<string>openmp</string></dict></plist>"
    )
    (documents / "index.html").write_text("<html>home</html>", encoding="utf-8")
    database = sqlite3.connect(resources / "docSet.dsidx")
    try:
        database.execute(
            "CREATE TABLE searchIndex "
            "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)"
        )
        database.execute(
            "INSERT INTO searchIndex (name, type, path) VALUES (?, ?, ?)",
            ("OnPlayerConnect", "Callback", "callbacks.html"),
        )
        database.commit()
    finally:
        database.close()
    return path


def create_tar_gz(archive_path: Path, source: Path, *, arcname="openmp.docset"):
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(source, arcname=arcname)
    return archive_path


class FakeManager:
    def __init__(self, root: Path):
        self.documentation_dir = root
        self.docset_path = root / "openmp.docset"
        self.version_file = root / ".openmp-docset-version.json"

    @staticmethod
    def validate_docset(path):
        from core.documentation_manager import OpenMPDocumentationManager

        return OpenMPDocumentationManager.validate_docset(path)


def make_worker(tmp_path, *, mode="install", release=None, on_complete=None, on_progress=None):
    root = tmp_path / "documentation"
    root.mkdir(parents=True, exist_ok=True)
    manager = FakeManager(root)
    return DocumentationWorker(
        manager,
        mode,
        on_complete or Mock(),
        on_progress=on_progress,
        release=release,
    )


def test_worker_rejects_unknown_mode(tmp_path):
    worker = make_worker(tmp_path)
    with pytest.raises(ValueError, match="mode must be"):
        DocumentationWorker(worker.manager, "remove", Mock())


def test_install_worker_requires_release(tmp_path):
    worker = make_worker(tmp_path, mode="install")
    worker.run()

    worker.on_complete.assert_called_once()
    success, result, error = worker.on_complete.call_args.args
    assert success is False
    assert result is None
    assert isinstance(error, ValueError)


def test_check_worker_dispatches_release(tmp_path):
    worker = make_worker(tmp_path, mode="check")
    release = DocumentationRelease("1.0", "https://github.com/example/docset.tgz")
    worker.manager.fetch_latest_release = Mock(return_value=release)

    worker.run()

    worker.manager.fetch_latest_release.assert_called_once()
    worker.on_complete.assert_called_once_with(True, release, None)


def test_cancelled_worker_does_not_dispatch_completion(tmp_path):
    worker = make_worker(tmp_path, mode="check")
    worker.manager.fetch_latest_release = Mock(return_value=object())
    worker.cancel()

    worker.run()

    worker.on_complete.assert_not_called()


def test_progress_dispatch_reports_percentage_only_when_changed(tmp_path):
    callback = Mock()
    worker = make_worker(tmp_path, on_progress=callback)

    worker._dispatch_progress(10, 100)
    worker._dispatch_progress(19, 100)
    worker._dispatch_progress(19, 100)  # same percentage should be suppressed
    worker._dispatch_progress(20, 100)
    worker._dispatch_progress(1, 0)

    assert callback.call_args_list == [
        call(10, 100, 10),
        call(19, 100, 19),
        call(20, 100, 20),
        call(1, 0, None),
    ]


def test_safe_member_path_accepts_normal_relative_path(tmp_path):
    root = tmp_path / "extract"
    root.mkdir()

    target = DocumentationWorker._safe_member_path(root, "openmp.docset/Contents/Info.plist")

    assert target == root / "openmp.docset" / "Contents" / "Info.plist"


@pytest.mark.parametrize(
    "member_name",
    ["../outside.txt", "openmp.docset/../../outside.txt", "/absolute/file.txt", "..\\outside.txt"],
)
def test_safe_member_path_rejects_traversal_and_absolute_paths(tmp_path, member_name):
    root = tmp_path / "extract"
    root.mkdir()

    with pytest.raises(DocumentationFormatError, match="unsafe path"):
        DocumentationWorker._safe_member_path(root, member_name)


def test_extract_docset_extracts_valid_archive(tmp_path):
    source = create_valid_docset(tmp_path / "source" / "openmp.docset")
    archive_path = create_tar_gz(tmp_path / "docset.tgz", source)
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")

    extracted = worker._extract_docset(archive_path, extraction_root)

    assert extracted == extraction_root / "openmp.docset"
    assert (extracted / "Contents" / "Resources" / "Documents" / "index.html").is_file()


def test_extract_docset_finds_single_nested_docset(tmp_path):
    source = create_valid_docset(tmp_path / "source" / "release" / "openmp.docset")
    archive_path = create_tar_gz(
        tmp_path / "docset.tgz",
        source.parent,
        arcname="release",
    )
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")

    extracted = worker._extract_docset(archive_path, extraction_root)

    assert extracted.name == "openmp.docset"
    assert extracted.is_dir()


def test_extract_docset_rejects_unsafe_tar_member(tmp_path):
    archive_path = tmp_path / "unsafe.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        member = tarfile.TarInfo("../outside.txt")
        member.size = 4
        import io
        archive.addfile(member, io.BytesIO(b"evil"))
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")

    with pytest.raises(DocumentationFormatError, match="unsafe path"):
        worker._extract_docset(archive_path, extraction_root)

    assert not (tmp_path / "outside.txt").exists()


def test_extract_docset_rejects_symbolic_links(tmp_path):
    archive_path = tmp_path / "symlink.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        member = tarfile.TarInfo("openmp.docset/link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        archive.addfile(member)
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")

    with pytest.raises(DocumentationFormatError, match="unsupported file type"):
        worker._extract_docset(archive_path, extraction_root)


def test_extract_docset_enforces_unpacked_size_limit(tmp_path, monkeypatch):
    archive_path = tmp_path / "large.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        import io
        member = tarfile.TarInfo("openmp.docset/large.bin")
        member.size = 16
        archive.addfile(member, io.BytesIO(b"0123456789abcdef"))
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")
    monkeypatch.setattr("core.documentation_worker.MAX_UNPACKED_BYTES", 8)

    with pytest.raises(DocumentationFormatError, match="too large"):
        worker._extract_docset(archive_path, extraction_root)


def test_extract_docset_rejects_archive_without_docset_bundle(tmp_path):
    archive_path = tmp_path / "other.tgz"
    source = tmp_path / "source"
    source.mkdir()
    (source / "readme.txt").write_text("not a docset", encoding="utf-8")
    create_tar_gz(archive_path, source, arcname="release")
    extraction_root = tmp_path / "extract"
    extraction_root.mkdir()
    worker = make_worker(tmp_path / "worker")

    with pytest.raises(DocumentationFormatError, match="does not contain exactly one"):
        worker._extract_docset(archive_path, extraction_root)


def test_download_archive_writes_stream_and_reports_progress(tmp_path):
    worker = make_worker(tmp_path)
    callback = Mock()
    worker.on_progress = callback
    response = Mock()
    response.headers = {"Content-Length": "6"}
    response.iter_content.return_value = [b"abc", b"", b"def"]
    release = DocumentationRelease("1.0", "https://github.com/example/docset.tgz", 6)
    destination = tmp_path / "download.tgz"

    with patch("core.documentation_worker.requests.get", return_value=response) as get:
        worker._download_archive(release, destination)

    assert destination.read_bytes() == b"abcdef"
    assert callback.call_args_list == [
        call(3, 6, 50),
        call(6, 6, 100),
    ]
    response.close.assert_called_once()
    get.assert_called_once()


def test_download_archive_rejects_empty_response(tmp_path):
    worker = make_worker(tmp_path)
    response = Mock()
    response.headers = {}
    response.iter_content.return_value = [b"", b""]

    with patch("core.documentation_worker.requests.get", return_value=response):
        with pytest.raises(RuntimeError, match="empty file"):
            worker._download_archive(
                DocumentationRelease("1.0", "https://github.com/example/docset.tgz"),
                tmp_path / "empty.tgz",
            )


def test_download_archive_rejects_incomplete_response(tmp_path):
    worker = make_worker(tmp_path)
    response = Mock()
    response.headers = {"Content-Length": "10"}
    response.iter_content.return_value = [b"short"]

    with patch("core.documentation_worker.requests.get", return_value=response):
        with pytest.raises(RuntimeError, match="Incomplete documentation download"):
            worker._download_archive(
                DocumentationRelease("1.0", "https://github.com/example/docset.tgz"),
                tmp_path / "partial.tgz",
            )


def test_replace_installation_replaces_docset_and_commits_version(tmp_path):
    worker = make_worker(tmp_path)
    manager = worker.manager
    create_valid_docset(manager.docset_path)
    (manager.docset_path / "old.txt").write_text("old", encoding="utf-8")
    candidate = create_valid_docset(tmp_path / "candidate" / "openmp.docset")
    (candidate / "new.txt").write_text("new", encoding="utf-8")

    worker._replace_installation(candidate, "2026.11.10")

    assert manager.validate_docset(manager.docset_path)
    assert (manager.docset_path / "new.txt").is_file()
    assert not (manager.docset_path / "old.txt").exists()
    assert not (manager.documentation_dir / ".openmp.docset.previous").exists()
    assert json_read(manager.version_file) == {"version": "2026.11.10"}


def json_read(path):
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def test_replace_installation_rolls_back_when_candidate_is_invalid(tmp_path):
    worker = make_worker(tmp_path)
    manager = worker.manager
    create_valid_docset(manager.docset_path)
    (manager.docset_path / "old.txt").write_text("old", encoding="utf-8")
    manager.version_file.write_text('{"version": "1.0"}', encoding="utf-8")
    candidate = tmp_path / "candidate" / "openmp.docset"
    (candidate / "Contents" / "Resources" / "Documents").mkdir(parents=True)
    (candidate / "Contents" / "Resources" / "Documents" / "index.html").write_text(
        "not complete", encoding="utf-8"
    )

    with pytest.raises(RuntimeError, match="failed validation"):
        worker._replace_installation(candidate, "2.0")

    assert manager.validate_docset(manager.docset_path)
    assert (manager.docset_path / "old.txt").read_text(encoding="utf-8") == "old"
    assert json_read(manager.version_file) == {"version": "1.0"}
    assert not (manager.documentation_dir / ".openmp.docset.previous").exists()
    assert not (manager.documentation_dir / ".openmp-version.new").exists()


def test_download_and_install_removes_staging_directory(tmp_path, monkeypatch):
    worker = make_worker(
        tmp_path,
        release=DocumentationRelease("3.0", "https://github.com/example/docset.tgz"),
    )
    source = create_valid_docset(tmp_path / "source" / "openmp.docset")
    archive_bytes_path = create_tar_gz(tmp_path / "source.tgz", source)
    archive_bytes = archive_bytes_path.read_bytes()

    def fake_download(_release, destination):
        destination.write_bytes(archive_bytes)

    monkeypatch.setattr(worker, "_download_archive", fake_download)

    result = worker._download_and_install(worker.release)

    assert result == worker.manager.docset_path
    assert worker.manager.validate_docset(result)
    assert not list(worker.manager.documentation_dir.glob(".openmp-docset-install-*"))
