"""Generate ``lyra.ico`` without third-party tools.

Draws the Lyra orb (the same accent gradient as the web GUI) and writes a
multi-size PNG-compressed ICO. Standard library only, so it runs anywhere:

    python packaging/windows/make_icon.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZES = (256, 128, 64, 48, 32, 16)
TOP = (110, 168, 255)     # --accent
BOTTOM = (155, 123, 255)  # --accent-2


def _pixel(x: int, y: int, size: int) -> tuple[int, int, int, int]:
    cx = cy = (size - 1) / 2
    radius = size * 0.46
    dx, dy = x - cx, y - cy
    dist = (dx * dx + dy * dy) ** 0.5
    if dist > radius:
        return (0, 0, 0, 0)
    t = y / max(size - 1, 1)
    r = round(TOP[0] + (BOTTOM[0] - TOP[0]) * t)
    g = round(TOP[1] + (BOTTOM[1] - TOP[1]) * t)
    b = round(TOP[2] + (BOTTOM[2] - TOP[2]) * t)
    # Feather the rim so the orb sits softly on any background.
    edge = max(0.0, min(1.0, (radius - dist) / 2.5))
    return (r, g, b, round(255 * edge))


def _png(size: int) -> bytes:
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0
        for x in range(size):
            raw.extend(_pixel(x, y, size))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def build_ico(target: Path) -> None:
    images = [_png(size) for size in SIZES]
    count = len(images)
    header = struct.pack("<HHH", 0, 1, count)  # reserved, type=icon, count
    offset = 6 + 16 * count
    entries, blobs = b"", b""
    for size, png in zip(SIZES, images):
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        blobs += png
        offset += len(png)
    target.write_bytes(header + entries + blobs)


if __name__ == "__main__":
    out = Path(__file__).with_name("lyra.ico")
    build_ico(out)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
