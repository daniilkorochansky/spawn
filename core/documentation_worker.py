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

"""Background feed check and safe open.mp docset download/installation."""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
import threading
import time
from pathlib import Path, PurePosixPath

import requests
import wx

from core.logger import SpawnLogger
from core.documentation_manager import (
    DocumentationFormatError,
    DocumentationRelease,
    OpenMPDocumentationManager,
)


MAX_UNPACKED_BYTES = 2 * 1024 * 1024 * 1024


class DocumentationWorker(threading.Thread):
    """Run either a feed check or a docset installation without blocking wx."""

    def __init__(
        self,
        manager: OpenMPDocumentationManager,
        mode: str,
        on_complete,
        on_progress=None,
        release: DocumentationRelease | None = None,
    ):
        super().__init__(name="OpenMPDocumentationWorker", daemon=True)
        if mode not in {"check", "install"}:
            raise ValueError("mode must be 'check' or 'install'")
        self.manager = manager
        self.mode = mode
        self.release = release
        self.on_complete = on_complete
        self.on_progress = on_progress
        self._cancel_event = threading.Event()
        self._last_reported_percent = None

    def cancel(self):
        self._cancel_event.set()

    def _dispatch_progress(self, downloaded: int, total: int):
        if self.on_progress:
            percent = int(downloaded * 100 / total) if total > 0 else None
            if percent is None or percent != self._last_reported_percent:
                self._last_reported_percent = percent
                wx.CallAfter(self.on_progress, downloaded, total, percent)

    def _dispatch_complete(self, success: bool, result=None, error: Exception | None = None):
        if self.on_complete:
            wx.CallAfter(self.on_complete, success, result, error)

    def run(self):
        try:
            if self.mode == "check":
                result = self.manager.fetch_latest_release()
            else:
                if self.release is None:
                    raise ValueError("A release is required for installation.")
                result = self._download_and_install(self.release)
            if not self._cancel_event.is_set():
                self._dispatch_complete(True, result, None)
        except Exception as exc:
            if not self._cancel_event.is_set():
                self._dispatch_complete(False, None, exc)

    def _download_and_install(self, release: DocumentationRelease) -> Path:
        root = self.manager.documentation_dir
        root.mkdir(parents=True, exist_ok=True)
        staging_root = Path(tempfile.mkdtemp(prefix=".openmp-docset-install-", dir=str(root)))
        archive_path = staging_root / "openmp.docset.tgz"
        extraction_root = staging_root / "extracted"
        extraction_root.mkdir()

        try:
            self._download_archive(release, archive_path)
            if self._cancel_event.is_set():
                raise InterruptedError("Documentation download was cancelled.")

            candidate = self._extract_docset(archive_path, extraction_root)
            if not self.manager.validate_docset(candidate):
                raise DocumentationFormatError(
                    "The downloaded archive does not contain a valid open.mp docset."
                )

            if self._cancel_event.is_set():
                raise InterruptedError("Documentation installation was cancelled.")

            self._replace_installation(candidate, release.version)
            return self.manager.docset_path
        finally:
            try:
                if staging_root.exists():
                    shutil.rmtree(staging_root)
                    SpawnLogger.info(
                        f"Removed temporary documentation directory: {staging_root}"
                    )
            except OSError as exc:
                SpawnLogger.warning(
                    f"Unable to remove temporary documentation directory "
                    f"{staging_root}: {exc}"
                )

    def _download_archive(self, release: DocumentationRelease, destination: Path):
        headers = {"User-Agent": "Spawn-IDE-openmp-documentation"}
        downloaded = 0
        total = max(0, int(release.size_bytes or 0))

        try:
            response = requests.get(
                release.download_url,
                stream=True,
                allow_redirects=True,
                timeout=(10.0, 45.0),
                headers=headers,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Unable to download documentation: {exc}") from exc

        header_length = response.headers.get("Content-Length")
        if header_length:
            try:
                total = int(header_length)
            except ValueError:
                pass

        try:
            with destination.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if self._cancel_event.is_set():
                        raise InterruptedError("Documentation download was cancelled.")
                    if not chunk:
                        continue
                    output.write(chunk)
                    downloaded += len(chunk)
                    self._dispatch_progress(downloaded, total)
        finally:
            response.close()

        if downloaded <= 0:
            raise RuntimeError("The documentation archive downloaded as an empty file.")
        if total > 0 and downloaded != total:
            raise RuntimeError(
                f"Incomplete documentation download ({downloaded} of {total} bytes)."
            )

    @staticmethod
    def _safe_member_path(extraction_root: Path, member_name: str) -> Path:
        normalized_name = member_name.replace("\\", "/")
        pure_path = PurePosixPath(normalized_name)
        if pure_path.is_absolute() or any(part in {"..", ""} for part in pure_path.parts):
            raise DocumentationFormatError("The documentation archive contains an unsafe path.")
        target = (extraction_root / Path(*pure_path.parts)).resolve()
        try:
            target.relative_to(extraction_root.resolve())
        except ValueError as exc:
            raise DocumentationFormatError("The archive attempts to write outside its staging directory.") from exc
        return target

    def _extract_docset(self, archive_path: Path, extraction_root: Path) -> Path:
        unpacked_bytes = 0
        try:
            with tarfile.open(archive_path, mode="r:gz") as archive:
                for member in archive.getmembers():
                    if self._cancel_event.is_set():
                        raise InterruptedError("Documentation installation was cancelled.")
                    target = self._safe_member_path(extraction_root, member.name)

                    # Do not extract symbolic links, hard links, devices or other special entries.
                    if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
                        raise DocumentationFormatError(
                            "The documentation archive contains an unsupported file type."
                        )

                    if member.isfile():
                        unpacked_bytes += int(member.size)
                        if unpacked_bytes > MAX_UNPACKED_BYTES:
                            raise DocumentationFormatError("The expanded documentation archive is too large.")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        source = archive.extractfile(member)
                        if source is None:
                            raise DocumentationFormatError("A file in the documentation archive could not be read.")
                        with source, target.open("wb") as output:
                            shutil.copyfileobj(source, output)
                    else:
                        target.mkdir(parents=True, exist_ok=True)
        except (tarfile.TarError, OSError) as exc:
            raise DocumentationFormatError(f"Unable to unpack documentation archive: {exc}") from exc

        preferred = extraction_root / "openmp.docset"
        if (preferred / "Contents" / "Info.plist").is_file():
            return preferred

        candidates = [
            path.parent.parent
            for path in extraction_root.rglob("Info.plist")
            if path.parent.name == "Contents" and path.parent.parent.name.endswith(".docset")
        ]
        if len(candidates) == 1:
            return candidates[0]
        raise DocumentationFormatError("The archive does not contain exactly one openmp.docset bundle.")

    def _replace_installation(self, candidate: Path, version: str):
        target = self.manager.docset_path
        backup = self.manager.documentation_dir / ".openmp.docset.previous"
        manifest = self.manager.version_file
        temporary_manifest = self.manager.documentation_dir / ".openmp-version.new"

        temporary_manifest.write_text(
            json.dumps({"version": str(version)}, indent=2) + "\n",
            encoding="utf-8",
        )

        moved_old = False

        try:
            # Remove an obsolete backup.
            if backup.exists():
                if self.manager.validate_docset(target):
                    shutil.rmtree(backup)
                else:
                    raise RuntimeError("An existing documentation backup cannot be safely removed.")

            # Move the currently installed documentation to backup.
            if target.exists():
                target.replace(backup)
                moved_old = True

            # Windows may temporarily lock extracted files.
            # Retry directory replacement before using copy fallback.
            installed = False
            last_error = None

            for attempt in range(4):
                try:
                    candidate.replace(target)
                    installed = True
                    break
                except PermissionError as exc:
                    last_error = exc
                    time.sleep(0.5)

            # Fallback: copy the directory instead of renaming it.
            if not installed:
                if target.exists():
                    raise last_error

                shutil.copytree(candidate, target)

            # Validate the final installation.
            if not self.manager.validate_docset(target):
                raise RuntimeError(
                    "The installed documentation failed validation."
                )

            # Commit the version manifest only after successful installation.
            temporary_manifest.replace(manifest)

        except Exception:
            # Remove incomplete installation.
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)

            # Restore previous documentation.
            if moved_old and backup.exists():
                backup.replace(target)

            temporary_manifest.unlink(missing_ok=True)
            raise

        else:
            # Remove previous version after successful installation.
            if backup.exists():
                shutil.rmtree(backup, ignore_errors=True)
