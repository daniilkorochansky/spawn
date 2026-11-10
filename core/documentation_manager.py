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

"""Installation and release metadata management for the open.mp docset."""

from __future__ import annotations

import json
import os
import shutil
from contextlib import closing
import plistlib
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

from core.platform_utils import PlatformUtils
from core.logger import SpawnLogger


DEFAULT_FEED_URL = (
    "https://github.com/daniilkorochansky/openmp-docset/"
    "releases/download/latest/open.mp.xml"
)
DOCSET_DIRECTORY_NAME = "openmp.docset"
VERSION_FILE_NAME = ".openmp-docset-version.json"


class DocumentationError(RuntimeError):
    """Base exception for documentation-related errors."""


class DocumentationNetworkError(DocumentationError):
    """Raised when the feed or documentation archive cannot be reached."""


class DocumentationFormatError(DocumentationError):
    """Raised when the feed or downloaded docset has an invalid format."""


@dataclass(frozen=True)
class DocumentationRelease:
    version: str
    download_url: str
    size_bytes: int = 0

    @property
    def size_text(self) -> str:
        if self.size_bytes <= 0:
            return "Unknown"
        value = float(self.size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if value < 1024 or unit == "GB":
                return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
            value /= 1024
        return f"{value:.1f} GB"


class OpenMPDocumentationManager:
    """Owns the installed open.mp docset and its update metadata."""

    def __init__(self, feed_url: str = DEFAULT_FEED_URL, config_dir: str | None = None):
        self.feed_url = feed_url
        base_dir = Path(config_dir or PlatformUtils.get_config_dir())
        self.documentation_dir = base_dir / "documentation"
        self.docset_path = self.documentation_dir / DOCSET_DIRECTORY_NAME
        self.version_file = self.documentation_dir / VERSION_FILE_NAME
        self.documentation_dir.mkdir(parents=True, exist_ok=True)

        self.recover_installation()
        self.cleanup_temp_directories()

    @staticmethod
    def _version_key(version: str) -> tuple:
        """Compare dotted numeric versions, including timestamp-style versions."""
        parts = []
        for part in str(version).strip().split("."):
            digits = "".join(char for char in part if char.isdigit())
            parts.append(int(digits) if digits else 0)
        return tuple(parts)

    @staticmethod
    def validate_docset(docset_path: str | Path) -> bool:
        """Check the Dash/Zeal bundle, plist and required SQLite table."""
        path = Path(docset_path)
        info_path = path / "Contents" / "Info.plist"
        index_path = path / "Contents" / "Resources" / "docSet.dsidx"
        documents_path = path / "Contents" / "Resources" / "Documents"
        home_page = documents_path / "index.html"

        if (
            not path.is_dir()
            or not info_path.is_file()
            or not index_path.is_file()
            or not documents_path.is_dir()
            or not home_page.is_file()
        ):
            return False

        try:
            with info_path.open("rb") as stream:
                info = plistlib.load(stream)
            if not isinstance(info, dict) or info.get("CFBundleIdentifier") != "openmp":
                return False

            with closing(sqlite3.connect(index_path.as_uri() + "?mode=ro", uri=True)) as connection:
                row = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='searchIndex'"
                ).fetchone()
                if not row:
                    return False
                columns = {
                    item[1] for item in connection.execute("PRAGMA table_info(searchIndex)")
                }
                if not {"name", "type", "path"}.issubset(columns):
                    return False
                return connection.execute("SELECT COUNT(*) FROM searchIndex").fetchone()[0] > 0
        except (OSError, ValueError, ET.ParseError, sqlite3.Error, plistlib.InvalidFileException):
            return False

    def recover_installation(self):
        """Recover or clean up a previous interrupted docset replacement."""
        backup = self.documentation_dir / ".openmp.docset.previous"

        if not backup.exists():
            return

        if self.validate_docset(self.docset_path):
            # The new installation is valid. The backup is no longer needed.
            shutil.rmtree(backup)
            SpawnLogger.info("Removed obsolete documentation backup.")
            return

        if self.validate_docset(backup):
            # The previous installation is valid; restore it.
            if self.docset_path.exists() or self.docset_path.is_symlink():
                if self.docset_path.is_dir() and not self.docset_path.is_symlink():
                    shutil.rmtree(self.docset_path)
                else:
                    self.docset_path.unlink()

            backup.replace(self.docset_path)
            SpawnLogger.info("Restored previous documentation installation.")

    def cleanup_temp_directories(self):
        """Remove abandoned documentation installation directories."""
        if not self.documentation_dir.exists():
            return

        for path in self.documentation_dir.glob(".openmp-docset-install-*"):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    SpawnLogger.info(f"Removed abandoned documentation directory: {path}")
            except OSError as exc:
                SpawnLogger.warning(f"Unable to remove temporary documentation directory {path}: {exc}")

    def is_installed(self) -> bool:
        return self.validate_docset(self.docset_path)

    def get_installed_version(self) -> str | None:
        try:
            data = json.loads(self.version_file.read_text(encoding="utf-8"))

            if not isinstance(data, dict):
                return None

            version = data.get("version")
            return str(version) if version else None

        except (OSError, ValueError, TypeError):
            return None

    def fetch_latest_release(self, timeout: tuple[float, float] = (8.0, 25.0)) -> DocumentationRelease:
        """Read the Zeal XML feed and determine the archive size when possible."""
        session = requests.Session()
        headers = {"User-Agent": "Spawn-IDE-openmp-documentation"}

        try:
            response = session.get(self.feed_url, timeout=timeout, headers=headers)
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise DocumentationFormatError(
                f"The documentation feed returned HTTP {exc.response.status_code}."
            ) from exc
        except requests.RequestException as exc:
            raise DocumentationNetworkError(str(exc)) from exc

        try:
            root = ET.fromstring(response.content)
            version = (root.findtext("version") or "").strip()
            download_url = (root.findtext("url") or "").strip()
        except ET.ParseError as exc:
            raise DocumentationFormatError("The documentation feed is not valid XML.") from exc

        if not version or not download_url:
            raise DocumentationFormatError("The documentation feed is missing version or URL.")

        parsed_url = urlparse(download_url)
        if parsed_url.scheme != "https" or parsed_url.hostname not in {"github.com", "objects.githubusercontent.com"}:
            raise DocumentationFormatError("The documentation feed contains an unexpected download URL.")

        size_bytes = 0
        try:
            head = session.head(
                download_url,
                allow_redirects=True,
                timeout=timeout,
                headers=headers,
            )
            if head.ok:
                size_bytes = int(head.headers.get("Content-Length") or 0)
        except (requests.RequestException, ValueError):
            size_bytes = 0

        # GitHub and some release proxies may omit Content-Length on HEAD.
        if size_bytes <= 0:
            try:
                probe = session.get(
                    download_url,
                    headers={**headers, "Range": "bytes=0-0"},
                    stream=True,
                    allow_redirects=True,
                    timeout=timeout,
                )
                if probe.ok or probe.status_code == 206:
                    content_range = probe.headers.get("Content-Range", "")
                    if "/" in content_range:
                        size_bytes = int(content_range.rsplit("/", 1)[1])
                    else:
                        size_bytes = int(probe.headers.get("Content-Length") or 0)
                probe.close()
            except (requests.RequestException, ValueError):
                size_bytes = 0

        return DocumentationRelease(version, download_url, max(0, size_bytes))

    def is_update_available(self, release: DocumentationRelease) -> bool:
        installed_version = self.get_installed_version()
        if not installed_version:
            # A valid manually installed docset without Spawn's manifest is treated as old.
            return True
        return self._version_key(release.version) > self._version_key(installed_version)

    def write_installed_version(self, version: str) -> None:
        self.documentation_dir.mkdir(parents=True, exist_ok=True)
        payload = {"version": str(version)}
        fd, temporary_name = tempfile.mkstemp(
            prefix=".openmp-version-",
            suffix=".tmp",
            dir=str(self.documentation_dir),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
                stream.write("\n")
            Path(temporary_name).replace(self.version_file)
        except Exception:
            Path(temporary_name).unlink(missing_ok=True)
            raise

    def get_home_page(self) -> Path:
        return self.docset_path / "Contents" / "Resources" / "Documents" / "index.html"
