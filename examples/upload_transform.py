"""Upload an image and run an ephemeral transform.

Usage: python examples/upload_transform.py <image>
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
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python examples/upload_transform.py <image>")

    input_path = Path(sys.argv[1])
    bytes_ = input_path.read_bytes()

    with Imazeo(
        api_key=api_key,
        base_url=os.environ.get("IMAZEO_BASE_URL", "http://localhost:3001"),
        project_id=os.environ.get("IMAZEO_PROJECT_ID"),
    ) as client:
        image = client.images.upload(
            bytes_,
            filename=input_path.name or "input.bin",
            content_type="application/octet-stream",
        )
        print("uploaded", image["_id"], image["metadata"])

        transformed = client.transforms.create(
            {
                "imageId": image["_id"],
                "mode": "EPHEMERAL",
                "transform": {"width": 800, "format": "webp", "quality": 80},
            }
        )
        Path("out.webp").write_bytes(transformed.data)
        print("wrote out.webp", transformed.transformation_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 — example script
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
