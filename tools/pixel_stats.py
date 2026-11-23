#!/usr/bin/env python3
"""pixel_stats.py - measure the page the way the playbook measures winners.

The strongest entries in this family share three measurable habits: a high
share of light pixels, a small dark share, and a disciplined palette. This
prints those numbers for the page at both full size and at thumbnail size,
so a build can be compared against the recorded benchmarks before it is sent.

    python tools/pixel_stats.py [entry.png]
"""

import sys
from collections import Counter

from PIL import Image

# The reference is the artifacts that actually placed first, second and third
# in this competition, measured by this tool -- not a figure written down from
# memory. The first version of this file carried the latter (dark <= 0.12,
# saturated <= 0.08, colours <= 150) and every one of those bounds was wrong:
# the winners measure dark 0.168-0.214, saturated 0.105-0.233 and 931-1664
# colours. A page tuned to the remembered numbers stripped its own colour out
# and read as a pale sheet beside them, which is exactly what happened.
#
#   rank1  dark 0.214  light 0.632  saturated 0.233  colours  931
#   rank2  dark 0.168  light 0.648  saturated 0.105  colours 1664
#   rank3  dark 0.195  light 0.687  saturated 0.147  colours 1266
REF = {
    "dark": (0.168, 0.214),
    "light": (0.632, 0.687),
    "saturated": (0.105, 0.233),
    "colours": (931, 1664),
}
BENCH = REF  # kept so older callers do not break


def stats(path, side=None, step=1):
    im = Image.open(path).convert("RGB")
    if side:
        im = im.resize((side, side), Image.LANCZOS)
    px = im.load()
    w, h = im.size
    dark = light = sat = 0
    n = 0
    colours = Counter()
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            n += 1
            v = (r * 299 + g * 587 + b * 114) // 1000
            if v < 70:
                dark += 1
            if v > 200:
                light += 1
            mx, mn = max(r, g, b), min(r, g, b)
            if mx and (mx - mn) / mx > 0.45:
                sat += 1
            colours[(r // 16, g // 16, b // 16)] += 1
    return {
        "dark": dark / n,
        "light": light / n,
        "saturated": sat / n,
        "colours": len(colours),
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    full = stats(path, None, 4)
    thumb = stats(path, 300, 1)
    # the colour count is a count of distinct colours, so it has to be taken
    # at full resolution: sampling every fourth pixel finds a fraction of them
    # and would report a rich page as poor
    full["colours"] = stats(path, None, 1)["colours"]

    print("%-12s %8s %8s %15s" % ("", "full", "300px", "winners"))
    print("-" * 50)
    fails = []
    for k in ("dark", "light", "saturated"):
        lo, hi = REF[k]
        inside = lo <= full[k] <= hi
        mark = "ok" if inside else ("low" if full[k] < lo else "high")
        if not inside:
            fails.append("%s %.3f outside %.3f-%.3f" % (k, full[k], lo, hi))
        print("%-12s %8.3f %8.3f %7.3f-%-7.3f %s"
              % (k, full[k], thumb[k], lo, hi, mark))
    lo, hi = REF["colours"]
    inside = lo <= full["colours"] <= hi
    mark = "ok" if inside else ("low" if full["colours"] < lo else "high")
    if not inside:
        fails.append("colours %d outside %d-%d" % (full["colours"], lo, hi))
    print("%-12s %8d %8d %7d-%-7d %s"
          % ("colours", full["colours"], thumb["colours"], lo, hi, mark))

    if fails:
        print("\nOUTSIDE the winners' range: " + "; ".join(fails))
        return 1
    print("\ninside the range the winners of this competition occupy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
