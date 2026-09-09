export const meta = {
  name: 'notch-parade-author-v2',
  description: 'Author approved clip briefs as detailed pixel-art modules (one agent per clip), blind-judge readability, director-judge charm/craft, one revision, keep or kill',
  phases: [
    { title: 'Author', detail: 'one agent per clip: write module, render, inspect, iterate' },
    { title: 'Judge', detail: 'blind viewer + brief-match + director per clip' },
    { title: 'Revise', detail: 'one revision for failures, then re-judge' },
  ],
}

// args = [{ name, bucket, brief, read }, ...]   (name = module/file name, read = what a stranger should see)
const CLIPS = Array.isArray(args) ? args : []
if (!CLIPS.length) throw new Error('pass the approved clip briefs as args')

const ROOT = '/Users/bittu./Documents/notch-parade'

const RULES = `You are a senior pixel artist and animator authoring ONE silent clip for "Notch Parade": a free Mac app where pixel characters
play tiny clips in Apple's notch silhouette. Everything is code: ASCII sprites rendered by ${ROOT}/tools/sprite.py.

FIRST read these files completely — the engine, the detail helpers, and the reference clip that sets the art bar:
  ${ROOT}/tools/sprite.py
  ${ROOT}/tools/clips_lib/gag_pigeon_camera_02.py     (the bar: 34 px, 5-tone ramp, eye ring + glint, sheen, rim outline, assemble())
  ${ROOT}/tools/clips_lib/gesture_snail_tea_01.py     (older, simpler; shows the Clip/frame loop only — do NOT copy its art level)

CANVAS AND WORLD (fixed, do not edit sprite.py):
- W=184 x H=52 art px, pure black. Each art px is 3x3 device px on the Mac (1.5 pt). The canvas is the WHOLE black shape.
- The HARDWARE NOTCH occludes x NOTCH_L..NOTCH_R (31..153), y 0..NOTCH_B (21). Nothing drawn there is ever seen. It is a solid
  object: hang from its underside (y=21), climb its sides, hide behind it, drop out of it. Beside it the ceiling is y=0.
  The floor/ledge is y=51; things can climb up over it or fall off it. Bottom corners are rounded (~16 px clipped).
- Lead characters 30-44 px tall; supporting ones 18-30; props 6-16. Small = unreadable on the notch; the owner rejected 18-px art.
- 12 fps. Clip 4-12 s. Every clip STARTS and ENDS on a completely empty frame (render.py asserts this).
- NO TEXT of any kind. Meaning through action.

ART BAR (the owner's words: "it has to be very detailed"):
- Shading: at least a 4-tone ramp per material via ramp(base) — shadow, base, light, highlight — lit from top-left, shadows cooler.
- Rim: assemble() the parts into one sprite and outline() it ONCE with a muted colour that reads on black. Never outline parts separately.
- Eyes carry the character: white, pupil, 1-px glint; an iris ring if the animal has one. Eyelids for blinks (swap sprite).
- Texture where it matters: fur strokes, feather lines, scales, cloth folds — 1-px darker/lighter accents, not noise.
- Secondary motion on EVERY character: tail/ears/antenna/cloth lag, breathing bob (bob()), a settle after every action,
  puff() on landings and take-offs, shadow() under grounded characters, burst() for sparks/confetti, tint() for night.
- Timing: anticipation -> action -> overshoot -> settle. Use ease(). Hold the look-to-camera for at least 8 frames.

MODULE CONTRACT — create exactly one file ${ROOT}/tools/clips_lib/<NAME>.py:
  import sys, os
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  from sprite import *
  BUCKET = '<idle|gag|gesture>'
  def build():
      c = Clip('<NAME>', <seconds>)
      for i in range(c.n): im = c.frame(); ...
      return c
The Clip name must equal the file name. Touch NO other file. Per-module colours: sprite(rows, MYPAL).

WORK LOOP (at least 3 rounds; keep going until it is genuinely good):
  1. Write the module.   2. cd ${ROOT} && python3 tools/render.py <NAME>
  3. python3 tools/zoom.py <NAME> <3-5 key frame indices>   then LOOK (Read tool) at
     ${ROOT}/test/out/<NAME>_sheet.png (whole clip, every 6th frame; the notch occluder is painted dark grey) and
     ${ROOT}/test/out/<NAME>_zoom.png (close-ups).
  4. Judge yourself honestly: is the character recognisable in 1 s? big enough? shaded, not flat? anything floating or detached?
     does the geometry gag (notch / ledge / ceiling) actually read? is the timing snappy? Fix and repeat.
Never declare done without having looked at the rendered images.`

const AUTHOR_OUT = {
  type: 'object',
  properties: {
    name: { type: 'string' }, written: { type: 'boolean' }, seconds: { type: 'number' },
    key_frames: { type: 'array', items: { type: 'integer' } }, self_assessment: { type: 'string' }, rounds: { type: 'integer' },
  },
  required: ['name', 'written', 'key_frames', 'self_assessment'],
}
const BLIND = {
  type: 'object',
  properties: { character: { type: 'string' }, action: { type: 'string' }, message_if_any: { type: 'string' }, confidence: { type: 'integer' }, craft_notes: { type: 'string' } },
  required: ['character', 'action', 'confidence', 'craft_notes'],
}
const MATCH = { type: 'object', properties: { readability: { type: 'integer' }, why: { type: 'string' } }, required: ['readability', 'why'] }
const DIRECTOR = {
  type: 'object',
  properties: { charm: { type: 'integer' }, detail: { type: 'integer', description: '1-5: shading, eyes, texture, size — 5 = matches or beats the pigeon v2 bar' }, technical_pass: { type: 'boolean' }, notes: { type: 'string' } },
  required: ['charm', 'detail', 'technical_pass', 'notes'],
}

function authorPrompt(c, feedback) {
  const brief = c.brief_file ? `Read your approved brief FIRST (beats with timings, twist, build notes): ${c.brief_file}` : c.brief
  return `${RULES}\n\nYOUR CLIP: name = ${c.name}   bucket = ${c.bucket}\nBRIEF (approved by the owner, follow its beats):\n${brief}\n` +
    (feedback ? `\nA judge panel reviewed your previous version and it did NOT pass. Their notes:\n${feedback}\nRevise the SAME module in place, re-render, re-inspect, and only stop when the notes are addressed.\n` : '')
}

async function judge(c, a) {
  const sheet = `${ROOT}/test/out/${c.name}_sheet.png`, zoom = `${ROOT}/test/out/${c.name}_zoom.png`
  const zoomCmd = `cd ${ROOT} && python3 tools/zoom.py ${c.name} ${(a.key_frames || [0]).join(' ')}`
  const blind = await agent(`You are a stranger seeing a tiny silent pixel animation for the first time. Run in Bash: ${zoomCmd}\nThen LOOK (Read tool) at ${sheet} (whole clip top-to-bottom, every 6th frame; the dark grey block top-centre is the hardware notch that hides whatever is behind it) and ${zoom} (close-ups). Say what character you see, what it does, and whether it seems to tell you something wordlessly. If it is a blob, say blob. Then blunt craft notes.`,
    { label: `blind:${c.name}`, phase: 'Judge', schema: BLIND, effort: 'medium' })
  const [match, dir] = await parallel([
    () => agent(`Intended: ${c.read}\nBrief: ${c.brief || ('see ' + c.brief_file)}\nBlind viewer reported: ${JSON.stringify(blind)}\nScore readability 1-5 (5 = they saw exactly the intended character, action and message; 3 = character right, action vague; 1 = unrecognisable).`,
      { label: `match:${c.name}`, phase: 'Judge', schema: MATCH, effort: 'low' }),
    () => agent(`You are a picky animation director. Brief: ${c.brief || ('read ' + c.brief_file + ' first')}\nLOOK (Read tool) at ${sheet} and ${zoom} (if missing run: ${zoomCmd}). Compare the art level against the reference ${ROOT}/test/out/gag_pigeon_camera_02_zoom.png (render it if missing: cd ${ROOT} && python3 tools/render.py gag_pigeon_camera_02 && python3 tools/zoom.py gag_pigeon_camera_02 27). Score charm 1-5 and detail 1-5, decide technical pass (starts+ends empty, no text, no teleporting, silhouette reads on black, geometry gag actually reads), and write specific fixes.`,
      { label: `director:${c.name}`, phase: 'Judge', schema: DIRECTOR, effort: 'medium' }),
  ])
  const ok = !!(match && dir && match.readability >= 3 && dir.charm >= 3 && dir.detail >= 3 && dir.technical_pass)
  return { blind, match, dir, ok }
}

log(`Authoring ${CLIPS.length} approved clips`)
const results = await pipeline(CLIPS,
  c => agent(authorPrompt(c), { label: `author:${c.name}`, phase: 'Author', schema: AUTHOR_OUT, effort: 'high' }),
  async (a, c) => {
    if (!a || !a.written) return { name: c.name, ok: false, reason: 'author did not write the module' }
    const j1 = await judge(c, a)
    if (j1.ok) return { name: c.name, ok: true, rounds: 1, judge: j1 }
    const notes = `Blind viewer saw: ${JSON.stringify(j1.blind)}\nReadability ${j1.match?.readability}/5: ${j1.match?.why}\nDirector: charm ${j1.dir?.charm}/5, detail ${j1.dir?.detail}/5, technical ${j1.dir?.technical_pass ? 'pass' : 'FAIL'}: ${j1.dir?.notes}`
    const a2 = await agent(authorPrompt(c, notes), { label: `revise:${c.name}`, phase: 'Revise', schema: AUTHOR_OUT, effort: 'high' })
    if (!a2 || !a2.written) return { name: c.name, ok: false, rounds: 2, judge: j1, reason: 'revision failed' }
    const j2 = await judge(c, a2)
    return { name: c.name, ok: j2.ok, rounds: 2, judge: j2, first: j1 }
  })
const done = results.filter(Boolean)
log(`${done.filter(r => r.ok).length}/${CLIPS.length} passed`)
return done
