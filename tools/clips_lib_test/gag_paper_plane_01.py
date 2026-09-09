import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- PAPER PLANE: glide in, loop, stall, nose-dive, crumple, hop up, shake, flee (gag) ----------
# One hand-drawn dart (nose LEFT, grey keel below) rotated nearest-neighbour for headings;
# crumple states are separate hand sprites. Heading angle: 0 = nose left, 90 = nose up, 180 = nose right.
DART = sprite("""
............ww
.........wwwww
......wwwwwwww
...wwwwwwwwwww
wwwbwwwwwwwwww
.wwbwwwwwwwww.
...pppppppppp.
......ppppppp.
.........ppp..
""")
_cache = {}
def plane(deg):
    """DART rotated so the nose points `deg` degrees (0 left, 90 up). Quantised to 5 deg, cached."""
    a = int(round(deg / 5.0)) * 5 % 360
    if a not in _cache: _cache[a] = DART.rotate(-a, resample=Image.NEAREST, expand=True)
    return _cache[a]

SQUASH = sprite("""
..wwwwwwwwwwww..
wwwbwwwwpwwwwwww
.wwwwwwwwwwwwww.
""")
BALL = sprite("""
...wwwww..
.wwwpwwww.
wwwwwpwwww
wwbwwwwpww
wwbpwwwwww
.wwwppwwww
..wwwwpww.
...wwwww..
""")
BALL_BLINK = sprite("""
...wwwww..
.wwwpwwww.
wwwwwpwwww
wwwwwwwpww
wbbpwwwwww
.wwwppwwww
..wwwwpww.
...wwwww..
""")
SQUAT = sprite("""
..wwwwwwww..
.wwwpwwwwww.
wwbwwwwpwwww
wwbwpwwwwwww
.wwwwwwpwww.
""")
HALF = sprite("""
.....wwwww..
..wwwwwwwww.
wwbwwwwpwwww
wwbwwwpppwww
.wwwppppppw.
...pppppp...
""")

def centred(im, c, spr, x, y):
    c.blit(im, spr, x - spr.width // 2, y - spr.height // 2)

def dust(im, k, x0, y0):
    """k = frames since impact: grey puffs flying out and up, fading."""
    col = PAL['s'] if k < 2 else PAL['P']
    for dx, dy in ((-1, 0), (1, 0), (-1, -1), (1, -1), (0, -1)):
        px, py = x0 + dx * (5 + 3 * k), y0 + dy * (1 + k) - k
        if 0 <= px < W and 0 <= py < H: im.putpixel((int(px), int(py)), col)

def build():
    c = Clip('gag_paper_plane_01', 6.0)
    CX, CY, R = 122, 15, 8                      # loop circle
    ground = H - 1
    LX = 92                                      # crash spot: right under the camera hole
    for i in range(c.n):
        im = c.frame()
        if i == 0: continue
        if i < 15:                                   # glide in from the right with a lazy bob
            t = (i - 1) / 13
            x = (W + 8) + (CX - (W + 8)) * t
            y = 16 + (CY + R - 16) * t + 1.5 * math.sin(i * 0.8)
            centred(im, c, plane(8 * math.sin(i * 0.8 + 1)), x, y)
        elif i < 31:                                 # one clean loop, 16 frames, clockwise on screen
            k = i - 15
            phi = math.radians(90 + 360 * k / 16)
            centred(im, c, plane(360 * k / 16), CX + R * math.cos(phi), CY + R * math.sin(phi))
        elif i < 37:                                 # proud climb up-left, slowing
            t = ease((i - 31) / 6)
            centred(im, c, plane(45 + 45 * t), CX - 14 * t, (CY + R) - 14 * t)
        elif i < 40:                                 # stall: hangs vertical, last 1px of lift
            centred(im, c, plane(90), CX - 14, CY + R - 14 - (i - 37) * 0.5)
        elif i < 43:                                 # nose flops over: up -> left -> down-left
            a = 90 - 45 * (i - 39)                   # 45, 0, -45
            centred(im, c, plane(a), CX - 15 - (i - 39), CY + R - 14 + (i - 39))
        elif i < 49:                                 # nose-dive, accelerating, drifting to the centre
            t = (i - 43) / 5; tt = t * t
            x0, y0 = CX - 18, CY + R - 12
            centred(im, c, plane(-90 - 10 * t), x0 + (LX - x0) * t, y0 + (ground - 5 - y0) * tt)
        elif i == 49:                                # impact: flat squash + dust
            c.blit(im, SQUASH, LX - 8, ground - 2); dust(im, 0, LX, ground - 1)
        elif i < 58:                                 # crumpled ball; a beat; one slow blink
            spr = BALL_BLINK if i in (54, 55) else BALL
            c.blit(im, spr, LX - 5, ground - 7)
            if i < 53: dust(im, i - 49, LX, ground - 2)
        elif i == 58:                                # anticipation squat
            c.blit(im, SQUAT, LX - 6, ground - 4)
        elif i == 59:                                # hop
            c.blit(im, BALL, LX - 5, ground - 13)
        elif i == 60:                                # half unfolded at the apex
            c.blit(im, HALF, LX - 6, ground - 15)
        elif i == 61:                                # full plane, settling
            centred(im, c, plane(0), LX, ground - 8)
        elif i < 66:                                 # shake it off: x jitter + small tilt
            s = 1 if (i - 62) % 2 == 0 else -1
            centred(im, c, plane(s * 15), LX + s * 2, ground - 8 - (i % 2))
        else:                                        # flee left, wobbling, accelerating off the edge
            t = (i - 66) / 5
            x = LX + (-18 - LX) * (t * t)
            y = ground - 9 - 4 * t + 2.5 * math.sin(i * 1.4)
            centred(im, c, plane(20 * math.cos(i * 1.4)), x, y)
    return c
