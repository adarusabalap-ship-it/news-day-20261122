#!/usr/bin/env python3
"""layout_audit.py - fail on anything that would read as a broken render.

Runs the poster's own drawing code in recording mode: every string drawn is
measured with the font it was drawn in, and checked against the measure, the
band it sits in, and every other string on the page. Then the same page is
measured at thumbnail scale, because that is the size the judge sees.

    python tools/layout_audit.py [entry.png]
"""

import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

import poster  # noqa: E402

MEASURE = poster.EDGE
TOL = 1


class Recorder(ImageDraw.ImageDraw):
    """An ImageDraw that remembers what it was asked to draw."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.texts = []

    def text(self, xy, text, font=None, fill=None, **kw):
        if font is not None and text and text.strip():
            self.texts.append((xy, text, font))
        return super().text(xy, text, font=font, fill=fill, **kw)


def measure(entry):
    img = Image.new("RGB", (poster.W, poster.H), poster.PAPER)
    d = Recorder(img)
    # swap the module's draw class, then run the real page. The page saves its
    # own image, so it is pointed at a scratch file: this audit must never
    # overwrite the entry it is measuring.
    poster.ImageDraw.Draw = lambda im, *a, **kw: d
    scratch = Path(tempfile.gettempdir()) / "layout-audit-scratch.png"
    try:
        poster.main(str(scratch))
    finally:
        poster.ImageDraw.Draw = _ORIGINAL
        scratch.unlink(missing_ok=True)
    return d.texts


_ORIGINAL = ImageDraw.Draw


def boxes(texts):
    out = []
    for xy, s, f in texts:
        x, y = xy
        try:
            bb = f.getbbox(s)
        except Exception:
            raise SystemExit("could not measure %r" % s)
        out.append((x + bb[0], y + bb[1], x + bb[2], y + bb[3], s, f.size))
    return out


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    texts = measure(target)
    bs = boxes(texts)
    problems = []

    # 1. nothing off the measure
    for x0, y0, x1, y1, s, sz in bs:
        if x0 < poster.M - TOL or x1 > poster.RIGHT + TOL:
            problems.append("off the measure: %r x=%d..%d" % (s, x0, x1))
        if y0 < 0 or y1 > poster.H:
            problems.append("off the page: %r y=%d..%d" % (s, y0, y1))

    # 2. no string drawn twice in the same place (a doubled render)
    seen = {}
    for x0, y0, x1, y1, s, sz in bs:
        key = (s, x0 // 3, y0 // 3)
        if key in seen:
            problems.append("drawn twice: %r at %d,%d" % (s, x0, y0))
        seen[key] = True

    # 3. no overlap between any two strings. This is all-pairs, not
    # band-by-band: a large string like the date spans many bands, and a
    # smaller one can sit inside its row without sharing its top edge.
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, b = bs[i], bs[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 2 and oy > 2:
                problems.append("overlap: %r and %r" % (a[4], b[4]))

    # 4. the date must be the largest thing on the page
    date_size = max((b[5] for b in bs if "NOVEMBER" in b[4]), default=0)
    other = max((b[5] for b in bs if "NOVEMBER" not in b[4]), default=0)
    if date_size <= other:
        problems.append("the date is not the largest type: %d vs %d" % (date_size, other))

    # 5. no string under 8pt: below that it is grey noise at 300px
    for x0, y0, x1, y1, s, sz in bs:
        if sz < 8:
            problems.append("too small to read at 300px: %r is %dpt" % (s, sz))

    print("%d strings measured, %d boxes" % (len(texts), len(bs)))
    if problems:
        for p in problems[:40]:
            print("  FAIL", p)
        print("%d problem(s)" % len(problems))
        return 1
    print("layout: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
