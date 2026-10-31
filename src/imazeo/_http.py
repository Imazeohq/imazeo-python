"""HTTP transport for the sync Imazeo client (httpx)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode, urlparse

import httpx

from imazeo.errors import NetworkError, map_http_error
from imazeo.types import BinaryResult, PreparedUpload, UploadFile, UploadSource
from imazeo.version import (
    DEFAULT_API_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT_MS,
    SDK_VERSION,
    SUPPORTED_API_VERSIONS,
    ApiVersion,
)


@dataclass(slots=True)
class JsonSuccess:
    data: Any
    meta: dict[str, Any]


@dataclass(slots=True)
class TransportConfig:
    api_key: str
    base_url: str
    api_version: ApiVersion
    timeout_ms: int
    user_agent: str


def assert_api_version(value: str) -> ApiVersion:
    if value not in SUPPORTED_API_VERSIONS:
        supported = ", ".join(SUPPORTED_API_VERSIONS)
        raise ValueError(f'Unsupported apiVersion "{value}". Supported: {supported}')
    return value  # type: ignore[return-value]


def normalize_base_url(raw: str) -> str:
    try:
        parsed = urlparse(raw)
    except Exception as exc:  # pragma: no cover - urlparse rarely raises
        raise ValueError(f"Invalid baseUrl: {raw}") from exc
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        if parsed.scheme not in ("http", "https"):
            raise ValueError("baseUrl must use http or https")
        raise ValueError(f"Invalid baseUrl: {raw}")
    if parsed.username or parsed.password:
        raise ValueError("baseUrl must not include credentials")
    path = parsed.path.rstrip("/")
    if path == "/v1":
        path = ""
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if path and path != "/":
        return f"{origin}{path}".rstrip("/")
    return origin


def create_transport_config(
    *,
    api_key: str,
    base_url: str | None = None,
    api_version: str | None = None,
    timeout_ms: int | None = None,
    app_name: str | None = None,
) -> TransportConfig:
    key = (api_key or "").strip()
    if not key:
        raise ValueError("apiKey is required")
    if len(key) > 128:
        raise ValueError("apiKey is too long")
    version = assert_api_version(api_version or DEFAULT_API_VERSION)
    origin = normalize_base_url(base_url or DEFAULT_BASE_URL)
    timeout = DEFAULT_TIMEOUT_MS if timeout_ms is None else timeout_ms
    if not isinstance(timeout, (int, float)) or timeout < 1:
        raise ValueError("timeoutMs must be a positive number")
    ua = (
        f"Imazeo-Python/{SDK_VERSION} {app_name}"
        if app_name
        else f"Imazeo-Python/{SDK_VERSION}"
    )
    return TransportConfig(
        api_key=key,
        base_url=origin,
        api_version=version,
        timeout_ms=int(timeout),
        user_agent=ua[:256],
    )


def prepare_upload(
    source: UploadSource,
    *,
    filename: str | None = None,
    content_type: str | None = None,
) -> PreparedUpload:
    if isinstance(source, UploadFile):
        data = bytes(source.data)
        return PreparedUpload(
            data=data,
            filename=source.filename or filename or "file.bin",
            content_type=source.content_type
            or content_type
            or "application/octet-stream",
        )
    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
        return PreparedUpload(
            data=data,
            filename=filename or "file.bin",
            content_type=content_type or "application/octet-stream",
        )
    raise TypeError("Unsupported upload source")


def _header_map(headers: httpx.Headers) -> dict[str, str]:
    return {k.lower(): v for k, v in headers.items()}


def _num_header(headers: httpx.Headers, name: str) -> int | None:
    raw = headers.get(name)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class HttpTransport:
    """Sync httpx transport with Imazeo envelope handling."""

    def __init__(
        self,
        config: TransportConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.config = config
        self._owns_client = client is None
        if client is not None:
            self._client = client
        else:
            self._client = httpx.Client(
                transport=transport,
                timeout=httpx.Timeout(config.timeout_ms / 1000.0),
                follow_redirects=False,
            )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HttpTransport:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def path(self, *segments: str) -> str:
        encoded = "/".join(_encode_segment(seg) for seg in segments)
        return f"{self.config.base_url}/{self.config.api_version}/{encoded}"

    def request_json(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
    ) -> JsonSuccess:
        import json

        req_headers = self._base_headers(accept="application/json", extra=headers)
        content: bytes | None = None
        if body is not None:
            req_headers["Content-Type"] = "application/json"
            content = json.dumps(body).encode("utf-8")
        response = self._send(
            method, url, headers=req_headers, content=content, timeout_ms=timeout_ms
        )
        return self._parse_json_envelope(response)

    def request_binary(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
    ) -> BinaryResult:
        req_headers = self._base_headers(accept="*/*", extra=headers)
        raw_content = content
        if body is not None:
            req_headers.setdefault("Content-Type", "application/json")
            import json

            raw_content = json.dumps(body).encode("utf-8")
        response = self._send(
            method,
            url,
            headers=req_headers,
            content=raw_content,
            timeout_ms=timeout_ms,
        )
        if response.status_code == 304:
            header_map = _header_map(response.headers)
            if_none = (headers or {}).get("If-None-Match")
            return BinaryResult(
                data=b"",
                content_type=response.headers.get(
                    "content-type", "application/octet-stream"
                ),
                request_id=response.headers.get("x-request-id", ""),
                headers=header_map,
                etag=response.headers.get("etag") or if_none,
                width=_num_header(response.headers, "x-image-width"),
                height=_num_header(response.headers, "x-image-height"),
                format=response.headers.get("x-image-format"),
                transformation_id=response.headers.get("x-transformation-id"),
                cache=response.headers.get("x-cache"),
                pdf_page=_num_header(response.headers, "x-pdf-page"),
                not_modified=True,
            )
        if response.is_error:
            raise self._error_from_response(response)
        return self._binary_from_response(response)

    def request_multipart_json(
        self,
        method: str,
        url: str,
        *,
        files: list[tuple[str, tuple[str, bytes, str]]],
        upload_length: int | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
    ) -> JsonSuccess:
        req_headers = self._base_headers(accept="application/json", extra=headers)
        if upload_length is not None:
            req_headers["X-Upload-Length"] = str(upload_length)
        response = self._send(
            method,
            url,
            headers=req_headers,
            files=files,
            timeout_ms=timeout_ms,
        )
        return self._parse_json_envelope(response)

    def request_multipart_binary(
        self,
        method: str,
        url: str,
        *,
        files: list[tuple[str, tuple[str, bytes, str]]],
        upload_length: int | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
    ) -> BinaryResult | JsonSuccess:
        req_headers = self._base_headers(accept="*/*", extra=headers)
        if upload_length is not None:
            req_headers["X-Upload-Length"] = str(upload_length)
        response = self._send(
            method,
            url,
            headers=req_headers,
            files=files,
            timeout_ms=timeout_ms,
        )
        if response.is_error:
            raise self._error_from_response(response)
        ct = response.headers.get("content-type", "")
        if "application/json" in ct:
            return self._parse_json_envelope(response)
        return self._binary_from_response(response)

    def _base_headers(
        self, *, accept: str, extra: dict[str, str] | None
    ) -> dict[str, str]:
        headers = {
            "Accept": accept,
            "X-API-Key": self.config.api_key,
            "User-Agent": self.config.user_agent,
        }
        if extra:
            headers.update(extra)
        return headers

    def _timeout(self, timeout_ms: int | None) -> httpx.Timeout:
        ms = self.config.timeout_ms if timeout_ms is None else timeout_ms
        return httpx.Timeout(ms / 1000.0)

    def _send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        content: bytes | None = None,
        files: list[tuple[str, tuple[str, bytes, str]]] | None = None,
        timeout_ms: int | None = None,
    ) -> httpx.Response:
        try:
            return self._client.request(
                method,
                url,
                headers=headers,
                content=content,
                files=files,
                timeout=self._timeout(timeout_ms),
            )
        except httpx.TimeoutException as exc:
            ms = self.config.timeout_ms if timeout_ms is None else timeout_ms
            raise NetworkError(
                f"Request timed out after {ms}ms",
                cause=exc,
            ) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(
                str(exc) or "Network request failed",
                cause=exc,
            ) from exc

    def _binary_from_response(self, response: httpx.Response) -> BinaryResult:
        return BinaryResult(
            data=response.content,
            content_type=response.headers.get(
                "content-type", "application/octet-stream"
            ),
            request_id=response.headers.get("x-request-id", ""),
            headers=_header_map(response.headers),
            etag=response.headers.get("etag"),
            width=_num_header(response.headers, "x-image-width"),
            height=_num_header(response.headers, "x-image-height"),
            format=response.headers.get("x-image-format"),
            transformation_id=response.headers.get("x-transformation-id"),
            cache=response.headers.get("x-cache"),
            pdf_page=_num_header(response.headers, "x-pdf-page"),
        )

    def _parse_json_envelope(self, response: httpx.Response) -> JsonSuccess:
        request_id = response.headers.get("x-request-id")
        try:
            payload = response.json()
        except ValueError as exc:
            if response.is_error:
                raise map_http_error(
                    status=response.status_code,
                    message=response.reason_phrase or "Request failed",
                    request_id=request_id,
                ) from exc
            raise NetworkError(
                "Response was not valid JSON",
                request_id=request_id,
                cause=exc,
            ) from exc
        if response.is_error:
            raise self._error_from_payload(response.status_code, payload, request_id)
        if (
            not isinstance(payload, dict)
            or payload.get("success") is not True
            or "data" not in payload
        ):
            raise map_http_error(
                status=response.status_code,
                message="Unexpected success envelope",
                request_id=request_id,
            )
        meta = payload.get("meta") or {}
        return JsonSuccess(
            data=payload["data"],
            meta={
                "requestId": meta.get("requestId") or request_id or "",
                "page": meta.get("page"),
                "limit": meta.get("limit"),
                "total": meta.get("total"),
                "pages": meta.get("pages"),
            },
        )

    def _error_from_response(self, response: httpx.Response) -> Exception:
        request_id = response.headers.get("x-request-id")
        try:
            payload = response.json()
        except ValueError:
            return map_http_error(
                status=response.status_code,
                message=response.reason_phrase or "Request failed",
                request_id=request_id,
            )
        return self._error_from_payload(response.status_code, payload, request_id)

    def _error_from_payload(
        self,
        status: int,
        payload: Any,
        request_id: str | None,
    ) -> Exception:
        err = None
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            err = payload["error"]
            meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
            request_id = meta.get("requestId") or request_id
        return map_http_error(
            status=status,
            code=err.get("code") if err else None,
            message=(err.get("message") if err else None) or "Request failed",
            request_id=request_id,
            details=err.get("details") if err else None,
        )


def _encode_segment(segment: str) -> str:
    return quote(segment, safe="")


def build_query(params: dict[str, Any]) -> str:
    items: list[tuple[str, str]] = []
    for key, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            items.append((key, "true" if value else "false"))
        else:
            items.append((key, str(value)))
    return urlencode(items)
