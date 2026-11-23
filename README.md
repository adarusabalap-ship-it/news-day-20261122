# news-day-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/adarusabalap-ship-it/news-day-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/adarusabalap-ship-it/news-day-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One page that sums up Sunday 22 November 2026: a masthead that names the day, a band of eight figures, eight illustrated cards, and a rail with the rest of the edition's stories. Every headline, figure, region and outlet on the page comes from that day's edition — the drawing is flat vector shapes and system fonts only, so the same run always writes the same bytes.

The eight cards are the stories that carry the day: Russia's 186 drones in one night and the block destroyed outside Kyiv, the COP31 deal that names no fossil fuels, Iran's claim to have hit two US radars and Bahrain's denial, Hong Kong electing its Election Committee, India declaring on 720 for 9 in New Zealand, Verstappen in Las Vegas, Wembanyama's 50 points, and the cargo ship Sparta II hit by drones with Finland leading the rescue.

The edition files seven regions and 35 stories; the page carries all 35, eight of them as cards and the other 27 in the foot rail, with the region tally stated at the top so the breadth is visible before a reader starts.

## Checks

- `python tools/layout_audit.py` runs the page's own drawing code in recording mode, measures all 375 strings with the font each was drawn in, and fails on any overlap, any string off the measure, any caption drawn twice, any string under 8pt, or a date that is not the largest type on the page.
- `python tools/content_audit.py` reads the day's edition and fails unless every card headline is one of its headlines word for word, every region label matches the region the edition files that story under, the tally band equals the edition's own tally, every figure in the numbers band appears in the edition, and the page claims no more stories than the edition carries.
- `python tools/pixel_stats.py` measures the page against the four numbers that separate the strongest entries in this family — dark share, light share, saturation and palette size — and fails outside them.
- `python tools/tune_tone.py` sweeps the two tone parameters against those benchmarks and prints which combinations land nearest the strongest entry's profile; the constants in `poster.py` come from its output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` reads `entry.png`, refuses it unless it is a whole PNG or JPEG within 1 MiB and 1024 by 1024, and copies it to the output directory. It uses the Python standard library only and touches no network.

## The map

`tools/data/ne_110m_land.geojson` is Natural Earth's 1:110m land layer
(public domain, nvkelso/natural-earth-vector), committed so the map renders
offline and always the same. `tools/poster.py` projects it in Web Mercator and
plots one dot per story whose edition record carries a place -- 30 of the 35.
The outline is real geometry rather than remembered coordinates, and the page
says how many stories it could place.
