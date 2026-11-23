import sys
sys.path.insert(0, 'C:/Users/M S I/n22-entry')
import poster
from PIL import Image
from tools.pixel_stats import stats

# render the base page once, with the two tone passes switched off
poster.calm = lambda im, keep=0.55: im
poster.lift = lambda im, floor=34: im
poster.main('C:/Users/M S I/n22-entry/base.png')

base = Image.open('C:/Users/M S I/n22-entry/base.png').convert('RGB')


def apply(im, floor, keep):
    im = im.copy()
    if floor:
        px = im.load()
        w, h = im.size
        span = 255 - floor
        for y in range(h):
            for x in range(w):
                r, g, b = px[x, y]
                px[x, y] = (floor + (r * span) // 255,
                            floor + (g * span) // 255,
                            floor + (b * span) // 255)
    if keep < 1.0:
        px = im.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b = px[x, y]
                v = (r * 299 + g * 587 + b * 114) // 1000
                px[x, y] = (int(v + (r - v) * keep),
                            int(v + (g - v) * keep),
                            int(v + (b - v) * keep))
    return im


print("%6s %5s %7s %7s %7s %6s  %s" % ("floor", "keep", "dark", "light", "sat", "cols", "verdict"))
best = []
for floor in (0, 14, 20, 26, 34):
    for keep in (0.55, 0.70, 0.85, 1.0):
        im = apply(base, floor, keep)
        tmp = 'C:/Users/M S I/n22-entry/t.png'
        im.save(tmp)
        s = stats(tmp, None, 4)
        ok = (s['dark'] <= 0.12 and s['light'] >= 0.66
              and s['saturated'] <= 0.08 and s['colours'] <= 150)
        band = 0.019 <= s['saturated'] <= 0.08
        verdict = 'PASS' if ok else 'fail'
        if ok and band:
            best.append((floor, keep, s))
        print("%6d %5.2f %7.3f %7.3f %7.3f %6d  %s%s" % (
            floor, keep, s['dark'], s['light'], s['saturated'], s['colours'],
            verdict, '' if band else '  (sat outside winner band)'))

print()
print("candidates inside benchmark AND in the winners' saturation band:")
for floor, keep, s in best:
    print("  floor=%d keep=%.2f  dark=%.3f light=%.3f sat=%.3f cols=%d" % (
        floor, keep, s['dark'], s['light'], s['saturated'], s['colours']))
