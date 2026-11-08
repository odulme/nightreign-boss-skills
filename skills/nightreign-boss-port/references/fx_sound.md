# Effects, sounds, hit sparks, hit sounds, brightness, readability, GPU budget

Tags as in `SKILL.md`. Pipeline stage S6 (`boss_pipeline.md`); look at each changed move from the debug panel with a source
reference picture beside the screenshot (`debug_panel.md` 7). Same-family FXR / FSB conversion: `ds3-nightreign-port` (`effects.md`, `audio_music.md`). Boss music
slots and the music switch: `nightreign-nightlord-replace` `fight_script.md` ("Start, health bar, name, music").

## 1. Convert or borrow

| situation | what worked |
|---|---|
| same engine family | convert the source FXR 1:1 (DS3: GPU trail length / 30) [game] |
| foreign engine particle effects (MHW efx, Relink est) | NR donor effects chosen with the tester, recoloured; source effects only as a look reference. Rebuilt Relink casts rendered but were rejected ("too poor"); the recoloured Heolstor gathering effect was approved [game] |
| flat art (magic circles, seals, sigils, rings) | new FXR shell carrying the SOURCE texture [game] |
| large flat ground art that must follow terrain | model particles (FXR action 605 + an sfx FLVER) instead of billboards [game] |

Never rebuild or flatten a native FXR graph: reuse it whole, adapt around it (owner bullets: count, speed, angles, interval)
and edit inside it **only float value slots in place** (renderer size constants x3, spark interval 0.033 -> 0.2 s, a LOD branch
forced) [game].

**FXR rule (corrected: "decode-equivalence + an inverse-edit check proves an edit" holds for value slots only)**: never change counts,
offsets or node links. Unlinking a sub-emitter (one container's effect count and child-container count 1 -> 0, 2 bytes, to drop two
ribbon tracers) passed every offline proof (decoded tree = original minus the subtree; inverse edit byte-exact) and **froze the game at
the first spawn of that effect**; the header's flat section tables (container / effect / action totals) no longer matched the tree
[game; cause inferred]. Hide parts by values instead: colour constant RGBA -> 0,0,0,0 (no light in additive, transparent in alpha)
[game: streak gone, no crash]; model emitters (RichModel rock slabs) -> particle scale 0.01 [game]. Never touch values that can divide
(widths, segment duration / count). 19-57 value-slot edits per FXR across six FXRs and two binders were fine [game]. Proof procedure:
section 11.

## 2. Choosing and auditing donors

- The tester names vanilla moves by their look ("Heolstor's purple gathering", "the flying dragon's fireball"). Map a named
  move to an id: NpcName FMG -> chr id; the vanilla TAE 96 event or Bullet `sfxId` that plays it is the evidence; judge the look
  from the FXR (colour keys, textures, size / life of the vanilla bullet that carries it). Never pick from a bank listing: a
  "ground fire" donor was the Ancient Dragon's deathblight miasma whose bullet applied deathblight [data].
- Record per effect: vanilla enemy + attack + look (a provenance table) and keep a blacklist.
- Audit the children of every copied FXR: reference-table / action 132 child ids must resolve in a loaded binder; fixing a
  dangling child can make a hidden child appear (an unwanted long jet) [game].
- Copied FXRs keep their sound actions (action 75 -> `play_s<donor id>`): silent unless the donor's bank is loaded, audible if
  the event is in resident `cs_main`. Rebuild that sound in your own bank or null the action; repeated owners multiply the
  requests [data].
- **Byte copies of vanilla FXRs render** when only value slots + the id (int at byte offset 12) change, with a copy of the source
  `.ffxreslist`, in the 0..n-1 / 400000 + i layout of BOTH the character binder and the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ map binder [game: several rounds].
  (Corrected: the earlier "dimmed clones invisible on every attach path" were writer round-trips, not copies.) Caveat: one copy (a common
  ground-fire carpet) never showed, cause unknown - prefer FX already seen in game in this port.
- **Never round-trip a vanilla FXR through a writer**: the SoulsFormats FXR3 writer reproduced only 27 of 110 FXRs of a binder
  byte-exactly [data]. Prefer native effects with native TAE event bytes.

## 3. Which binder the game loads

- The character loader builds `sfx/sfxbnd_c%04d` from NpcParam.SfxResBankId; the map binder `sfxbnd_m<area>` is loaded with the
  map [code]. A binder named after a NEW chr id is never requested unless SfxResBankId points at it (me3 log: no `override=`
  line) [game].
- Set SfxResBankId to the binder you ship and prove it with the me3 log; until proven, also ship the effects byte-identical in the
  arena's map binder: the map binder worked as the ONLY binder for a boss's TAE 96 effects [game].
- A boss that keeps a donor's vanilla SfxResBankId must ship an override of that vanilla binder (every vanilla member
  byte-identical + yours, normalised) - also where its hit sparks are looked up (section 7).
- Binder layout: FXR members 0..n-1, `.ffxreslist` at 400000 + i (one per effect, empty when it has no texture), textures
  100000 + k, models 200000 + k. Registration stops at the first member id >= 99999 - checked even for non-FXR members, so a TPF
  sorted before your FXRs ends it (15 effects were never registered until re-slotted) [code, game].
- NR FXRs carry 0x0001 at byte 4: clear it before reading with SoulsFormats and restore on write; new SoulsFormats-written FXRs
  render (the "full rewrite" problem applies to rewritten COPIES of vanilla effects) [data, game].
- Reslist model lines `s#####.sib` + `s#####_a.tif` work [game].

## 4. Recolour and variants

- Patch colour floats + the id in place and decode-verify that exactly the intended property changed; keep pale tints with a
  threshold; never tint a Distortion (action 607) multiplier (it drew "a filled box per particle"; restoring the native white
  keys fixed it) [game].
- Per-phase colour sets: the strong / medium / base timelines (`aNNN_` variants) differ only in judge / SpEffect / FX ids
  (e.g. blue = orange id + 10); the game selects them only with registered leaves [game: blue fire appeared after the leaves].
- Without a recoloured version of a large effect: use a smaller one of the right colour at twice the rate [data].
- Tiled copies of a breath: strip extra radial blur (608), distortion (607) and point lights (609); keep one mouth light [data].

## 5. Direction, attachment, size

- Bullet type 2 attachment 2 inherits the dummy's frame: a mouth dummy pitched +27 deg made a fan "aim up"; attachment 0 keeps
  the dummy position with the actor's forward (local -Z) and fixed it [code, game]. TAE 96 flag "ignore dummy angle" levels the
  effect to world up, keeps yaw [code].
- FX +Z = dummy forward (model effects may use X = forward: check the vanilla user) [data].
- Effect size vs hit size: `attacks_hits.md` 5. Billboard size (action 604) behaves like a half extent [inferred].

## 6. Emitters, helpers, performance

- Visual owner bullets: harmless Atk, zero contact radius, penetrate map, follow 0, finite life, no child recursion, one
  projectile per emission, deliberate interval [game]. A continuous TAE type 2 keeps consuming shootInterval while enabled; the first
  shot fires at the event start, not one interval later (`tae_turning_windows.md` 10); several concurrent judges on one AttackIndex
  work [code].
- EMEVD ShootBullet from a helper returns silently if the helper's actor, body or dummy transform is missing: a disabled helper
  parked far below never fired; an ENABLED helper at a safe standby point with a readiness wait + one pose frame did [code, game].
  But an enabled helper that fires is not one that fires from the right place: `Warp ... Copy Floor` with dummy -1 never moved an
  invisible helper, and pattern rows were laid at its parking spot for many builds - log the helper's position, or fire patterns from
  the boss (`attacks_hits.md` 4.6) [game]. A hidden aiming helper stayed inert in another port: aim from the boss AI instead [game].
- `DeleteMapSFX(id, 1)` deletes only the root; infinite-life particles stay: follow with a full delete [game].
- Before blaming FX for a frame drop, audit melee capsules (`attacks_hits.md` 7).

## 7. Hit sparks and hit sounds

- Sparks are table-driven: NpcParam `materialSfx1 / 2` (normal parts), `materialSfx_Weak1 / 2` -> HitEffectSfxConceptParam (row =
  material; columns by ATTACKER material, two layers) -> HitEffectSfxParam (20 ids {Slash, Blow, Thrust, Neutral} x {Normal, S,
  L, Sp1, Sp2} by AtkParam atkAttribute / atkPow_forSfx); effects in commoneffects. The engine looks the effect up in the
  TARGET's own binder [game]. A donor's materials give the donor's sparks (blood on an armoured boss).
- Hit sounds are NOT table-driven in NR (no HitEffectSeParam; materialSe only drives floor switches). Vanilla Nightlords are silent
  on light hits too and sound only on 8060 / 8500 / 8700 (generic cues c999999999 / c999999991 / c999999986 at 0.0 s - put them
  back when you rebuild those clips); ordinary enemies get sounds from per-hit flinch TAEs [data].
- Recipe [game in a DS3 port]: cues in the boss's own bank; per (visual, sound) one wrapper FXR (vanilla f000220000 layout:
  BasicNode + NodeSound + ProxyNode to the vanilla spark), private small ids, packed into the boss's binder; private concept /
  effect rows with SMALL ids (materialSfx u16, concept cells s16); point only the boss's materialSfx fields at them. Never edit
  vanilla rows or effects. Whitelist the private ranges in any pack merge.
- Material choices: armoured / supernatural body = clone of the final-form Heolstor concept (steel sparks, violet bloom); metal
  parts = clone of HeavyIron; scaled dragons keep the Ancient Dragon / flying dragon scale set [data]. Armour sound set by
  atkPow (light S / M, heavy L / XL) and attribute (slash = plate clank + impact, thrust = sharp + impact, strike lower
  pitch, steel parts add a blade ting), ~+6 dB over swings [data, built].

## 8. Sound banks [game]

- Source media: MHW Wwise 2016 Vorbis wems and Relink Wwise 2021 Vorbis copy into NR v135 banks byte for byte (Relink: strip
  `cue ` / `LIST` chunks); multichannel music is downmixed by the engine. DS3 FMOD: decode -> Wwise IMA ADPCM.
- Shape (copied from a proven‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ bank): root actor-mixer -> character mixer (clone of a vanilla boss's) -> voice mixer (with a
  playback limit) and near / far / arena sub-mixers. Root: either a private actor-mixer (own id, parent 0, vanilla bus
  override) or an in-bank copy of the vanilla root id whose ONLY child is your mixer - both played. Only object types present in
  a proven bank; every object a structural twin of a proven one.
- NO reference may leave the bank: cloned vanilla FX-sound containers pointing at state / modulator objects elsewhere silenced
  the whole bank; rebuild each layer as your own random container (volume, pitch, random pitch, HPF, loop, delay, limit, stop
  fade). Attenuations: byte copies of vanilla attenuations, only the id changed.
- Order: every child before its parent (5 containers appended after their mixer killed all 352 events; moving 10 records fixed
  it). Strictly, the loader keeps the status of a parent's LAST listed child, so a late child can abort the read [code] -
  always write children first and check the order on the raw HIRC.
- Attenuation classes: near (boss SE; silent at >= 100 m), voice (~130 m), far (300 m), arena (600 m, nearly flat) for set-piece
  and arena-wide sounds; trims keep 5 m levels equal [game: near sounds were unheard at 50-185 m].
- Events: `play_c<id>` / `stop_c<id>` for every sound, `play_s` / `stop_s` aliases for FXR action 75 and Bullet seId; id = FNV-1
  32 of the lower-case name (`scripts/wwise_fnv.py`).
- Flatten source events: follow play actions, ignore stop / set-prop / set-state (source-internal ducking), sum delays, choose
  default switch branches (ground material -> soil), keep step sequences in lockstep, fold ancestor mixer volumes.
- Voice: global limit 1, equal-priority newcomers dropped (priorities shout < key line < death); probabilities with Silence entries.
- Loudness: match a vanilla boss (container level, peak cap ~+4.5 dB) [data].
- Re-check the bank after every edit with an independent parser.

## 9. Timeline -> TAE 129

- Time = source frame on the clip clock; shift / scale to the slot; drop rows outside the played window; loops once.
- Play mode 0 for one-shots (mode 1 on 0.1 s tell events clipped a one-shot to ~24 % of its energy); mode 1 for loops / sounds
  that must stop at the event end [data].
- Dummy mapping: the source request's joint -> NR dummy (head -> mouth, limbs -> foot dummies, wings, tail, FX sounds on the
  FX dummy); MHW collision events on the feet = footsteps (soil); skip them if the donor graph plays its own steps.
- Generic kill sound: type 129 id 999999997 at the start of every death clip; engine-generic ids >= 999999000 stay unchanged.
- Scale of a big boss: ~4,200 TAE 129 rows -> ~100 distinct events; 140 sounds / 400 media / 20 MB in memory played.

## 10. Budget, streaming, extra banks

- Proven: banks of 10-27 MB play; a 48 MiB bank (padding nobody references) loaded with normal sounds; a 108 MB PCM bank stayed
  silent; 148 MB of custom PCM in total made a later bank fail, 43 MB of ADPCM played. MO_WWISE heap is 181 MiB shared by all
  banks (vanilla m19 peak ~80-86 MB, cs_main 55 MB resident) [code, game]. Keep the TOTAL resident custom media of one fight
  near or below ~60 MB; compressed codecs (Vorbis copies, ADPCM).
- Long sounds / music: loose streamed `sd/wem/<first two digits>/<id>.wem` with an in-bank prefetch (header + seek table + setup +
  first packets) [game].
- `SoundAddBankId` = a second bank (vanilla bosses use two); keep `SoundBankId` where an engine sound comes from it [game].
- EMEVD `Play SE(20000, 1, <id>)` played a character-bank sound (a victory jingle) [game].

## 11. FXR value-slot editing: proof, users, working property names

- **Find each slot by decoding a trial write; then prove**: every target slot found; the decoded file = the intended document; the
  skeleton (containers / effects / actions / links) identical; bytes differ only inside the target slots; the inverse edit restores the
  source; every other member of the binder byte-identical and decodable; an independent re-implementation of the plan matches leaf by
  leaf [data]. Edit both binders that carry a copy (character and map) identically.
- **Scan every user before editing an FXR in place**: all four Bullet FX fields (`sfxId_Bullet / Hit / Flick / ForceErase`) across the
  regulation, every TAE FX event, the fight script, MSB SFX regions, other FXRs' references. A mine blast FX was also the hit burst of ~30
  fireball rows and a finisher: give each family its own copy and repoint the `sfxId_Bullet` cells. A new FXR id must not occur as an int
  inside any FXR [data].
- **Shorten an effect** by scaling its life AND every age-curve key time by the same factor (width, colour, colour3, flipbook, speed);
  leave key tangents alone [data; game OK].
- **Working property names for vanilla NR emitters** (consistent across rounds, reproduced a screenshot, still [inferred]): action 60
  P1[1] speed curve; action 131 P1[0] start speed, P1[1] scale; Properties2[0] rgbMultiplier, Properties2[1] alphaMultiplier; Fields2[4]
  bloom on, Fields2[8] bloom strength; point light = (diffuse + specular) x multiplier; QuadLine colour is HDR (~50); point-emitter
  direction value 1 = the effect's up axis (252 of 260 vanilla "debris fountains" use it; narrowed bursts went up in game).
- **Identify an emitter's role by its texture before cutting**: vanilla common explosion family (800140): s21001 lit smoke flipbook
  (+ s21002 normal), s31051 fire flipbook (late frames turn to dark smoke from ~0.7 s), s31421 additive sparks, s43031 stone shards;
  warnings s10011 soft glow, s60101 crack decal, s33015 embers; the lava-rock warning family 675101 / 675103 adds a RichModel rock s84161.
  MHW's warning is only a glowing crack decal; keep the decal <= 0.9 x the blast width [data; game].

## 12. Brightness, readability and GPU budget

- **Perceived brightness comes from the HDR multipliers, not the colour**: billboard light = texture x colour1 x colour3 x rgbMultiplier;
  coverage = alpha x alphaMultiplier clamped to 1; bloom on top; values 20-60 sit at the top of the tone curve. RGB x0.75 changed
  perceived brightness 0-12 % and the tester saw no change [game, model]. Typical vanilla warning / explosion values [data]: glow disc
  rgbMul 5 / alphaMul 2 (inner 20 % opaque), lava crack 50 / 25, embers 50, spark QuadLines 50 x bloom 0.1, fire flipbook colour3 2.5 x
  rgbMul 2.5, sparks 15, point light x10.
- **Brightness rule**: bring HDR peaks to ~1-3 and remove fully opaque cores (alphaMul > 1); ship presets (mild / soft / half / strong)
  behind a builder flag and expect one tuning round: "half" (~50 %) was "a bit dark", "soft" (~60 % of the modelled perceived brightness)
  was accepted [game]. QuadLines glare through the bloom halo: HDR 37.5 -> 3 kept 75-94 % of the core, removed 96 % of the halo [model].
  Leave sizes, timings, counts and rates alone in a brightness pass.
- **Find what blocks the view before cutting**: two rounds cut the s21001 smoke (puffs / 2, alpha x0.5 / x0.3, size x0.8 / x0.7) and the
  view stayed blocked; the blocker was the billowing fire flipbook - 6 sprites (life 1.5 s, spread 112.5 deg from up, 3.1 -> 11.6 m) + a
  3.9 -> 14.8 m core drifting randomly + sparks to 9.5 m [data, game]. Ask for a screenshot plus a source reference picture and model which
  emitter‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ covers the screen (screen-coverage model, `diagnostics.md` 8).
- **Upward-jet recipe (value edits only)** [game passed]: fire main spread 112.5 -> 10 deg, scale x0.42, life + age curves x0.67, alpha
  x0.85; core spread 6 deg, speed x2.2, scale x0.32; smoke spread 12 deg, scale x0.55; sparks spread 25 deg, start speed 11.4 -> 15.4 m/s,
  scale x0.45; emission at t = 0 unchanged (the hit moment still reads); blast bullets `sfxPostureType 2` (upright). Peak screen cover at
  3 m 81 -> 27 %, a row of 9 blasts 100 -> 23 %, time with the boss >= 50 % hidden 0.8 -> 0 s, quad fill -81 % [model]. Keep the warning
  glow marking the whole hit radius when the column is narrower than the hit.
- Smoke per blast [model]: vanilla explosion upper-bound fill 456 m2, smoke alone 144 m2; a row of 9 mines' smoke 1,297 -> 414 m2 after
  the cut.
- **GPU-timeout budget** (corrected: the trigger is dense blended particle / trail load, not textures - slimming textures did not help)
  [game-MP]: a GPU reset reported DXGI_ERROR_DEVICE_HUNG, no page fault / out-of-bounds, hung inside the transparent / effect pass at a
  steady 60 fps at the densest alpha-blended moment (~230 FX alive, up to ~1,500 particles per laser, tracer ribbons, a point light per
  laser); sparkle max 1000 -> 40 (-74 % FX load) was followed by crash-free co-op tests. **Rule for "denser without more crash risk"**:
  time-aligned quad fill <= the heaviest move that already ships; particles <= 1.5x; FX alive not higher; no new point-light /
  distortion / radial-blur / tracer / GPU-particle node; FXR changes only as byte copies with in-place values [design; game]. Reference
  [model]: heaviest shipped move ~153k m2 upper-bound fill and ~18-20k particles; vanilla Heolstor ~1,260 FX alive, p99.9 67.5k
  particles per FX instance. Diagnosis tooling (DRED, asset audit, collector): `diagnostics.md` 4.
- **Count lights per instance in map-region FX**: 96 of a breath's 99 point lights came from one ground-field FX (2 lights x 48 regions),
  the cheapest cut if a crash recurs [data].
- Identical FX on identical spokes loop visually (`attacks_hits.md` 4.4); ground FX on a stationary bullet in the air may render
  nothing (`attacks_hits.md` 4.6).

## 13. Ground art on tessellated terrain

- A ground seal model floating 12.5 cm above a sand mesh showed half missing from the start: the arena's sand material has GPU
  tessellation, which displaces the surface above the base mesh [data, inferred]. Lift such models ~0.35 m or place them on a
  non-tessellated surface; verify with an MSB round-trip that only the Y values changed [data].
- Large flat ground art that must follow terrain: model particles (section 1).

## Unverified

FXR property meanings of section 11; why a cross-binder copy of a vanilla carpet FX never rendered; why ground FX born from an expired
stationary hold do not render; the GPU hang location in the effect pass (DRED order) [inferred]; stop events posted when a wrapper /
FXR ends; a fire-set change in mid-animation switching the timeline; long voice lines
streamed from a character bank; first-loaded-bank-wins for duplicate event ids; vanilla-named target binder override for hit
sparks on a boss; sound distance fields (50 vs 200) on NpcParam.
