"""Giraffe — gesture: stretch. Too tall for the strip: the body walks in headless (neck lost in the notch), the head
comes DOWN out of the notch beside the body, chews, rolls its neck, blinks at you, goes back up — and gets left behind
in the notch when the body walks off. 4-tone hide + spot ramps, big lashed eyes, mane, ossicones, rim outline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'
T = ramp((228, 178, 92))                      # tan hide: shadow, base, light, highlight
SP = ramp((150, 86, 40))                      # spots: shadow, base, light
PAL2 = {'D': T[0], 'y': T[1], 'l': T[2], 'h': T[3],
        'S': SP[0], 's': SP[1], 't': SP[2],
        'm': (78, 46, 30), 'M': (122, 76, 46),            # mane, ossicone knobs, hooves (+ lit side)
        'u': (206, 172, 126), 'U': (156, 122, 86),        # muzzle + its shadow
        'k': (64, 44, 40),                                 # nostrils
        'i': (98, 60, 36), 'b': (24, 18, 22), 'w': (250, 250, 245), 'W': (255, 255, 255),
        'c': (150, 214, 244)}                              # sweat drop
S = lambda rows: sprite(rows, PAL2)
RIM = (98, 74, 64)

# ---------- body, facing right; neck root at the front-top (cols 25..31) ----------
BODY = S("""
.......................hhhhhhhhh..
..............hhhhhhhhhhhlllllllll
..........hhhhllllyyyyyyylyyyyyyyl
.......hhllyyyyyyyytssyyyyyyytssyl
....hhllyyytssyyyyysSyyyyyyyyysSyl
..hhlyyyyysSyyyyyyyyyyyyytsyyyyyyl
.hlyyyyyyyyyyyyyyyyyyyyyyssSyyyyyD
.lyyyyyyyyyyyyytssyyyyyyyyyyyyyyDD
.lyyytssyyyyyyysSSyyytsyyyyyyyyDD.
..lyysSSyyyyyyyyyyyyysSyyyyyyyDDD.
..DlyyyyyyyyytsyyyyyyyyyyyyyyDDD..
...DDDyyyyyyysSyyyyyyyyyyyyDDDD...
....DDDDDDDDDDDDDDDDDDDDDDDD......
""")
NECK_BLOCK = """
MmlyyyyD
MmlytsyD
MmlysSyD
MmlyyyyD
MmlyyyyD
MmltssyD
MmlsSSyD
MmlyyyyD
"""
NECK = S(NECK_BLOCK * 5)                       # 40 rows: rises from the body top through the ceiling / into the notch
NECK_DN = S("""
mlyyyyyD
mlyytssD
mlyysSSD
mlyyyyyD
mlyyyyyD
mltssyyD
mlsSSyyD
mlyyyyyD
mlyyyyyD
mlyyytsD
mlyyysSD
mlyyyyyD
mlyyyyyD
mltsyyyD
mlsSyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
mlyyyyyD
""")                                           # the neck coming DOWN behind the head (top hidden in the notch)
TAIL_A = S("""
.D..
.D..
D...
D...
D...
m...
mm..
Mm..
.m..
""")
TAIL_B = S("""
.D..
.D..
.D..
..D.
..D.
..m.
..mm
..Mm
...m
""")

# ---------- head: frontal, looking DOWN at you (24 wide). eyes are 6x5 tiles substituted into rows 10..14 ----------
EYE_OPEN  = (['.bbbb.', 'bwbbwi', 'iwWbwi', 'iwbbwi', '.iiii.'], ['.bbbb.', 'iwbbwb', 'iwWbwi', 'iwbbwi', '.iiii.'])
EYE_SHUT  = (['yyyyyy', 'yyyyyy', 'ybbbby', 'byyyyb', 'yyyyyy'],) * 2
EYE_WIDE  = (['.bbbb.', 'bwwwwi', 'iwbbwi', 'iwwwwi', '.iiii.'], ['.bbbb.', 'iwwwwb', 'iwbbwi', 'iwwwwi', '.iiii.'])
EYE_SIDE  = (['.bbbb.', 'bbbwwi', 'iWbwwi', 'ibbwwi', '.iiii.'], ['.bbbb.', 'ibbwwb', 'iWbwwi', 'ibbwwi', '.iiii.'])
HEAD_ROWS = """
......mM........mM......
......mM........mM......
......Mm........Mm......
.......ly......ly.......
.......ly......ly.......
.....hhlymmmmmmylhh.....
hhl..lhyyymmmmyyylhl.lhh
lyyl.lyyyyyyyyyyyyyl.lyD
lyyylhlyyyyyyyyyyyyylyyD
.DyylhllyyyyyyyyyyyyyyD.
..DDlAAAAAAyyBBBBBBDDD..
....lAAAAAAyyBBBBBBD....
....lAAAAAAyyBBBBBBD....
....lAAAAAAyyBBBBBBD....
....lAAAAAAyyBBBBBBD....
....lDyyyyyyyyyyyyDD....
....lytsyyyyyyyytsDD....
.....lsSyyyyyyyysSD.....
.....llyyyyyyyyyyDD.....
......lhuuuuuuuuUD......
......luuuuuuuuuUD......
......lkkuuuuuukkD......
......luuuuuuuuuUD......
......UuuummmmuuuU......
.......DUuuuuuuUD.......
........DDDDDDDD........
""".strip('\n').split('\n')
EARS_UP    = HEAD_ROWS[6:9]
EARS_FLICK = ['.hhl.lhyyymmmmyyylhl.lhh', '..lyylyyyyyyyyyyyyylyyD.', '...lyyyyyyyyyyyyyyyyyD..']
MOUTH = [['......UuuummmmuuuU......', '.......DUuuuuuuUD.......'],
         ['......UuummmmuuuuU......', '......DUuuuuuuuUD.......']]

_cache = {}
def head(eyes=EYE_OPEN, chew=0, ears=EARS_UP):
    key = (str(eyes), chew, tuple(ears))
    if key not in _cache:
        rows = list(HEAD_ROWS)
        for k in range(5): rows[10 + k] = rows[10 + k].replace('AAAAAA', eyes[0][k]).replace('BBBBBB', eyes[1][k])
        rows[6:9] = ears; rows[23:25] = MOUTH[chew]
        spr, mx, my = assemble([(NECK_DN, 8, -22), (S('\n'.join(rows)), 0, 0)])
        _cache[key] = (outline(spr, RIM), mx - 1, my - 1)
    return _cache[key]

def leg(dx, far=False):
    """Leg with a 3-px thigh, knee, 2-px cannon, fetlock and hoof; the hoof swings dx px, the knee bends forward."""
    h = 18; im = Image.new('RGBA', (12, h), (0, 0, 0, 0)); px = im.load(); cx = 5
    lt, bs, sh = (T[1], T[0], T[0]) if far else (T[2], T[1], T[0])
    P = lambda x, y, col: px.__setitem__((x, y), col + (255,))
    for y in range(h):
        x = cx + round(dx * y / (h - 1)) + (1 if dx > 0 and 5 <= y <= 11 else 0)
        if y >= h - 2:                              # hoof
            P(x - 1, y, PAL2['M']); P(x, y, PAL2['m']); P(x + 1, y, PAL2['m'])
        elif y == h - 3:                            # fetlock: a shade darker
            P(x, y, bs); P(x + 1, y, sh)
        elif y < 6:                                 # thigh: 3 wide
            P(x - 1, y, lt); P(x, y, bs); P(x + 1, y, sh)
        else:
            P(x, y, lt if y != 7 else T[3]); P(x + 1, y, bs)   # knee catches the light
    return im

SWING_A = [3, 1, -3, -1]; SWING_B = [-3, -1, 3, 1]
_bcache = {}
def giraffe(pose=0, tail=0):
    """Body + legs + neck column, assembled and outlined once. Anchor: body top-left; hooves at body_y + 27."""
    key = (pose, tail)
    if key not in _bcache:
        a, b = SWING_A[pose], SWING_B[pose]
        parts = [(leg(a, True), 3 - 5, 10), (leg(b, True), 23 - 5, 10),
                 (TAIL_A if tail == 0 else TAIL_B, -3, 4), (BODY, 0, 0),
                 (leg(b), 7 - 5, 10), (leg(a), 27 - 5, 10), (NECK, 25, -39)]
        spr, mx, my = assemble(parts)
        _bcache[key] = (outline(spr, RIM), mx - 1, my - 1)
    return _bcache[key]

def eo(t, k=0.06):
    """ease with a small overshoot before settling (k = overshoot fraction)."""
    t = max(0.0, min(1.0, t)); return ease(t) + k * math.sin(math.pi * t) * t

def build():
    c = Clip('gesture_giraffe_stretch_01', 11.5)
    PARK, BODY_Y = 66, 24                     # neck column at x 91..97 (under the notch); hooves on the ledge
    HEAD_X, HEAD_Y, HIDE_Y = 103, 21, -29     # head hangs beside the neck; HIDE_Y puts its whole rim inside the notch
    for i in range(c.n):
        im = c.frame()
        bx = None; hd = None                  # body x, head (x, y, eyes, ears)
        chew = (i // 3) % 2
        # ---- body ----
        if 1 <= i <= 26:                      # walk in from the left
            u = (i - 1) / 25; bx = -44 + (PARK + 44) * ease(u)
        elif 27 <= i <= 111:
            bx = PARK
        elif 112 <= i <= 129:                      # walk off right
            u = (i - 112) / 17; bx = PARK + (W + 6 - PARK) * (u ** 1.25)
        if bx is not None:
            walking = i <= 26 or i >= 112
            pose = int(bx / 6) % 4 if walking else 0
            by = BODY_Y - (1 if walking and pose % 2 else 0) + (0 if walking else bob(i, 24, 1))
            tail = 0
            if 29 <= i <= 31 or 34 <= i <= 36 or (walking and (i // 4) % 3 == 0): tail = 1
            spr, mx, my = giraffe(pose, tail); c.blit(im, spr, bx + mx, by + my)
            shadow(im, bx + 2, 32)
            if i == 27: puff(im, PARK + 28, H - 1, 0.1); puff(im, PARK + 8, H - 1, 0.1)
            if 28 <= i <= 31: puff(im, PARK + 28, H - 1, (i - 27) / 4)
        # ---- sparkle at the notch lip: found something up there ----
        if 30 <= i <= 36:
            sx, sy = HEAD_X + 11, NOTCH_B + 1
            if (i // 2) % 2 == 0: dots(im, [(sx, sy)], PAL2['W'])
            else: dots(im, [(sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)], PAL2['c']); dots(im, [(sx, sy)], PAL2['W'])
        # ---- head ----
        dx = dy = 0; eyes = EYE_OPEN; ears = EARS_UP; show = False
        if 37 <= i <= 46:                     # slides down out of the notch, eyes shut, chewing, content
            show = True; eyes = EYE_SHUT; dy = HIDE_Y + (HEAD_Y - HIDE_Y) * eo((i - 37) / 9) - HEAD_Y
        elif 47 <= i <= 54:                   # opens eyes on the viewer; one ear flick
            show = True
            if i in (50, 51): ears = EARS_FLICK
        elif 55 <= i <= 64:                   # tilt left, hold
            show = True; dx = -4 * ease((i - 55) / 4); dy = 1 * ease((i - 55) / 4)
        elif 65 <= i <= 74:                   # tilt right, hold
            show = True; dx = -4 + 8 * ease((i - 65) / 5); dy = 1
        elif 75 <= i <= 90:                   # one slow loop: down, around, up (offset path, no rotation)
            show = True; th = 2 * math.pi * (i - 75) / 16; dx = 4 * math.cos(th); dy = 3 * math.sin(th)
        elif 91 <= i <= 93:                   # settle
            show = True; dx = 4 * (1 - ease((i - 90) / 3))
        elif 94 <= i <= 103:                  # blink to camera, hold the look
            show = True; chew = 0
            if i in (96, 97): eyes = EYE_SHUT
        elif 104 <= i <= 111:                 # anticipation dip, then slides back up into the notch
            show = True; chew = 0
            if i <= 105: dy = 2
            else: dy = 2 + (HIDE_Y - HEAD_Y - 2) * ease((i - 106) / 5)
        elif 116 <= i <= 135:                 # twist: the head is still in the notch. peeks, realises, zips off after the body
            show = True; chew = 0
            peek = 12 - HEAD_Y                # eyes just under the lip
            if i <= 119: dy = (HIDE_Y - HEAD_Y) + (peek - (HIDE_Y - HEAD_Y)) * ease((i - 116) / 3)
            else: dy = peek
            if 120 <= i <= 125: eyes = EYE_SIDE            # glances after the body
            if i >= 126: eyes = EYE_WIDE; dy = peek + 3     # drops a little more with the shock
            if 126 <= i <= 131: dots(im, [(HEAD_X + 25, HEAD_Y + dy + 8 + (i - 126)), (HEAD_X + 25, HEAD_Y + dy + 9 + (i - 126))], PAL2['c'])
            if 130 <= i <= 131: dx = -2 * (i - 129)        # wind-up left
            if i >= 132:
                z = (i - 132) / 3; dx = -4 + (W + 30 - HEAD_X) * (z * z)
                for r in range(3): dots(im, [(HEAD_X + dx - 4 - 3 * r - k, HEAD_Y + dy + 10 + 5 * r) for k in range(3)], T[2])
                if i == 132: puff(im, HEAD_X + 8, HEAD_Y + dy + 26, 0.2)
        if show:
            spr, mx, my = head(eyes, chew, ears); c.blit(im, spr, HEAD_X + dx + mx, HEAD_Y + dy + my)
    return c
