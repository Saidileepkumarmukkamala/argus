import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *
from PIL import Image, ImageDraw

BUCKET = 'gesture'

# ---------- BALLOON BREATHES (gesture: slow in, hold, slow out, let go) ----------
# The body is a procedural ellipse (its size is the animation); face + knot are ASCII modules on offsets.
TEAL = {'T': (72, 190, 180), 'L': (150, 232, 222), 'D': (38, 118, 112), 'f': (18, 48, 48)}
EYE_S = sprite("f", TEAL)                    # calm dot
EYE_M = sprite("w\nf", TEAL)                 # open
EYE_W = sprite("ww\nff", TEAL)               # wide (full breath)
EYE_SHUT = sprite("ff", TEAL)                # blink
SMILE_S = sprite("f.f\n.f.", TEAL)
SMILE_L = sprite("f...f\n.fff.", TEAL)
KNOT = sprite("\n.DD.\nDDDD", TEAL)

def body(rx, ry):
    """Filled teal ellipse with a soft highlight; returns RGBA (2rx+1 x 2ry+1)."""
    im = Image.new('RGBA', (2 * rx + 1, 2 * ry + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 2 * rx, 2 * ry], fill=TEAL['T'] + (255,))
    if rx >= 3:                                # highlight: a square glint top-left
        hx, hy = max(1, rx // 2), max(1, ry // 2); k = 1 if rx >= 7 else 0
        d.rectangle([hx - 1, hy - 1, hx - 1 + k, hy - 1 + k], fill=TEAL['L'] + (255,))
    return im

def balloon(im, c, cx, base_y, rx, ry, string_phase, sag=0, blink=False):
    """cx = centre column, base_y = row of the knot's top. rx/ry = radii."""
    top = base_y - 2 * ry
    c.blit(im, body(rx, ry), cx - rx, top)
    c.blit(im, KNOT, cx - 2, base_y - 1)
    # string: hangs below the knot; slack and wiggly when empty, pulled straight when full
    amp = 1.0 - min(1.0, max(0.0, (rx - 4) / 7))
    for k in range(base_y + 2, min(H, base_y + 6)):
        sx = cx + round(math.sin(string_phase + k * 0.7) * amp)
        if 0 <= sx < W and 0 <= k < H: im.putpixel((int(sx), int(k)), TEAL['D'])
    # face scales with the breath
    if rx >= 4:
        ey = top + ry - max(1, ry // 3) - sag
        eye = EYE_SHUT if blink else (EYE_W if rx >= 9 else (EYE_M if rx >= 4 else EYE_S))
        gap = 2 if rx <= 5 else rx // 2 + 1
        c.blit(im, eye, cx - gap - eye.width + 1, ey)
        c.blit(im, eye, cx + gap, ey)
        smile = SMILE_L if rx >= 8 else SMILE_S
        c.blit(im, smile, cx - smile.width // 2, ey + eye.height + max(1, ry // 4))

def build():
    c = Clip('gesture_balloon_breathe_01', 10.0)
    cx, base_y = CAM[0], H - 5
    R_MIN, R_MAX = 4, 11
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i == c.n - 1: continue
        if i < 48:                                     # inhale: 4 s, ease in/out
            t = ease(i / 47); r = R_MIN * ease(min(1, i / 6)) + (R_MAX - R_MIN) * t
            rx, ry = round(r), round(r); sag = 0
        elif i < 60:                                   # hold: 1 s, the faintest shimmer
            rx, ry = R_MAX, R_MAX + ((i // 6) % 2); sag = 0
        elif i < 108:                                  # exhale: 4 s, sags a little wider than tall
            t = ease((i - 60) / 47); r = R_MAX + (R_MIN - R_MAX) * t
            rx, ry = round(r + 1.2 * math.sin(math.pi * t)), round(r); sag = 1 if 0.2 < t < 0.8 else 0
        else:                                          # let go: drift up past the camera hole
            t = (i - 108) / 10; tt = t * t
            rx = ry = R_MIN
            lift = (base_y + 14) * tt
            base = round(base_y - lift)
            balloon(im, c, cx + round(math.sin(t * 6) * 2), base, rx, ry, i * 0.5)
            continue
        balloon(im, c, cx, base_y, rx, ry, i * 0.4, sag, blink=60 <= i < 63)
    return c
