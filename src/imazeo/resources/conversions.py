from __future__ import annotations
from imazeo.api_types import ConversionCapabilities, ConversionJob, DocxOptions, XlsxOptions, PptxOptions, WebsiteOptions, ToolArtifact
from imazeo.types import BinaryResult, UploadSource
from imazeo._http import prepare_upload
from imazeo.resources.project import ProjectResource, processing_headers
class ConversionsResource(ProjectResource):
    def capabilities(self) -> ConversionCapabilities:
        return self._http.request_json('GET', self._url('conversions', 'capabilities')).data
    def list(self, engine: str = 'docx') -> list[ConversionJob]:
        return self._http.request_json('GET', self._url('conversions', query={'engine': engine})).data
    def get(self, id: str) -> ConversionJob:
        return self._http.request_json('GET', self._url('conversions', id)).data
    def lookup(self, key: str) -> ConversionJob:
        return self._http.request_json('GET', self._url('conversions', 'lookup', query={'key': key})).data
    def cancel(self, id: str) -> ConversionJob:
        return self._http.request_json('POST', self._url('conversions', id, 'cancel')).data
    def save(self, id: str) -> ToolArtifact:
        return self._http.request_json('POST', self._url('conversions', id, 'save')).data
    def download(self, id: str) -> BinaryResult:
        return self._http.request_binary('GET', self._url('conversions', id, 'download'))
    def website(self, url: str, options: WebsiteOptions | None = None, *, idempotency_key: str, quote_id: str) -> ConversionJob:
        return self._http.request_json('POST', self._url('conversions', 'website', query=options), body={'url': url}, headers=processing_headers(idempotency_key, quote_id)).data
    def _upload(self, engine: str, source: UploadSource, options: dict | None, idempotency_key: str, quote_id: str) -> ConversionJob:
        prepared = prepare_upload(source, filename='document.' + engine)
        parts = ('conversions',) if engine == 'docx' else ('conversions', engine)
        return self._http.request_multipart_json('POST', self._url(*parts, query=options), files=[('file', (prepared.filename, prepared.data, prepared.content_type))], upload_length=prepared.byte_length, headers=processing_headers(idempotency_key, quote_id)).data
    def docx(self, source: UploadSource, options: DocxOptions | None = None, *, idempotency_key: str, quote_id: str) -> ConversionJob:
        return self._upload('docx', source, options, idempotency_key, quote_id)
    def xlsx(self, source: UploadSource, options: XlsxOptions | None = None, *, idempotency_key: str, quote_id: str) -> ConversionJob:
        return self._upload('xlsx', source, options, idempotency_key, quote_id)
    def pptx(self, source: UploadSource, options: PptxOptions | None = None, *, idempotency_key: str, quote_id: str) -> ConversionJob:
        return self._upload('pptx', source, options, idempotency_key, quote_id)
