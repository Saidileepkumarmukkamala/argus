"""Rendered 3D frames -> app clips. Makes two variants from one render:
  NAME        smooth 3D at 552x156 (1 device px per render px on the notch)
  NAME + 'px' 3D-pixel look: downsampled to 184x52, quantised to a small palette (Donkey Kong Country style)
Usage: python3 tools3d/post.py NAME BUCKET FRAMES_DIR"""
import sys, os, json, glob, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, bucket, fdir = sys.argv[1], sys.argv[2], sys.argv[3]
frames = [Image.open(p).convert('RGB') for p in sorted(glob.glob(os.path.join(fdir, '*.png')))]
assert frames, 'no frames'
W, H = frames[0].size
def write(nm, frs, w, h):
    strip = Image.new('RGB', (w, h * len(frs)), (0, 0, 0))
    for i, f in enumerate(frs): strip.paste(f, (0, i * h))
    os.makedirs(os.path.join(ROOT, 'clips'), exist_ok=True)
    strip.save(os.path.join(ROOT, 'clips', f'{nm}.png'), optimize=True)
    mp = os.path.join(ROOT, 'clips', 'manifest.json')
    man = json.load(open(mp)) if os.path.exists(mp) else []
    man = [m for m in man if m['name'] != nm]
    man.append({'name': nm, 'bucket': bucket, 'frames': len(frs), 'fps': 12, 'w': w, 'h': h})
    json.dump(sorted(man, key=lambda m: m['name']), open(mp, 'w'), indent=1)
    # preview gif at 2x
    out = os.path.join(ROOT, 'test', 'out'); os.makedirs(out, exist_ok=True)
    big = [f.resize((552 * 2 // (552 // w), 156 * 2 // (156 // h)), Image.NEAREST) for f in frs]
    big[0].save(os.path.join(out, f'{nm}.gif'), save_all=True, append_images=big[1:], duration=1000 // 12, loop=0)
    # contact sheet
    picks = frs[::6]; sheet = Image.new('RGB', (552, (156 + 4) * len(picks)), (30, 30, 30))
    for i, f in enumerate(picks): sheet.paste(f.resize((552, 156), Image.NEAREST), (0, i * 160))
    sheet.save(os.path.join(out, f'{nm}_sheet.png'))
    return os.path.getsize(os.path.join(ROOT, 'clips', f'{nm}.png'))
s1 = write(name, frames, W, H)
px = [f.resize((184, 52), Image.BOX).quantize(colors=48, dither=Image.Dither.NONE).convert('RGB') for f in frames]
s2 = write(name + 'px', px, 184, 52)
print(f'{name}: {len(frames)} frames, smooth {s1//1024} KB, pixel {s2//1024} KB')
