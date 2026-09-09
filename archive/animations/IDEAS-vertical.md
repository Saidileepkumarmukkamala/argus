# Notch Parade — vertical clips (climb up / hang down)

Editor's cut of 30 pitches, two judges each (audience A, director D, max 5 each).
Canvas 184x52. Hardware notch covers x 31..153, y 0..21. Underside y=21. Side walls x=30/31 and 153/154. Ceiling y=0 in the side areas. Ledge y=51. Bottom corners rounded ~16 px.

Selection rules applied on top of the scores:
- One idea per premise. Two mountaineers, two trapdoor-ladders, two bat rows, two hydration drips were in the top tier; each pair keeps one, the other goes to the bench with a "reuse the assets" note.
- No third cat. Threadbare is recast as a ferret; nothing else changes.
- Clips over 10 s were trimmed unless every beat earns its time. Trims are written into the beats below, not left as notes.
- Bucket mix: 7 gag, 2 gesture, 1 idle. The owner asked for funny; the gestures and the idle are there so the parade is not one-note.

Shared assets, build once:
- **Ledge climb, 4 poses** (hands/claws, head, heave, land+squash): Worm on a String, Second Summit, Threadbare, One Drop, Dead Hang.
- **Thread/rope with a length value** (1 px vertical): Worm on a String, Threadbare, Trapdoor ladder rails.
- **Underside hatch, 3-frame hinge**: Cuckoo (as two door panels), Trapdoor, later Fire Drill.
- **Bat sprite with 3 tilt frames**: Newton's Roost, later Lights Out.
- Particle helper: dust, feathers, stars, drips, sparks. Squash/stretch helper. Tint helper.

Suggested build order: Cuckoo, Worm on a String (lands the ledge-climb asset), Newton's Roost, One Drop, then the rest.

---

## 1. Top 10 vertical clips

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

### 2. Worm on a String — gag — 10 s — A4 D5 (9) — `hangers-1`
**Premise.** The notch is fishing the desktop. A baited hook lowers from the underside; a bird climbs over the ledge for it and becomes the catch.
**Characters.** Stubby round bird 16 px, one big eye, orange feet; worm on a hook 5 px with two eye pixels; unseen angler inside the notch.
**Beats.**
- 0-1.5 s: thread lowers from the underside at x~100 with hook and wriggling worm (2-frame wiggle). Stops 7 px above the floor, sways, settles.
- 1.5-3 s: two claws hook the ledge at x~125, head pops up, eye locked on the worm, heave onto the floor, bounce and dust puff.
- 3-4.5 s: bird tiptoes toward the worm, high steps, head bob. Worm notices, stops wriggling, eyes go wide.
- 4.5-5.5 s: peck-grab. Thread yanks up in one jerk: bird lifted by the beak, feet pedaling, wings flapping, stops just under y=21, dangling and slowly spinning (mirror flip every 0.4 s). Eye finds the viewer.
- 5.5-7.5 s: worm stretches between hook and beak (5 -> 9 px), snaps free. Bird drops, lands flat in a wide squash, three feathers drift, dizzy blink. Thread whips up into the notch.
- 7.5-9 s: beat. Thread lowers again with a bigger, smug worm (8 px). Bird looks at worm, at viewer, at worm.
- 9-10 s: bird turns, marches to the ledge, climbs back down feet last. Worm reels up. Empty.
**Twist.** The catch escapes and the bait comes back bigger. The notch is patient.
**Geometry.** Underside as rod tip, ledge as the world the bird climbs from and back into, behind as the angler nobody sees.
**Build.** Thread = vertical line with a length value. Hook+worm = tiny sprite with a stretch scale. Bird = body + head + 2 wing states + feet. Ledge climb = the shared 4-pose sequence. Lift = ease-out over 6 frames; spin = alternate mirrored sprite. No rotation.

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

### 4. Threadbare — gag — 10 s — A5 D3 (8) — `climbers-3`, recast
**Premise.** A ferret climbs up to hunt a spider dangling from the notch. The spider hides inside the notch, comes back down behind the ferret, and the startled jump meets a ceiling two pixels away.
**Characters.** Ferret 16 px long, mask markings, long tail, whole-body wiggle; spider 4 px with two leg frames on a 1 px thread. (Was a cat; cats are already twice in the done list. Nothing in the beats depends on the species.)
**Beats.**
- 0-1.5 s: paws hook the ledge at x~40, ears, eyes, then the mantle: squash on the pull, stretch on the pop, dust puff. Tail whips up and settles over four frames.
- 1.5-3 s: ferret lopes right under the notch to x~95. Spider descends from the underside on a thread to y~30 and dangles, legs wiggling.
- 3-5 s: ferret sits, pupils dilate (frame swap), rear-end wiggle, tail tip ticks. Pounce: a paw bats and the spider zips up into the underside (gone at y=21), thread retracting.
- 5-6.5 s: ferret stares at the spot. Head tilt left, right. Ears back.
- 6.5-7.5 s: thread reappears 20 px to the right; spider descends silently behind the ferret's head and taps its ear with one leg.
- 7.5-8.5 s: ferret launches straight up (extreme stretch), bonks the underside: three star pixels at y=22, fur puff; lands in a full squash, legs splayed.
- 8.5-10 s: slides off the ledge tail-last; tail hooks the edge for two frames and lets go. Spider swings gently, reels up into the notch. Empty.
**Twist.** The spider returns where the ferret isn't looking, and the low ceiling turns the jump into the punchline.
**Geometry.** Ledge (climb-in, slide-off), underside (thread anchor, the bonk), behind (spider hides in the block).
**Build.** Ferret = body + head + tail, tail with its own four-frame lag; two head variants for ear position. Spider two-frame. Thread = shared length-value line. Stars and fur from the particle helper.

### 5. One Drop — gesture (drink water) — 8.5 s — A4 D4 (8) — `climbers-6`
**Premise.** A parched gecko crawls over the ledge. One bead of water forms on the underside and falls into its mouth; colour floods back. It leaves the second drop for you.
**Characters.** Desert gecko 14 px long, crest, curling tail, splayed toe pads; tinted dusty at first.
**Beats.**
- 0-2 s: toe pads grip the ledge at x~70; hauls up slowly, belly dragging, tongue out, three heat-shimmer pixels. Collapses flat; tail lands last.
- 2-3.5 s: a water bead forms on the underside at x~90, y=22: grows over four frames, stretches to a teardrop, sways once.
- 3.5-4.5 s: eye opens and tracks the bead. Pushes up onto front legs.
- 4.5-5.5 s: bead falls, mouth opens, splash of four droplets and one ring. Tint sweeps dusty -> bright green head to tail over three frames; crest stands, tail curls, eyes go shiny.
- 5.5-7 s: second bead forms. Gecko looks at it, turns to the user, looks back. Holds. Blink.
- 7-8.5 s: leaves the second bead, walks right with a springy tail wave, slips over the ledge. Bead falls onto the empty ledge with a ring. Empty.
**Twist.** It saves the second drop for you.
**Geometry.** Ledge (crawl-in, exit over the edge), underside (drip source).
**Build.** Gecko = body + head + tail + two leg frames. Per-column tint sweep over three frames. Bead = four grow frames + eased fall. Splash from the particle helper.

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

### 7. Newton's Roost — gag — 9 s — A5 D3 (8) — `hangers-2`
**Premise.** Five bats asleep under the notch. One wakes, falls, flaps back up too hard and bumps the row; the impulse travels through the sleepers like a Newton's cradle and only the far bat swings.
**Characters.** Five bats 14 px, folded wings, ears, one eye each; the far-right one slightly larger.
**Beats.**
- 0-1.5 s: five bats hang from y=21 between x~50 and x~130, wings folded, 1 px breathing squash on staggered phases, random ear twitches.
- 1.5-3 s: leftmost opens its eye, looks at the viewer, yawns (3 mouth frames), stretches one wing which clips its neighbour's ear; the ear flicks.
- 3-4.5 s: lets go to stretch both wings, drops 6 px, panics (eye wide), flaps up hard with two motion streaks, overshoots sideways and thumps into bat 2.
- 4.5-6.5 s: bats 2-4 do not move. Far-right bat swings out ~40 degrees on its feet hinge (3 tilt frames), dust motes shake off the underside, swings back and the impulse returns: bat 1 swings out left, back, two damped cycles. Ears lag one frame behind bodies.
- 6.5-8 s: cradle stops. Big bat slowly opens one eye and looks down the row. Bat 1 tucks its wings, faces forward, cheeks puffed in an innocent whistle pose.
- 8-9 s: eyes close in sequence, then one by one they drop and flap up into the notch. Last one's ear twitches, then goes. Empty.
**Twist.** Only the end bats move; the middle three sleep through it.
**Geometry.** Underside as the roost bar; behind as the exit. (Director docked it for being the obvious hanger; kept because the audience read is instant and the middle-three economy makes five characters cost like two.)
**Build.** Bat = body + head + 2 wings + 2 ears; hanging pose = standing sprite flipped. Swing = 3 pre-drawn tilt frames pivoted at the feet, sine easing. Impulse chain is scripted timing, no physics. Bat sprite reused by Lights Out later.

### 8. Going Up — gag — 10.5 s — A3 D4 (7) — `occluder-3`, trimmed
**Premise.** The notch is an elevator shaft. A queue waits below it; the cabin arrives already occupied.
**Characters.** Two commuters (tall-thin 20 px; tiny-with-hat 14 px) and a bear 26 px, asleep. (Was three commuters at 12 s; the round one is cut, the hat callback stays.)
**Beats.**
- 0-1.5 s: two commuters walk in from the left along the floor and queue under the notch at x~80/95, idle bobs at different rates; the tiny one keeps rising on tiptoe to look up.
- 1.5-3 s: a lit slit opens in the underside at x~120; two cables drop and a cabin (outlined box, lit interior) descends to the floor, ease-out, 2-frame overshoot. The queue straightens.
- 3-4.5 s: doors slide open: a bear fills the cabin, asleep, belly rising 1 px, one bubble at the nose. Both lean back in unison.
- 4.5-5.5 s: doors close; cabin rises into the underside; slit goes dark. Tall one looks down at tiny one; tiny one shrugs.
- 5.5-7.5 s: cabin returns empty, cables swaying; they file in (1 px squash each); the tiny one turns and looks at the user before the doors close.
- 7.5-8.5 s: cabin rises, slit dark. Empty floor for one full second.
- 8.5-10.5 s: cabin comes down once more, doors open: the bear, still asleep, wearing the tiny one's hat. Doors close, cabin rises. Empty.
**Twist.** The bear is a regular, and somewhere up in the notch it acquired a hat.
**Geometry.** Underside (shaft slit, cabin docks against it); behind (cabin and everyone in it vanish upward into the hardware). Strongest "the notch is a building" sell in the set.
**Build.** Cabin = rectangle + two sliding door sprites; cables = 1 px lines with sine sway; three sprites, no crowd.

### 9. Cocoon — idle — 10 s — A3 D4 (7) — `occluder-6`
**Premise.** A caterpillar crawls along the ceiling into one side of the notch and, after a quiet wait, a butterfly comes out the other side.
**Characters.** Caterpillar 14 px long, six segments, wave gait, two antennae; butterfly 16 px wingspan, three wing frames.
**Beats.**
- 0-3 s: caterpillar inches in upside down along the ceiling y=0 from the left edge; segments ripple back to front, head bobs, antennae twitch. Reaches the left side wall at x=30.
- 3-4 s: pauses; antennae feel the wall; bends and inches straight into it, disappearing segment by segment.
- 4-6.5 s: nothing. Then three soft 1 px dust puffs from the right side wall at y~10, 0.7 s apart, like knocks from inside.
- 6.5-9 s: from the right wall a butterfly emerges wing-first, crumpled, unfurls over three frames, clings, opens and closes twice slowly, drops, catches air, flutters an ease-in-out figure-eight and exits top-right.
- 9-10 s: a tiny cocoon husk drops out of the underside at x~150, tumbles two frames, bounces on the floor, rolls off the ledge. Empty.
**Twist.** The notch is a chrysalis; the husk falling out is the proof.
**Geometry.** Ceiling (crawl), both side walls (in one, out the other), behind (transformation), underside and ledge (husk). Most complete tour of the shape in the batch; the one calm clip that still says something about the hardware.
**Build.** Six segment sprites with a phase-offset sine; wings = closed/half/open (add a fourth frame if the unfurl reads thin); figure-eight = two sines. No rotation.

### 10. Dead Hang — gesture (rest, sleep) — 8.5 s — A4 D3 (7) — `climbers-7`, compressed
**Premise.** A sloth climbs up at glacial speed, hooks the underside, hangs, and falls asleep so completely that it lets go.
**Characters.** Sloth 20 px, long arms with claw hooks, fur tufts, permanent half-smile.
**Beats.** (10 s -> 8.5 s: the opening crawl is shortened so a glancer never sees a dead frame; something always moves.)
- 0-2 s: one claw hooks the ledge at x~110. Pause. Second claw. The face rises over the edge with a slow blink. Every ease is slow, but a tuft or an eyelid moves in every frame.
- 2-4 s: reaches up and hooks the underside at y=21, then the other arm, swings the body under: three decaying pendulum swings, tufts lagging.
- 4-5.5 s: slow smile, slow blink, slower blink, eyes half. Two-frame chest bob per breath lifts one tuft.
- 5.5-7 s: eyes close. Claws relax pixel by pixel; the left releases and the body rotates ten degrees (second sprite variant), hanging by one arm.
- 7-8.5 s: second claw lets go. Drops past the ledge, asleep, smiling. One tuft floats down after it. Empty.
**Twist.** It falls asleep so hard it falls.
**Geometry.** Ledge (climb-in), underside (the hang), ledge again (the drop). Both owner wishes in one clip.
**Build.** Sloth = body + two arms with hook/release states + two rotation variants. Pendulum = x offset on a damped sine. Tufts two-frame; blinks are eyelid swaps.

---

## 2. Bench (build after the ten; scores A/D/total)

- **Fire Drill** `climbers-10` — 4/4/8 — Same hatch+ladder as Trapdoor, so it is nearly free once Trapdoor ships; bring the ducklings up from 6 px to 10 px to meet the character spec before building.
- **Hide and Seek** `occluder-4` — 3/4/7 — Cut to two hiders (hanging kid + clipped blob), drop the pull-up, and it fits 10 s; the seeker falling off the ledge is the beat worth keeping.
- **Fresh Coat** `climbers-5` — 2/5/7 — The hardware-rule joke is the best director idea in the set but a stranger reads "man waving at nothing"; fix by making the first stroke visibly disappear at the wall edge (paint runs along x=153 and stops) before the ceiling reveal, then re-judge.
- **Well Bucket** `hangers-6` — 3/4/7 — Freshest ledge reading (spray from below the shape) but it is a second drink-water clip behind One Drop; build when the gesture bucket needs depth.
- **Heavy Rope** `climbers-4` — 4/3/7 — Solid reversal, warm ending, but plays identically on any ledge; keep for volume once geometry-dependent clips are done.
- **Moth Cocoon** `hangers-7` — 3/4/7 — Same shell as Cocoon (idle) with a gag ending; only worth it if the wall bumps can be made to read as "chasing a light" without explanation.
- **Pinata Friday** `hangers-8` — 4/3/7 — Good gag, priciest build; cut to 8 s and lose the spin-fall before it goes on the schedule.
- **Lights Out** `occluder-9` — 4/3/7 — Reuses the Newton's Roost bat sprite; a sweet go-to-sleep gesture that costs almost nothing once the bats exist.
- **Vending Machine** `occluder-2` — 4/3/7 — Kick-the-machine is stock and the can torrent is the costliest particle work here; the buried tail is the only detail worth saving.
- **Feeding Time** `occluder-8` — 4/3/7 — Warm and legible, but the nest sits on the floor and the notch is only a pantry; an eat-something gesture for later.

## 3. Cut and why

- **Summit** `occluder-1` — 4/4/8 — Same joke as Second Summit; its rope-flick and ice-axe opening is grafted into #3 above. Not lost, merged.
- **Blowhole** `climbers-2` — 3/3/6 — A 6 px back is not a character at 1x; no turn.
- **Squeegee** `climbers-8` — 3/3/6 — The rope from the ceiling anchor to a washer under the notch passes through the solid block, which breaks the one rule the canvas has; also the priciest rig in the batch.
- **Sloth and Spider** `hangers-4` — 3/3/6 — 12 s at 2 px/s; Dead Hang gets the sloth's hang in 8.5 s with a turn.
- **Possum Star-Stretch** `hangers-5` — 3/3/6 — Too close to the done cat stretch; the underside is only a hook.
- **Icicle Season** `hangers-10` — 3/3/6 — Seasonal dressing other notch apps already ship; 7 s before the one beat.
- **Stalactite** `occluder-7` — 3/3/6 — Third drink-water pitch; a dark drip on black and a 1 px water line are invisible at 1x.
- **Crumbs** `climbers-9` — 3/2/5 — Desktop-pet standard; dangling legs need drawing outside the shape for the only distinctive image.
- **Nothing Here** `occluder-5` — 2/3/5 — Invisible character fails the "great detailed animations" ask by design; a one-time double-take.
- **Jelly Lamp** `hangers-9` — 2/2/4 — Breathing was done (balloon); a pendant under any ceiling, no beat.
