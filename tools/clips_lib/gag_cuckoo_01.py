"""Cuckoo — the notch is a clock with a worn spring. Third time out, the spring keeps going; the bird gets one
moment on the floor and is snatched straight back. Bird ~24 px (crest to feet), 4-tone ramps, eye ring + glint,
rim outline once per pose; spring = parametric zigzag; doors = 3-px planks drawn at any hinge angle."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *
from PIL import ImageDraw

BUCKET = 'gag'

B = ramp((92, 138, 176)); C = ramp((238, 222, 178)); V = ramp((58, 92, 138)); N = ramp((236, 176, 60))
R = ramp((224, 84, 72)); T = ramp((152, 102, 56)); J = ramp((230, 150, 70)); STEEL = ramp((176, 180, 196))
PAL2 = {'B': B[0], 'b': B[1], 'l': B[2], 'h': B[3],                       # slate-blue plumage
        'C': C[0], 'c': C[1], 'e': C[2], 'E': C[3], 'd': (176, 150, 118),  # cream belly + barring
        'V': V[0], 'v': V[1], 'u': V[2], 'f': (40, 62, 100),               # wing + feather lines
        'K': N[0], 'n': N[1], 'm': N[2], 'M': N[3],                        # beak
        'R': R[0], 'r': R[1], 'q': R[2], 'Q': R[3],                        # crest
        'o': (250, 250, 245), 'k': (22, 18, 32), 'g': (255, 255, 255), 'y': (236, 196, 64),   # eye
        'J': J[0], 'j': J[1], 'X': (150, 40, 50),                                              # legs
        'T': T[0], 't': T[1], 's': T[2], 'S': T[3]}                        # wood
S = lambda rows: sprite(rows, PAL2)

CREST = S("""
.Qq....
Qqrq...
.qrrqq.
.RrrrrR
..RRRR.
""")
CREST_FLICK = S("""
Qq...Qq
.qq.qr.
..qrrq.
.RrrrrR
..RRRR.
""")
HEAD = S("""
....hhhhhh...
..hhlllllllh.
.hllbbbbbbbll
.lbbbyyyybbbl
hlbbyogkoybbl
hlbbyokkoybbl
.lbbbyyyybbbl
.lBbbbbbbbbBl
..BBbbbbbbBB.
...BBBBBBB...
""")
HEAD_WIDE = S("""
....hhhhhh...
..hhlllllllh.
.hlbbyyyyybll
.lbbyoooooybl
hlbbyoogooybl
hlbbyookooybl
.lbbyoooooybl
.lBbbyyyyybBl
..BBbbbbbbBB.
...BBBBBBB...
""")
HEAD_UP = S("""
....hhhhhh.Mm
..hhlllllllnn
.hlbbyyyybbnK
.lbbyogkoybKl
hlbbyokkoybll
hlbbbyyyybbbl
.lbbbbbbbbbbl
.lBbbbbbbbbBl
..BBbbbbbbBB.
...BBBBBBB...
""")
HEAD_FRONT = S("""
....hhhhhh...
..hhlllllllh.
.hyyybbbyyyll
.yogkybyogkyl
lyokkybyokkyl
lyoooybyoooyl
.lyyybbbyyyl.
.lBbbbMnbbbBl
..BBbbKKbbBB.
...BBBBBBB...
""")
HEAD_FRONT_BLINK = S("""
....hhhhhh...
..hhlllllllh.
.hlbbbbbbbbll
.lbbbbbbbbbbl
lbBBBbbbBBBbl
lbbbbbbbbbbbl
.lbbbbbbbbbl.
.lBbbbMnbbbBl
..BBbbKKbbBB.
...BBBBBBB...
""")
HEAD_BLINK = S("""
....hhhhhh...
..hhlllllllh.
.hllbbbbbbbll
.lbbbbbbbbbbl
hlbbbBBBBbbbl
hlbbbbbbbbbbl
.lbbbbbbbbbbl
.lBbbbbbbbbBl
..BBbbbbbbBB.
...BBBBBBB...
""")
BEAK = S("""
Mmmm..
nnnnnn
.KKKK.
""")
BEAK_OPEN = S("""
.....Mm
...mmm.
.nnn...
nXX....
.nnn...
...KKK.
.....KK
""")
BODY = S("""
....hhhhhhhh....
..hhllllllllll..
.hllbbbbbbbbccl.
.lbbbbbbbbbccce.
lbbbbbbbbbcceee.
lbbbbbbbbcdcdee.
lBbbbbbbbcdcdee.
lBBbbbbbbcccccE.
.BBBbbbbbCccccE.
..BBBBbbBCCccC..
....BBBBBCCCC...
""")
BODY_PUFF = S("""
....hhhhhhhh....
..hhlllllllllll.
.hllbbbbbbbbccce
.lbbbbbbbbbcccee
lbbbbbbbbbcceeeE
lbbbbbbbbcdcdeeE
lBbbbbbbbcdcdeeE
lBBbbbbbbcccccE.
.BBBbbbbbCccccE.
..BBBBbbBCCccC..
....BBBBBCCCC...
""")
WING = S("""
....uuuuuu.
..uuvvvvvvu
.uvvfvvfvvv
.Vvvvfvvfvv
..VVvvvfvvV
....VVvvvV.
......VVV..
""")
WING_UP = S("""
.......uuu.
.....uuvvu.
...uuvvfvv.
..uvvfvvvv.
.uvvfvvvV..
.VvvvvVV...
..VVVV.....
""")
WING_DOWN = S("""
.VVVV......
.VvvvvV....
..VvvfvvV..
...VvvfvvV.
....VvvvfvV
.....VVvvvu
.......uuuu
""")
TAIL = S("""
......uu
....uuvv
..uuvvvV
uvvvvVV.
VVVVV...
""")
LEGS = S("""
.j...j..
.j...j..
jjj.jjj.
""")
FEATHER = [S("""
..uuu.
.uvvvu
uvvhu.
.uu...
"""), S("""
.uuuuu
uvvvvh
.uuuu.
"""), S("""
.uuu..
uvvvu.
.uhvvu
...uu.
""")]

RIM = (70, 66, 96)

def bird(head='side', beak=0, wing='mid', crest=0, puff=0):
    """Assemble + outline once per pose. Returns (sprite, ox, oy): blit at (X+ox, Y+oy) for bird origin (X, Y).
    Spring attaches at bird-local (9, 2); feet bottom row is local y=23."""
    parts = [(TAIL, -6, 14), (BODY_PUFF if puff else BODY, 0, 11),
             ({'mid': WING, 'up': WING_UP, 'down': WING_DOWN}[wing], 2, 13), (LEGS, 6, 21)]
    h = {'side': HEAD, 'sblink': HEAD_BLINK, 'wide': HEAD_WIDE, 'up': HEAD_UP, 'front': HEAD_FRONT, 'blink': HEAD_FRONT_BLINK}[head]
    parts.append((h, 3, 2))
    parts.append((CREST_FLICK if crest else CREST, 2, -1))
    if head in ('side', 'sblink', 'wide'): parts.append((BEAK_OPEN if beak else BEAK, 15, 3 if beak else 6))
    spr, mx, my = assemble(parts)
    return outline(spr, RIM), mx - 1, my - 1

def scaled(spr, sx, sy):
    return spr.resize((max(1, round(spr.width * sx)), max(1, round(spr.height * sy))), Image.NEAREST)

# ---------- world: door + spring ----------
DOOR_CX, HINGE_L, HINGE_R, TOP = 92, 80, 104, NOTCH_B + 1      # first visible row under the notch is y = 22
SPRING_X = DOOR_CX

def plank(im, hx, deg, length=12):
    """3-px wood plank hung from hinge (hx, TOP); deg 0 = straight down, +ve tips inward (for a left door)."""
    a = math.radians(deg)
    for k in range(length):
        x, y = hx + k * math.sin(a), TOP + k * math.cos(a)
        rx, ry = round(x), round(y)
        dots(im, [(rx - 1, ry)], T[2]); dots(im, [(rx, ry)], T[1]); dots(im, [(rx + 1, ry)], T[1]); dots(im, [(rx + 2, ry)], T[0])
        if k in (3, 8): dots(im, [(rx, ry), (rx + 1, ry)], (104, 66, 32))     # panel lines
        if k == 6: dots(im, [(rx + 1 if hx < DOOR_CX else rx, ry)], (40, 30, 24))   # knob on the inner edge
    x, y = hx + (length - 1) * math.sin(a), TOP + (length - 1) * math.cos(a)
    rx, ry = round(x), round(y)
    dots(im, [(rx - 1, ry + 1), (rx, ry + 1), (rx + 1, ry + 1), (rx + 2, ry + 1)], RIM)

def doors(im, dl, dr):
    """dl/dr: hinge angle in degrees or None for closed (flush with the underside = invisible)."""
    if dl is None and dr is None: return
    dots(im, [(x, TOP) for x in range(HINGE_L - 2, HINGE_R + 3)], T[0])   # sill of the opening
    dots(im, [(x, TOP) for x in range(HINGE_L + 1, HINGE_R)], (34, 30, 44))   # the dark inside
    if dl is not None: plank(im, HINGE_L, dl)
    if dr is not None: plank(im, HINGE_R - 1, -dr)

def spring(im, yend, amp=3):
    """Zigzag from inside the notch down to yend. 2-tone steel."""
    d = ImageDraw.Draw(im)
    pts = []; y = TOP - 8; k = 0
    while y < yend:
        pts.append((SPRING_X + (amp if k % 2 else -amp), y)); y += 2; k += 1
    pts.append((SPRING_X, yend))
    for a, b in zip(pts, pts[1:]): d.line([(a[0], a[1] + 1), (b[0], b[1] + 1)], fill=STEEL[0])
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=STEEL[2])

def coils(im, n, x, y):
    """Excess spring spilling out of the door and piling on the floor behind the bird."""
    d = ImageDraw.Draw(im)
    top = y - (n - 1) * 2
    pts = [(SPRING_X - 3, TOP + 3), (x + 4, TOP + 12), (x + 2, top - 2), (x + 6, top)]      # the sag from the door to the pile
    for a, b in zip(pts, pts[1:]): d.line([(a[0], a[1] + 1), (b[0], b[1] + 1)], fill=STEEL[0])
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=STEEL[2])
    for c in range(n):
        cx = x - (c % 2) * 2; cy = y - c * 2
        d.ellipse([cx, cy + 1, cx + 12, cy + 4], outline=STEEL[0]); d.ellipse([cx, cy, cx + 12, cy + 3], outline=STEEL[2])

# ---------- timeline as a list of per-frame dicts ----------
def build():
    F = []
    def f(**kw): F.append(kw); return kw
    OPEN = [(45, 45), (-8, -8), (0, 0)]          # closed -> half -> overshoot outward -> hang
    SHUT = [(40, 40), (None, None), (75, 75), (None, None)]

    def hold(n, **kw):
        for _ in range(n): f(**kw)
    def open_doors():
        for j, (a, b) in enumerate(OPEN): f(dl=a, dr=b, dust=(j + 1) / 3)
    def shut_doors():
        for j, (a, b) in enumerate(SHUT): f(dl=a, dr=b, dust=(0.15 if j == 1 else None))
    def pop_and_call():
        for L in (1, 3, 4, 3, 3): f(dl=0, dr=0, L=L)                       # overshoot then settle
        for beak in (1, 1, 0, 1, 1): f(dl=0, dr=0, L=3, beak=beak, puff=beak)
        f(dl=0, dr=0, L=3, head='sblink')
        for L in (2, 1): f(dl=0, dr=0, L=L)

    hold(3)
    open_doors(); pop_and_call(); shut_doors(); hold(2)                  # first cuckoo
    open_doors(); pop_and_call(); shut_doors(); hold(2)                  # second cuckoo
    open_doors()
    for L in (1, 3, 4, 3, 3): f(dl=0, dr=0, L=L)                          # third pop
    f(dl=0, dr=0, L=3, beak=1, puff=1); f(dl=0, dr=0, L=3, beak=1, puff=1)
    creak = (3, 4, 4, 5, 6, 7, 8)                                   # the spring keeps going
    for j, L in enumerate(creak):
        f(dl=0, dr=0, L=L, head='wide' if j >= 2 else 'side', wing=('up', 'down')[j % 2] if j >= 3 else 'mid', beak=1 if j >= 5 else 0)
    f(dl=0, dr=0, ground=True, squash=(1.3, 0.7), head='wide', wing='down', land=0.1, coilsn=0)   # contact
    f(dl=0, dr=0, ground=True, squash=(0.92, 1.08), head='wide', wing='up', land=0.4, coilsn=1)
    for j, n in enumerate((1, 2, 3, 4)):                          # spring dumps out: coils pile up
        f(dl=0, dr=0, ground=True, squash=(1.08, 0.92), head='wide', wing=('up', 'down')[j % 2], coilsn=n, land=0.7 if j == 0 else None)
    f(dl=0, dr=0, ground=True, coilsn=4, head='side'); f(dl=0, dr=0, ground=True, coilsn=4, squash=(0.96, 1.04))   # stands, settle
    hold(1, dl=0, dr=0, ground=True, coilsn=4)
    hold(2, dl=0, dr=0, ground=True, coilsn=4, crest=1); hold(1, dl=0, dr=0, ground=True, coilsn=4); hold(2, dl=0, dr=0, ground=True, coilsn=4, crest=1)   # crest flick
    hold(1, dl=0, dr=0, ground=True, coilsn=4)
    hold(4, dl=0, dr=0, ground=True, coilsn=4, head='up')                 # looks up its own spring
    hold(4, dl=0, dr=0, ground=True, coilsn=4, head='front')              # ... at the user
    hold(2, dl=0, dr=0, ground=True, coilsn=4, head='blink')
    hold(4, dl=0, dr=0, ground=True, coilsn=4, head='front')
    hold(1, dl=0, dr=0, ground=True, coilsn=4, head='front', wing='up', lift=1)
    hold(4, dl=0, dr=0, ground=True, coilsn=4, head='front', wing='up', lift=2)      # shrug
    hold(1, dl=0, dr=0, ground=True, coilsn=4, head='front')
    f(dl=0, dr=0, ground=True, coilsn=2, stretch=(0.7, 1.45), head='wide')             # yank: stretch frame
    f(dl=0, dr=0, yank=1, feather=0)                                                     # halfway into the notch
    f(dl=None, dr=None, dust=0.2, feather=1, slam=True)                                  # doors bang shut
    f(dl=None, dr=50, feather=2)
    n0 = len(F)
    for j in range(3, 24): f(dl=None, dr=22, feather=j)                                  # crooked door hangs; feather drifts, rolls off
    f(dl=None, dr=50); f(dl=None, dr=None)
    while len(F) % 12: f()
    hold(0)
    c = Clip('gag_cuckoo_01', len(F) // 12)
    assert c.n == len(F)

    X, GROUND_Y = DOOR_CX - 9, H - 24         # bird origin: spring at X+9; standing feet on the ledge
    for i in range(c.n):
        im = c.frame(); k = F[i]
        doors(im, k.get('dl'), k.get('dr'))
        if k.get('dust') is not None:
            puff(im, HINGE_L, TOP + 2, k['dust']); puff(im, HINGE_R, TOP + 2, k['dust'])
        spr, ox, oy = bird(k.get('head', 'side'), k.get('beak', 0), k.get('wing', 'mid'), k.get('crest', 0), k.get('puff', 0))
        if k.get('L') is not None:                                          # hanging on the spring
            L = k['L']; Y = TOP + L - 2 - (1 if k.get('puff') else 0)
            spring(im, Y + 2); c.blit(im, spr, X + ox, Y + oy)
        elif k.get('ground'):
            Y = GROUND_Y - k.get('lift', 0) + bob(i, 16, 1)
            if k.get('squash'):
                sx, sy = k['squash']; s2 = scaled(spr, sx, sy)
                bx = X + ox + (spr.width - s2.width) // 2; by = H - s2.height + 1   # anchored at the feet (Y+23 = 51)
                spring(im, by + round(2 * sy)); c.blit(im, s2, bx, by)
            elif k.get('stretch'):
                sx, sy = k['stretch']; s2 = scaled(spr, sx, sy)
                bx = X + ox + (spr.width - s2.width) // 2; by = TOP + 3                     # pulled up from the head
                spring(im, by + 2); c.blit(im, s2, bx, by)
            else:
                spring(im, Y + 2); c.blit(im, spr, X + ox, Y + oy)
            shadow(im, X - 4, 24)
            if k.get('coilsn'): coils(im, k['coilsn'], X - 17, H - 5)
            if k.get('land') is not None: puff(im, X + 2, H - 1, k['land']); puff(im, X + 18, H - 1, k['land'])
        elif k.get('yank'):
            s2 = scaled(spr, 0.8, 1.3); c.blit(im, s2, X + ox + 2, TOP - 22)      # legs still trailing out of the door
            spring(im, TOP + 1)
        # feather: released at the yank, falling-leaf sway, lands, rolls off the ledge
        if k.get('feather') is not None:
            j = k['feather']
            if j < 15:
                x = X + 12 + 1.4 * j + 6 * math.sin(j * 0.6); y = TOP + 10 + 1.6 * j
                spr_f = FEATHER[0 if math.cos(j * 0.6) > 0.3 else (2 if math.cos(j * 0.6) < -0.3 else 1)]
                c.blit(im, spr_f, x, min(y, H - 4))
            elif j < 24:
                x = X + 12 + 1.4 * 14 + 7 * (j - 14); spr_f = FEATHER[(j % 3)]
                c.blit(im, spr_f, x, H - 4 + (0 if x < 168 else (x - 168) // 2))
        if k.get('slam'): puff(im, DOOR_CX, TOP + 2, 0.05)
    return c
