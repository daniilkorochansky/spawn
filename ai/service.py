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

"""Application-level AI service, independent of wxPython and WebView."""
from __future__ import annotations
from typing import Any
from .lm_studio import LMStudioClient, AIClientError
from .context import AIContext

class AIService:
    def __init__(self, settings: dict[str, Any] | None = None):
        self.update_settings(settings or {})

    def update_settings(self, settings: dict[str, Any]) -> None:
        self.settings = dict(settings)
        self.client = LMStudioClient(
            self.settings.get("base_url", "http://localhost:1234/v1"),
            self.settings.get("api_key", ""),
            timeout=float(self.settings.get("timeout", 90) or 90),
        )

    def list_models(self) -> list[dict[str, Any]]:
        return self.client.list_models()

    def test_connection(self) -> list[dict[str, Any]]:
        return self.list_models()

    def chat(self, messages: list[dict[str, str]], model: str | None = None,
             context: AIContext | None = None, **kwargs) -> str:
        # Context is deliberately not sent until project-context UI is implemented.
        selected_model = model or self.settings.get("model", "")
        return self.client.chat(messages, selected_model, **kwargs)
