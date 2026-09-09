import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- KID ON A BIKE LOSES A RED BALLOON (gag) ----------
# Modular: bike frame + 2 wheels (spoke swap) + legs (pedal swap) + torso + head variants + arm variants + balloon.
KP = {'B': (70, 120, 230), 'R': (160, 40, 40), 'd': (95, 95, 150)}

FRAME = sprite("""
...........nnn..
..nnn......n....
...n.......n....
...n.n....n.....
...n..n..n......
...n...nn.......
....nnnn........
""", KP)                                   # rows y=21..27, wheels sit at y=26..30
WHEEL_A = sprite("""
.SSS.
S.p.S
SpppS
S.p.S
.SSS.
""", KP)
WHEEL_B = sprite("""
.SSS.
Sp.pS
S.p.S
Sp.pS
.SSS.
""", KP)
LEG_A = sprite("""
..dd..
..dd..
...dd.
....y.
....y.
....kk
""", KP)                                   # foot on front pedal
LEG_B = sprite("""
..dd..
..dd..
..dd..
..y...
..y...
.kk...
""", KP)                                   # foot on back pedal
TORSO = sprite("""
.BBB.
BBBBB
BBBBB
.BBB.
""", KP)
HEAD = sprite("""
.gggg..
gggggg.
.yywby.
.yyyyy.
..yyy..
""", KP)                                   # looking right
HEAD_UP_BACK = sprite("""
wb.ggg.
yygggg.
yyyyyg.
.yyyy..
..yyy..
""", KP)                                   # looking up over the shoulder (balloon is behind)
HEAD_UP = sprite("""
.ggg.wb
ggggggy
.gyyyyy
..yyyy.
...yy..
""", KP)                                   # looking up-right (balloon passing overhead / camera)
ARM_FWD = sprite("""
y.....
.y....
..yy..
....yy
""", KP)                                   # right hand on the handlebar
ARM_UP = sprite("""
y.
y.
.y
.y
""", KP)                                   # left hand holds the string, 2x4 at (bx, 14)
ARM_REACH = sprite("""
y.
y.
y.
y.
.y
.y
""", KP)                                   # grabbing at air
ARM_DOWN = sprite("""
y
y
y
""", KP)
ARMS_SHRUG = sprite("""
yy.....yy
.y.....y.
..y...y..
""", KP)                                 # both palms up, elbows in
BALLOON = sprite("""
.rrrr.
rrwrrr
rwrrrr
rrrrrr
.rrrr.
..rr..
...R..
""", KP)                                   # knot at (3, 6)
PUFF = sprite("""
.s.
s.s
""", KP)

def line(im, x0, y0, x1, y1, col):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for k in range(n + 1):
        x = round(x0 + (x1 - x0) * k / n); y = round(y0 + (y1 - y0) * k / n)
        if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), col)

def bike(im, c, bx, arm, head=HEAD, lift=0):
    """bx = bike origin x (rear wheel left edge). Wheels + pedals turn with distance so they stop when the bike stops."""
    c.blit(im, FRAME, bx, 21)
    wheel = WHEEL_A if int(bx // 3) % 2 == 0 else WHEEL_B
    c.blit(im, wheel, bx, 26); c.blit(im, wheel, bx + 11, 26)
    c.blit(im, LEG_A if int(bx // 4) % 2 == 0 else LEG_B, bx + 3, 22)
    c.blit(im, TORSO, bx + 2, 18 - lift)
    c.blit(im, head, bx + 2, 13 - lift)
    if arm != 'shrug': c.blit(im, ARM_FWD, bx + 6, 18 - lift)
    if arm == 'up':      c.blit(im, ARM_UP, bx, 14)
    elif arm == 'reach': c.blit(im, ARM_REACH, bx, 11)
    elif arm == 'down':  c.blit(im, ARM_DOWN, bx + 1, 19)
    elif arm == 'shrug': c.blit(im, ARMS_SHRUG, bx, 17 - lift)

def balloon(im, c, kx, ky, hx=None, hy=None, wob=0):
    """kx,ky = knot. If a hand is given the string is held; else it dangles with a wobble."""
    c.blit(im, BALLOON, kx - 3, ky - 6)
    if hx is not None: line(im, kx, ky + 1, hx, hy, PAL['s'])
    else:
        for k in range(1, 6):
            x = kx + (wob if k >= 3 else 0); y = ky + k
            if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), PAL['s'])

def build():
    c = Clip('gag_kid_balloon_01', 7.0)
    X0, XSLIP, XSTOP = -24.0, 58.0, 72.0
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= 82: continue
        # ---- bike position ----
        if i < 19:   bx = X0 + (XSLIP - X0) * (i - 1) / 17                     # steady ride in
        elif i < 27: bx = XSLIP + (XSTOP - XSLIP) * (1 - (1 - (i - 19) / 7) ** 2)  # brake
        elif i < 63: bx = XSTOP
        else:        bx = XSTOP + (W + 8 - XSTOP) * ((i - 63) / 17) ** 1.6    # pedal off, accelerating
        bx = int(round(bx))
        # ---- balloon ----
        kx = ky = None
        if i < 19:
            bob = (i // 4) % 2; sway = ((i // 6) % 3) - 1
            if i >= 16: bob, sway = -1, -2                                     # tug: string goes taut before it slips
            kx, ky = bx - 4 + sway, 9 + bob
            balloon(im, c, kx, ky, bx, 13)
        elif i < 49:
            t = (i - 19) / 29
            kx = int(round(XSLIP - 6 + (CAM[0] + 1 - XSLIP + 6) * ease(t) + ((i // 3) % 2)))
            ky = int(round(8 - 13 * (t ** 1.25)))
            balloon(im, c, kx, ky, wob=((i // 2) % 2) * 2 - 1)
        # ---- kid pose ----
        if i < 19:       arm, head, lift = 'up', HEAD, 0
        elif i < 25:     arm, head, lift = 'reach', HEAD_UP_BACK, 0
        elif i < 52:     arm, head, lift = 'down', HEAD_UP_BACK if (kx is not None and kx < bx + 5) else HEAD_UP, 0
        elif i < 54:     arm, head, lift = 'down', HEAD, 0
        elif i < 62:     arm, head, lift = 'shrug', HEAD, 1 if i < 61 else 0
        else:            arm, head, lift = 'down', HEAD, 0
        bike(im, c, bx, arm, head, lift)
        if 20 <= i < 27 and i % 2 == 0: c.blit(im, PUFF, bx - 3, 27)            # skid dust behind the rear wheel
    return c
