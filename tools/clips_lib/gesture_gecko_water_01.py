"""One Drop — a parched desert gecko hauls over the ledge, a bead forms on the notch underside and falls into its
mouth; colour floods back head to tail. It leaves the second drop for you. ~48 px long, 4-tone ramps, procedural tail."""
import sys, os, math
from functools import lru_cache
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- palettes: one green, one dusty (derived), same keys so sprites share geometry ----------
Gb = ramp((104, 184, 78)); Bb = ramp((226, 218, 168))
GREEN = {'S': Gb[0], 's': Gb[1], 'l': Gb[2], 'h': Gb[3],
         'B': Bb[0], 'b': Bb[1], 'e': Bb[2],
         'c': (58, 140, 96), 'C': (36, 96, 70), 'o': (64, 124, 52),
         'R': (200, 116, 40), 'Y': (244, 200, 70), 'y': (252, 232, 150), 'k': (18, 14, 22), 'W': (255, 255, 255),
         'm': (120, 44, 64), 'r': (232, 110, 128), 'p': (236, 200, 190), 'P': (180, 130, 120)}
KEEP = set('kWmr')

def dust(c):
    g = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    t = (g * 0.72 + 52, g * 0.66 + 42, g * 0.55 + 26)
    return tuple(int(c[k] * 0.25 + t[k] * 0.75) for k in range(3))

DUSTY = {k: (v if k in KEEP else dust(v)) for k, v in GREEN.items()}
PALS = {'g': GREEN, 'd': DUSTY}
RIM = {'g': (62, 96, 72), 'd': (92, 84, 68)}
BLUE = {'c': (130, 205, 235), 'C': (70, 140, 195), 'W': (255, 255, 255)}

@lru_cache(maxsize=None)
def S(rows, pk='g'):
    return sprite(rows, PALS[pk])

def dark(rows):
    """Far-side limb: same shape, all shadow tones."""
    return rows.translate(str.maketrans('slhpP', 'SSSPP'))

# ---------- head: base rows + eye block splice + mouth variants (facing right) ----------
HEAD_TOP = ["......hhhhhh....",
            "...hhllllllll...",
            "..hllllsssssss.."]
HEAD_EYE = [".hllsssssssssss.",
            ".llsssssssssssss",
            ".lsssssssssssssh",
            ".sssssssssssssss",
            ".Sssssssssssssss"]
MOUTH = {
    'closed': [".SSsssssssbbbbmm",
               "..SSBbbbbbbbBBB."],
    'tongue': [".SSsssssssbbbmrr",
               "..SSBbbbbbbbBBBr",
               "................r"],
    'open':   [".SSsssssmmmmmmmm",
               "..SSssssmrrrmmm.",
               "...SSbbbbbbbbb..",
               "....SBBBBBBBB..."],
}
EYES = {
    'open':   [".RRR.", "RYyYR", "RYkWR", "RYkYR", ".RRR."],
    'up':     [".RRR.", "RYkWR", "RYkYR", "RYyYR", ".RRR."],
    'shiny':  [".RRR.", "RyyyR", "RykWR", "RYkYR", ".RRR."],
    'half':   [".lll.", "lssss", "RYkWR", "RYkYR", ".RRR."],
    'closed': [".lll.", "lssss", "sSSSs", "sssss", ".sss."],
}

def head_rows(eye, mouth):
    rows = list(HEAD_TOP)
    for r, e in zip(HEAD_EYE, EYES[eye]):
        r = list(r)
        for k, ch in enumerate(e):
            if ch != '.': r[4 + k] = ch
        rows.append(''.join(r))
    return '\n'.join(rows + MOUTH[mouth])

HEAD_FRONT = {
    'open': """
....hhhhhh....
..hlllllllll..
.llssssssssss.
.lRRRssssRRRs.
.RYyYRssRYyYR.
.RykWRssRykWR.
.RYkYRssRYkYR.
..RRRsssssRRR.
..SsssssssssS.
...SbbbbbbbS..
....BBBBBB....
""",
    'closed': """
....hhhhhh....
..hlllllllll..
.llssssssssss.
.llllssssllll.
.lssssssssssl.
.sSSSsssssSSSs
.ssssssssssss.
..ssssssssss..
..SsssssssssS.
...SbbbbbbbS..
....BBBBBB....
"""}

# ---------- body (20x8) + crest ----------
BODY = """
...hhhhhhhhhhhhhhhh.
.hlllllolllllolllllh
hlssssssssssssssssss
lsssossssoossssosssS
sssssssssssssssssssS
SsssssssssssssssssbS
SBbbbbbbbbbbbbbbbbb.
.BBBBBBBBBBBBBBBBB..
"""
CREST_FLAT = "...c...c...c...c...c"
CREST_UP = """
...c...c...c...c...c
..cCc.cCc.cCc.cCc.cC
"""

# ---------- legs (bottom row = toe pads on the floor) ----------
LEG_F = ["""
Ss....
.Ss...
..ss..
..sss.
.pPpPp
""", """
..sS..
..sS..
..ss..
.sss..
pPpPp.
"""]
LEG_B = ["""
...sS.
..sS..
..ss..
.sss..
pPpPp.
""", """
Ss....
.Ss...
..ss..
..sss.
.pPpPp
"""]
LEG_F_FLAT = """
Ss.........
.Sss.......
...ssspPpPp
"""
LEG_B_FLAT = """
........sS.
......sssS.
pPpPpsss...
"""
PADS = """
pPpPp
.SSS.
"""

def leg_up(n):
    """Straight front leg, n rows of shin above the foot."""
    return '\n'.join(['Ss...'] * n + ['.ss..', 'pPpPp'])

# ---------- procedural tail: returns (sprite, ax, ay) with (ax, ay) = base point inside the sprite ----------
@lru_cache(maxsize=None)
def tail(pk, mode, amt=1.0, phase=0.0, drop=0, L=19):
    p = PALS[pk]; pix = {}
    x = y = 0.0; th_ = math.pi
    for k in range(L):
        s = k / (L - 1)
        if mode == 'drag':
            x, y = -k, min(drop, k * 0.7)
        elif mode == 'wave':
            x, y = -k, amt * math.sin(phase + s * 2 * math.pi) * s * 3.2 - s * 2
        else:  # curl
            th_ = math.pi + amt * (s ** 1.25) * 1.75 * math.pi
            x += math.cos(th_); y += math.sin(th_)
        th = 3 if s < 0.35 else 2 if s < 0.7 else 1
        cx, cy = round(x), round(y)
        if th == 3:
            for dx, dy, ch in ((0, 0, 's'), (-1, 0, 's'), (1, 0, 's'), (0, -1, 'l'), (0, 1, 'S')): pix.setdefault((cx + dx, cy + dy), ch)
        elif th == 2:
            pix.setdefault((cx, cy), 's'); pix.setdefault((cx, cy + 1), 'S')
        else:
            pix.setdefault((cx, cy), 's')
    xs = [q[0] for q in pix]; ys = [q[1] for q in pix]
    mnx, mny = min(xs), min(ys)
    im = Image.new('RGBA', (max(xs) - mnx + 1, max(ys) - mny + 1), (0, 0, 0, 0)); px = im.load()
    for (qx, qy), ch in pix.items(): px[qx - mnx, qy - mny] = p[ch] + (255,)
    return im, -mnx, -mny

def shear(spr, rise):
    """Tilt a sprite: right-most column raised by `rise` px relative to the left-most."""
    if rise <= 0: return spr
    w, h = spr.size; out = Image.new('RGBA', (w, h + rise), (0, 0, 0, 0))
    for x in range(w):
        col = spr.crop((x, 0, x + 1, h)); out.paste(col, (x, rise - round(rise * x / (w - 1))), col)
    return out

# ---------- assembly: local space, floor row = F, body left = 16, facing right ----------
F = 24
def gecko(pk, pose, eye='open', mouth='closed', face='side', step=0, rise=0, tl=('drag', 1.0, 0.0), crest='flat'):
    """pose: crawl | flat | up | stand. Returns (outlined sprite, mx, my); blit at (gx + mx, gy + my) with gy = floor row - F."""
    lift = 4 if pose == 'stand' else 0
    parts = []
    # far legs first (dark), then tail, body, near legs, head
    if pose == 'stand':
        parts += [(S(dark(LEG_B[step]), pk), 15, F - 5), (S(dark(LEG_F[step]), pk), 29, F - 5)]
    elif pose in ('flat', 'crawl'):
        parts += [(S(dark(LEG_B_FLAT), pk), 4, F - 3), (S(dark(LEG_F_FLAT), pk), 30, F - 3)]
    else:  # up: back legs flat, front straight
        parts += [(S(dark(LEG_B_FLAT), pk), 4, F - 3), (S(dark(leg_up(rise)), pk), 30, F - 2 - rise)]
    tspr, ax, ay = tail(pk, tl[0], tl[1], tl[2], drop=lift + 2 if tl[0] == 'drag' else 0)
    parts.append((tspr, 17 - ax, F - lift - 3 - ay))
    body = S(BODY, pk)
    if pose == 'up': body = shear(body, rise)
    parts.append((body, 16, F - lift - body.height))
    cr = S(CREST_UP if crest == 'up' else CREST_FLAT, pk)
    parts.append((shear(cr, rise) if pose == 'up' else cr, 16, F - lift - body.height - cr.height))
    if pose == 'stand':
        parts += [(S(LEG_B[step], pk), 17, F - 5), (S(LEG_F[step], pk), 31, F - 5)]
    elif pose in ('flat', 'crawl'):
        parts += [(S(LEG_B_FLAT, pk), 6, F - 3), (S(LEG_F_FLAT, pk), 32, F - 3)]
    else:
        parts += [(S(LEG_B_FLAT, pk), 6, F - 3), (S(leg_up(rise), pk), 32, F - 2 - rise)]
    if face == 'front':
        hs = S(HEAD_FRONT[eye], pk); parts.append((hs, 33, F - lift - hs.height))
    else:
        hs = S(head_rows(eye, mouth), pk)
        hraise = rise if pose == 'up' else (2 if pose == 'crawl' else 0)
        parts.append((hs, 32, F - lift - hraise - 10))
    spr, mx, my = assemble(parts)
    return outline(spr, RIM[pk]), mx - 1, my - 1

def gecko_sweep(cut, **kw):
    """Column tint sweep: sprite-local columns >= cut are green, the rest dusty."""
    d, mx, my = gecko('d', **kw); g, _, _ = gecko('g', **kw)
    if cut <= 0: return g, mx, my
    if cut >= d.width: return d, mx, my
    out = d.copy(); out.paste(g.crop((cut, 0, g.width, g.height)), (cut, 0)); return out, mx, my

# ---------- water ----------
BEADS = [sprite("c", BLUE), sprite("cW\nCc", BLUE), sprite(".c.\ncWc\n.C.", BLUE), sprite(".c.\ncWc\ncCc\n.C.", BLUE)]
DROP = sprite(".C.\n.c.\ncWc\ncCc\n.C.", BLUE)

def bead(im, x, y, i, t0, sway0):
    """Bead growing on the underside at (x, y) from frame t0; sways once starting at sway0."""
    if i < t0: return
    k = min(3, (i - t0) // 3)
    if 0 <= i - sway0 < 6: x += [1, 1, 0, -1, -1, 0][i - sway0]
    dots(im, [(x - 1, y), (x, y), (x + 1, y)], BLUE['C'])
    im.paste(BEADS[k], (int(x) - BEADS[k].width // 2, int(y)), BEADS[k])

def fall(im, x, y0, y1, i, t0, n):
    """Eased (gravity) fall of a drop from y0 to y1 over n frames starting at t0."""
    if not t0 <= i < t0 + n: return
    t = (i - t0) / (n - 1); y = y0 + (y1 - y0) * t * t
    im.paste(DROP, (int(x) - 1, int(y)), DROP)

def splash(im, cx, cy, k, floor=False):
    """Four droplets + one ring, k frames after impact."""
    if not 0 <= k < 6: return
    d = ImageDraw.Draw(im)
    r = 1 + k * (2 if floor else 1); fade = 1 - k / 6
    col = tuple(int(v * fade) for v in BLUE['c'])
    if floor: d.ellipse((cx - r, cy - r // 3, cx + r, cy + r // 3), outline=col)
    else: d.ellipse((cx - r, cy - r // 2, cx + r, cy + r // 2), outline=col)
    for vx, vy in ((-1.6, -2.2), (1.6, -2.2), (-0.7, -2.8), (0.9, -2.6)):
        dots(im, [(cx + vx * k, cy + vy * k + 0.45 * k * k)], BLUE['W'] if k < 2 else col)

# ---------- the clip ----------
def build():
    c = Clip('gesture_gecko_water_01', 8.5)
    gx = 44                      # gecko local origin -> mouth lands under x ~ 90
    gy = H - 1 - F               # local floor row F sits on canvas row 51
    bx, by = 86, 22              # bead on the notch underside
    for i in range(c.n):
        im = c.frame()
        # underside wet spot once the first bead starts (frames 22+); second bead at 66+
        if 2 <= i <= 5:
            c.blit(im, S(PADS, 'd'), 70, 50); c.blit(im, S(PADS, 'd'), 78, 50)
        if 6 <= i <= 17:          # haul up over the ledge: rises from below, clipped by the floor
            t = ease((i - 6) / 11); dy = round(16 * (1 - t))
            spr, mx, my = gecko('d', 'crawl', eye='half', mouth='tongue', tl=('drag', 1, 0, 0))
            c.blit(im, spr, gx + mx, gy + my + dy)
            if i <= 12: c.blit(im, S(PADS, 'd'), 70, 50); c.blit(im, S(PADS, 'd'), 78, 50)
        if 18 <= i <= 41:         # collapsed flat; tail lands last; heat shimmer; tongue out
            tl = ('curl', 0.35, 0.0) if i <= 19 else ('drag', 1, 0)
            spr, mx, my = gecko('d', 'flat', eye='closed', mouth='tongue', tl=tl)
            c.blit(im, spr, gx + mx, gy + my); shadow(im, gx + 4, 48)
            if i == 18: puff(im, gx + 26, H - 1, 0.15); puff(im, gx + 44, H - 1, 0.1)
            if i == 21: puff(im, gx + 8, H - 1, 0.2)
        if 4 <= i <= 34:          # heat shimmer over the head
            hx = gx + 36
            for k in range(3):
                sy = 34 - ((i + k * 2) % 6) - (2 if i < 18 else 0)
                dots(im, [(hx + 2 + k * 4 + ((i // 2 + k) % 2), sy)], (140, 110, 96))
        if 42 <= i <= 53:         # eye opens, tracks the bead; pushes up onto front legs
            eye = 'half' if i <= 43 else 'up'
            rise = round(7 * ease((i - 46) / 4)) if i >= 46 else 0
            pose = 'up' if rise > 0 else 'flat'
            spr, mx, my = gecko('d', pose, eye=eye, mouth='closed', rise=rise, tl=('drag', 1, 0))
            c.blit(im, spr, gx + mx, gy + my); shadow(im, gx + 4, 48)
            if i == 47: puff(im, gx + 34, H - 1, 0.2)
        if 54 <= i <= 61:         # bead falls, mouth opens, splash, tint sweep head -> tail
            mouth = 'open' if 55 <= i <= 60 else 'closed'
            dip = 1 if i in (60, 61) else 0
            eye = 'shiny' if i >= 60 else 'up'
            crest = 'up' if i >= 60 else 'flat'
            kw = dict(pose='up', eye=eye, mouth=mouth, rise=7, tl=('drag', 1, 0), crest=crest)
            if i < 59: spr, mx, my = gecko('d', **kw)
            else:
                spr, mx, my = gecko_sweep({59: 40, 60: 24, 61: 0}[i], **kw)
            c.blit(im, spr, gx + mx, gy + my + dip); shadow(im, gx + 4, 48)
            splash(im, gx + 45, 43, i - 58)
        if 62 <= i <= 94:         # green, standing, second bead; look to viewer; walk off
            curl = {62: 1.3, 63: 0.8, 64: 1.1}.get(i, 1.0)
            if i <= 85:
                face = 'front' if 72 <= i <= 81 else 'side'
                eye = 'closed' if i in (77, 78) else ('up' if (66 <= i <= 71 or 82 <= i <= 85) else 'shiny')
                if face == 'front': eye = 'closed' if i in (77, 78) else 'open'
                spr, mx, my = gecko('g', 'stand', eye=eye, face=face, tl=('curl', curl, 0.0), crest='up')
                y = gy + my + bob(i, 16, 1) - (2 if i == 62 else 0)
                c.blit(im, spr, gx + mx, y); shadow(im, gx + 6, 46)
                if i == 62: puff(im, gx + 20, H - 1, 0.1); puff(im, gx + 36, H - 1, 0.1)
            else:
                wx = gx + 6 * (i - 85)
                spr, mx, my = gecko('g', 'stand', eye='shiny', step=(i // 2) % 2, tl=('wave', 1.0, i * 1.1), crest='up')
                c.blit(im, spr, wx + mx, gy + my - bob(i, 4, 1)); shadow(im, wx + 6, 46)
                if i == 86: puff(im, gx + 10, H - 1, 0.1)
        if 95 <= i <= 98:         # slips over the ledge
            wx = gx + 54 + 3 * (i - 94); dy = [3, 8, 15, 24][i - 95]
            spr, mx, my = gecko('g', 'flat', eye='open', tl=('wave', 1.0, i * 1.1), crest='up')
            c.blit(im, spr, wx + mx, gy + my + dy)
            if i == 95: puff(im, wx + 40, H - 1, 0.2)
        # water
        bead(im, bx, by, i, 24, 36) if i <= 53 else None
        fall(im, bx, by, 41, i, 54, 5)
        if 66 <= i <= 94: bead(im, bx, by, i, 66, 76)
        fall(im, bx, by, 48, i, 95, 4)
        if i <= 100: splash(im, bx, 50, i - 98, floor=True)
    return c
