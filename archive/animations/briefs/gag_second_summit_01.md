### 3. Second Summit — gag — 10 s — A4 D4 (8) — `climbers-1`, merged with `occluder-1` Summit
**Premise.** A climber tops out on the ledge, plants a flag, looks up for the sky and finds the notch underside two pixels above his hat. So he keeps climbing.
**Characters.** One mountaineer 18 px: knit hat with bobble, mittens, ice axe, rope, two plain-colour pennant flags in the pack.
**Beats.** (Summit's rope-and-axe opening grafted on; Second Summit's epilogue shortened; 11.5 s -> 10 s.)
- 0-1 s: empty. A rope end flicks up over the ledge at x~92 and slides back; second flick; an ice axe hooks the edge with a 1 px chip.
- 1-2.5 s: two mitts, then the bobble, then squinting eyes. Heave: squash on the pull, stretch on the pop, mantle, dust puff. Wobble-settle; bobble sways three frames after he stops.
- 2.5-4 s: pulls flag one, stabs it into the ledge at his feet (two-frame sink, wobble), arms up, flag flutters (two-frame swap).
- 4-5 s: looks up. Underside is right above him. Head tilt. Bobble flops over.
- 5-7.5 s: shoulders drop, breath puff. Walks right to x~150, chalks hands (white puff), climbs the side wall x=154 hand over hand, y 21 -> 0, rope trailing.
- 7.5-8.5 s: at the ceiling hammers a piton (three taps, spark pixels), hangs, plants flag two INTO the ceiling pointing down. It flutters upside down.
- 8.5-10 s: abseils: two bounces off the wall, past the ledge, gone. Piton pops (spark), inverted flag falls past the ledge. Ledge flag tips and slides off. Empty.
**Twist.** The summit has a ceiling, so he plants the flag on the sky.
**Geometry.** Ledge (hands-first climb-in, abseil exit), notch side wall x=154 (second climb), ceiling y=0 in the right side area (piton, inverted flag).
**Build.** Mountaineer = body + head + two arm sprites (reach/pull). Wall climb = two-frame alternation with eased y. Rope = 1 px line from anchor to hips with a sag function. Flags = two-frame flutter, one drawn inverted. Snow/dust/sparks from the particle helper.
