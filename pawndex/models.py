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


from dataclasses import dataclass, field


@dataclass(slots=True)
class Package:

    id: str
    name: str

    user: str
    repo: str

    description: str = ""

    type: str = ""

    stars: int = 0
    forks: int = 0

    latest_tag: str = ""

    labels: list[str] = field(
        default_factory=list
    )

    tags: list[str] = field(
        default_factory=list
    )

    topics: list[str] = field(
        default_factory=list
    )

    total_downloads: int = 0

    official: bool = False

    @classmethod
    def from_json(cls,data: dict):
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),

            user=data.get("user", ""),
            repo=data.get("repo", ""),

            description=data.get(
                "description",
                "",
            ),

            type=data.get(
                "type",
                "",
            ),

            stars=data.get(
                "stars",
                0,
            ),

            forks=data.get(
                "forks",
                0,
            ),

            latest_tag=data.get(
                "latestTag",
                "",
            ),

            labels=data.get(
                "labels",
                [],
            ),

            tags=data.get(
                "tags",
                [],
            ),

            topics=data.get(
                "topics",
                [],
            ),

            total_downloads=data.get(
                "totalDownloads",
                0,
            ),

            official=data.get(
                "official",
                False,
            ),
        )
