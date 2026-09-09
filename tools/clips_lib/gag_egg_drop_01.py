"""Egg Drop — the notch is a birdhouse and things keep falling out of it. The second egg isn't hers."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

HEN, COMB, BEAK = ramp((228, 222, 206)), ramp((214, 58, 62)), ramp((236, 168, 58))
EGG1, EGG2 = ramp((242, 234, 208)), ramp((196, 218, 176))       # cream / pale green (not hers)
CHK, CRC = ramp((246, 204, 72)), ramp((92, 168, 82))
MYPAL = {
    'S': HEN[0], 'c': HEN[1], 'l': HEN[2], 'h': HEN[3], 'd': (168, 150, 130),
    'R': COMB[0], 'r': COMB[1], 'q': COMB[2],
    'N': BEAK[0], 'n': BEAK[1], 'm': BEAK[2],
    'o': (206, 124, 44), 'w': (250, 250, 246), 'b': (26, 22, 34), 'W': (255, 255, 255),
    'E': EGG1[0], 'e': EGG1[1], 'f': EGG1[2], 'F': EGG1[3],
    '1': EGG2[0], '2': EGG2[1], '3': EGG2[2], '4': EGG2[3], 'k': (96, 108, 72),
    'x': (58, 48, 44),
    'Y': CHK[0], 'y': CHK[1], 'u': CHK[2], 'U': CHK[3],
    'G': CRC[0], 'g': CRC[1], 'v': CRC[2], 'V': CRC[3], 'p': (196, 214, 132), 'z': (236, 222, 120),
}
S = lambda rows: sprite(rows, MYPAL)
OUT_HEN, OUT_EGG, OUT_CHK, OUT_CRC = (96, 84, 104), (104, 92, 84), (124, 96, 52), (60, 104, 72)

# ---------- egg ----------
EGG_ROWS = """
....ffff....
...fFFfff...
..fFFfffee..
..fFffffee..
.fFfffffeee.
.fffffffeeE.
fffffffeeeeE
ffffffeeeeeE
ffffffeeeeEE
fffffeeeeeEE
ffffeeeeeEEE
fffeeeeeEEEE
.ffeeeeEEEE.
..eeeeEEEE..
....EEEE....
"""
EGG_SPR = {1: S(EGG_ROWS), 2: S(EGG_ROWS.translate(str.maketrans('EefF', '1234')))}
SPECK = S("""
............
............
.....k......
..k.........
.......k....
....k.......
.........k..
..k.....k...
.....k......
.........k..
...k........
......k.....
........k...
............
............
""")
CRACK = {1: S("""
............
............
............
............
......x.....
.....x......
......x.....
.....xx.....
....x.......
.....x......
............
"""), 2: S("""
............
............
......x.....
.....x.x....
....x.x.....
.....x......
....x.xx....
...x.x..x...
....x.......
...x.x......
....x.......
.....x......
""")}
HAT_ROWS = """
...ffFff...
..ffffffe..
.fffffeeeE.
fffeeeeEEEE
f.fe.eE.E.E
"""
HAT = {1: S(HAT_ROWS), 2: S(HAT_ROWS.translate(str.maketrans('EefF', '1234')))}

# ---------- hen (drawn upside-down: neck at the top, comb hanging at the bottom) ----------
HEAD_SIDE = S("""
......hlllllS.........
......hlllllcS........
......hllllllcS.......
.....hlllllllccS......
....hllllllccccS......
...hlllllccccccc......
...hllllcccccccc......
..hlllllccccccccc.....
..hllllccccccccccc....
..lllllcccccccccccc...
..lllllcccccccccccc...
..lllllcccccccccccc...
..llllcccccccccccccS..
..llllcccccccccccccS..
..lllccccccccccccccS..
..lllcccccccccccccS...
..llccccccccccccccS...
..llcccccccccccccS....
..lccccccccccccccS....
..ScccccccccccccS.....
...SccccccccccSS......
""")
HEAD_FRONT = S("""
.......hllllS.......
.......hllllcS......
......hlllllcS......
.....hllllllccS.....
....hlllllcccccS....
...hlllllccccccSS...
..hllllllcccccccS...
..hllllcccccccccS...
..hlllcccccccccccS..
..llllcccccccccccS..
..lllccccccccccccS..
..lllccccccccccccS..
..lllccccccccccccS..
..llcccccccccccccS..
..llcccccccccccccS..
..llccccccccccccSS..
..lcccccccccccccS...
..lccccccccccccSS...
..ScccccccccccS.....
...SccccccccSS......
""")
COMB_SPR = S("""
RRRRRRRRRR
RrrrrrrrrR
.rqrrqrrqr
.rq.rq.rq.
.q..q..q..
""")
WATTLE = S("""
.rr
Rrr
.R.
""")
BEAK_SIDE = {0: S("""
.mmnnn.
mnnnnnn
NNNNNN.
.NNN...
"""), 1: S("""
..mnn..
.mnnnn.
mnnnn..
bbb....
NNNNNN.
.NNN...
""")}
BEAK_FRONT = S("""
..mm..
.mnnn.
nnnnnN
NNNNNN
""")
EYE = {
    'narrow': S("""
.oooo.
owwWbo
owwbbo
dddddd
cccccc
.cccc.
"""),
    'egg': S("""
.oooo.
owwwwo
owwwwo
owwWbo
owwbbo
.oooo.
"""),
    'wide': S("""
.oooo.
owwwwo
owWbwo
owbbwo
owwwwo
.oooo.
"""),
    'down': S("""
.oooo.
owwwwo
owwwwo
owWbwo
owbbwo
.oooo.
"""),
    'shut': S("""
......
.cccc.
cccccc
dddddd
cccccc
......
"""),
    'lid': S("""
.oooo.
owwwwo
owWbwo
dddddd
cccccc
.cccc.
"""),
}

# ---------- chick (faces left) ----------
CHK_BODY = S("""
....uuuuu...
..uuUUuuyy..
.uuUuyyyyyy.
.uuyyyyyyyy.
uuyyyyyyyyyy
uyyyyyyyyyyY
yyyyyyyyyyyY
yyyyyyyyyyYY
.yyyyYyyyyYY
.yyyyyYyyYYY
.yyyyyyYYYYY
..yyyyyYYYY.
...YYyYYYY..
""")
CHK_EYE = {'n': S("""
.ww.
wWbw
wbbw
.ww.
"""), 'up': S("""
.Wb.
wbbw
wwww
.ww.
"""), 'shut': S("""
....
....
YYYY
....
""")}
CHK_BEAK = {0: S("""
.nn
nnN
"""), 1: S("""
.nn
b..
.NN
""")}
CHK_LEG = {0: S("""
..n...n.
..n...n.
.nnn.nnn
"""), 1: S("""
.n....n.
..n..n..
nnn..nnn
""")}

# ---------- crocodile (faces left) ----------
CRC_HEAD = {0: S("""
..........vvv.
.........vgggv
.......vvggggg
....vvvvgggggg
.vvvggggggggg.
vgggggggggggg.
GwGwGwGggggg..
.GGGGGGGGGG...
"""), 1: S("""
..........vvv.
.........vgggv
.......vvggggg
....vvvvgggggg
.vvvggggggggg.
vgggggggggggg.
wwwwwwwwggggg.
bbbbbbbbbGGG..
wwwwwwwwGG....
.GGGGGGGG.....
""")}
CRC_BODY = S("""
................Vv
..G..G..G.....vvgg
.vgvvgvvgv...vvggg
vggggggggggvvvgggG
gggggggggggggggGG.
ggggggggggggggGG..
GggggggggggggGG...
GpppppppppGGGG....
.GppppppppG.......
..GGGGGGGG........
""")
CRC_TAIL = {0: S("""
....Vv
..vvgg
.vvggg
vvgggG
gggG..
GG....
"""), 1: S("""
......
......
.vvvVv
vvgggg
gggGG.
GG....
""")}
CRC_EYE = {'n': S("""
.zz.
zbWz
zbzz
.zz.
"""), 'up': S("""
.bW.
zbzz
zzzz
.zz.
"""), 'shut': S("""
....
....
GGGG
....
""")}
CRC_LEG = {0: S("""
gG.
gG.
GGG
"""), 1: S("""
.gG
.gG
GGG
""")}
CRC_ARM = {0: S("""
gG
gG
GG
"""), 1: S("""
.vv
gg.
G..
""")}

# ---------- assembly ----------
def finish(spr, mx, my, col, sx=1.0, sy=1.0):
    """Optionally squash/stretch (bottom-centre anchored), then rim-outline once. Returns (sprite, dx, dy)."""
    if (sx, sy) != (1.0, 1.0):
        w, h = spr.size; nw, nh = max(1, round(w * sx)), max(1, round(h * sy))
        spr = spr.resize((nw, nh), Image.NEAREST); mx += (w - nw) // 2; my += h - nh
    return outline(spr, col), mx - 1, my - 1

def shear(spr, k):
    """Lean the sprite: rows slide sideways by k px per row from the middle (egg wobble)."""
    w, h = spr.size; out = Image.new('RGBA', (w + 4, h), (0, 0, 0, 0))
    for y in range(h):
        row = spr.crop((0, y, w, y + 1)); out.paste(row, (2 + round(k * (h / 2 - y)), y), row)
    return out

def egg(kind=1, crack=0, k=0.0, sx=1.0, sy=1.0):
    parts = [(EGG_SPR[kind], 0, 0)]
    if kind == 2: parts.append((SPECK, 0, 0))
    if crack: parts.append((CRACK[crack], 0, 0))
    spr, mx, my = assemble(parts)
    if k: spr = shear(spr, k); mx -= 2
    return finish(spr, mx, my, OUT_EGG, sx, sy)

def hen(view='side', eye='narrow', beak=0, comb=(0, 0)):
    """Upside-down hen head hanging from the notch. Origin = top-left of the head block (neck at the top)."""
    if view == 'side':
        parts = [(HEAD_SIDE, 0, 0), (BEAK_SIDE[beak], 16, 7 - (2 if beak else 0)), (WATTLE, 15, 4),
                 (EYE[eye], 5, 11), (COMB_SPR, 4 + comb[0], 21 + comb[1])]
    else:
        parts = [(HEAD_FRONT, 0, 0), (BEAK_FRONT, 7, 5), (WATTLE, 9, 2),
                 (EYE[eye], 3, 11), (EYE[eye], 11, 11), (COMB_SPR, 4 + comb[0], 20 + comb[1])]
    spr, mx, my = assemble(parts)
    return finish(spr, mx, my, OUT_HEN)

def chick(eye='n', beak=0, leg=0, hat=True, sx=1.0, sy=1.0, hang=False):
    """Origin = top-left of the body block; feet at the bottom."""
    parts = [(CHK_BODY, 0, 0), (CHK_EYE[eye], 2, 3), (CHK_BEAK[beak], -2, 6 - beak), (CHK_LEG[leg], 2, 13)]
    if hat: parts.append((HAT[1], 0, -3))
    spr, mx, my = assemble(parts)
    return finish(spr, mx, my, OUT_CHK, sx, sy)

def croc(head=0, eye='n', leg=0, tail=0, arm=0, hat=True, sx=1.0, sy=1.0, face='left'):
    """Origin = top-left of the body block; feet at the bottom."""
    parts = [(CRC_TAIL[tail], 23, 0), (CRC_BODY, 11, 0), (CRC_HEAD[head], 0, 2), (CRC_EYE[eye], 9, 3),
             (CRC_LEG[leg], 14, 10), (CRC_LEG[1 - leg], 22, 10), (CRC_ARM[arm], 13 if arm == 0 else 12, 8 if arm == 0 else 6)]
    if hat: parts.append((HAT[2], 8, -2))
    spr, mx, my = assemble(parts)
    spr, mx, my = finish(spr, mx, my, OUT_CRC, sx, sy)
    if face == 'right': spr = hflip(spr)
    return spr, mx, my

# ---------- timeline ----------
EX = 116                     # egg column (left edge); everything happens under the notch's right half
EY = H - 15                  # egg resting top row (37)
HX, HY = 92, NOTCH_B - 3     # hen head hangs left of the egg, neck buried 3 rows into the notch
HIDE = -34                   # head fully inside the notch
EGG_COLS = ((250, 244, 220), (222, 212, 184), (255, 250, 236), (236, 226, 200))
EGG2_COLS = ((214, 232, 196), (180, 206, 160), (236, 246, 220), (200, 220, 180))

def lerp(a, b, t): return a + (b - a) * t

def egg_beats(im, c, i, t0, kind):
    """Drop -> squash -> hop -> wobble -> rest. t0 = first frame the egg is visible. Returns True while the egg is drawn."""
    j = i - t0
    if j < 0: return False
    if j <= 6:                                          # gravity fall out of the notch
        y = 5 + (EY - 5) * (j / 6) ** 2; spr, dx, dy = egg(kind); c.blit(im, spr, EX + dx, y + dy); return True
    if j <= 8:                                          # squash on impact
        spr, dx, dy = egg(kind, sx=1.25, sy=0.8); c.blit(im, spr, EX + dx, EY + dy)
    elif j <= 10:                                       # rebound hop, stretched
        spr, dx, dy = egg(kind, sx=0.85, sy=1.2); c.blit(im, spr, EX + dx, EY + dy - (3 if j == 9 else 4))
    elif j == 11:
        spr, dx, dy = egg(kind); c.blit(im, spr, EX + dx, EY + dy - 2)
    elif j == 12:
        spr, dx, dy = egg(kind, sx=1.12, sy=0.9); c.blit(im, spr, EX + dx, EY + dy)
    elif j <= 20:                                       # wobble: decaying lean
        k = (0.3, 0.3, -0.3, -0.3, 0.2, 0.2, -0.12, -0.12)[j - 13]
        spr, dx, dy = egg(kind, k=k); c.blit(im, spr, EX + dx, EY + dy)
    else:
        spr, dx, dy = egg(kind); c.blit(im, spr, EX + dx, EY + dy)
    if 7 <= j <= 10: puff(im, EX + 6, H - 1, (j - 7) / 3)
    shadow(im, EX - 1, 14)
    return True

def cracked_egg(im, c, i, t0, kind):
    """t0 = first crack frame: crack1 x4 (jitter last 2), crack2 x2. Returns True while drawn."""
    j = i - t0
    if j < 0 or j > 5: return False
    spr, dx, dy = egg(kind, crack=1 if j < 4 else 2)
    c.blit(im, spr, EX + dx + (j % 2 if j >= 2 else 0), EY + dy); shadow(im, EX - 1, 14); return True

def build():
    c = Clip('gag_egg_drop_01', 12.0)
    CX, CY = EX, H - 16                                 # chick origin (feet on the ledge)
    RX, RY = EX - 2, H - 13                             # croc origin
    for i in range(c.n):
        im = c.frame()
        # ===== A: egg 1 (frames 1-23), cracks 24-29, pops 30 =====
        if i < 24: egg_beats(im, c, i, 1, 1)
        elif cracked_egg(im, c, i, 24, 1): pass
        # ----- chick 30-52 -----
        if 30 <= i <= 52:
            eye = 'up' if i >= 36 else 'n'; beak = 1 if i in (38, 39, 40, 44, 45, 46) else 0
            sx, sy = ((1.3, 0.7), (0.85, 1.25), (1.0, 1.0))[min(i - 30, 2)]
            leg = 0
            if i <= 47:                                 # on the ledge
                spr, dx, dy = chick(eye, beak, leg, sx=sx, sy=sy)
                c.blit(im, spr, CX + dx, CY + dy + bob(i, 12, 1)); shadow(im, CX, 12)
        if 30 <= i < 44: burst(im, EX + 6, EY + 8, i - 30, n=8, speed=1.3, life=12, cols=EGG_COLS)
        # ----- hen 1: descend 34-40, overshoot 41-42, hold 43-45, anticipate 46-47, lunge 48-49, grab 50-52, haul 53-60 -----
        if 34 <= i <= 60:
            hx, hy, eye, beak, comb = HX, HY, 'narrow', 0, (0, 0)
            if i <= 40: hy = lerp(HIDE, HY + 2, ease((i - 34) / 6)); comb = (0, -1)
            elif i <= 42: hy = HY + (2 if i == 41 else 1)
            elif i <= 45: pass
            elif i <= 47: hy = HY - 2; eye = 'egg'; comb = (0, 1)
            elif i <= 49: hx, hy, beak, eye = HX + (3 if i == 48 else 6), HY + (3 if i == 48 else 5), 1, 'egg'; comb = (-1, -1)
            elif i <= 52: hx, hy, eye = HX + 6, HY + 5, 'egg'
            else:
                t = ((i - 53) / 7) ** 2; hx, hy, eye = HX + 6, lerp(HY + 5, HIDE - 26, t), 'narrow'; comb = (0, 2 if i > 54 else 0)
            spr, dx, dy = hen('side', eye, beak, comb); c.blit(im, spr, hx + dx, hy + dy)
            if i >= 50:                                 # chick dangles from the beak tip, kicking
                leg = (i // 2) % 2
                spr, dx, dy = chick('n', 1 if i >= 52 else 0, leg, sx=0.9, sy=1.15)
                c.blit(im, spr, hx + 22 - 5 + dx, hy + 12 + dy)
        # ===== B: egg 2 drops 63-85, cracks 92-97, pops 98 =====
        if 63 <= i < 92: egg_beats(im, c, i, 63, 2)
        elif cracked_egg(im, c, i, 92, 2): pass
        # ----- hen 2: descend 74-79, overshoot 80-81, stare at egg 82-89, face viewer 90-107, withdraw 108-123 -----
        if 74 <= i <= 123:
            hx, hy, view, eye, comb = HX, HY, 'side', 'narrow', (0, 0)
            if i <= 79: hy = lerp(HIDE, HY + 2, ease((i - 74) / 5)); comb = (0, -1)
            elif i <= 81: hy = HY + (2 if i == 80 else 1)
            elif i <= 89: eye = 'egg' if i >= 85 else 'narrow'
            elif i <= 107:
                view = 'front'
                eye = 'wide'
                if i in (98, 99): eye = 'shut'
                elif i >= 100: eye = 'down' if i < 106 else 'lid'
                if i == 100: hy = HY - 1                # jolt at the hatch
            else:
                t = ((i - 108) / 15) ** 3; view, eye = 'front', 'lid'; hy = lerp(HY, HIDE - 6, t); comb = (0, 1 if i > 116 else 0)
            spr, dx, dy = hen(view, eye, 0, comb); c.blit(im, spr, hx + dx, hy + dy)
        # ----- croc 98-140 -----
        if 98 <= i <= 140:
            sx, sy = ((1.3, 0.7), (0.85, 1.25), (1.0, 1.0))[min(i - 98, 2)]
            eye = 'n' if i < 102 else 'up'
            head, arm, leg, tail, face, rx, ry = 0, 0, 0, 0, 'left', RX, RY
            if i >= 110: head = 1; eye = 'up'
            if 118 <= i <= 123: arm = 1; ry = RY - 1; eye = 'n'; head = 1 if i < 121 else 0
            if i >= 124: eye, head = 'n', 0
            if i >= 126:                                # turn and waddle off right
                face = 'right'; k = i - 126; rx = RX + 5 * k; leg = (k // 2) % 2; tail = (k // 3) % 2
                ry = RY - (k % 2)
                if k == 0: puff(im, RX + 10, H - 1, 0.2)
            if i in (114, 115): eye = 'shut'
            spr, dx, dy = croc(head, eye, leg, tail, arm, sx=sx, sy=sy, face=face)
            c.blit(im, spr, rx + dx, ry + dy); shadow(im, rx + 2, 26)
        if 98 <= i < 112: burst(im, EX + 6, EY + 8, i - 98, n=8, speed=1.3, life=12, cols=EGG2_COLS)
    return c
