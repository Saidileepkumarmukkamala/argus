"""Boot Shelter — a ladybird beetle is nearly stomped twice by a giant boot, then finds the one place a boot
cannot reach: under the notch. The boot slides in after it and its shin bonks the notch's corner (the notch is
solid: nothing above y=21 gets past x=153). Smug lean, one crumb from the notch on the head. ~29 px beetle."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *
from PIL import ImageDraw

BUCKET = 'gag'

RD = ramp((204, 52, 58))       # shell red
DK = ramp((74, 68, 100))       # head / legs, dark blue-grey
LE = ramp((150, 96, 52))       # boot leather
SO = ramp((78, 74, 84))        # boot sole
PAL2 = {'S': RD[0], 'R': RD[1], 'L': RD[2], 'H': RD[3],
        'd': DK[0], 'D': DK[1], 'l': DK[2], 'h': DK[3],
        'k': (26, 22, 36), 'w': (248, 248, 244), 'W': (255, 255, 255), 'b': (14, 12, 22),
        'n': (240, 200, 92),
        'c': LE[0], 'B': LE[1], 'M': LE[2], 'N': LE[3],
        'Z': SO[0], 'G': SO[1], 'T': SO[2], 'y': (226, 206, 160), 'e': (44, 30, 30)}
S = lambda rows: sprite(rows, PAL2)

# ---------- beetle parts ----------
BODY = S("""
.......RRRRRR.......
....LLLLRRRRRRRR....
...LHHLLRkRRRRRRR...
..LHHLLLRRkRRRRRRS..
..LHLLLLRRkRRRRRRS..
.LLLLLRRRRkRRRkkRRS.
.LLkkLRRRRkRRkkkkRS.
.LRkkRRRRRkRRRkkRSS.
.RRRRkkRRRkRRRRRSSS.
..RRRkkRRRkRRkkRSS..
..SRRRRRRRkRRkkSSS..
...SSRRRRRkRRSSSS...
.....SSSSSSSSSSS....
""")
HEAD_TOP = ["....hhll....", "..hllDDDDd..", ".hlDDDDDDDd."]
HEAD_BOT = [".dDDDDDDDDDd", ".dDDDkkkDDdd", "..dDDDDDDdd.", "...ddddddd.."]
EYES = {'r': [".lDwwwDDwwwd", ".lDwWbDDwWbd", ".lDwwbDDwwbd"],    # looking right (ahead)
        'f': [".lDwwwDDwwwd", ".lDWbwDDWbwd", ".lDwbwDDwbwd"],    # to camera
        'u': [".lDWbwDDWbwd", ".lDwbwDDwbwd", ".lDwwwDDwwwd"],    # up at the notch
        'k': [".lDWwwDDWwwd", ".lDbwwDDbwwd", ".lDbwwDDbwwd"],    # back over the shoulder
        'x': [".lDDDDDDDDDd", ".lDkkkDDkkkd", ".lDDDDDDDDDd"],    # shut
        's': [".lDkkkDDkkkd", ".lDwbwDDwbwd", ".lDwwwDDwwwd"]}    # half-lid, smug
HEADS = {k: S('\n'.join(HEAD_TOP + v + HEAD_BOT)) for k, v in EYES.items()}
ANT = {'n': S("n......n\n.D....D.\n..D..D.."),
       'back': S("n..n....\n.D..D...\n..D..D.."),
       'flat': S("........\nn......n\n.DD..DD."),
       'up': S("..n..n..\n..D..D..\n..D..D..")}
LEG_A = S("""
.....DD.......DD....
....DD.........DD...
...DD...........DD..
..DDD...........DDD.
""")
LEG_B = S("""
......DD....DD......
......DD....DD......
......DD....DD......
.....DDD....DDD.....
""")
LEG_TUCK = S("""
....DD.........DD...
...DDD.........DDD..
""")
LEG_CROSS = S("""
......DD.....DD.....
......DD....DD......
......DD..DDD.......
.....DDDDDD.........
""")
LEG_SPLAY = S("..DD................DD")
ARM_DOWN = S("D.\n.D\n.D\n.D\nDD")
ARM_UP = S('\n'.join(["DD"] + ["D."] * 14 + ["DD"]))          # palm flat on the notch underside


def beetle(pose='stand', eyes='r', ant='n', step=0, face=1):
    """Assemble + outline once. Feet sit at the sprite's bottom; blit at y = H - height for the ledge."""
    head = HEADS[eyes]
    if pose == 'hunker':        # flat on the floor: head sunk into a squashed shell, legs splayed
        parts = [(ANT[ant], 6, 0), (head, 4, 1), (BODY.resize((24, 9), Image.NEAREST), -2, 7), (LEG_SPLAY, -2, 16)]
    elif pose == 'squash':      # landing frame
        parts = [(ANT[ant], 6, 2), (BODY.resize((22, 11), Image.NEAREST), -1, 14), (head, 4, 5), (ARM_DOWN, 18, 17), (LEG_B, 0, 25)]
    else:
        legs = {'stand': LEG_B, 'walk': (LEG_A if step % 2 == 0 else LEG_B), 'jump': LEG_TUCK, 'lean': LEG_CROSS}[pose]
        hx = 3 if pose == 'lean' else 4
        parts = [(ANT[ant], hx + 2, 0), (BODY, 0, 12), (head, hx, 3), (legs, 0, 25)]
        parts.append((ARM_UP, 18, -1) if pose == 'lean' else (ARM_DOWN, 18, 17))
    spr, mx, my = assemble(parts)
    spr = outline(spr)
    return hflip(spr) if face < 0 else spr


# ---------- boot: 31 wide (fits beside the notch), 70 tall so the leg always runs off the top edge ----------
def _shin():
    rows = []
    for r in range(54):
        row = ['.'] * 31
        for x in range(2, 20): row[x] = 'B'
        row[2] = row[3] = 'M'; row[4] = 'N' if 6 <= r <= 30 and r % 7 < 3 else 'M'
        row[17] = row[18] = row[19] = 'c'
        if r < 4: row[2:20] = list('c' * 18)                                  # cuff
        if r >= 8:
            k = r % 6
            if k == 0: row[12] = row[16] = 'e'                                   # eyelets
            elif k == 1: row[13] = row[15] = 'y'
            elif k == 2: row[14] = 'y'
            elif k == 3: row[13] = row[15] = 'y'
            elif k == 4: row[12] = row[16] = 'y'
        rows.append(''.join(row))
    return S('\n'.join(rows))
FOOT = S("""
..MBBBBBBBBBBBBBBcccc..........
..MBBBBBBBBBBBBBBBcccc.........
.MMBBBBBBBBBBBBBBBBcccc........
.MMBBBBBBBBBBBBBBBBBccccc......
.MMBBBBBBBBBBBBBBBBBBBcccccc...
MMBBBBBBBBBBBBBBBBBBBBBBcccccc.
MBBBBBBBBBBBBBBBBBBBBBBBBNccccc
MBBBBBBBBBBBBBBBBBBBBBBBBBBcccc
cBBBBBBBBBBBBBBBBBBBBBBBBBBBccc
cyByByByByByByByByByByByByByBcc
TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGZZ
ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
ZZ.ZZZ.ZZZ.ZZZ.ZZZ.ZZZ.ZZZ.ZZZZ
""")
_b, _, _ = assemble([(_shin(), 0, 0), (FOOT, 0, 54)])
BOOT_R = outline(_b)            # toe points right (left-zone boot)
BOOT_L = hflip(BOOT_R)          # toe points left (right-zone boot)
BOOT_DOWN = H - BOOT_R.height + 1     # sprite y when the sole is on the ledge (outline row clipped)
BOOT_GONE = -BOOT_R.height - 4


def floor_shadow(im, cx, t, ox=0, oy=0):
    """Growing shadow ellipse on the ledge under a descending boot, t in 0..1."""
    if t <= 0: return
    w = 3 + 28 * t; v = int(22 + 26 * t)
    ImageDraw.Draw(im).ellipse((cx - w / 2 + ox, 48 + oy, cx + w / 2 + ox, 52 + oy), fill=(v, v, v + 8))


def build():
    c = Clip('gag_boot_shelter_01', 11.75)
    LB, RB = 0, 153                       # boot sprite x: left-zone boot (toe right), right-zone boot landing spot
    RB_BONK = 143                         # right boot slid left until its shin meets the notch corner (x=153)
    bx = 0.0; face = 1
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= c.n - 1: continue
        sc = Image.new('RGB', (W, H), (0, 0, 0)); ox = oy = 0
        # ----- boots -----
        b1y = b2y = BOOT_GONE; b2x = RB
        if 22 <= i <= 25: b1y = BOOT_GONE + (BOOT_DOWN - BOOT_GONE) * ((i - 22) / 3) ** 2
        elif 25 < i < 28: b1y = BOOT_DOWN
        elif 28 <= i <= 36: b1y = BOOT_DOWN + (BOOT_GONE - BOOT_DOWN) * ease((i - 28) / 8)
        elif 50 <= i <= 53: b1y = BOOT_GONE + (BOOT_DOWN - BOOT_GONE) * ((i - 50) / 3) ** 2
        elif 53 < i < 80: b1y = BOOT_DOWN
        elif 80 <= i <= 88: b1y = BOOT_DOWN + (BOOT_GONE - BOOT_DOWN) * ease((i - 80) / 8)
        if 42 <= i <= 45: b2y = BOOT_GONE + (BOOT_DOWN - BOOT_GONE) * ((i - 42) / 3) ** 2
        elif 45 < i < 80:
            b2y = BOOT_DOWN
            if 62 <= i <= 65: b2x = RB + (RB_BONK - RB) * ease((i - 62) / 3)
            elif 65 < i < 80:                                   # two presses: ease back 3 px, slam in again
                j = (i - 66) % 6; b2x = RB_BONK + (3 * ease(j / 2) if j < 3 else 3 * (1 - ease((j - 3) / 2)))
                if i >= 78: b2x = RB_BONK
        elif 80 <= i <= 88: b2y = BOOT_DOWN + (BOOT_GONE - BOOT_DOWN) * ease((i - 80) / 8); b2x = RB_BONK
        # jolts: landings shake the strip down 1 px, the bonk shakes it left
        if i in (25, 26, 45, 46, 53, 54): oy = 1
        if i in (65, 66, 72, 78): ox = -1
        if 14 <= i <= 25: floor_shadow(sc, 16, (i - 14) / 11, ox, oy)
        if 38 <= i <= 45: floor_shadow(sc, 168, (i - 38) / 7, ox, oy)
        if 44 <= i <= 53: floor_shadow(sc, 16, (i - 44) / 9, ox, oy)
        # ----- beetle -----
        pose, eyes, ant, step = 'walk', 'r', 'n', i // 3
        by = H
        if i <= 22:                                   # stroll in
            bx = -26 + 70 * (i - 1) / 21
            if i >= 18: eyes = 'k'
            if i >= 20: ant = 'up'
            if i % 6 < 3: ant = 'back' if ant == 'n' else ant
        elif i <= 29:                                 # pop off the floor, land
            t = (i - 25) / 4; bx = 44 + 10 * t; by = H - 7 * math.sin(math.pi * t)
            pose, ant, eyes = ('jump', 'flat', 'r') if i < 29 else ('squash', 'flat', 'r')
        elif i <= 30: bx = 54; pose = 'stand'; ant = 'up'
        elif i <= 44:                                 # sprint right under the notch
            bx = 54 + 5 * (i - 30); ant = 'back'; step = i // 2
        elif i <= 48:                                 # skid: right boot just landed ahead
            bx = 124 + 2 * ease((i - 44) / 4); pose = 'stand'; ant = 'up'; eyes = 'u'
        elif i <= 49: bx = 126; pose = 'stand'; face = -1; ant = 'up'; eyes = 'r'
        elif i <= 52: bx = 126 - 5 * (i - 49); face = -1; ant = 'back'; step = i // 2
        elif i <= 55:                                 # left boot slams again: skid to a stop
            bx = 111 - 2 * ease((i - 52) / 3); face = -1; pose = 'stand'; ant = 'up'; eyes = 'u'
        elif i <= 59:                                 # hop and dive flat
            t = (i - 55) / 4; bx = 109 + 6 * t; by = H - 5 * math.sin(math.pi * t); face = 1
            pose, ant, eyes = 'jump', 'flat', 'x'
        elif i <= 83:                                 # hunker while the boot shoves at the notch corner
            bx = 115; pose = 'hunker'; face = 1
            ant = 'flat'; eyes = 'x' if 63 <= i <= 67 or 71 <= i <= 73 or 77 <= i <= 79 else 'r'
        elif i <= 87: bx = 115; pose = 'hunker'; ant = 'up'; eyes = 'u'
        elif i <= 89: bx = 115; pose = 'stand'; ant = 'up'; eyes = 'u'
        elif i <= 96:                                 # step to the notch's corner
            bx = 115 + 2 * (i - 89); ant = 'n'; step = i // 3
        elif i <= 103: bx = 129; pose = 'stand'; eyes = 'u'; ant = 'up'; by = H - bob(i, 12, 1)
        elif i <= 114: bx = 129; pose = 'stand'; eyes = 'f'; ant = 'n'; by = H - bob(i, 12, 1)
        elif i <= 129: bx = 129; pose = 'lean'; eyes = 's'; ant = 'n'
        elif i <= 133: bx = 129; pose = 'lean'; eyes = 'x'; ant = 'flat'
        else: bx = 129; pose = 'lean'; eyes = 's'; ant = 'n'
        spr = beetle(pose, eyes, ant, step, face)
        c.blit(sc, spr, bx + ox, by - spr.height + oy)
        if by >= H and pose not in ('jump',): shadow(sc, bx + ox + 3, spr.width - 6, H - 1)
        # ----- boots over the beetle (they're nearer the viewer) -----
        c.blit(sc, BOOT_R, LB + ox, b1y + oy)
        c.blit(sc, BOOT_L, b2x + ox, b2y + oy)
        # ----- effects -----
        for (f0, x) in ((25, 0), (25, 30), (45, 154), (45, 182), (53, 0), (53, 30)):
            if f0 <= i <= f0 + 4: puff(sc, x + ox, H - 2 + oy, (i - f0) / 4)
        if 29 <= i <= 33: puff(sc, bx + 2, H - 1, (i - 29) / 4); puff(sc, bx + 20, H - 1, (i - 29) / 4)
        if 45 <= i <= 48: puff(sc, bx + 22, H - 1, (i - 45) / 3, (140, 140, 150))
        if 53 <= i <= 55: puff(sc, bx - 1, H - 1, (i - 53) / 2, (140, 140, 150))
        if 59 <= i <= 63: puff(sc, 112, H - 1, (i - 59) / 4); puff(sc, 140, H - 1, (i - 59) / 4)
        for f0 in (65, 72, 78):
            if f0 <= i < f0 + 8:
                burst(sc, 153, 23, i - f0, n=7, speed=1.3, life=8, cols=((255, 226, 90), (255, 170, 60), (255, 255, 210)))
        if 126 <= i <= 129:                            # one crumb drops out of the notch onto the head
            t = i - 126; cy = 22 + int(1.2 * t * t)
            dots(sc, [(140, cy), (141, cy), (140, cy + 1)], (214, 178, 110))
        elif 130 <= i <= 131:
            dots(sc, [(139 - (i - 130) * 2, 29 + (i - 130)), (143 + (i - 130) * 2, 29 + (i - 130))], (214, 178, 110))
        im.paste(sc, (0, 0))
    return c
