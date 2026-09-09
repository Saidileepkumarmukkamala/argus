import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- KNIGHT SALUTE (gesture: you are doing great) ----------
# Same knight as gag_knight_trip_01: plume + helm + body + arm + legs composed at offsets from the helm's top-left.
PLUME = sprite("""
rr.....
rrr....
.rrr...
..rrr..
...rr..
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
ARM_OUT = sprite("""
pppp
""")
ARM_SALUTE = sprite("""
pp
.p
.p
.p
pp
""")
LEGS_STAND = sprite("""
.Ppp..
.Ppp..
.Ppp..
.Ppp..
.tttt.
""")
LEGS_SQUASH = sprite("""
.Pppp.
.Pppp.
.Pppp.
.ttttt
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

HEART_SMALL = sprite("""
r.r
rrr
.r.
""")
HEART = sprite("""
.r.r.
rwrrr
rrrrr
.rrr.
..r..
""")
HEART_PALE = sprite("""
.n.n.
nnnnn
.nnn.
..n..
""", {'n': (255, 150, 150)})


def compose(parts):
    """parts: [(sprite, dx, dy)] relative to the helm's top-left -> (RGBA, ox, oy)."""
    x0 = min(dx for _, dx, _ in parts); y0 = min(dy for _, _, dy in parts)
    x1 = max(dx + s.width for s, dx, _ in parts); y1 = max(dy + s.height for s, _, dy in parts)
    im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for s, dx, dy in parts: im.paste(s, (dx - x0, dy - y0), s)
    return im, x0, y0


def standing(legs, arm=ARM_FWD, helm=HELM, chin=0):
    """chin>0 lifts helm+plume (proud); chin<0 dips them (nod)."""
    parts = [(helm, 0, -chin), (PLUME, -1, -5 - chin), (BODY, 0, 6)]
    if arm is ARM_FWD: parts.append((arm, 7, 8))
    elif arm is ARM_OUT: parts.append((arm, 7, 7))
    else: parts.append((arm, 8, 3 - chin))
    parts.append((legs, 2 if legs.width == 8 else 1, 12))
    return parts


def build():
    c = Clip('gesture_knight_salute_01', 6.0)
    HY = H - 17                                        # helm top-left y when standing, feet on the floor
    CX = W // 2 - 6                                    # stop with the helm centred under the camera
    CYC = [(KNEE_NEAR, 1, 2)] * 3 + [(APART_NEAR, 0, 6)] * 2 + [(KNEE_FAR, 1, 2)] * 3 + [(APART_FAR, 0, 6)] * 2
    x = -12.0
    hx = hy = None
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= 71: continue
        if i < 28:                                     # march in from the left
            legs, bob, adv = CYC[(i - 1) % 10]
            x = min(CX, x + adv)
            comp, ox, oy = compose(standing(legs))
            c.blit(im, comp, x + ox, HY + oy - bob)
        elif i < 31:                                   # crisp stop: plant + squash + settle
            x = CX
            legs = LEGS_SQUASH if i < 30 else LEGS_STAND
            comp, ox, oy = compose(standing(legs))
            c.blit(im, comp, x + ox, HY + oy + (1 if i < 30 else 0))
        elif i < 33:                                   # arm swings up
            comp, ox, oy = compose(standing(LEGS_STAND, arm=ARM_OUT))
            c.blit(im, comp, x + ox, HY + oy)
        elif i < 45:                                   # the salute: held firm, chin up
            comp, ox, oy = compose(standing(LEGS_STAND, arm=ARM_SALUTE, chin=1))
            c.blit(im, comp, x + ox, HY + oy)
        elif i < 47:                                   # arm back down
            comp, ox, oy = compose(standing(LEGS_STAND, arm=ARM_OUT))
            c.blit(im, comp, x + ox, HY + oy)
        elif i < 53:                                   # one nod
            j = i - 47
            chin = [0, -1, -1, -1, 0, 0][j]
            helm = HELM_BLINK if j in (1, 2) else HELM
            comp, ox, oy = compose(standing(LEGS_STAND, helm=helm, chin=chin))
            c.blit(im, comp, x + ox, HY + oy)
        else:                                          # march off right, a touch quicker
            legs, bob, adv = CYC[(i - 53) % 10]
            x += adv + 1
            comp, ox, oy = compose(standing(legs))
            c.blit(im, comp, x + ox, HY + oy - bob)
        # the heart: pops above the helm during the salute, floats up and off
        if 36 <= i < 58:
            t = i - 36
            if hx is None: hx, hy = CX + 3, HY - 8
            spr = HEART_SMALL if t < 2 else HEART if t < 14 else HEART_PALE
            yy = hy - (t - 2) // 2 if t >= 2 else hy
            xx = hx + (1 if (t // 3) % 2 else 0)
            c.blit(im, spr, xx - spr.width // 2 + 2, yy)
    return c
