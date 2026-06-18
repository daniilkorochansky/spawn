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
from unittest.mock import Mock
from unittest.mock import patch

from pawndex.client import PawndexClient
from pawndex.index import PackageIndex
from pawndex.models import Package


def test_package_from_json():
    data = {
        "id": "Y-Less/sscanf",
        "name": "sscanf",
        "user": "Y-Less",
        "repo": "sscanf",
        "description": "SA:MP sscanf plugin",
        "stars": 100,
        "forks": 20,
        "latestTag": "v2.13.8",
    }

    package = Package.from_json(data)

    assert package.id == "Y-Less/sscanf"
    assert package.name == "sscanf"
    assert package.user == "Y-Less"
    assert package.latest_tag == "v2.13.8"

def test_load_index(tmp_path):
    file = tmp_path / "packages.json"

    file.write_text(
        json.dumps(
            {
                "packages": {
                    "Y-Less/sscanf": {
                        "id": "Y-Less/sscanf",
                        "name": "sscanf",
                        "user": "Y-Less",
                        "repo": "sscanf",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    index = PackageIndex()

    index.load(file)

    assert index.count() == 1

def test_get_package(tmp_path):
    file = tmp_path / "packages.json"

    file.write_text(
        json.dumps(
            {
                "packages": {
                    "Y-Less/sscanf": {
                        "id": "Y-Less/sscanf",
                        "name": "sscanf",
                        "user": "Y-Less",
                        "repo": "sscanf",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    index = PackageIndex()

    index.load(file)

    package = index.get(
        "Y-Less/sscanf"
    )

    assert package is not None
    assert package.name == "sscanf"

def test_search_by_name(tmp_path):
    file = tmp_path / "packages.json"

    file.write_text(
        json.dumps(
            {
                "packages": {
                    "streamer": {
                        "id": "streamer",
                        "name": "streamer",
                        "user": "Incognito",
                        "repo": "streamer",
                    },
                    "mysql": {
                        "id": "mysql",
                        "name": "mysql",
                        "user": "pBlueG",
                        "repo": "mysql",
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    index = PackageIndex()

    index.load(file)

    results = index.search(
        "stream"
    )

    assert len(results) == 1
    assert results[0].name == "streamer"

@patch("pawndex.client.requests.get")
def test_get_page(mock_get):

    response = Mock()

    response.json.return_value = {
        "items": [],
        "pageCount": 1,
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = PawndexClient()

    page = client.get_page(1)

    assert page["pageCount"] == 1

@patch.object(PawndexClient,"get_page")
def test_build_index(mock_get_page):
    mock_get_page.return_value = {
        "items": [
            {
                "id": "test/package",
                "name": "package",
            }
        ],
        "pageCount": 1,
    }

    client = PawndexClient()

    index = client.build_index()

    assert (index["package_count"] == 1)

    assert ("test/package" in index["packages"])
