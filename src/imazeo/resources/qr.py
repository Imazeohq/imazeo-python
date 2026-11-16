"""QR code generation resource."""

from __future__ import annotations

from collections.abc import Callable

from imazeo.resources.project import processing_headers
from imazeo._http import HttpTransport
from imazeo.types import BinaryResult, QrGenerateInput
from imazeo.version import LIGHT_TIMEOUT_MS


class QrResource:
    def __init__(
        self,
        http: HttpTransport,
        project_id: Callable[[], str],
    ) -> None:
        self._http = http
        self._project_id = project_id

    def generate(self, input: QrGenerateInput, *, idempotency_key: str | None = None, quote_id: str | None = None) -> BinaryResult:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "tools", "qr")
        return self._http.request_binary(
            "POST",
            url,
            body=input,
            headers={"Content-Type": "application/json", "Accept": "*/*", **processing_headers(idempotency_key, quote_id)},
            timeout_ms=LIGHT_TIMEOUT_MS,
        )
