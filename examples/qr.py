"""Minimal server-side QR example.

Requires: IMAZEO_API_KEY, optional IMAZEO_BASE_URL, IMAZEO_PROJECT_ID
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from imazeo import Imazeo


def main() -> None:
    api_key = os.environ.get("IMAZEO_API_KEY")
    if not api_key:
        raise SystemExit("Set IMAZEO_API_KEY")

    with Imazeo(
        api_key=api_key,
        base_url=os.environ.get("IMAZEO_BASE_URL", "https://api.imazeo.com"),
        project_id=os.environ.get("IMAZEO_PROJECT_ID"),
    ) as client:
        ctx = client.context.get()
        print("project", ctx["projectId"], "env", ctx["environment"])

        qr = client.qr.generate(
            {
                "content": "https://imazeo.com",
                "size": 256,
                "format": "png",
            }
        )
        Path("qr.png").write_bytes(qr.data)
        print("wrote qr.png", qr.content_type)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 — example script
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
