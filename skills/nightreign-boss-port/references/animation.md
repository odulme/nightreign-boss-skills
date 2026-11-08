# Clips: conversion, root motion, length, variants, stitching, retargeting, props, verification

Tags as in `SKILL.md`. Pipeline stages S2b / S4 (`boss_pipeline.md`). Same-family (DS3) clips are carried byte for byte instead
(`ds3-nightreign-port`).

## 1. Target format and encoder

- NR clips: spline-compressed Havok 2018.1 tagfiles at 30 fps; ThreeComp40 rotations, 16-bit translations, keep scale tracks;
  blocks of <= 256 frames, block b covers frames b x 255 .. b x 255 + 255 [data].
- Use a fixed encoder: the stock soulstruct packer misses 4-byte alignment after an odd animated scale track, writes a
  near-identity constant quaternion without its flag, and its decoder splits blocks at 256 instead of 255 [data].
- Write with HKLib into vanilla clip templates: one without a reference frame (in-place clips), one with
  `hkaDefaultAnimatedReferenceFrame` (up (0, 1, 0), forward (0, 0, 1)), an identity additive template for 9xxx layers [game].
- Verify every clip with three readers (HKLib bit-identical, a tagfile reader, your own spline decoder) and compare decoded FK +
  reference frame with the source world pose at EVERY frame. Budgets that played well: world error p99 ~8 cm / max ~22 cm
  vs the source, encoding error <= 2 mm / 0.06 deg; measure far helper bones relative to their lever arm [data].
- Store one hkx per distinct clip (hash the content); other TAE entries import it. anibnd layout: skeleton 1000000, TAE
  3000000, compendium 7000000, clip member 1000000000 + group x 1000000 + number. anibnds of 7-9 MB (2 x the largest vanilla)
  loaded [game].

## 2. Resampling and the source clock

- 60 fps -> 30 fps: take source frame 2k; when (F - 1) is odd append one exact last sample (the clip gets <= 1/60 s longer)
  [data].
- Apply source speed curves through the clock contract (`survey_and_extraction.md` 4) in clip sampling AND timeline timing.
- Keep the source rate as ONE switch in the builder: a clip treated as 30 fps runs at half speed and every event lands late
  [game].

## 3. Root motion

- NR reads root motion from the reference frame: one (x, y, z, yaw) sample per 30 Hz frame, first sample 0, yaw about +Y,
  unwrapped (may exceed pi), positive = right turn. Master stays identity; the pelvis stays at the horizontal origin; travel
  and yaw go into the reference frame [game].
- Split recipe (foreign source, root track separate from the body): source world = RootMotion . FK; NR world = T(x, y, z)
  Ry(yaw) . FK. Reference sample = converted root (x, [y], z, yaw), rebased so sample 0 = 0; the residual
  Q = Mref^-1 . Root (pitch, roll, vertical offset, non-zero frame 0) is multiplied into every child of Master [game].
- Root motion below ~1 cm / 0.05 deg in total: bake it into the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ body, no reference frame (idle sway) [data].
- Root vs body compensation: some source motions move the root far while the body moves back (72 m root, 44 m back = 27.9 m
  visible). Use the HIP's horizontal travel (body + root) as the reference frame ("anchor hip") [data].
- Flight heights: source flight motions can be authored relative to a height the source ENGINE holds (not in the data). Bake
  per-segment vertical offsets into the children of Master (constant, ramp, continuity with the previous segment's hip,
  landing to 0). The entity stays on the ground [game].
- Stage-anchored motions (cutscene coordinates, body 15-155 m away inside the bone tracks): make a stage version anchored on
  the source landing bone and an in-place version (pelvis pinned); use the in-place one or extract the horizontal travel
  [data].
- Same family: the Master track moves in most clips and is carried byte for byte; source Master offsets can be intentional
  (centring the collision capsule) [game].
- Measure as the game reads it: decode the INSTALLED hkx before blaming the engine. When every engine turn is frozen and the
  actor still turns, it is the clip's root motion. A source root yaw can be pure bookkeeping (body already turned):
  measure the trunk heading from a mirrored bone pair before dropping or keeping a yaw [game].
- **Airborne spans are measured on posed skeletons, not read from root motion** (root motion carries no height; the height lives
  in the body). Feet = rear toes + wing-hand digits (whatever touches the ground); jump start = first frame with all feet > 0.30 m
  above the start ground or pelvis > 1.0 m above standing; touchdown = after the last frame with pelvis > 3 m, first frame with a
  foot within 0.30 m or pelvis back within 1.0 m. The TAE JT27 gravity-off span agreed within 0.1-0.2 s but once missed a
  gravity-on descent and once ran ~1 s past touchdown. Use the measured span for SpEffect 45 / airborne markers
  (`reactions_death_phases.md` 6) [data; game no complaint].

## 4. Clip length rule [game]

- Keep every clip with root motion within 29.7 s and 892 reference samples (largest known good). A 45.3 s / 1,359-sample clip
  turned the actor by itself; splitting it fixed it.
- Frame count alone is not the limit: a 23.5 s clip with 1,413 frames (60 Hz pose track) and 707 reference samples played.
- Stationary event clips without travel ran up to ~47 s in solo and co-op (hover baked in the body, AI off). Vanilla's longest
  attacks are ~33 s.
- List frames / duration / reference samples of every installed clip after every build.

**Splitting recipe**: cut where the root is not moving (e.g. 0.3 s after the last flame row); overlap ~0.4 s so both parts show
the same motion during the blend; every timeline row goes into exactly one part, rows crossing the hand-off (flags, markers,
turn rate) into both; play part B in another slot or as a variant of a slot, forced on schedule [game].

## 5. Variants of one move

**Distance variants** (the source picks a travel distance; NR plays one clip) [game]:
- Scale the body's forward travel so the entity path is monotone and ends exactly L ahead; write the lateral / lag part of the
  body into the children of Master; reference z = -path.
- Buckets (e.g. 15 buckets 27..111 m in 6 m steps) as animIdOffset variants (10M..150M), chosen by ring regions around the
  destination a few frames before the request; the base clip is the fallback and must never overshoot.
- Register every variant leaf in the graph (`donor_graph.md` 3), else the base always plays.

**Mirrored variants** [data]: W'_b = X . W_sym(b) . C_b with C_b = (X . Wbind_sym)^-1 . Wbind_b (bind pose maps to itself);
negate root x and yaw; mirroring twice must return the original within the rig's own asymmetry; mirror in SOURCE space
(convert to source, mirror, convert back). Mirrored clips come out ~27 % larger.

**Member swap inside an installed clip**: first prove your converter rebuilds the installed segment (here 0.2 mm, 0.06 deg),
then splice the new member (same frame count, ~9-frame seam blend, root after the segment carried over) [game, weak].

**Root-only retouch**: keep the encoded pose bytes, rewrite only the reference samples (e.g. scale a return flight to land
in front of a gate) [data].

## 6. Chains and stitching

- Rebuild the source's own chain (take-off -> flight -> swoop -> turn -> body -> return -> landing) from the source motions;
  a generic glide loop made a fast take-off last 17-19 s instead of 4 s, and a 6.4 m pose gap at a seam swept the wings [game].
- Seams: segment k starts exactly at its t_start; the previous pose's delta decays to 0 within 0.15 s (0.2 s for big jumps,
  <= 40 % of the segment) or a smoothstep cross-fade over the first ~10 frames; quaternion hemisphere continuity; root motion
  accumulates; error outside blends <= 0.1 mm [game].
- Additive / hit layers and look-at / IK come from the donor graph; leave them off unless mapped.

## 7. Pacing, speed, blend

- Locomotion: scale root motion per slot to NR-like speeds (humanoid boss: walk ~2 m/s, slow walk 1.5, run 6.5) [game].
- Forward step: replace only the horizontal reference displacement of a clip (bones, height, yaw untouched) - a source back-dash
  peaking at 43.6 m/s that never hit in front became a short forward step [game].
- Wind-up / reaction time: stretching with slow motion was rejected by the tester. Accepted: a piecewise‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ time map that leaves
  the key motion (e.g. a blink) untouched, eases the stretch, moves EVERY TAE event through the same map, resamples the hkx and
  keeps total root travel [game].
- Blend-in: graph default transitions are 0 s in most vanilla states, so the cross-fade is the TAE blend event (type 16) at the
  start of the NEW clip. Vanilla Nightlord attacks: median 0.333 s, max ~0.55 s. Rule: p90 body cross-fade speed <= 3 m/s,
  cap 0.5 s, end <= first hit - 0.25 s (an inherited 0.233 s caused visible pops) [data, mechanism inferred].
- Teleport / blink clips: copy Heolstor's blink rows (opacity triple TAE 193, JT39, turn-speed rows) + a TAE 760 for the
  arrival distance; one shared timing for all blinks (fade 0.07-0.23 s, gone 0.23-0.57, reappear 0.57, opaque 0.73) [game].

## 8. Solver bones and scale

- Runtime-driven helper bones (constraint solvers) have no motion data: solve them per frame and bake them as ordinary tracks;
  the encoder input is the SOLVED pose; re-run the solver after any retarget, trim or stitch [game].
- Keep scale tracks: non-uniform wing scale composed like the source (error 4e-6) [data]. Preview renders must use Havok's QS
  chain rule (child offset scaled by the parent scale), not 4x4 matrices [data].

## 9. Checks per build

Clip lengths + reference samples; every TAE entry's imported clip exists; body + root trajectory of changed clips vs the source;
heading as the game reads it (`tae_turning_windows.md` 4); seams (pose jump per frame); pose contact sheets of the WRITTEN files;
for new or changed moves, the move requested and looped from the debug panel in game (`debug_panel.md` 7).

## 10. Retargeting vanilla motions onto your own skeleton (route B, also for missing moves of a port)

Donor choice
- Pick the motion donor by posture first: an upright humanoid donor (Nameless King c7900) needed far less correction than hunched
  ones (Heolstor c7580 leans ~35 deg, Godskin Apostle c3560 ~39 deg) [data].
- **Check the donor's stance twist before building anything on its idle**: c7900 stands with the pelvis ~26 deg off the chest, and that
  propagates to every clip that starts from idle [data; inferred for "every clip"].
- Decode vanilla clips read-only (spline-compressed Havok -> per-frame TRS + root-motion samples); never write into the vanilla dump
  [code].

Conversion
- Per mapped bone apply the world-space rotation DELTA relative to the donor rest pose, then align limb / finger / spine bone
  directions to the donor's (pose copy). Root motion goes on Root; scale travel by the leg-length ratio (0.631 here) [data].
- Verify the turn yaw sign by foot sliding: wrong sign 0.81 m/s planted-foot speed, right sign 0.14 m/s [data].
- Vanilla loop clips repeat frame 0 at the end: every loop-phase operation (mirroring, foot lock) wraps on period = n - 1, or left /
  right end up one frame apart [data].
- Foot grounding per frame (lowest contact point to the floor) for idle / walk / turns; only "no penetration" for clips with flight
  (hops, falls); let toes curl up when the heel lifts [data].

Things that broke and their fixes [data unless marked]
- Donor holds a weapon in the right hand -> right arm = mirrored left arm, shifted half a cycle in locomotion.
- Donor walk's right leg wobbles at toe-off (knee 15 -> 49 -> 33 -> 70 deg) -> mirror the clean leg, then a ball-of-foot lock: per
  contact interval (lower foot AND slow in world space) hold the ball of the foot at the weighted mean of the interval with two-bone IK;
  lock the ball (the heel-off pivot), not the ankle, or the heel-off slides.
- Narrowed track (walking "on a line") made the boots touch -> keep 80 % of the track width plus a 7 cm outward arc while the swing
  foot passes the planted one.
- Donor torso leans back 10-13 deg -> "upright": remove the clip-mean lean of spine / neck / head and keep 60 % of the motion around
  it (loops); for one-shot clips straighten around the stance at the first + last frame instead of the clip mean, or the reaction is
  damped.
- Signature pose (e.g. open arms) rides on the chest as a target; one-shots keep a share of the source arm motion (steps 20 %, small
  hits 35 %, heavy 45 %, stagger / death 60 %) so arms are not frozen.
- One-shot clips start / end on the idle stance: offset the feet (root-local xy) toward the stance, smoothstep between the ends,
  then ball lock.
- A big donor hop (feet 0.6 m up, chest folding 88 deg) can be calmed in place: damp pelvis rotation, hip height, foot lift, push-off
  rotation and foot xy around the ends' stance (keep 12-40 %), same travel and timing.
- **Stance twist**: with an upright, forward-facing torso the donor's whole 26 deg pelvis-vs-chest offset sat in the narrow Pelvis /
  Spine weight blend: waist band stretched 80-120 %, coat front sheared across one leg. Fix: turn the pelvis + both legs as one unit by
  a constant yaw (the pelvis-vs-chest heading at the reference frames) and land the feet on a frontal stance with a fixed toe-out.
  Waist seam stretch (mean over Pelvis + Spine blend verts): idle 0.60 -> 0.12, strafe 0.67 -> 0.13, walk back 0.54 -> 0.17, 180 turn
  0.66 -> 0.23 [sim; in-game check pending].
  - Locomotion: turn the PELVIS ONLY - turning the legs too tilts the foot paths against the root travel and planted feet slid ~10x
    (0.016 -> 0.15 m/s) [sim].
  - Stance clips (hits, death): pelvis-only made the tail (a pelvis child) hit the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ legs for 35 frames; keep pelvis + legs and relax the
    foot-lock detection (vmax 0.035 -> 0.06 m / frame, vmin 0.02) so slightly creeping planted feet are still caught [sim].

Verification (frame by frame, every clip)
- Planted-foot speed = horizontal speed of the slower foot's ball point (m/s): report mean and p90 per clip and compare against the
  previous round, not against zero (hits legitimately skid) [data].
- Extra limbs: tail-vs-leg hits per frame (tail core vertices inside leg capsules), tail / body minimum height [data].
- Correlate every secondary motion with its driver (e.g. coat hem vs knee forward position): a negative correlation exposed an
  inverted sign that had shipped in every clip. Do not judge sign by eye [data].
- A GIF per clip from a fixed follow camera over a 0.5 m ground grid for the owner's review; sliding is judged on the grid [data].
- Secondary motion (tail, coat): `original_model.md` 6. Export, identity additive `a000_009500`, rest-pose reset per action:
  `original_model.md` 8.

## 11. Props with bone chains (siege weapons, telescoping drills)

- Source props are often stored in the retracted rest pose; an `(x, y, -z)` conversion reversed one (the open rear tube faced the
  arena: "a cylinder without a drill"), and 4 m per stage hid the shaft in the wall [game].
- With no travel animation in the data (native code drives it), take the reach from geometry (tube lengths minus ~1 m overlap per
  joint), re-encode the asset clips (extend / hold + spin / retract), keep skeleton / TAE sounds / binder layout byte-identical, PTCH /
  THSH audit MISSING 0, and enlarge the FLVER header bounding box to the whole motion so the far tip is not culled [game OK; culling
  reason inferred].
- Set-piece contact boxes for such props: `attacks_hits.md` 4.9.

## Unverified

Whether the limit is ~30 s or ~1,024 reference samples; 60 Hz pose tracks and 2-sample reference frames being fully correct;
the mirrored chain built from MHW aliases (no explicit verdict); vertical travel inside the reference frame being executed;
source speed curves matching source playback exactly; the frontal-stance retarget in game; whether the donor stance twist really
propagates to every clip.
