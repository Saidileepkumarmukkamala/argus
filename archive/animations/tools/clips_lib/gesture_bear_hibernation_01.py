"""Bear hibernation — gesture: go to sleep. The notch is the cave; the bear hauls himself and his blanket into it,
then his slippers fall out and wake him. ~44 px quadruped bear, 4-tone fur + tan muzzle, eye glint, rim outline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

F = ramp((132, 86, 52))                      # fur: shadow, base, light, highlight
T = ramp((214, 172, 118))                    # muzzle / tummy / pads
K = ramp((158, 58, 82))                      # blanket plum
PAL2 = {'D': F[0], 'm': F[1], 'l': F[2], 'h': F[3], 'M': (104, 66, 42),   # M = far-limb fur (darker mid)
        'u': T[0], 't': T[1], 'v': T[2],
        'n': (26, 20, 24), 'w': (250, 250, 245), 'b': (28, 22, 30), 'W': (255, 255, 255),
        'e': (196, 124, 116), 'r': (140, 46, 58), 'q': (226, 128, 138), 'z': (236, 228, 210),
        'A': K[0], 'a': K[1], 'c': K[2], 'C': K[3], 'y': (238, 218, 172), 'Y': (186, 160, 118),
        's': (92, 152, 204), 'S': (54, 98, 150), 'x': (140, 196, 236), 'p': (250, 246, 240)}
S = lambda rows: sprite(rows, PAL2)
RIM = (96, 70, 56)
RIM_B = (104, 60, 80)
RIM_S = (60, 90, 130)

# ---------- side view (walk in, facing right) ----------
BODY_SIDE = S("""
.........hhhhhhhhhh..........
......hhhlllllllllllh........
....hhllllmmmmmmmmmmll.......
...hlllmmmmmmmmmmmmmmml......
..hllmmmmmmmmmmmmmmmmmml.....
..hlmmmmmmmmmmmmmmmmmmmml....
.hlmmmmDmmmmmmmmmmmmmmmmmm...
hlmmmmmmDmmmmmDmmmmmmmmmmm...
.lmmmmmmmmmmmmmDmmmmmmmmmm...
.lmmmmmmmmmmmmmmmmmmDmmmDD...
.lmmmmmDmmmmmmmmmmmmmDmDDD...
.DmmmmmmDmmmmmDmmmmmmmDDDD...
.DmmmmmmmmmmmmmDmmmmmDDDDD...
.DDmmmmmmmmmmmmmmmmmDDDDD....
.DDmmmmmmmmmmmmmmmmmDDDDD....
..DDDmmmmmmmmmmmmmmDDDDDD....
""")
HEAD_SIDE = S("""
..hhh.....hhh.....
.hleeh...hleeh....
.hleelhhhlleelh...
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmwwwwmmmmmmlh
.hlmmmwWbwmmmmmmttl
.lmmmmwbbwmmmmmtttnn
.lmmmmmwwmmmmmttttnn
.lmmmmmmmmmmmtttttuD
.DmmmmmmmmmmmtttuuD.
.DmmmmmmmmmmmtuuuD..
..DmmmmmmmmmDDDDD...
...DDDmmmmDDD.......
.....DDDDD..........
""")
HEAD_SIDE_SLEEPY = S("""
..hhh.....hhh.....
.hleeh...hleeh....
.hleelhhhlleelh...
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmDDDmmmmmmlh
.hlmmmwwbwmmmmmmttl
.lmmmmwbbwmmmmmtttnn
.lmmmmmwwmmmmmttttnn
.lmmmmmmmmmmmtttttuD
.DmmmmmmmmmmmtttuuD.
.DmmmmmmmmmmmtuuuD..
..DmmmmmmmmmDDDDD...
...DDDmmmmDDD.......
.....DDDDD..........
""")
LEGS_A = S("""
..MMMMM....lmmmmD.........MMMMM....lmmmmD..
..MMMMM....lmmmmD.........MMMMM....lmmmmD..
.MMMMM....lmmmmmD........MMMMM.....lmmmmD..
.MMMMM....lmmmmmD........MMMMM.....lmmmmmD.
MMMMM.....lmmmmmD.......MMMMM......lmmmmmD.
MMMMM....lmmmmmmD.......MMMMM......lmmmmmmD
MMMMM....lmmuuumD......MMMMM.......lmmuuumD
MMMMMM...DDuuuuD.......MMMMMM......DDuuuuD.
""")
LEGS_B = S("""
....MMMMM..lmmmmD...........MMMMM..lmmmmD..
....MMMMM..lmmmmD...........MMMMM..lmmmmD..
....MMMMM.lmmmmmD...........MMMMM.lmmmmmD..
....MMMMM.lmmmmmD...........MMMMM.lmmmmmD..
....MMMMMlmmmmmmD...........MMMMMlmmmmmmD..
....MMMMMlmmmmmmD...........MMMMMlmmmmmmD..
....MMMMlmmuuumD............MMMMlmmuuumD...
....MMMMDDuuuuD.............MMMMDDuuuuD....
""")

# ---------- front view (sit under the cave, yawn, rub, reach) ----------
HEAD_FRONT = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmwwwwmmmmwwwwlh
.lmmwWbwwmmmwWbwml
.lmmwbbwwmmmwbbwml
.lmmmwwwwtttwwwwml
.DmmmmmttvtttmmmmD
.DmmmmmtvnnnttmmmD
.DmmmmmtttnttttmmD
..DmmmmuttttuummD.
..DDmmmmuuuuummDD.
...DDDDDDDDDDDDD..
""")
HEAD_SLEEPY = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmDDDDmmmmDDDDlh
.lmmwwbwwmmmwwbwml
.lmmwbbwwmmmwbbwml
.lmmmwwwwtttwwwwml
.DmmmmmttvtttmmmmD
.DmmmmmtvnnnttmmmD
.DmmmmmtttnttttmmD
..DmmmmuttttuummD.
..DDmmmmuuuuummDD.
...DDDDDDDDDDDDD..
""")
HEAD_YAWN = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmmmmmmmmmmmmmlh
.lmmmDDDmmmmmDDDml
.lmmmmmmmmmmmmmmml
.lmmmmmttvnnntmmml
.DmmmmmtvrrrrtmmmD
.DmmmmmtrrrrrrtmmD
.DmmmmmtrrqqrrtmmD
..DmmmmurrqqrummD.
..DDmmmmurrrrmmDD.
...DDDDDDDDDDDDD..
""")
HEAD_YAWN_MID = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmmDDDmmmmDDDmlh
.lmmwwwwmmmmwwwwml
.lmmmwwwwmmmwwwwml
.lmmmmmttvnnntmmml
.DmmmmmtvtnntmmmmD
.DmmmmmttrrrrtmmmD
.DmmmmmtrrqqrtmmmD
..DmmmmuttttummmD.
..DDmmmmuuuuummDD.
...DDDDDDDDDDDDD..
""")
HEAD_RUB = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmDDDDmmmmmmmmlh
.lmmwwbwwmmmmmmmml
.lmmwbbwwmmmmmmmml
.lmmmwwwwtttmmmmml
.DmmmmmttvtttmmmmD
.DmmmmmtvnnnttmmmD
.DmmmmmtttnttttmmD
..DmmmmuttttuummD.
..DDmmmmuuuuummDD.
...DDDDDDDDDDDDD..
""")
HEAD_GRUMPY = S("""
..hhhh......hhhh..
.hleelh....hleelh.
.hleeelhhhhleeelh.
..hllllllllllllh..
..hlmmmmmmmmmmmlh.
.hlmmmmmmmmmmmmmlh
.hlmDDDDmmmmDDDDlh
.lmmwbbwwmmmwbbwml
.lmmwbbwwmmmwbbwml
.lmmmwwwwtttwwwwml
.DmmmmmttvtttmmmmD
.DmmmmmtvnnnttmmmD
.DmmmmmtttnttttmmD
..DmmmmuttttuummD.
..DDmmmmuuuuummDD.
...DDDDDDDDDDDDD..
""")
BODY_FRONT = S("""
.......hhlllllllllll......
.....hllmmmmmmmmmmmmml....
....hlmmmmmmmmmmmmmmmml...
...hlmmmmmmtttttmmmmmmml..
..hlmmmmmmttvvvvttmmmmmml.
..lmmmmmmmtvvvvvvttmmmmmmD
..lmmmmmDmtvvvvvvttmmmmmmD
..lmmmmmmmtvvvvvvttmmmDmmD
..lmmmmmmmttvvvvtttmmmmmDD
..lmmmmmmmmttttttttmmmmmDD
..DmmmmmmmmmttttttmmmmmmDD
..DmmmmmmDmmmmmmmmmmDmmmDD
..DDmmmmmmmmmmmmmmmmmmDDDD
...DDDDDDDDDDDDDDDDDDDDDD.
""")
FEET = S("""
lmmmmmD..............lmmmmmD
lmuuumD..............lmuuumD
DmuvumD..............DmuvumD
DDuuuDD..............DDuuuDD
.DDDDD................DDDDD.
""")
FEET_TUCK = S("""
..lmmmmD..........lmmmmD..
..lmuuuD..........lmuuuD..
..DDuuDD..........DDuuDD..
""")
ARM_REST = S("""
hlmm.
lmmmm
lmmmmD
DmmmmD
DmuumD
.DuuD.
""")
ARM_UP = S("""
.DuuD.
DmuumD
DmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
lmmmmD
hlmmmD
.hlmmD
""")
ARM_RUB = S("""
..DDD
.DmuuD
DmuumD
lmmmmD
lmmmmD
lmmmD.
lmmD..
""")
# arm hanging out of the cave: column + paw; length varies
PAW = S("""
DmmmmmmD
DmmmmmmD
DmuuuumD
DuuvvuuD
.zuuuuz.
..z..z..
""")
PAW_GRIP = S("""
DmmmmmmD
DmmmmmmD
DmuuuumD
DuuuuuuD
.DuuuuD.
..DDDD..
""")
SLIPPER = S("""
....SSSS.....
...SxppxS....
..SsxppxsS...
.SsssxxsssSSS
SssssssssSnnS
SSSSSSSSSSSSS
""")

ARM_TOP = NOTCH_B - 8                            # the arm's top row hides inside the notch
def draw_arm(im, c, ax, paw_bottom, grip=False):
    """Arm hanging out of the cave: fur column from inside the notch down to a paw whose last row is paw_bottom."""
    length = paw_bottom - ARM_TOP - 5
    if length < 1: return
    col = S('\n'.join(['lmmmmmmD'] * length))
    spr, mx, my = assemble([(col, 0, 0), (PAW_GRIP if grip else PAW, 0, length - 1)])
    c.blit(im, outline(spr, RIM), ax + mx - 1, ARM_TOP + my - 1)

def bear_side(step):
    parts = [(LEGS_A if step == 0 else LEGS_B, 1, 19), (BODY_SIDE, 0, 6), (HEAD_SIDE if step != 2 else HEAD_SIDE_SLEEPY, 22, 0)]
    spr, mx, my = assemble(parts)
    return outline(spr, RIM), mx, my

def bear_sit(head=HEAD_FRONT, arms='rest', feet=FEET, rub=0):
    """Sitting front view, ~30 px tall: head over belly, arms at the sides. Origin = top-left of head box."""
    parts = [(BODY_FRONT, 0, 13), (feet, -1, 26), (head, 4, 0)]
    if arms == 'rest':
        parts += [(ARM_REST, -2, 17), (hflip(ARM_REST), 23, 17)]
    elif arms == 'up':
        parts += [(ARM_UP, -1, 3), (hflip(ARM_UP), 21, 3)]
    elif arms == 'rub':
        parts += [(ARM_RUB, 3 + rub, 7), (hflip(ARM_REST), 23, 17)]
    spr, mx, my = assemble(parts)
    return outline(spr, RIM), mx, my

def blanket(im, gx, top_y, rem, i, flutter=True):
    """Plum striped blanket: a vertical piece hanging at column gx from top_y, then lying left along the floor.
    rem = visible length in px (the rest is inside the cave). Drawn on a layer, outlined once, then blitted."""
    if rem <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = lay.load()
    floor_top = H - 6
    vlen = max(0, min(rem, floor_top - top_y))
    flen = rem - vlen
    def cloth(x, y, s, shade):                    # shade: 0 light edge, 1 base, 2 shadow edge
        if not (0 <= x < W and 0 <= y < H): return
        stripe = (s // 8) % 3 == 0
        if s >= rem - 2:                          # fringe: tassels every other px, fluttering
            if (x + y + (i // 3 if flutter else 0)) % 2: return
            px[x, y] = PAL2['Y'] + (255,); return
        if stripe: px[x, y] = (PAL2['y'] if shade < 2 else PAL2['Y']) + (255,)
        else: px[x, y] = (PAL2['c'], PAL2['a'], PAL2['A'])[shade] + (255,)
    for k in range(int(vlen)):                    # hanging piece
        y = top_y + k
        for j in range(6): cloth(gx - 3 + j, y, k, 0 if j == 0 else (2 if j == 5 else 1))
    if flen > 0:                                  # floor piece, bend at gx+2
        for k in range(int(flen)):
            x = gx + 2 - k
            for j in range(6): cloth(x, floor_top + j, vlen + k, 0 if j == 0 else (2 if j >= 4 else 1))
        if vlen > 0:                              # fold shadow at the bend
            for j in range(6):
                if 0 <= gx + 2 < W: px[gx + 2, floor_top + j] = PAL2['A'] + (255,)
    im.paste(outline(lay, RIM_B), (-1, -1), outline(lay, RIM_B))

def slipper(im, c, x, y, flipped=False):
    spr = outline(hflip(SLIPPER) if flipped else SLIPPER, RIM_S)
    c.blit(im, spr, x - 1, y - 1)

def build():
    c = Clip('gesture_bear_hibernation_01', 12.0)
    FLOOR = H - 1
    rest_x = 62                                       # where the bear parks (rear); also where the blanket end lies
    L = 83                                            # blanket length: 30 hang + 2 x 24 tugs + 5 corner
    sit_x, sit_y = rest_x + 6, NOTCH_B + 1            # sit pose box (30 tall) fills the space under the cave
    grab_x = rest_x + 4                               # column the paw works at
    slip1_x, slip2_x = 100, 122
    # segments
    WALK, SIT, YAWN, RUB, REACH, RISE, HOLD = 22, 4, 12, 8, 5, 12, 3
    t_sit = WALK; t_yawn = t_sit + SIT; t_rub = t_yawn + YAWN; t_reach = t_rub + RUB; t_rise = t_reach + REACH
    t_hold = t_rise + RISE; t_tug = t_hold + HOLD; TUG = 8
    t_breathe = t_tug + 3 * TUG; t_slip1 = t_breathe + 8; t_slip2 = t_slip1 + 8; t_feel = t_slip2 + 8
    t_grab = t_feel + 9; t_tuck = t_grab + 8; t_end = t_tuck + 4
    assert t_end <= c.n, t_end
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= t_end: continue
        if i < t_sit:                                      # shuffle in from the left, blanket trailing off-screen
            t = ease(i / (t_sit - 1)) * 0.35 + (i / (t_sit - 1)) * 0.65
            x = -50 + (rest_x + 50) * t
            step = (i // 4) % 2
            blanket(im, int(x) + 8, FLOOR - 13 + (i // 4) % 2, L, i)
            spr, mx, my = bear_side(2 if (i // 12) % 2 else step)
            c.blit(im, spr, x + mx, FLOOR + 1 - 27 + my + ((i // 4) % 2))
            shadow(im, x + 4, 40)
        elif i < t_yawn:                                   # sit up: lets go of the blanket, it drops flat
            j = i - t_sit; t = ease(j / (SIT - 1))
            blanket(im, grab_x, int(FLOOR - 13 + 13 * t), L, i)
            spr, mx, my = bear_sit(HEAD_SLEEPY)
            c.blit(im, spr, sit_x + mx, sit_y + my + int(4 * (1 - t)))
            shadow(im, sit_x + 2, 28)
            if j == SIT - 1: puff(im, sit_x + 2, FLOOR, 0.2); puff(im, sit_x + 26, FLOOR, 0.2)
        elif i < t_rub:                                    # yawn: open, hold, close
            j = i - t_yawn
            head = HEAD_YAWN_MID if j in (0, 1, 12, 13) else (HEAD_YAWN if 2 <= j < 12 else HEAD_SLEEPY)
            blanket(im, grab_x, FLOOR, L, i)
            spr, mx, my = bear_sit(head, arms='rest' if j < 2 or j >= 12 else 'rub', rub=0)
            c.blit(im, spr, sit_x + mx, sit_y + my + bob(i, 12, 1))
            shadow(im, sit_x + 2, 28)
        elif i < t_reach:                                  # rub one eye
            j = i - t_rub
            blanket(im, grab_x, FLOOR, L, i)
            spr, mx, my = bear_sit(HEAD_RUB, arms='rub', rub=(0, 1, 1, 0, -1, -1)[j % 6])
            c.blit(im, spr, sit_x + mx, sit_y + my + bob(i, 12, 1))
            shadow(im, sit_x + 2, 28)
        elif i < t_rise:                                   # anticipation crouch, then arms go up into the cave
            j = i - t_reach
            blanket(im, grab_x, FLOOR, L, i)
            if j < 2: spr, mx, my = bear_sit(HEAD_SLEEPY); dy = 2
            else: spr, mx, my = bear_sit(HEAD_SLEEPY, arms='up'); dy = 0
            c.blit(im, spr, sit_x + mx, sit_y + my + dy)
            shadow(im, sit_x + 2, 28)
        elif i < t_hold:                                   # haul up into the notch, ease-out; feet tuck, dust
            j = i - t_reach - REACH; t = ease(j / (RISE - 1))
            blanket(im, grab_x, FLOOR, L, i)
            spr, mx, my = bear_sit(HEAD_SLEEPY, arms='up', feet=FEET_TUCK if j > 3 else FEET)
            c.blit(im, spr, sit_x + mx, sit_y + my - int(40 * t))
            if j == 1: puff(im, sit_x + 4, FLOOR, 0.1); puff(im, sit_x + 24, FLOOR, 0.1)
            if j < 4: shadow(im, sit_x + 2, 28)
        elif i < t_tug:                                    # bear is in; blanket lies across the floor
            blanket(im, grab_x, FLOOR, L, i)
        elif i < t_breathe:                                # three tugs: paw down, grab, yank
            j = i - t_tug; k = j // TUG; p = j % TUG
            if p < 3: reach = ease(p / 2)                  # descend
            elif p < 6: reach = 1 - ease((p - 3) / 2)      # yank
            else: reach = 0
            if k == 0:                                     # first tug lifts the end off the floor
                paw_y = NOTCH_B + int(30 * reach)          # paw bottom
                top_y = FLOOR if p < 3 else NOTCH_B + int(30 * reach)
                u = 0
            else:
                paw_y = NOTCH_B + int(24 * reach)
                u = 24 * (k - 1) + (0 if p < 3 else int(24 * (1 - reach)))
                top_y = NOTCH_B
            blanket(im, grab_x, top_y, L - u, i)
            if p < 6: draw_arm(im, c, grab_x - 4, paw_y, grip=p >= 3)
        else:
            rem = L - 46                                   # 7 px corner hangs out
            awake = i >= t_slip2 + 6
            breath = 0 if awake else bob(i, 14, 1)
            if i >= t_tuck: rem = max(0, rem - 2 * (i - t_tuck + 1))
            blanket(im, grab_x, NOTCH_B, rem + breath, i, flutter=not awake)
            # slippers
            def drop(t0, sx, flipped):
                if i < t0: return None
                j = i - t0
                if j < 6: y = NOTCH_B - 5 + int(1.1 * j * j)
                elif j < 9: y = FLOOR - 4 - (3, 4, 2)[j - 6]
                else: y = FLOOR - 4
                y = min(y, FLOOR - 4)
                if j == 6: puff(im, sx + 6, FLOOR, 0.2)
                if j == 9: puff(im, sx + 6, FLOOR, 0.35)
                return y
            s1 = drop(t_slip1, slip1_x, False); s2 = drop(t_slip2, slip2_x, True)
            if i < t_grab:
                if s1 is not None: slipper(im, c, slip1_x, s1)
                if s2 is not None: slipper(im, c, slip2_x, s2, True)
            # paw feels around, can't reach; then stretches and grabs both
            if t_feel <= i < t_grab:
                j = i - t_feel
                reach = ease(min(1, j / 3)) * 24
                ax = grab_x + int(ease(min(1, j / 4)) * 26) + (0, 1, 2, 1, 0, -1, -2, -1)[j % 8]
                wob = (0, 1, 2, 1, 0, 0)[j % 6] if j >= 3 else 0
                draw_arm(im, c, ax - 4, NOTCH_B + int(reach) + wob)
            elif t_grab <= i < t_tuck:
                j = i - t_grab
                s1x, s2x, sy = slip1_x, slip2_x, FLOOR - 4
                if j < 2:                                  # strain: arm stretches to the floor, drifting right
                    reach = 24 + int(ease((j + 1) / 2) * 6); ax = grab_x + 26 + int(ease((j + 1) / 2) * 6)
                elif j < 5:                                # sweep right along the floor, shoving slipper 1 along
                    reach = 30; ax = grab_x + 32 + int(ease((j - 1) / 3) * 20); s1x = max(slip1_x, ax + 2)
                else:                                      # whip up with both
                    reach = max(0, 30 - int(ease((j - 4) / 4) * 46)); ax = grab_x + 52; s1x = ax - 9; s2x = ax + 2
                    sy = NOTCH_B + reach - 5
                    if j == 5: puff(im, ax, FLOOR, 0.3)
                if reach > 0:
                    if j >= 5: slipper(im, c, s1x, sy); slipper(im, c, s2x, sy + 1, True)
                    else: slipper(im, c, s1x, sy); slipper(im, c, s2x, sy, True)
                    draw_arm(im, c, ax - 4, NOTCH_B + reach, grip=j >= 4)
    return c
