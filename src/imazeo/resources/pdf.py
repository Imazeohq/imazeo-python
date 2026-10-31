"""PDF tools resource."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from imazeo._http import HttpTransport, JsonSuccess, build_query, prepare_upload
from imazeo.types import (
    BinaryResult,
    PdfExtractOptions,
    PdfInfo,
    PdfMultiPageResult,
    PdfRenderOptions,
    PdfRenderPage,
    UploadSource,
)
from imazeo.version import PDF_TIMEOUT_MS


class PdfResource:
    def __init__(
        self,
        http: HttpTransport,
        project_id: Callable[[], str],
    ) -> None:
        self._http = http
        self._project_id = project_id

    def info(
        self,
        source: UploadSource,
        *,
        filename: str | None = None,
    ) -> PdfInfo:
        project_id = self._project_id()
        prepared = prepare_upload(
            source,
            filename=filename or "document.pdf",
            content_type="application/pdf",
        )
        files = [
            ("file", (prepared.filename, prepared.data, prepared.content_type)),
        ]
        url = self._http.path("projects", project_id, "tools", "pdf", "info")
        res = self._http.request_multipart_json(
            "POST",
            url,
            files=files,
            timeout_ms=PDF_TIMEOUT_MS,
        )
        return res.data  # type: ignore[no-any-return]

    def render(
        self,
        source: UploadSource,
        options: PdfRenderOptions | None = None,
        *,
        filename: str | None = None,
    ) -> BinaryResult | PdfMultiPageResult:
        options = options or {}
        project_id = self._project_id()
        prepared = prepare_upload(
            source,
            filename=filename or "document.pdf",
            content_type="application/pdf",
        )
        files = [
            ("file", (prepared.filename, prepared.data, prepared.content_type)),
        ]
        query: dict[str, object] = {}
        if "pages" in options:
            query["pages"] = options["pages"]
        if "rangeStart" in options:
            query["rangeStart"] = options["rangeStart"]
        if "rangeEnd" in options:
            query["rangeEnd"] = options["rangeEnd"]
        if "all" in options:
            query["all"] = options["all"]
        if "format" in options:
            query["format"] = options["format"]
        if "scale" in options:
            query["scale"] = options["scale"]
        if "quality" in options:
            query["quality"] = options["quality"]
        qs = build_query(query)
        url = self._http.path("projects", project_id, "tools", "pdf", "render")
        if qs:
            url = f"{url}?{qs}"
        result = self._http.request_multipart_binary(
            "POST",
            url,
            files=files,
            timeout_ms=PDF_TIMEOUT_MS,
        )
        if isinstance(result, JsonSuccess):
            pages: list[PdfRenderPage] = (result.data or {}).get("pages") or []
            return PdfMultiPageResult(
                pages=pages,
                request_id=result.meta.get("requestId") or "",
            )
        return result

    def merge(self, sources: Sequence[UploadSource]) -> BinaryResult:
        if not sources:
            raise ValueError("At least one PDF is required")
        project_id = self._project_id()
        files: list[tuple[str, tuple[str, bytes, str]]] = []
        for i, source in enumerate(sources):
            prepared = prepare_upload(
                source,
                filename=f"file-{i + 1}.pdf",
                content_type="application/pdf",
            )
            files.append(
                ("file", (prepared.filename, prepared.data, prepared.content_type))
            )
        url = self._http.path("projects", project_id, "tools", "pdf", "merge")
        result = self._http.request_multipart_binary(
            "POST",
            url,
            files=files,
            timeout_ms=PDF_TIMEOUT_MS,
        )
        if isinstance(result, JsonSuccess):
            raise RuntimeError("Expected PDF binary response from merge")
        return result

    def extract(
        self,
        source: UploadSource,
        options: PdfExtractOptions,
        *,
        filename: str | None = None,
    ) -> BinaryResult:
        project_id = self._project_id()
        prepared = prepare_upload(
            source,
            filename=filename or "document.pdf",
            content_type="application/pdf",
        )
        files = [
            ("file", (prepared.filename, prepared.data, prepared.content_type)),
        ]
        query: dict[str, object] = {}
        if "pages" in options:
            query["pages"] = options["pages"]
        if "rangeStart" in options:
            query["rangeStart"] = options["rangeStart"]
        if "rangeEnd" in options:
            query["rangeEnd"] = options["rangeEnd"]
        qs = build_query(query)
        url = self._http.path("projects", project_id, "tools", "pdf", "extract")
        if qs:
            url = f"{url}?{qs}"
        result = self._http.request_multipart_binary(
            "POST",
            url,
            files=files,
            timeout_ms=PDF_TIMEOUT_MS,
        )
        if isinstance(result, JsonSuccess):
            raise RuntimeError("Expected PDF binary response from extract")
        return result
