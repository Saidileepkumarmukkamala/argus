"""Black Hole Burp — the notch swallows anything that slides under it, until it meets an anvil.
Teacup, boot, ringed planet, fish get stretched tall and pulled up. The anvil won't go: the notch strains,
finally gulps it, then burps everything back out into a pile. The anvil drops last, flattens the pile,
and is so heavy it cracks the ledge and falls through. ~12 s."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sprite import *

BUCKET = 'gag'

PORC = ramp((190, 192, 205)); LEAT = ramp((152, 94, 54)); PLAN = ramp((132, 92, 212)); RING = ramp((222, 182, 92))
FISH = ramp((238, 138, 58)); IRON = ramp((112, 118, 136))
MYPAL = {
    # porcelain teacup: S shadow c base l light h highlight; B blue band, D band shadow; T tea, t tea light
    'S': PORC[0], 'c': PORC[1], 'l': PORC[2], 'h': PORC[3], 'B': (84, 126, 204), 'D': (52, 84, 156), 'T': (146, 88, 40), 't': (204, 142, 80),
    # leather boot: K shadow b base m light n highlight; Z sole dark z sole; L lace, e eyelet; q sock red, Q sock shadow
    'K': LEAT[0], 'b': LEAT[1], 'm': LEAT[2], 'n': LEAT[3], 'Z': (38, 34, 46), 'z': (76, 70, 84), 'L': (236, 226, 204), 'e': (206, 172, 82),
    'q': (206, 66, 70), 'Q': (140, 40, 56),
    # planet: U shadow u base v light V highlight; A band; ring: R shadow i base I light j highlight
    'U': PLAN[0], 'u': PLAN[1], 'v': PLAN[2], 'V': PLAN[3], 'A': (196, 132, 236), 'R': RING[0], 'i': RING[1], 'I': RING[2], 'j': RING[3],
    # fish: F shadow f base g light G highlight; d scale line; x fin, X fin shadow; eye w white k dark W glint
    'F': FISH[0], 'f': FISH[1], 'g': FISH[2], 'G': FISH[3], 'd': (200, 104, 44), 'x': (252, 204, 96), 'X': (196, 138, 52),
    'w': (250, 250, 245), 'k': (24, 20, 34), 'W': (255, 255, 255),
    # anvil: Y shadow a base E light H highlight; r rivet
    'Y': IRON[0], 'a': IRON[1], 'E': IRON[2], 'H': IRON[3], 'r': (64, 66, 84),
}
S = lambda rows: outline(sprite(rows, MYPAL))

TEACUP = S("""
....hhhhhhhhhhhhhh......
...hlTtTTTTTTTTTTlh.....
...lcTTTTTTTTTTTTcS.....
...lcccccccccccccS.hh...
...lcBBBBBBBBBBBDSh.lh..
...lcccccccccccccS...l..
...lcBBBBBBBBBBDSS...l..
....lccccccccccSS.l.l...
....lcccccccccSSS.lll...
.....lcccccccSSSS.......
......lccccSSSSS........
.......hcSSSSSS.........
........SSSSSS..........
..hllllllllllllllllllh..
.hcccccccccccccccccccSS.
..SSSSSSSSSSSSSSSSSSSS..
""")
BOOT = S("""
..qqqqqqqqqq..
..qQqqqqqqQq..
..nmmbbbbbbK..
..nmbbLeLbbK..
..nmbbeLebbK..
..nmbbLeLbbK..
..nmbbeLebbK..
..nmbbLeLbbK..
..nmbbeLebbK..
..nmbbLeLbbK..
..nmbbbbbbbK..
..nmbbbbbbbK..
..nmbbbbbbbK..
..nmbbbbbbbK..
..nmbbbbbbbKK.
..nmbbbbbbbbKK
.nmmbbbbbbbbbK
nmmbbbbbbbbbbK
nmbbbbbbbbbKKK
zzzzzzzzzzzzzz
ZZZZZZZZZZZZZZ
ZZZZ..ZZZZZZZ.
""")
PLANET = S("""
............uvvvvvu...........
..........uvvvvVVvvvu.........
.........uuvvvvVVVvvuu........
........uuuvvvvvvvvvvuuU......
........uuuAAAAAAAAAAuuU......
.......uuuuuuuuuuuuuuuUUU.....
.......uuuuuuuuuuuuuuuUUU.....
.......uuuAAAAAAAAAAAAUUU.....
..jIIIIuuuuuuuuuuuuuuuUUUIIR..
.jI....uuuuuuuuuuuuuuUUU...IR.
.jI....UUuuuuuuuuuuUUUU....IR.
.jIIIjjjjjjjjjjjjjjjjjjjjjIIR.
..RiiiiiiiiiiiiiiiiiiiiiiiiR..
....RRRRRRRRRRRRRRRRRRRRRR....
........UUUuuuuuuuUUUUU.......
.........UUUuuuuuUUUUU........
..........UUUUUUUUUU..........
............UUUUUU............
""")
def fish_rows(tail):
    t1, t2 = ('Xx..', 'xX..') if tail else ('.Xx.', '.xX.')
    return f"""
...........xxxx...........
..........XxxxX...........
........GGGGGGGGGGGG......
{t1}..GGgggggggggggggGG...
{t2}.GggdggdggdggggggggG..
{t1}GggdggdggdgggggggwwkG.
{t2}FggdggdggdggggggwWkkk.
{t1}FfgdggdggdgggggfwkkkG.
{t2}FffdffdffdfffffffkkFF.
{t1}.FffffffffffffFFFFFF..
{t2}..FFffffffffFFFFF.....
XX....FFFFxxxFFFF.........
..........XxX.............
"""
FISH_A, FISH_B = S(fish_rows(0)), S(fish_rows(1))
ANVIL = S("""
..........HHHHHHHHHHHHHHHHHHHHHHHHHHH...
....HHHHHEEEEEEEEEEEEEEEEEEEEEEEEEEEEH..
..HHEEEEaaaaaaaaaaaaaaaaaaaaaaaaaaaaaYY.
.HEEaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaYYY.
.EEaaaaaraaaaaaaaaaaaaaaaaaaaaaaaraaYYY.
..EaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaYYY.
....YYYYYaaaaaaaaaaaaaaaaaaaaaaaaaaYYY..
........YYaaaaaaaaaaaaaaaaaaaaaaaaYYY...
...........EaaaaaaaaaaaaaaaaaaaaYYY.....
............EaaaaaaaaaaaaaaaaaaYYY......
............EaaaaaaaaaaaaaaaaaaYYY......
............EaaaaaaaaaaaaaaaaaaYYY......
............EaaaaaaaaaaaaaaaaaaYYY......
...........EaaaaaaaaaaaaaaaaaaaaYYY.....
..........EaaaaaaaaaaaaaaaaaaaaaaYYY....
.........EaaaaaaaaaaaaaaaaaaaaaaaaYYY...
........HEEEEEEEEEEEEEEEEEEEEEEEEEEYYY..
........EaaaaraaaaaaaaaaaaaaaaraaaaaYYY.
........EaaaaaaaaaaaaaaaaaaaaaaaaaaaYYY.
........YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY.
""")
BOOT_LYING = BOOT.transpose(Image.ROTATE_90)      # toe up, sole to the right: lands on its side in the pile

CX = (NOTCH_L + NOTCH_R) // 2                     # 92: the notch's mouth
FLOOR = H                                         # bottom edge (sprite bottom = FLOOR)

def scaled(spr, sx, sy):
    return spr.resize((max(1, round(spr.width * sx)), max(1, round(spr.height * sy))), Image.NEAREST)

def suck(c, im, spr, j, n=8):
    """Object at centre, bottom on the floor: stretch 2x tall / half wide (first half), then whip up into the notch."""
    t = j / (n - 1)
    st = ease(min(1.0, t * 2)); s = scaled(spr, 1 - 0.5 * st, 1 + 1.0 * st)
    lift = 0 if t < 0.5 else (t - 0.5) * 2
    y = FLOOR - s.height - (s.height + 34) * lift * lift
    c.blit(im, s, CX - s.width // 2, y)
    dots(im, [(CX - 9 + (k * 5) % 19, NOTCH_B + 1 + (k * 11 - j * 4) % 26) for k in range(4)], (96, 96, 112))
    if j == 0: puff(im, CX - spr.width // 2, H - 1, 0.3); puff(im, CX + spr.width // 2, H - 1, 0.3)

def drop_out(c, im, spr, j, n, tx, ty, arc=0):
    """Burp: from inside the notch mouth down to (tx, ty) (top-left); gravity ease; squash on the landing frame."""
    t = min(1.0, j / (n - 1))
    if j >= n:
        c.blit(im, spr, tx, ty); return True
    x = (CX - spr.width // 2) + (tx - (CX - spr.width // 2)) * t
    y = (NOTCH_B - spr.height) + (ty - (NOTCH_B - spr.height)) * t * t - arc * 4 * t * (1 - t)
    if j == n - 1:
        s = scaled(spr, 1.15, 0.85); c.blit(im, s, tx - (s.width - spr.width) // 2, ty + spr.height - s.height)
        puff(im, tx, ty + spr.height - 1, 0.2); puff(im, tx + spr.width, ty + spr.height - 1, 0.2)
    else:
        c.blit(im, spr, x, y)
    return False

def build():
    c = Clip('gag_black_hole_burp_01', 12.0)
    T = [(TEACUP, 1), (BOOT, 12), (PLANET, 24), (FISH_A, 36)]     # (sprite, frame it enters); 10 in + 8 suck each
    AN_IN, AN_STOP, AN_SHOOT, AN_GONE = 52, 66, 83, 87           # anvil: slide 52-65, strain 66-82, shoot 83-86, silence 87-94
    BURP = 95
    # pile layout (top-left): fish lying left, boot on its side centre, planet right, teacup upright on the boot
    fish_p = (54, FLOOR - FISH_A.height); planet_p = (100, FLOOR - PLANET.height)
    boot_p = (76, FLOOR - BOOT_LYING.height); cup_p = (boot_p[0] + 2, boot_p[1] - TEACUP.height + 2)
    LAND = 113; DROP = 121; HIT = 126; POP = HIT - 3; CRACK = 131; SINK = 134
    for i in range(c.n):
        im = c.frame()
        # ---- 1. the conveyor of victims ----
        for spr, t0 in T:
            j = i - t0
            if j < 0 or j >= 18: continue
            fish = spr is FISH_A
            if fish and (j // 2) % 2: spr = FISH_B                        # tail flips every 2 frames
            if j < 10:                                                    # slide in from the left, settle at centre
                t = ease(j / 9); x = -spr.width + (CX - spr.width // 2 + spr.width) * t
                hop = 0
                if spr is BOOT: hop = 3 if j % 4 == 1 else (1 if j % 4 == 2 else 0)          # boot hops along
                if fish: hop = (4, 6, 4, 0)[j % 4]                                              # fish flops
                if spr is PLANET: hop = bob(j, 4, 1)                                           # planet rolls, ring wobbles
                y = FLOOR - spr.height - hop
                c.blit(im, spr, x, y); shadow(im, x + 2, spr.width - 4)
                if j >= 7 and spr is TEACUP: puff(im, x - 2, H - 1, (j - 7) / 3)              # skid dust
                if fish and j % 4 == 3: puff(im, x + 4, H - 1, 0.3)
            else:
                suck(c, im, spr, j - 10)
        # ---- 2. the anvil ----
        if AN_IN <= i < AN_STOP:                                          # heavy slide, decelerating
            t = ease((i - AN_IN) / (AN_STOP - AN_IN - 1)); x = -ANVIL.width + (CX - ANVIL.width // 2 + ANVIL.width) * t
            c.blit(im, ANVIL, x, FLOOR - ANVIL.height); shadow(im, x + 8, ANVIL.width - 10)
            if i >= AN_STOP - 4: puff(im, x - 1, H - 1, (i - AN_STOP + 4) / 4)
        elif AN_STOP <= i < AN_SHOOT:                                     # strain: tremble, 1-px stretch, shivering ledge dust, suction streaks
            j = i - AN_STOP; k = min(1.0, j / 12)
            s = ANVIL if j < 5 else scaled(ANVIL, 1.0, 1 + 1 / ANVIL.height)
            jit = 0 if j < 3 else ((-1, 0, 1, 0)[j % 4] if k < 1 else (-1, 1)[j % 2])
            x = CX - ANVIL.width // 2 + jit
            c.blit(im, s, x, FLOOR - s.height); shadow(im, x + 8, ANVIL.width - 10)
            for kk in range(3 + int(k * 5)):                                # streaks intensify as the notch strains
                dots(im, [(CX - 24 + (kk * 13) % 48, NOTCH_B + 1 + (kk * 7 - j * 3) % 10)], (96, 96, 112))
            for kk in range(8):                                             # dust on the ledge shivers
                dx = 18 + (kk * 19) % 150; dy = H - 2 - ((j + kk) % 2 if j > 2 else 0)
                dots(im, [(dx + ((j // 2 + kk) % 2 if j > 2 else 0), dy)], (110, 108, 122))
        elif AN_SHOOT <= i < AN_GONE:                                      # gulp: shoots up in 4 frames
            j = i - AN_SHOOT; s = scaled(ANVIL, 0.9 - 0.1 * j, 1.2 + 0.3 * j)
            y = FLOOR - s.height - (12, 30, 60, 90)[j]
            c.blit(im, s, CX - s.width // 2, y)
            puff(im, CX - 14, H - 2, j / 4); puff(im, CX + 14, H - 2, j / 4)
            dots(im, [(CX - 20 + (kk * 11) % 40, NOTCH_B + 1 + (kk * 5 - j * 6) % 20) for kk in range(8)], (110, 110, 128))
        # ---- 3. the burp: everything comes back, separate parabolas ----
        if i >= BURP:
            order = [(FISH_A, 0, 9, fish_p, 6), (PLANET, 2, 9, planet_p, 8), (BOOT_LYING, 5, 9, boot_p, 4), (TEACUP, 8, 10, cup_p, 12)]
            pile_done = i >= HIT
            if not pile_done:
                for spr, t0, n, pos, arc in order:
                    j = i - BURP - t0
                    if j < 0 or (spr is TEACUP and i >= POP): continue
                    if spr is FISH_A and j < n: spr = FISH_B if (j // 2) % 2 else FISH_A
                    landed = drop_out(c, im, spr, j, n, pos[0], pos[1], arc)
                    if landed and spr is TEACUP and j in (n, n + 1): c.blit(im, TEACUP, pos[0], pos[1] - 1)   # hop-settle on the boot
                    if landed: shadow(im, pos[0] + 2, spr.width - 4)
                if i >= BURP + 4 and i < HIT: shadow(im, 40, 100)
            # ---- 4. the anvil drops last; the cup is squeezed out from under it ----
            if POP <= i < POP + 12:                                       # the teacup pops out sideways off the right edge, spinning, unbroken
                j = i - POP; t = j / 11; tx = cup_p[0] + 6 + (W + 4 - cup_p[0]) * t; ty = cup_p[1] - 26 * 4 * t * (1 - t) + 14 * t
                cup = TEACUP
                for _ in range((j // 2) % 4): cup = cup.transpose(Image.ROTATE_270)
                c.blit(im, cup, tx, ty)
            if DROP <= i < HIT:
                t = (i - DROP) / (HIT - DROP); ay = (NOTCH_B - ANVIL.height) + ((FLOOR - 4 - ANVIL.height) - (NOTCH_B - ANVIL.height)) * t * t
                c.blit(im, ANVIL, CX - ANVIL.width // 2 - 4, ay)
            if i >= HIT:
                j = i - HIT
                # the flattened pile: 4-px pancakes of everything under the anvil
                sink = 0
                if i >= SINK:
                    s = i - SINK; sink = 2 * s * s
                fy = FLOOR - 4 + sink
                sq = (1.0, 1.25, 1.45)[min(j, 2)]
                for spr, (px, _) in ((FISH_A, fish_p), (PLANET, planet_p), (BOOT_LYING, boot_p)):
                    ps = scaled(spr, sq, 5 / spr.height); c.blit(im, ps, px - (ps.width - spr.width) // 2, fy - 1)
                s = scaled(ANVIL, 1.08, 0.9) if j == 0 else ANVIL
                ax = CX - ANVIL.width // 2 - 4 - (s.width - ANVIL.width) // 2
                c.blit(im, s, ax, fy - s.height)
                if j < 6:
                    puff(im, ax - 2, H - 2, j / 5); puff(im, ax + s.width + 2, H - 2, j / 5)
                    puff(im, ax + 6, H - 6, j / 5); puff(im, ax + s.width - 6, H - 6, j / 5)
                    burst(im, CX, FLOOR - 6, j, n=8, speed=1.4, life=8, cols=((120, 118, 132), (150, 148, 160)))
            if i >= HIT:
                j = i - HIT
                # the ledge cracks under the weight, then gives way
                if i >= CRACK:
                    crack = [(ax + 4, H - 1), (ax + 5, H - 2), (ax + 6, H - 3), (ax + s.width - 5, H - 1), (ax + s.width - 6, H - 2),
                             (ax + s.width - 8, H - 3), (ax + 12, H - 1), (ax + s.width - 14, H - 1)]
                    if i >= CRACK + 1: crack += [(ax + 2, H - 1), (ax + 3, H - 3), (ax + 8, H - 4), (ax + s.width - 3, H - 1), (ax + s.width - 10, H - 4)]
                    dots(im, [(x_, y_ + sink) for x_, y_ in crack], (58, 56, 70))
                if i >= SINK:
                    sk = i - SINK
                    for kk in range(6): puff(im, ax - 4 + (kk * (s.width + 8)) // 5, H - 1, sk / 6)
    return c
