import json
import httpx
from imazeo import Imazeo

KEY = 'c37368a9-ed6f-4a78-9fb0-bb577368bde9'
QUOTE = 'b90144bd-1ef3-49db-84fc-28de61bb1e99'

def client(handler):
    return Imazeo(api_key='test-key', project_id='project', transport=httpx.MockTransport(handler))

def success(data, meta=None):
    return httpx.Response(200, json={'success': True, 'data': data, 'meta': {'requestId': 'request', **(meta or {})}})

def test_conversion_request_headers_and_upload():
    def handler(request):
        assert request.url.path == '/v1/projects/project/conversions/xlsx'
        assert request.url.params['showGridLines'] == 'false'
        assert request.headers['Idempotency-Key'] == KEY
        assert request.headers['X-Quote-ID'] == QUOTE
        assert request.headers['X-Upload-Length'] == '3'
        assert b'\x01\x02\x03' in request.content
        assert request.headers['X-API-Key'] == 'test-key'
        assert 'Authorization' not in request.headers
        return success({'id': 'job'})
    with client(handler) as sdk:
        assert sdk.conversions.xlsx(b'\x01\x02\x03', {'showGridLines': False}, idempotency_key=KEY, quote_id=QUOTE)['id'] == 'job'

def test_artifact_fields_are_multipart_text_fields():
    def handler(request):
        assert b'name="kind"\r\n' in request.content
        assert b'name="kind"; filename=' not in request.content
        assert b'Company QR' in request.content
        assert b'{"format": "png"}' in request.content
        return success({'_id': 'saved'})
    with client(handler) as sdk:
        assert sdk.artifacts.save(b'image', {'kind': 'qr', 'displayName': 'Company QR', 'contentType': 'image/png'}, request_snapshot={'format': 'png'})['_id'] == 'saved'

def test_dynamic_revision_and_scan_filters():
    def handler(request):
        if request.method == 'PATCH':
            assert request.headers['Idempotency-Key'] == KEY
            assert json.loads(request.content) == {'expectedRevision': 0, 'analyticsEnabled': False}
            return success({'revision': 1})
        assert request.url.params['bot'] == 'false'
        return httpx.Response(200, text='date,count\n', headers={'Content-Type': 'text/csv'})
    with client(handler) as sdk:
        assert sdk.dynamic_codes.update('code', {'expectedRevision': 0, 'analyticsEnabled': False}, idempotency_key=KEY)['revision'] == 1
        assert sdk.dynamic_codes.export_analytics('code', {'bot': False}).data == b'date,count\n'

def test_operation_recovery_and_list_metadata():
    def handler(request):
        if request.url.path.endswith('/result'):
            return success({'pages': [{'pageNumber': 1}]})
        return success([{'id': 'output'}], {'page': 2, 'limit': 10, 'total': 11, 'pages': 2})
    with client(handler) as sdk:
        assert sdk.operations.result('operation') == {'pages': [{'pageNumber': 1}]}
        result = sdk.outputs.list({'page': 2, 'limit': 10})
        assert (result.page, result.total, result.pages, result.request_id) == (2, 11, 2, 'request')
