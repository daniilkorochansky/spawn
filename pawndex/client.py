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

import json

from datetime import datetime, UTC
from pathlib import Path

import requests


class PawndexClient:
    BASE_URL = "https://packages.open.mp/api/v1/packages"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get_page(
        self,
        page: int,
        limit: int = 1000,
    ) -> dict:

        response = requests.get(
            self.BASE_URL,
            params={
                "type": "all",
                "limit": limit,
                "page": page,
            },
            headers={
                "Accept": "application/json",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def build_index(
        self,
        limit: int = 1000,
        progress_callback=None,
    ) -> dict:

        try:
            first_page = self.get_page(
                page=1,
                limit=limit,
            )
        except requests.RequestException as error:
            raise RuntimeError(
                "Failed to download first page."
            ) from error

        page_count = first_page["pageCount"]

        packages = {}

        for item in first_page["items"]:
            packages[item["id"]] = item

        if progress_callback:
            progress_callback(
                1,
                page_count,
            )

        for page in range(2, page_count + 1):

            try:
                data = self.get_page(
                    page=page,
                    limit=limit,
                )
            except requests.RequestException as error:
                raise RuntimeError(
                    f"Failed to download page {page}."
                ) from error

            for item in data["items"]:
                packages[item["id"]] = item

            if progress_callback:
                progress_callback(
                    page,
                    page_count,
                )

        return {
            "updated_at": datetime.now(
                UTC
            ).isoformat(),
            "package_count": len(packages),
            "packages": packages,
        }

    def save_index(
        self,
        path: str | Path,
        limit: int = 1000,
        progress_callback=None,
    ) -> Path:

        index = self.build_index(
            limit=limit,
            progress_callback=progress_callback,
        )

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                index,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return path
