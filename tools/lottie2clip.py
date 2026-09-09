"""Turn a Lottie animation into a notch clip. Renders with rlottie at Retina res, composites on black, loops the
animation while moving it (or holding it centre), writes the app strip + manifest + previews.
Usage: python3 tools/lottie2clip.py NAME SRC.json [--seconds 6] [--height 120] [--motion cross|center|cross-rl] [--bucket gag] [--y 0]"""
import sys, os, argparse, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vec import VClip, VW, VH, FPS, ease_in_out
from rlottie_python import LottieAnimation
from PIL import Image

ap = argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('src'); ap.add_argument('--seconds', type=float, default=6)
ap.add_argument('--height', type=int, default=120); ap.add_argument('--motion', default='cross'); ap.add_argument('--bucket', default='gag'); ap.add_argument('--y', type=int, default=0)
ap.add_argument('--speed', type=float, default=1.0)
ap.add_argument('--drop', default='', help='comma-separated substrings; layers whose name contains one are removed (backgrounds)')
a = ap.parse_args()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import json, tempfile
doc = json.load(open(a.src))
if a.drop:
    keys = [k.lower() for k in a.drop.split(',') if k]
    def keep(l): return not any(k in (l.get('nm') or '').lower() for k in keys)
    doc['layers'] = [l for l in doc.get('layers', []) if keep(l)]
    for asset in doc.get('assets', []):
        if 'layers' in asset: asset['layers'] = [l for l in asset['layers'] if keep(l)]
tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(doc, tmp); tmp.close()
an = LottieAnimation.from_data(open(tmp.name).read())
sw, sh = an.lottie_animation_get_size(); total = an.lottie_animation_get_totalframe(); lfps = an.lottie_animation_get_framerate()
# auto-crop: union alpha bbox over the animation, rendered at native size
bb = None
for k in range(0, total, max(1, total // 12)):
    fr0 = an.render_pillow_frame(frame_num=k, width=sw, height=sh).convert('RGBA')
    b = fr0.getchannel('A').getbbox()
    if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
bb = bb or (0, 0, sw, sh)
cw, ch = bb[2] - bb[0], bb[3] - bb[1]
H = a.height; W = int(round(cw * H / ch)); S = H / ch
RW, RH = int(round(sw * S)), int(round(sh * S))          # render whole comp at this scale, then crop to the bbox
crop = tuple(int(round(v * S)) for v in bb)
clip = VClip(a.name, a.seconds)
for i in range(clip.n):
    t = i / FPS * a.speed
    lf = int((t * lfps) % total)
    spr = an.render_pillow_frame(frame_num=lf, width=RW, height=RH).convert('RGBA').crop(crop)
    fr = Image.new('RGB', (VW, VH), (0, 0, 0))
    u = i / max(1, clip.n - 1)
    if a.motion == 'cross':     x = -W + (VW + W) * u
    elif a.motion == 'cross-rl': x = VW - (VW + W) * u
    elif a.motion == 'left':    x = 52
    elif a.motion == 'right':   x = VW - W - 52
    else:                       x = (VW - W) / 2
    y = VH - H + a.y
    if i == 0 or i == clip.n - 1: fr = Image.new('RGB', (VW, VH), (0, 0, 0))        # empty first/last frame
    else: fr.paste(spr, (int(x), int(y)), spr)
    clip.frames.append(fr)
an.lottie_animation_destroy()
clip.export(os.path.join(ROOT, 'test', 'out'))
print(clip.export_strip(os.path.join(ROOT, 'clips'), a.bucket), clip.n, 'frames')
