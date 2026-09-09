import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- PENGUIN BELLY-SLIDE (gag) ----------
# Modular: head (side / front / blink) + body + flipper + feet; slide pose is its own sprite.
MYPAL = {'N': (62, 72, 118), 'L': (104, 118, 176), 'w': (245, 245, 240), 'b': (20, 20, 24), 'n': (255, 160, 60)}
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
FLIPPER_UP = S("""
.L
LL
L.
L.
""")
FEET = S("""
.nn.nn.
""")
FLOP = S("""
............NNNNN.
...........NNNNNNN
..........NNNNwbNN
.........NNNNNNNNnn
........NNNNNNNN..
......NNNwwNNNN...
.....NNwwwwNN.....
....NNwwwwNN......
...NNwwwwNN.......
..NNwwwwNN........
.NNwwwwNN.........
.NNNNNN...........
.nn.nn............
""")
SLIDE = S("""
...........NNNNNNN....
..........NNNNNwbNN...
NNNNNNNNNNNNNNNNNNNnn.
NNNNNNNNNNNNNNNNNNN...
.NwwwwwwwwwwwwwwwwN...
nnwwwwwwwwwwwwwwww....
""")
SLIDE_FLIP_UP = S("""
.L
LL
""")
SLIDE_FLIP_DOWN = S("""
LL
L.
""")

def penguin(im, c, x, y, head='side', bob=0, rock=0, flip=0, feet_dx=0, neck=0):
    """x = left of body, y = top of body (9 tall); feet sit under it, head above. neck = head lift px."""
    c.blit(im, FEET, x + 2 + feet_dx, y + 9)
    c.blit(im, BODY, x, y - bob)
    c.blit(im, FLIPPER_UP if flip else FLIPPER, x + 2, y + 1 - bob - flip)
    hd = {'side': HEAD_SIDE, 'front': HEAD_FRONT, 'blink': HEAD_BLINK}[head]
    c.blit(im, hd, x + 1 + rock, y - 5 - bob - neck)

def build():
    c = Clip('gag_penguin_slide_01', 5.0)
    gy = H - 2                    # feet row
    by = gy - 9                   # body top
    stop_x = 40
    spray = []                    # (x, y, born)
    for i in range(c.n):
        im = c.frame()
        if i == 0 or i >= 58:
            continue
        if i <= 24:                                   # waddle in from the left
            t = i / 24
            x = -14 + (stop_x + 14) * (t if t < 0.8 else 0.8 + 0.2 * ease((t - 0.8) / 0.2))
            k = (i // 3) % 2
            penguin(im, c, x, by, 'side', bob=k, rock=(1 if k else -1), feet_dx=(1 if k else 0))
        elif i <= 27:                                 # settle
            penguin(im, c, stop_x, by, 'side')
        elif i <= 37:                                 # look at the viewer, blink
            head = 'blink' if i in (33, 34) else 'front'
            penguin(im, c, stop_x, by, head, rock=(1 if 29 <= i <= 31 else 0))   # tiny head tilt: "hm?"
        elif i <= 40:                                 # anticipation: face right, stretch up, flippers up
            penguin(im, c, stop_x, by, 'side', neck=1, rock=-1, flip=1)
        elif i == 41:                                 # flop: pivots forward over the feet
            c.blit(im, FLOP, stop_x + 1, gy - 12)
        elif i == 42:                                 # lands on the belly, puff of snow
            c.blit(im, SLIDE, stop_x + 2, gy - 4)
            for k in range(5): spray.append((stop_x - k // 2 + (k % 2) * 22, gy + 1 - k % 2, i))
        else:                                         # belly slide, accelerating, off the right edge
            t = (i - 43) / 14
            x = stop_x + 2 + ((W + 2) - stop_x - 2) * (t ** 1.6)
            c.blit(im, SLIDE, x, gy - 4)                       # paste clips at the edge: tail leaves last
            c.blit(im, SLIDE_FLIP_UP if (i // 2) % 2 else SLIDE_FLIP_DOWN, x + 7, gy - 4 if (i // 2) % 2 else gy - 3)
            for k in range(3):
                spray.append((x - 1 - ((i * 7 + k * 5) % 3), gy + 1 - ((i * 3 + k) % 2), i))
        # spray: white -> grey, drifts up-left, lives 3 frames
        for (sx, sy, born) in spray:
            age = i - born
            if age > 2: continue
            px, py = int(sx - age // 2), int(sy - age)
            if 0 <= px < W and 0 <= py < H:
                im.putpixel((px, py), [PAL['w'], PAL['s'], PAL['P']][age])
    return c
