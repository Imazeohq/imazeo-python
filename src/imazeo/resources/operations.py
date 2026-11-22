from __future__ import annotations
import json
from imazeo.api_types import ProcessingStatus, ProcessingLookupInput
from imazeo.types import BinaryResult
from imazeo.resources.project import ProjectResource
class OperationsResource(ProjectResource):
    def get(self, id: str) -> ProcessingStatus:
        return self._http.request_json('GET', self._url('operations', id)).data
    def lookup(self, input: ProcessingLookupInput) -> ProcessingStatus:
        return self._http.request_json('POST', self._url('operations', 'lookup'), body=input).data
    def result(self, id: str) -> BinaryResult | object:
        result = self._http.request_binary('GET', self._url('operations', id, 'result'))
        return json.loads(result.data)['data'] if 'application/json' in result.content_type else result
