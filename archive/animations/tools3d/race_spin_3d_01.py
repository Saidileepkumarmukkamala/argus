"""Proof clip: an original red race car ("Rocket": headlight eyes, boxy hot-rod body, big spoiler) tears in, brakes under the
notch, spins a full 360, settles, and drives off. A calm blue car passes in the background lane. 5 s.
Run: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools3d/race_spin_3d_01.py -- <outdir>"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notch_scene import *

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '/tmp/race_frames'
N = 60

def car(name, paint, stripe=True, spoiler=True):
    root = empty(name)
    body_m = material(f'{name}_paint', paint, rough=0.3, spec=0.6)
    dark = material(f'{name}_dark', (0.05, 0.05, 0.06), rough=0.7)
    glass = material(f'{name}_glass', (0.15, 0.22, 0.32), rough=0.15, metal=0.2)
    chrome = material(f'{name}_chrome', (0.8, 0.8, 0.85), rough=0.25, metal=0.9)
    white = material(f'{name}_white', (0.96, 0.96, 0.94), rough=0.5)
    black = material(f'{name}_black', (0.02, 0.02, 0.03), rough=0.6)
    tyre = material(f'{name}_tyre', (0.06, 0.06, 0.07), rough=0.9)
    rounded_box('body', (30, 14, 8), (0, 0, 8), body_m, bevel=2.5, parent=root)
    rounded_box('cabin', (14, 12, 7), (-3, 0, 14.5), glass, bevel=2.2, parent=root)
    rounded_box('roof', (12, 11, 1.6), (-3, 0, 18.4), body_m, bevel=0.6, parent=root)
    rounded_box('grille', (1.2, 8, 3), (15.2, 0, 6.5), dark, bevel=0.4, parent=root, smooth=False)
    # grin: a thin dark bar with upturned corners, sitting on the bumper under the eyes
    rounded_box('mouth', (0.8, 7, 1.0), (15.4, 0, 8.4), black, bevel=0.3, parent=root, smooth=False)
    for y in (-3.8, 3.8): rounded_box(f'grin{y}', (0.8, 1.0, 1.6), (15.4, y, 9.0), black, bevel=0.3, parent=root, smooth=False)
    if stripe: rounded_box('stripe', (28, 3, 0.6), (0, 0, 12.2), white, bevel=0.2, parent=root, smooth=False)
    if spoiler:
        rounded_box('wing', (4, 18, 1.2), (-15, 0, 17), body_m, bevel=0.5, parent=root, smooth=False)
        for y in (-5, 5): rounded_box(f'strut{y}', (1, 1, 5), (-14, y, 13), dark, bevel=0.2, parent=root, smooth=False)
    # headlight eyes: white sphere + pupil, sitting in the front corners
    for y in (-4.6, 4.6):
        sphere(f'eye{y}', 2.4, (14.2, y, 10.2), white, parent=root)
        sphere(f'pupil{y}', 1.1, (16.1, y * 0.9, 10.4), black, parent=root)
        sphere(f'glint{y}', 0.4, (16.7, y * 0.9 - 0.5, 11.1), white, parent=root)
    wheels = []
    for x in (9.5, -9.5):
        for y in (-6.5, 6.5):
            w = cylinder(f'wheel{x}{y}', 4.6, 3.2, (x, y, 4.6), (math.radians(90), 0, 0), tyre, parent=root)
            hub = cylinder(f'hub{x}{y}', 2.6, 3.4, (x, y, 4.6), (math.radians(90), 0, 0), chrome, parent=root)
            hub.parent = w; hub.location = (0, 0, 0); hub.rotation_euler = (0, 0, 0)
            wheels.append(w)
    root.scale = (1.6, 1.6, 1.6)
    return root, wheels

sc = reset(); camera(); lights()
A, A_wheels = car('rocket', (0.85, 0.08, 0.06))
B, B_wheels = car('calm', (0.12, 0.35, 0.85), stripe=False, spoiler=False)

def place(root, wheels, x, y, yaw=0.0, pitch=0.0, roll=0.0, dist=0.0, bounce=0.0):
    root.location = (x, y, bounce)
    root.rotation_euler = (math.radians(roll), math.radians(pitch), math.radians(yaw))
    for w in wheels: w.rotation_euler = (math.radians(90), 0, 0); w.rotation_euler.rotate_axis('Z', -dist / 4.6)

def step(i):
    # Rocket: in fast, brake, 360 spin, settle, leave
    if i < 27: t = i / 26; x = -150 + 170 * (1 - (1 - t) ** 2); pitch = 0; yaw = 0; roll = 0; b = 0
    elif i < 33: t = (i - 27) / 6; x = 20 + 6 * t; pitch = -9 * math.sin(math.pi * t); yaw = 0; roll = 0; b = 0
    elif i < 48: t = ease((i - 33) / 15); x = 26 + 22 * t; yaw = 360 * t; pitch = 0; roll = 7 * math.sin(math.pi * t); b = 0
    elif i < 53: t = (i - 48) / 5; x = 48; yaw = 360; pitch = 0; roll = 0; b = abs(math.sin(math.pi * t)) * 1.5
    else: t = (i - 53) / 7; x = 48 + 115 * t * t; yaw = 360; pitch = 2; roll = 0; b = 0
    place(A, A_wheels, x, 0, yaw, pitch, roll, dist=x, bounce=b)
    # Calm: steady in the background lane
    xb = -150 + (i - 6) * 7.0 if 6 <= i < 50 else 400
    place(B, B_wheels, xb, 34, 0, 0, 0, dist=xb)

render_frames(OUT, N, step)
print('rendered', N, 'frames to', OUT)
