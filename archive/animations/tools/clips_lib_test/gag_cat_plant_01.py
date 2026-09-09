import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- CAT KNOCKS THE PLANT OFF (gag) ----------
# Modular grey cat facing right: body + tail + head (side / front) + legs + paw. Pot is a prop with tip poses.
CP = {'i': (240, 140, 160)}   # nose pink

C_BODY = sprite("""
..ppppppppp..
.pppppppppppp
.pppppppppppp
.pppppppppppp
..ppppppppppp
..ppppppppppp
""", CP)
C_TAIL = sprite("""
..ss
.pps
.pp.
pp..
pp..
""", CP)
C_TAIL_FLICK = sprite("""
ss..
spp.
.pp.
.pp.
.pp.
""", CP)
C_HEAD_SIDE = sprite("""
.p...p..
.pP.Pp..
.ppppppp
.pppwwpp
.pppwbpp
.pppppip
..ppppp.
""", CP)
C_HEAD_FRONT = sprite("""
.p.....p.
.pP...Pp.
.ppppppp.
pwwpppwwp
pwbpppbwp
.pppipppp
..ppppp..
""", CP)
C_BLINK_SIDE = sprite("""
pp
pp
""", CP)
C_BLINK_FRONT = sprite("""
ppppppppp
ppppppppp
""", CP)
C_LEGS = [sprite(s, CP) for s in ("""
.pp.....pp.
.pp.....pp.
.pp.....pp.
""", """
pp.......pp
.pp.....pp.
.pp.....pp.
""", """
..pp...pp..
.pp.....pp.
.pp.....pp.
""")]
C_LEG_BACK = sprite("""
.pp........
.pp........
.pp........
""", CP)
C_SIT = sprite("""
....ppppp....
...ppppppppp.
..pppppppppp.
..ppppppppppp
..ppppppppppp
..ppppppppppp
..ppppppppppp
...pppp..pp..
...pppp..pp..
""", CP)

POT = sprite("""
..g.gg...
.gGg.gg..
..ggggg..
...gg....
.OOOOOOO.
.oooOooo.
..ooOoo..
..OOOOO..
""")
def pot_tipped(deg):
    """Pot rotated clockwise by deg (nearest-neighbour keeps it chunky); bottom-right corner is the pivot."""
    return POT.rotate(-deg, resample=Image.NEAREST, expand=True)

FLOOR = H - 1

def cat(im, c, x, leg=0, head='side', hdx=0, hdy=0, blink=False, tail=None, paw=0):
    """x = left of the body; feet on FLOOR. head offsets nudge the head (bob, sniff)."""
    by = FLOOR - 2 - 6 + 1               # body top: legs 3 rows, body 6 rows, overlap 1
    c.blit(im, tail or C_TAIL, x - 1, by - 3)
    c.blit(im, C_LEG_BACK if paw else C_LEGS[leg], x + 1, FLOOR - 2)
    c.blit(im, C_BODY, x, by)
    if paw:                              # front leg lifted: a chunky limb out from the shoulder, paw pad drooping at the tip
        for k in range(paw):
            for r in (2, 3): im.putpixel((int(x + 11 + k), by + r), PAL['p'])
        for k in range(2):
            for r in (3, 4): im.putpixel((int(x + 11 + paw - 1 + k), by + r), PAL['p'])
    hx, hy = x + 9 + hdx, by - 5 + hdy
    if head == 'side':
        c.blit(im, C_HEAD_SIDE, hx, hy)
        if blink: c.blit(im, C_BLINK_SIDE, hx + 4, hy + 3)
    else:
        c.blit(im, C_HEAD_FRONT, hx - 1, hy)
        if blink: c.blit(im, C_BLINK_FRONT, hx - 1, hy + 3)

def cat_sit(im, c, x, blink=False, tail=None):
    top = FLOOR - 8
    c.blit(im, tail or C_TAIL, x - 1, top + 2)
    c.blit(im, C_SIT, x, top)
    c.blit(im, C_HEAD_FRONT, x + 4, top - 5)
    if blink: c.blit(im, C_BLINK_FRONT, x + 4, top - 2)

def build():
    c = Clip('gag_cat_plant_01', 7.0)
    POT_X = 96; POT_Y = FLOOR - 7
    STAND = POT_X - 22                   # cat body-left when standing at the pot
    for i in range(c.n):
        im = c.frame()
        # ---- pot: drops in from above (1-7), sits, gets pushed (47-56), tips (56-60), falls (60-66)
        if 1 <= i < 7:
            t = ease((i - 1) / 5); y = -9 + (POT_Y - -9) * t
            c.blit(im, POT, POT_X, y)
        elif 7 <= i < 47:
            c.blit(im, POT, POT_X, POT_Y)
        elif 47 <= i < 56:
            t = ease((i - 47) / 8); c.blit(im, POT, POT_X + 9 * t, POT_Y)
        elif 56 <= i < 67:               # over the edge: keeps rotating while gravity takes it below the strip
            t = (i - 56) / 10; spr = pot_tipped(15 + 100 * t)
            c.blit(im, spr, POT_X + 9 + 8 * t, FLOOR + 1 - spr.height + 34 * t * t)
        # ---- cat
        if 2 <= i < 22:                  # walk in from the left
            t = ease((i - 2) / 19); x = -26 + (STAND + 26) * t
            cat(im, c, x, leg=[0, 1, 0, 2][(i // 2) % 4], hdy=-((i // 2) % 2))
        elif 22 <= i < 32:               # sniff: head dips toward the plant, little bobs
            j = i - 22
            dip = ease(min(1, j / 3))
            cat(im, c, STAND, hdx=int(3 * dip), hdy=int(3 * dip) + ((j // 2) % 2 if j >= 3 else 0),
                tail=C_TAIL_FLICK if j in (4, 5) else None)
            if j >= 3 and j % 2:         # two sniff wisps by the leaves
                for k in range(2):
                    im.putpixel((POT_X + 1 + k * 2, POT_Y - 1 - (j // 2) % 2 + k), PAL['s'])
        elif 32 <= i < 44:               # look straight out at the viewer, beat
            cat(im, c, STAND, head='front', blink=i in (40, 41))
        elif 44 <= i < 63:               # push: paw out, then the slow shove
            paw = int(ease(min(1, (i - 44) / 3)) * 10)
            step = 9 * ease(min(1, max(0, i - 47) / 8))          # cat leans/steps in with the pot
            cat(im, c, STAND + step, head='front', paw=paw, leg=1 if 49 <= i < 53 else 0,
                tail=C_TAIL_FLICK if i in (57, 58) else None)
        elif 63 <= i < 70:               # sit, blink
            cat_sit(im, c, STAND + 9, blink=i in (66, 67))
        elif 70 <= i < 84:               # walk off right
            t = ease((i - 70) / 13); x = STAND + 9 + (W + 6 - STAND - 9) * t
            cat(im, c, x, leg=[0, 1, 0, 2][(i // 2) % 4], hdy=-((i // 2) % 2))
    return c
