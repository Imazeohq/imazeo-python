# imazeo

Official **server-side** Python SDK for Imazeo.

|                |                                 |
| -------------- | ------------------------------- |
| Package        | `imazeo`                        |
| SDK version    | `1.0.0`                         |
| Default API    | `v1`                            |
| Supported APIs | `v1`                            |
| Runtime        | Python **3.10+** (sync `httpx`) |
| Registry       | [PyPI](https://pypi.org/project/imazeo/) |
| Source         | [GitHub](https://github.com/Imazeohq/imazeo-python) |

> **Security:** Secret API keys (`X-API-Key`) are for trusted servers only.
> Do **not** ship this client with a secret key in browsers or client apps.

Integration contract and learning path: [GUIDE.md](GUIDE.md).

## Install

```bash
pip install imazeo
```

Requires Python 3.10+. Create a project API key in the
[Imazeo Customer portal](https://app.imazeo.com).
Default API origin is `https://api.imazeo.com` (override with `base_url` when needed).

## Learning path

Read the self-contained [integration guide](GUIDE.md) for project/key setup,
language examples, PDF response types, pagination, output retention, troubleshooting
and production practices.

The default HTTP client refuses redirects so credentials stay on the configured
API origin.

## Quick start

```python
from pathlib import Path
from imazeo import Imazeo
import os

client = Imazeo(
    api_key=os.environ["IMAZEO_API_KEY"],
    base_url=os.environ["IMAZEO_API_ORIGIN"],  # supplied API origin
    # project_id="…",  # optional; otherwise resolved via /v1/api-key/context
)

qr = client.qr.generate({
    "content": "https://imazeo.com",
    "format": "png",
    "size": 256,
})
Path("qr.png").write_bytes(qr.data)
client.close()
```

Or use as a context manager:

```python
with Imazeo(api_key=os.environ["IMAZEO_API_KEY"]) as client:
    ctx = client.context.get()
    print(ctx["projectId"], ctx["keyId"])
```

## Authentication

```python
Imazeo(api_key=os.environ["IMAZEO_API_KEY"])
```

Sends `X-API-Key` only. Never send `Authorization` together with an API key
(backend rejects that combination).

## Resources

| Resource            | Methods                                                                          |
| ------------------- | -------------------------------------------------------------------------------- |
| `client.context`    | `get()` → project/key IDs                                                        |
| `client.images`     | `upload`, `list` (`page`/`limit`/`q`), `get`, `delete`, `download`               |
| `client.transforms` | `create`, `list`, `get`, `download` (`if_none_match` → `not_modified`), `delete` |
| `client.qr`         | `generate`                                                                       |
| `client.barcodes`   | `generate`                                                                       |
| `client.pdf`        | `info`, `render`, `merge`, `extract`                                             |

### Upload + transform

```python
image = client.images.upload(
    photo_bytes,
    filename="photo.jpg",
    content_type="image/jpeg",
)

out = client.transforms.create({
    "imageId": image["_id"],
    "mode": "EPHEMERAL",
    "transform": {"width": 1200, "format": "webp", "quality": 85},
})
# out.data → bytes
```

### Remote URL transform

```python
out = client.transforms.create({
    "url": "https://example.com/image.jpg",
    "transform": {"width": 640, "format": "jpeg"},
})
```

### PDF

```python
info = client.pdf.info(pdf_bytes)
page = client.pdf.render(pdf_bytes, {"pages": "1", "format": "png"})
merged = client.pdf.merge([pdf_a, pdf_b])
extracted = client.pdf.extract(pdf_bytes, {"pages": "1,2"})
```

## Errors

```python
from imazeo import ImazeoError, RateLimitError

try:
    client.images.get(image_id)
except RateLimitError as error:
    print(error.code, error.request_id)
except ImazeoError as error:
    print(error.status, error.code, error.message)
```

## Configuration

| Option        | Default                  | Notes                                  |
| ------------- | ------------------------ | -------------------------------------- |
| `api_key`     | required                 | Secret key                             |
| `project_id`  | from context             | Path project                           |
| `base_url`    | `https://api.imazeo.com` | Origin only; `/v1` stripped if present |
| `api_version` | `v1`                     | Allowlisted                            |
| `timeout_ms`  | `60000`                  | PDF uses 120s; QR/barcode 30s          |
| `app_name`    | —                        | Appended to User-Agent                 |
| `transport`   | —                        | Optional `httpx.BaseTransport` (tests) |

## API version vs package version

- **API** path version: `v1` (configured via `api_version`)
- **SDK** SemVer: `1.0.0`

`Imazeo.api_compatibility()` reports supported API versions.

## Not included

Portal JWT APIs (projects CRUD, API-key management, usage, plans, tickets, auth),
admin APIs, tool-artifacts, outputs, and browser secret-key usage.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT

## Barcode and PDF notes

Barcode generation requires `type` and string `content`. Optional `format` is
`png` or `svg` (default `png`); `includeText` defaults to `true`.
PDF merge uploads files in order as repeated multipart `file` parts.
Omit optional fields to use API defaults. Integer fields such as barcode scale
and image hue must be integers.

```python
client.barcodes.generate({'type': 'code128', 'content': 'IMAZEO-2026', 'format': 'svg', 'includeText': False})
```
