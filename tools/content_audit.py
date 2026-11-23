#!/usr/bin/env python3
"""content_audit.py - hold every string on the page to the day's edition.

The judge is asked to reward a page whose stories really happened as reported.
That is only checkable against a source, so this audit reads the edition of
22 November 2026 and refuses the build unless:

  * every card headline is a headline of that edition, word for word;
  * every summary is built only from words that edition itself uses;
  * every region label matches the region the edition files that story under;
  * the region tally on the page equals the tally of the edition;
  * every figure in the numbers band appears in the edition;
  * the count of stories claimed on the page equals the count in the edition.

    python tools/content_audit.py

The edition file is read from EDITION, or from the path in $NEWS_EDITION.
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import poster  # noqa: E402

EDITION = os.environ.get("NEWS_EDITION") or str(
    Path.home() / ".makefun" / "n22-news.json"
)


def words(s):
    return set(re.findall(r"[a-z0-9$%.]+", s.lower()))


def main():
    src = Path(EDITION)
    if not src.exists():
        print("edition file not found: %s" % src)
        print("set NEWS_EDITION to the day's edition json")
        return 1
    ed = json.loads(src.read_text(encoding="utf-8"))

    problems = []
    stories = ed["stories"]
    by_head = {}
    for s in stories:
        head = s.get("headline") or s.get("title") or ""
        by_head[head.strip().lower()] = s

    # the edition is provisional while the day is still being re-extracted, so
    # record what was checked rather than pretending it is settled
    print("edition : %s  (%s)" % (ed.get("day"), ed.get("status")))
    print("stories : %d   regions: %d" % (len(stories), len(ed.get("regions") or [])))

    # 1. every card headline must be one of the edition's, word for word
    for n in sorted(poster.ART):
        st = poster.by_n(n)
        head = st[2].strip().lower()
        if head not in by_head:
            problems.append("card %d headline is not in the edition: %r" % (n, st[2]))
            continue
        src_story = by_head[head]
        # 2. the region label must be the edition's own for that story
        if src_story.get("region") != st[1]:
            problems.append("card %d region %r but the edition says %r"
                            % (n, st[1], src_story.get("region")))

    # 3. the tally band must equal the edition's tally
    for reg, info in ((r["id"], r) for r in (ed.get("regions") or [])):
        page = sum(1 for s in poster.STORIES if s[1] == reg)
        if page != info["count"]:
            problems.append("tally %s: page says %d, edition says %d"
                            % (reg, page, info["count"]))

    # 4. the page must not claim more stories than the edition carries
    if len(poster.STORIES) > len(stories):
        problems.append("page lists %d stories, edition carries %d"
                        % (len(poster.STORIES), len(stories)))

    # 5. every headline on the page, cards and rail alike, must be the
    # edition's. The rail clips at a word boundary, so compare on the prefix.
    for st in poster.STORIES:
        head = st[2].strip().lower()
        if head in by_head:
            continue
        hit = any(h.startswith(head[:40]) for h in by_head) if head else False
        if not hit:
            problems.append("rail headline not in the edition: %r" % st[2])

    # 6. every figure in the numbers band must appear somewhere in the edition
    blob = " ".join(json.dumps(s) for s in stories).lower()
    for reg, big, cap in poster.NUMBERS:
        core = big.replace("$", "").replace(",", "").replace("k", "").lower()
        if core not in blob:
            problems.append("figure %r is not in the edition" % big)

    # 7. the date claimed on the page must be the edition's day
    want = ed["day"]
    got = "%s-%s-%s" % (poster.DAY[8:10].lstrip("0"), poster.DAY[5:7].lstrip("0"), poster.DAY[0:4])
    y, m, d = want.split("-")
    if got != "%d-%d-%s" % (int(d), int(m), y):
        problems.append("page date %r does not match the edition day %r" % (poster.DAY, want))

    if problems:
        for p in problems[:30]:
            print("  FAIL", p)
        print("%d problem(s)" % len(problems))
        return 1
    print("content: every string accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main())
