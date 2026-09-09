"""Render vector clip modules in tools/vclips/. Usage: python3 tools/vrender.py [NAME]  (no NAME = all, writes manifest)"""
import sys, os, glob, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
only = sys.argv[1] if len(sys.argv) > 1 else None
for p in sorted(glob.glob(os.path.join(HERE, 'vclips', '*.py'))):
    name = os.path.basename(p)[:-3]
    if only and name != only: continue
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    clip = m.build(); assert clip.name == name
    clip.export(os.path.join(ROOT, 'test', 'out'))
    if not only: clip.export_strip(os.path.join(ROOT, 'clips'), m.BUCKET)
    print(name, len(clip.frames), 'frames', f'{len(clip.frames)/24:.1f}s')
