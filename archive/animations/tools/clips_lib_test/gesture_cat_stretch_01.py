import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gesture'

# ---------- TUXEDO CAT: walks in, big slow stretch (arch high -> long low), yawns, looks at you, leaves ----------
# Modular, every part faces LEFT (it enters from the right and exits left, so no flipping).
# Dark fur is a charcoal, not black: pure black vanishes on the strip. White chest/socks/muzzle carry the silhouette.
CP = {'k': (88, 88, 104), 'K': (120, 120, 138), 'i': (240, 140, 160), 'm': (170, 60, 80), 'b': (16, 16, 20)}

HEAD = sprite("""
..k....k.
..kK..Kk.
..kkkkkk.
.kkkkkkkk
.kbwkkkkk
wwwkkkkkk
iwwwkkkk.
.wwwkkk..
""", CP)
HEAD_SHUT = sprite("""
.kbbkkkkk
""", CP)                                       # pastes over the eye row
HEAD_FRONT = sprite("""
.k.....k.
.kK...Kk.
.kkkkkkk.
kkkkkkkkk
kwbkkkbwk
kkkwwwkkk
kkwwiwwkk
.kkwwwkk.
""", CP)
HEAD_FRONT_BLINK = sprite("""
kbbkkkbbk
""", CP)
HEAD_YAWN_SMALL = sprite("""
..k....k.
..kK..Kk.
..kkkkkk.
.kkkkkkkk
.kbbkkkkk
wwwkkkkkk
mmwwkkkk.
.wwwkkk..
""", CP)
HEAD_YAWN = sprite("""
..k....k.
..kK..Kk.
..kkkkkk.
.kkkkkkkk
.kbbkkkkk
wwwkkkkkk
wwwwkkkkk
mmmwkkkk.
mmmmkkkk.
immmkkkk.
.wwwkkk..
""", CP)
BODY = sprite("""
..kkkkkkkkkkk..
.kkkkkkkkkkkkkk
kkkkkkkkkkkkkkk
wwkkkkkkkkkkkkk
.wwkkkkkkkkkkk.
""", CP)
LEGS_A = sprite("""
.kk........kk.
.kk........kk.
.ww........ww.
""", CP)
LEGS_B = sprite("""
kk.kk....kk.kk
kk..kk..kk..kk
w....w..w....w
""", CP)
TAIL_UP = sprite("""
..ww
.kkw
kkk.
kk..
k...
""", CP)
TAIL_QUIVER = sprite("""
.ww.
.kkw
kkk.
kk..
k...
""", CP)
TAIL_LOW = sprite("""
kk..
.kk.
..kw
..ww
""", CP)
# arch: on tiptoe, back humped high, head hangs at the front
ARCH = sprite("""
.......kkkkkkk....
.....kkkkkkkkkkk..
....kkkkkkkkkkkkk.
...kkkkkkkkkkkkkk.
..kkkkkkkkkkkkkkk.
..kkkkkkkkkkkkkkk.
..kkkkkkkkkkkkkk..
..kkkk.......kkk..
..wkk........kkk..
...kk........kk...
...kk........kk...
...kk........kk...
...ww........ww...
""", CP)
# long low: chest down, front paws slid forward, rump high. Two reaches so the slide reads as motion.
LOW_MID = sprite("""
...................kkkk...
................kkkkkkkkk.
.............kkkkkkkkkkkkk
..........kkkkkkkkkkkkkkkk
.......kkkkkkkkkkkkkkkkkkk
....kkkkkkkkkkkkkkkkk..kkk
..kkkkkkkkkkkkkkkkk...kkk.
kkkkkkkkkkkkkkkk......kk..
wwkkkkkkkkkkkk........ww..
""", CP)
LOW_FAR = sprite("""
.......................kkkk...
....................kkkkkkkkk.
.................kkkkkkkkkkkkk
..............kkkkkkkkkkkkkkkk
...........kkkkkkkkkkkkkkkkkkk
........kkkkkkkkkkkkkkkkk..kkk
.....kkkkkkkkkkkkkkkkkk...kkk.
..kkkkkkkkkkkkkkkkkkk.....kk..
kkkkkkkkkkkkkkkkkk........kk..
wwwkkkkkkkkkkkkk..........ww..
""", CP)

LW, LH = 46, 22

def layer(): return Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
def put(L, spr, x, y): L.paste(spr, (int(x), int(y)), spr)

def stand(walk=0, bob=0, head_dy=0, head=None, blink=False, tail=TAIL_UP):
    """Standing cat on a layer, feet on the layer bottom. Anchor = layer top-left."""
    L = layer()
    put(L, LEGS_A if walk == 0 else LEGS_B, 11, LH - 3)
    put(L, BODY, 10, LH - 7 - bob); put(L, tail, 23, LH - 11 - bob)
    hy = LH - 13 - bob + head_dy
    if head == 'front':
        put(L, HEAD_FRONT, 7, hy)
        if blink: put(L, HEAD_FRONT_BLINK, 7, hy + 4)
    elif head == 'yawn':
        put(L, HEAD_YAWN, 6, hy - 1)
    elif head == 'yawn_small':
        put(L, HEAD_YAWN_SMALL, 6, hy)
    else:
        put(L, HEAD, 6, hy)
        if blink: put(L, HEAD_SHUT, 6, hy + 4)
    return L

def arch(head_dy=0, tail_t=1.0, rise=1.0):
    """rise<1 draws the whole pose lower (legs clip below the floor) so the hump grows up out of the crouch."""
    L = layer(); d = int(5 * (1 - rise))
    put(L, ARCH, 9, LH - 13 + d); put(L, TAIL_UP, 24, LH - 16 - int(2 * tail_t) + d)
    put(L, HEAD, 2, LH - 10 + head_dy + d)
    return L

def low(far=False, head_dx=0, head_dy=0, quiver=False):
    L = layer(); tail = TAIL_QUIVER if quiver else TAIL_UP
    if far: put(L, LOW_FAR, 1, LH - 10); put(L, tail, 24, LH - 14)
    else:   put(L, LOW_MID, 5, LH - 9); put(L, tail, 22, LH - 13)
    put(L, HEAD, 3 + head_dx, LH - 8 + head_dy)
    return L

def build():
    c = Clip('gesture_cat_stretch_01', 7.0)
    GY = H - LH
    X_IN, STAND = W + 4, 52                    # layer x when fully off right / when stopped
    for i in range(c.n):
        im = c.frame()
        L, x = None, STAND
        if i == 0 or i >= 83: continue                             # empty bookends
        if i < 19:                                                 # walk in from the right
            t = i / 18; t = 1 - (1 - t) ** 2
            x = X_IN + (STAND - X_IN) * t
            L = stand(walk=(i // 3) % 2, bob=(i // 3) % 2)
        elif i < 23:                                               # stop, sniff the floor: head dips (anticipation)
            L = stand(head_dy=min(3, i - 19), tail=TAIL_LOW)
        elif i < 35:                                               # ARCH: pops up, then the hump holds and the head hangs lower
            j = i - 23
            if j == 0: L = stand(head_dy=3, bob=1, tail=TAIL_LOW)
            elif j < 4: L = arch(rise=ease(j / 3), tail_t=0)
            else: L = arch(head_dy=int(2 * ease((j - 4) / 6)), tail_t=ease((j - 4) / 6))
        elif i < 53:                                               # LONG LOW: slide forward in two reaches, chest to the floor
            j = i - 35
            if j == 0: L = arch(head_dy=2, rise=0.5)                # sinks forward before the paws slide out
            elif j < 8:  L = low(False, head_dx=-int(2 * ease(j / 7)), head_dy=int(ease(j / 7)))
            else:      L = low(True, head_dx=-2 - int(2 * ease((j - 8) / 6)), head_dy=1 + int(ease((j - 8) / 6)),
                               quiver=j in (14, 16))
        elif i < 57:                                               # gather back up to standing
            j = i - 53
            L = low(False, head_dx=-1, head_dy=0) if j < 2 else stand(head_dy=1, tail=TAIL_LOW)
        elif i < 66:                                               # YAWN: mouth cracks, gapes, snaps shut
            j = i - 57
            if j == 0 or j == 7: L = stand(head='yawn_small')
            elif j < 7: L = stand(head='yawn', head_dy=-1 - (j >= 3))
            else: L = stand(blink=True)
        elif i < 72:                                               # look straight at the viewer, one blink
            L = stand(head='front', blink=i in (69, 70))
        else:                                                      # walk off left
            t = (i - 72) / 10; t = t * t * 0.4 + t * 0.6
            x = STAND + (-LW - 2 - STAND) * t
            L = stand(walk=(i // 3) % 2, bob=(i // 3) % 2)
        if L is not None: c.blit(im, L, x, GY)
    return c
