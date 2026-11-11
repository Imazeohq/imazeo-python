"""Tests for the Imazeo Python SDK."""

from __future__ import annotations

import json

import httpx
import pytest

from imazeo import (
    AuthenticationError,
    Imazeo,
    PageParams,
    RateLimitError,
    ValidationError,
)
from imazeo._http import normalize_base_url
from imazeo.version import SDK_VERSION


def _json_response(
    data: object,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    if status < 400:
        body: object = {"success": True, "data": data, "meta": {"requestId": "req_test"}}
    else:
        body = {
            "success": False,
            "error": data,
            "meta": {"requestId": "req_test"},
        }
    return httpx.Response(
        status,
        json=body,
        headers={
            "content-type": "application/json",
            "x-request-id": "req_test",
            **(headers or {}),
        },
    )


def _client_with_handler(handler) -> Imazeo:
    transport = httpx.MockTransport(handler)
    return Imazeo(
        api_key="secret-key",
        base_url="https://api.example.com",
        transport=transport,
    )


def test_normalizes_base_url_and_strips_v1() -> None:
    assert normalize_base_url("https://api.example.com/") == "https://api.example.com"
    assert normalize_base_url("https://api.example.com/v1") == "https://api.example.com"
    with pytest.raises(ValueError):
        normalize_base_url("ftp://x")


def test_rejects_unsupported_api_version() -> None:
    with pytest.raises(ValueError, match="Unsupported apiVersion"):
        Imazeo(api_key="key", api_version="v9")  # type: ignore[arg-type]


def test_sends_x_api_key_and_user_agent() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.example.com/v1/api-key/context"
        assert request.headers.get("X-API-Key") == "secret-key"
        assert request.headers.get("User-Agent", "").startswith(f"Imazeo-Python/{SDK_VERSION}")

        assert "Authorization" not in request.headers
        return _json_response(
            {"projectId": "proj_1", "keyId": "key_1"}
        )

    client = _client_with_handler(handler)
    ctx = client.context.get()
    assert ctx["projectId"] == "proj_1"
    client.close()


def test_resolves_project_id_from_context_when_omitted() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if str(request.url).endswith("/api-key/context"):
            return _json_response(
                {"projectId": "proj_auto", "keyId": "k"}
            )
        assert "/v1/projects/proj_auto/images" in str(request.url)
        return _json_response([])

    client = Imazeo(
        api_key="k",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    page = client.images.list(PageParams(page=1, limit=10))
    assert page.items == []
    assert page.request_id == "req_test"
    client.close()


def test_uploads_with_x_upload_length_and_multipart_file_field() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Upload-Length") == "4"
        content_type = request.headers.get("Content-Type", "")
        assert content_type.startswith("multipart/form-data")
        body = request.content
        assert b'name="file"' in body
        return _json_response(
            {
                "_id": "img_1",
                "projectId": "p1",
                "sourceType": "upload",
                "originalName": "a.png",
                "bytes": 4,
                "sha256": "abc",
                "metadata": {
                    "format": "png",
                    "mimeType": "image/png",
                    "width": 1,
                    "height": 1,
                    "frames": 1,
                    "pixelCount": 1,
                    "hasAlpha": False,
                    "orientation": None,
                },
                "status": "ready",
                "createdAt": "2026-01-01T00:00:00.000Z",
                "updatedAt": "2026-01-01T00:00:00.000Z",
            },
            status=201,
        )

    client = Imazeo(
        api_key="k",
        project_id="p1",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    image = client.images.upload(
        b"\x01\x02\x03\x04",
        filename="a.png",
        content_type="image/png",
    )
    assert image["_id"] == "img_1"
    client.close()


def test_maps_error_envelopes_to_typed_errors() -> None:
    def auth_handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            {"code": "API_KEY_INVALID", "message": "bad key"}, status=401
        )

    client = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(auth_handler),
    )
    with pytest.raises(AuthenticationError):
        client.images.get("x")
    client.close()

    def rate_handler(request: httpx.Request) -> httpx.Response:
        return _json_response(
            {"code": "RATE_LIMIT_EXCEEDED", "message": "slow down"}, status=429
        )

    client2 = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(rate_handler),
    )
    with pytest.raises(RateLimitError):
        client2.images.get("x")
    client2.close()

    def bad_handler(request: httpx.Request) -> httpx.Response:
        return _json_response({"code": "TOOL_INVALID", "message": "bad"}, status=400)

    client3 = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(bad_handler),
    )
    with pytest.raises(ValidationError):
        client3.qr.generate({"content": "hi"})
    client3.close()


def test_returns_binary_results_for_qr_generation() -> None:
    png = bytes([137, 80, 78, 71])

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=png,
            headers={
                "content-type": "image/png",
                "x-request-id": "req_bin",
            },
        )

    client = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    result = client.qr.generate({"content": "https://imazeo.com"})
    assert result.content_type == "image/png"
    assert result.data == png
    assert result.request_id == "req_bin"
    client.close()


def test_passes_image_list_q_filter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "q=photo" in str(request.url)
        return _json_response([])

    client = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    client.images.list(PageParams(q="photo", page=1))
    client.close()


def test_returns_not_modified_on_transform_download_304() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("If-None-Match") == '"abc"'
        return httpx.Response(
            304,
            headers={
                "etag": '"abc"',
                "x-request-id": "req_304",
            },
        )

    client = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    result = client.transforms.download("tr_1", if_none_match='"abc"')
    assert result.not_modified is True
    assert len(result.data) == 0
    assert result.request_id == "req_304"
    assert result.etag == '"abc"'
    client.close()


def test_posts_transform_json_and_returns_binary() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["imageId"] == "img"
        assert payload["transform"] == {"width": 100, "format": "webp"}
        return httpx.Response(
            200,
            content=bytes([1, 2]),
            headers={
                "content-type": "image/webp",
                "x-transformation-id": "tr_1",
                "x-cache": "MISS",
                "x-request-id": "req_t",
            },
        )

    client = Imazeo(
        api_key="k",
        project_id="p",
        base_url="https://api.example.com",
        transport=httpx.MockTransport(handler),
    )
    out = client.transforms.create(
        {"imageId": "img", "transform": {"width": 100, "format": "webp"}}
    )
    assert out.transformation_id == "tr_1"
    assert out.cache == "MISS"
    client.close()
