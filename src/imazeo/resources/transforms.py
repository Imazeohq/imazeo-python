"""Transforms resource."""

from __future__ import annotations

from collections.abc import Callable

from imazeo._http import HttpTransport, build_query
from imazeo.types import (
    BinaryResult,
    Page,
    PageParams,
    TransformationRecord,
    TransformRequest,
)


class TransformsResource:
    def __init__(
        self,
        http: HttpTransport,
        project_id: Callable[[], str],
    ) -> None:
        self._http = http
        self._project_id = project_id

    def create(self, request: TransformRequest) -> BinaryResult:
        if not request.get("imageId") and not request.get("url"):
            raise ValueError("Exactly one of imageId or url is required")
        if request.get("imageId") and request.get("url"):
            raise ValueError("Provide only one of imageId or url")
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "transforms")
        return self._http.request_binary(
            "POST",
            url,
            body=request,
            headers={"Content-Type": "application/json", "Accept": "*/*"},
        )

    def list(self, params: PageParams | None = None) -> Page[TransformationRecord]:
        params = params or PageParams()
        project_id = self._project_id()
        query: dict[str, object] = {}
        if params.page is not None:
            query["page"] = params.page
        if params.limit is not None:
            query["limit"] = params.limit
        qs = build_query(query)
        url = self._http.path("projects", project_id, "transforms")
        if qs:
            url = f"{url}?{qs}"
        res = self._http.request_json("GET", url)
        items: list[TransformationRecord] = res.data or []
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

    def get(self, transformation_id: str) -> TransformationRecord:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "transforms", transformation_id)
        res = self._http.request_json("GET", url)
        return res.data  # type: ignore[no-any-return]

    def download(
        self,
        transformation_id: str,
        *,
        if_none_match: str | None = None,
    ) -> BinaryResult:
        project_id = self._project_id()
        url = self._http.path(
            "projects", project_id, "transforms", transformation_id, "content"
        )
        headers: dict[str, str] = {}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        return self._http.request_binary("GET", url, headers=headers)

    def delete(self, transformation_id: str) -> dict[str, str]:
        project_id = self._project_id()
        url = self._http.path("projects", project_id, "transforms", transformation_id)
        res = self._http.request_json("DELETE", url)
        return res.data  # type: ignore[no-any-return]
