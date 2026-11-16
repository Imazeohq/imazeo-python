from __future__ import annotations
import json
from imazeo.api_types import ArtifactSaveInput, ToolArtifact
from imazeo.types import BinaryResult, Page, UploadSource
from imazeo._http import prepare_upload
from imazeo.resources.project import ProjectResource
class ArtifactsResource(ProjectResource):
    def list(self, params: dict[str, object] | None = None) -> Page[ToolArtifact]:
        return self._page(('tools', 'artifacts'), params)
    def get(self, id: str) -> ToolArtifact:
        return self._http.request_json('GET', self._url('tools', 'artifacts', id)).data
    def delete(self, id: str) -> dict[str, str]:
        return self._http.request_json('DELETE', self._url('tools', 'artifacts', id)).data
    def download(self, id: str) -> BinaryResult:
        return self._http.request_binary('GET', self._url('tools', 'artifacts', id, 'content'))
    def save(self, source: UploadSource, input: ArtifactSaveInput, *, request_snapshot: dict[str, object] | None = None, source_image_id: str | None = None) -> ToolArtifact:
        prepared = prepare_upload(source, content_type=input['contentType'])
        fields = dict(input)
        if request_snapshot is not None:
            fields['requestSnapshot'] = json.dumps(request_snapshot)
        if source_image_id is not None:
            fields['sourceImageId'] = source_image_id
        files = [('file', (prepared.filename, prepared.data, prepared.content_type))]
        files.extend((key, (None, str(value).encode(), 'text/plain')) for key, value in fields.items())
        return self._http.request_multipart_json('POST', self._url('tools', 'artifacts'), files=files, upload_length=prepared.byte_length).data
