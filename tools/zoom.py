"""Zoom a rendered frame for inspection: python3 tools/zoom.py NAME FRAME [FRAME ...] -> test/out/NAME_zoom.png
Crops each frame to its non-black content (+margin), scales x8, stacks vertically."""
import sys, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, idxs = sys.argv[1], [int(a) for a in sys.argv[2:]] or [0]
tiles = []
for i in idxs:
    f = Image.open(os.path.join(ROOT, 'test', 'out', f'{name}_frames', f'{i:04d}.png')).convert('RGB')
    bb = f.point(lambda v: 255 if v > 8 else 0).convert('L').getbbox() or (0, 0, f.width, f.height)
    m = 30; box = (max(0, bb[0]-m), 0, min(f.width, bb[2]+m), f.height)
    c = f.crop(box); tiles.append(c.resize((c.width * 2, c.height * 2), Image.NEAREST))
W = max(t.width for t in tiles); H = sum(t.height for t in tiles) + 6 * len(tiles)
out = Image.new('RGB', (W, H), (40, 40, 40)); y = 0
for t in tiles: out.paste(t, (0, y)); y += t.height + 6
p = os.path.join(ROOT, 'test', 'out', f'{name}_zoom.png'); out.save(p); print(p, out.size)
