"""Tether — Juno (astronaut, lead, 30 px) & Bip (rover, 26x15 + whip antenna).
She clips her tether to Bip's antenna and floats up into the notch. Bip waits, gets tugged, reverses hard —
Juno drops out of the notch upside down. Beat. Then whatever is up there hauls Bip in, and Juno follows."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- Juno palette: suit / gold visor rim / backpack / orange accents, each a 4-tone ramp ----------
SU = ramp((200, 204, 214)); GO = ramp((222, 168, 60)); BK = ramp((116, 124, 148)); OR = ramp((226, 112, 52))
JP = {'A': SU[0], 'a': SU[1], 'e': SU[2], 'E': SU[3],
      'Y': GO[0], 'y': GO[1], 'q': GO[2], 'Q': GO[3],
      'K': BK[0], 'k': BK[1], 'm': BK[2], 'M': BK[3],
      'O': OR[0], 'o': OR[1], 'n': OR[2], 'N': OR[3],
      'v': (26, 30, 56), 'V': (52, 64, 110), 'c': (110, 150, 200),          # visor glass, reflection, streak
      'z': (238, 190, 160), 'Z': (196, 140, 118), 'h': (74, 44, 46),        # skin, skin shadow, hair
      'w': (250, 250, 245), 'W': (255, 255, 255), 'b': (22, 20, 30),
      's': (204, 204, 214), 'S': (140, 140, 156), 'r': (236, 70, 70), 'g': (110, 220, 110)}
J = lambda rows: sprite(rows, JP)
JRIM = (84, 80, 118)

HELMET = J("""
.....eEEEe....
...eeEEEeeaA..
..eeEEeeaaaaA.
.eeeaYYYYYYYYA
.eeaYvvvVvccYA
.eaaYvhhhhhcYA
.eaaYvhzzzzcYA
.aaaYvzWbzWbYA
.aaAYvzwbzwbYA
.aaAYvzzzZzzYA
..aAYYYYYYYYYA
...AsSSSSSSSA.
""")
HELMET_BLINK = J("""
.....eEEEe....
...eeEEEeeaA..
..eeEEeeaaaaA.
.eeeaYYYYYYYYA
.eeaYvvvVvccYA
.eaaYvhhhhhcYA
.eaaYvhzzzzcYA
.aaaYvzzzzzzYA
.aaAYvzZZzZZYA
.aaAYvzzzZzzYA
..aAYYYYYYYYYA
...AsSSSSSSSA.
""")
TORSO = J("""
.KkaeeeeeaaA..
KkmaeeeeaaaaA.
KkmaeeaKKKKaA.
KkmaeeaKrgKaA.
KkmaaeaKKKKaA.
KkmAaaaaaaaAA.
KKmAaaaaaaAA..
.KAoooooooooA.
..AAaaaaaaAs..
...AaaaaaAA...
""")
ARM_DOWN = J("""
eaA
eaA
eaA
.aA
.aA
.oO
.oO
""")
ARM_BACK = J("""
AaA
AaA
Aa.
Aa.
oO.
oO.
""")
ARM_REACH = J("""
......nO
.....aoO
....aaO.
...aaA..
..aaA...
.eaA....
eaA.....
""")
ARM_UP = J("""
..oO
.aoO
.aA.
eaA.
eaA.
""")
FARM_UP = J("""
Oo.
Oo.
Aa.
Aa.
.Aa
""")
LEGS_STAND = J("""
..AaaA.aaA.
..AaaA.aaA.
.AAaaA.aaA.
.AaaaA.aaA.
.AaaAA.aaA.
.OooO.OooO.
.OoooOOoooO
.OOOOO.OOOO
""")
LEGS_CROUCH = J("""
..AaaA.aaA.
.AAaaAAaaAA
.OooOAOooOA
.OoooOOoooO
.OOOOO.OOOO
""")
LEGS_TUCK = J("""
..AaaAaaA..
.AAaaAaaAA.
.AaaAOAaaO.
.OooOOOooO.
.OoooO.OOO.
.OOOOO.....
""")
LEGS_FLOAT = J("""
..AaaA.....
..AaaA.aaA.
.AAaaA.aaA.
.AaaaA.aaA.
.AaaAA.aaAA
.OooO..OooO
.OoooO.OooO
.OOOOO..OOO
""")

# --- upside-down Juno: drawn directly (not flipped) so the light still comes from the top-left ---
DLEGS = J("""
.nNNNn.NNNn
.noooOnoooO
.nooO.nooO.
.eaaAA.aaA.
.eaaaA.aaA.
.eeaaA.aaA.
..eaaA.aaA.
..AaaA.AaA.
""")
DTORSO = J("""
...eeaaaaAA...
..eaaaaaaaAs..
.KmnooooooooA.
KMmeaaaaaaAA..
KkmeeaaaaaaAA.
KkmaeeaKKKKaA.
KkmaeeaKrgKaA.
KkmaeeaKKKKaA.
KkmaeeeeaaaaA.
.KkAaaaaaaAA..
""")
DHELMET = J("""
...esSSSSSSSA.
..eeYYYYYYYYYA
.eeaYvzzzZzzYA
.eaaYvzWbzWbYA
.eaaYvzbbzbbYA
.aaaYvhzzzzcYA
.aaAYvhhhhhcYA
.aaAYvvvVvccYA
.aaAAYYYYYYYYA
..aaAAAAAAAAA.
...aaAAAAAAA..
.....AAAAA....
""")
DHELMET_BLINK = J("""
...esSSSSSSSA.
..eeYYYYYYYYYA
.eeaYvzzzZzzYA
.eaaYvzzzzzzYA
.eaaYvzZZzZZYA
.aaaYvhzzzzcYA
.aaAYvhhhhhcYA
.aaAYvvvVvccYA
.aaAAYYYYYYYYA
..aaAAAAAAAAA.
...aaAAAAAAA..
.....AAAAA....
""")
DARM_A = J("""
aA..
aA..
.aA.
.aA.
.aA.
..oO
..oO
..OO
""")
DARM_B = J("""
aA...
.aA..
.aaA.
..aA.
...oO
...oO
...OO
""")
DFARM_A = J("""
.AA
.Aa
AA.
Aa.
Aa.
OO.
Oo.
OO.
""")
DFARM_B = J("""
..AA
..Aa
.AA.
.Aa.
AA..
OO..
Oo..
OO..
""")

JUNO_H = 30                       # feet at figure row 30 -> standing blit y = H - 30
JUNO_CLIP = {'stand': (11, 20), 'reach': (11, 20), 'tuck': (11, 20), 'float': (11, 20), 'crouch': (11, 23)}

def juno(pose, blink=False):
    """Assemble + outline once. Returns (sprite, dx, dy) relative to the figure origin (helmet top-left, standing)."""
    head = HELMET_BLINK if blink else HELMET
    if pose == 'stand':   parts = [(TORSO, 0, 12), (head, 0, 0), (LEGS_STAND, 3, 22), (ARM_DOWN, 11, 13)]
    elif pose == 'crouch': parts = [(TORSO, 0, 15), (head, 0, 3), (LEGS_CROUCH, 3, 25), (ARM_BACK, 11, 16)]
    elif pose == 'reach':  parts = [(TORSO, 0, 12), (head, 0, 0), (LEGS_STAND, 3, 22), (ARM_REACH, 11, 7)]
    elif pose == 'tuck':   parts = [(FARM_UP, -1, 8), (TORSO, 0, 12), (head, 0, 0), (LEGS_TUCK, 3, 22), (ARM_UP, 11, 8)]
    else:                  parts = [(FARM_UP, -1, 8), (TORSO, 0, 12), (head, 0, 0), (LEGS_FLOAT, 3, 22), (ARM_UP, 11, 8)]
    spr, mx, my = assemble(parts)
    return outline(spr, JRIM), mx - 1, my - 1

DANGLE_CLIP = (11, 9)             # belt clip on the upside-down figure (figure origin = boot soles top-left)

def juno_dangle(flail=0, blink=False):
    head = DHELMET_BLINK if blink else DHELMET
    farm, near, fx = (DFARM_A, DARM_A, 0) if flail == 0 else (DFARM_B, DARM_B, -1)
    parts = [(farm, fx, 15), (DLEGS, 3, 0), (DTORSO, 0, 8), (head, 0, 18), (near, 11, 15)]
    spr, mx, my = assemble(parts)
    return outline(spr, JRIM), mx - 1, my - 1

# ---------- Bip palette: rust-orange body, dark lens housing, solar cells, one big lens, rubber wheels ----------
BO = ramp((206, 118, 56)); DK = ramp((88, 90, 106))
BP = {'R': BO[0], 'r': BO[1], 'u': BO[2], 'U': BO[3],
      'D': DK[0], 'd': DK[1], 'f': DK[2], 'F': DK[3],
      'c': (60, 110, 170), 'C': (36, 68, 120), 'L': (255, 96, 80),
      'w': (250, 250, 245), 'W': (255, 255, 255), 'b': (18, 18, 26), 'I': (62, 150, 190), 'i': (30, 92, 132),
      'T': (44, 44, 54), 't': (78, 78, 92), 's': (204, 204, 214), 'S': (150, 150, 162)}
B = lambda rows: sprite(rows, BP)
BRIM = (98, 64, 46)

BODY = B("""
...fFFFFFFFFFFFf..........
...fcCcCcCcCcCcf..........
...fCcCcCcCcCcCf..........
.UuuuuuuuuuuuuuuuFFFFFFFFF
UurrrrrrrrrrrrrrrF.......D
UurrrrrrrrrrrRRRRRF.......D
UurrrRRrrrrRuuuRrf.......D
UurrrRLLRrrRuurRrf.......D
UurrrRLLRrrRRRRRrf.......D
UuRrrrRRrrrrrrrrRf.......D
.URRRRRRRRRRRRRRRd.......D
..RRRRRRRRRRRRRRRDDDDDDDDD
""")
LENS = {
 'r': B("""
.WWwww.
WIIIIIw
WIIWbbw
wIIbbbw
wIibbbw
wIiiiIw
.wwwww.
"""),
 'cam': B("""
.WWwww.
WIIIIIw
WIWbbIw
wIbbbIw
wibbbiw
wIiiiIw
.wwwww.
"""),
 'up': B("""
.WWwww.
WIIWbbw
WIIbbbw
wIIbbbw
wIiIIiw
wIiiiIw
.wwwww.
""")}
WHEEL_A = B("""
.TTTTT.
TtTTTtT
TTTsTTT
TTsSsTT
TTTsTTT
TtTTTtT
.TTTTT.
""")
WHEEL_B = B("""
.TtTtT.
TTTTTTT
tTTsTTt
TTsSsTT
tTTsTTt
TTTTTTT
.TtTtT.
""")
WHEEL_BLUR = B("""
..TtTtT..
.TtTTTtT.
tTTTsTTTt
TTTsSsTTT
tTTTsTTTt
.TtTTTtT.
..TtTtT..
""")
BIP_H = 15                        # body rows 0-11, wheels rows 8-14 -> grounded blit y = H - 15
ANT_BASE = (1, 3)                 # antenna root on the rear top corner (figure coords)
ANT = (176, 176, 190); BALL = (232, 72, 72); BALL_HI = (255, 170, 160)
TETH = (196, 196, 206); TETH2 = (140, 140, 156)

def bip(spin=0, lens='r', lean=0):
    """spin: 0/1 tread frames, 2 blur. lean: body offset vs wheels (+ = leans back while reversing)."""
    wheel = (WHEEL_A, WHEEL_B, WHEEL_BLUR)[spin]; wx = -1 if spin == 2 else 0
    parts = [(BODY, lean, 0), (LENS[lens], 18 + lean, 4), (wheel, 3 + wx, 8), (wheel, 16 + wx, 8)]
    spr, mx, my = assemble(parts)
    return outline(spr, BRIM), mx - 1, my - 1

def antenna(im, bx, by, lag):
    """Whip antenna from the root (bx, by) up 10 px, tip displaced by `lag` (quadratic = a bending whip). Returns ball pos."""
    pts = [(round(bx + lag * (k / 10) ** 2), by - k) for k in range(11)]
    dots(im, pts, ANT)
    tx, ty = pts[-1]
    dots(im, [(tx, ty - 1), (tx + 1, ty - 1), (tx, ty), (tx + 1, ty)], BALL); dots(im, [(tx, ty - 1)], BALL_HI)
    return tx, ty - 1

def tether(im, p0, p1, sag=0.0):
    """1-px cord between two anchors; sag > 0 lets it hang (quadratic droop)."""
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
    for k in range(n + 1):
        t = k / n
        dots(im, [(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)))], TETH if k % 3 else TETH2)

def ease_in(t):  t = max(0.0, min(1.0, t)); return t * t
def ease_out(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) * (1 - t)

def build():
    c = Clip('gag_tether_juno_bip_01', 10.5)
    BIP_X, JUNO_X = 96, 78
    JY, BY = H - JUNO_H, H - BIP_H                     # grounded blit rows
    NOTCH_PT = (92, NOTCH_B)                           # where both cords vanish into the notch
    prev_bx = None
    for i in range(c.n):
        im = c.frame()
        # ------------------------------------------------------------------ Bip state
        bx, by, spin, lens, lean, lag, dig = BIP_X, BY, 0, 'r', 0, 0.0, 0
        show_bip = True
        if i < 30:                                     # roll in from the left, easing to the park spot
            bx = -34 + (BIP_X + 34) * ease(i / 29)
        elif i < 72:                                   # wait: antenna wiggles, lens to camera at 62
            lag = 1.5 * math.sin(i * 0.7)
            lens = 'cam' if i >= 62 else 'r'
        elif i < 90:                                   # tether snaps taut and tugs him about; he braces, wheels dig in
            lens = 'cam' if i < 78 else 'up'
            if i in (72, 73): bx = BIP_X + 2; lag = 3
            elif i in (75, 76): bx = BIP_X - 2; lag = -3
            elif i >= 77: dig = 1; lag = 2 + (1 if i % 2 else 0)
        elif i < 102:                                  # reverse hard to the left, wheel blur, body leans back
            t = ease((i - 90) / 11)
            bx = BIP_X + (50 - BIP_X) * t; spin = 2 if 1 <= i - 90 <= 10 else 0; lean = 1 if spin == 2 else 0
            lag = 4 if spin == 2 else 2; lens = 'up'; dig = 1 if i < 92 else 0
        elif i < 114:                                  # stopped; watches her dangle
            bx = 50; lens = 'r'; lag = 2 * math.cos((i - 102) * 0.9) * (1 - (i - 102) / 14)
        elif i < 116:                                  # anticipation: cord yanks, he is lifted off his wheels
            bx = 50 + (i - 113); by = BY - 2; lag = 5; lens = 'up'; spin = i % 2
        elif i < 122:                                  # hauled up-right into the notch, wheels spinning
            t = ease_in((i - 115) / 6)
            bx = 53 + (82 - 53) * t; by = (BY - 2) + (-22 - (BY - 2)) * t; spin = 2; lean = 1; lag = 5; lens = 'up'
        else:
            show_bip = False
        vel = 0 if prev_bx is None else bx - prev_bx; prev_bx = bx if show_bip else None
        if i < 30:
            spin = 2 if abs(vel) > 3 else (i // 2) % 2
            lag = max(-4.0, -0.7 * vel)
        # ------------------------------------------------------------------ Juno state
        jx, jy, pose, blink, show_juno, dangle, flail = JUNO_X, JY, 'stand', False, True, False, 0
        sway = 0
        if i < 30:                                     # low-gravity bounds behind Bip: 3 hops of 10 frames
            jx = -62 + (JUNO_X + 62) * ease(i / 29)
            u = (i % 10) / 10; hop = -9 * math.sin(math.pi * u)
            jy = JY + round(hop); pose = 'crouch' if u < 0.15 or u > 0.85 else 'tuck'
        elif i < 34:                                   # land + settle
            pose = 'crouch' if i == 30 else 'stand'
        elif i < 40:                                   # hop and reach for the antenna ball
            u = (i - 34) / 5; jy = JY - round(3 * math.sin(math.pi * u)); pose = 'reach'
        elif i < 44:
            pose = 'stand'
        elif i < 48:                                   # anticipation: crouch
            pose = 'crouch'
        elif i < 60:                                   # push off and float up into the notch
            t = ease_out((i - 48) / 11)
            jy = JY + (-16 - JY) * t; pose = 'float'; jx = JUNO_X + round(2 * t)
        elif i < 96:
            show_juno = False
        elif i < 114:                                  # drops out of the notch upside down; dangles 2 px above the floor
            dangle = True
            if i < 104:
                t = ease_in((i - 96) / 7); jy = -34 + (22 - -34) * t          # overshoot to 22
            elif i < 107: jy = 21
            else: jy = 20
            jx = 104 + (round(math.sin((i - 100) * 0.8)) if i >= 100 else 0)
            flail = ((i - 96) // 3) % 2; blink = i in (109, 110)
        elif i < 124:                                  # hauled up feet-first after Bip
            dangle = True
            t = ease_in((i - 114) / 8); jy = 20 + (-36 - 20) * t; jx = 104 + round(4 * t)
            flail = (i // 2) % 2
        else:
            show_juno = False
        if show_juno and i >= 30 and not dangle and pose == 'stand': jy += bob(i, 24, 1)
        # ------------------------------------------------------------------ anchors + cords (cords go under the characters)
        ant_root = (round(bx) + ANT_BASE[0], round(by) + ANT_BASE[1] + dig)
        ball = (ant_root[0] + round(lag), ant_root[1] - 11)
        if show_juno and not dangle:
            cx, cy = JUNO_CLIP[pose]; clip = (round(jx) + cx, round(jy) + cy)
        elif show_juno:
            clip = (round(jx) + DANGLE_CLIP[0], round(jy) + DANGLE_CLIP[1])
        else:
            clip = None
        attached = i >= 37
        if attached and show_bip:
            if i < 60:                                 # rover -> her belt while she floats up
                tether(im, ball, clip, sag=1.0 if i < 48 else 0.0)
            elif i < 72:                               # she is in the notch: cord hangs from the notch, slackening
                tether(im, ball, (NOTCH_PT[0], NOTCH_PT[1] - 6), sag=min(4.0, (i - 60) * 0.5))
            else:                                      # taut, quivering
                tether(im, ball, (NOTCH_PT[0] + (0 if i < 90 else 2), NOTCH_PT[1] - 6), sag=(-0.5 if i % 2 else 0.0) if i < 90 else 0.0)
        if attached and show_juno and dangle:          # her cord into the notch
            tether(im, clip, (clip[0] - 8, NOTCH_B - 6))
        if attached and i >= 122 and show_juno:        # Bip is gone: his end of the cord is inside the notch already
            pass
        # ------------------------------------------------------------------ draw
        if show_bip:
            spr, mx, my = bip(spin, lens, lean)
            c.blit(im, spr, round(bx) + mx, round(by) + my + dig)
            if by >= BY - 2 and i < 116: shadow(im, round(bx) + 2, 24)
            antenna(im, ant_root[0], ant_root[1], lag)
            if spin == 2 and 90 <= i < 102:            # dust kicked up behind the reversing wheels
                puff(im, round(bx) + 26, H - 1, ((i - 90) % 4) / 4)
                puff(im, round(bx) + 12, H - 2, ((i - 88) % 4) / 4)
            if 77 <= i < 82: puff(im, round(bx) + 3, H - 1, (i - 77) / 5); puff(im, round(bx) + 22, H - 1, (i - 77) / 5)
            if 114 <= i < 119: puff(im, round(bx) + 6, H - 1, (i - 114) / 5); puff(im, round(bx) + 20, H - 1, (i - 114) / 5)
            if i < 30 and abs(vel) > 3: puff(im, round(bx) - 2, H - 1, ((i) % 3) / 3)
        if show_juno:
            if dangle: spr, mx, my = juno_dangle(flail, blink)
            else:      spr, mx, my = juno(pose, blink or i in (41, 42))
            c.blit(im, spr, round(jx) + mx, round(jy) + my)
            if not dangle and jy >= JY - 1 and i >= 30: shadow(im, round(jx) + 3, 12)
            if i < 30 and (i % 10) == 0 and i > 0: puff(im, round(jx) + 7, H - 1, 0.2)
            if i in (37, 38):                          # the clip snaps on: a spark at the antenna ball
                dots(im, [(ball[0] - 1, ball[1] - 1), (ball[0] + 2, ball[1] - 1), (ball[0], ball[1] - 2), (ball[0] + 1, ball[1] + 2)], (255, 255, 255))
            if 48 <= i < 53: puff(im, round(jx) + 8, H - 1, (i - 48) / 5)
        if 122 <= i < 124:                             # last dust settling where Bip stood
            puff(im, 62, H - 1, (i - 120) / 4)
    return c
