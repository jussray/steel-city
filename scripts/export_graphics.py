"""Reproducibly export the approved Pittsburgh skyline from the game's art source.

Read-only verification is the default; --write only updates this one derived image.
This 2D key-art image is not a textured/rigged production 3D model.
"""
from pathlib import Path
import argparse
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "index.html"
TARGET = ROOT / "assets" / "pittsburgh-night-skyline.jpg"


def source_bytes():
    html = GAME.read_text(encoding="utf-8")
    match = re.search(r"data:image/jpeg;base64,([A-Za-z0-9+/=]+)", html)
    if not match:
        raise SystemExit("BLOCKED: Approved skyline art missing from game source")
    payload = base64.b64decode(match.group(1), validate=True)
    if not payload.startswith(b"\xff\xd8\xff") or not payload.endswith(b"\xff\xd9"):
        raise SystemExit("BLOCKED: Invalid JPEG source art")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Export the currently embedded art into the static assets directory")
    args = parser.parse_args()
    expected = source_bytes()
    if args.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(expected)
    if not TARGET.is_file() or TARGET.read_bytes() != expected:
        raise SystemExit("BLOCKED: Exported graphics asset missing or drifted; run --write in reviewed source tree")
    print(f"PASS: {TARGET.relative_to(ROOT)} exactly matches embedded approved art ({len(expected)} bytes)")


if __name__ == "__main__":
    main()