from __future__ import annotations
from imazeo.api_types import OutputRow, OutputsSummary
from imazeo.types import Page
from imazeo.resources.project import ProjectResource
class OutputsResource(ProjectResource):
    def summary(self) -> OutputsSummary:
        return self._http.request_json('GET', self._url('outputs', 'summary')).data
    def list(self, params: dict[str, object] | None = None) -> Page[OutputRow]:
        return self._page(('outputs',), params)
