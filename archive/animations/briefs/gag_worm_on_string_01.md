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
