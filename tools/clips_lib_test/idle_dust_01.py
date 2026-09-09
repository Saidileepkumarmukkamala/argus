import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'idle'

# ---------- DUST MOTES (idle) ----------
# Three 1-px motes drift in from an edge, curve toward the camera hole, circle it once like a moth
# at a lamp, and slip out through the top. Barely there.
GREY = [(70, 70, 80), (110, 110, 122), (150, 150, 165), (200, 200, 215)]
ORBIT, RISE = 10, 4                                  # frames circling under the hole, frames leaving

# (start frame, end frame, entry point, mid control point, wobble phase, orbit direction)
MOTES = [
    (0,  64, (-1, 24), (40, 22),  0.0,  1),
    (16, 82, (W, 18),  (140, 14), 2.1, -1),
    (34, 95, (58, H),  (62, 16),  4.2,  1),
]

def mote(f, t0, t1, p0, p1, phase, d):
    """(x, y, colour) of a mote at frame f, or None if it is not on stage."""
    if not (t0 < f < t1): return None
    cx, cy, r = CAM[0], 2, 3
    ta = t1 - ORBIT - RISE                           # drift ends, orbit starts
    tb = t1 - RISE                                   # orbit ends, rise starts
    if f < ta:                                       # drift: quadratic bezier p0 -> p1 -> orbit entry
        s = ((f - t0) / (ta - t0)) ** 1.35           # lazy start, pulled in faster near the light
        p2 = (cx + d * r, cy)
        x = (1-s)**2 * p0[0] + 2*(1-s)*s * p1[0] + s*s * p2[0]
        y = (1-s)**2 * p0[1] + 2*(1-s)*s * p1[1] + s*s * p2[1]
        x += 1.5 * (1 - s) * math.sin(f * 0.45 + phase); y += (1 - s) * math.sin(f * 0.3 + phase)
    elif f < tb:                                     # orbit: half-turn under the hole
        a = math.pi * (f - ta) / ORBIT
        x = cx + d * r * math.cos(a); y = cy + r * math.sin(a)
    else:                                            # rise: straight up and out
        x = cx - d * r; y = cy - 2 * (f - tb)
    fade = min(1.0, (f - t0) / 6)
    s = min(1.0, (f - t0) / (ta - t0))
    twinkle = 0.5 + 0.5 * math.sin(f * 0.8 + phase)
    lvl = int(round(fade * (1 + twinkle + s)))       # brighter as it nears the hole
    return int(round(x)), int(round(y)), GREY[max(0, min(3, lvl))]

def build():
    c = Clip('idle_dust_01', 8.0)
    for i in range(c.n):
        im = c.frame()
        for m in MOTES:
            r = mote(i, *m)
            if r and 0 <= r[0] < W and 0 <= r[1] < H:
                im.putpixel((r[0], r[1]), r[2])
    return c

if __name__ == '__main__':                           # self-check: empty ends, no jumps
    c = build()
    assert not c.frames[0].getbbox() and not c.frames[-1].getbbox()
    for m in MOTES:
        prev = None
        for f in range(m[0], m[1]):
            r = mote(f, *m)
            if r and prev: assert abs(r[0]-prev[0]) <= 3 and abs(r[1]-prev[1]) <= 3, (m, f, prev, r)
            prev = r
    print('ok')
