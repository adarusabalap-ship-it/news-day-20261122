import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")

LIMIT_BYTES = 1 << 20
LIMIT_SIDE = 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"
JPEG_SIG = b"\xff\xd8\xff"


def inspect(path):
    """Read the picture and refuse anything the gate would refuse."""
    raw = path.read_bytes()
    if raw.startswith(PNG_SIG):
        if len(raw) < 24:
            raise SystemExit("%s: truncated PNG header" % path.name)
        width = int.from_bytes(raw[16:20], "big")
        height = int.from_bytes(raw[20:24], "big")
    elif raw.startswith(JPEG_SIG):
        width, height = jpeg_size(raw)
    else:
        raise SystemExit("%s is neither a PNG nor a JPEG" % path.name)
    if len(raw) > LIMIT_BYTES:
        raise SystemExit("%s is %d bytes, over the 1 MiB cap" % (path.name, len(raw)))
    if not width or not height:
        raise SystemExit("%s has no readable size" % path.name)
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        raise SystemExit("%s is %dx%d, over %d" % (path.name, width, height, LIMIT_SIDE))
    return width, height, len(raw)


def jpeg_size(raw):
    """Walk the JPEG segments to the frame header that holds the size."""
    i = 2
    n = len(raw)
    while i + 9 < n:
        if raw[i] != 0xFF:
            i += 1
            continue
        marker = raw[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = int.from_bytes(raw[i + 2:i + 4], "big")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height = int.from_bytes(raw[i + 5:i + 7], "big")
            width = int.from_bytes(raw[i + 7:i + 9], "big")
            return width, height
        i += 2 + seg_len
    return 0, 0


def main():
    src = HERE / "entry.png"
    width, height, size = inspect(src)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")
    print("entry.png %dx%d, %d bytes -> %s" % (width, height, size, OUT))


if __name__ == "__main__":
    main()
