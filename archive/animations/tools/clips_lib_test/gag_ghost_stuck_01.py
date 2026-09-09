import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- GHOST SQUEEZES INTO THE CAMERA HOLE, GETS STUCK (gag) ----------
# Modular: sheet body (3 squash/stretch sizes, generated) + eyes + mouth + arms + blush as offsets/swaps.
MYPAL = {'q': (255, 140, 165)}          # blush

_DOME = {10: (3, 2, 1), 12: (4, 2, 1), 14: (5, 3, 1)}   # transparent px each side for the 3 dome rows
_cache = {}
def body(w, h, hem):
    """Sheet: rounded top, right-edge shade, scalloped hem (hem = 0|1 shifts the scallops = wave)."""
    key = (w, h, hem)
    if key not in _cache:
        rows = []
        for r in range(h - 1):
            k = _DOME[w][r] if r < 3 else 0
            row = '.' * k + 'w' * (w - 2 * k) + '.' * k
            if r >= 3: row = row[:-1] + 's'
            rows.append(row)
        rows.append(''.join('.' if (x + 2 * hem) % 4 < 2 else ('s' if x == w - 1 else 'w') for x in range(w)))
        _cache[key] = sprite('\n'.join(rows), MYPAL)
    return _cache[key]

NORMAL, TALL, WIDE = (12, 15), (10, 18), (14, 12)
EYE = sprite("bb\nwb\nbb")            # dark socket with a white glint
EYE_WIDE = sprite("bb\nwb\nbb\nbb")
EYE_SQUINT = sprite("bb\nbb")
MOUTH_O = sprite("kk\nkk")
MOUTH_FLAT = sprite("kkk")
ARM = sprite("www\n.ww")
BLUSH = sprite("qq", MYPAL)

def ghost(im, c, x, bottom, size=NORMAL, hem=0, look=(0, 0), eye=EYE, mouth=None, arms=0, blush=False):
    """x = left of body, bottom = y just below the hem. look = eye offset. arms = row offset (int or (l, r))."""
    w, h = size
    y = bottom - h
    c.blit(im, body(w, h, hem), x, y)
    ey = y + h // 3 + look[1]
    if eye is not None:
        c.blit(im, eye, x + w // 2 - 4 + look[0], ey)
        c.blit(im, eye, x + w // 2 + 2 + look[0], ey)
    if blush:
        c.blit(im, BLUSH, x + w // 2 - 5, ey + 3)
        c.blit(im, BLUSH, x + w // 2 + 3, ey + 3)
    if mouth is not None:
        c.blit(im, mouth, x + w // 2 - 1, ey + 5)
    dl, dr = arms if isinstance(arms, tuple) else (arms, arms)
    c.blit(im, ARM, x - 3, y + h // 2 + dl)
    c.blit(im, flip(ARM), x + w, y + h // 2 + dr)

def build():
    c = Clip('gag_ghost_stuck_01', 6.0)
    home_x, hover = CAM[0] - 6, H - 2            # centred under the hole; hem one px above the floor
    for i in range(c.n):
        im = c.frame()
        bob = round(1.2 * math.sin(i * 0.6))
        if i == 0:
            continue                              # empty first frame
        if i < 18:                                # float in from the left
            t = ease((i - 1) / 16)
            ghost(im, c, -18 + 78 * t, hover + bob, hem=(i // 4) % 2, eye=EYE_SQUINT if i in (9, 10) else EYE)   # blink
        elif i < 22:                              # notice the hole: startle hop, eyes wide and up
            hop = (-3, -4, -2, 0)[i - 18]
            ghost(im, c, 60, hover + hop, hem=i % 2, look=(0, -1), eye=EYE_WIDE, mouth=MOUTH_O, arms=-2)
        elif i < 30:                              # drift under it, eyes on the hole
            t = ease((i - 22) / 7)
            ghost(im, c, 60 + (home_x - 60) * t, hover + bob, hem=(i // 3) % 2, look=(0, -1), mouth=MOUTH_O)
        elif i < 33:                              # anticipation: squash down
            ghost(im, c, home_x - 1, H, size=WIDE, hem=i % 2, look=(0, -1), mouth=MOUTH_O, arms=1)
        elif i < 39:                              # launch up into the hole, accelerating (stretch)
            t = ((i - 32) / 6) ** 2
            ghost(im, c, home_x + 1, hover + (8 - hover) * t, size=TALL, hem=i % 2, look=(0, -1), mouth=MOUTH_O, arms=-4)
        elif i < 56:                              # stuck: only the hem half hangs from the ceiling, wiggling
            j = i - 39
            dx = (0, 1, 1, 0, -1, -1)[j % 6]
            yank = j % 6 in (3, 4)
            if yank: ghost(im, c, home_x + dx, 8, size=TALL, hem=i % 2, eye=None, arms=1)   # heave: arms braced on the ceiling
            else:    ghost(im, c, home_x + dx, 11 if j == 0 else 10, hem=i % 2, eye=None, arms=((-2, 1), (1, -2))[(j // 2) % 2])
        elif i < 62:                              # pop free: drop, stretch, splat on the floor, bounce
            k = i - 56
            size, bottom = ((TALL, 12), (TALL, 22), (WIDE, H), (WIDE, H), (NORMAL, hover - 3), (NORMAL, hover))[k]
            ghost(im, c, home_x + (1 if size == TALL else -1 if size == WIDE else 0), bottom, size=size,
                  hem=i % 2, mouth=MOUTH_O, eye=EYE_WIDE if k < 4 else EYE, arms=-4 if k < 2 else 1 if k < 4 else 0)
        elif i < 67:                              # embarrassed: blush, squint, glance right then left
            look = (1 if i < 65 else -1, 0)
            ghost(im, c, home_x, hover, hem=(i // 2) % 2, look=look, eye=EYE_SQUINT, mouth=MOUTH_FLAT, blush=True)
        else:                                     # zip off right, accelerating; last frame fully off-strip
            t = ((i - 66) / (c.n - 1 - 66)) ** 2
            ghost(im, c, home_x + (W + 4 - home_x) * t, hover + bob, hem=i % 2, look=(1, 0), eye=EYE_SQUINT,
                  mouth=MOUTH_FLAT, blush=True)
    return c
