import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- SNAIL WITH TEA (gesture: take a break) ----------
SNAIL_BODY = sprite("""
..................wb.wb.
..................ww.ww.
...................g..g.
...................g.g..
...................gg...
..................ggg...
.................gggg...
................ggggg...
...............gggggg...
..............ggggggg...
.............gggggggg...
..ggG.......ggggggggG...
.ggggggggggggggggggggG..
.GGGGGGGGGGGGGGGGGGGG...
""")
SNAIL_EYES_SHUT = sprite("""
..................gg.gg.
""")
SHELL = sprite("""
...OOOOOO...
..OooooooO..
.OoyyoooooO.
.OoyoOOoooO.
.OoooOyOooO.
.OoooOOOooO.
.OOoooooOOO.
..OOoooOOO..
...OOOOOO...
""")
CUP = sprite("""
wwwww.
wtttww
wwwwww
.wwww.
""")

def build():
    c = Clip('gesture_snail_tea_01', 8.0)
    x = -30.0
    step = (W + 60) / (c.n / 2)         # cross the strip in the clip length, moving half the frames
    for i in range(c.n):
        im = c.frame()
        cyc = i % 8
        if cyc < 4: x += step                # extend: move
        contract = cyc >= 4                  # contract: hold, shell slides forward
        sx = 2 if contract else 0
        base_y = H - 14
        c.blit(im, SNAIL_BODY, x, base_y)
        c.blit(im, SHELL, x + 1 + sx, base_y + 3)
        c.blit(im, CUP, x + 4 + sx, base_y - 1)
        # steam: two wisps rising, wiggling
        for k in range(3):
            wy = base_y - 3 - k - ((i // 3) % 2)
            wx = x + 5 + sx + ((i // 4 + k) % 2)
            if 0 <= wx < W and 0 <= wy < H: im.putpixel((int(wx), int(wy)), PAL['s'])
        if i % 30 in (20, 21):
            c.blit(im, SNAIL_EYES_SHUT, x, base_y + 1)
    return c

