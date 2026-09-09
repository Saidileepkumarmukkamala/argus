"""Cuckoo (vector). A clock door in the notch's underside; third pop, the worn spring keeps going."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vec import *

BUCKET = 'gag'
TEAL, TEAL_RIM, TEAL_LIGHT = (52, 150, 170), (18, 60, 78), (112, 202, 216)
CREAM, CREST, BEAK, BEAK_D = (246, 226, 182), (222, 72, 72), (246, 162, 52), (188, 108, 30)
PUPIL, FEET, WOOD, WOOD_D, PLATE = (24, 22, 36), (240, 150, 60), (150, 100, 62), (78, 48, 30), (64, 64, 72)
SPRING, SHINE = (150, 150, 162), (214, 214, 224)
CX = 276                       # door centre (under the camera)
HANG = 46                      # crest top to feet ≈ 50 px; bird's "top" hangs `ext` px below the underside

def draw_doors(sc, open_l, open_r):
    """Two panels hinged on the underside at x=CX±30, swinging down/outward. open in 0..1 (1 = ~105 degrees)."""
    sc.rrect(CX - 34, NOTCH_B - 2, CX + 34, NOTCH_B + 5, 3, PLATE)                       # frame plate
    for side, opn in ((-1, open_l), (1, open_r)):
        hx = CX + side * 30; ang = side * math.radians(105) * opn                         # hinge at the outer edge
        L, T = 29, 5
        rect = [(hx, NOTCH_B + 1), (hx - side * L, NOTCH_B + 1), (hx - side * L, NOTCH_B + 1 + T), (hx, NOTCH_B + 1 + T)]
        pts = rot(rect, hx, NOTCH_B + 1, -ang)                                             # rotate about the hinge
        sc.poly(pts, WOOD, outline=WOOD_D, width=1.5)
        kx, ky = pts[1]; sc.circle((kx + hx) / 2, (ky + NOTCH_B + 1) / 2 + 2, 1.6, WOOD_D)   # knob

def draw_spring(sc, ext, slack=0.0):
    """Zigzag from the door opening to the bird's crest. slack>0: coils sag sideways (bird on the floor)."""
    top, bot = NOTCH_B + 2, NOTCH_B + 2 + max(4, ext)
    n = 9; pts = []
    for k in range(n + 1):
        t = k / n; y = lerp(top, bot, t)
        amp = 8 + slack * 14 * math.sin(math.pi * t)
        x = CX + (amp if k % 2 else -amp) * (0.25 if k in (0, n) else 1)
        pts.append((x, y))
    sc.line(pts, SPRING, 3.2); sc.line([(x - 1, y - 1) for x, y in pts], SHINE, 1.0)

K = 1.3                                                   # bird scale: ~65 px tall (33 pt on the notch)
def draw_bird(sc, bx, by, sx=1.0, sy=1.0, beak=0.0, eye_r=6.0, pdx=1.5, pdy=0.5, wing=0.0, blink=0.0, look_cam=False):
    """bx, by = body centre. sx/sy squash-stretch. beak 0..1 open. wing = flap angle (rad, + = up). blink 0..1."""
    sx, sy = sx * K, sy * K; eye_r *= K; pdx *= K; pdy *= K
    body_rx, body_ry = 20 * sx, 17 * sy
    hx, hy = bx + 2 * sx, by - 20 * sy                     # head centre
    # tail feathers
    for k, a in enumerate((-0.55, -0.35, -0.15)):
        sc.ellipse(bx - 21 * sx, by + 6 * sy + k * 2 * K, 13 * K, 4.5 * K, shade(TEAL, 0.85 + k * 0.08), ang=a, )
    # far wing
    sc.ellipse(bx - 10 * sx, by + 1 * sy, 12 * K, 6.5 * K, shade(TEAL, 0.75), ang=-0.35 - wing)
    # body + belly
    sc.blob(bx, by, body_rx, body_ry, TEAL, rim=TEAL_RIM, light=TEAL_LIGHT)
    sc.ellipse(bx + 4 * sx, by + 4 * sy, 11 * sx, 10 * sy, CREAM)
    # near wing
    sc.ellipse(bx - 6 * sx, by + 2 * sy, 13 * K, 7 * K, shade(TEAL, 0.92), ang=-0.3 - wing, )
    sc.ellipse(bx - 6 * sx, by + 2 * sy, 13, 7, TEAL_RIM, ang=-0.3 - wing, outline=None) if False else None
    # feet
    for fx in (bx - 5 * K, bx + 6 * K):
        sc.line([(fx, by + body_ry - 2), (fx - 1, by + body_ry + 5 * K)], FEET, 2.4 * K)
        sc.line([(fx - 4 * K, by + body_ry + 5 * K), (fx + 3 * K, by + body_ry + 5 * K)], FEET, 2.4 * K)
    # head + crest
    sc.blob(hx, hy, 13.5 * sx, 13 * sy, TEAL, rim=TEAL_RIM, light=TEAL_LIGHT)
    for k, a in enumerate((-1.25, -0.95, -0.65)):
        sc.ellipse(hx - 2 * K + k * 3 * K, hy - 12 * sy - (2 * K if k == 1 else 0), 8 * K, 3 * K, CREST, ang=a)
    # eye
    ex, ey = hx + 5 * sx, hy - 2 * sy
    if look_cam: pdx, pdy = 0.0, 0.8
    sc.circle(ex, ey, eye_r, (255, 255, 255)); sc.circle(ex, ey, eye_r + 0.9, TEAL_RIM) if False else None
    sc.circle(ex + pdx, ey + pdy, eye_r * 0.5, PUPIL); sc.circle(ex + pdx - 1.2, ey + pdy - 1.4, eye_r * 0.17, (255, 255, 255))
    if blink > 0: sc.ellipse(ex, ey - eye_r + eye_r * blink, eye_r + 0.6, eye_r * blink + 0.4, TEAL)   # lid comes down
    # beak (upper fixed, lower rotates open)
    bx0, by0 = hx + 11 * sx, hy + 1 * sy
    sc.poly([(bx0, by0 - 3 * K), (bx0 + 13 * K, by0 - 0.5 * K), (bx0, by0 + 1 * K)], BEAK)
    low = rot([(bx0, by0), (bx0 + 12 * K, by0 + 1.5 * K), (bx0, by0 + 4 * K)], bx0, by0, 0.75 * beak)
    sc.poly(low, BEAK_D)

def feather(sc, x, y, a): sc.ellipse(x, y, 9, 3.2, TEAL_LIGHT, ang=a); sc.line([(x - 8, y), (x + 8, y)], shade(TEAL, 0.8), 1.0)

def build():
    c = VClip('gag_cuckoo_v_01', 10.0)
    POP = 6                                        # normal pop extension; FLOOR_EXT = feet on the floor
    FLOOR_EXT = 24
    for i in range(c.n):
        sc = c.scene()
        opn_l = opn_r = 0.0; ext = None; beak = 0.0; blink = 0.0; wing = 0.0; sx = sy = 1.0; eye_r = 6.0; pdx, pdy = 1.5, 0.5
        look = False; slack = 0.0; extra = []
        def pop(a, b):                              # doors open at a..a+10, bird out a+10..b-14, back b-14..b, doors close b..b+8
            nonlocal opn_l, opn_r, ext, beak
            d = ease_out_back(seg(i, a, a + 10)); opn_l = opn_r = d if i < b else max(0.0, 1 - ease_in(seg(i, b, b + 8)))
            if a + 10 <= i < b - 14: ext = POP * ease_out_bounce(seg(i, a + 10, a + 24))
            elif b - 14 <= i < b: ext = POP * (1 - ease_in(seg(i, b - 14, b)))
            if ext is not None and a + 20 <= i < b - 16:
                ph = (i - a - 20) % 12; beak = math.sin(math.pi * ph / 6) if ph < 6 else 0
        if 12 <= i < 64: pop(12, 56)
        elif 68 <= i < 120: pop(68, 112)
        elif 124 <= i:                              # third time: the spring keeps going
            d = ease_out_back(seg(i, 124, 134)); opn_l = opn_r = d
            if i < 146: ext = POP * ease_out_bounce(seg(i, 134, 146)); ph = (i - 138) % 12; beak = math.sin(math.pi * ph / 6) if 138 <= i and ph < 6 else 0
            elif i < 162:
                t = ease_in(seg(i, 146, 162)); ext = lerp(POP, FLOOR_EXT, t); eye_r = lerp(6, 8.5, t); pdx, pdy = 0.5, -1.0 * t
                wing = 0.6 * math.sin(i * 1.3); beak = 0.5 * t
            elif i < 200:
                ext = FLOOR_EXT; slack = 1.0
                if i < 168: q = seg(i, 162, 168); sx, sy = lerp(1.28, 1.0, ease_out(q)), lerp(0.72, 1.0, ease_out(q)); eye_r = 8; pdx, pdy = 0, 1
                elif i < 176: pdx, pdy = 0.0, -2.2; eye_r = 6.5                                   # looks up its own spring
                elif i < 200: look = True; eye_r = 6.5; blink = math.sin(math.pi * seg(i, 184, 189)) if 184 <= i < 189 else 0
                if 190 <= i < 200: wing = 0.9 * math.sin(math.pi * seg(i, 190, 200))               # shrug
                if 162 <= i < 172: extra.append(('puff', seg(i, 162, 172)))
            elif i < 210:                            # recoil: stretch, then yanked up
                q = seg(i, 200, 210)
                if q < 0.25: ext = FLOOR_EXT; sx, sy = 0.85, 1.3; eye_r = 8; pdx, pdy = 0, 1
                else: ext = lerp(FLOOR_EXT, -80, ease_in((q - 0.25) / 0.75)); sx, sy = 0.8, 1.35; eye_r = 8.5
                slack = 0.0
            else: ext = None
            if 208 <= i < 214: q = seg(i, 208, 214); opn_l = 1 - q; opn_r = 1 - q                  # slam
            elif 214 <= i < 236: opn_l = 0; opn_r = 0.4 * (1 - ease_in_out(seg(i, 224, 236)))       # right door bounces, hangs, swings shut
            elif i >= 236: opn_l = opn_r = 0
            if 212 <= i < 238: extra.append(('feather', seg(i, 212, 238)))
        if ext is not None:
            draw_spring(sc, ext, slack)
            by = NOTCH_B + 2 + ext + 36 * K                                                         # crest top sits at the spring end
            draw_bird(sc, CX, by, sx, sy, beak, eye_r, pdx, pdy, wing, blink, look)
        for kind, t in extra:
            if kind == 'puff':
                for k in range(6):
                    a = math.pi + math.pi * (k + 0.5) / 6; r = 6 + 26 * ease_out(t)
                    sc.circle(CX + 30 * math.cos(a) * (1 + 0.8 * t), FLOOR - 3 - abs(10 * math.sin(a)) * ease_out(t), lerp(2.2, 0.4, t), shade((120, 120, 132), 1 - 0.7 * t))
            elif kind == 'feather':
                feather(sc, CX + 40 + 26 * math.sin(t * 9.0), lerp(NOTCH_B + 6, FLOOR + 12, t), 0.5 * math.sin(t * 9.0 + 1.2))
        draw_doors(sc, opn_l, opn_r)
        c.add(sc)
    return c
