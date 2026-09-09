"""Tiny pixel-sprite engine for notch clips. Zero dependencies beyond Pillow + ffmpeg.

Logical canvas: 240x40 px (6:1 strip). Export scales x5 with nearest-neighbour -> 1200x200.
Sprites are ASCII grids; one char = one pixel; '.' is transparent.
Every clip starts and ends on an empty strip so any clip can follow any clip.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw

W, H = 184, 52          # the whole black shape at 1.5 pt per art px (3 device px): 276 x 78 pt on a 14" MBP
# The hardware notch occludes the top-centre of the canvas. Nothing drawn there is ever seen — use it as an object:
# hang from its underside (y = NOTCH_B), climb its sides, hide behind it, drop out of it. Beside it, the ceiling is y = 0.
NOTCH_L, NOTCH_R, NOTCH_B = 31, 153, 21      # occluder x-range (inclusive) and bottom row, in art px
NOTCH_RECT = (NOTCH_L, 0, NOTCH_R, NOTCH_B)
SCALE = 6                # preview export scale
FPS = 12
CAM = (W // 2, 10)       # camera lens: inside the notch occluder (never visible; aim gags at the notch's underside)

PAL = {
    'k': (40, 36, 52),    'w': (245, 245, 240),  'b': (20, 20, 24),
    'g': (122, 199, 79),  'G': (78, 138, 46),    'y': (255, 213, 138),
    'o': (244, 162, 89),  'O': (196, 109, 43),   't': (160, 82, 45),
    's': (200, 200, 210), 'p': (170, 170, 190),  'P': (110, 110, 135),
    'r': (230, 80, 80),   'c': (120, 200, 230),  'n': (255, 160, 60),
    'S': (150, 150, 160),
}

def sprite(rows, pal=None):
    """ASCII rows -> RGBA image. Rows may have ragged length. pal: per-module colour overrides/additions."""
    p = {**PAL, **(pal or {})}
    rows = [r for r in rows.strip('\n').split('\n')]
    w = max(len(r) for r in rows); h = len(rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in p: px[x, y] = p[ch] + (255,)
    return im

def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)

class Clip:
    def __init__(self, name, seconds):
        self.name = name; self.n = int(seconds * FPS); self.frames = []
    def frame(self):
        im = Image.new('RGB', (W, H), (0, 0, 0)); self.frames.append(im); return im
    def blit(self, im, spr, x, y):
        im.paste(spr, (int(x), int(y)), spr)
    def export_strip(self, clipdir, bucket):
        """App format: one vertical PNG strip at LOGICAL resolution (W x H*n) + manifest entry."""
        import json
        os.makedirs(clipdir, exist_ok=True)
        strip = Image.new('RGB', (W, H * len(self.frames)), (0, 0, 0))
        for i, f in enumerate(self.frames): strip.paste(f, (0, i * H))
        strip.save(os.path.join(clipdir, f'{self.name}.png'), optimize=True)
        mpath = os.path.join(clipdir, 'manifest.json')
        man = json.load(open(mpath)) if os.path.exists(mpath) else []
        man = [m for m in man if m['name'] != self.name]
        man.append({'name': self.name, 'bucket': bucket, 'frames': len(self.frames), 'fps': FPS, 'w': W, 'h': H})
        json.dump(sorted(man, key=lambda m: m['name']), open(mpath, 'w'), indent=1)
        return os.path.join(clipdir, f'{self.name}.png')

    @staticmethod
    def with_notch(f):
        """Preview only: paint the hardware occluder (dark grey) + camera dot over a frame."""
        g = f.copy(); d = ImageDraw.Draw(g)
        d.rectangle(NOTCH_RECT, fill=(22, 22, 26)); d.point(CAM, fill=(70, 70, 80)); return g

    def export(self, outdir, preview=True):
        os.makedirs(outdir, exist_ok=True)
        fdir = os.path.join(outdir, f'{self.name}_frames'); os.makedirs(fdir, exist_ok=True)
        for i, f in enumerate(self.frames):
            self.with_notch(f).resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(fdir, f'{i:04d}.png'))
        mp4 = os.path.join(outdir, f'{self.name}.mp4')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, '%04d.png'),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', mp4], check=True)
        if preview:
            # contact sheet: every 6th frame, x3, with the camera hole ring for orientation
            picks = self.frames[::6]
            sheet = Image.new('RGB', (W * 3, H * 3 * len(picks) + 4 * len(picks)), (30, 30, 30))
            for i, f in enumerate(picks):
                sheet.paste(self.with_notch(f).resize((W * 3, H * 3), Image.NEAREST), (0, i * (H * 3 + 4)))
            sheet.save(os.path.join(outdir, f'{self.name}_sheet.png'))
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'fps=12,scale=720:-1:flags=neighbor',
                            os.path.join(outdir, f'{self.name}.gif')], check=True)
        return mp4

def ease(t):  # smoothstep
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


# ---------- detail helpers (secondary motion is what makes pixel clips feel alive) ----------
import math

def bob(i, period=12, amp=1):
    """Vertical offset for a breathing/idle bob: 0..amp..0 over `period` frames."""
    return round(amp * (0.5 - 0.5 * math.cos(2 * math.pi * (i % period) / period)))

def shadow(im, x, w, y=None, col=(28, 28, 34)):
    """1-px contact shadow under a grounded character; anchors it to the ledge."""
    y = H - 1 if y is None else int(y)
    for px in range(int(x), int(x + w)):
        if 0 <= px < W and 0 <= y < H and im.getpixel((px, y)) == (0, 0, 0): im.putpixel((px, y), col)

def dots(im, pts, col):
    """Plot a list of (x, y) pixels, clipped to the strip."""
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H: im.putpixel((int(x), int(y)), col)

def puff(im, x, y, t, col=(120, 120, 130)):
    """Dust puff at (x, y) for t in 0..1: four specks spread out and fade. Use on landings, skids, take-offs."""
    if not 0 <= t <= 1: return
    r = 1 + int(3 * t); c = tuple(int(v * (1 - t * 0.7)) for v in col)
    dots(im, [(x - r, y - r // 2), (x + r, y - r // 2), (x - r // 2, y - r), (x + r // 2, y - r)], c)

def burst(im, cx, cy, i, n=10, speed=1.6, life=14, cols=((255, 90, 90), (255, 220, 80), (90, 200, 255), (120, 255, 140))):
    """Radial particle burst (confetti / sparks) i frames after ignition; gravity pulls them down."""
    if not 0 <= i < life: return
    for k in range(n):
        a = 2 * math.pi * k / n; vx, vy = math.cos(a) * speed, math.sin(a) * speed - 1.2
        dots(im, [(cx + vx * i, cy + vy * i + 0.12 * i * i)], cols[k % len(cols)])

def tint(im, col, a):
    """Blend the whole frame toward `col` by a in 0..1 (night = (10, 20, 60), a≈0.5). Black stays black."""
    if a <= 0: return
    px = im.load()
    for y in range(H):
        for x in range(W):
            p = px[x, y]
            if p != (0, 0, 0): px[x, y] = tuple(int(p[k] * (1 - a) + col[k] * a) for k in range(3))

def hflip(spr): return spr.transpose(Image.FLIP_LEFT_RIGHT)


# ---------- detail helpers: shading ramps, rim outlines, part assembly ----------
def ramp(base, n=4):
    """Shading ramp from one base colour: [shadow, base, light, highlight] (pixel-art style: shadows go cooler)."""
    r, g, b = base
    sh = (int(r * 0.55), int(g * 0.55), min(255, int(b * 0.7) + 20))
    lt = (min(255, int(r * 1.18) + 10), min(255, int(g * 1.18) + 10), min(255, int(b * 1.1) + 10))
    hi = (min(255, int(r * 1.35) + 40), min(255, int(g * 1.35) + 40), min(255, int(b * 1.25) + 40))
    return [sh, base, lt, hi][:n]

def assemble(parts):
    """Compose [(sprite, dx, dy), ...] into one RGBA sprite (dx, dy may be negative). Outline AFTER assembling."""
    minx = min(dx for _, dx, _ in parts); miny = min(dy for _, _, dy in parts)
    maxx = max(dx + s.width for s, dx, _ in parts); maxy = max(dy + s.height for s, _, dy in parts)
    out = Image.new('RGBA', (maxx - minx, maxy - miny), (0, 0, 0, 0))
    for s, dx, dy in parts: out.paste(s, (dx - minx, dy - miny), s)
    return out, minx, miny

def outline(spr, col=(70, 66, 96)):
    """Add a 1-px rim around the opaque silhouette. A muted, slightly light colour reads against black; pure black would vanish."""
    w, h = spr.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); out.paste(spr, (1, 1), spr)
    src = out.load(); res = out.copy(); dst = res.load()
    for y in range(h + 2):
        for x in range(w + 2):
            if src[x, y][3] == 0 and any(0 <= x + dx < w + 2 and 0 <= y + dy < h + 2 and src[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                dst[x, y] = col + (255,)
    return res
