# SDK-2 plan — Python

**Status: implemented (1.0.0)**

1. ~~Mirror TypeScript resource surface (`context`, `images`, `transforms`, `qr`, `barcodes`, `pdf`)~~
2. ~~Use `httpx` with finite timeouts~~
3. ~~Typed models via TypedDict / dataclasses (lean, no pydantic)~~
4. ~~Multipart + `X-Upload-Length`~~
5. ~~Error hierarchy matching SDK_BEHAVIOR~~
6. ~~pytest unit tests with `httpx.MockTransport`~~
7. CI on supported Python versions (evaluate 3.10+) — deferred until registry/CI ownership

Reference: `../sdk-typescript/`
Contract: `../docs/SDK_BEHAVIOR.md`

PyPI project name `imazeo` is reserved for this SDK. Confirm your PyPI account
owns the first upload before publishing `1.0.0`.
