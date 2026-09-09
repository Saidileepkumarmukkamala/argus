"""Render every clip module in tools/clips_lib/ into clips/ (app format) + test/out/ (previews).
Usage: python3 tools/render.py            # all
       python3 tools/render.py NAME       # one module, previews only, no manifest touch (safe in parallel)
"""
import sys, os, importlib.util, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    paths = sorted(glob.glob(os.path.join(HERE, 'clips_lib', '*.py')))
    if only: paths = [p for p in paths if os.path.basename(p)[:-3] == only]
    bad = []
    for p in paths:
        try:
            m = load(p); clip = m.build()
            assert clip.name == os.path.basename(p)[:-3], f"clip name {clip.name} != module {p}"
            assert not clip.frames[0].getbbox() and not clip.frames[-1].getbbox(), "first/last frame must be empty"
            clip.export(os.path.join(ROOT, 'test', 'out'))
            if not only: clip.export_strip(os.path.join(ROOT, 'clips'), m.BUCKET)
            print(clip.name, len(clip.frames), 'frames', f'{len(clip.frames)/12:.1f}s')
        except Exception as e:
            bad.append(os.path.basename(p)); print('FAILED', os.path.basename(p), type(e).__name__, e)
            if only: raise
    if bad: print('BROKEN:', ', '.join(bad))
