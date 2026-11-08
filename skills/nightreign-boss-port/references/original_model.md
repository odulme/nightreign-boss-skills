# Original boss from its own model (route B): model, skeleton, rig, extra limbs, secondary motion, export, show build

Tags as in `SKILL.md`. Route B of `boss_pipeline.md`: no source game; the boss starts as a concept / generated / sculpted model, is
rigged on its own skeleton in Blender, animated by retargeting vanilla motions (`animation.md` 10), exported to FLVER / HKX / TAE and
loaded as a show build. Distilled from a tall armoured humanoid in a long frock coat with a rigid backpack, a fully armoured
telescoping tail and rigid accessories, which reached a stable non-attacking show build in a vanilla arena. Placeholders:
`<BLENDER_FILE>`, `<STAGE_DIR>`, `<CHR_ID>`, `<DONOR_CHR>` (motion donor), `<BEH_DONOR>` (behaviour-graph donor).

Gates G0-G8 and where they sit in S0-S12: `boss_pipeline.md` 0. Never report a single "done": say which gate passed
(Blender-OK / format read-back OK / loads in game / fight-ready).

## 0. Process rules for this route

- Do every gate on a NEW version folder (v001, v002 ...) and keep the previous one as rollback: two "fixes" in a row shipped
  regressions that were only visible in game [game].
- One fail-fast chain script (bash `set -euo pipefail`; every check exits non-zero): a check that only prints is skipped by the time
  the build is reported [data].
- For experiments add env switches to the builder (unset = shipped config) and rebuild only the affected clips into a test file;
  delete the test files afterwards (each ~150 MB) [data].
- A builder that always rewrites its report is clobbered by partial test builds; the full rebuild regenerates it [data].
- Havok helper scripts needed PowerShell 7, not Windows PowerShell 5.1 [code].

## 1. Modelling and budget (S1-alt, G1 / G2)

- Generate / sculpt in parts (body, helmet, pack, tail, props) when using an AI mesh generator (one pass loses detail on small rigid
  pieces), but keep sleeves, cuffs, gloves and boots in the body: a separate higher-poly bracer stacked onto cut sleeves broke the cuff
  interface and was reverted [data].
- Fix interfaces in the static model before rigging (collar vs helmet, cuff vs glove, pack mounts, tail socket): a visible seam there
  survives every later stage. Classify helmet vs collar faces by the source colour / metal / roughness maps, not by a horizontal cut (the
  cut destroyed the collar) [data].
- Budget that loaded: ~167k tris for a 2.6 m humanoid with a three-layer armoured tail; FLVER read-back ~240k verts. Vanilla references:
  a Morgott-class body ~98k verts, Heolstor ~200k verts [data; game: loads, 60 fps in a quiet arena]. LOD tier and the final budget
  with effects are open (`boss_pipeline.md` 8).
- Decimate with Blender Collapse after welding duplicate seam verts (1e-5 m): Collapse treats UV-discontinuous edges as borders, so UV
  seams stay intact. Re-run the rigging scripts on the decimated mesh instead of transferring weights [data].
- Do not flat-shade a hard-surface part to get crisp plates: an armoured tail exported with every face sharp became ~150k FLVER verts
  (vertices split per face normal). Use angle-based smoothing / custom normals [data].
- End caps on cut armour sections cost ~300 tris each: simplify caps first when over budget [data].
- Keep generator originals and every delivered‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ version immutable; work in a copy [data].

## 2. Skeleton design (S2a)

- FromSoftware core names and hierarchy (Master, Root, Pelvis, Spine, Spine1, Spine2, Neck, Head; L_ / R_ Clavicle, UpperArm,
  Forearm, Hand, Finger0-4 (Finger0 = thumb incl. metacarpal, 3 joints each), Thigh, Calf, Foot, Toe0), placed from YOUR model's
  measured joints, not a vanilla skeleton's proportions: retargeting and behaviour graphs key on names and parenting. Spine is a child
  of Root (sibling of Pelvis) in this layout [data].
- 118 bones (116 weighted) loaded and animated with a humanoid behaviour donor; no twist, face or weapon bones were needed for a show
  build. Append extras at the END of the bone order so existing indices do not move [game].
- No twist bones: set the behaviour character property `RefTwistEnable` to 0 [inferred: done pre-emptively, loads; not proven necessary].
- Coat: one chain per panel side (CoatFront / CoatSide / CoatBack, 3 joints each, per side) parented to Pelvis. Rigid accessories one
  bone each (pack and chest prop on Spine2; helmet and visor 100 % Head) [game].
- Tail: root bone on Pelvis, then one visible bone per armour section plus two hidden layer bones per section (section 4) [game].
- Master must be an identity transform in the exported skeleton: rebase it and fold its old transform into its children (the skeleton
  writer / runtime assume it) [code].
- Coordinates: Blender rig Z up, facing -Y, +X = character's left (L_ bones on +X); NR / Havok Y up, facing -Z, left-handed. Convert
  every matrix by conjugation with C = diag(P, 1), P swapping Y and Z; a bone's "along" axis ends up on local Z in game space. Verify by
  rebuilding world bone heads from the exported tracks + reference frame: 1e-6 m [data].

## 3. Rigging and weights (S2a, G3)

- Classify the single body mesh into arm / leg / coat / torso before assigning weights. Separate coat from legs with TWO competing
  geodesic floods (one seeded at the coat hem, one at the knee / boot tops; each vertex goes to the nearer front along the surface): a
  single flood from the hem leaked through the waist into puffy breeches, which then followed the coat bones and tore at the knee in
  the walk [game].
- Smooth weights along the mesh (3 passes everywhere, +12 inside the coat) to remove the kinks of piecewise segment weights; cap at 4
  influences, drop < 1.5 %, renormalise [data].
- Rigid parts (pack, mounts, prop, bracers, helmet, tail plates) 100 % on one bone; blend only at real joints (bracer: elbow top and
  wrist; tail socket: Pelvis -> tail root gradient) [data].
- Never shape cloth in the REST pose by rotating its bones (e.g. to open a coat vent for the tail): piecewise-blended weights twist the
  panel into a crease. Use a smooth displacement field on the mesh (zero on the centre seam, fading above the vent) and keep all coat
  bones unrotated in rest [data, owner-visible crease].
- Measure edge stretch (posed / rest edge length) per test pose and look where p99+ sits: tiny connector edges at the shoulder top and
  hip front can stretch 8-15x without a visible tear; broad areas over ~25 % read as pulled cloth [data].
- G3 pose tests: walk, arm raise + elbow bend, fist, squat, torso twist, tail swing / extended; dominant-bone colour map (export
  positions + weights and draw in Python if Blender's vertex-colour workbench render crashes headless) [data].

## 4. Telescoping armoured tail (an extra limb)

- Cut the tail at its armour seams into root + N sections + tip. Each section has 3 nested copies of its plate (scale 1.0 / 0.97 /
  0.94: visible, a, b), an inner dark sleeve to hide the joint gap when bent, and capped ends so an extended tail is never see-through
  [data].
- Extend = translate each a / b bone along its local +Y by its bone length (continuous 0..1); full extension here ~2.6x (2.9 m ->
  7.5 m). Ship extend / retract as tail-only additive layers to stack on attacks [data].
- While collapsed, a / b bones stay at zero rotation (bend only the visible bones), or inner plates poke through the outer ones; once
  extended they may rotate. Inner plates briefly cross during the slide - acceptable for fast moves [data].
- Placement: put the downward bend INSIDE the body (pivot well inside, not on the surface), keep the section that passes the coat vent
  straight, spread the turn back over several joints below the hem (<= 12 deg each). A pivot on the surface bulged the root "like a
  ball"; bends inside the vent stair-stepped the plates [data, owner review].
- Key hidden layer bones explicitly to zero in every action so blending never moves them [data].
- Open: hit / attack capsules along a telescoping tail (on the a / b bones?) (`boss_pipeline.md` 8).

## 5. Base motions by retargeting

Recipe, fixes and per-frame verification: `animation.md` 10. Route-specific checks: tail-vs-leg hits per frame (tail core vertices
inside leg capsules), tail / body minimum height, correlation of every secondary motion with its driver.

## 6. Tail and coat secondary motion (procedural, on top of the retarget)

Tail
- Leg avoidance from a thigh-angle signal flips too early and hits the lifted heel; drive it from which ankle (or calf midpoint) is
  actually behind the hip, with per-joint lag toward the tip, and unwind the distal part so the tip trails straight [data].
- Crossover strafes keep a foot under the tail root: no signal-based rule clears it. A per-frame root-yaw search (dynamic programming
  over candidate yaws; cost = penetration of tail capsules into leg capsules + magnitude + smoothness) cleared 222 / 389 hit vertices to
  0; a lift axis and an exact per-vertex cost did worse [data].
- Margin: 3 cm -> 6 cm fixed a residual case; 9 cm saturated the +-45 deg yaw range and got worse [data].
- Floor constraint: when a section would go below the floor, bend its upstream joint up [data].

Coat (bones only - section 7 explains why not cloth)
- Each coat chain follows its thigh's swing in the pelvis frame with a 2-frame lag and follow-through on the lower joints; front panels
  follow forward swing more, back panels backward swing. Blend the two gains with tanh through zero: a hard switch at mid-stride kinked
  the hem (jitter p95 0.092 -> 0.012) [data].
- Soft-cap the follow angle (unchanged to 25 deg, approaching 40 deg), or lunges / falls turn panels into stiff boards [data].
- Twist compensation: a coat hangs from the shoulders, so in TWIST its ring roots follow‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the chest, in BEND they follow the pelvis. Rotate
  each coat ring root (location + rotation) about the pelvis up axis through the waist by w x twist(chest vs pelvis); twist = swing-twist
  split of Spine2 relative to Pelvis about the pelvis up axis; w = front 0.8 / side 0.5 / back 0.2 (the back stays near the pelvis
  because of the tail vent); soft cap 28 -> 40 deg; gaussian smoothing sigma 2 frames [game: coat stable after the fix].
  - Do not measure twist as the heading of a forward vector: it jumped 26 deg / frame and reached 104 deg in hits where the torso bends
    far [data].
  - Re-parenting the coat to the spine was rejected: in bows / hits the skirt would follow the chest pitch and lift like a board
    [inferred].
- **Write-order bug (shipped once)**: writing location keys frame by frame let each frame evaluate the location keyed on the previous
  frame and add the twist again; the coat roots orbited the waist ~0.1-0.2 m per frame and the skirt shredded in game. Compute every
  target matrix from the untouched pose first, then write; drop stale location curves and zero the location property first (values
  leak from the previously built action in the same Blender run) [game].
- **Build guard**: on every frame of every game clip, coat ring-root local translation step <= 0.05 m / frame and offset from rest
  <= 0.30 m, else fail the build. The broken build failed 20 of 21 clips; the fixed one passes with 0.0001 m (idle) to 0.034 m (heavy
  hit) per frame [data].

## 7. Cloth: what is and is not possible

- Real-time cloth for a custom mesh is not available: vanilla `_c.hkx` cloth deforms only display vertices of the vanilla-authored mesh
  it was made for (vertex order must match) and there is no authoring path for new cloth data [data]. (Player-model ports simulated
  custom cloth graphs with much tuning - `skeleton_model.md` 7; not tried on a boss.)
- So: skinned coat chains + procedural follow + twist compensation + a frontal stance. Remaining stretch is linear-blend skinning at
  bone boundaries: reduce the twist / bend that crosses a narrow weight blend rather than tuning weights [sim].
- Dynamic coat in attacks (plan, not done): offline Blender cloth simulation per clip with body collision, baked onto a denser coat bone
  set (~40-60 bones instead of 18); physical look, no runtime reaction [inferred].

## 8. Game export (S2c, G5)

Skeleton and clips
- Write the skeleton from a JSON spec onto a vanilla template skeleton file; check with two independent readers and compare type hashes
  with vanilla: 0 mismatches before moving on [data].
- Clips in place plus a reference-frame track (x, y, z, yaw in Havok space = donor root samples x stride scale); encode, then read back:
  round-trip error here <= 7 um and <= 0.05 deg, so offline checks on the decoded data represent the game [data].
- Provide the identity additive clip (`a000_009500`, 2 frames) that humanoid behaviour graphs run [code].
- Reset the rest pose before exporting each action: tail-only layers key only tail bones, and the previous action's pose leaked into
  them otherwise [data].

FLVER
- **Flip V**: Blender's UV origin is bottom-left (v up), FLVER / DirectX top-left (v down): `uv.y = 1 - uv.y`. Unflipped UVs looked
  like camouflage in game; an offline renderer that flips back hides the bug, so check the flip explicitly [game]. (Foreign-engine
  sources already in DirectX convention keep raw UVs: `skeleton_model.md` 3.)
- Normal map: G flipped relative to OpenGL; verify with the curl test (corr(dR/dv, dG/du) > 0, same sign as vanilla maps); B = gloss =
  255 (1 - roughness)^2 [data; game: shading correct].
- Up to 4 weights, 8-bit; dummies copied from a humanoid donor scaled by the height ratio (0.797 here) for lock-on / hit / effect
  points: a donor point-cloud transfer is enough for a show build [data; lock-on in game not yet confirmed]. Placement dummies for
  attacks later go on the fixed SFX node (`skeleton_model.md` 6).
- Materials: one per texture set (body, tail, helmet, pack, prop, visor glow ...); an emissive visor needs a glow material [game].
- Read back the FLVER (node / mesh / vertex / material counts, bind-pose error ~2.6e-7) and render it posed. If your offline renderer
  came from another project, check winding: one copy reversed faces after the axis swap and rendered black [data].

Textures
- Show-build sizes: body + tail 2048, other parts 1024 -> high-res TPF ~33 MB, low-res ~2 MB; source was 8K / 4K. Keep the sources,
  downsize only the game copies [game].

Hit capsules, TAE, behaviour
- Physics hkx from a donor physics template with capsules measured on YOUR body (column placed by world offsets, limited head radius),
  then the PTCH / missing-hash audit and a convex fault simulation on every hkx (`physics_hurtboxes.md` 2) [game: hits land].
- TAE: map the donor TAE's entries onto your own clip ids (180 entries here) and read back; keep only control events in a show build
  [data].
- Behaviour: copy a humanoid behaviour donor (`<BEH_DONOR>`) with your skeleton swapped in, plus its HKS under your id
  (`donor_graph.md` 2) [game: loads and idles; reactions not yet checked in game].

## 9. Show-build test setup (S2e, G7)

- Put the boss into a vanilla arena slot first (no own map yet): replace the target Nightlord's MSB part with your part (same entity id,
  variation -1) and keep everything else vanilla [game].
- Params as new rows only: NpcParam based on the target's row with very low HP, NpcThinkParam whose battle goal does nothing (AI off),
  ChrModelParam, ScratchedPartsParam; text rows in the NpcName FMG [game].
- Entrance: a hub action button that warps to the arena, a debug fight flow with a retry / return dialog, and an in-arena "return" anchor
  asset. The return event is generated only when the builder finds the anchor in the arena MSB it reads: point that MSB candidate at the
  CURRENT stage - after an old stage moved away the builder silently fell back to the vanilla MSB and dropped the return event. Assert it
  in the build [data].
- Separate‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ test profile: its own save file, the base mod package, then a "common" package (hub / arena events, menu text), then the
  boss package; each version in its own `<STAGE_DIR>` [game].

## 10. Health bar and name

- The bar name at fight start is NOT `NpcParam.nameId` and NOT the name argument of the victory event 90075901 (that one feeds the
  victory banner, 2003[100]); patching 90075901 left the vanilla name on the bar [game].
- Common event 90075101 (fight start: bar, name, BGM, forced clips) hard-codes the vanilla boss's NpcName in 2003[11] and 2003[102]. Copy
  it into the map EMEVD as a local event with your name id and redirect every caller for your entity from `InitializeCommonEvent`
  2000[6] to `InitializeEvent` 2000[0] (slot 0); read back that no caller is left [data; same method used by earlier in-arena
  replacements in game].
- Each language's name from the official localisation of the source work, not your own translation; ship every language the game ships
  (bars showed BLANK names where a language was missing) [game, data].

## 11. Offline checks that paid off

- Read-back render of the STAGED FLVER posed with the STAGED clip data on several frames per clip (idle start / middle / end, a turn
  mid-frame, a heavy hit mid-frame, a strafe): all secondary-motion bugs so far were invisible on frame 0 [game].
- Edge-stretch heat map (red stretched, blue compressed) plus a numeric "seam" metric on the vertices that blend two named bones;
  compare before / after on the same frames [sim].
- Dominant-bone colour map of the skin weights [data].
- EMEVD dump: list every instruction carrying a given int (entity, name id, event id) and every 2003[11] - finds where a value really
  comes from [data].

## 12. Housekeeping

- Blender keeps the previous save as `*.blend1` next to every saved file (~150 MB each here): delete them in the rebuild script,
  archive old versions to another drive, delete experiment files - or a small system drive fills up [data].
- Stopping a background shell task did not stop a running multi-step chain script: check the process list / log after stopping [data].

## Unverified

Baked offline cloth onto extra coat bones (bone budget, whether graph / TAE need anything for extra non-humanoid bones, blending
between baked clips); LOD tier and texture budget with effects; tail hitboxes on a telescoping tail; second form as one character with
display-mask switching vs two characters with HP hand-over (depends on sharing the skeleton); whether the frontal stance reads well in
game and how much residual twist heavy-hit frames show; whether `RefTwistEnable = 0` is required; lock-on from transferred donor
dummies; the behaviour donor's reactions on this skeleton.
