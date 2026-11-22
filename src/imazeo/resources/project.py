"""Project resource helpers."""
from __future__ import annotations
from collections.abc import Callable, Mapping
from imazeo._http import HttpTransport, build_query
from imazeo.types import Page

def processing_headers(idempotency_key: str | None = None, quote_id: str | None = None) -> dict[str, str]:
    headers = {}
    if idempotency_key:
        headers['Idempotency-Key'] = idempotency_key
    if quote_id:
        headers['X-Quote-ID'] = quote_id
    return headers

class ProjectResource:
    def __init__(self, http: HttpTransport, project_id: Callable[[], str]) -> None:
        self._http = http
        self._project_id = project_id

    def _url(self, *parts: str, query: Mapping[str, object] | None = None) -> str:
        url = self._http.path('projects', self._project_id(), *parts)
        qs = build_query(dict(query or {}))
        return url + ('?' + qs if qs else '')

    def _page(self, parts: tuple[str, ...], params: dict[str, object] | None = None) -> Page:
        result = self._http.request_json('GET', self._url(*parts, query=params))
        meta = result.meta
        return Page(items=result.data, page=meta.get('page', 1), limit=meta.get('limit', 20), total=meta.get('total', len(result.data)), pages=meta.get('pages', 1), request_id=meta.get('requestId', ''))
