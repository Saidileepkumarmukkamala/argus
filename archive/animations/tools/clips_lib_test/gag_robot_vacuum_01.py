import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- ROBOT VACUUM EATS A CRUMB (gag) ----------
# Modular: disc body + eyes + status light + back vent + side brush. A "facing" angle slides the
# eyes across the front half and the vent across the back half, so the spin and the U-turn are
# one function. Squash poses are nearest-neighbour resizes of the same body, never redraws.
BODY = sprite("""
.......ssssssssss.......
....ssssssssssssssss....
..ssssssssssssssssssss..
.ssssssssssssssssssssss.
ssssssssssssssssssssssss
pppppppppppppppppppppppp
pppppppppppppppppppppppp
.PPPPPPPPPPPPPPPPPPPPPP.
...PPPPPPPPPPPPPPPPPP...
""")
BW, BH = BODY.size
BODY_GULP = BODY.resize((BW + 2, BH - 1), Image.NEAREST)      # wide + short: swallow
BODY_BUMP = BODY.resize((BW - 3, BH + 1), Image.NEAREST)      # narrow + tall: hit the wall
EYES_R = sprite("""
wb.wb
ww.ww
""")
EYES_L = flip(EYES_R)
EYES_DOWN = sprite("""
ww.ww
wb.wb
""")
EYES_SHUT = sprite("""
kk.kk
""")
EYES_HAPPY = sprite("""
.w..w.
w.ww.w
""")
BRUSH = [sprite("S.S\n.S.\nS.S"), sprite(".S.\nSSS\n.S.")]   # spinning side brush, 2 poses
VENT = sprite("""
S.S.S
""")
MOUTH = sprite("""
bbb
bbb
""")
CRUMB = sprite("""
.yyy.
yOtOy
yOOOy
.ttt.
""")
CW = CRUMB.width
LIGHT = {k: sprite(k * 2 + '\n' + k * 2) for k in 'cygr'}

def vac(im, c, x, y, facing=0.0, eyes=None, light='c', body=None, brush=None, mouth=False):
    """x,y = top-left of the normal body (poses are re-centred on the same floor point).
    facing: 0 = right, 0.5 = left, 0..1 = one full spin. brush: frame index while moving."""
    body = body or BODY
    bx0 = x + (BW - body.width) // 2; by0 = y + BH - body.height
    a = 2 * math.pi * facing
    ex = x + 10 + 9 * math.cos(a)                          # eye centre sweeps across the front band
    brx = x + BW - 2 if math.cos(a) >= 0 else x - 1        # brush rides the front bumper
    if brush is not None: c.blit(im, BRUSH[brush % 2], brx, y + 6)
    c.blit(im, body, bx0, by0)
    if light: c.blit(im, LIGHT[light], x + 11, by0 + 1)
    if mouth: c.blit(im, MOUTH, x + BW - 4, y + 6)         # dark intake at the front-bottom
    if math.sin(a) >= -1e-6:                               # front half: eyes visible
        spr = eyes or (EYES_R if (facing % 1) < 0.25 or (facing % 1) > 0.75 else EYES_L)
        c.blit(im, spr, ex, by0 + 5)
    else:                                                  # back half: vent slides across instead
        c.blit(im, VENT, ex, by0 + 6)

def trail(im, x, i, d):
    """Two dust pixels behind a fast-moving vacuum; d = direction the trail extends."""
    for k in (0, 3):
        px, py = int(x + d * (k + (i % 2))), H - 2 - (k + i) % 2
        if 0 <= px < W: im.putpixel((px, py), PAL['S'])

def crumb(im, c, cx, cy, clip_x=None):
    """Blit the crumb; anything left of clip_x is inside the vacuum and hidden."""
    spr = CRUMB
    if clip_x is not None:
        cut = int(clip_x - cx)
        if cut >= CW: return
        if cut > 0: spr = CRUMB.crop((cut, 0, CW, CRUMB.height)); cx += cut
    c.blit(im, spr, cx, cy)

def build():
    c = Clip('gag_robot_vacuum_01', 6.0)
    y = H - BH
    crumb_x, crumb_y = 100, H - 4
    stop_x = crumb_x - BW - 6                              # pull up a little short of the crumb
    mouth_x = stop_x + BW - 1
    edge_x = W - BW
    for i in range(c.n):
        im = c.frame()
        blink = 'c' if (i // 5) % 2 == 0 else None
        if i < 18:                                # crumb tumbles in from the top; vacuum drives in, eases to a halt
            fall = min(1.0, i / 6) ** 2
            cy = -4 + (crumb_y + 4) * fall - (2 if i == 7 else 1 if i in (6, 8) else 0)
            crumb(im, c, crumb_x, cy)
            if i >= 2:
                t = ease((i - 2) / 15); x = -BW + (stop_x + BW) * t
                vac(im, c, x, y, light=blink, brush=i)
        elif i < 24:                              # notice: little hop, eyes drop to the crumb, light goes amber
            hop = -1 if i in (19, 20) else 0
            crumb(im, c, crumb_x, crumb_y)
            vac(im, c, stop_x, y + hop, eyes=EYES_DOWN, light='y')
        elif i < 30:                              # suction spins up: crumb shivers, motes stream toward the mouth
            j = i - 24
            crumb(im, c, crumb_x + (j % 2), crumb_y - (j % 3 == 1))
            for k in range(3):
                mx = crumb_x + 8 + k * 5 - (j * 3 + k) % 14; my = H - 2 - (k + j) % 3
                if mx > mouth_x + 2: im.putpixel((int(mx), int(my)), PAL['s'])
            vac(im, c, stop_x, y, eyes=EYES_DOWN, light='y', mouth=True)
        elif i < 38:                              # crumb rips into the mouth (accelerating), gulp
            j = i - 30; t = min(1.0, (j / 4) ** 2)
            cx = crumb_x + (mouth_x - CW - crumb_x) * t
            crumb(im, c, cx, crumb_y - (j < 4), clip_x=mouth_x)
            for k in range(2):
                mx = crumb_x + 6 + k * 5 - (j * 4 + k) % 12; my = H - 2 - (k + j) % 2
                if mouth_x + 2 < mx < W: im.putpixel((int(mx), int(my)), PAL['s'])
            body = BODY_GULP if j in (5, 6) else None
            vac(im, c, stop_x, y, eyes=EYES_DOWN if j < 5 else EYES_SHUT, light='y', body=body, mouth=j < 5)
        elif i < 48:                              # satisfied: one full spin with a happy bounce
            j = i - 38; facing = ease(j / 9)
            bounce = -1 if j % 4 < 2 else 0
            vac(im, c, stop_x, y + bounce, facing=facing, eyes=EYES_HAPPY, light='g', brush=i)
        elif i < 54:                              # zoom right, ease-in
            t = ((i - 48) / 5) ** 2; x = stop_x + (edge_x - stop_x) * t
            vac(im, c, x, y, light='g', brush=i)
            trail(im, x - 2, i, -1)
        elif i < 58:                              # bump the edge: squash, red light, sparks, recoil
            j = i - 54
            body = BODY_BUMP if j < 2 else None
            vac(im, c, edge_x - (0 if j < 2 else j - 1), y, eyes=EYES_SHUT, light='r', body=body)
            if j < 2:
                for (sx, sy) in ((W - 1, y + 2), (W - 2, y - 1), (W - 1, y + 7)):
                    im.putpixel((sx, sy - j), PAL['y'])
        elif i < 62:                              # half-turn to face left
            facing = 0.5 * ease((i - 58) / 3)
            vac(im, c, edge_x - 3, y, facing=facing, light='r' if i < 60 else blink)
        else:                                     # drive off left, accelerating out
            t = (i - 62) / 9; t = t * t
            x = (edge_x - 3) + (-BW - (edge_x - 3)) * t
            vac(im, c, x, y, facing=0.5, light=blink, brush=i)
            if 64 < i < c.n - 1: trail(im, x + BW + 1, i, 1)
    return c
