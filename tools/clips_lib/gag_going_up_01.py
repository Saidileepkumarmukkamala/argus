"""Going Up — the notch is an elevator shaft. Two commuters queue; the cabin arrives already occupied by a sleeping bear.
Second trip: they ride up. Third trip: the bear comes back down wearing the tiny one's hat."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *
from PIL import Image, ImageDraw

BUCKET = 'gag'

# ---------- palettes ----------
SK = ramp((238, 196, 160))                      # skin
CT = ramp((58, 108, 142))                       # tall's teal coat
PT = ramp((44, 48, 66))                         # trousers
MU = ramp((226, 150, 58))                       # tiny's mustard coat
HT = ramp((74, 62, 100))                        # bowler hat
FU = ramp((152, 102, 58))                       # bear fur
SN = ramp((224, 192, 142))                      # bear snout / belly
BC = ramp((146, 88, 48))                        # briefcase leather
PAL2 = {
    'K': SK[0], 'k': SK[1], 'L': SK[2], 'M': SK[3],
    'C': CT[0], 'c': CT[1], 'D': CT[2], 'E': CT[3],
    'Q': PT[0], 'q': PT[1], 'U': PT[2],
    'N': MU[0], 'n': MU[1], 'O': MU[2], 'V': MU[3],
    'A': HT[0], 'a': HT[1], 'e': HT[2], 'i': HT[3],
    'F': FU[0], 'f': FU[1], 'g': FU[2], 'j': FU[3],
    'S': SN[0], 's': SN[1], 't': SN[2], 'u': SN[3],
    'B': BC[0], 'x': BC[1], 'X': BC[2],
    'H': (58, 40, 30), 'h': (92, 66, 46),                      # tall's hair
    'R': (118, 74, 44), 'Y': (170, 118, 70),                   # tiny's hair
    'w': (250, 250, 245), 'W': (255, 255, 255), 'b': (22, 18, 30), 'r': (196, 60, 62),
    'z': (150, 150, 165),                                      # eyelid line (blink)
}
S = lambda rows: sprite(rows, PAL2)

# ---------- tall commuter (faces right, 3/4 view; 10 wide, 25 tall assembled) ----------
T_HEAD = S("""
....hHHH..
...hHHHHHH
..HHLkkkkH
..HKLkbkwW
..KKLkbkwb
...KLkkkwb
...KkkkkkK
....KkkrkK
.....KkkK.
""")
T_HEAD_DOWN = S("""
....hHHH..
...hHHHHHH
..HHLkkkkH
..HKLkkkkw
..KKLkbkwb
...KLkbkwb
...KkkkkkK
....KkkrkK
.....KkkK.
""")
T_HEAD_BLINK = S("""
....hHHH..
...hHHHHHH
..HHLkkkkH
..HKLkkkkk
..KKLkzkzz
...KLkkkkk
...KkkkkkK
....KkkrkK
.....KkkK.
""")
T_BODY = S("""
.....Kkk..
..DDDcccC.
.DDcwwrwcC
.DccwwrwcC
.DcccwrccC
.DccccccCC
.DccccccCC
.DccccccCC
.DccccccCC
.DccccccCC
.DCCCCCCCC
""")
T_ARM = S("""
Dc.
DcC
.cC
.cC
.cC
.cC
.CC
.Kk
""")
T_CASE = S("""
..Xx..
.XXXXB
XxxxxB
XxxxxB
XXxxxB
.BBBB.
""")
T_LEGS_STAND = S("""
..Uq.Uq...
..Uq.Uq...
..Uq.Uq...
..Uq.Uq...
..Qq.Qq...
.bbb.bbb..
""")
T_LEGS_A = S("""
...UqUq...
..Uq..Uq..
.Uq....Uq.
.Qq....Qq.
Qq......Qq
bbb....bbb
""")
T_LEGS_B = S("""
..UqUq....
..UqUq....
..Uq.Uq...
..Uq.Uq...
..Qq..Qq..
.bbb..bbb.
""")

def tall(legs='stand', head='norm', lean=0, walk_phase=0):
    """Assemble the tall commuter; returns (outlined sprite, dx, dy). Feet on the sprite's bottom row."""
    hd = {'norm': T_HEAD, 'down': T_HEAD_DOWN, 'blink': T_HEAD_BLINK}[head]
    lg = {'stand': T_LEGS_STAND, 'a': T_LEGS_A, 'b': T_LEGS_B}[legs]
    parts = [(lg, 0, 19), (T_BODY, 0 - lean // 2, 8), (T_ARM, 7 - lean // 2, 10), (T_CASE, 6 - lean // 2, 18 + walk_phase),
             (hd, 0 - lean, 0)]
    spr, mx, my = assemble(parts)
    return outline(spr), mx, my

# ---------- tiny commuter (faces right, big head; 9 wide, 16 tall + hat) ----------
S_HAT = S("""
..eiiiie..
.aeeeeeea.
.arrrrrra.
aeeeeeeeea
""")
S_HEAD = S("""
..YRRRRR.
.YRRRRRRR
.YkkkkkkK
.LkwWkwWK
.LkwbkwbK
.KkkkkkkK
..KkkrkK.
...KkkK..
""")
S_HEAD_FRONT = S("""
..YRRRRR.
.YRRRRRRR
.YkkkkkkK
.LwWkkwWK
.LwbkkwbK
.KkkkkkkK
..KkrrkK.
...KkkK..
""")
S_HEAD_BLINK = S("""
..YRRRRR.
.YRRRRRRR
.YkkkkkkK
.LkkkkkkK
.LkzzkzzK
.KkkkkkkK
..KkkrkK.
...KkkK..
""")
S_BODY = S("""
..OOnnN..
.OnwwnnN.
.OnnnnnN.
.OnnnnnNN
.ONNNNNN.
""")
S_BODY_SHRUG = S("""
Ok.....kN
.OnnnnnN.
.OnwwnnN.
.OnnnnnNN
.ONNNNNN.
""")
S_LEGS_STAND = S("""
..Uq.Uq..
..Qq.Qq..
.bbb.bbb.
""")
S_LEGS_TIPTOE = S("""
..Uq.Uq..
..Uq.Uq..
..Qq.Qq..
..bb.bb..
""")
S_LEGS_A = S("""
.Uq...Uq.
Qq.....Qq
bb.....bb
""")
S_LEGS_B = S("""
..UqUq...
..Uq.Qq..
.bbb.bbb.
""")

def tiny(legs='stand', head='norm', hat=True, lean=0, shrug=0):
    hd = {'norm': S_HEAD, 'front': S_HEAD_FRONT, 'blink': S_HEAD_BLINK}[head]
    lg = {'stand': S_LEGS_STAND, 'tiptoe': S_LEGS_TIPTOE, 'a': S_LEGS_A, 'b': S_LEGS_B}[legs]
    body = S_BODY_SHRUG if shrug else S_BODY
    top = 4 if hat else 0
    parts = [(lg, 0, top + 8 + 5), (body, 0, top + 8 - shrug), (hd, 0 - lean, top - shrug)]
    if hat: parts.append((S_HAT, 0 - lean, 0 - shrug))
    spr, mx, my = assemble(parts)
    return outline(spr), mx, my

# ---------- bear (front view, asleep; 22 wide, 25 tall) ----------
B_HEAD = S("""
.jgg.......ggF..
jgffg.....gfffF.
.gfffffffffffFF.
gffffffffffffff.
gfffffffffffffF.
gfbbbffffffbbbF.
gfgfffssssfffgF.
gffffsuuuussfffF
.gfffsutbbtsfFF.
.gffffsbbbssFF..
..gfffsssssFF...
...gFFFFFFF.....
""")
B_BODY = S("""
....gjjjjjjjjjjff....
..gfffffffffffffffF..
.gffffffffffffffffFF.
.gffffffffffffffffFF.
gfffffffffffffffffFFF
gfffffffffffffffffFFF
gfffffffffffffffffFFF
.gffffffffffffffffFF.
.gffffffffffffffffFF.
..gffffffffffffffFF..
..gfff.........fffF..
..FFFF.........FFFF..
""")
B_BELLY = S("""
...ssssss...
.ssuuuutsss.
.suuuuuttss.
suuuuuuttsss
suuuuuutttss
.suuuuuttsS.
.ssttttttsS.
...ssssss...
""")

def bear(i, hat=False):
    """Sleeping bear: belly rises 1 px on a slow cycle. Bubble handled by the caller."""
    up = bob(i, 24, 1)
    parts = [(B_BODY, 0, 12), (B_BELLY, 5, 14 - up), (B_HEAD, 3, 0)]
    if hat: parts.append((S_HAT, 6, -1))          # bowler sits between the ears
    spr, mx, my = assemble(parts)
    return outline(spr), mx, my

# ---------- cabin ----------
CAB_W, CAB_H = 30, 30
CAB_X = 108                                       # cabin left edge; doors open over x 109..136
DOCK_Y, HIDE_Y = 21, -9                           # docked: top frame sits inside the slit, bottom on the floor; hidden: fully in the notch
MT = ramp((142, 148, 166))                        # cabin metal
DM = ramp((112, 122, 146))                        # door metal
GLOW = (255, 238, 178)

def make_cabin():
    im = Image.new('RGBA', (CAB_W, CAB_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, CAB_W - 1, CAB_H - 1), fill=MT[1] + (255,))
    d.line((0, 0, CAB_W - 1, 0), fill=MT[2] + (255,)); d.line((0, 0, 0, CAB_H - 1), fill=MT[2] + (255,))
    d.line((0, CAB_H - 1, CAB_W - 1, CAB_H - 1), fill=MT[0] + (255,)); d.line((CAB_W - 1, 0, CAB_W - 1, CAB_H - 1), fill=MT[0] + (255,))
    im.putpixel((0, 0), MT[3] + (255,))
    # lit interior: ceiling light, warm wall gradient, handrail, floor
    for y in range(1, CAB_H - 1):
        t = (y - 1) / (CAB_H - 3)
        col = tuple(int(GLOW[k] * (1 - t) + (198, 160, 112)[k] * t) for k in range(3))
        d.line((1, y, CAB_W - 2, y), fill=col + (255,))
    d.line((1, 1, CAB_W - 2, 1), fill=(255, 250, 220, 255))
    d.line((1, 17, CAB_W - 2, 17), fill=(150, 112, 76, 255))            # handrail
    d.line((1, CAB_H - 2, CAB_W - 2, CAB_H - 2), fill=(126, 96, 68, 255))  # floor
    return outline(im)
CABIN = make_cabin()

def make_door():
    w, h = 14, CAB_H - 2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=DM[1] + (255,))
    d.line((0, 0, 0, h - 1), fill=DM[2] + (255,)); d.line((0, 0, w - 1, 0), fill=DM[2] + (255,))
    d.line((w - 1, 0, w - 1, h - 1), fill=DM[0] + (255,))                 # seam edge
    d.rectangle((0, h - 5, w - 1, h - 1), fill=DM[0] + (255,))            # kick plate
    for y in range(6, h - 6, 5): d.line((2, y, w - 3, y), fill=DM[2] + (255,))   # brushed lines
    d.rectangle((4, 3, 9, 9), fill=(120, 96, 70, 255))                    # window frame shadow
    d.rectangle((5, 4, 8, 8), fill=(178, 214, 232, 255))
    d.line((5, 4, 5, 6), fill=(230, 245, 250, 255)); im.putpixel((6, 4), (230, 245, 250, 255))
    return im
DOOR_L = make_door(); DOOR_R = hflip(DOOR_L)

def draw_cabin(im, c, ytop, door_open, occupants=(), dx=0):
    """occupants: [(sprite, dx, dy, x_in_cabin)] with feet on the interior floor. door_open in 0..14 px. dx: dangle sway."""
    CAB_X = globals()['CAB_X'] + dx
    c.blit(im, CABIN, CAB_X - 1, ytop - 1)
    floor = ytop + CAB_H - 2                         # last interior row
    for spr, mx, my, x in occupants:
        c.blit(im, spr, CAB_X + x + mx, floor + 1 - spr.height)
    o = int(round(door_open))
    if o < 14:
        vis = 14 - o
        c.blit(im, DOOR_L.crop((0, 0, vis, CAB_H - 2)), CAB_X + 1, ytop + 1)
        c.blit(im, DOOR_R.crop((14 - vis, 0, 14, CAB_H - 2)), CAB_X + 1 + 14 + o, ytop + 1)

def draw_slit(im, open_t):
    """Lit slit in the notch underside: open_t 0..1 grows from the centre."""
    if open_t <= 0: return
    half = int(round(13 * min(1.0, open_t))); cx = CAB_X + CAB_W // 2
    dots(im, [(x, NOTCH_B + 1) for x in range(cx - half, cx + half + 1)], GLOW)
    dots(im, [(x, NOTCH_B + 2) for x in range(cx - half + 2, cx + half - 1)], (120, 104, 66))

# ---------- timeline ----------
# cabin trips: (slit_open, descend_start, descend_end, doors_open_start, doors_close_start, rise_start, rise_end, slit_close)
TRIPS = [
    dict(slit=10, d0=13, d1=21, o0=23, c0=37, r0=42, r1=48, sc=48, sway=0.0),   # trip 1: the bear
    dict(slit=53, d0=55, d1=63, o0=65, c0=86, r0=90, r1=96, sc=96, sway=1.4),   # trip 2: empty, the commuters ride up
    dict(slit=105, d0=107, d1=115, o0=117, c0=131, r0=135, r1=141, sc=141, sway=0.8),  # trip 3: bear with hat
]
QX_T, QX_S = 72, 88                                # queue spots (sprite left edges)

def cabin_state(i):
    """Returns (ytop or None if fully hidden, door_open px, slit_t, trip index, cables sway)."""
    for k, T in enumerate(TRIPS):
        if T['slit'] - 1 <= i < T['sc'] + 4:
            slit = 1.0
            if i < T['d0']: slit = (i - T['slit'] + 1) / 3
            elif i >= T['sc']: slit = 1 - (i - T['sc'] + 1) / 3
            y = None
            if T['d0'] <= i < T['r1']:
                if i < T['d1']:
                    t = ease((i - T['d0']) / (T['d1'] - T['d0'] - 1)); y = HIDE_Y + (DOCK_Y - HIDE_Y) * t
                    y = round(y)
                elif i < T['d1'] + 2: y = DOCK_Y + 1                      # overshoot dip into the floor
                elif i < T['r0']: y = DOCK_Y
                else:
                    t = ease((i - T['r0']) / (T['r1'] - T['r0'])); t = t * t
                    y = round(DOCK_Y + (HIDE_Y - DOCK_Y) * t)
            door = 0.0
            if T['o0'] <= i < T['c0']: door = 14 * ease((i - T['o0']) / 3)
            elif T['c0'] <= i < T['r0']: door = 14 * (1 - ease((i - T['c0']) / 3))
            return y, door, slit, k, T['sway'] * max(0.0, 1 - (i - T['d0']) / 16) if i >= T['d0'] else 0.0
    return None, 0.0, 0.0, None, 0.0

def build():
    c = Clip('gag_going_up_01', 12.0)
    for i in range(c.n):
        im = c.frame()
        y, door, slit, trip, sway = cabin_state(i)

        # ---- the queue (outside the cabin) ----
        show_tall = i < 82; show_tiny = i < 75
        # walk in: 0..13, ease-out arrival
        if i < 14:
            t = ease(i / 13)
            tx = -34 + (QX_T + 34) * t; sx = -18 + (QX_S + 18) * t
            legs = ('a', 'b')[(i // 2) % 2]; ph = (i // 2) % 2
            spr, mx, my = tall(legs=legs, walk_phase=ph); c.blit(im, spr, tx + mx, H - 27 + my - ph)
            spr, mx, my = tiny(legs=legs); c.blit(im, spr, sx + mx, H - 22 + my - ph)
            for xx in (tx, sx):
                if i % 4 == 0: puff(im, xx - 2, H - 1, 0.3)
        else:
            tx, sx = QX_T, QX_S
            lean = 0
            if 29 <= i < 38: lean = min(2, (i - 29))
            elif 38 <= i < 41: lean = 2 - (i - 38)
            # tall
            if show_tall:
                if i < 76:
                    head = 'down' if 46 <= i < 58 else ('blink' if i % 41 in (17, 18) else 'norm')
                    tb = bob(i, 16, 1) if i < 21 else 0
                    spr, mx, my = tall(head=head, lean=lean); c.blit(im, spr, tx + mx, H - 27 + my + tb)
                    shadow(im, tx + 1, 9)
                else:                                          # file in: 76..81, squash on the threshold
                    t = ease((i - 76) / 5); x = tx + (CAB_X + 3 - tx) * t
                    legs = ('a', 'b')[(i // 2) % 2]
                    spr, mx, my = tall(legs=legs, walk_phase=(i // 2) % 2)
                    if i == 80: spr = spr.resize((spr.width, spr.height - 1), Image.NEAREST); my += 1
                    c.blit(im, spr, x + mx, H - 27 + my)
                    shadow(im, x + 1, 9)
            # tiny
            if show_tiny:
                if i < 69:
                    tip = 3 if (i < 21 and (i // 6) % 2 == 1) else 0
                    if i < 21 and tip:
                        spr, mx, my = tiny(legs='tiptoe', lean=lean); c.blit(im, spr, sx + mx, H - 23 + my)
                    else:
                        head = 'blink' if i % 37 in (9, 10) else 'norm'
                        shrug = 1 if 50 <= i < 60 else 0
                        spr, mx, my = tiny(head=head, lean=lean, shrug=shrug); c.blit(im, spr, sx + mx, H - 22 + my)
                    shadow(im, sx + 1, 8)
                else:                                          # file in: 69..75
                    t = ease((i - 69) / 5); x = sx + (CAB_X + 15 - sx) * t
                    legs = ('a', 'b')[(i // 2) % 2]
                    spr, mx, my = tiny(legs=legs)
                    if i == 73: spr = spr.resize((spr.width, spr.height - 1), Image.NEAREST); my += 1
                    c.blit(im, spr, x + mx, H - 22 + my)
                    shadow(im, x + 1, 8)

        # ---- the shaft: slit, cables, cabin, occupants, doors ----
        draw_slit(im, slit)
        if y is not None:
            dx = round(sway * math.sin(0.9 * i)) if y < DOCK_Y else 0    # empty cabin dangles on the way down
            occ = []
            if trip == 0 or trip == 2:
                spr, mx, my = bear(i, hat=(trip == 2)); occ.append((spr, mx, my, 3))
            if trip == 1 and i >= 82:
                spr, mx, my = tall(); occ.append((spr, mx, my, 3))
            if trip == 1 and i >= 75:
                head = 'front' if i >= 78 else 'norm'
                spr, mx, my = tiny(head=head); occ.append((spr, mx, my, 15))
            draw_cabin(im, c, y, door, occ, dx)
            if trip in (0, 2):
                # bubble at the nose grows over the hold, pops before the doors close
                T = TRIPS[trip]; bt = i - (T['o0'] + 2)
                if 0 <= bt and i < T['c0'] - 1:
                    nx, ny = CAB_X + 3 + 3 + 11, y + CAB_H - 2 - 26 + 9      # right of the nose
                    r = min(3, 1 + bt // 4)
                    if r == 1: dots(im, [(nx, ny)], (200, 232, 242))
                    elif r == 2: dots(im, [(nx, ny), (nx + 1, ny), (nx, ny + 1), (nx + 1, ny + 1)], (200, 232, 242)); dots(im, [(nx, ny)], (255, 255, 255))
                    else:
                        ring = [(nx + dx, ny + dy) for dx in range(3) for dy in range(3) if (dx, dy) != (1, 1)]
                        dots(im, ring, (200, 232, 242)); dots(im, [(nx, ny)], (255, 255, 255))
                elif i == T['c0'] - 1:
                    nx, ny = CAB_X + 3 + 3 + 11, y + CAB_H - 2 - 26 + 9
                    dots(im, [(nx - 2, ny - 2), (nx + 4, ny - 2), (nx - 2, ny + 4), (nx + 4, ny + 4)], (200, 232, 242))
            if y == DOCK_Y + 1:                                  # landing puffs at both bottom corners
                puff(im, CAB_X + 1, H - 1, 0.35); puff(im, CAB_X + CAB_W - 2, H - 1, 0.35)
            if y >= DOCK_Y: shadow(im, CAB_X - 3, CAB_W + 6)
    return c
