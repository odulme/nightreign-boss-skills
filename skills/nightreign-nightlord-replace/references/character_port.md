# Porting the boss character (model, skeleton, physics, graph, clips, TAE, hits, FX, sound)

Tags as in `ids_and_planning.md`. Exe offsets: NR 1.3.3.0. General FLVER / TPF / WitchyBND basics are in the skill
`nightreign-modding`; DS3-family sources (same engine family, converted clips / TAE / FXR / FSB) are in `ds3-nightreign-port`.
Deep version with the full recipes: skill `nightreign-boss-port` (this file is its short form; where the two differ, the deep
version is newer). Pipeline stages S1-S7 of `nightreign-boss-port/references/boss_pipeline.md` cover this file; build the
dev-only debug panel (`nightreign-boss-port/references/debug_panel.md`) and the sync log before the first attack (S3).

## 0. Source extraction (any game)

- Extract everything once and keep it read-only: the source game may be uninstalled later and the extraction becomes
  irreplaceable. Collect mesh, skeleton, every motion, per-motion timelines (attack / effect / sound / flags), attack and hurt
  volumes, AI trees, enemy params, sound banks (voice, SE, BGM), textures incl. virtual / streamed textures.
- Write your own decoders when public tools are partial, and verify every decoder with renders against the source.
- Examples that worked:
  - MHW: WorldChunkTool (needs oo2core_8), MHWorld Blender tools / MHW Model Editor for MOD3 / TEX; own decoders for LMT
    (all encodings), TIML timelines, shells (SHLP), `em###.col` attack capsules, THK AI trees. LMT is **60 fps** (treated as
    30 fps, every event lands late and clips run at half speed); units are cm; alias motions can be mirrored
    copies (which flags2 bit marks them is disputed, bit 0 vs 0x10: verify by rendering; symmetric-bone map); shell lifespans
    are seconds; the
    motion "busy" bit is cleared where the source lets the next action start (use it as the release point) [data].
  - GBF Relink: GBFRDataTools (extract, bxm -> xml, tex -> dds), GraniteTextureReader (virtual textures); `.mot` = Platinum mot
    v2, 60 fps Hermite splines, absolute local values, Euler XYZ (R = Rz Ry Rx) - own parser; attack boxes are HALF extents.
- Runtime-driven helper bones (constraint solvers, e.g. Relink `.sop`) have no motion data: solve and bake them as ordinary
  animated bones, and re-run the solver after any retarget / trim [game].
- Per attack, record during extraction: the source's own spawn joint (MHW breath shells come from a breath joint, not the head),
  shell life vs effect life, radius and growth, re-hit interval, and whether the pattern is anchored to the target, the boss or the
  floor; six later fix rounds of one port were "aimed / anchored from the wrong place" [game].

## 1. Skeleton and coordinates

- NR characters face **-Z**. For a Y-up source facing +Z with left = +X: position (x, y, -z) x unit, quaternion (-qx, -qy, qz,
  qw), same mirror for vertices / normals. Check handedness on an asymmetric feature (sword hand, eye) [game].
- Add `Master` (identity, never animated) at index 0 and a `Root` if the source has none; NR order Master -> Root -> Pelvis,
  depth-first, parent < child [game].
- Skeleton bone count is not the problem: 538-bone skeletons work [game]; vanilla goes up to 522 in a skeleton and 489 weighted
  in one FLVER [data]. Every port that ran had <= 256 WEIGHTED bones (UByte4 bone indices); more needs the UShort layout (untested).
- FLVER binds to the Havok skeleton by NAME; animations and ragdoll mappers bind by INDEX [data].
- Build the skeleton hkx with the soulstruct-havok encoder (Blender's Python) then HKLib (Smithbox, pwsh 7) for the tagfile, or
  with HKLib alone from a vanilla skeleton template;
  read it back with three independent readers [game].

## 2. Model (FLVER), materials, display masks, dummies

- FLVER node order must be [weighted bones] -> [mesh nodes] -> [dummy owner nodes] -> [other bones], second skeleton table
  depth-first; otherwise the game crashes when the player walks near (exe+0x6F3EEA8 / 0x6F3EED7) [code, game].
- Template = a vanilla FLVER for headers, vertex format, GX lists (c2130's humanoid one also worked for a quadruped dragon) [game].
- Weights: <= 4 bones per vertex, drop < 1.5 %, 8-bit quantised with sum 255, no zero-weight vertices; least-squares fit 4
  influences from an 8-weight source [game]. Unanimated chains may be merged into their parent (optional).
- Materials: generic character matbins (`C[AMSN]`, `_e` alpha test, `_Glow`) with texture paths in the FLVER; no allmaterial edit
  needed. Material names must be unique (a duplicate stopped a texture from loading) [game].
- Display masks: material prefix `#NN#` = mask group NN; NpcParam `modelDispMaskNN` must be 1 for every group that should‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ show,
  or the mesh is invisible [game]. Toggle groups with EMEVD ChangeCharacterDispmask.
- Dummy polys: the NPC getter uses `id % 1000` [code]: keep every dummy id < 1000 and unique (high ids aliased low ones and broke
  all attacks) [game]. Copy the donor's conventions: 220 lock-on (222-228 multi-lock), 200 hit / status surface, 960 death cloud,
  10 mouth / breath origin, 900 / 901 trace head / tail. Change a shared dummy master atomically across FLVER, TAE, AtkParam,
  Bullet [game].
- **A dummy with ParentBoneIndex -1 / AttachBoneIndex -1 is NOT at the model origin**: the engine binds it to node 0, which on an
  MHW-style skeleton is the animated hip (bullets from such dummies rose as tilted "staircases" 3-15 m up) [model, game]. Parent
  every placement dummy to the fixed SFX owner node (`Dmypoly_SFX_固定` in FromSoftware FLVERs: in the FLVER, not in the HKX
  skeleton, never animates); floor dummies at Y 0.3; ship a dummy change as anibnd + chrbnd + regulation together. **REFINES**
  the dummy rules above; deep version `skeleton_model.md`.
- Ship each helper character only the textures its meshes use (duplicated 88 MB sets inflated every arena load by 365 MB) [data];
  slimming did not prevent a later GPU timeout on the affected machine [game-MP].

## 3. Hurt volumes, parts, collision

- What gets hit = physics hkx in the chrbnd (id 300): keyframed ragdoll capsules (names may stay the template's: the mapper
  binds bodies to bones) [data, game]. Part groups live
  in the hkxpwv (id 500) and map to NpcParam `partsDamageRate1..8`; weak flag 0x09 -> `weakPartsDamageRate` [data].
- `hitHeight / hitRadius / chrHitRadius` are the movement capsule, not the hurtbox [data].
- Generate capsules per bone from the mesh (p85-p95 vertex distance) and write the hkxpwv yourself (SoulsFormats cannot read NR's)
  [game]. Hurt capsules must stick out of the movement cylinder or short weapons cannot reach them (a hovering humanoid got a
  vertical Root column r 0.70 to the ground; chrHitRadius below hitRadius) [game]. Large flyers: +25-45 % capsule radius so
  arrows and ordinary attacks connect; keep the head weak point exposed [game].
- `chrHitGroupAndNavimesh 5`: players collide with the ragdoll capsules (Ancient Dragon pattern) [data].
- **Check hurtbox coverage before anybody grows capsules** [data]: pose the installed skeleton at each logged hit, signed distance
  to every capsule, mesh coverage per part (one head was 99.6 % covered, median hit distance -0.002 m: slow breaks were never a
  hitbox problem). Capsule damage type = (hkxpwv dword +4 >> 8) & 0xF: 1-8 -> partsDamageRate1-8, 9 -> weakPartsDamageRate, 0 ->
  none; NpcParam `partsDamageType` 0 applies the rate only to arrow attacks; a rate on a type no capsule carries does nothing
  [code]. Part records (40 global slots) and the damage path: `fight_script.md` 7.
- HKLib-written physics hkx needs two repairs, plus a PTCH audit (MISSING = 0, UNHASHED = 0) on every new hkx [code, game]:
  register the hkRelArray PTCH entries (else crash exe+0x1A11B59) and transplant the TYPE section of a vanilla physics file
  with the same type table (else crash exe+0x182AC83). The same audit applies to new map collision hkx.
- A creature without foot IK: NpcParam `isUnduration 0`, or the body tilts from one contact normal and jitters [code].

## 4. Behaviour graph, donor, slots, variants

- No NR graph has a flight locomotion state: flight is authored inside attack / event clips [data].
- Donors that worked in game: **c2130** Morgott (humanoid; 41 attack slots, 19 single event slots, generic hks); **c4510** Ancient
  Dragon (quadruped winged; idle 0/20, walk 2000/2001, run 2100, turns 5000-5003, damage 8060, stance break 8700, death
  10000/10001, attacks 3000-3038 with gaps 3018/3020/3035/3039, single event slots 20000/1/2/10/19/20/25/26, loop event slots
  30000/5/10/19/25/26; 30011 is a single-shot state a port appended) [data, game].
- behbnd: 7000300 project, 7000400 `Characters\c<chr>.hkx`, 7000500 `Behaviors\c<chr>.hkx` wrapper, 7000501 `Behaviors\c9997.hkx`
  (the real graph, content differs per donor). Copy c9997 verbatim from the donor and rename the wrappers; in `Characters` set
  the look-at twist bones, clear foot / hand IK, RefTwistEnable 0; in `Behaviors\<id>` disable IK modifiers, GetHandleOnBone -1;
  ship `action/script/c<chr>.hks` (generic = c2130's; c4510 has its own) [game].
- **The graph plays only its own states.** A new animation id does nothing until it reaches a slot: reuse a donor event slot,
  or append a `W_Event<id>` state with a small graph patch (append-only, with a tagfile writer that keeps the type table - HKLib
  cannot read NR's c9997 because CustomManualSelectorGenerator has an extra `isBasePoseAnim` field) [game].
- EMEVD `Force Animation Playback` starts only animations with a `W_Event<id>` transition. Damage states (8060, 8700: only
  `W_SABreak` / `W_DamageExtraLarge`) cannot be forced: copy their timeline into an event slot that imports their clip [game].
- **Animation-offset variants**: a SpEffect with `animIdOffset` N x 1,000,000 makes the engine play `aNNN_xxxxxx`, but ONLY if
  that animation's selector node (CustomManualSelectorGenerator, offsetType 15) has a clip leaf named `aNNN_xxxxxx`; without
  the leaf the base clip and base TAE play silently [game]. A TAE entry that imports the base clip is enough for the data. Use
  variants for power / element sets, distance variants of travel clips, mirrored chains. Diff a variant timeline row by row
  against its base before switching it on (never-played variants drift) [data].
- In-arena replacement: list the animation ids the vanilla arena script forces (e.g. 20029 / 30029 at fight start); they must
  exist in your TAE and be harmless (a donor 20029 was "fade out + invulnerable + no lock") [game].

## 5. Clips: resample, root motion, encoding, limits

- NR clips: spline-compressed Havok 2018.1 tagfiles at **30 fps**. From 60 fps take frame 2k without interpolation; duration =
  (frames - 1) / 30. ThreeComp40 rotation, 16-bit translation, keep scale tracks; blocks <= 256 frames, block b covers b x 255
  .. b x 255 + 255 [data].
- Use a fixed encoder: the soulstruct packer misses 4-byte alignment after an odd animated scale track, writes a near-identity
  constant quaternion without its flag, and its decoder splits at 256 instead of 255.
- Root motion lives in `hkaDefaultAnimatedReferenceFrame`: one (x, y, z, yaw) sample per frame, first = 0, yaw about +Y, positive
  = right turn, may exceed pi. Pelvis stays at the horizontal origin; travel and yaw go into the reference frame [game].
- Vertical travel (take-off, hover) baked into the body worked; stage-anchored source motions (cutscene coordinates, 15-155 m
  inside the bone tracks) must be re-anchored. Idle / loop clips with mm sway: bake into the body, no reference frame [data].
- **CLIP LENGTH RULE [game]**: keep every root-motion clip within 29.7 s / 892 reference samples (largest known good); frame
  count alone is not the limit (a 23.5 s clip with 1,413 frames / 707 samples played). A 1359-sample / 45 s clip made the actor
  turn by itself; splitting it fixed it. Split long chains into two slots (or slot + variant) with the second part forced at a
  scripted time. List clip lengths after every build. Stationary event clips without travel ran up to ~47 s (solo and co-op).
  Details: skill `nightreign-boss-port` `animation.md` 4.
- Measure root motion as the game reads it (decode the INSTALLED hkx) before blaming the engine. When every engine turn is
  frozen and the actor still turns, it is the clip's root motion. A source root yaw can be pure bookkeeping (body already
  turned); dropping it flips everything after it [data, game].
- Rebuild the source's own motion chain rather than stitching generic loops (a generic glide loop made a fast take-off slow) [game].
- anibnd layouts that load: NR native (skeleton 1000000, TAE 3000000, compendium 7000000; animation member = 1000000000 + group
  x 1000000 + number) and ER-port (skeleton 4000000, TAE 5000000, `_div00`) [game].
- Store a clip once and let other TAE entries import it; before replacing an hkx list every TAE entry that imports it (a death
  froze because the death entries imported a replaced clip) [game].

## 6. TAE rules

- Start from the donor's TAE so every name the graph references resolves; map unmapped names to idle; keep only control
  events (jump tables, blend, turn speed, cancel windows), delete the donor's attacks / bullets / status SpEffects / FX / sounds /
  invulnerability; scale times to the new clip length. Write with AsmTool or own tools on Smithbox `TAE.Template.NR.xml` [game].
  Keep the donor's generic state SpEffects that vanilla uses (5980 over attacks, 14895 over death / stance break, the 8700
  stance-break set) unless the tester objects [game].
- Event types (Smithbox NR names) [data]: 0 jump table; 1 attack (judge at byte 8 -> BehaviorParam -> AtkParam_Npc); 2 bullet;
  67 SpEffect; 96 FX; 129 sound (`play_c<id>`); 193 opacity fade; 224 Set Turn Speed; 233 draw mask; 500 per-part hit mask;
  700 twist; 760 root-motion multiplier toward the target (displacement = clamp(distance - arrive, min, max)) [data, inferred].
- Jump tables [data]: JT7 Disable Turning, JT8 invulnerable, JT12 Death State, JT24 super armour, JT27 / JT51 / JT113 gravity /
  fall / height in flight, JT132 flight state bit [code], JT39 / JT50 collision / hurtbox off, JT49 lock-on off, JT95 shadow off;
  AI windows JT23, JT86 (next attack may cancel), JT78 / JT79 (move / turn may cancel).
- **Heading hold, vanilla way [game]**: 224 = 0 plus JT7 over the whole attack clip; turn windows (224 > 0) only where the source
  creature really rotates (its turn‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ speed / angle data). Wide engine turn windows make the body rotate without a turn clip
  ("sliding"). For AI tracking 0.01 is not the vanilla way to freeze (use JT7); inside EMEVD Rotate-driven clips a rate of 0
  becomes 90 deg/s, so freeze those with a small positive rate (0.01) [code, game].
- **Turn-rate semantics [code, game]**: no 224 row = NpcParam default turn rate (5 deg/s for one ported boss), not 90 (a native audit
  reads 90 for explicit turns without a row: give every Rotate-started clip an explicit row); inside the
  EMEVD Rotate controller a rate <= 0 becomes 90 deg/s. One Rotate request per actor (a new one replaces it; it can survive a
  following forced animation). Aim Rotate at points hundreds of metres away. Never rely on authored root yaw right after a
  Rotate-driven clip.
- In-place turns: the AI plays turn clips 5000-5003 (source turn motions) through the common hks ExecTurn when the target is
  outside +-45 deg, instead of engine spin [game].
- AI windows (JT86 / JT23) after the full source move at its release point. Vanilla: JT86 never before the last attack / bullet,
  JT23 never after JT86. "Last hit + 0.6 s" cut long moves in half [game].
- Idle heartbeat: a short inert SpEffect (~0.2-0.3 s) pulsed by TAE 67 in idle / locomotion / turn clips; marker SpEffects on
  reaction clips (8060 / 8500 / 8550 / 8700) so scripts know a reaction runs [game].
- **Aimed multi-shot moves need re-aim windows between shots** (REFINES the heading hold): bullets aim at the target only inside
  the Bullet's `lockShootLimitAng` of the muzzle; with the heading held through a chain, shots left the mouth sideways. Turn
  windows (~60 deg/s) that close 0.35 s before each release and reopen 0.5 s after it, release times unchanged, took the facing
  error from 57 to 3.6 deg median [model, game]. 110 deg/s read as sliding.
- **Release events: >= 0.1 s for bullets, >= 0.05 s for markers** on every clip with a speed multiplier (a one-frame event at TAE
  608 speed 1.05 fell between frames ~5 % of the time); the first shot fires at the event start; divide source times by the clip
  speed multiplier [data]. Vanilla: 0 of 1,136 bullet events in 7 Nightlord TAEs are shorter than 0.0667 s.

## 7. Attacks and hit volumes

- Chain per event: TAE 1 / 2 -> BehaviorParam (judge convention 100 + (slot - 3000) x 10 + k; k 0-4 melee, 5-9 bullets) ->
  AtkParam_Npc / Bullet. Verify the whole chain for every event [game].
- A body-contact (0-damage) attack needs its own AttackIndex slot; a persistent attack in slot 0 blocked every melee attack
  that used slot 0 [code, game].
- Clone donor Bullet / Atk rows, then set every SpEffect slot to -1 unless wanted (a cloned fire row carried deathblight) [data].
- Hit sizes: start from the source's own volumes (MHW `em###.col` radii); check against what the effect shows and against the
  radius vanilla pairs with the donor effect (donor effects are often smaller). Accepted: melee = source radii, projectiles /
  impacts x1.2, effects unscaled [game].
- A volume between helper bones can be full size from frame 0 while the visible effect still grows: sample the pose over time;
  for beams fire bullets along the mouth direction, stopped by the ground [game for the defect].
- Map-hit cost: attack rows >= 30 m use `mapHitType 2`, `atkObj 0` in vanilla [data]. Never keep a large melee capsule set active
  over dense (display-derived) map collision: severe frame drop; put area damage on bullets [game].
- Bullets fired from an MSB region point go opposite to character facing: region rotY 180 + FiringAngleY 180 [game].
- Bullet type 2 attachment 2 inherits the dummy's frame (a pitched mouth dummy made a fan aim up); attachment 0 keeps the dummy
  position with the actor's forward [code, game].
- No JT8 / JT132 in ordinary flight clips unless wanted (with larger capsules this let arrows hit a flyer) [game].
- Projectiles and the map (deep version `attacks_hits.md`): Bullet +0x8C is a float MAP-collision radius (-1 = the hit radius);
  0.1 on fan rays stopped low bumps from killing them [model, game]. Aim streams from the source's spawn joint (a dummy 2.0 m along
  the breath joint) [game]. `sfxPostureType` 0 on stream / beam bullets, 1 only on ground splashes [data, game]. Stationary
  growing damage spheres: `isEndlessHit 1` [game]. Bullets never hit player-only or player-proxy collision; a projectile-only
  blocker uses MSB HitFilter 16 (`nightreign-map-port` collision-traversal.md 3) [code, game]. Lowest point of every damage sphere
  <= ~0.9 m above the floor or short / crouching characters are never hit [model, game].

## 8. Flight and set-piece clips

- Flight inside clips: gravity / fall off (JT27 / JT51 / JT113), horizontal travel in root motion, height in the body [game].
- Scripted flights switch map collision and gravity off / on by EMEVD; `2004[31]` polarity is 1 = collision ON, 0 = OFF (the
  EMEDF label is wrong; the boss fell through the floor) [game].
- Where the source picks a travel distance, use distance variants (registered leaves) chosen a few frames before the request [game].
- Co-op: forced animation, Rotate and short warp act on the local copy only [code]; see `coop.md` before scripting any set piece.

## 9. Reactions, knock-down, death

- Nightlords have only 7400, 8060 (poise break), 8500 (parried), 8700 (stance break), 9000 + death; reaction clips start with
  generic impact cues at 0.0 s (8060 c999999999, 8500 c999999991, 8700 c999999986) - put those type-129 rows back [data].
- Scripted knock-down (part break, siege weapon) = an event slot whose TAE imports the source's own knock-down chain [game].
- **SpEffect 45 over every forced / scripted clip** (TAE 67 from 0 to the clip end on every entry of every event-forced chain and
  every variant; vanilla precedent c7520 20003 / 20004 / 20010-20012 / 20019 / 30005, c7540 20000, c7530 30015, every character's
  11060): without it a scripted knock-down drained the stance pool and `ExecSaBreakDamage` replaced it with 8700 / 8060 [game-MP
  symptoms, code]. **CORRECTS** the reading that JT24 protects flights and set pieces: JT24 stops ordinary flinches, not stance
  damage [inferred, code]. AI flight attacks: SpEffect 45 only over the measured airborne span. Drop the stance-break critical rows
  (SpEffect 36 + FX 600700) when no ThrowParam row has the boss's DefChrId; keep SpEffect 50 [data, game]. Deep version
  `reactions_death_phases.md`.
- Death [code: hks + graph]: HP 0 -> A10000 (DeathStartDefault) -> A10001 (DeathIdle, loop). 11010 / 11060 / 11070 are BEING
  THROWN and 11011 / 11061 / 11071 thrown-and-killed; an ordinary kill never plays them. Source death motion -> 10000, its last
  pose -> 10001.
- Vanilla Nightlord dissolve (copy vanilla event bytes): A10000 FXR 203 on dummies 960, TAE 193 fade to 0, FXR 213 at the chest
  dummy, JT12 + JT50 / JT39 / JT95 (vanilla A10000 has no JT49; lock-on off is an extra); A10001 holds opacity 0 + the same
  jump tables [game on a ported boss]. The ordinary-enemy pattern (FX 204 on dummies 960, 214 on the chest dummy, JT12 at
  impact, SpEffect 14895, no fade) also worked [game].

## 10. Effects (FXR)

- An effect must sit in a loaded ffxbnd: the character's `sfx/sfxbnd_c<SfxResBankId>`, commoneffects, or the map bank [data, game].
  A binder named after a new chr id is never requested unless SfxResBankId points at it: prove it with the me3 log [game].
- TAE 96 records must be 32 bytes: StateInfo (u16 at +16) is read unconditionally; 16-byte records read the next header and the
  effect was rejected [code].
- **Binder rule [code, game]**: FXR enumeration stops at the first member id >= 99999. Lay out FXR members 0..n-1 with
  `.ffxreslist` at 400000 + i (FfxBndNormalize); never append at max id + 1. Effect id != binder member id; keep FXR ids sorted.
- Never pick donors by name (identify donor characters through NpcName FMG). Recolour by patching only colour floats + id and
  decode-verify (FxTool2); rewritten COPIES of vanilla effects change header bytes - wrap a vanilla visual with a ProxyNode
  instead (new FXRs written with SoulsFormats render [game]).
- **CORRECTS** "dimmed clones turned out invisible": **byte copies** of vanilla FXRs render when only value slots + the id (int at
  byte offset 12) change, with a copy of the source `.ffxreslist`, in the 0..n-1 / 400000 + i layout of both binders [game]; the
  invisible ones were writer round-trips (the SoulsFormats FXR3 writer reproduced 27 of 110 FXRs of a binder byte-exactly). Rules:
  edit only float value slots in place, never counts, offsets or node links (a 2-byte unlink of a sub-emitter passed every offline
  proof and froze the game at the first spawn); hide parts by values (colour RGBA 0, model scale 0.01); never touch values that can
  divide; scan every user of an FXR (all four Bullet FX fields, TAE, fight script, MSB SFX regions, other FXRs) before editing it in
  place [game, data]. Perceived brightness lives in the HDR multipliers, not the colour; GPU-hang budget: `testing.md` 6. Deep
  version `fx_sound.md`.
- Helper emitters for EMEVD Shoot Bullet: it returns silently if the helper's actor / body / dummy is missing - an ENABLED helper at
  a safe standby point with a readiness wait + one pose frame fired, a disabled parked one never did [code, game]; a hidden aiming
  helper stayed inert in another port: aim from‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the boss AI. An enabled helper may still fire from the wrong place (dummy -1
  warps do not move it): fire patterns from the boss (`fight_script.md` 6) [log, game].
- Invisible helper characters: use a FLVER with 0 meshes as vanilla does (81 empty meshes carried 37 MB of never-drawn vertex
  data) [data].

## 11. Sounds and banks

- Banks: `sd/cs_c<NpcParam.SoundBankId>.bnk` + optional `cs_c<SoundAddBankId>.bnk`; NR has only the enus language [data, code].
  TAE 129 plays `play_c<id>`; FXR NodeSound / EmissionSound and Bullet seId play `play_s<id>` [data, game].
- **Bank rules [game]**: in HIRC every child precedes its parent (the loader keeps the status of a parent's LAST listed child,
  so a late child aborts the WHOLE bank [code]); never clone vanilla
  objects that reference state / modulator objects in other banks (a dangling reference silenced the bank); byte copies of
  vanilla attenuations / mixers; DIDX sorted (DATA 16-byte alignment is a convention: an unaligned bank played). Source Vorbis
  media copied byte for byte played fine.
- Budget the TOTAL resident custom media: banks of 10-27 MB played, a 48 MiB test bank (unreferenced padding) loaded, a 108 MB
  PCM bank stayed silent and 148 MB of custom PCM in total made a later bank fail; MO_WWISE heap 181 MiB shared by all banks
  [game, code]. Details: skill `nightreign-boss-port` `fx_sound.md` 10.
- EMEVD `Play SE(20000, 1, <id>)` played a character-bank sound (a victory jingle) [game].
- Long sounds / music: loose streamed `sd/wem/<first two digits>/<id>.wem` with an in-bank prefetch [game]. Near-SE curves are
  silent beyond ~100 m: arena-wide set-piece sounds need far curves [game]. Boss music slots: `fight_script.md` 5.
- **Hit sparks** are table-driven: NpcParam `materialSfx1/2` / `materialSfx_Weak1/2` -> HitEffectSfxConceptParam (row = material,
  columns = attacker material, two layers) -> HitEffectSfxParam (20 ids: {Slash, Blow, Thrust, Neutral} x {Normal, S, L, Sp1,
  Sp2}). The engine looks the effect up in the TARGET's `sfxbnd_c<SfxResBankId>` [game]. A donor's SfxResBankId gives the
  donor's materials (blood on an armoured boss).
- **Hit sounds** are NOT table-driven in NR (no HitEffectSeParam; vanilla enemies get them from TAE 129 in reaction clips).
  Recipe [game in another port]: private cues in the boss bank; per (visual, sound) one wrapper FXR (vanilla f000220000 layout:
  BasicNode + NodeSound + ProxyNode to the visual) in the boss binder; private concept / effect rows with small ids
  (materialSfx is u16, concept cells s16); point only the boss's materialSfx slots at them. Never edit vanilla rows / effects.

## 12. NpcParam checklist

Clone the replaced Nightlord's row (team, rewards, scaling links, defence, parts), then set: SoundBankId, SfxResBankId,
modelDispMask list, hit / collision capsules, turn default and `isUnduration`, materialSfx, part damage rates; remove donor
resident SpEffects that do not fit; ChrModelParam memory class as the Nightlords; NpcThinkParam (battleGoalID); NpcName in 4
languages. Scaling and HP: `balance.md`. Multi-actor bosses: teamType 33 like vanilla multi-actor Nightlords (7 let helpers
damage each other) [game].

## 13. Verification order

1. "Show" build first: model, idle, hurtboxes, AI battle goal 11000 (vanilla do-nothing); confirm visible, lockable, hittable,
   normal death before any move [game].
2. Crashes: Windows Application event 1001 gives the offset; bisect with stick-figure FLVER / donor files on the same base.
   Known: 0x1A11B59 / 0x182AC83 (hkx PTCH / THSH), 0x6F3EEA8 / 0x6F3EED7 (FLVER node order).
3. "Nothing changed" -> dump the INSTALLED files; the me3 log `override=` lines prove which files loaded.
4. Two near-identical sequences, one broken: make it byte-for-byte the working one first; compare plain sizes / counts early.
5. Offline models (flight distances, pose sampling, turn tables, AI windows vs content) reproduced tester reports: build one
   before guessing. Send preview renders of model / pose changes before installing.

## Unverified

TAE 233 byte meaning; weapon-trail path via AtkParam trace fields; `mapHitType 2` curing a roar hitch (inferred);
GameSystemCommonParam auto-turn selectors 26001-26031 used by Rotate with anim -1; which MHW flags2 bit marks mirrored aliases
(bit 0 vs 0x10); whether the clip limit is ~30 s or ~1,024 reference samples; > 256 weighted bones in a port; whether JT7 stops
an EMEVD Rotate; whether a missing 224 row inside a Rotate means the NpcParam rate or 90 deg/s; which of fixed dummy / endless
hit / no carrier made an impact circle hit; why one cross-binder copy of a vanilla ground-fire FX never rendered; FXR property
meanings beyond the value slots used.
