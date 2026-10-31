"""SDK and API version constants."""

from __future__ import annotations

from typing import Final, Literal

SDK_VERSION: Final = "1.0.0"
DEFAULT_API_VERSION: Final = "v1"
SUPPORTED_API_VERSIONS: Final = ("v1",)
ApiVersion = Literal["v1"]
DEFAULT_BASE_URL: Final = "https://api.imazeo.com"
DEFAULT_TIMEOUT_MS: Final = 60_000
PDF_TIMEOUT_MS: Final = 120_000
LIGHT_TIMEOUT_MS: Final = 30_000
