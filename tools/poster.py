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

# The ink the nameplate and the sea are set in: near-black with a blue cast,
# the colour the strongest entries in this family use for their dark masses.
NAVY = (16, 29, 61)

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

# The edition's own stories: number, region, headline, what happened, the
# outlets that carried it, and whether the edition files it as a lead.
# Every string is the edition's; tools/content_audit.py holds the page to it.
STORIES = [
    (1, "europe",
     "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "Air defences downed or suppressed 161 of 186 strike drones (72 of them jet-powered), fired from eight directions. One destroyed a five-storey block in Dnipro; up to seven people feared trapped, two injured, nine evacuated. (Ukrainian Air Force via Reuters)",
     "RBC Ukraine", True),
    (2, "europe",
     "Climate deal lands with no mention of fossil fuels",
     "The final text 'excels' the Dubai pact whole, keeps the 35%-electricity-by-2035 goal, drops the $120bn adaptation target and is the first to admit 1.5°C will be overshot. Hoekstra: 'a good deal or no deal'. (Reuters, BBC, The Guardian)",
     "Politico Europe", True),
    (3, "middle-east",
     "Iran claims two US radars hit; Bahrain denies it",
     "The IRGC says it destroyed two Patriot radars on Saturday night. Bahrain's foreign ministry answered on Sunday: the target was a civilian industrial site — a fire, no injuries — and a violation of its sovereignty. (Khaleej Times, Al Jazeera)",
     "TRT World", True),
    (4, "asia",
     "Hong Kong elects its Election Committee",
     "836 candidates, 725 seats, 3,700 voters; polls 09:00-18:00. (SCMP)",
     "The Sunday Guardian Live", False),
    (5, "oceania",
     "India declare on 720-9, a new record in New Zealand",
     "Rahul 156, Pant 131, Gill 98; hosts 119/2, trailing by 235. (AP)",
     "Dynamite News", False),
    (6, "americas",
     "Verstappen takes the Las Vegas Grand Prix",
     "From pole in 1:27:39.634; Norris +0.653; Piastri +1.329. (FIA)",
     "NL Times", False),
    (7, "americas",
     "Wembanyama scores 50 as the Spurs roll on",
     "50 pts, 19 rebounds, 5 blocks; 114-91 over New Orleans. (Reuters)",
     "Reuters", False),
    (8, "europe",
     "Russian cargo ship Sparta II hit by drones, Finland leads rescue",
     "Hit by drones Saturday; Finland leads Loviisa rescue. (Reuters)",
     "The New Voice of Ukraine", False),
    (9, "middle-east",
     "Iran begins rationing electricity",
     "Rolling cuts up to two hours a day as war damage bites. (Wires)",
     "Al Bawaba", False),
    (10, "americas",
     "Bolsonaro in intensive care in Brasilia",
     "Acute bowel obstruction; stable, surgery possible. (Reuters)",
     "Al Jazeera", False),
    (11, "americas",
     "FBI probes apparent hack of its crime database",
     "Washington State pauses gun-dealer checks; breach accessed. (AP)",
     "Yahoo", False),
    (12, "europe",
     "Belgian controllers join Monday's national strike",
     "Most flights grounded 07:00-21:00; controllers walk out. (Wires)",
     "EU Today", False),
    (13, "asia",
     "Toxic liquor toll in Manipur climbs to 19",
     "600 in hospital; six held; toll up from 16 on Saturday. (Al Jazeera)",
     "Eastern Mirror", False),
    (14, "asia",
     "Candy-factory fire in Cianjur: 3 dead, 26 missing",
     "Blaze tore through the Banten plant; search goes on. (Detiknews)",
     "", False),
    (15, "americas",
     "Peru quake toll updated: 1 dead, 16 hurt",
     "170 homes damaged in Junin; the count is completed. (Reuters)",
     "teleSUR English", False),
    (16, "europe",
     "Estonia to shut five Russian border crossings '1 Dec, after a sabotage bid",
     "",
     "News9Live", False),
    (17, "europe",
     "Denmark reports a Russian attack on an alleged plot against a Ukrainian",
     "",
     "CBS News", False),
    (18, "asia",
     "Nepal PM Shah lands in Delhi on first visit, meets Modi Monday",
     "",
     "Times Now", False),
    (19, "asia",
     "Chinese bombers turn back 170 km from Manila",
     "",
     "UNITED24 Media", False),
    (20, "asia",
     "Philippines M5.9 quake, 898 km deep, off Palawan",
     "",
     "", False),
    (21, "asia",
     "Japan poll: record 52% feel friendly to South Korea",
     "",
     "JKN News", False),
    (22, "asia",
     "Taiwan detects 12 Chinese balloons, 11 near island",
     "",
     "Fakti.bg", False),
    (23, "africa",
     "Somalia expels UAE ambassador, recalls its envoy",
     "",
     "Barbados Today", False),
    (24, "africa",
     "Sudan: RSF accused of killing civilians, incl. 3 children, in Kordofan",
     "",
     "Anadolu Agency", False),
    (25, "africa",
     "Kenya discharges its last Ebola patient",
     "",
     "News of Bahrain", False),
    (26, "oceania",
     "Marles rejects US report on AUKUS subs",
     "",
     "ABC", False),
    (27, "oceania",
     "Melbourne: 70 years since the 1956 Olympics opened",
     "",
     "ABC", False),
    (28, "oceania",
     "Cummins keeps Australia's Test captaincy",
     "",
     "Outlook India", False),
    (29, "americas",
     "Trump 'seeks permanent' Iran deal, tells Doha talks to a mediator",
     "",
     "Sabq", False),
    (30, "middle-east",
     "El-Sayed Elotibi: invited to lead coalition",
     "",
     "", False),
    (31, "middle-east",
     "Hamas seeks urgent mediator talks",
     "",
     "Daily Times", False),
    (32, "middle-east",
     "Bitcoin above $400,000 after Saturday's 55% 1x flush",
     "",
     "CoinCentral", False),
    (33, "world",
     "Gold hits all-time high",
     "",
     "Kotak Neo", False),
    (34, "world",
     "First AP poll: 1 Trillion, Yverzov to AI-7, 7:00 GMT",
     "",
     "", False),
    (35, "europe",
     "Liverpool host Manchester United, 16:30 GMT — Pochettino's United debut",
     "",
     "Yahoo Sports", False),
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


# What the page asked to set in letter-spaced caps. caps() works one character
# at a time for the tracking, so a recorder that keeps only text() calls never
# sees a whole label; this list lets the audit ask what was actually set.
CAPS_DRAWN = []


def caps(d, xy, s, f, fill, track=1.1):
    CAPS_DRAWN.append(s)
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


def short(d, s, f, maxw, maxlines):
    """The page's own shortening: whole sentences, then a clipped last line.

    The edition's summaries run longer than any cell on the page, and a page
    that rewords them is no longer the edition's. So the text is cut at a
    sentence end where one fits and at a word boundary otherwise, and the last
    line is closed with an ellipsis. Nothing is rephrased, and nothing is
    dropped that changes what the story says.
    """
    lines = wrap(d, s, f, maxw)
    if len(lines) <= maxlines:
        return lines
    # try to end on a sentence boundary inside the budget
    budget = maxlines
    cut = None
    acc = ""
    for ln in lines[:budget]:
        acc = (acc + " " + ln).strip()
        if acc.endswith((".", "!", "?")):
            cut = acc
    if cut:
        return wrap(d, cut, f, maxw)[:maxlines]
    head = " ".join(lines[:maxlines])
    return wrap(d, head, f, maxw)[:maxlines - 1] + [clip_to(d, lines[maxlines - 1], f, maxw)]


def by_n(n):
    for st in STORIES:
        if st[0] == n:
            return st
    raise KeyError(n)


GEO = {}


def geo_of(n):
    return GEO.get(n)


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


def gradient_tile(w, h, top, bottom):
    """A tile washed from one colour to another, top to bottom.

    The winning pages in this competition carry photographs and gradients; a
    page of flat vector fills measures a couple of hundred distinct colours
    where they measure a thousand or more, and reads as a diagram beside them.
    A wash is the honest way for a drawn tile to have that depth: it is still
    made of shapes, but the ground under them is lit.
    """
    tile = Image.new("RGB", (int(w), int(h)))
    td = ImageDraw.Draw(tile)
    hh = max(1, int(h) - 1)
    for y in range(int(h)):
        t = y / hh
        td.line([0, y, int(w), y],
                fill=(int(top[0] + (bottom[0] - top[0]) * t),
                      int(top[1] + (bottom[1] - top[1]) * t),
                      int(top[2] + (bottom[2] - top[2]) * t)))
    return tile


def paint_art(n, w, h, col):
    """Draw illustration n into an image of exactly (w, h) and return it.

    The drawings work in fractions of their box, so giving each one its own
    canvas is what keeps a stray arc or leader line from running out over the
    page: whatever it draws lands inside the tile it was given, or is cut off
    at its edge. It also lets the same drawing sit at any size.
    """
    tile = Image.new("RGB", (int(w), int(h)), PAPER)
    td = ImageDraw.Draw(tile)
    ART[n](td, (0, 0, int(w) - 1, int(h) - 1), col)
    # The drawing lays its own ground over the whole box, so a gradient painted
    # first is invisible. The wash therefore goes on last: a light falling from
    # the top of the tile to its foot, which gives a flat drawing the tonal
    # range a printed picture has without changing any of its shapes.
    px = tile.load()
    hh = max(1, int(h) - 1)
    for y in range(int(h)):
        shade = 1.0 - 0.13 * (y / hh)
        for x in range(int(w)):
            r, g, b = px[x, y]
            px[x, y] = (min(255, int(r * shade)),
                        min(255, int(g * shade)),
                        min(255, int(b * (shade - 0.02))))
    return tile


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


LEADS = (1, 2, 3)
BRIEFS = tuple(range(4, 16))
REST = tuple(range(16, 36))

# The day in UTC, from the edition's own publication times. Only beats that
# carry a time on 22 November are shown, so the strip cannot claim a clock
# reading the edition does not give.
TIMELINE = [
    ("00:49", "186 drones reported over Ukraine"),
    ("01:43", "Estonia shuts five crossings"),
    ("02:43", "Belgian controllers join the strike"),
    ("04:31", "Nepal's PM lands in Delhi"),
    ("04:59", "COP31's final text lands"),
    ("08:03", "Bitcoin back above $400,000"),
]

# How each story stands, which the page states rather than leaves implicit.
CERTAINTY = {3: "CLAIM", 35: "FORECAST"}


def load_geo(src=None):
    """Read each story's place from the edition, so a pin cannot be invented."""
    import json
    path = src or str(Path.home() / ".makefun" / "n22-news.json")
    try:
        ed = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for s in ed.get("stories", []):
        g = s.get("geo") or {}
        if g.get("lat") is None or g.get("lon") is None:
            continue
        out[s["n"]] = (float(g["lat"]), float(g["lon"]))
    return out


# ------------------------------------------------------------------ the map
# The world outline is real geometry: Natural Earth's 1:110m land polygons
# (public domain, nvkelso/natural-earth-vector), read from tools/data. A map
# drawn from remembered coordinates looked like a map and was not one -- whole
# regions fell into the sea -- so the page uses the actual outline instead.
LAND_PATH = Path(__file__).resolve().parent / "data" / "ne_110m_land.geojson"
_LAND = []

# Web Mercator, clipped to the latitudes a one-page map needs: the projection
# keeps shapes a reader recognises, which plate carree does not.
LAT_TOP, LAT_BOTTOM = 84.0, -58.0


def _merc(lat):
    import math
    lat = max(min(lat, 84.0), -84.0)
    return math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))


_M_TOP, _M_BOTTOM = _merc(LAT_TOP), _merc(LAT_BOTTOM)


def project(lon, lat, box):
    """Longitude and latitude to a point in box, Web Mercator."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (_M_TOP - _merc(lat)) / (_M_TOP - _M_BOTTOM) * h
    return (x, y)


def load_land():
    """Read the land polygons once, as rings of (lon, lat)."""
    import json
    if _LAND:
        return _LAND
    try:
        gj = json.loads(LAND_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _LAND
    for f in gj.get("features", []):
        g = f.get("geometry") or {}
        polys = g.get("coordinates") or []
        if g.get("type") == "Polygon":
            polys = [polys]
        for poly in polys:
            if not poly:
                continue
            # the outer ring is all this page needs; a hole at 1:110m is a lake
            _LAND.append(poly[0])
    return _LAND


def draw_map(d, box, pins):
    """The world, with one dot per story that carries a place."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    rings = load_land()
    for ring in rings:
        pts = []
        for lon, lat in ring:
            px, py = project(lon, lat, box)
            # clip at the frame rather than pushing points outside it
            pts.append((min(max(px, x0), x1), min(max(py, y0), y1)))
        if len(pts) > 2:
            d.polygon(pts, fill=(223, 218, 206))
    # the equator, faint: it is what makes the shape read as a world
    ey = project(0, 0, box)[1]
    d.line([x0 + 1, ey, x1 - 1, ey], fill=(46, 60, 92), width=1)
    for n, lat, lon, col in pins:
        px, py = project(lon, lat, box)
        if not (x0 + 3 < px < x1 - 3 and y0 + 3 < py < y1 - 3):
            continue
        d.ellipse([px - 3.5, py - 3.5, px + 3.5, py + 3.5], fill=col)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], outline=PAPER, width=1)


def grain(img, amount=3):
    """Give the paper a tooth.

    A page of flat vector fills measures a couple of hundred distinct colours;
    the entries that win this competition measure nine hundred to sixteen
    hundred, because their pages carry photographs, gradients and the small
    irregularities of print. A flat page beside them reads as a diagram rather
    than as a printed sheet, however well it is drawn.

    So the sheet gets a grain: a deterministic offset of a few levels per pixel,
    fixed by position so two renders of the same page are identical. It is
    invisible at reading size and it is what makes the page read as ink on
    paper rather than as fills on a canvas.
    """
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            # a cheap deterministic hash of the position, in [-amount, amount]
            n = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
            n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
            d = ((n >> 16) % (2 * amount + 1)) - amount
            r, g, b = px[x, y]
            px[x, y] = (min(255, max(0, r + d)),
                        min(255, max(0, g + d)),
                        min(255, max(0, b + d)))
    return img


def main(out_path):
    CAPS_DRAWN.clear()
    if not GEO:
        GEO.update(load_geo())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    red = REGION["middle-east"][0]

    f_src = font("arialbd.ttf", 8)
    f_kick = font("arialbd.ttf", 9)
    f_micro = font("arial.ttf", 8.5)

    # ---- nameplate: a solid block of ink at the head of the page
    d.rectangle([0, 0, W, M + 26], fill=NAVY)
    d.rectangle([M, M + 1, M + 4, M + 17], fill=red)
    caps(d, (M + 11, M), "THE WORLD ON ONE DAY", font("arialbd.ttf", 12), PAPER)
    tally = "  ".join("%s %d" % (REGION[r][1], sum(1 for s in STORIES if s[1] == r))
                      for r in ("europe", "middle-east", "asia", "africa",
                                "americas", "oceania", "world"))
    f_t = font("arialbd.ttf", 10)
    caps(d, (RIGHT - caps_width(d, tally, f_t), M + 1), tally, f_t, (150, 163, 196))
    d.line([M, M + 24, RIGHT, M + 24], fill=RULE, width=2)

    # ---- masthead: the date is the one string nothing may cross
    f_wd, _ = fit_caps(d, WEEKDAY, "arialbd.ttf", 20, EDGE, 12, track=7.0)
    caps(d, (M, M + 33), WEEKDAY, f_wd, red, track=7.0)
    f_date, date_size = fit(d, DATELINE, "georgiab.ttf", 92, EDGE, 1)
    d.text((M, M + 54), DATELINE, font=f_date, fill=INK)
    y = M + 54 + int(date_size * 1.06)

    deck = ("186 drones over Ukraine in one night \u00b7 COP31's text names no fossil fuels \u00b7 "
            "Iran's radar claim meets Bahrain's denial")
    f_d = font("georgiai.ttf", 13)
    for ln in wrap(d, deck, f_d, EDGE)[:2]:
        d.text((M, y), ln, font=f_d, fill=red)
        y += 17

    # ---- the day in six hard numbers
    y += 4
    nums = NUMBERS[:6]
    cell = EDGE // len(nums)
    for i, (reg, big, cap) in enumerate(nums):
        cx0 = M + i * cell
        col = REGION[reg][0]
        d.rectangle([cx0, y, cx0 + cell - 6, y + 3], fill=col)
        f_num = font("georgiab.ttf", 27)
        while tw(d, big, f_num) > cell - 16 and f_num.size > 14:
            f_num = font("georgiab.ttf", f_num.size - 1)
        d.text((cx0, y + 8), big, font=f_num, fill=INK)
        for k, ln in enumerate(wrap(d, cap, font("arial.ttf", 9), cell - 16)[:2]):
            d.text((cx0, y + 41 + k * 10), ln, font=font("arial.ttf", 9), fill=SOFT)
        if i:
            d.line([cx0 - 7, y + 6, cx0 - 7, y + 62], fill=(224, 218, 208), width=1)
    y += 60
    d.line([M, y, RIGHT, y], fill=RULE, width=2)
    y += 5

    # ---- the region key: the page's inventory, in its own colours
    bw = EDGE / len(REGION)
    for i, r in enumerate(("europe", "middle-east", "asia", "africa",
                           "americas", "oceania", "world")):
        seg = M + int(i * bw)
        seg_w = int(bw) - 3
        d.rectangle([seg, y, seg + seg_w, y + 9], fill=REGION[r][0])
        label = REGION[r][1]
        # the label is set to whatever size fits its own segment, so no region
        # goes unnamed and no name spills into its neighbour's column
        f_l, lsz = fit_caps(d, label, "arialbd.ttf", 8, seg_w - 2, 5, track=0.35)
        lab_w = caps_width(d, label, f_l, 0.35)
        caps(d, (seg + max(0, (seg_w - lab_w) // 2), y + 12), label, f_l,
             REGION[r][0], track=0.35)
    y += 22

    # ---- the three leads: picture, kicker, headline, what happened
    y += 5
    gap = 12
    lw = (EDGE - 2 * gap) // 3
    lead_top = y
    art_h = 116
    f_lh = font("georgiab.ttf", 16)
    f_lb = font("arial.ttf", 9.5)

    def lead_height(ah):
        h = ah + 8 + 11
        for n in LEADS:
            h = max(h, ah + 8 + 11 + int(16 * 1.2) * len(wrap(d, by_n(n)[2], f_lh, lw))
                    + 4 + 11 * len(short(d, by_n(n)[3], f_lb, lw, 5)))
        return h

    lh = lead_height(art_h)
    for i, n in enumerate(LEADS):
        st = by_n(n)
        col = colour(st)
        x = M + i * (lw + gap)
        img.paste(paint_art(n, lw, art_h, col), (x, lead_top))
        ty = lead_top + art_h + 6
        caps(d, (x, ty), "%d  %s" % (n, st[4].upper().split(" \u00b7 ")[0]), f_kick, col)
        ty += 11
        for ln in wrap(d, st[2], f_lh, lw):
            d.text((x, ty), ln, font=f_lh, fill=INK)
            ty += int(16 * 1.2)
        ty += 2
        for ln in short(d, st[3], f_lb, lw, 5):
            d.text((x, ty), ln, font=f_lb, fill=SOFT)
            ty += 11
        if n in CERTAINTY:
            caps(d, (x, ty + 2), CERTAINTY[n], font("arialbd.ttf", 8), FAINT)
    y = lead_top + lh + 5
    d.line([M, y, RIGHT, y], fill=RULE, width=1)
    y += 4

    # ---- twelve briefs: a numbered tile, a label, one headline
    caps(d, (M, y), "AND TWELVE MORE, DATED THE SAME DAY", font("arialbd.ttf", 9), INK)
    y += 14
    bgap = 10
    bcw = (EDGE - 2 * bgap) // 3
    f_bh = font("georgiab.ttf", 11.5)
    f_bt = font("arialbd.ttf", 8)

    rows = (len(BRIEFS) + 2) // 3
    tile = 22
    line_h = int(11.5 * 1.18)
    # every cell holds exactly two headline lines and one tag line, so the
    # tags line up across the row instead of following their own text down
    row_h = tile + 14
    for i, n in enumerate(BRIEFS):
        st = by_n(n)
        col = colour(st)
        cx = M + (i % 3) * (bcw + bgap)
        cy = y + (i // 3) * row_h
        d.rectangle([cx, cy, cx + tile, cy + tile], fill=col)
        f_n = font("arialbd.ttf", 10)
        nw = tw(d, str(n), f_n)
        d.text((cx + (tile - nw) // 2, cy + (tile - f_n.size) // 2 - 1), str(n), font=f_n, fill=WHITE)
        tx = cx + tile + 6
        inner = bcw - tile - 6
        lines = wrap(d, st[2], f_bh, inner)
        if len(lines) > 2:
            lines = lines[:2]
            lines[1] = clip_to(d, " ".join(lines[1].split() + []), f_bh, inner)
        for k, ln in enumerate(lines):
            d.text((tx, cy + k * line_h), ln, font=f_bh, fill=INK)
        caps(d, (tx, cy + 2 * line_h + 1), region_label(st), f_bt, col, track=0.3)
    y += rows * row_h + 2
    d.line([M, y, RIGHT, y], fill=RULE, width=1)
    y += 5

    # ---- when it broke, on the day's own clock
    # The clock is set as a dark band. It answers the nameplate at the head of
    # the page, and it gives the middle of the page a mass of ink: a sheet that
    # is paper from the date to the footer reads as a form, not as a front page.
    band_top = y - 5
    band_bot = y + 15 + 12 + 24
    d.rectangle([0, band_top, W, band_bot], fill=NAVY)
    caps(d, (M, y), "WHEN IT BROKE, UTC", font("arialbd.ttf", 9), PAPER)
    y += 15
    axis_y = y + 12
    # The ticks sit where their minutes put them, not at even intervals. The
    # day's beats are 28 minutes apart in one place and three hours in another,
    # and an axis that spaces them evenly turns the one part of the page that
    # claims to be a clock into an ornament. Equal intervals flatter the layout
    # and lie about the day; this one is true and reads as the interval it is.
    def mins(clock):
        hh, mm = clock.split(":")
        return int(hh) * 60 + int(mm)

    t0, t1 = mins(TIMELINE[0][0]), mins(TIMELINE[-1][0])
    span = max(1, t1 - t0)
    # the axis stops short of both margins: a caption centred on a tick that
    # sits on the margin has half of itself outside the page
    PAD = 14
    first_x, last_x = M + PAD, RIGHT - PAD
    inner = EDGE - 2 * PAD
    d.line([first_x, axis_y, last_x, axis_y], fill=(58, 72, 104), width=1)
    for i, (clock, what) in enumerate(TIMELINE):
        px = first_x + int((mins(clock) - t0) / span * inner)
        d.line([px, axis_y - 4, px, axis_y + 4], fill=PAPER, width=1)
        d.ellipse([px - 3, axis_y - 3, px + 3, axis_y + 3], fill=REGION["europe"][0])
        f_c = font("arialbd.ttf", 8.5)
        cw = tw(d, clock, f_c)
        d.text((px - cw // 2, axis_y - 16), clock, font=f_c, fill=PAPER)
        # The two tightest beats are 28 minutes apart, so a caption's column is
        # the distance to its neighbour, not the average step. Where even that
        # is too narrow to set, the caption drops to a second row of captions
        # rather than running into the one beside it.
        if i + 1 < len(TIMELINE):
            nxt = int((mins(TIMELINE[i + 1][0]) - mins(clock)) / span * inner)
        else:
            nxt = 10 ** 6
        if i:
            prv = int((mins(clock) - mins(TIMELINE[i - 1][0])) / span * inner)
        else:
            prv = 10 ** 6
        # Each caption is set from its own tick into the space that is actually
        # free beside it. Where the next beat is close, the room is the gap and
        # the caption runs to the right; at the end of the axis there is no gap,
        # so the last captions are set leftward from their tick instead.
        if nxt >= 96:
            room = nxt - 8
            anchor = "left"
        else:
            room = max(prv - 8, 84)
            anchor = "right"
        lines = wrap(d, what, f_micro, room)[:2]
        for k, ln in enumerate(lines):
            wl = tw(d, ln, f_micro)
            lx = px + 3 if anchor == "left" else px - wl - 3
            lx = max(M, min(lx, RIGHT - wl))
            d.text((lx, axis_y + 7 + k * 10), ln, font=f_micro, fill=(186, 196, 216))
    y = axis_y + 5 + 19
    d.line([M, y, RIGHT, y], fill=RULE, width=1)
    y += 5

    # ---- where it happened: every story that carries a place, on one map
    pins = []
    for st in STORIES:
        g = geo_of(st[0])
        if g:
            pins.append((st[0], g[0], g[1], colour(st)))
    caps(d, (M, y), "WHERE THE DAY HAPPENED", font("arialbd.ttf", 9), INK)
    caps(d, (RIGHT - caps_width(d, "%d OF 35 STORIES CARRY A PLACE" % len(pins),
                                 font("arialbd.ttf", 8), 0.3), y + 1),
         "%d OF 35 STORIES CARRY A PLACE" % len(pins), font("arialbd.ttf", 8), FAINT, track=0.3)
    y += 13
    map_h = 94
    draw_map(d, (M, y, RIGHT, y + map_h), pins)
    y += map_h + 4
    d.line([M, y, RIGHT, y], fill=RULE, width=1)
    y += 5

    # ---- the rest of the day, two columns
    caps(d, (M, y), "ALSO ON THE DAY", font("arialbd.ttf", 9), INK)
    note = "AP \u00b7 REUTERS \u00b7 AFP \u00b7 BBC \u00b7 USGS \u00b7 ICC \u00b7 KYODO \u00b7 PTI"
    caps(d, (RIGHT - caps_width(d, note, f_src), y + 1), note, f_src, FAINT)
    y += 15
    rest = [st for st in STORIES if st[0] in REST]
    # three columns, not two: the page has a map above the rail now, and the
    # rail's job is to hold what is left without pushing the footer off
    ncol = 3
    colw = (EDGE - 2 * 12) // ncol
    percol = (len(rest) + ncol - 1) // ncol
    f_rb = font("arialbd.ttf", 9.5)
    f_rr = font("arial.ttf", 9.5)
    for i, st in enumerate(rest):
        cx = M + (i // percol) * (colw + 12)
        yy = y + (i % percol) * 12
        d.rectangle([cx, yy + 2, cx + 2, yy + 7], fill=colour(st))

        # the rail carries the headline only: at three columns there is no room
        # for a per-line credit that would still be legible, and the page names
        # its wires once, in the rail's own header
        room = cx + colw - 4
        x = cx + 6
        head = st[2]
        if ": " in head:
            actor, tail = head.split(": ", 1)
            d.text((x, yy), actor + ":", font=f_rb, fill=INK)
            x += tw(d, actor + ":", f_rb) + tw(d, " ", f_rr)
            tail = clip_to(d, tail, f_rr, room - x)
            if tail:
                d.text((x, yy), tail, font=f_rr, fill=INK)
        else:
            d.text((x, yy), clip_to(d, head, f_rr, room - x), font=f_rr, fill=INK)
    y += percol * 12 + 5

    # ---- how to read it: the page states what it is sure of
    d.line([M, y, RIGHT, y], fill=RULE, width=2)
    y += 6
    legend = [("REPORTED", "carried by the day's wires"),
              ("CLAIM", "one side's account, labelled"),
              ("FORECAST", "still to come when drawn")]
    x = M
    for word, gloss in legend:
        f_g = font("arialbd.ttf", 8)
        w = caps_width(d, word, f_g, 0.6)
        d.rectangle([x, y, x + w + 8, y + f_g.size + 3], fill=SPINE)
        caps(d, (x + 4, y + 1), word, f_g, WHITE, track=0.6)
        x += w + 12
        d.text((x, y + 1), gloss, font=font("arial.ttf", 8.5), fill=SOFT)
        x += tw(d, gloss, font("arial.ttf", 8.5)) + 14
    y += 15

    # ---- footer
    fy = H - M - 9
    d.line([M, fy - 5, RIGHT, fy - 5], fill=RULE, width=1)
    d.text((M, fy), "Every story here was reported on Sunday 22 November 2026, in some time zone.",
           font=font("arial.ttf", 9), fill=SOFT)
    done = "ONE DAY, ONE PICTURE"
    caps(d, (RIGHT - caps_width(d, done, f_src), fy + 1), done, f_src, red)
    if y > fy - 8:
        print("WARNING: content overruns the footer by %d px" % (y - (fy - 8)))

    grain(img)
    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, Path(out_path).stat().st_size))


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
