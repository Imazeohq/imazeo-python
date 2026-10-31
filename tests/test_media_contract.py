import json
import httpx
from imazeo import Imazeo


def test_barcode_names_and_pdf_merge_fields():
    def handler(request: httpx.Request):
        if request.url.path.endswith('/barcode'):
            assert json.loads(request.content) == {
                'type': 'ean8', 'content': '0123456', 'format': 'svg', 'includeText': False,
            }
            return httpx.Response(200, content=b'<svg/>', headers={'content-type': 'image/svg+xml'})
        assert request.url.path.endswith('/pdf/merge')
        body = request.read()
        assert body.count(b'name="file"') == 2
        assert body.index(b'first') < body.index(b'second')
        return httpx.Response(200, content=b'pdf', headers={'content-type': 'application/pdf'})

    client = Imazeo(api_key='test', project_id='project', http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    client.barcodes.generate({'type': 'ean8', 'content': '0123456', 'format': 'svg', 'includeText': False})
    client.pdf.merge([b'first', b'second'])
