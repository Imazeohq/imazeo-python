"""Barcode generation resource."""

from __future__ import annotations

from collections.abc import Callable

from imazeo._http import HttpTransport
from imazeo.types import BarcodeGenerateInput, BinaryResult
from imazeo.version import LIGHT_TIMEOUT_MS


class BarcodesResource:
    def __init__(
        self,
        http: HttpTransport,
        project_id: Callable[[], str],
    ) -> None:
        self._http = http
        self._project_id = project_id

    def generate(self, input: BarcodeGenerateInput) -> BinaryResult:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "tools", "barcode")
        return self._http.request_binary(
            "POST",
            url,
            body=input,
            headers={"Content-Type": "application/json", "Accept": "*/*"},
            timeout_ms=LIGHT_TIMEOUT_MS,
        )
