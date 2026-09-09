# Ledge

Tiny animated visitors for the MacBook notch. A free macOS menu-bar app: every few minutes an animated character
drops by the notch; click the notch for another. Silent, offline, ~10 MB.

- `app/` — the AppKit shell (`Ledge.swift`, ~200 lines). `./build.sh --dist` builds, bundles `clips/`, ad-hoc signs, zips.
- `clips/` — the library the app plays: one PNG strip per clip (all frames stacked) + `manifest.json`.
- `tools/lottie2clip.py` — turns a Lottie JSON into a clip (`--height`, `--motion cross|center|left|right|cross-rl`, `--drop` background layers).
- `tools/vec.py` — vector stage for composed scenes; `tools/sprite.py` — the earlier pixel engine (retired from rotation).
- `lottie/` — source animations (LottieFiles community, Lottie Simple License).
- `docs/` — the landing page (GitHub Pages).

Build: `cd app && ./build.sh --dist`. Requires Xcode command line tools, Python 3 with Pillow and rlottie-python, ffmpeg.
