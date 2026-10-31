"""Images resource."""

from __future__ import annotations

from collections.abc import Callable

from imazeo._http import HttpTransport, build_query, prepare_upload
from imazeo.types import BinaryResult, ImageRecord, Page, PageParams, UploadSource


class ImagesResource:
    def __init__(
        self,
        http: HttpTransport,
        project_id: Callable[[], str],
    ) -> None:
        self._http = http
        self._project_id = project_id

    def upload(
        self,
        source: UploadSource,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> ImageRecord:
        project_id = self._project_id()
        prepared = prepare_upload(
            source, filename=filename, content_type=content_type
        )
        files = [
            ("file", (prepared.filename, prepared.data, prepared.content_type)),
        ]
        url = self._http.path("projects", project_id, "images")
        res = self._http.request_multipart_json(
            "POST",
            url,
            files=files,
            upload_length=prepared.byte_length,
        )
        return res.data  # type: ignore[no-any-return]

    def list(self, params: PageParams | None = None) -> Page[ImageRecord]:
        params = params or PageParams()
        project_id = self._project_id()
        query: dict[str, object] = {}
        if params.page is not None:
            query["page"] = params.page
        if params.limit is not None:
            query["limit"] = params.limit
        if params.q:
            query["q"] = params.q
        qs = build_query(query)
        url = self._http.path("projects", project_id, "images")
        if qs:
            url = f"{url}?{qs}"
        res = self._http.request_json("GET", url)
        items: list[ImageRecord] = res.data or []
        meta = res.meta
        return Page(
            items=items,
            page=meta.get("page") if meta.get("page") is not None else (params.page or 1),
            limit=meta.get("limit")
            if meta.get("limit") is not None
            else (params.limit or 20),
            total=meta.get("total") if meta.get("total") is not None else len(items),
            pages=meta.get("pages") if meta.get("pages") is not None else 1,
            request_id=meta.get("requestId") or "",
        )

    def get(self, image_id: str) -> ImageRecord:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "images", image_id)
        res = self._http.request_json("GET", url)
        return res.data  # type: ignore[no-any-return]

    def delete(self, image_id: str) -> dict[str, str]:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "images", image_id)
        res = self._http.request_json("DELETE", url)
        return res.data  # type: ignore[no-any-return]

    def download(self, image_id: str) -> BinaryResult:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "images", image_id, "content")
        return self._http.request_binary("GET", url)
