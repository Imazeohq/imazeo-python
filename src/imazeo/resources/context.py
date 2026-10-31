"""API key context resource."""

from __future__ import annotations

from imazeo._http import HttpTransport
from imazeo.types import ApiKeyContext
from imazeo.version import LIGHT_TIMEOUT_MS


class ContextResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

    def get(self) -> ApiKeyContext:
        url = self._http.path("api-key", "context")
        res = self._http.request_json("GET", url, timeout_ms=LIGHT_TIMEOUT_MS)
        return res.data  # type: ignore[no-any-return]
