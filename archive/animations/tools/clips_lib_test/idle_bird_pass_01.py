import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'idle'

# ---------- DISTANT BIRD CROSSES HIGH UP (idle) ----------
# 4 px wide. Two-frame flap (wings up / wings down) + a tucked glide for the dive.
# Body is the brighter pixel pair, wings the cooler grey, so the flap reads even this small.
BIRD_UP = sprite("""
s..s
.ww.
""")
BIRD_DOWN = sprite("""
.ww.
s..s
""")
BIRD_GLIDE = sprite("""
ssws
""")

# timing (frames): cruise -> lift (anticipation) -> dive (glide, faster) -> climb (hard flap) -> overshoot settle -> cruise
LIFT, DIVE, CLIMB, SETTLE = 14, 17, 24, 34
BASE_Y, DEPTH = 4, 8

def build():
    c = Clip('idle_bird_pass_01', 4.0)
    n = c.n
    # horizontal: forward speed boosts through the dive, integrate then rescale so it spans the strip
    vx = [0.0] + [1.6 if DIVE <= i < CLIMB else 1.0 for i in range(1, n - 1)] + [0.0]
    xs, acc = [], 0.0
    for v in vx: acc += v; xs.append(acc)
    x0, x1 = -7, W
    xs = [x0 + (x1 - x0) * a / xs[-2] for a in xs]
    for i in range(n):
        im = c.frame()
        if i == 0 or i == n - 1: continue         # empty bookends
        if i < LIFT:            dy = 0;                                            spr = None
        elif i < DIVE:          dy = -1;                                           spr = BIRD_UP     # wings high: anticipation
        elif i < CLIMB:         dy = -1 + (DEPTH + 1) * ease((i - DIVE) / (CLIMB - DIVE)); spr = BIRD_GLIDE
        elif i < SETTLE:        dy = DEPTH - (DEPTH + 1) * ease((i - CLIMB) / (SETTLE - CLIMB)); spr = BIRD_UP if i % 2 == 0 else BIRD_DOWN  # hard flap
        elif i < SETTLE + 4:    dy = -1 + ease((i - SETTLE) / 4);                  spr = None
        else:                   dy = 0;                                            spr = None
        if spr is None: spr = BIRD_UP if (i // 2) % 2 == 0 else BIRD_DOWN         # cruise flap
        c.blit(im, spr, round(xs[i]), BASE_Y + round(dy))
    return c
