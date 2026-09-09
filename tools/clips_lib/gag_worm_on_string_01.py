"""Worm on a string — the notch goes fishing. A baited hook lowers from the underside; a stubby bluebird climbs over
the ledge for it, pecks, gets hauled up by the beak, snaps free, and the bait comes back bigger and smugger."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'
BL = ramp((70, 138, 205))                    # bluebird body: shadow, base, light, highlight
CR = ramp((240, 222, 180))                   # cream belly
OR = ramp((238, 150, 58))                    # beak + feet
PK = ramp((228, 118, 150))                   # worm
PAL2 = {'D': BL[0], 'b': BL[1], 'l': BL[2], 'h': BL[3],
        'C': CR[0], 'c': CR[1], 'e': CR[2],
        'O': OR[0], 'o': OR[1], 'n': OR[2],
        'R': PK[0], 'r': PK[1], 'q': PK[2], 'Q': PK[3],
        'i': (176, 104, 34), 'k': (22, 18, 30), 'w': (250, 250, 246), 'W': (255, 255, 255),
        'd': (30, 60, 120), 's': (208, 208, 218), 'S': (138, 138, 152), 'T': (168, 168, 182)}
S = lambda rows: sprite(rows, PAL2)
RIM = (56, 64, 104)
WRIM = (110, 48, 84)

# ---------- bird parts (faces LEFT; the eye field is white, the iris is overlaid so the gaze can move) ----------
HEAD = S("""
.......hhhhhh...
.....hhllllllb..
....hlllbbbbbbb.
...hlllbbbbbbbb.
...lbwwwwwwbbbbb
..lbwwwwwwwwbbbb
..lbwwwwwwwwbbbb
nnobwwwwwwwwbbbD
noobwwwwwwwwbbbD
.OobbbwwwwwwbbDD
..DbbbbbbbbbbDD.
...DDbbbbbbbDDD.
....DDDDDDDD....
""")
HEAD_OPEN = S("""
.......hhhhhh...
.....hhllllllb..
....hlllbbbbbbb.
...hlllbbbbbbbb.
...lbwwwwwwbbbbb
..lbwwwwwwwwbbbb
nnlbwwwwwwwwbbbb
.nobwwwwwwwwbbbD
...bwwwwwwwwbbbD
.OobbbwwwwwwbbDD
OODbbbbbbbbbbDD.
...DDbbbbbbbDDD.
....DDDDDDDD....
""")
HEAD_UP = S("""
....nn..........
...nno..........
...noo..........
...noob.........
..hlbbbbbh......
.hllbbbbbbbb....
.llwwwwwwwbbbb..
llwwwwwwwwbbbbb.
lbwwwwwwwwbbbbb.
lbwwwwwwwwbbbbbD
lbwwwwwwwwbbbbbD
.bbbwwwwwwwbbbDD
.DbbbbbbbbbbbDD.
..DDbbbbbbbDDD..
...DDDDDDDDD....
""")
IRIS = S("""
iiii
iWki
ikki
iiii
""")
IRIS_SMALL = S("""
.ii.
ikki
iiii
""")
LID = S("""
.bbbbbb.
bbbbbbbb
bbbbbbbb
bbbbbbbb
bbbbbbbb
DDDDDDDD
""")
HALF_LID = S("""
.bbbbbb.
bbbbbbbb
DDDDDDDD
""")
BODY = S("""
.......hhhhhhhhh.....
.....hhlllllllllll...
....hlllbbbbbbbbbbb..
...hllbbbbbbbbbbdbbb.
..llbbbbbbbbbbbbbdbbD
..lebbbbbbbbbbbbbbdbD
.lecebbbbbbbbbbbbbDDD
.leccebbbbbbbbbbbDDDD
.lecccebbbbbbbbbDDDDD
.CccccceebbbbbbbDDDD.
.CccccccccebbbbDDDDD.
..CCcccccccccDDDDDD..
...CCCccccccDDDDD....
.....CCCCCDDDD.......
""")
BODY_FLAT = S("""
.........hhhhhhhhhh.......
......hhlllllllllllll.....
....hlllbbbbbbbbbbdbbbb...
..hllbbbbbbbbbbbbbbbdbbbD.
.lecebbbbbbbbbbbbbbbbDDDDD
.leccccebbbbbbbbbbbDDDDDDD
.CccccccccebbbbbbDDDDDDDD.
..CCcccccccccDDDDDDDDDD...
....CCCCCCCDDDDDDDD.......
""")
WING = S("""
..dllllllld..
.dlbbbbbbbbd.
.dbbbbbbbbbd.
.dDbbbbbbbDd.
..dDbbbbbDd..
...ddDDDdd...
""")
WING_UP = S("""
.........dlld
.......dllbbd
.....dllbbbd.
...dlbbbbbd..
..dbbbbbDd...
..dDbbDDd....
..ddDDd......
""")
WING_DOWN = S("""
..dDDDd......
..dbbbbDd....
..dlbbbbbDd..
...dlbbbbbDd.
.....dlbbbbDd
.......dllbbd
.........ddd.
""")
TAIL = S("""
.....DDl
..DDDDDl
DDDDDDl.
.DDDD...
""")
TAIL_DOWN = S("""
DDl.
DDDl
.DDl
.DDD
..DD
""")
LEG_A = S("""
..o.....o..
..o.....o..
..o.....o..
Oooo..Oooo.
""")
LEG_B = S("""
...o....o..
..oo....o..
.Ooo....o..
......Oooo.
""")
LEG_C = S("""
..o....o...
..o....oo..
..o....ooO.
Oooo.......
""")
LEG_PED_A = S("""
..o......o.
..o.....o..
.oo....oo..
Oo.....O...
""")
LEG_PED_B = S("""
..o.....o..
...o....o..
...oo..oo..
....O..Oo..
""")
LEG_REACH = S("""
..o.....o..
..o.....o..
..o.....o..
.ooo...ooo.
O..O..O..O.
""")
WING_OUT_UP = S("""
...........dld
.........dllbd
.......dllbbd.
.....dllbbbd..
...dllbbbbd...
.dlbbbbbbd....
dDbbbbbDd.....
.ddDDDdd......
""")
WING_OUT_DOWN = S("""
dDDd..........
dbbbDd........
dlbbbbDd......
.dlbbbbbDd....
..dlbbbbbbDd..
....dlbbbbbDd.
......dllbbbdd
........ddddd.
""")
LEG_SPLAY = S("""
Ooo...........ooO
""")
CLAW = S("""
.o.o.
ooooo
.O.O.
""")
# ---------- rig ----------
HOOK = S("""
...ss
...ss
...ss
s..ss
sSsS.
.SS..
""")
WORM_A = S("""
.rqq.
rkrkq
rrrq.
.rrq.
Rrr..
Rrq..
.Rr..
..R..
""")
WORM_B = S("""
.rqq.
rkrkq
rrrq.
.rrq.
.Rrr.
.Rrq.
..Rr.
...R.
""")
WORM_WIDE = S("""
.wwww
rwkwk
rrrq.
.rrq.
.Rrq.
.Rrq.
.Rr..
.R...
""")
WORM_BIG = S("""
..rqqq..
.rrrrqq.
rrwwrwwq
rrrkrrkq
rrrrrrq.
Rrkkkkq.
Rrrrrq..
.Rrrq...
.Rrrq...
..Rrq...
..Rr....
...R....
""")

def bird(pose='stand', legs=LEG_A, head=HEAD, hdx=0, hdy=0, gaze=0, lid=None, wing=WING):
    """Assemble + outline once. Returns (sprite, ox, oy): blit at (x + ox, y + oy) where (x, y) is the head origin.
    Standing bird is 27 px tall, feet on the bottom row. gaze: iris shift 0 (toward the worm) .. 3 (toward the viewer)."""
    if pose == 'hang':
        up = wing is WING_UP
        rw = (WING_OUT_UP, 13, 5) if up else (WING_OUT_DOWN, 14, 12)
        lw = (hflip(WING_OUT_UP), -6, 5) if up else (hflip(WING_OUT_DOWN), -7, 12)
        parts = [lw, (BODY, 2, 8), (TAIL_DOWN, 21, 12), rw, (legs, 8, 20), (HEAD_UP, 0, 0)]
        eye = (3 + gaze, 7)
    elif pose == 'flat':
        parts = [(BODY_FLAT, 2, 14), (TAIL, 24, 17), (WING, 10, 16), (LEG_SPLAY, 5, 23), (head, 0 + hdx, 8 + hdy)]
        eye = (5 + gaze + hdx, 5 + 8 + hdy)
    else:
        parts = [(BODY, 3, 9), (TAIL, 22, 13), (wing, 10, 12), (legs, 9, 23), (head, hdx, hdy)]
        eye = (5 + gaze + hdx, 5 + hdy)
    if lid is None: parts.append((IRIS, eye[0], eye[1]))
    elif lid == 'shut': parts.append((LID, eye[0] - gaze - 1, eye[1] - 1))
    elif lid == 'dizzy': parts.append((IRIS_SMALL, eye[0], eye[1] + 1)); parts.append((HALF_LID, eye[0] - gaze - 1, eye[1] - 1))
    spr, mx, my = assemble(parts)
    return outline(spr, RIM), mx - 1, my - 1

def rig(im, hook_y, worm=None, sway=0, x=100):
    """Thread from the notch to the hook at (x, hook_y); the worm hangs on the bend. Everything above y=21 is inside the notch."""
    dots(im, [(x + sway, y) for y in range(0, int(hook_y))], PAL2['T'])
    c_blit(im, HOOK, x - 3 + sway, hook_y)
    if worm is not None: c_blit(im, outline(worm, WRIM), x - 3 + sway - 1, hook_y + 4)

def c_blit(im, spr, x, y): im.paste(spr, (int(x), int(y)), spr)

def feathers(im, i, x0, y0):
    """Three feathers drift down and sideways from (x0, y0) over 16 frames."""
    if not 0 <= i < 16: return
    for k, (dx, ph) in enumerate(((-6, 0.0), (4, 1.3), (10, 2.4))):
        fx = x0 + dx + 2 * math.sin(i * 0.5 + ph); fy = min(H - 2, y0 + 1.4 * i + k * 2)
        dots(im, [(fx, fy), (fx + 1, fy)], BL[2]); dots(im, [(fx - 1, fy + 1)], PAL2['d'])

def build():
    c = Clip('gag_worm_on_string_01', 12.0)
    HX = 100                                  # thread x
    HOOK_Y = 30                               # lowered hook: worm bottom sits 7 px above the floor
    STAND_Y = H - 27                          # head origin y for a standing bird
    LEDGE_X = 122                             # where the bird climbs over
    bx = float(LEDGE_X)
    for i in range(c.n):
        im = c.frame()
        worm = WORM_A if (i // 3) % 2 == 0 else WORM_B
        # ---- 0-1.5 s: the bait lowers, sways, settles ----
        if i == 0: continue                    # empty lead frame
        if i < 20:
            t = ease((i - 1) / 12); hy = -12 + (HOOK_Y + 12) * t
            sway = round(1.4 * math.sin((i - 13) * 1.1) * max(0, 1 - (i - 13) / 8)) if i >= 13 else 0
            rig(im, hy, worm, sway)
        # ---- 1.5-3 s: claws on the ledge, head pops up, heave, land ----
        elif i < 42:
            rig(im, HOOK_Y, worm)
            if i < 25:
                c_blit(im, CLAW, bx + 4, H - 3 + (0 if i < 23 else -1)); c_blit(im, CLAW, bx + 13, H - 3 + (0 if i < 23 else -1))
            elif i < 31:
                spr, ox, oy = bird(gaze=0, hdy=0); c_blit(im, spr, bx + ox, H - 13 + oy)
                c_blit(im, CLAW, bx + 4, H - 3); c_blit(im, CLAW, bx + 13, H - 3)
            elif i < 36:
                yy = H - 13 - 4 * (i - 30)                      # heave: rises 4 px a frame
                spr, ox, oy = bird(gaze=0, legs=LEG_B); c_blit(im, spr, bx + ox, yy + oy)
            elif i < 38:
                spr, ox, oy = bird('flat'); c_blit(im, spr, bx + ox, H - 25 + oy); shadow(im, bx + 2, 30)
                puff(im, bx + 4, H - 1, 0.15 + 0.3 * (i - 36)); puff(im, bx + 26, H - 1, 0.15 + 0.3 * (i - 36))
            else:
                spr, ox, oy = bird(hdy=-2 if i == 38 else 0); c_blit(im, spr, bx + ox, STAND_Y + oy); shadow(im, bx + 3, 26)
        # ---- 3-4.5 s: tiptoe toward the worm; the worm notices ----
        elif i < 60:
            noticed = i >= 52
            rig(im, HOOK_Y, WORM_WIDE if noticed else worm)
            bx = LEDGE_X - (i - 42) * 1.0
            k = (i - 42) % 6; legs = LEG_B if k < 3 else LEG_C; up = 2 if k in (1, 2, 4, 5) else 0
            spr, ox, oy = bird(legs=legs, hdy=-1 if k in (0, 3) else 0); c_blit(im, spr, bx + ox, STAND_Y - up + oy)
            shadow(im, bx + 3, 26)
        # ---- 4.5-5.5 s: anticipation, peck-grab, yank ----
        elif i < 69:
            if i < 65:                                          # rear back
                rig(im, HOOK_Y, WORM_WIDE)
                spr, ox, oy = bird(hdx=2, hdy=-3, lid=None); c_blit(im, spr, bx + ox, STAND_Y + oy)
            elif i == 65:
                rig(im, HOOK_Y, WORM_WIDE)
                spr, ox, oy = bird(head=HEAD_OPEN, hdx=-1, hdy=5); c_blit(im, spr, bx + ox, STAND_Y + oy)
            elif i == 66:
                rig(im, HOOK_Y, WORM_WIDE)
                spr, ox, oy = bird(head=HEAD_OPEN, hdx=-3, hdy=11); c_blit(im, spr, bx + ox, STAND_Y + oy)
            else:                                               # beak closed on the worm
                rig(im, HOOK_Y, None)
                spr, ox, oy = bird(hdx=-3, hdy=11); c_blit(im, spr, bx + ox, STAND_Y + oy)
                c_blit(im, WORM_WIDE, HX - 3, HOOK_Y + 4)
            shadow(im, bx + 3, 26)
        # ---- 5.5-8.5 s: hauled up, dangle + spin, look at the viewer, stretch, snap ----
        elif i < 101:
            if i < 76:                                          # yank: beak from y=43 to 20 with overshoot into the notch
                path = [43, 31, 19, 16, 18, 20, 21]; by = path[i - 69]; sway = 0
                if by > 22: rig(im, by - 5, None)               # thread visible until the hook enters the notch
                flip = False; wing = WING_UP if (i % 2) else WING_DOWN; legs = LEG_PED_A if i % 2 else LEG_PED_B; gaze = 0; lid = None
                if i == 69: puff(im, bx + 8, H - 1, 0.2); puff(im, bx + 20, H - 1, 0.2)
            elif i < 94:                                        # dangle; mirror flip every 5 frames; eye finds the viewer at 84
                by = 21 + (1 if (i // 3) % 2 else 0); flip = ((i - 76) // 5) % 2 == 1; sway = round(2 * math.sin((i - 76) * 0.7))
                wing = WING_UP if (i // 2) % 2 else WING_DOWN; legs = LEG_PED_A if (i // 2) % 2 else LEG_PED_B
                gaze = 3 if i >= 84 else 1; lid = None
            else:                                               # stretch: the worm gives, the bird sinks, legs reach for the floor
                t = min(1, (i - 94) / 4); by = 21 + round(6 * ease(t)); flip = False; sway = (i % 2) if i >= 98 else 0   # taut: toes touch, line quivers
                wing = WING_UP if i % 2 else WING_DOWN; legs = LEG_REACH if i >= 96 else LEG_PED_A; gaze = 0; lid = None
                dots(im, [(HX + 1 + sway, y) for y in range(NOTCH_B + 1, by + 1)], PK[2])      # taut worm, tail in the beak
                dots(im, [(HX + sway, y) for y in range(NOTCH_B + 1, by + 1)], PK[1])
                dots(im, [(HX - 1 + sway, y) for y in range(NOTCH_B + 1, by + 1)], PK[0])
            spr, ox, oy = bird('hang', legs=legs, wing=wing, gaze=gaze, lid=lid)
            if flip: spr = hflip(spr); tip = spr.width - 1 - (4 - ox)
            else: tip = 4 - ox
            c_blit(im, spr, HX - tip + sway, by + oy)
        # ---- 8.5-9 s: snap, plop, feathers, dizzy ----
        elif i < 108:
            j = i - 101
            if j < 2: spr, ox, oy = bird('flat', lid='shut'); yy = H - 25; puff(im, HX, NOTCH_B + 4, 0.3 + 0.4 * j)   # worm whips into the notch
            elif j == 2: spr, ox, oy = bird(hdy=-2, lid='dizzy'); yy = STAND_Y
            else: spr, ox, oy = bird(lid='dizzy', gaze=(0, 2)[(j // 2) % 2], hdx=(-1, 1)[(j // 2) % 2]); yy = STAND_Y
            c_blit(im, spr, bx + ox, yy + oy); shadow(im, bx + 2, 30 if j < 2 else 26)
            if j < 3: puff(im, bx + 2, H - 1, 0.2 + 0.3 * j); puff(im, bx + 28, H - 1, 0.2 + 0.3 * j)
            feathers(im, j, bx + 10, 26)
        # ---- 9-11 s: the bait comes back bigger; bird looks at worm, at viewer, at worm ----
        elif i < 133:
            j = i - 108
            if j < 9: hy = -14 + (28 + 14) * ease(j / 8)
            else: hy = 28
            rig(im, hy, WORM_BIG)
            feathers(im, i - 101, bx + 10, 26)
            if j < 5: gaze, lid, hdx = (0, 2)[(j // 2) % 2], 'dizzy', (-1, 1)[(j // 2) % 2]
            elif j < 11: gaze, lid, hdx = 0, None, 0
            elif j < 21: gaze, lid, hdx = 3, None, 0
            else: gaze, lid, hdx = 0, None, 0
            blink = 'shut' if j in (11, 21) else lid
            spr, ox, oy = bird(gaze=gaze, lid=blink, hdx=hdx, hdy=bob(i, 16, 1)); c_blit(im, spr, bx + ox, STAND_Y + oy)
            shadow(im, bx + 3, 26)
        # ---- 11-12 s: turn, march to the ledge, climb back down feet last; worm reels up ----
        else:
            j = i - 133
            hy = 28 - 12 * max(0, j - 4) if j >= 4 else 28
            if hy > -14: rig(im, hy, WORM_BIG)
            if j < 6:
                bx = min(LEDGE_X, bx + 3.0)
                spr, ox, oy = bird(legs=LEG_B if (j // 2) % 2 else LEG_A, hdy=-1 if j % 2 else 0)
                spr = hflip(spr); c_blit(im, spr, bx + 26 - (spr.width + ox), STAND_Y + oy); shadow(im, bx + 3, 26)
            elif j < 8:
                spr, ox, oy = bird(legs=LEG_B); spr = hflip(spr); c_blit(im, spr, bx + 26 - (spr.width + ox), H - 20 + 4 * (j - 6) + oy)
            elif j == 8:
                spr, ox, oy = bird(); spr = hflip(spr); c_blit(im, spr, bx + 26 - (spr.width + ox), H - 12 + oy)
                c_blit(im, CLAW, bx + 4, H - 3); c_blit(im, CLAW, bx + 13, H - 3)
            elif j == 9:
                puff(im, bx + 8, H - 1, 0.4); puff(im, bx + 18, H - 1, 0.4)      # j == 10 (last frame) stays empty
    return c
