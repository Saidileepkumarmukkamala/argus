"""Smooth vector-cartoon engine for notch clips. Anti-aliased shapes at full Retina resolution, 24 fps.
Canvas 552 x 156 device px = the 276 x 78 pt body of the open notch shape (same aspect as the 184 x 52 pixel canvas,
so the app scales either to fill). Shapes are drawn 3x oversampled and downsampled with Lanczos for clean edges.
Coordinates are device px, origin top-left. The hardware notch occludes NOTCH; its underside is y = NOTCH[3]."""
import math, os, json, subprocess
from PIL import Image, ImageDraw

VW, VH = 552, 156
SS = 3
FPS = 24
NOTCH = (93, 0, 459, 63)                 # occluder in device px (art 31..153, 0..21 at 3x)
NOTCH_B = NOTCH[3]; FLOOR = VH - 1

# ---------- easing ----------
def clamp(t): return max(0.0, min(1.0, t))
def ease_in_out(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def ease_out_back(t, s=1.7): t = clamp(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
def ease_out_bounce(t):
    t = clamp(t); n, d = 7.5625, 2.75
    if t < 1 / d: return n * t * t
    if t < 2 / d: t -= 1.5 / d; return n * t * t + 0.75
    if t < 2.5 / d: t -= 2.25 / d; return n * t * t + 0.9375
    t -= 2.625 / d; return n * t * t + 0.984375
def lerp(a, b, t): return a + (b - a) * t
def seg(i, a, b): """0..1 progress of frame i inside [a, b) frames."""; return clamp((i - a) / max(1, b - a))

# ---------- geometry ----------
def rot(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
def ellipse_pts(cx, cy, rx, ry, ang=0.0, n=64):
    pts = [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return rot(pts, cx, cy, ang) if ang else pts
def shade(col, k):
    """Lighten (k>1) or darken (k<1) a colour."""
    return tuple(max(0, min(255, int(c * k))) for c in col)

class Scene:
    def __init__(self):
        self.im = Image.new('RGB', (VW * SS, VH * SS), (0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def _s(self, pts): return [(x * SS, y * SS) for x, y in pts]
    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self._s(pts), fill=fill, outline=outline, width=int(width * SS) if outline else 0)
    def ellipse(self, cx, cy, rx, ry, fill, outline=None, width=0, ang=0.0):
        self.poly(ellipse_pts(cx, cy, rx, ry, ang), fill, outline, width)
    def circle(self, cx, cy, r, fill, outline=None, width=0): self.ellipse(cx, cy, r, r, fill, outline, width)
    def line(self, pts, fill, width=2, joint='curve'):
        self.d.line(self._s(pts), fill=fill, width=max(1, int(width * SS)), joint=joint)
    def rrect(self, x0, y0, x1, y1, r, fill, outline=None, width=0):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill, outline=outline, width=int(width * SS) if outline else 0)
    def blob(self, cx, cy, rx, ry, fill, ang=0.0, rim=None, rim_w=2.5, light=None):
        """A shaded body: rim outline, base fill, soft highlight ellipse top-left."""
        if rim: self.ellipse(cx, cy, rx + rim_w, ry + rim_w, rim, ang=ang)
        self.ellipse(cx, cy, rx, ry, fill, ang=ang)
        if light: self.ellipse(cx - rx * 0.3, cy - ry * 0.35, rx * 0.45, ry * 0.3, light, ang=ang)
    def finish(self): return self.im.resize((VW, VH), Image.LANCZOS)

class VClip:
    def __init__(self, name, seconds):
        self.name = name; self.n = int(round(seconds * FPS)); self.frames = []
    def scene(self): return Scene()
    def add(self, sc): self.frames.append(sc.finish())
    def export(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        fdir = os.path.join(outdir, f'{self.name}_frames'); os.makedirs(fdir, exist_ok=True)
        for i, f in enumerate(self.frames):
            g = f.copy(); ImageDraw.Draw(g).rectangle(NOTCH, fill=(20, 20, 24)); g.save(os.path.join(fdir, f'{i:04d}.png'))
        mp4 = os.path.join(outdir, f'{self.name}.mp4')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, '%04d.png'),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', mp4], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'fps=12,scale=552:-1:flags=lanczos', os.path.join(outdir, f'{self.name}.gif')], check=True)
        picks = self.frames[::FPS // 2]     # every half second
        sheet = Image.new('RGB', (VW, (VH + 4) * len(picks)), (30, 30, 30))
        for k, f in enumerate(picks):
            g = f.copy(); ImageDraw.Draw(g).rectangle(NOTCH, fill=(20, 20, 24)); sheet.paste(g, (0, k * (VH + 4)))
        sheet.save(os.path.join(outdir, f'{self.name}_sheet.png'))
        return mp4
    def export_strip(self, clipdir, bucket):
        os.makedirs(clipdir, exist_ok=True)
        strip = Image.new('RGB', (VW, VH * len(self.frames)), (0, 0, 0))
        for i, f in enumerate(self.frames): strip.paste(f, (0, i * VH))
        strip.save(os.path.join(clipdir, f'{self.name}.png'), optimize=True)
        mpath = os.path.join(clipdir, 'manifest.json')
        man = json.load(open(mpath)) if os.path.exists(mpath) else []
        man = [m for m in man if m['name'] != self.name]
        man.append({'name': self.name, 'bucket': bucket, 'frames': len(self.frames), 'fps': FPS, 'w': VW, 'h': VH})
        json.dump(sorted(man, key=lambda m: m['name']), open(mpath, 'w'), indent=1)
