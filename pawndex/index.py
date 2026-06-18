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


import json

from pathlib import Path

from .models import Package


class PackageIndex:

    def __init__(self):

        self.packages = {}

    def load(
        self,
        path: str | Path,
    ):

        path = Path(path)

        with path.open(
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        self.packages = {
            package_id: Package.from_json(
                package_data
            )
            for package_id, package_data
            in data["packages"].items()
        }

    def get(self,package_id: str):

        return self.packages.get(package_id)

    def search(self,query: str):
        query = query.lower()

        return [
            package
            for package
            in self.packages.values()
            if (
                query in package.name.lower()
                or query
                in package.description.lower()
            )
        ]

    def count(self):
        return len(self.packages)
