import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- PIGEON PECKS THE CAMERA HOLE (gag) ----------
# Modular: body + head + wing + legs, so head-bob and wing-flap are offsets, not redraws.
P_BODY = sprite("""
......PppppP.....
.....PppppppPP...
....PppppppppPPP.
....PpppppppPPPPP
....PppppppPPPPPP
....PpppppppPPPP.
.....PpppppppPP..
......PppppppP...
.......PPPPPP....
""")
P_HEAD = sprite("""
...PPPP.
..PppppP
.PpwbpppP
nnPppppP
..PPPPP.
""")
P_WING_MID = sprite("""
.PPPPPPP.
PPPPPPPPP
.PPPPPP..
""")
P_WING_UP = sprite("""
....PP..
...PPPP.
..PPPPP.
.PPPPPP.
PPPPPPP.
""")
P_WING_DOWN = sprite("""
PPPPPPP.
.PPPPPP.
..PPPPP.
...PPPP.
....PP..
""")
P_LEGS = sprite("""
.n..n.
.n..n.
nn.nn.
""")

def pigeon(im, c, x, y, pose='stand', peck=0):
    """x,y = top-left of body. pose: stand | fly_up | fly_down."""
    c.blit(im, P_BODY, x, y)
    if pose == 'stand':
        c.blit(im, P_WING_MID, x + 5, y + 2)
        c.blit(im, P_LEGS, x + 5, y + 9)
        c.blit(im, P_HEAD, x - 1 - peck * 2, y - 3 + peck * 3)
    else:
        wing = P_WING_UP if pose == 'fly_up' else P_WING_DOWN
        c.blit(im, wing, x + 4, y - 4 if pose == 'fly_up' else y + 3)
        c.blit(im, P_HEAD, x - 1, y - 2)

def build():
    c = Clip('gag_pigeon_camera_01', 4.5)
    land_x, land_y = CAM[0] + 8, H - 13
    for i in range(c.n):
        im = c.frame()
        if i < 15:                                   # fly in from right, descend
            t = ease(i / 14)
            x = (W + 10) + (land_x - (W + 10)) * t; y = 6 + (land_y - 6) * t
            pigeon(im, c, x, y, 'fly_up' if (i // 3) % 2 == 0 else 'fly_down')
        elif i < 40:                                 # peck cycle: 4 up, 3 down
            j = (i - 15) % 7
            pigeon(im, c, land_x, land_y, 'stand', peck=1 if j >= 4 else 0)
        elif i < 43:
            pigeon(im, c, land_x, land_y, 'stand')
        else:                                        # fly off up-right
            t = ease((i - 43) / 10)
            x = land_x + ((W + 20) - land_x) * t; y = land_y + (-16 - land_y) * t
            pigeon(im, c, x, y, 'fly_up' if (i // 3) % 2 == 0 else 'fly_down')
    return c

