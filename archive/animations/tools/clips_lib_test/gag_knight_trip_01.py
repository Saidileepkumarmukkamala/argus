import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *
from PIL import ImageDraw

BUCKET = 'gag'

# ---------- KNIGHT TRIPS OVER NOTHING (gag) ----------
# Modular: plume + helm + body + arm + legs composed at offsets from the helm's top-left.
# The trip itself shears/rotates the composed standing figure so the fall is one continuous body.
PLUME_UP = sprite("""
rr.....
rrr....
.rrr...
..rrr..
...rr..
""")
PLUME_TALL = sprite("""
.rr
.rr
rrr
.rr
.rr
.rr
""")
PLUME_FLOP = sprite("""
rr....
.rrr..
...rr.
....rr
....rr
""")
PLUME_FLAT = sprite("""
rr...
.rrrr
""")
HELM = sprite("""
..ssss..
.ssssss.
ssssssss
sPPPwbPs
ssssssss
.ssssss.
""")
HELM_BLINK = sprite("""
..ssss..
.ssssss.
ssssssss
sPPPPPPs
ssssssss
.ssssss.
""")
HELM_LOOKBACK = sprite("""
..ssss..
.ssssss.
ssssssss
sPPbwPPs
ssssssss
.ssssss.
""")
BODY = sprite("""
.ssssss.
ssrrrrss
ssrrrrss
ssrrrrss
.syyyys.
.ssssss.
""")
ARM_FWD = sprite("""
ppp
..p
""")
ARM_UP = sprite("""
pp
p.
p.
p.
p.
""")
ARM_OUT = sprite("""
pppp
""")
LEGS_STAND = sprite("""
.Ppp..
.Ppp..
.Ppp..
.Ppp..
.tttt.
""")
LEGS_CROUCH = sprite("""
.Ppp..
.tttt.
""")
_KNEE = """
.BBAAAAA
.BB...AA
.BB...tt
.BB.....
.ttt....
"""
_APART = """
...BBAA..
..BB..AA.
.BB....AA
.BB....AA
.tt....tt
"""
NEAR = {'A': PAL['p'], 'B': PAL['P']}
FAR = {'A': PAL['P'], 'B': PAL['p']}
KNEE_NEAR, KNEE_FAR = sprite(_KNEE, NEAR), sprite(_KNEE, FAR)
APART_NEAR, APART_FAR = sprite(_APART, NEAR), sprite(_APART, FAR)

FLAG_A = sprite("""
yrrrrrr
.rrrrrr
.rryyrr
.rrrrr.
.rrrr..
""")
FLAG_B = sprite("""
yrrrrr.
.rrrrrr
.rryyrr
.rrrrrr
.rrrr..
""")
FLAG_HANG = sprite("""
yrr
rrr
rrr
rry
rr.
""")
FLAG_FLAT = sprite("""
yrrrrrr
.rrrrrr
""")
POLE_L = 20

# hand-drawn horizontal poses: rotating the standing figure reads as mush at this size
DIVE = sprite("""
..............rrr........
.............rr.ssss.....
.PP..........r.ssssss....
.PPpppssssssss.sPPwbPs...
..PPppssrrrrrssssssssspp.
....ppssrrrrrs..ssss..ppp
......ssyyyyss...........
......ssssssss...........
""")
PRONE_DOWN = sprite("""
...........sssss..ssssss....
..........sssssss.sssssss...
.PPPPpp..ssrrrrrsssssssssss.
.pppppp..ssrrrrrsssssssssppp
tt...tt.ssyyyyyysssssssrrrrr
""")
PRONE_UP = sprite("""
.....................rr....
....................ssss.rr
...................ssssssrr
...................sPPwbPs.
.PPPPpp..sssssss...ssssss..
.pppppp..ssrrrrrsssssssssss
tt...tt.ssyyyyyyssssssspppp
""")

def compose(parts):
    """parts: [(sprite, dx, dy)] relative to the helm's top-left -> (RGBA, ox, oy) where (ox,oy) is the
    offset of the image's top-left from that origin."""
    x0 = min(dx for _, dx, _ in parts); y0 = min(dy for _, _, dy in parts)
    x1 = max(dx + s.width for s, dx, _ in parts); y1 = max(dy + s.height for s, _, dy in parts)
    im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for s, dx, dy in parts: im.paste(s, (dx - x0, dy - y0), s)
    return im, x0, y0

def shear(im, lean):
    """Lean the figure forward: rows shift right, more toward the top (feet stay put)."""
    out = Image.new('RGBA', (im.width + lean, im.height), (0, 0, 0, 0))
    for r in range(im.height):
        sh = round(lean * (im.height - r) / im.height)
        out.paste(im.crop((0, r, im.width, r + 1)), (sh, r))
    return out

def pole(im, px, py, ang, i):
    """Banner pole: pivot at the butt end (px,py), ang degrees above the ground, flag at the tip."""
    import math
    tx = px + POLE_L * math.cos(math.radians(ang)); ty = py - POLE_L * math.sin(math.radians(ang))
    ImageDraw.Draw(im).line([(px, py), (tx, ty)], fill=PAL['t'])
    if ang > 60: im.paste(FLAG_A if (i // 4) % 2 else FLAG_B, (int(tx), int(ty)), FLAG_A if (i // 4) % 2 else FLAG_B)
    elif ang > 15: im.paste(FLAG_HANG, (int(tx) - 1, int(ty)), FLAG_HANG)
    else: im.paste(FLAG_FLAT, (int(tx), int(ty) - 1), FLAG_FLAT)

def standing(legs, plume=PLUME_UP, helm=HELM, arm=ARM_FWD, chin=0):
    parts = [(helm, 0, -chin), (BODY, 0, 6)]
    if plume is PLUME_UP: parts.append((plume, -1, -5 - chin))
    elif plume is PLUME_TALL: parts.append((plume, 2, -6 - chin))
    else: parts.append((plume, 4, -1 - chin))
    if arm is ARM_FWD: parts.append((arm, 7, 8))
    elif arm is ARM_UP: parts.append((arm, 8, 3))
    else: parts.append((arm, 7, 7))
    lx = 2 if legs.width == 8 else 1
    parts.append((legs, lx, 12))
    return parts

def build():
    c = Clip('gag_knight_trip_01', 7.0)
    HY = H - 17                       # helm top-left y when standing (legs bottom on the strip floor)
    # stride cycle (10 frames): 3 near-knee, 2 apart, 3 far-knee, 2 apart
    CYC = [(KNEE_NEAR, 1, 'k')] * 3 + [(APART_NEAR, 0, 'a')] * 2 + [(KNEE_FAR, 1, 'k')] * 3 + [(APART_FAR, 0, 'a')] * 2
    x = -24.0; trip_x = 80
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= 81: continue
        if i < 30:                                       # march in, big proud steps
            legs, bob, kind = CYC[(i - 1) % 10]
            x += 2 if kind == 'k' else 6
            if i == 29: x = trip_x
            parts = standing(legs)
            comp, ox, oy = compose(parts)
            c.blit(im, comp, x + ox, HY + oy - bob)
            pole(im, x + 10, HY + 10 - bob, 90, i)
        elif i < 33:                                     # the catch: toe hooks, body pitches forward
            lean = [2, 4, 7][i - 30]
            parts = standing(APART_NEAR, arm=ARM_OUT if lean >= 6 else ARM_FWD)
            comp, ox, oy = compose(parts)
            c.blit(im, shear(comp, lean), x + ox, HY + oy)
            pole(im, x + 10 + lean, HY + 10, 90 - lean * 4, i)
        elif i < 36:                                     # airborne: full superman dive, dropping
            j = i - 33
            dx, dy = [2, 5, 8][j], [HY + 6, HY + 10, H - 8][j]
            c.blit(im, DIVE, x + dx - 2, dy)
            pole(im, x + dx + 18, dy + 5, [50, 35, 18][j], i)
        else:
            if i == 36: x += 8                           # he lands where the dive carried him
            px, py = x + 24 - max(0, min(10, (i - 41) * 2)), H - 2   # pole lands by his outstretched hand; he drags it back in
            if i < 47:                                   # faceplant + beat
                if i < 41:                               # face in the floor
                    pr = PRONE_DOWN
                    if i == 36: pr = pr.resize((pr.width + 3, pr.height - 1), Image.NEAREST)   # squash
                    c.blit(im, pr, x - 1, H - pr.height)
                    hx = x + 18
                    for k, (ddx, ddy) in enumerate([(-2, 1), (3, 2), (8, 1), (1, 4), (6, 4), (-6, 2)]):
                        t = i - 36
                        if t <= 2 + k % 2:
                            im.putpixel((int(hx + ddx + t), int(min(H - 1, H - 2 - ddy - t))), PAL['S'])
                else:                                    # head lifts, dazed; blink (he lies on the pole)
                    pole(im, px, py, 0, i)
                    c.blit(im, PRONE_UP, x - 1, H - PRONE_UP.height)
                    if i in (44, 45):
                        for k in (21, 22): im.putpixel((int(x - 1 + k), H - 7 + 3), PAL['P'])
                if i < 41: pole(im, px, py, [10, 4, 0, 3, 1][i - 36], i)
            elif i < 49:                                 # push up to a crouch, grab the pole
                parts = [(HELM, 0, 0), (BODY, 0, 6), (PLUME_FLOP, 4, -1), (ARM_FWD, 7, 8), (LEGS_CROUCH, 1, 12)]
                comp, ox, oy = compose(parts)
                y = H - 14
                c.blit(im, comp, x + ox, y + oy)
                pole(im, x + 12 - (i - 47) * 2, y + 10, 30 + (i - 47) * 30, i)
            elif i < 51:                                 # up, with a stretch overshoot
                comp, ox, oy = compose(standing(LEGS_STAND, plume=PLUME_FLOP))
                yy = HY - (1 if i == 49 else 0)
                c.blit(im, comp, x + ox, yy + oy)
                pole(im, x + 10, yy + 10, 90, i)
            elif i < 60:                                 # straighten the plume, glance back
                j = i - 51
                if j < 3: plume, arm, helm = PLUME_FLOP, ARM_UP, HELM
                elif j == 3: plume, arm, helm = PLUME_TALL, ARM_UP, HELM
                elif j < 6: plume, arm, helm = PLUME_UP, ARM_UP, HELM
                else: plume, arm, helm = PLUME_UP, ARM_FWD, HELM_LOOKBACK
                comp, ox, oy = compose(standing(LEGS_STAND, plume=plume, helm=helm, arm=arm))
                c.blit(im, comp, x + ox, HY + oy)
                pole(im, x + 10, HY + 10, 90, i)
            else:                                        # march out, chin up, dignity fully restored
                legs, bob, kind = CYC[(i - 60) % 10]
                x += 3 if kind == 'k' else 8
                comp, ox, oy = compose(standing(legs, chin=1))
                c.blit(im, comp, x + ox, HY + oy - bob * 2)
                pole(im, x + 10, HY + 10 - bob * 2, 90, i)
    return c
