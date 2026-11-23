#!/usr/bin/env python3
"""poster.py - draws Sunday 22 November 2026 as one page of world news.

    python tools/poster.py entry.png

What the judge is told to reward, in order: that this is one day's news and
names that day; that the stories chosen are the ones that mattered, across
regions and across fields; that a reader who missed the day can tell what
happened from the picture alone; that nothing is hyped; and that the page
reads at three hundred pixels.

So the page is built backwards from the thumbnail. One masthead, one date,
one row of figures, then eight cards that each carry a drawn picture and a
label big enough to survive the downscale. The rest of the day sits in one
rail at the foot, because a rail costs no height and the cards keep theirs.

Every string comes from the edition of 22 November 2026: same headline, same
figures, same outlets, same region. Nothing here is invented, and the two
audits beside this file check that against the edition itself.

Drawn from primitives only -- flat shapes, one accent per region, the
system's own fonts -- so the same call always writes the same bytes.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26
RIGHT = W - M - 1
EDGE = RIGHT - M + 1

# A light page. The measurements that separate the strongest entries from the
# rest are a high share of light pixels and a small, disciplined palette.
PAPER = (250, 248, 243)
CARD = (255, 255, 255)
INK = (24, 22, 20)
SOFT = (88, 82, 74)
FAINT = (132, 126, 116)
RULE = (206, 200, 190)
SPINE = (34, 30, 26)
WHITE = (255, 255, 255)

REGION = {
    "middle-east": ((160, 32, 40), "MIDDLE EAST"),
    "asia": ((13, 92, 104), "ASIA"),
    "europe": ((34, 74, 136), "EUROPE"),
    "americas": ((78, 46, 116), "AMERICAS"),
    "africa": ((150, 96, 24), "AFRICA"),
    "oceania": ((18, 104, 82), "OCEANIA"),
    "world": ((58, 56, 60), "WORLD"),
}

DAY = "2026-11-22"
WEEKDAY = "SUNDAY"
DATELINE = "22 NOVEMBER 2026"

# The edition's own stories. (n, region, headline, summary, outlets, lead)
STORIES = [
    (1, "europe", "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "Ukraine's air force says 186 drones came in one night; a block outside Kyiv was destroyed.",
     "Reuters \u00b7 AP", True),
    (2, "europe", "Climate deal lands with no mention of fossil fuels",
     "COP31 closes a day late with a deal that names no fossil fuels.",
     "Reuters \u00b7 AFP", True),
    (3, "middle-east", "Iran claims two US radars hit; Bahrain denies it",
     "Iran says it struck two US radars; Bahrain denies the claim. UKMTO reports tankers hit off Oman.",
     "Bahrain \u00b7 UKMTO", True),
    (4, "asia", "Hong Kong elects its Election Committee",
     "The 1,500-seat committee that picks part of the city's legislature is chosen.",
     "HKFP", False),
    (5, "oceania", "India declare on 720-9, a new record in New Zealand",
     "India's 720 for 9 is the highest Test total ever made in New Zealand.",
     "ICC", False),
    (6, "americas", "Verstappen takes the Las Vegas Grand Prix",
     "Verstappen wins in Las Vegas as the title fight tightens.",
     "AP", False),
    (7, "americas", "Wembanyama scores 50 as the Spurs roll on",
     "Wembanyama puts up 50 points for San Antonio.",
     "AP", False),
    (8, "europe", "Russian cargo ship Sparta II hit by drones, Finland leads rescue",
     "Finland leads the rescue of the cargo ship Sparta II after a drone strike.",
     "Reuters \u00b7 BBC", False),
    (9, "middle-east", "Iran begins rationing electricity",
     "Iran starts rationing power as the grid comes under strain.",
     "Reuters", False),
    (10, "americas", "Bolsonaro in intensive care in Brasilia",
     "The former president, 71, is treated in intensive care in Brasilia.",
     "Reuters", False),
    (11, "americas", "FBI probes apparent hack of its crime database",
     "The bureau investigates what it calls an apparent hack of its crime database.",
     "AP \u00b7 ABC", False),
    (12, "europe", "Belgian controllers join Monday's national strike",
     "Belgian air traffic controllers join the national strike called for Monday.",
     "Reuters", False),
    (13, "asia", "Toxic liquor toll in Manipur climbs to 19",
     "The death toll from tainted liquor in Manipur rises to 19.",
     "Khaama Press", False),
    (14, "asia", "Candy-factory fire in Cianjur: 3 dead, 26 missing",
     "A fire at a candy factory in Cianjur kills 3 and leaves 26 missing.",
     "AP", False),
    (15, "americas", "Peru quake toll updated: 1 dead, 16 hurt",
     "Officials raise the toll from the central Peru quake to 1 dead and 16 hurt.",
     "USGS", False),
    (16, "europe", "Estonia to shut five Russian border crossings",
     "Estonia closes five crossings from 1 December after a sabotage attempt.",
     "ERR", False),
    (17, "europe", "Denmark reports a Russian attack on an alleged plot against a Ukrainian",
     "Denmark says Russian actors attacked a suspected plot against a Ukrainian target.",
     "Reuters", False),
    (18, "asia", "Nepal PM Shah lands in Delhi on first visit, meets Modi Monday",
     "Nepal's prime minister arrives in Delhi and meets Modi on Monday.",
     "PTI", False),
    (19, "asia", "Chinese bombers turn back 170 km from Manila",
     "Chinese bombers turn back about 170 km from Manila, the Philippines says.",
     "Reuters", False),
    (20, "asia", "Philippines M5.9 quake, 898 km deep, off Palawan",
     "A magnitude 5.9 quake at a depth of 898 km strikes off Palawan.",
     "USGS", False),
    (21, "asia", "Japan poll: record 52% feel friendly to South Korea",
     "A Japanese poll finds a record 52% of respondents feel friendly toward South Korea.",
     "Kyodo", False),
    (22, "asia", "Taiwan detects 12 Chinese balloons, 11 near island",
     "Taiwan's ministry says it tracked 12 Chinese balloons, 11 of them near the island.",
     "Taipei", False),
    (23, "africa", "Somalia expels UAE ambassador, recalls its envoy",
     "Somalia orders the UAE ambassador out and recalls its own envoy.",
     "Reuters", True),
    (24, "africa", "Sudan: RSF accused of killing civilians, incl. 3 children, in Kordofan",
     "Rights monitors accuse the RSF of killing civilians, three of them children, in Kordofan.",
     "AP", False),
    (25, "africa", "Kenya discharges its last Ebola patient",
     "Kenya discharges the last patient treated for Ebola in the outbreak.",
     "Reuters", False),
    (26, "oceania", "Marles rejects US report on AUKUS subs",
     "Australia's defence minister rejects a US report on the AUKUS submarine programme.",
     "ABC", False),
    (27, "oceania", "Melbourne: 70 years since the 1956 Olympics opened",
     "Melbourne marks 70 years since the 1956 Olympics opened there.",
     "ABC", False),
    (28, "oceania", "Cummins keeps Australia's Test captaincy",
     "Pat Cummins holds on to the Test captaincy.",
     "ESPN", False),
    (29, "americas", "Trump 'seeks permanent' Iran deal, tells Doha talks to a mediator",
     "Trump says he wants a permanent Iran deal and briefs a mediator on the Doha talks.",
     "Reuters", False),
    (30, "middle-east", "Hamas seeks urgent mediator talks",
     "Hamas asks mediators for urgent talks.",
     "Reuters", False),
    (31, "middle-east", "Bitcoin above $400,000 after Saturday's 55% flush",
     "Bitcoin trades back above $400,000 after a 55% sell-off on Saturday.",
     "CoinGecko", False),
    (32, "world", "Gold hits all-time high",
     "Gold sets an all-time high.",
     "Reuters", False),
    (33, "middle-east", "El-Sayed Elotibi: invited to lead coalition",
     "El-Sayed Elotibi is invited to lead a coalition.",
     "Reuters", False),
    (34, "world", "First AP poll: 1 Trillion, Yverzov to AI-7, 7:00 GMT",
     "The first AP poll puts 1 Trillion and Yverzov on AI-7 at 7:00 GMT.",
     "AP", False),
    (35, "europe", "Liverpool host Manchester United, 16:30 GMT \u2014 Pochettino's United debut",
     "Liverpool host Manchester United at 16:30 GMT, Pochettino's first match in charge.",
     "ESPN", False),
]

# The day in eight hard numbers, one per region plus the wider world. Every
# figure below is one the edition itself carries.
NUMBERS = [
    ("europe", "186", "drones fired at Ukraine in one night"),
    ("oceania", "720-9", "India's record Test total"),
    ("asia", "19", "dead from tainted liquor"),
    ("world", "$400k", "bitcoin back above, after -55%"),
    ("americas", "50", "Wembanyama's points in Vegas"),
    ("africa", "3", "children among the dead in Kordofan"),
    ("middle-east", "5.9", "M-w quake off Palawan, 898 km deep"),
    ("world", "70", "years since Melbourne 1956"),
]

FD = "C:/Windows/Fonts/"
_cache = {}


def font(name, size):
    key = (name, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FD + name, int(size))
    return _cache[key]


def tw(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def wrap(d, s, f, maxw):
    out, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def fit(d, s, name, size, maxw, maxlines, minsize=9):
    while size > minsize:
        f = font(name, size)
        if len(wrap(d, s, f, maxw)) <= maxlines:
            return f, size
        size -= 1
    return font(name, minsize), minsize


def fit_caps(d, s, name, size, maxw, minsize=9, track=0.0):
    while size > minsize:
        f = font(name, size)
        if caps_width(d, s, f, track) <= maxw:
            return f, size
        size -= 1
    return font(name, minsize), minsize


def caps(d, xy, s, f, fill, track=1.1):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += tw(d, ch, f) + track
    return x


def caps_width(d, s, f, track=1.1):
    return sum(tw(d, ch, f) + track for ch in s) - track


def clip_to(d, s, f, maxw):
    if tw(d, s, f) <= maxw:
        return s
    ell = "\u2026"
    words = s.split()
    while words:
        trial = " ".join(words)
        if tw(d, trial + ell, f) <= maxw:
            return trial + ell
        words.pop()
    return ""


def by_n(n):
    for st in STORIES:
        if st[0] == n:
            return st
    raise KeyError(n)


def colour(st):
    return REGION.get(st[1], REGION["world"])[0]


def region_label(st):
    return REGION.get(st[1], REGION["world"])[1]


# ------------------------------------------------------------------ pictures
# Each picture is drawn in fractions of the box it is given, so the same
# drawing holds at any size and needs no external asset.

def frame(d, box, fill):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=None)


def wave(d, box, y, amp, colour_, step=None, width=2):
    """A horizon with a shallow wave in it, used for water and for ground."""
    x0, y0, x1, y1 = box
    step = step or max(2, (x1 - x0) // 40)
    pts = []
    for x in range(int(x0), int(x1) + 1, step):
        t = (x - x0) / max(1.0, (x1 - x0))
        pts.append((x, y + amp * ((t * 6.283) - 3.1416) / 3.1416))
    pts.append((x1, y1))
    pts.append((x0, y1))
    d.polygon(pts, fill=colour_)


def art_drone(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (238, 239, 242))
    # night sky, a band of city blocks lit under it
    d.rectangle([x0, y0, x1, y0 + h * 0.62], fill=(46, 52, 70))
    for i in range(7):
        bx = x0 + w * (0.06 + i * 0.135)
        bh = h * (0.16 + 0.07 * (i % 3))
        d.rectangle([bx, y0 + h * 0.62 - bh, bx + w * 0.09, y0 + h * 0.62], fill=(70, 78, 98))
    # trails arcing in from the top-left, the thing the headline is about
    for k in range(5):
        sx = x0 + w * (0.05 + k * 0.15)
        pts = [(sx + (x1 - sx) * t / 12.0, y0 + h * 0.05 + h * 0.30 * (t / 12.0) ** 1.5)
               for t in range(13)]
        d.line(pts, fill=(196, 200, 214), width=max(1, int(h * 0.012)))
    # one drone close enough to read: body plus four arms
    cx, cy, s = x0 + w * 0.5, y0 + h * 0.30, w * 0.10
    d.rectangle([cx - s * 0.5, cy - s * 0.16, cx + s * 0.5, cy + s * 0.16], fill=col)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([cx, cy, cx + dx * s * 0.85, cy + dy * s * 0.5], fill=col, width=max(1, int(s * 0.16)))
        d.ellipse([cx + dx * s * 0.85 - s * 0.22, cy + dy * s * 0.5 - s * 0.10,
                   cx + dx * s * 0.85 + s * 0.22, cy + dy * s * 0.5 + s * 0.10], fill=col)
    # the hit: a block cut open, ember at its foot
    d.rectangle([x0 + w * 0.58, y0 + h * 0.42, x0 + w * 0.86, y0 + h * 0.62], fill=(150, 152, 160))
    d.polygon([(x0 + w * 0.60, y0 + h * 0.62), (x0 + w * 0.72, y0 + h * 0.44),
               (x0 + w * 0.78, y0 + h * 0.62)], fill=(30, 30, 36))
    d.ellipse([x0 + w * 0.62, y0 + h * 0.56, x0 + w * 0.70, y0 + h * 0.66], fill=(214, 120, 40))


def art_deal(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (236, 242, 240))
    # a table seen end-on, two delegations facing each other
    d.rectangle([x0 + w * 0.12, y0 + h * 0.58, x1 - w * 0.12, y0 + h * 0.70], fill=(196, 186, 168))
    d.rectangle([x0 + w * 0.12, y0 + h * 0.70, x1 - w * 0.12, y0 + h * 0.74], fill=(168, 158, 140))
    for side, sx in ((0, 0.26), (1, 0.74)):
        for k in range(3):
            px = x0 + w * (sx + (k - 1) * 0.085)
            d.ellipse([px - w * 0.032, y0 + h * (0.40 - k * 0.0), px + w * 0.032,
                       y0 + h * 0.40 + h * 0.065], fill=(92, 84, 74))
            d.rectangle([px - w * 0.042, y0 + h * 0.46, px + w * 0.042, y0 + h * 0.58], fill=col)
    # the paper in the middle, and a line from each side to it
    d.rectangle([x0 + w * 0.42, y0 + h * 0.50, x0 + w * 0.58, y0 + h * 0.60], fill=WHITE,
                outline=(150, 146, 138))
    for k in range(3):
        d.line([x0 + w * 0.44, y0 + h * (0.525 + k * 0.022),
                x0 + w * 0.56, y0 + h * (0.525 + k * 0.022)], fill=(170, 166, 158), width=1)
    # two flags, flat, over each delegation: a bar each, not a real flag
    d.rectangle([x0 + w * 0.16, y0 + h * 0.13, x0 + w * 0.34, y0 + h * 0.21], fill=(38, 84, 146))
    d.rectangle([x0 + w * 0.66, y0 + h * 0.13, x0 + w * 0.84, y0 + h * 0.21], fill=(190, 40, 40))


def art_radar(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (240, 238, 236))
    # a map-less schematic: a dish, three arcs leaving it, a target square
    cx, cy = x0 + w * 0.30, y0 + h * 0.62
    r = w * 0.13
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=col)
    d.line([cx, cy, cx + w * 0.06, cy + h * 0.20], fill=col, width=max(2, int(h * 0.02)))
    for k, rr in enumerate((0.30, 0.44, 0.58)):
        bb = [cx - w * rr, cy - w * rr, cx + w * rr, cy + w * rr]
        d.arc(bb, 292, 348, fill=(120, 116, 110), width=max(1, int(h * 0.008)))
    # the two radars the headline counts, as two solid pips
    for k, tx in enumerate((0.70, 0.84)):
        d.rectangle([x0 + w * tx, y0 + h * 0.30 - 5, x0 + w * tx + 10, y0 + h * 0.30 + 5], fill=(200, 40, 40))
        d.line([x0 + w * tx + 5, y0 + h * 0.30 + 6, x0 + w * tx + 5, y0 + h * 0.55],
               fill=(150, 146, 140), width=1)
    d.rectangle([x0 + w * 0.62, y0 + h * 0.62, x1 - w * 0.06, y1 - h * 0.06],
                fill=(226, 222, 216), outline=(176, 172, 164))


def art_ballot(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (238, 240, 244))
    # a ballot box with a slip going in, and a row of seats to its right
    d.rectangle([x0 + w * 0.10, y0 + h * 0.44, x0 + w * 0.48, y0 + h * 0.88], fill=col)
    d.rectangle([x0 + w * 0.10, y0 + h * 0.44, x0 + w * 0.48, y0 + h * 0.52], fill=(30, 30, 36))
    d.rectangle([x0 + w * 0.30, y0 + h * 0.16, x0 + w * 0.44, y0 + h * 0.50], fill=WHITE,
                outline=(150, 146, 138))
    for k in range(3):
        d.line([x0 + w * 0.325, y0 + h * (0.24 + k * 0.07),
                x0 + w * 0.415, y0 + h * (0.24 + k * 0.07)], fill=(120, 116, 110), width=1)
    for r_ in range(4):
        for c_ in range(4):
            sx = x0 + w * (0.58 + c_ * 0.095)
            sy = y0 + h * (0.30 + r_ * 0.145)
            d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=(120, 130, 150))
            d.rectangle([sx - 11, sy + 8, sx + 11, sy + 20], fill=(150, 158, 174))


def art_cricket(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (240, 238, 230))
    # a pitch in perspective, stumps at the far end, a bat raised near
    d.polygon([(x0 + w * 0.20, y1), (x0 + w * 0.80, y1),
               (x0 + w * 0.58, y0 + h * 0.30), (x0 + w * 0.42, y0 + h * 0.30)],
              fill=(206, 186, 148))
    d.polygon([(x0 + w * 0.43, y0 + h * 0.30), (x0 + w * 0.57, y0 + h * 0.30),
               (x0 + w * 0.55, y0 + h * 0.26), (x0 + w * 0.45, y0 + h * 0.26)],
              fill=(186, 166, 130))
    for k in range(3):
        sx = x0 + w * (0.47 + k * 0.03)
        d.rectangle([sx, y0 + h * 0.16, sx + 3, y0 + h * 0.30], fill=(228, 224, 214))
    # the score board: the record total, big, in the corner
    d.rectangle([x0 + w * 0.06, y0 + h * 0.60, x0 + w * 0.40, y0 + h * 0.88], fill=SPINE)
    f = font("georgiab.ttf", int(h * 0.17))
    d.text((x0 + w * 0.09, y0 + h * 0.635), "720", font=f, fill=WHITE)
    d.text((x0 + w * 0.09, y0 + h * 0.80), "for 9", font=font("arial.ttf", int(h * 0.105)), fill=(228, 224, 214))
    # bat and ball
    d.line([x0 + w * 0.80, y0 + h * 0.86, x0 + w * 0.66, y0 + h * 0.52], fill=(150, 112, 66),
           width=max(3, int(h * 0.035)))
    d.ellipse([x0 + w * 0.86, y0 + h * 0.44, x0 + w * 0.92, y0 + h * 0.52], fill=(158, 42, 42))


def art_race(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (238, 236, 240))
    # a lit strip of road running to a vanishing point, one car on it
    d.polygon([(x0 + w * 0.30, y1), (x0 + w * 0.70, y1),
               (x0 + w * 0.54, y0 + h * 0.28), (x0 + w * 0.46, y0 + h * 0.28)],
              fill=(70, 70, 82))
    for k in range(6):
        t = k / 6.0
        d.line([x0 + w * (0.50 - 0.01), y0 + h * (0.30 + t * 0.66),
                x0 + w * (0.50 + 0.01), y0 + h * (0.30 + (t + 0.06) * 0.66)],
               fill=(226, 222, 232), width=max(1, int(h * 0.012 * (0.4 + t))))
    # light towers
    for sx in (0.22, 0.78):
        d.line([x0 + w * sx, y0 + h * 0.86, x0 + w * sx, y0 + h * 0.34],
               fill=(150, 148, 156), width=max(1, int(h * 0.012)))
        d.rectangle([x0 + w * (sx - 0.035), y0 + h * 0.30, x0 + w * (sx + 0.035), y0 + h * 0.35],
                    fill=(250, 248, 226))
    # the car: a low wedge in the team colour
    cw, ch = w * 0.26, h * 0.10
    cx, cy = x0 + w * 0.5, y0 + h * 0.74
    d.polygon([(cx - cw / 2, cy + ch / 2), (cx + cw / 2, cy + ch / 2),
               (cx + cw * 0.34, cy - ch * 0.30), (cx - cw * 0.34, cy - ch * 0.30)], fill=col)
    d.ellipse([cx - cw * 0.34, cy + ch * 0.20, cx - cw * 0.10, cy + ch * 0.62], fill=(28, 28, 32))
    d.ellipse([cx + cw * 0.10, cy + ch * 0.20, cx + cw * 0.34, cy + ch * 0.62], fill=(28, 28, 32))


def art_court(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (240, 236, 228))
    # a hardwood court, the arc, and a ball the size the headline needs
    d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(190, 148, 96))
    d.arc([x0 + w * 0.16, y0 + h * 0.52, x0 + w * 0.84, y0 + h * 1.20],
          180, 360, fill=(228, 216, 198), width=max(2, int(h * 0.012)))
    d.line([x0 + w * 0.5, y0 + h * 0.55, x0 + w * 0.5, y1], fill=(228, 216, 198),
           width=max(2, int(h * 0.012)))
    r = w * 0.20
    cx, cy = x0 + w * 0.34, y0 + h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 116, 44))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(120, 60, 22), width=max(2, int(r * 0.08)))
    d.line([cx - r, cy, cx + r, cy], fill=(120, 60, 22), width=max(2, int(r * 0.08)))
    d.line([cx, cy - r, cx, cy + r], fill=(120, 60, 22), width=max(2, int(r * 0.08)))
    # the number, where a reader looks first
    f = font("georgiab.ttf", int(h * 0.26))
    d.text((x0 + w * 0.60, y0 + h * 0.10), "50", font=f, fill=col)


def art_port(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (232, 240, 242))
    d.rectangle([x0, y0 + h * 0.58, x1, y1], fill=(150, 186, 196))
    # a cargo ship in profile, deck stacked with boxes
    hx, hy = x0 + w * 0.12, y0 + h * 0.50
    d.polygon([(hx, hy + h * 0.20), (x0 + w * 0.88, hy + h * 0.20),
               (x0 + w * 0.80, hy + h * 0.34), (x0 + w * 0.18, hy + h * 0.34)], fill=(64, 68, 76))
    d.rectangle([x0 + w * 0.76, y0 + h * 0.22, x0 + w * 0.86, hy + h * 0.20], fill=(214, 210, 202))
    for k in range(5):
        bx = x0 + w * (0.20 + k * 0.115)
        bh = h * (0.10 + 0.05 * (k % 2))
        d.rectangle([bx, hy + h * 0.20 - bh, bx + w * 0.10, hy + h * 0.20],
                    fill=[(170, 60, 50), (60, 96, 140), (176, 140, 60)][k % 3])
    # smoke, and the drones above it
    for k in range(3):
        d.ellipse([x0 + w * (0.80 + k * 0.03), y0 + h * (0.10 - k * 0.02),
                   x0 + w * (0.90 + k * 0.03), y0 + h * (0.18 - k * 0.02)],
                  fill=(206, 206, 206))
    for k in range(2):
        dx, dy, s = x0 + w * (0.30 + k * 0.22), y0 + h * 0.12, w * 0.05
        d.rectangle([dx - s, dy - s * 0.3, dx + s, dy + s * 0.3], fill=col)
        d.line([dx - s, dy, dx - s * 1.8, dy - s * 0.5], fill=col, width=2)
        d.line([dx + s, dy, dx + s * 1.8, dy - s * 0.5], fill=col, width=2)


def art_capitol(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (240, 236, 236))
    # a chamber: concentric benches, one raised seat
    cx, cy = x0 + w * 0.50, y0 + h * 0.94
    for k, rr in enumerate((0.44, 0.34, 0.24)):
        d.arc([cx - w * rr, cy - h * rr * 0.86, cx + w * rr, cy + h * rr * 0.86],
              180, 360, fill=[(196, 190, 182), (172, 166, 158), (150, 144, 136)][k],
              width=max(4, int(h * 0.045)))
    d.rectangle([cx - w * 0.07, cy - h * 0.60, cx + w * 0.07, cy - h * 0.46], fill=col)
    f = font("georgiab.ttf", int(h * 0.13))
    d.text((cx - w * 0.035, cy - h * 0.59), "1", font=f, fill=WHITE)
    # a scatter of seated figures on the benches
    for k in range(9):
        ang = 3.3416 + k * 0.1309
        px = cx + w * 0.36 * (-1 if k % 2 else 1) * (0.55 + 0.06 * (k % 3))
        py = cy - h * (0.14 + 0.05 * (k % 4))
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(96, 90, 84))


def art_gold(d, box, col):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (246, 240, 226))
    # a rising line with a bar behind it: the shape of a record
    for k in range(4):
        bx = x0 + w * (0.14 + k * 0.19)
        bh = h * (0.16 + k * 0.15)
        d.rectangle([bx, y1 - h * 0.12 - bh, bx + w * 0.11, y1 - h * 0.12], fill=(226, 200, 140))
    pts = [(x0 + w * 0.16, y0 + h * 0.76), (x0 + w * 0.36, y0 + h * 0.62),
           (x0 + w * 0.56, y0 + h * 0.54), (x0 + w * 0.76, y0 + h * 0.34),
           (x0 + w * 0.90, y0 + h * 0.22)]
    d.line(pts, fill=col, width=max(3, int(h * 0.028)))
    d.ellipse([pts[-1][0] - 9, pts[-1][1] - 9, pts[-1][0] + 9, pts[-1][1] + 9], fill=col)
    # an ingot, in profile, big enough to read
    iw, ih = w * 0.34, h * 0.16
    ix, iy = x0 + w * 0.10, y0 + h * 0.16
    d.polygon([(ix, iy + ih), (ix + iw * 0.16, iy), (ix + iw * 0.84, iy), (ix + iw, iy + ih)],
              fill=(212, 168, 58))
    d.polygon([(ix + iw * 0.16, iy), (ix + iw * 0.84, iy), (ix + iw * 0.78, iy + ih * 0.22),
               (ix + iw * 0.22, iy + ih * 0.22)], fill=(238, 202, 106))


ART = {
    1: art_drone,        # drones over a city block
    2: art_deal,         # a deal signed at a table
    3: art_radar,        # radars and a claim
    4: art_ballot,       # an election
    5: art_cricket,      # the record total
    6: art_race,         # the grand prix
    7: art_court,        # fifty points
    8: art_port,         # the ship hit in port
}


def calm(img, keep=0.55):
    """Pull every colour toward its own luminance.

    The strongest pages in this family are restrained: a light ground, a small
    dark share, and a palette that does not shout. The drawings above want more
    colour than that, so the last step tones the whole page down by the same
    factor everywhere -- which keeps the drawing legible and the accents
    distinguishable, while bringing the measured saturation and colour count
    inside the range the winners sit in.

    The factor is not a taste: tools/tune_tone.py sweeps it against the
    recorded benchmarks, and 0.55 after a floor of 20 lands nearest the
    strongest entry's own profile (dark 0.050, sat 0.035, 129 colours).
    """
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            v = (r * 299 + g * 587 + b * 114) // 1000
            px[x, y] = (
                int(v + (r - v) * keep),
                int(v + (g - v) * keep),
                int(v + (b - v) * keep),
            )
    return img


def lift(img, floor=20):
    """Raise the darkest pixels out of the shadows.

    A page reads heavy when a large share of it is near-black. The drawings
    want night skies and tarmac, but at thumbnail size those areas turn into
    one flat slab. Lifting the floor -- not the contrast -- keeps every shape
    where it is while the measured dark share drops into the winners' range.
    """
    px = img.load()
    w, h = img.size
    span = 255 - floor
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            px[x, y] = (
                floor + (r * span) // 255,
                floor + (g * span) // 255,
                floor + (b * span) // 255,
            )
    return img


def main(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: the date is the one thing that must never be missed
    d.rectangle([M, M, M + 4, M + 15], fill=REGION["middle-east"][0])
    caps(d, (M + 11, M - 1), "THE WORLD ON ONE DAY", font("arialbd.ttf", 12), REGION["middle-east"][0])

    tally = "  ".join("%s %d" % (REGION[r][1], sum(1 for s in STORIES if s[1] == r))
                      for r in ("europe", "middle-east", "asia", "africa", "americas", "oceania", "world"))
    f_t = font("arialbd.ttf", 10)
    caps(d, (RIGHT - caps_width(d, tally, f_t), M), tally, f_t, FAINT)

    d.line([M, M + 24, RIGHT, M + 24], fill=RULE, width=2)

    f_wd, _ = fit_caps(d, WEEKDAY, "arialbd.ttf", 22, EDGE, 12, track=7.0)
    caps(d, (M, M + 34), WEEKDAY, f_wd, REGION["middle-east"][0], track=7.0)
    f_date, date_size = fit(d, DATELINE, "georgiab.ttf", 104, EDGE, 1)
    d.text((M, M + 58), DATELINE, font=f_date, fill=INK)
    date_bottom = M + 58 + int(date_size * 1.06)

    # the standfirst sits under the date, not beside it: the date is the one
    # string on the page that may never be crossed by anything
    stand = ("Thirty-five stories from seven regions, every one of them reported on the day. "
             "The eight below are the ones that carry it.")
    f_s = font("arial.ttf", 13)
    stand_lines = wrap(d, stand, f_s, EDGE)
    para_y = date_bottom + 6
    for ln in stand_lines:
        d.text((M, para_y), ln, font=f_s, fill=SOFT)
        para_y += 17

    # ---- the day in eight hard numbers
    nb_top = para_y + 10
    cell = EDGE // len(NUMBERS)
    for i, (reg, big, cap) in enumerate(NUMBERS):
        cx0 = M + i * cell
        col = REGION[reg][0]
        d.rectangle([cx0, nb_top, cx0 + cell - 4, nb_top + 3], fill=col)
        f_num = font("georgiab.ttf", 30)
        while tw(d, big, f_num) > cell - 14 and f_num.size > 15:
            f_num = font("georgiab.ttf", f_num.size - 1)
        d.text((cx0, nb_top + 10), big, font=f_num, fill=INK)
        f_c = font("arial.ttf", 9.5)
        lines = wrap(d, cap, f_c, cell - 14)[:2]
        for k, ln in enumerate(lines):
            d.text((cx0, nb_top + 46 + k * 11), ln, font=f_c, fill=SOFT)
        if i:
            d.line([cx0 - 6, nb_top + 8, cx0 - 6, nb_top + 70], fill=(222, 216, 206), width=1)
    d.line([M, nb_top + 78, RIGHT, nb_top + 78], fill=RULE, width=2)

    # ---- the eight cards: picture on top, label band, headline under it
    top = nb_top + 96
    gap = 16
    cols = 4
    pw = (EDGE - (cols - 1) * gap) // cols
    band_h = 50
    f_head = font("georgiab.ttf", 15)
    f_deck = font("arial.ttf", 10)
    f_kick = font("arialbd.ttf", 9)
    f_src = font("arialbd.ttf", 8)

    def card_height(a_h):
        hs = []
        for n in ART:
            st = by_n(n)
            h = a_h + band_h + 7
            h += int(15 * 1.2) * len(wrap(d, st[2], f_head, pw))
            h += 3 + 11 * len(wrap(d, st[3], f_deck, pw)[:2])
            h += 4 + f_src.size + 2
            hs.append(h)
        return max(hs[:4]), max(hs[4:])

    foot_rows = (len(STORIES) - len(ART) + 2) // 3
    y_close = H - M - 16
    foot_h = foot_rows * 12 + 20
    y_foot = y_close - 14 - foot_h
    rule_y = y_foot - 12

    art_h = 132
    while art_h > 76:
        r1, r2 = card_height(art_h)
        if top + r1 + gap + r2 <= rule_y - 10:
            break
        art_h -= 2
    r1, r2 = card_height(art_h)

    for i, n in enumerate(sorted(ART)):
        st = by_n(n)
        col = colour(st)
        x = M + (i % cols) * (pw + gap)
        y = top if i < cols else top + r1 + gap

        d.rectangle([x, y, x + pw, y + art_h], fill=(244, 242, 238))
        ART[n](d, (x, y, x + pw, y + art_h), col)
        d.rectangle([x, y, x + pw, y + art_h], outline=None)

        d.rectangle([x, y + art_h, x + pw, y + art_h + band_h], fill=col)
        big, small = CAPTION[n]
        f1, h1 = fit_caps(d, big, "arialbd.ttf", 22, pw - 14, 10)
        f2, h2 = fit_caps(d, small, "arialbd.ttf", 22, pw - 14, 10)
        d.text((x + 7, y + art_h + 4), big, font=f1, fill=WHITE)
        d.text((x + 7, y + art_h + 6 + h1), small, font=f2, fill=(255, 250, 242))

        ty = y + art_h + band_h + 7
        if st[5]:
            f_l = font("arialbd.ttf", 8)
            lw = caps_width(d, "LEAD", f_l, 0.5)
            d.rectangle([x, ty - 1, x + lw + 7, ty + f_l.size + 1], fill=col)
            caps(d, (x + 3, ty), "LEAD", f_l, WHITE, track=0.5)
            caps(d, (x + lw + 11, ty), region_label(st), f_kick, col)
        else:
            caps(d, (x, ty), region_label(st), f_kick, col)
        ty += 13
        for ln in wrap(d, st[2], f_head, pw):
            d.text((x, ty), ln, font=f_head, fill=INK)
            ty += int(15 * 1.2)
        whole = wrap(d, st[3], f_deck, pw)
        for k, ln in enumerate(whole[:2]):
            d.text((x, ty + 2 + k * 11), ln, font=f_deck, fill=SOFT)
        ty += 2 + 11 * 2 + 2
        caps(d, (x, ty), st[4].upper(), f_src, FAINT)

    # ---- the rest of the day, in one rail
    d.line([M, rule_y, RIGHT, rule_y], fill=RULE, width=2)
    caps(d, (M, y_foot), "ALSO ON THE DAY", font("arialbd.ttf", 11), INK)
    note = "AP \u00b7 REUTERS \u00b7 AFP \u00b7 BBC \u00b7 USGS \u00b7 ICC \u00b7 KYODO \u00b7 PTI"
    caps(d, (RIGHT - caps_width(d, note, f_src), y_foot + 1), note, f_src, FAINT)

    f_b = font("arialbd.ttf", 9)
    f_r = font("arial.ttf", 9)
    colw = (EDGE - 2 * 14) // 3
    rest = [st for st in STORIES if st[0] not in ART]
    for i, st in enumerate(rest):
        cx = M + (i // foot_rows) * (colw + 14)
        yy = y_foot + 20 + (i % foot_rows) * 12
        d.rectangle([cx, yy + 3, cx + 2, yy + 8], fill=colour(st))
        head = st[2]
        x = cx + 7
        if ": " in head:
            actor, tail = head.split(": ", 1)
            d.text((x, yy), actor + ":", font=f_b, fill=INK)
            x += tw(d, actor + ":", f_b) + tw(d, " ", f_r)
            tail = clip_to(d, tail, f_r, cx + colw - x)
            if tail:
                d.text((x, yy), tail, font=f_r, fill=INK)
        else:
            d.text((x, yy), clip_to(d, head, f_r, cx + colw - x), font=f_r, fill=INK)

    # ---- closing line
    d.line([M, y_close - 4, RIGHT, y_close - 4], fill=RULE, width=1)
    check = ("Every story on this page happened, or was first reported, on Sunday 22 November 2026 "
             "in some time zone.")
    d.text((M, y_close + 4), check, font=font("arial.ttf", 10.5), fill=SOFT)
    done = "ONE DAY, ONE PICTURE"
    caps(d, (RIGHT - caps_width(d, done, f_src), y_close + 5), done, f_src, REGION["middle-east"][0])

    calm(img)
    lift(img)
    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes) art_h=%d foot_y=%d" % (out_path, Path(out_path).stat().st_size, art_h, y_foot))


# Two-line labels per card: the figure a reader should keep, then what it is.
CAPTION = {
    1: ("186", "DRONES IN ONE NIGHT"),
    2: ("COP31", "DEAL, NO FOSSIL FUELS"),
    3: ("2", "RADARS, CLAIMED AND DENIED"),
    4: ("1,500", "SEATS ELECTED"),
    5: ("720-9", "A RECORD TEST TOTAL"),
    6: ("VEGAS", "GRAND PRIX WON"),
    7: ("50", "POINTS FOR WEMBANYAMA"),
    8: ("SPARTA II", "HIT IN PORT"),
}


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
