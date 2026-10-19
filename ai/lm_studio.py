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

"""OpenAI-compatible HTTP client for LM Studio's local server."""
from __future__ import annotations
from typing import Any
from urllib.parse import urlsplit
import json
import requests

class AIClientError(RuntimeError):
    """Safe, user-presentable provider/network error."""

class AIRequestCancelled(AIClientError):
    """Raised when the user stops generation."""

class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1",
                 api_key: str = "", timeout: float = 60.0):
        self.base_url = self._normalize_base_url(base_url)
        self.api_key = (api_key or "").strip()
        self.timeout = max(1.0, float(timeout))
        self._active_response = None

    @staticmethod
    def _normalize_base_url(value: str) -> str:
        value = (value or "http://localhost:1234/v1").strip().rstrip("/")
        parsed = urlsplit(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise AIClientError("Invalid server URL. Enter an HTTP(S) URL, e.g. http://localhost:1234/v1.")
        if parsed.username or parsed.password:
            raise AIClientError("Do not put credentials in the URL. Use the API Key setting.")
        if value.endswith("/v1/v1"):
            value = value[:-3]
        elif not parsed.path.rstrip("/").endswith("/v1"):
            value += "/v1"
        return value

    def cancel_current_request(self) -> None:
        """Close the active streaming response to interrupt generation."""
        response = self._active_response
        if response is not None:
            try:
                response.close()
            except Exception:
                pass

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    def _error_detail(response) -> str:
        try:
            payload = response.json()
            err = payload.get("error", {}) if isinstance(payload, dict) else {}
            detail = err.get("message", "") if isinstance(err, dict) else str(err)
            return str(detail)[:500]
        except (ValueError, AttributeError):
            return ""

    def list_models(self) -> list[dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/models", headers=self._headers(), timeout=min(self.timeout, 10.0))
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise AIClientError("LM Studio timed out while listing models. Check that its local server is running.") from exc
        except requests.ConnectionError as exc:
            raise AIClientError("Cannot connect to LM Studio. Start the local server and verify the Server URL.") from exc
        except requests.HTTPError as exc:
            response = exc.response
            code = response.status_code if response is not None else "unknown"
            detail = self._error_detail(response) if response is not None else ""
            raise AIClientError(f"LM Studio returned HTTP {code}" + (f": {detail}" if detail else ".")) from exc
        except (requests.RequestException, ValueError) as exc:
            raise AIClientError(f"Could not read the model list from LM Studio: {exc}") from exc
        models = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(models, list):
            raise AIClientError("LM Studio returned an unexpected response for /models.")
        return [item for item in models if isinstance(item, dict) and item.get("id")]

    def chat(self, messages: list[dict[str, str]], model: str,
             temperature: float = 0.7, max_tokens: int | None = None,
             stream: bool = False, on_token=None, cancel_event=None) -> str:
        if not model:
            raise AIClientError("No model selected. Open Spawn Settings → AI and choose a model.")
        body: dict[str, Any] = {
            "model": model, "messages": messages,
            "temperature": temperature, "stream": bool(stream),
        }
        if max_tokens is not None and max_tokens > 0:
            body["max_tokens"] = int(max_tokens)

        try:
            # No read timeout for generation: small local models can take a long time.
            # A connect timeout still protects against an unreachable endpoint.
            timeout = (10.0, None) if stream else (10.0, None)
            with requests.post(
                f"{self.base_url}/chat/completions",
                headers={**self._headers(), "Accept": "text/event-stream" if stream else "application/json"},
                json=body, timeout=timeout, stream=stream
            ) as response:
                self._active_response = response
                response.raise_for_status()
                if stream:
                    # SSE payloads are UTF-8. requests may otherwise infer a
                    # legacy encoding from headers, corrupting apostrophes/emoji.
                    response.encoding = "utf-8"
                    chunks = []
                    for line in response.iter_lines(decode_unicode=False):
                        if cancel_event is not None and cancel_event.is_set():
                            response.close()
                            raise AIRequestCancelled("Generation stopped.")
                        if not line:
                            continue
                        if isinstance(line, bytes):
                            line = line.decode("utf-8", errors="replace")
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            payload = json.loads(data)
                        except ValueError:
                            continue
                        choices = payload.get("choices", [])
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        token = delta.get("content", "")
                        if isinstance(token, list):
                            token = "".join(
                                str(item.get("text", "")) for item in token if isinstance(item, dict)
                            )
                        if token:
                            chunks.append(str(token))
                            if callable(on_token):
                                on_token(str(token))
                    if cancel_event is not None and cancel_event.is_set():
                        raise AIRequestCancelled("Generation stopped.")
                    content = "".join(chunks)
                else:
                    payload = response.json()
                    content = payload["choices"][0]["message"]["content"]
        except AIRequestCancelled:
            raise
        except requests.Timeout as exc:
            raise AIClientError("Could not connect to LM Studio. The connection timed out before generation began.") from exc
        except requests.ConnectionError as exc:
            raise AIClientError("Connection to LM Studio was lost. Check that its local server is running.") from exc
        except requests.HTTPError as exc:
            response = exc.response
            code = response.status_code if response is not None else "unknown"
            detail = self._error_detail(response) if response is not None else ""
            raise AIClientError(f"LM Studio returned HTTP {code}" + (f": {detail}" if detail else ".")) from exc
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIClientError(f"Could not process the response from LM Studio: {exc}") from exc
        finally:
            self._active_response = None

        if isinstance(content, list):
            content = "\\n".join(str(x.get("text", "")) for x in content if isinstance(x, dict))
        if not isinstance(content, str) or not content.strip():
            if cancel_event is not None and cancel_event.is_set():
                raise AIRequestCancelled("Generation stopped.")
            raise AIClientError("The model returned an empty response.")
        return content
