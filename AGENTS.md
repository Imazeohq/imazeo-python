# imazeo (Python) — agent notes

Independent public package for the Imazeo API-key client.

- Contract: published API `v1` (see [GUIDE.md](GUIDE.md))
- Scope: `context`, `images`, `transforms`, `qr`, `barcodes`, `pdf` only
- Do not add admin or customer JWT portal APIs
- Do not publish without maintainer approval — see [RELEASE.md](RELEASE.md)
- Never commit PyPI tokens
- Release: `$env:RELEASE_MODE="true"; npm run release` (syncs `pyproject.toml` + `version.py`); Actions publishes via Trusted Publishing
