import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- PENGUIN BRINGS YOU A GLASS OF WATER (gesture: drink water) ----------
# Modular: head (side / front / blink) + body + flippers (push / tap / rest) + feet; the glass is a prop
# that rides in front of the flippers. Waddle = bob/rock offsets, taps = flipper swaps + a water jiggle.
MYPAL = {'N': (62, 72, 118), 'L': (104, 118, 176), 'w': (245, 245, 240), 'b': (20, 20, 24),
         'n': (255, 160, 60), 'c': (120, 200, 230), 'C': (180, 230, 250), 's': (200, 200, 210)}
def S(rows): return sprite(rows, MYPAL)

HEAD_SIDE = S("""
...NNNNN...
..NNNNNNN..
.NNNNwbNNN.
.NNNNNNNNnn
.NNNNNNNN..
..NNNNNN...
""")
HEAD_FRONT = S("""
...NNNN...
..NNNNNN..
.NwbNNbwN.
.NNNnnNNN.
.NNNNNNNN.
..NNNNNN..
""")
HEAD_BLINK = S("""
...NNNN...
..NNNNNN..
.NLLNNLLN.
.NNNnnNNN.
.NNNNNNNN.
..NNNNNN..
""")
BODY = S("""
..NNNNNNNN..
.NNwwwwwwNN.
.NNwwwwwwwN.
.NNwwwwwwwN.
.NNwwwwwwwN.
.NNwwwwwwwN.
.NNwwwwwwNN.
..NNwwwwNN..
...NNNNNN...
""")
FLIPPER = S("""
L.
LL
LL
LL
.L
""")
PUSH = S("""
LLLL
.LLL
""")
TAP_UP = S("""
...L
..LL
.LL.
LL..
""")
TAP_HIT = S("""
LLLLL
.LLL.
""")
FEET = S("""
.nn.nn.
""")
GLASS = S("""
wwwwwwwww
s.......s
s.......s
sCCCCCCCs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
.sssssss.
""")
GLASS_JIGGLE = S("""
wwwwwwwww
s.......s
s.CC....s
sCccCCCCs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
sCccccccs
.sssssss.
""")
DING = S("""
w.w
.w.
""")

GLASS_DX = 13   # glass left edge relative to penguin body left

def penguin(im, c, x, y, head='side', bob=0, rock=0, feet_dx=0, arms='push'):
    c.blit(im, FEET, x + 2 + feet_dx, y + 9)
    c.blit(im, BODY, x, y - bob)
    if arms == 'push':
        c.blit(im, PUSH, x + 9, y + 3 - bob)
    elif arms == 'tap_up':
        c.blit(im, TAP_UP, x + 9, y - 1 - bob)
    elif arms == 'tap_hit':
        c.blit(im, TAP_HIT, x + 9, y + 1 - bob)
    else:                                            # rest: flippers down both sides
        c.blit(im, FLIPPER, x + 1, y + 1 - bob)
        c.blit(im, flip(FLIPPER), x + 9, y + 1 - bob)
    hd = {'side': HEAD_SIDE, 'front': HEAD_FRONT, 'blink': HEAD_BLINK}[head]
    c.blit(im, hd, x + 1 + rock, y - 5 - bob)

def build():
    c = Clip('gesture_penguin_water_01', 8.0)
    gy = H - 2                     # feet row
    by = gy - 9                    # body top
    glass_y = H - 1 - 16 + 1       # glass bottom on the floor
    park_x = CAM[0] - GLASS_DX - 4 # glass centred under the camera hole
    start_x = -14 - GLASS_DX - 9
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= 95:
            continue
        if i <= 26:                                   # waddle in from the left, pushing the glass
            t = i / 26
            x = start_x + (park_x - start_x) * (t if t < 0.75 else 0.75 + 0.25 * ease((t - 0.75) / 0.25))
            k = (i // 3) % 2
            penguin(im, c, x, by, 'side', bob=k, rock=(1 if k else -1), feet_dx=(1 if k else 0))
            c.blit(im, GLASS, x + GLASS_DX, glass_y)
        elif i <= 30:                                 # settle
            penguin(im, c, park_x, by, 'side')
            c.blit(im, GLASS, park_x + GLASS_DX, glass_y)
        elif i <= 42:                                 # tap-tap: raise (2), hit (2), back (2) x2
            j = (i - 31) % 6
            arms = 'tap_up' if j < 2 else ('tap_hit' if j < 4 else 'push')
            penguin(im, c, park_x, by, 'side', arms=arms)
            hit = j in (2, 3)
            c.blit(im, GLASS_JIGGLE if hit else GLASS, park_x + GLASS_DX, glass_y)
            if hit:
                c.blit(im, DING, park_x + GLASS_DX + 9, glass_y - 2)
        elif i <= 74:                                 # turn to the viewer, long expectant hold, one blink
            head = 'blink' if i in (58, 59) else 'front'
            penguin(im, c, park_x, by, head, rock=(1 if i >= 66 else 0), arms='rest')   # tiny head tilt: "well?"
            c.blit(im, GLASS, park_x + GLASS_DX, glass_y)
        elif i <= 77:                                 # back to the glass, lean in
            penguin(im, c, park_x, by, 'side', rock=1, arms='push')
            c.blit(im, GLASS, park_x + GLASS_DX, glass_y)
        else:                                         # push it off to the right, accelerating
            t = (i - 78) / 16
            x = park_x + ((W + 2) - park_x) * (t ** 1.5)
            k = (i // 3) % 2
            penguin(im, c, x, by, 'side', bob=k, rock=(1 if k else -1), feet_dx=(1 if k else 0))
            c.blit(im, GLASS, x + GLASS_DX, glass_y)
    return c
