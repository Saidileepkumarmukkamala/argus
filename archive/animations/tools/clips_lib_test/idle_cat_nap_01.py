import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'idle'

# ---------- ORANGE CAT: walks in, circles, curls up, naps, stretches, leaves (idle) ----------
# Modular: every part is drawn facing LEFT and composed on a layer; facing right = flip the layer.
CP = {'o': (242, 150, 58), 'O': (190, 92, 28), 'p': (245, 140, 160), 'k': (70, 34, 14)}

BODY = sprite("""
..oooooooooooo..
.ooooOoooOoooooo
oooooooooooooooo
oooooooooooooooo
.oooooooooooooo.
""", CP)
HEAD = sprite("""
.o...o.
.op.po.
.ooooo.
ooooooo
obwoooo
ooooooo
.opooo.
..ooo..
""", CP)
HEAD_SHUT = sprite("""
.o...o.
.op.po.
.ooooo.
ooooooo
okkoooo
ooooooo
.opooo.
..ooo..
""", CP)
LEGS_A = sprite("""
.oo........oo.
.oo........oo.
.oo........oo.
""", CP)
LEGS_B = sprite("""
oo.oo....oo.oo
oo..oo..oo..oo
o....o..o....o
""", CP)
LEGS_TUCK = sprite("""
.oooo.....oooo.
""", CP)
TAIL_UP = sprite("""
..OO
.oOo
ooo.
oO..
o...
""", CP)
TAIL_DOWN = sprite("""
o....
oO...
.ooOo
""", CP)
# back view (narrow, no face) and front view (two eyes) for the turning circle
BACK = sprite("""
.o.....o...
.oo...oo...
.ooooooo...
.ooooooo.OO
.ooooooo.oO
.ooooooo.o.
ooooooooooo
ooooooooo..
oooOoOooo..
ooooooooo..
.ooooooo...
.oo...oo...
.oo...oo...
""", CP)
FRONT = sprite("""
.o.....o.
.op...po.
.ooooooo.
.ooooooo.
.bwoooowb
.ooooooo.
.oooopoo.
ooooooooo
oowwwwwoo
oowwwwwoo
.ooooooo.
.oo...oo.
.oo...oo.
""", CP)
# curled-up ball: body A (exhale) / B (inhale, one row taller, chest a px fuller); head tucked low in front
CURL_A = sprite("""
......ooooooo....
....ooooooooooo..
...oooOoooOoooooo
..ooooooooooooooo
..ooooooooooooooo
..ooooooooooooooo
...oooooooooooooo
....ooooooooooooo
""", CP)
CURL_B = sprite("""
......oooooooo...
....oooooooooooo.
...oooOoooOoooooo
..ooooooooooooooo
..ooooooooooooooo
..ooooooooooooooo
..ooooooooooooooo
...oooooooooooooo
....ooooooooooooo
""", CP)
# tail wraps under the body along the floor and curls up in front of the chin; tip lifts 1-2 px on a flick
TAIL_CURL = sprite("""
oo.....................
.oooooOooOooOooOooooo..
""", CP)
TAIL_CURL_F1 = sprite("""
oo.....................
o......................
.oooooOooOooOooOooooo..
""", CP)
TAIL_CURL_F2 = sprite("""
oo.....................
o......................
o......................
.oooooOooOooOooOooooo..
""", CP)
# stretch: front paws slid forward and low, rump high, back sloping
STRETCH = sprite("""
......................oo..
....................ooooo.
..................oooooooo
...............ooooOoooooo
............ooooooOooooooo
.........ooooooooooooooooo
......oooooooooooooo.oo.oo
...ooooooooooooooo..oo.oo.
oooooooooooooooo....oo.oo.
oooooo..............oo.oo.
""", CP)

def layer():
    return Image.new('RGBA', (40, 18), (0, 0, 0, 0))

def put(L, spr, x, y): L.paste(spr, (int(x), int(y)), spr)

def cat_side(walk=0, bob=0, head_dy=0, tail=TAIL_UP, crouch=False, shut=False):
    """Side view facing left on a 40x18 layer; ground = layer bottom. Anchor = layer top-left."""
    L = layer()
    if crouch:
        put(L, LEGS_TUCK, 8, 17)
        put(L, BODY, 8, 12 - 1); put(L, tail, 23, 8 if tail is TAIL_UP else 13)
        put(L, HEAD_SHUT if shut else HEAD, 4, 6 + head_dy)
    else:
        put(L, LEGS_A if walk == 0 else LEGS_B, 9, 15)
        put(L, BODY, 8, 10 - bob); put(L, tail, 23, 7 - bob)
        put(L, HEAD_SHUT if shut else HEAD, 4, 4 - bob + head_dy)
    return L

def cat_curl(inhale=False, flick=0, head_dy=0, shut=True):
    L = layer()
    put(L, [TAIL_CURL, TAIL_CURL_F1, TAIL_CURL_F2][flick], 0, 16 - flick)
    put(L, CURL_B if inhale else CURL_A, 6, 9 if inhale else 10)
    put(L, HEAD_SHUT if shut else HEAD, 2, 10 + head_dy)
    return L

def cat_stretch():
    L = layer()
    put(L, STRETCH, 0, 8); put(L, TAIL_UP, 22, 4); put(L, HEAD, 2, 9)
    return L

def cat_turn(front):
    L = layer(); put(L, FRONT if front else BACK, 12, 5); return L

def build():
    c = Clip('idle_cat_nap_01', 12.0)
    GY = H - 18                      # layer top so the layer bottom sits on the strip floor
    X_IN, X_REST = W + 2, 148        # walk-in target (facing left); ball sits at the far right
    for i in range(c.n):
        im = c.frame()
        L, x, facing_right = None, X_REST, False
        if i == 0 or i >= 142:
            continue                                     # empty bookends
        if i < 25:                                       # walk in from the right, facing left
            t = 1 - (1 - i / 24) ** 2; x = X_IN + (X_REST - X_IN) * t
            L = cat_side(walk=(i // 3) % 2, bob=(i // 3) % 2)
        elif i < 45:                                     # turn a small circle: back, right, front, left
            j = (i - 25) // 5; s = (i - 25) % 5
            drift = [3, 5, 3, 0][j]; x = X_REST + drift
            if j == 0: L = cat_turn(front=False)
            elif j == 1: L = cat_side(walk=(s // 2) % 2); facing_right = True
            elif j == 2: L = cat_turn(front=True)
            else: L = cat_side(walk=0, head_dy=1)
        elif i < 53:                                     # settle down: crouch, then curl
            L = cat_side(crouch=True, head_dy=(i - 45) // 2, tail=TAIL_UP if i < 47 else TAIL_DOWN) if i < 49 else cat_curl(shut=False, head_dy=-(52 - i))
        elif i < 101:                                    # sleep: breathe (7 out / 5 in), tail-tip flick now and then
            k = (i - 53) % 12
            L = cat_curl(inhale=k >= 7, flick={17: 1, 18: 2, 19: 2, 20: 1, 35: 1, 36: 2, 37: 1}.get(i - 53, 0))
        elif i < 107:                                    # wake: eye opens, head lifts
            L = cat_curl(shut=False, head_dy=-((i - 101) // 2))
        elif i < 113:                                    # get up: crouch -> stand
            L = cat_side(crouch=True, head_dy=1) if i < 110 else cat_side(walk=0)
        elif i < 125:                                    # long stretch, held, tail high
            L = cat_stretch() if i < 122 else cat_side(walk=0)
        elif i < 128:                                    # turn to face right
            L = cat_turn(front=False); x = X_REST + 2
        else:                                            # walk out right
            t = ((i - 128) / 13) ** 2 * 0.4 + (i - 128) / 13 * 0.6; x = X_REST + (X_IN - X_REST) * t
            L = cat_side(walk=(i // 3) % 2, bob=(i // 3) % 2); facing_right = True
        if L is not None:
            if facing_right: L = flip(L)
            c.blit(im, L, x, GY)
    return c
