"""Official Imazeo server-side Python client."""

from __future__ import annotations

from imazeo._http import HttpTransport, create_transport_config
from imazeo.resources.barcodes import BarcodesResource
from imazeo.resources.context import ContextResource
from imazeo.resources.images import ImagesResource
from imazeo.resources.pdf import PdfResource
from imazeo.resources.qr import QrResource
from imazeo.resources.transforms import TransformsResource
from imazeo.version import (
    DEFAULT_API_VERSION,
    SDK_VERSION,
    SUPPORTED_API_VERSIONS,
    ApiVersion,
)

import httpx


class Imazeo:
    """Official Imazeo server-side client.

    Uses secret ``X-API-Key`` authentication. Do not embed API keys in browsers.
    """

    version = SDK_VERSION

    def __init__(
        self,
        *,
        api_key: str,
        project_id: str | None = None,
        base_url: str | None = None,
        api_version: ApiVersion | None = None,
        timeout_ms: int | None = None,
        app_name: str | None = None,
        transport: httpx.BaseTransport | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._http = HttpTransport(
            create_transport_config(
                api_key=api_key,
                base_url=base_url,
                api_version=api_version,
                timeout_ms=timeout_ms,
                app_name=app_name,
            ),
            transport=transport,
            client=http_client,
        )
        configured = (project_id or "").strip() or None
        self._configured_project_id = configured
        self._resolved_project_id: str | None = None

        self.context = ContextResource(self._http)
        self.images = ImagesResource(self._http, self.resolve_project_id)
        self.transforms = TransformsResource(self._http, self.resolve_project_id)
        self.qr = QrResource(self._http, self.resolve_project_id)
        self.barcodes = BarcodesResource(self._http, self.resolve_project_id)
        self.pdf = PdfResource(self._http, self.resolve_project_id)

    @classmethod
    def api_compatibility(cls) -> dict[str, object]:
        """Default and supported API versions."""
        return {
            "default_api": DEFAULT_API_VERSION,
            "supported": list(SUPPORTED_API_VERSIONS),
        }

    def resolve_project_id(self) -> str:
        if self._configured_project_id:
            return self._configured_project_id
        if self._resolved_project_id is None:
            self._resolved_project_id = self.context.get()["projectId"]
        return self._resolved_project_id

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Imazeo:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
