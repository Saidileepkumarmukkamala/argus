import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

# ---------- CHROME TOASTER POPS TWO SLICES; THEY COME ALIVE AND WALK OFF HAND IN HAND (gag) ----------
# Modular: toaster body + eyes + lever, toast slice + eyes + legs. Shake, squint, pop, squash and walk are offsets/swaps.
TOASTER = sprite("""
...ssssssssssssssssssssss...
..sskkkkkkkkksskkkkkkkkkss..
..ssssssssssssssssssssssss..
.swwsssssssssssssssssssssP..
.swwssssssssssssssssssssspP.
.swsssssssssssssssssssssspP.
.sppppppppppppppppppppppPPP.
.sppppppppppppppppppppppPPP.
.sppppppppppppppppppppppPPP.
.PpppppppppppppppppppppppPP.
.PPPPPPPPPPPPPPPPPPPPPPPPPP.
...PP..................PP...
...PP..................PP...
""")
TOASTER_SQUASH = TOASTER.resize((30, 11), Image.NEAREST)     # pop recoil: wider, shorter
LEVER = sprite("""
Prr
Prr
""")
T_EYE = sprite("""
ww
wb
ww
""")
T_EYE_SQUINT = sprite("bb")
T_EYE_WIDE = sprite("""
www
wbw
www
""")
TOAST = sprite("""
.OOO.OOO.
OoooOoooO
OoooooooO
OoooooooO
OoooooooO
OoooooooO
OoooooooO
OoooooooO
.OOOOOOO.
""")
TOAST_SQUASH = TOAST.resize((11, 7), Image.NEAREST)
EYE_R = sprite("""
wb
ww
""")
EYE_L = flip(EYE_R)
EYE_SHUT = sprite("bb")
SMILE = sprite("""
b.b
.b.
""")
SLOT_L, SLOT_R = 4, 15          # toast x offsets inside the toaster
TW = 28                          # toaster width
TY = H - 13                      # toaster top (13 tall incl. feet)

def dot(im, x, y, col):
    if 0 <= x < W and 0 <= y < H: im.putpixel((int(x), int(y)), col)

def toaster(im, c, x, y, eyes='open', lever_up=False):
    c.blit(im, TOASTER, x, y)
    c.blit(im, LEVER, x + 26, y + (2 if lever_up else 7))
    for ex in (x + 9, x + 17):
        if eyes == 'squint': c.blit(im, T_EYE_SQUINT, ex, y + 6)   # strain: eyes shut tight
        elif eyes == 'wide': c.blit(im, T_EYE_WIDE, ex - 1, y + 5)
        else: c.blit(im, T_EYE, ex, y + 5)

def toast(im, c, x, y, legs=0, look=None, stride=0, blink=False):
    """x,y = top-left of the slice. legs: 0..3 px. look: 'L'|'R'|None. stride: 0 straight, 1 legs apart."""
    c.blit(im, TOAST, x, y)
    if legs:
        lx = (x + 1, x + 6) if stride else (x + 2, x + 5)
        for k, px_ in enumerate(lx):
            for j in range(legs): dot(im, px_, y + 9 + j, PAL['O'])
            dot(im, px_ + (1 if k else -1), y + 9 + legs - 1, PAL['O'])   # foot
    if look:
        if blink:
            c.blit(im, EYE_SHUT, x + 2, y + 4); c.blit(im, EYE_SHUT, x + 5, y + 4)
        else:
            e = EYE_R if look == 'R' else EYE_L
            c.blit(im, e, x + 2, y + 3); c.blit(im, e, x + 5, y + 3)
        c.blit(im, SMILE, x + 3, y + 6)

def build():
    c = Clip('gag_toaster_01', 7.0)
    TX = CAM[0] - TW // 2                      # 78: centred under the camera hole
    T_RATTLE, T_POP, T_LEAVE, T_LAND, T_SPROUT, T_WALK, T_MEET, T_OFF = 12, 27, 30, 37, 39, 45, 57, 61
    LAND_L, LAND_R = 62, 104                   # where the slices land (either side of where the toaster stood)
    FY = H - 9                                 # toast top when sitting on the floor with no legs
    for i in range(c.n):
        im = c.frame()
        # ---- toaster position ----
        tx = None
        if i < T_RATTLE: tx = -30 + (TX + 30) * ease(i / (T_RATTLE - 1))
        elif i < T_LEAVE: tx = TX
        elif i < T_LEAVE + 12: tx = TX + (-32 - TX) * ease((i - T_LEAVE) / 11)
        # ---- slices in the slots / in flight (drawn first so the toaster body occludes them) ----
        if T_POP <= i < T_LAND:
            t = (i - T_POP) / (T_LAND - T_POP - 1)
            ang = int(round(t * 4)) % 4 * 90
            for x0, x1, sgn in ((TX + SLOT_L, LAND_L, 1), (TX + SLOT_R, LAND_R, -1)):
                x = x0 + (x1 - x0) * t
                y = (TY + 1) + (FY - (TY + 1)) * t - 19 * 4 * t * (1 - t)
                c.blit(im, TOAST.rotate(sgn * ang), x, y)
        # ---- toaster: slide in, rattle + squint, squash on pop, wide eyes, slide off ----
        if tx is not None:
            if T_POP <= i < T_POP + 2:
                c.blit(im, TOASTER_SQUASH, tx - 1, TY + 2)
                c.blit(im, LEVER, tx + 27, TY + 3)
                for ex in (tx + 8, tx + 17): c.blit(im, T_EYE_WIDE, ex, TY + 5)
            else:
                dx = dy = 0; eyes = 'open'
                if T_RATTLE <= i < T_POP:
                    p = (i - T_RATTLE) / (T_POP - T_RATTLE)
                    amp = 1 + int(p * 2.2)
                    dx = amp * (1 if (i // (2 if p < 0.4 else 1)) % 2 == 0 else -1)
                    dy = -1 if p > 0.7 and i % 2 else 0
                    eyes = 'squint' if p > 0.3 else 'open'
                elif T_POP <= i < T_LEAVE + 4: eyes = 'wide'
                toaster(im, c, tx + dx, TY + dy, eyes, lever_up=i >= T_POP)
                if T_RATTLE <= i < T_POP:                                   # heat glow in the slots
                    for gx in (tx + dx + 5 + (i % 3) * 3, tx + dx + 16 + ((i + 1) % 3) * 3):
                        dot(im, gx, TY + dy + 1, PAL['n'])
        # ---- anticipation: the crusts creep up out of the slots, jittering ----
        if T_RATTLE <= i < T_POP:
            p = (i - T_RATTLE) / (T_POP - T_RATTLE)
            peek = (1 if p > 0.35 else 0) + (1 if p > 0.65 and i % 2 == 0 else 0) + (1 if p > 0.85 else 0)
            if peek:
                for sx in (SLOT_L, SLOT_R): c.blit(im, TOAST.crop((0, 0, 9, peek)), tx + dx + sx, TY + dy - peek)
        # ---- crumbs at the pop ----
        if T_POP <= i < T_POP + 4:
            k = i - T_POP
            for cx, cy in ((TX + 2 - k * 2, TY - 2 - k * 2), (TX + 25 + k * 2, TY - 2 - k * 2),
                           (TX + 10 - k, TY - 4 - k * 3), (TX + 18 + k, TY - 4 - k * 3)):
                dot(im, cx, cy, PAL['y'])
        # ---- landed slices: squash, sprout eyes + legs, walk to each other, walk off together ----
        if i < T_LAND: continue
        if i < T_LAND + 2:
            for lx in (LAND_L, LAND_R): c.blit(im, TOAST_SQUASH, lx - 1, H - 7)
            continue
        legs = min(3, max(0, i - T_SPROUT - 2))                     # legs grow 1px/frame
        look_on = i >= T_SPROUT
        blink = i in (T_SPROUT, T_SPROUT + 1)
        if i < T_WALK:
            for lx, look in ((LAND_L, 'R'), (LAND_R, 'L')):
                toast(im, c, lx, FY - legs, legs, look if look_on else None, 0, blink)
        elif i < T_MEET:
            t = ease((i - T_WALK) / (T_MEET - T_WALK - 1))
            lx = LAND_L + (LAND_R - 9 - LAND_L) * t
            j = (i - T_WALK) % 4
            toast(im, c, lx, FY - 3 + (-1 if j in (1, 2) else 0), 3, 'R', 1 if j < 2 else 0)
            toast(im, c, LAND_R, FY - 3, 3, 'L', 0, blink=(i == T_MEET - 3))
        elif i < T_OFF:                                              # joy hop together
            hop = (0, -2, -3, -1)[i - T_MEET]
            toast(im, c, LAND_R - 9, FY - 3 + hop, 3, 'R', 1 if hop else 0)
            toast(im, c, LAND_R, FY - 3 + hop, 3, 'L' if i - T_MEET < 2 else 'R', 1 if hop else 0)
        else:
            rx = LAND_R + (i - T_OFF) * 4.2
            j = i % 4
            bobA = -1 if j in (1, 2) else 0
            bobB = -1 if j in (3, 0) else 0
            toast(im, c, rx - 9, FY - 3 + bobA, 3, 'R', 1 if j < 2 else 0)
            toast(im, c, rx, FY - 3 + bobB, 3, 'R', 1 if j >= 2 else 0)
            dot(im, rx - 1, FY + 2 + min(bobA, bobB), PAL['y'])      # held hands at the seam
            dot(im, rx, FY + 2 + min(bobA, bobB), PAL['y'])
    return c

if __name__ == '__main__':
    c = build()
    assert c.frames[0].getbbox() is None and c.frames[-1].getbbox() is None, 'clip must start and end empty'
    print('ok', c.n)
