from __future__ import annotations
from imazeo.api_types import DynamicCapabilities, DynamicCode, DynamicCreateInput, DynamicEditInput, ScanAnalytics, ScanQuery
from imazeo.types import BinaryResult, Page
from imazeo.resources.project import ProjectResource, processing_headers
class DynamicCodesResource(ProjectResource):
    def capabilities(self) -> DynamicCapabilities:
        return self._http.request_json('GET', self._url('dynamic-codes', 'capabilities')).data
    def list(self, params: dict[str, object] | None = None) -> Page[DynamicCode]:
        return self._page(('dynamic-codes',), params)
    def get(self, id: str) -> DynamicCode:
        return self._http.request_json('GET', self._url('dynamic-codes', id)).data
    def create(self, input: DynamicCreateInput, *, idempotency_key: str) -> DynamicCode:
        return self._http.request_json('POST', self._url('dynamic-codes'), body=input, headers=processing_headers(idempotency_key)).data
    def update(self, id: str, input: DynamicEditInput, *, idempotency_key: str) -> DynamicCode:
        return self._http.request_json('PATCH', self._url('dynamic-codes', id), body=input, headers=processing_headers(idempotency_key)).data
    def analytics(self, id: str, query: ScanQuery | None = None) -> ScanAnalytics:
        return self._http.request_json('GET', self._url('dynamic-codes', id, 'analytics', query=query)).data
    def export_analytics(self, id: str, query: ScanQuery | None = None) -> BinaryResult:
        return self._http.request_binary('GET', self._url('dynamic-codes', id, 'analytics', 'export', query=query))
