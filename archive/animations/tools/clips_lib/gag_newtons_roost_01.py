"""Newton's Roost — five bats asleep under the notch. One wakes, falls, flaps back too hard and thumps the row;
the impulse skips the three sleepers and only the far bat swings — a Newton's cradle. ~24 px bats (big one 27),
4-tone fur + membrane ramps, amber eye ring + glint, feet-pivot swings with one-frame ear lag, single rim outline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'
F = ramp((112, 92, 152))            # fur: shadow, base, light, highlight
M = ramp((74, 56, 106))             # wing membrane
PAL2 = {'D': F[0], 'f': F[1], 'l': F[2], 'h': F[3],
        'M': M[0], 'm': M[1], 'v': M[2], 'V': M[3],
        'e': (214, 132, 156), 'E': (150, 82, 108),          # ear / nose pink + shadow
        'c': (196, 186, 206),                                 # claws
        'w': (248, 246, 250), 'W': (255, 255, 255), 'b': (22, 18, 30),
        'a': (232, 170, 70), 'A': (168, 110, 40),             # amber iris ring + shadow
        'r': (140, 44, 70), 'R': (92, 26, 46)}                # mouth
S = lambda rows: sprite(rows, PAL2)
RIM = (98, 88, 132)

LEGS = S("""
c.....c
.f...f.
.Df.fD.
""")
BODY_FOLD = S("""
....hlfffD.....
..VvvlfffDmM...
.VvvvlfffDmmM..
VvvvvlfffDmmmM.
VvvvMlfffDmMmM.
VvvMvlfffDMmmM.
.vvMvlfffDmMmM.
.vMvvlfffDmmMM.
.vMvvhlffDmMM..
..MvvhlfDmMM...
..MvvhlfDMM....
...MvhlfDM.....
....MhlfM......
""")
TORSO = S("""
..hlfffD.
.hlffffDD
.hlffffDD
hlfffffDD
hlfffffDD
hlfDfffDD
hlfffffDD
.hlffDfDD
.hlffffD.
.hlffffD.
..hlffD..
..hlffD..
...hlfD..
""")
WING = {  # left wing, three poses; 'a' = shoulder pixel (x, y) inside the sprite
    'open': (S("""
..........VVVv
.....VVvvvvvvm
..VVvvvMvvvMvm
VvvvMvvvvMvvmm
vvMvvvvMvvvMmm
.MvvvMvvvvMmm.
..MMvMmmmMmm..
....MMmmMM....
"""), (13, 0)),
    'up': (S("""
Vv............
Vvvv..........
vvvvvv........
MvvvvvvV......
.MvvvvvvvVV...
..MvvMvvvvvvVv
...MMvvMvvvvvm
.....MMMmmMmmm
"""), (13, 7)),
    'down': (S("""
.........VVVvv
......VVvvvvmm
....VvvvMvvmm.
..VvvvMvvvMm..
.vvvMvvvMmm...
.vMvvvMmm.....
mMvvMmm.......
Mmmm..........
"""), (13, 0)),
}
HEAD = S("""
...hlfffD..
..hlffffffD
.hlfffffffD
.hlfffffffD
.hlfffffffD
.hlfffffffD
..hlfffffD.
...hlfffD..
""")
NOSE = S("""
eE
""")
EAR_L = S("""
.lff
feee
feeD
feeD
.feD
.fD.
.D..
""")
EAR_R = S("""
ffD.
EEEf
DEEf
DEEf
DEf.
.Df.
..D.
""")
EAR_L_FLICK = S("""
.lff
feeef
feeD.
.D...
""")
EAR_R_FLICK = S("""
.ffD
fEEE
.DEf
...D
""")
EYES = {  # 4 wide; pupil 2x2 with a 1-px glint, amber iris ring
    'closed': S("bbbb"),
    'half':   S("bbbb\naWba\nabba"),
    'open':   S("waaw\naWba\nabba\n.ww."),
    'wide':   S(".ww.\nwWbw\nwbbw\n.ww."),
    'left':   S("aaww\nWbaw\nbbaw\n.ww."),          # pupil toward the viewer's left (down the row)
    'up':     S("wWbw\nwbbw\naaaa\n.ww."),          # innocent: pupils toward the ceiling
}
MOUTH = {
    'yawn1': S("rr\nRR"),
    'yawn2': S("rrrr\nrbbr\nRwwR"),                 # fangs on the upper jaw, which hangs at the bottom
    'yawn3': S(".rr.\nrbbr\n.RR."),
    'whistle': S("hh.bb.hh\nhh....hh"),             # puffed cheeks either side of a tiny 'o'
}

def taller(spr, n):
    """Big bat: stretch the middle rows of a sprite by n px (clean pixel duplication)."""
    w, h = spr.size; mid = h // 2
    out = Image.new('RGBA', (w, h + n), (0, 0, 0, 0))
    out.paste(spr.crop((0, 0, w, mid)), (0, 0))
    for k in range(n): out.paste(spr.crop((0, mid, w, mid + 1)), (0, mid + k))
    out.paste(spr.crop((0, mid, w, h)), (0, mid + n)); return out

def rot(spr, px, py, ang):
    """Rotate about local pivot (px, py) on a square canvas; returns (canvas, dx, dy) with dx/dy relative to the pivot."""
    s = 2 * max(abs(px), abs(spr.width - px), abs(py), abs(spr.height - py)) + 6; c = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    c.paste(spr, (s // 2 - px, s // 2 - py), spr)
    if ang: c = c.rotate(ang, resample=Image.NEAREST)
    return c, -s // 2, -s // 2

def bat(eyes='closed', mouth=None, wl='fold', wr='fold', ear_l=0, ear_r=0, big=0, squash=0, ang=0, ear_ang=None):
    """Hanging bat. wl/wr: 'fold' | 'open' | 'up' | 'down'. Returns (sprite, dx, dy) relative to the feet pivot at the notch underside."""
    ear_ang = ang if ear_ang is None else ear_ang
    by0 = 3 - squash; hy = by0 + 12 + big
    if wl == 'fold' and wr == 'fold': parts = [(taller(BODY_FOLD, big) if big else BODY_FOLD, 1, by0)]
    else:
        parts = [(taller(TORSO, big) if big else TORSO, 4, by0)]
        for side, pose in (('l', wl), ('r', wr)):
            w, (ax, ay) = WING[pose if pose != 'fold' else 'open']
            if side == 'r': w = hflip(w); ax = w.width - 1 - ax
            parts.append((w, (4 if side == 'l' else 12) - ax, by0 + 1 - ay))
    parts += [(HEAD, 3, hy), (NOSE, 8, hy + 2)]
    ey = EYES[eyes]; parts += [(ey, 4, hy + 3), (ey, 9, hy + 3)]
    if mouth: m = MOUTH[mouth]; parts.append((m, 8 - m.width // 2 + (1 if m.width % 2 else 0), hy + 1 - (1 if mouth == 'whistle' else 0)))
    body, bx, by = assemble(parts + [(LEGS, 5, 0)])
    ears = [(EAR_L_FLICK if ear_l else EAR_L, 0, hy + 5), (EAR_R_FLICK if ear_r else EAR_R, 13, hy + 5)]
    ear, ex, eyy = assemble(ears)
    # pivot = feet contact, local (8, 0); rotate body and ears (lagged) about it, then outline once
    b, bdx, bdy = rot(body, 8 - bx, 0 - by, ang); e, edx, edy = rot(ear, 8 - ex, 0 - eyy, ear_ang)
    spr, mx, my = assemble([(b, bdx, bdy), (e, edx, edy)])
    return outline(spr, RIM), mx - 1, my - 1

def swing(i, i0, i1, amp):
    """0 -> amp -> 0 across frames i0..i1 with a sine ease (pendulum)."""
    if not i0 <= i <= i1: return 0
    return amp * math.sin(math.pi * (i - i0) / (i1 - i0))

XS = [45, 67, 89, 111, 133]          # feet x of bats 1..5 along the notch underside
FEET_Y = NOTCH_B + 1                 # first visible row
TWITCH = {1: (7, 30, 75, 104), 2: (15, 61), 3: (12, 52, 99), 4: (18, 44, 91)}   # ear-twitch start frames, sleepers

def build():
    c = Clip('gag_newtons_roost_01', 10.0)
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= c.n - 1: continue
        for k in range(5):
            x = XS[k]; big = 2 if k == 4 else 0
            kw = dict(big=big, squash=bob(i + k * 5, 26, 1))
            y = FEET_Y; ang = 0; ear_ang = None
            # ---- entrance: lower out of the notch, staggered
            t_in = (i - 1 - k) / 6
            if t_in < 1: y = FEET_Y - 28 * (1 - ease(max(0, t_in)))
            # ---- exit: eyes close in sequence, then drop and flap up into the notch one by one
            t_out = i - (103, 105, 108, 110, 113)[k]
            if k == 4 and 110 <= i <= 112: kw['ear_r'] = 30
            if k == 4 and 102 <= i: kw['eyes'] = 'closed'
            if t_out >= 0:
                if t_out < 2: y = FEET_Y + 2 * t_out; kw.update(wl='down', wr='down')
                else: y = FEET_Y + 4 - 10 * (t_out - 1); kw.update(wl='up' if t_out % 2 else 'down', wr='up' if t_out % 2 else 'down')
                if y < FEET_Y - 30: continue
            # ---- sleepers' ear twitches
            if k in TWITCH:
                for t0 in TWITCH[k]:
                    if t0 <= i < t0 + 3: kw['ear_l' if k % 2 else 'ear_r'] = 28 if (i - t0) != 1 else 40
            if k == 1 and 43 <= i <= 47: kw['ear_l'] = 45 if i < 46 else 22      # clipped by bat 1's wing
            # ---- bat 1: the waker
            if k == 0:
                if 22 <= i < 24: kw['eyes'] = 'half'
                elif 24 <= i < 33: kw['eyes'] = 'open'
                elif 33 <= i < 41:
                    kw['eyes'] = 'half'; kw['mouth'] = 'yawn1' if i < 35 or i >= 39 else 'yawn2'
                    if i >= 37 and i < 39: kw['mouth'] = 'yawn3'
                elif 41 <= i < 50:
                    kw['eyes'] = 'open'; kw['wr'] = 'open' if 41 <= i < 48 else 'fold'
                elif 50 <= i < 64:
                    drop = [0, 1, 2, 4, 6, 6, 5, 3, 1, -1, -2, -2, -1, 0][i - 50]
                    y = FEET_Y + drop; kw['eyes'] = 'open' if i < 52 else 'wide'
                    if i < 54: kw.update(wl='open', wr='open')
                    else:
                        kw.update(wl='up' if i % 2 else 'down', wr='up' if i % 2 else 'down')
                        x = XS[0] + [0, 1, 3, 5, 8, 10, 12, 12, 7, 3][i - 54]
                    if 54 <= i < 61:                                   # motion streaks under the beating wings
                        for sx in (x - 13, x - 12, x + 12, x + 13):
                            dots(im, [(sx, y + 15 + j + (i % 2) * 3) for j in range(4)], M[3])
                elif 64 <= i < 68: kw['eyes'] = 'wide'; kw['squash'] = 1 if i % 2 else 0
                elif i < 84: kw['eyes'] = 'wide'
                elif i < 100: kw['eyes'] = 'up'; kw['mouth'] = 'whistle'
                ang = -swing(i, 74, 84, 40) - swing(i, 92, 98, 16)
            # ---- bat 5: the far end of the cradle
            if k == 4:
                ang = swing(i, 64, 74, 40) + swing(i, 84, 92, 20)
                if 86 <= i < 90: kw['eyes'] = 'half'
                elif 90 <= i < 102: kw['eyes'] = 'left'
                if 64 <= i < 71:                                       # dust motes shaken off the underside
                    j = i - 64
                    dots(im, [(x - 9 + 3 * q, FEET_Y + j * (1 + q % 2) + (q * 7) % 3) for q in range(6)], (120, 112, 128))
            if ang or i in (75, 85, 93, 99):
                # ears lag one frame behind the body
                pa = (-swing(i - 1, 74, 84, 40) - swing(i - 1, 92, 98, 16)) if k == 0 else (swing(i - 1, 64, 74, 40) + swing(i - 1, 84, 92, 20))
                ear_ang = pa
            if k == 0 and 100 <= i: kw['eyes'] = 'closed'; kw.pop('mouth', None)
            spr, dx, dy = bat(ang=ang, ear_ang=ear_ang, **kw)
            c.blit(im, spr, x + dx, y + dy)
            if t_out >= 2 or (k == 0 and 50 <= i < 62): puff(im, x, FEET_Y + 2, 0.4 if t_out >= 2 else (i - 50) / 12, col=(90, 84, 110))
        if 60 <= i < 64: burst(im, XS[1] - 9, FEET_Y + 10, i - 60, n=8, speed=1.5, life=4, cols=((240, 232, 250), (200, 180, 230)))   # the thump
    return c
