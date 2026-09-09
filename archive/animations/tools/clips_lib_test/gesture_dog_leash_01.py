import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- DOG BRINGS THE LEASH (gesture: go outside) ----------
# Modular: side-view trot (body/head/legs/tail) + front-view sit (body/head/tail), leash separate.
DP = {'B': (186, 112, 52), 'D': (118, 66, 30), 'L': (240, 206, 160), 'k': (30, 26, 34)}

# --- side view, facing right ---
S_BODY = sprite("""
...BBBBBBBBBBB..
..BBBBBBBBBBBBB.
.BBBBBBBBBBBBBBB
.BBBBBBBBBBBBBBB
.BBBBBBBBBBBBBB.
..BBBLLLLLBBBB..
""", DP)
S_HEAD = sprite("""
..DDD......
.DDDBBBB...
.DDBBBBBB..
..BBBBBBBB.
..BBwbBBBBB
..BBBBBBLLk
..BBBBBLLL.
...BBBBLL..
""", DP)
S_HEAD_BLINK = sprite("""
....BB.
""", DP)
S_LEGS_A = sprite("""
..DB.......DB...
..DB.......DB...
..DB.......DB...
.DDD......DDD...
""", DP)
S_LEGS_B = sprite("""
..DB......BD....
.D.B.....B..D...
D..B....B....D..
D.DDD..DD....DD.
""", DP)
S_TAIL_UP = sprite("""
B...
.B..
..B.
..BB
""", DP)
S_TAIL_MID = sprite("""
....
BB..
..B.
..BB
""", DP)
LEASH_SIDE = sprite("""
r...
r...
.rr.
r..r
r..r
.rr.
""")

# --- front view, sitting, looking at the viewer ---
F_HEAD = sprite("""
.DD......DD.
DDDBBBBBBDDD
DDBBBBBBBBDD
.DBBBBBBBBD.
.BBwbBBBwbB.
.BBBBBBBBBB.
.BBBLLLLLBB.
..BBLkkLLB..
..BBLLLLLB..
...BBBBBB...
""", DP)
F_HEAD_TILT = sprite("""
.DD......DD..
DDDBBBBBBDDD.
DDBBBBBBBBDD.
.DBBBBBBBBDD.
.BBBBBBBwbBD.
.BBwbBBBBBB..
..BBBLLLLLBB.
...BBLkkLLB..
...BBLLLLLB..
....BBBBBB...
""", DP)
F_BLINK = sprite("""
BB...BB
""", DP)
F_BODY = sprite("""
..BBBBBBBB..
.BBBBBBBBBB.
.BBBLLLLBBB.
BBBBLLLLBBBB
BBBBLLLLBBBB
BBBB.LL.BBBB
.BB......BB.
.DDD....DDD.
""", DP)
F_TAIL = sprite("""
BB.
.BB
""", DP)
F_TAIL_BIG = sprite("""
B...
BB..
.BBB
""", DP)
LEASH_FRONT = sprite("""
.r..
.r..
.r..
.rr.
r..r
r..r
.rr.
""")

GROUND = H            # feet sit on the bottom row


def dog_side(im, c, x, i, moving=True, blink=False):
    """x = left edge of body. Trot cycle on i."""
    by = GROUND - 4 - 6                      # legs 4 + body 6
    legs = (S_LEGS_A, S_LEGS_B)[(i // 2) % 2] if moving else S_LEGS_A
    bob = 0 if not moving else ((i // 2) % 2)
    c.blit(im, S_TAIL_UP if (i // 2) % 2 == 0 else S_TAIL_MID, x - 2, by - 3 - bob)
    c.blit(im, legs, x, GROUND - 4)
    c.blit(im, S_BODY, x, by - bob)
    hx, hy = x + 11, by - 6 - bob
    c.blit(im, S_HEAD, hx, hy)
    if blink: c.blit(im, S_HEAD_BLINK, hx, hy + 4)
    c.blit(im, LEASH_SIDE, hx + 7, hy + 7)


def dog_front(im, c, x, tilt=False, tail=0, big=False, bounce=0, blink=False):
    """x = left edge of body. tail: -1 left, +1 right. big = harder wag."""
    by = GROUND - 8 - bounce
    T = F_TAIL_BIG if big else F_TAIL
    if tail < 0: c.blit(im, T, x - 3, by + 3)
    elif tail > 0: c.blit(im, flip(T), x + 11, by + 3)
    c.blit(im, F_BODY, x, by)
    if tilt:
        c.blit(im, F_HEAD_TILT, x - 1, by - 8)
        if blink: c.blit(im, F_BLINK, x + 2, by - 4)
        c.blit(im, LEASH_FRONT, x + 4, by + 2)
    else:
        c.blit(im, F_HEAD, x, by - 8)
        if blink: c.blit(im, F_BLINK, x + 2, by - 4)
        c.blit(im, LEASH_FRONT, x + 4, by + 2)


def build():
    c = Clip('gesture_dog_leash_01', 7.0)
    cx = W // 2 - 6                            # sit centred on the strip
    x0 = -32.0
    for i in range(c.n):
        im = c.frame()
        if i < 1:
            continue                           # empty lead frame
        if i < 24:                             # trot in from the left, slowing into centre
            t = ease((i - 1) / 22)
            x = x0 + (cx - 3 - x0) * t
            dog_side(im, c, x, i)
        elif i < 27:                           # settle: stop, then sit
            dog_side(im, c, cx - 3, 0, moving=False)
        elif i < 46:                           # sit, tail wagging, look at the viewer
            j = i - 27
            dog_front(im, c, cx, tail=1 if (j // 2) % 2 == 0 else -1, blink=j in (10, 11))
        elif i < 58:                           # head tilt (hold), tail still going
            j = i - 46
            dog_front(im, c, cx, tilt=True, tail=1 if (j // 2) % 2 == 0 else -1)
        elif i < 70:                           # untilt, wag HARDER: every frame, bigger tail, body hop
            j = i - 58
            dog_front(im, c, cx, tail=1 if j % 2 == 0 else -1, big=True, bounce=(j % 4 == 1))
        elif i < 72:                           # stand up
            dog_side(im, c, cx - 3, 0, moving=False)
        elif i < c.n - 1:                      # trot off right
            t = (i - 72) / (c.n - 2 - 72)
            x = (cx - 3) + ((W + 6) - (cx - 3)) * (t * t * 0.4 + t * 0.6)
            dog_side(im, c, x, i)
    return c
