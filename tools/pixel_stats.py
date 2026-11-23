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

BENCH = {
    "dark": 0.12,      # strongest entries: 0.065 - 0.18
    "light": 0.66,     # strongest entries: 0.56 - 0.72
    "saturated": 0.08,  # strongest entries: 0.019 - 0.10
    "colours": 150,    # strongest entries: 126 - 198
}


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

    print("%-12s %8s %8s %8s" % ("", "full", "300px", "benchmark"))
    print("-" * 40)
    for k in ("dark", "light", "saturated"):
        mark = "ok" if (full[k] <= BENCH[k] if k != "light" else full[k] >= BENCH[k]) else "OFF"
        print("%-12s %8.3f %8.3f %8.3f  %s" % (k, full[k], thumb[k], BENCH[k], mark))
    mark = "ok" if full["colours"] <= BENCH["colours"] else "OFF"
    print("%-12s %8d %8d %8d  %s" % ("colours", full["colours"], thumb["colours"], BENCH["colours"], mark))

    fails = []
    if full["dark"] > BENCH["dark"]:
        fails.append("dark %.3f > %.3f" % (full["dark"], BENCH["dark"]))
    if full["light"] < BENCH["light"]:
        fails.append("light %.3f < %.3f" % (full["light"], BENCH["light"]))
    if full["saturated"] > BENCH["saturated"]:
        fails.append("saturated %.3f > %.3f" % (full["saturated"], BENCH["saturated"]))
    if full["colours"] > BENCH["colours"]:
        fails.append("colours %d > %d" % (full["colours"], BENCH["colours"]))
    if fails:
        print("\nOFF BENCHMARK: " + "; ".join(fails))
        return 1
    print("\nall four measures inside the benchmark")
    return 0


if __name__ == "__main__":
    sys.exit(main())
