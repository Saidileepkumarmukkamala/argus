"""Trapdoor — a hatch in the notch's underside opens, a rope ladder unrolls, a cellar gremlin climbs down
with a lantern, sees the viewer, and flees. Twist: the monster under the notch is scared of you."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

HOOD = ramp((124, 96, 170)); SKIN = ramp((150, 176, 126)); CLOTH = ramp((118, 84, 58))
WOOD = ramp((156, 108, 62)); ROPE = ramp((196, 164, 104))
PAL2 = {'A': HOOD[0], 'a': HOOD[1], 'b': HOOD[2], 'c': HOOD[3],
        'S': SKIN[0], 's': SKIN[1], 't': SKIN[2], 'u': SKIN[3],
        'D': CLOTH[0], 'd': CLOTH[1], 'e': CLOTH[2], 'f': CLOTH[3], 'Z': (58, 40, 34),
        'V': WOOD[0], 'v': WOOD[1], 'x': WOOD[2], 'y': WOOD[3], 'z': (112, 74, 40),
        'R': ROPE[0], 'r': ROPE[1], 'q': ROPE[2], 'Q': ROPE[3],
        'w': (250, 250, 244), 'k': (14, 10, 20), 'i': (206, 222, 92), 'W': (255, 255, 255), 'm': (70, 50, 70),
        'F': (48, 36, 44), 'E': (84, 66, 78),
        'I': (58, 60, 74), 'J': (116, 118, 134), 'g': (255, 214, 120), 'o': (255, 150, 60), 'G': (64, 58, 54), 'O': (96, 72, 60)}
S = lambda rows: sprite(rows, PAL2)
RIM = (64, 54, 88)

# ---------- gremlin parts (local space: hood peak at (0,0); feet row 24; 20 wide) ----------
HOOD_SPR = S("""
.........cc.........
........cbbc........
.......cbbaac.......
......cbbaaaaA......
.....cbba....aaA....
....cbba......aaA...
...cbba........aaA..
..cbba..........aaA.
..cba............aA.
..Aba............aA.
..Aaa............AA.
..AAa............AA.
...AAA..........AAA.
""")
FLAP = S("""
aA
aA
aA
bA
bA
AA
""")
FLAP_OUT = S("""
.aA
.aA
aA.
aA.
bA.
AA.
""")

def face(eyes='centre', wide=False):
    """Face inside the hood: skin + two big eyes. eyes: centre|left|right|shut."""
    base = ["....tttt....", "...tssssss..", "..tsssssssss", "ssssssssssss", "ssssssssssss",
            "ssssssssssss", "ssssssssssss", "sSssssssssSs", ".SSssmmssSS."]
    g = [list(r) for r in base]
    if wide:                                       # full-size eyes, pinprick pupils, mouth open
        eye = ["wwwww", "wiiiw", "wiWiw", "wikiw", "wiiiw", "wwwww"]; y0 = 1
        g[7][5] = g[7][6] = g[8][5] = g[8][6] = 'm' 
    elif eyes == 'shut':
        eye = ["SSSSS", "sssss", "sssss", "sssss"]; y0 = 3
    else:
        sh = {'left': -1, 'right': 1, 'centre': 0}[eyes]; p0 = 1 + sh
        e = [list("wwwww") for _ in range(4)]
        e[1][p0], e[1][p0 + 1], e[2][p0], e[2][p0 + 1] = 'W', 'k', 'k', 'k'
        if p0 + 2 < 5: e[1][p0 + 2] = e[2][p0 + 2] = 'i'
        if p0 - 1 >= 0 and sh > 0: e[1][p0 - 1] = e[2][p0 - 1] = 'i'
        eye = [''.join(r) for r in e]; y0 = 3
    for ex in (0, 7):
        for j, r in enumerate(eye):
            for k, ch in enumerate(r):
                if 0 <= y0 + j < len(g): g[y0 + j][ex + k] = ch
    return S('\n'.join(''.join(r) for r in g))

TUNIC = S("""
..eedddddddD
.edddDdddddD
.eddDddDdddD
.eddDddDddDD
.ZZZZZfZZZZZ
.eddDddDdddD
.eddDddDddDD
.DDDDDDDDDD.
""")
ARM_DOWN = S("""
Ss.
Ss.
Ss.
.Ss
.Ss
.ts
.SS
""")
ARM_OUT = S("""
....ts
...Sss
.SSs..
Ss....
""")
ARM_UP = S("""
tsS
tsS
Ss.
Ss.
Ss.
Ss.
Ss.
""")
LEGS = {
 'stand': S("""
.Ss..Ss.
.Ss..Ss.
.Ss..Ss.
EFF..EFF
"""),
 'a': S("""
.Ss..Ss.
EFF..Ss.
.....Ss.
.....EFF
"""),
 'b': S("""
.Ss..Ss.
.Ss..EFF
.Ss.....
EFF.....
"""),
 'free': S("""
.Ss..Ss....
.Ss...Ss...
.Ss....Ss..
EFF.....EFF
"""),
 'crouch': S("""
.Ss..Ss.
EFF..EFF
"""),
}
LANTERN_ON = S("""
..JJ..
.J..J.
IIIIII
IgggoI
IgooeI
IgggoI
IIIIII
.IIII.
""")
LANTERN_OFF = S("""
..JJ..
.J..J.
IIIIII
IGGGOI
IGOOGI
IGGGGI
IIIIII
.IIII.
""")
LANT_ON = outline(LANTERN_ON, RIM); LANT_OFF = outline(LANTERN_OFF, RIM)

def gremlin(pose='stand', eyes='centre', wide=False, legs=None, flaps='in', crouch=False):
    """Assemble + outline once. Returns (sprite, ox, oy) with (0,0) = hood peak in local space; feet at local y 24."""
    fl = FLAP_OUT if flaps == 'out' else FLAP
    parts = [(face(eyes, wide), 4, 4), (HOOD_SPR, 0, 0), (fl, 1 if flaps == 'out' else 2, 8), (hflip(fl), 17, 8)]
    legs = legs or ('stand' if pose == 'stand' else 'a')
    if crouch:
        parts += [(TUNIC, 4, 14), (LEGS['crouch'], 6, 22)]
    else:
        parts += [(TUNIC, 4, 13), (LEGS[legs], 6, 21)]
    if pose == 'stand':
        parts += [(ARM_DOWN, 2, 13 + crouch), (ARM_OUT, 15, 10 + crouch)]
    else:                                             # hands up on the rails beside the hood
        parts += [(ARM_UP, 1, 7), (hflip(ARM_UP), 16, 7)]
    spr, mx, my = assemble(parts)
    return outline(spr, RIM), mx - 1, my - 1

def ghost(spr, a):
    g = spr.copy(); g.putalpha(spr.split()[3].point(lambda v: int(v * a))); return g

# ---------- hatch door states (24-px plank, hinge at its left end on the underside) ----------
def plank_rows(state):
    if state == 'flat':
        return ["y" * 24, "v" * 5 + "z" + "v" * 9 + "z" + "v" * 8, "V" * 24]
    if state == 'peek':
        return ["V" * 24]
    if state == 'diag':
        return ['.' * k + 'xV' for k in range(17)]
    if state == 'vert':
        return [("xvV" if r not in (5, 12, 19) else "xzV") for r in range(24)]
    if state == 'vert_over':
        return [(".xvV" if r < 12 else "xvV.") for r in range(24)]
    if state == 'crack':
        g = [['.'] * 24 for _ in range(6)]
        for k in range(24):
            j = k // 6; g[j][k] = 'x' if j == 0 else 'v'; g[j + 1][k] = 'V'
        return [''.join(r) for r in g]
    return []
DOOR = {s: outline(S('\n'.join(plank_rows(s))), RIM) for s in ('flat', 'peek', 'diag', 'vert', 'vert_over', 'crack')}

def ladder(L, sway=0.0):
    """Rope ladder sprite, top at the underside; rails 2 px, rungs every 5 rows. L rows long."""
    if L <= 0: return None
    rows = []
    for r in range(L):
        row = ['.'] * 18
        row[0], row[1] = ('q', 'r') if r % 2 == 0 else ('r', 'R')
        row[16], row[17] = ('r', 'R') if r % 2 == 0 else ('R', 'R')
        if r % 5 == 4: row[2:16] = ['q'] * 14
        if r % 5 == 0 and r: row[2:16] = ['R'] * 14
        off = round(sway * r / max(L, 1))
        rows.append('.' * max(0, off + 2) + ''.join(row) + '.' * max(0, 2 - off))
    return outline(S('\n'.join(rows)), RIM)

def glow(im, cx, cy, r=7):
    """Warm lantern light on nearby pixels: black gets a dim halo, colours warm up a little."""
    px = im.load()
    for y in range(max(0, cy - r), min(H, cy + r + 1)):
        for x in range(max(0, cx - r), min(W, cx + r + 1)):
            d = math.hypot(x - cx, y - cy)
            if d > r: continue
            f = (1 - d / r)
            p = px[x, y]
            if p == (0, 0, 0): px[x, y] = (int(96 * f * f), int(66 * f * f), int(22 * f * f))
            else: px[x, y] = tuple(min(255, int(p[k] * (1 - 0.25 * f) + (255, 205, 120)[k] * 0.25 * f)) for k in range(3))

def dust(im, i, i0, x0, x1, n, seed, life=10):
    if not 0 <= i - i0 < life: return
    rng = random.Random(seed); t = i - i0
    for _ in range(n):
        x = rng.randint(x0, x1); d = rng.randint(0, 2); v = 0.4 + rng.random() * 0.6
        if t < d: continue
        k = t - d; y = NOTCH_B + 1 + v * k + 0.09 * k * k
        c = int(150 - 10 * k)
        dots(im, [(x, int(y))], (c, c - 8, c - 14))

def build():
    c = Clip('gag_trapdoor_01', 9.75)
    hx = 82                                  # hatch: hx..hx+23 on the underside; ladder rails hx+5 & hx+19
    lx = hx + 5; gx = hx + 3                 # gremlin local origin so the hands sit on the rails
    dark = 0.0
    for i in range(c.n):
        im = c.frame()
        door = None; L = 0; sway = 0.0; g = None; lamp = None; ghosts = []
        # ---- 0-1 s: shudder, dust, hinge open ----
        if 1 <= i <= 3: dust(im, i, 1, hx + 2, hx + 21, 3, 1)
        if 4 <= i <= 9:
            door = ('peek', (-1, 0, 1, 0, -1, 1)[i - 4], 0); dust(im, i, 4, hx, hx + 23, 5, 2)
        if i == 10: door = ('flat', 0, 0)
        if i == 11: door = ('diag', 0, 0)
        if i == 12: door = ('vert', 0, 0)
        if i == 13: door = ('vert_over', -1, 0)
        if 14 <= i <= 95: door = ('vert', 0, 0)
        if i in (10, 11, 12): dust(im, i, 10, hx, hx + 23, 4, 3)
        # ---- 1-2.5 s: ladder unrolls, hits floor, sways, settles ----
        if 14 <= i <= 21:
            L = int(30 * ease((i - 14) / 6)); sway = 0
            if i == 20: puff(im, lx + 1, H - 1, 0.15); puff(im, lx + 15, H - 1, 0.15)
        if 22 <= i <= 95:
            L = 30
            k = i - 22
            sway = 2.5 * math.sin(k * 1.1) * max(0.0, 1 - k / 9)
        # ---- 2.5-5 s: climb down rung by rung ----
        if 30 <= i <= 53:
            step, ph = divmod(i - 30, 4)
            fy = 21 + 5 * step + (0, 2, 4, 5)[ph]
            legs = ('a', 'a', 'b', 'b')[ph]
            g = dict(pose='climb', legs=legs, flaps='out' if ph in (1, 2) else 'in', fy=fy)
            lamp = ('on', 3.0, 14)
        if i == 54:
            g = dict(pose='stand', fy=51, crouch=True, flaps='out'); puff(im, gx + 6, H - 1, 0.1); puff(im, gx + 16, H - 1, 0.1)
            lamp = ('on', 3.0, 14)
        if 55 <= i <= 63:
            eyes = 'left' if i < 58 else ('right' if i < 61 else 'centre')
            g = dict(pose='stand', fy=51, eyes=eyes, flaps='out' if i == 55 else 'in'); lamp = ('on', 2.0, 16)
        # ---- 5-6 s: freeze; eyes full size; lantern flickers out ----
        if 64 <= i <= 78:
            g = dict(pose='stand', fy=51, wide=i >= 66)
            st = 'on'
            if i in (70, 72, 73): st = 'off'
            if i >= 75: st = 'off'
            lamp = (st, 1.0, 16)
            if i >= 75: dark = min(0.35, dark + 0.12)
        # ---- 6-7.5 s: scramble up at triple speed, ghosts, miss a rung, haul ladder, slam ----
        if 79 <= i <= 80:
            g = dict(pose='stand', fy=51, wide=True, crouch=True, flaps='in'); lamp = ('off', 1.0, 16)
            if i == 80: puff(im, gx + 6, H - 1, 0.1); puff(im, gx + 16, H - 1, 0.1)
        if 81 <= i <= 86:
            k = i - 81
            fy = 51 - 6 * (k + 1)
            legs = 'free' if k == 2 else ('a' if k % 2 else 'b')
            g = dict(pose='climb', legs=legs, wide=True, flaps='out', fy=fy)
            lamp = ('off', 6.0, 6)
            ghosts = [(fy + 6, 0.5), (fy + 12, 0.25)]
            if k == 0: puff(im, gx + 10, H - 1, 0.3)
        if 87 <= i <= 94:
            L = max(0, 30 - 4 * (i - 86)); sway = (-2, 2)[i % 2] * (L / 30)
        if i == 95: door = ('diag', 0, 0)
        if i == 96: door = ('flat', 0, 0)
        if i >= 96: dust(im, i, 96, hx - 3, hx + 26, 14, 7, life=12)
        if i == 97: puff(im, hx, NOTCH_B + 2, 0.2); puff(im, hx + 23, NOTCH_B + 2, 0.2)
        # ---- 7.5-9.75 s: silence; the crack; one eye; closes ----
        eye = None
        if 104 <= i <= 113:
            door = ('crack', 0, 0)
            eye = 'left' if i < 107 else ('right' if i < 110 else 'centre')
        if i == 114: door = ('flat', 0, 0)

        # ---- draw: ladder, door, ghosts, gremlin, lantern ----
        if L > 0:
            ld = ladder(L, sway); c.blit(im, ld, lx - 3, NOTCH_B + 1 - 1)
        if door:
            st, dx, dy = door; c.blit(im, DOOR[st], hx + dx - 1, NOTCH_B + 1 + dy - 1)
        if g:
            fy = g.pop('fy')
            for gy, a in ghosts:
                sp, ox, oy = gremlin(**g); c.blit(im, ghost(sp, a), gx + ox, gy - 24 + oy)
            sp, ox, oy = gremlin(**g); top = fy - 24 - (bob(i, 16, 1) if 55 <= i <= 65 else 0)   # breathe while looking around; rigid in the freeze
            c.blit(im, sp, gx + ox, top + oy)
            if fy == 51 and not ghosts: shadow(im, gx + 2, 16)
            if lamp:
                st, amp, per = lamp
                ldx = round(amp * math.sin(2 * math.pi * i / per)); ldy = abs(ldx) // 2
                if g.get('pose') == 'stand': hx0, hy0 = gx + 20, top + 11 + (1 if g.get('crouch') else 0)
                else: hx0, hy0 = gx + 19, top + 8
                cx, cy = hx0 + ldx, hy0 + 2 - ldy
                dots(im, [(hx0 + round(ldx * t), hy0 + round((2 - ldy) * t)) for t in (0.5, 1.0)], PAL2['J'])
                if st == 'on': glow(im, cx + 3, cy + 4, 8)
                c.blit(im, LANT_ON if st == 'on' else LANT_OFF, cx - 2, cy)
        if dark > 0: tint(im, (10, 20, 60), dark)
        if eye:                                        # drawn after the tint so it stays bright in the dark
            sh = {'left': -1, 'right': 1, 'centre': 0}[eye]; p0 = 2 + sh
            e = [list("wwwwww") for _ in range(4)]
            for r in (0, 3): e[r][p0], e[r][p0 + 1] = 'i', 'i'
            for r in (1, 2): e[r][p0 - 1], e[r][p0 + 2] = 'i', 'i'
            e[1][p0], e[1][p0 + 1], e[2][p0], e[2][p0 + 1] = 'W', 'k', 'k', 'k'
            c.blit(im, outline(S('\n'.join(''.join(r) for r in e)), RIM), hx + 17, NOTCH_B + 1 - 1)
    return c
