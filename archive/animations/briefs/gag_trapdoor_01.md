### 6. Trapdoor — gag — 9 s — A4 D4 (8) — `hangers-3`
**Premise.** A hatch opens in the underside, a rope ladder unrolls, something climbs down to look at the world. It regrets it immediately.
**Characters.** Cellar gremlin 15 px, hood with floppy ear-flaps, huge eyes, a lantern; rope ladder.
**Beats.**
- 0-1 s: a 10 px square in the underside at x~85 shudders, dust falls, swings open on a 3-frame hinge.
- 1-2.5 s: ladder unrolls: two rails and rungs extend to the floor, overshoot, bounce, settle.
- 2.5-5 s: gremlin climbs down rung by rung, lantern pendulum out of phase with the body, hood flaps bobbing. Reaches the floor, looks left, right, at the viewer.
- 5-6 s: freeze. Eyes go to full size. Lantern flickers out (tint drop).
- 6-7.5 s: scrambles back up at triple speed with ghost frames, misses a rung (one leg swings free), hauls the ladder up hand over hand, hatch slams with a dust shower from the underside.
- 7.5-9 s: silence. Hatch cracks open 1 px. One eye in the gap looks left, right, at the viewer. Closes. Empty.
**Twist.** The monster under the notch is scared of you. The eye in the crack is the button.
**Geometry.** Underside as a door into behind; floor as the visited world.
**Build.** Hatch = 3-frame hinge against the underside line (shared with Cuckoo doors, reused by Fire Drill). Ladder = rails + rung-count value + bounce ease. Lantern = 3 offset states cycled slower than the walk. Speed-up = frame skipping + ghost copy. Lantern light = tint swap on nearby pixels.
