### 1. Cuckoo — gag — 8 s — A5 D5 (10) — `occluder-10`
**Premise.** There is a cuckoo-clock door in the underside of the notch. Third time out, the spring keeps going.
**Characters.** Cuckoo bird 14 px with crest; two 6x8 door panels; a spring drawn as a parametric zigzag.
**Beats.**
- 0-1 s: empty. Two door panels on the underside at x~92 swing open (two frames each, 1 px dust at the hinges).
- 1-2 s: cuckoo pops out downward on an 8 px spring, beak opens twice (silent call, chest puffs), retracts; doors shut with a settle.
- 2-3 s: pause. Doors open again; pop, two beak-opens, retract.
- 3-5 s: third time the spring keeps extending: 8, 16, 24 px; eyes widen on the way down, wings flap uselessly; squashes onto the floor at y=51, coils piling behind it.
- 5-6.5 s: stands, straightens feathers (crest flick), looks up its own spring, looks at the user, shrugs.
- 6.5-8 s: spring recoils: stretch frame, bird yanked up through the door, doors bang shut, one bounces back open and hangs crooked. One feather drifts down in a falling-leaf sway, lands, rolls off the ledge. Crooked door swings shut. Empty.
**Twist.** The notch is a clock with a worn spring; the bird gets one moment on the ground and is snatched straight back.
**Geometry.** Underside (the door), behind (the bird lives inside the hardware), floor and ledge (landing, feather exit).
**Build.** Spring = zigzag polyline from a length parameter. Squash/stretch on landing and recoil. Feather = sway particle. Doors = two hinged sprites, 3-frame swing. One character; cheapest of the strong ideas.
