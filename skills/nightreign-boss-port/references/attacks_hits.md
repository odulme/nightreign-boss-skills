# Attacks: chain, ids, volumes, bullets, area patterns, collision-aware hits, sizing, dodge review, performance

Tags as in `SKILL.md`. Pipeline stage S5 (`boss_pipeline.md`); test each move from the debug panel (`debug_panel.md` 7). Damage
numbers: `params_balance.md`. Effects of attacks: `fx_sound.md`. Bullet field names follow Smithbox's NR paramdef; `+0xNN` are byte
offsets inside BulletParam rows.

## 1. The chain (verify it end to end for every event) [game]

TAE type 1 / 2 (AttackIndex, judge) -> BehaviorParam `200000000 + behaviorVariationId x 1000 + judge` (refType 0 AtkParam_Npc,
1 Bullet, 2 SpEffect) -> AtkParam_Npc / Bullet -> Bullet children (`HitBulletID`, interval children; no judge of their own) ->
their AtkParam rows (bullet attack rows carry no geometry). A verifier must resolve every type 1 / 2, check that every FX id
exists in a loaded binder and every sound id in a loaded bank, and refuse large melee footprints (section 7).

## 2. Id conventions (pick one, write it into the coordination file)

| scheme | blocks |
|---|---|
| humanoid port | judge = 100 + (slot - 3000) x 10 + k (k 0-4 melee, 5-9 bullets); 20xxx slots 500 + (slot - 20000) x 10 + k; later blocks 800-899 slices, 900-949 wave segments |
| dragon port | melee 100-489 = 100 + (slot - 3000) x 10 + k; projectiles in their own blocks per strength set (500 base, 600 strong, 700 medium = base + 100 per set); 800-805 utility areas (roar, winds, final burst, shocks); 990 body contact |
| both | EMEVD-cast rows in a separate band (BehaviorParam 80<chr>xxx, Bullet / Atk 8<chr>xxx); child bullets in a no-judge band; SpEffects: fight-state markers 100-199, moves 200+ of the chr band; every new band claimed in the id registry before building (`boss_pipeline.md` S0) |

## 3. Melee volumes from the source's own data

- MHW: col node capsules -> pairs of NR bone dummies; deduplicate by pair keeping the max radius; cap 16 capsules per row by
  radius x length; NR pairs repeated dummy ids ordinally (`hitN_DmyPoly1[k]` with `DmyPoly2[k]`, up to 8) [data, game].
- Relink: shapes 0 sphere, 1 capsule (r, half length), 2 box (HALF extents), 4 cylinder; PartsNo -1 root / weapon bones /
  ground anchor; NR position = (x, y + hover + root height, -z). Half-extent proof: blades lie inside the boxes, a line attack
  starts exactly 1 m ahead, ground cracks reach the floor only as half extents [data].
- One source swing is often 2-3 boxes: a union capsule hits the far side 0.12-0.19 s early ("hit while the sword was far
  away"). Split per slice (3-5 capsules per sector, sectors bounded by bisectors between neighbours) with ZERO standing-area
  overlap, so a swing hits at most once; slice window = 25-95 % quantile of blade arrival, min 1/30 s; single-frame source hits
  -> 0.1 s [game].
- Hits on a weapon: capsule between hilt and tip dummies on the weapon bone (100 % fit); fixed-point capsules need the weapon
  animation re-timed to sweep through them [game]. Self-centred bursts: a vertical capsule between two body dummies [game].
- A judge window covers only the VISIBLE strike: a 40 m projection left active for 3 s before the sweep caused invisible hits
  ("can't dodge") [game].
- De-dup rules (vanilla evidence): same AttackIndex + same judge + continuous = one hit; the same judge after a 1-frame gap
  re-hits; a new judge re-hits [data].
- Body contact: its own AttackIndex (e.g. 6) with 0 damage over every attack and locomotion clip; never AttackIndex 0 (a
  persistent attack there blocked every melee attack using 0); never enlarge it (pushes players off the legs) [code, game].

## 4. Area damage on bullets: streams, circles, projectiles, fans, mines, breaths

General: beams, streams, fans, sweeps, waves and anything >= ~30 m or > 1,000 m2 for > 0.5 s carry their damage on invisible
bullets, never on large melee capsules (section 7). Record the source data for each (spawn joint, shell life, radius and growth,
speed, re-hit interval, placement rule) in S1 (`survey_and_extraction.md` 6).

### 4.1 Beams and breath streams

- A capsule between helper bones covered 50 m from frame 0 while the mouth still pointed at the feet: use invisible damage bullets
  from a dummy, same speed / reach / interval as the visible flame (e.g. 100 m/s x 0.5 s every 0.08 s), stopped by the ground, one hit
  per target per breath (shared hit record), heading held with JT7 [game].
- **Aim every stream from the source's spawn joint, not the head bone** (corrected: "from the mouth dummy"). One snake-breath joint
  points 22-80 deg down while the head points -64..+25 deg; with the beam on a head dummy its floor point was off by median 7.8 m
  (p90 17.8 m) and 26 of 117 emissions never reached the floor within 50 m ("sprays forward, does not hit in front"). A dummy 2.0 m
  along the breath joint (= the source spawn offset): median 0.3 m, p90 0.6 m [model; game "great"]. Same fix elsewhere: a straight
  beam 1.55 -> 0.29 m, an under-belly stream floor point 6.1 -> 4.67 m (= source) [model, game]. Check every stream with FK: floor
  intersection over clip time vs the source joint.
- **End the damage beam with the source shell's life** (here 6.28 s), not with the mouth effect (7.5 s): after the shell the joint
  lifts to horizontal and a longer beam sprays 50 m ahead. The mouth‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ flame may run to the effect end on its own [data, game].
- **`sfxPostureType` 0 (Parent) on stream / beam bullets, 1 (Global Y) only on ground splashes** (vanilla c4500: stream 4500230 = 0,
  splash 4500231 = 1). With 1 the flame FX is born upright with the bullet's yaw and its particles fly along the FX forward (FXR action
  131 speeds 17.8 / 8.9 m/s), so emitted flames kept sliding ~14 m over the floor after the bullet landed ("stray spreading flames")
  [data, model; game gone after the change].
- **Give each beam bullet a floor child**: `HitBulletID` -> stationary 0.1 s sphere (r ~2.9 m), same attack, shared hit list, 1 s
  record, no FX: the hit sits where the flame lands whatever stop rule applies [game].
- **Children with posture 1 take their yaw from the PARENT bullet**: a near-vertical carrier's small horizontal component pointed
  backward (circular mean 157 deg from forward), so every ground-flame child licked ~7 m back toward the tail [model, game]. Fixes that
  worked: fire the carrier with attachment 0 + Bullet elevation -85..-88 deg (yaw = actor forward), set `isOwnerOverrideInitAngle 1`
  on children (BulletParam +0x9c bit 6 = use the owner character's pose) [code], or use FX whose look does not depend on heading.
- **Harmless visuals where nothing is drawn**: a stream that hurts where no explosion is drawn reads as unfair; make it visual-only
  (neutral all-zero AtkParam row), let only drawn explosions hurt, and set `lockShootLimitAng 0` so the harmless flame lands on the
  source's line instead of tracking the player [model; game OK].
- Sustained streams / sweeps: gob streams r 2 -> 2.4 m, 50 m/s, life 0.6 s, every 0.06 s, 0.5 s shared hit list; +0x8C (section 4.4)
  0.1 m keeps low-mouth gobs alive near the ground while the character radius stays [code].
- Ground blasts after a stream: isolated downward detector bullets from the same dummy and clock (moving stream projectiles carried the
  blast away; dummies on animated bones went under the floor); for "in front of the boss" use a fixed dummy not attached to an animated
  bone (`skeleton_model.md` 6) [game].

### 4.2 Impact / under-belly damage circles (took 7 rounds in one port)

- **Fire the circle straight from a TAE bullet event on a fixed floor dummy** (fixed SFX node, Y 0.3) as a stationary growing sphere;
  never as the child of a carrier that must first reach the floor. Source reference (an MHW impact shell): R 1 -> 10 m in 20 frames,
  +-2 m tall, life 2.58 s [data].
- **`isEndlessHit 1` on stationary growing damage spheres** (vanilla c4500 4501202: r 0.1 -> 5 m in 1 s, 0.4 s hit record; only ~30 % of
  vanilla stationary growing bullets set it) and keep the stream's shared hit list (one hit per 0.5 s). The build with fixed dummy + TAE
  event + endless hit passed; earlier carrier / endless-0 builds gave no hit the tester noticed; which change was decisive was never
  isolated [game].
- **Size against the pose, not the root**: a rearing dragon's stream lands only ~2.6 m in front of the hind feet, so a 10 m ring centred
  there reached 5 m along the tail ("hits at the tail"). The tester finally chose the source size (12 m incl. the visible spread). Expose
  radius, centre, start and life as builder flags [model, game].
- **Build the visible spread only from FX already seen in game in this port**: a copy of a vanilla common ground-fire carpet never showed
  in three rounds (cause unknown); what showed: 24 flat spoke bullets (15 deg apart +-3, 15 m/s, map off, no gravity, 0.467 s) dropping
  already-proven ground flames every 0.133 s -> rings at 2 / 4 / 6 m licking outward; ~97 bullets and ~3.7k particles per breath [game].
  Speed-0 copies of a flipbook flame stand as isolated upright columns [game].
- A visible dev marker on an invisible damage volume while building (`diagnostics.md` 7).

### 4.3 Projectiles and multi-shot moves

- Fireballs: ~60 m/s straight, impact child growing r -> 2r in 0.2 s; standing blast life <= 0.2 s so a roll works [data].
- Multi-shot chains: re-aim windows between shots (`tae_turning_windows.md` 4) - bullets aim only inside `lockShootLimitAng`.
- Visible fireball rays at 50 m/s every 0.5 s leave 25 m gaps ("one flame repeated"): emit visual rays every 0.15 s (peak bullets
  typical 96 -> 187) and keep the damage rows unchanged [game].
- Shockwave lines: N segments advancing (e.g. 10 x 4 m every 7/60 s, r 1.3); shrink neighbouring segment ends so a wave hits once;
  freeze turning during the hits [game].
- Vanilla patterns worth reusing [game for appearance]: Harmonia ring chain (expanding rings), Adel random rain, meteor = invisible
  slide -> ground warning -> lift 20 m -> fall, Heolstor burst (0.3 s TAE bullet event, interval 0.1 s, shared hit record).
- Weapon trails on helpers: AtkParam `traceSfxId0` with trace dummies 900 / 901 and native commoneffects traces [game].

### 4.4 Fans and collision-aware hits (terrain, pillars, cover)

**Landing rule** [code]: a map hit ends a bullet only if `isPenetrateMap 0`; a character hit ends it only if `isPenetrateChr 0`,
guarded or not; a guarded ("flicked") hit only plays `sfxId_Flick` / `seId_Flick` and still applies; the force-erase flag always ends
it; no field ends a bullet only on a guarded hit; with `isHitBothTeam 0` the boss and its helpers never block their own bullets;
`dmgCalcSide` is 0 on every vanilla row (not a switch).

- **Bullet +0x8C is a float MAP-collision radius; -1 = use the hit radius** (now proven on rays too). Fan rays at 2.55-2.88 m height with
  r 1.4 touched anything taller than ~1.2-1.5 m, r 2.5 damage spheres touched the floor wherever it rose a few cm: median reach 7.5 m,
  85 % of rays stopped before 45 m. With +0x8C = 0.1: median 45 m, 0 % stopped by low bumps; only walls / platforms / the arena edge stop
  it [model; game: "small bumps block it" gone]. MHW also stops fan lines by the line centre (`mRayCastID`, `mCheckWallEndOffset`) [data].
- **Visual and damage rays as one family**: same directions, same INITIAL radius, same map rule, so the drawn flame ends where the damage
  ends; `bulletSfxDeleteType_byHit 1` for a crisp end [game].
- **Bullets never hit player-only or player-proxy collision** [code: native layer pairing]: bullet filters 97-103 pair only with map
  layers 54 / 57 / 61 / 62 / 63; player-only asset carriers (collisionType 11) are layers 67-69; MSB HitFilter 22 (player wall) = layer
  59. To make an obstacle stop projectiles but not movement, add a projectile-only map collision copy with **MSB HitFilter 16 (-> layer
  57**, which pairs only with 97 / 98 / 100 / 102 / 103 / 114 / 116 / 117 - not player layers 2 / 21, not NPC layers 9 / 10 / 24 / 25),
  extruded >= 5 m (ray heights) and as wide at ray height as the shadow should be (prism r 1.8 m for a ~2.4 m stump) [game: pillars
  block, players walk through]. Side effect: every map-colliding boss bullet stops there. Check the source's blockers against the
  port's collision layers: two pillars with only player-proxy collision let the fan pass [data, game].
- **A shadow exists only if the ray's damage radius is close to the blocker width** [model]: 17 rays at r 3.6 m reach 2-4 m behind any
  blocker (no shadow); r 2.5 still hit 56 % of a 1.2 m stump's shadow.
- **Accepted fan** (corrected: was "damage rays one sphere each r 2.5-3 m every 0.15 s"): 33 rays x 3 deg (+-48 deg), r 1.4 -> 1.6 m
  over the 0.9 s flight, a volley every 0.3 s, shared 0.5 s hit record, +0x8C 0.1, damage origin ~2.0 m above the floor (section 9):
  shadow 0.000, beside 0.978, open 1.00 [model; game accepted]. Bullet angle fields are integers -> rays in whole-degree steps [data].
- Source fan facts (MHW) [data]: 17 LINE shells (5 at r 3.0 at 0 / +-6.25 / +-12.5 deg, 6 at r 2.5, 6 at r 2.0, out to +-50 deg),
  50 m/s to 45 m, life 5.25 s, re-hit 0.5 s, plus a no-damage 2 m "check" collision node; no guard-only rule in the data.
- **Fans that look like a loop**: identical FX on identical spokes whose periodic emitters fire at bullet age 0 redraw the same picture
  every volley (repetition index 1.00) and all age-0 emissions overlap at the mouth (11x the far density) -> "looping", "mouth stronger
  than the far end". Fix: invisible parents with `lifeRandomRange` +-0.12 s and `shootAngleYMaxRandom` +-3 deg handing over
  (`HitBulletID`, launch condition 0) to child rays that carry the FX -> repetition 0.08, far / near density 1.38; a x0.3 flame copy on
  the parents fills the first 5 m [model; game accepted]. Emitted particles live on after their bullet ends: use it to join a parent's
  near flame with the child's stretch.
- **Bullet erasers** (`attachEffectType`, the bullet-vs-bullet pass of the bullet manager) [code]:

  | type | removes bullets with | effect | whose |
  |---|---|---|---|
  | 1 Force | `isHitForceMagic` | pushed aside | hostile |
  | 2 | `isHitFlare` | reflected | hostile |
  | 3 Dark Force | `isHitDarkForceMagic` | pushed aside | hostile |
  | 4 | `isHitOtherBulletForceEraseA` | erased | same owner only |
  | 5 Absorb | `isHitOtherBulletForceEraseB` | removed | hostile |

  Type 5 reach = eraser radius + the ray's INITIAL hitRadius; the absorber survives unless its own `launchConditionType` is 6.

### 4.5 "Only a guarding, standing player blocks the fan" (guard-shadow barrier)

- Every vanilla player guard animation (start / loop / end, guard walk, guard skills, guard-hit reactions 19000-19622) carries TAE 67
  SpEffect 8884190 "Guarding Accumulator" [data]; native "on successful guard" relic effects are per-passive hks, not a generic trigger.
- Chain [code, model; game: fan accepted]: event on every machine, sync off, for the own player: fight running AND
  `IF Damage Type(10000, boss, any)` AND `IF Character Has SpEffect(10000, 8884190)` in the same frame -> SpEffect copied from relic
  7033404 (stateInfo 275, dummy 900) -> BehaviorParam_PC -> launcher bullet (yaw 180, elevation 27, 20 m/s, 0.141 s = ~2.5 m back,
  1.3 m up) -> Absorb barrier (copy of 30000210: type 5, no damage, invisible, r 2.0, 0.8 s); the rays carry
  `isHitOtherBulletForceEraseB 1`. Add a "standing" test (team types 1 / 2 / 20 / 29) re-checked 2 frames later (a guard broken into a
  knock-down otherwise leaves a barrier). The guarder is hit at least one frame before absorption; shadow 1-2 m half-width at 3-6 m.
- **Side effect**: every hostile vanilla Absorb bullet erases erasable rays too (Carian Retaliation, the Golden Retaliation family, skill
  waves 30000210-30009240, relic / passive effects; ~50 player-side rows) - top candidate for "the fan did not hit the ally reviving next
  to me" [inferred, game-MP report]. Decide with the tester.

### 4.6 Delayed ground mines and pattern placement (took 7 rounds in one port)

- **Never place mines by dropping from high above to the first collision**: projectors falling from dummy Y+12 at gravity 999 put mines
  on walls, terraces and into the moat; 25-34 % of line mines ended > 1.5 m off the boss's floor [model; game 5 of 19 casts misplaced].
- **Floor rule that passed** ("very well done"): drop each mine from 1.5 m above the reference floor with gravity tuned so a flat floor is
  reached at the original time (g = 2h / t^2: 1.5 m in 0.17 s -> 103.8 m/s^2), map collision on, life 0.26 s (gives up 2.0 m below); the
  warning child gets `launchConditionType 5` = created only if the parent ended on a map hit (on life expiry the hit material is -1 and 5
  blocks the child; 776 of 964 vanilla LC-5 parents end only on map hit or expiry) [code, data]. Result: 98 % of on-floor points‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ kept,
  ~54 % of off-floor points dropped, median height error 0.2 m [model; game]. A finisher from the head dummy: cap the fall (life 0.095 s at
  g 999 = 4.5 m). `launchConditionType 0` = on landing or expiry.
- **Ground FX need a floor-contact birth**: a blast born from an expired stationary hold 0.3 m up played its sound but drew nothing; born
  on the floor contact of a falling detector it rendered [game]. Lava-crack warnings born from 0.3 m holds did render; which property
  matters is unknown - default to contact birth [inferred].
- **Do not lay patterns by warping a helper onto a player**: `Warp Character and Copy Floor(helper, 2, player, -1, player)` (dummy -1) had
  no lasting effect on an invisible helper with gravity and map hit off; it stayed at its MSB parking spot and every "through the player"
  row was laid there for many builds [log, model; game]. In 199 vanilla scripts characters are warped onto players only with a player
  dummy (210 / 220 / 13 / 36 / 900 / 200), never -1 [data]. Log the helper's position. (Refines `fx_sound.md` 6: an enabled helper that
  fires is not one that fires from the right place.)
- **Fire patterns from the boss instead**: EMEVD `Shoot Bullet(boss, T, -1, behaviour, 0, 0, 0)` at the target (T = 20000 solo; in co-op
  the slot from host-published one-hot flags, `reactions_death_phases.md` 7; 100 vanilla uses with 20000) -> invisible stationary root
  (0.02 s) -> child mover with `isOwnerOverrideInitAngle 1` and yaw = the pattern direction -> flies through the map to the pattern point
  -> floor-rule fall. Mover life = old marker time - 0.02 s (timing unchanged). Firing all roots at capture means an interrupted move still
  lays its whole row. Error <= 0.25 m from integer angle fields + up to speed / 60 per frame [code, model; game].
- **Anchor rows to the targeted player as the source does** (MHW: X +-24 m around the hunter; far line Z -12..+36 m through the hunter,
  across the boss-player line). Rows fixed 8 m in front of the boss read as "always at one place". A player-anchored row sits on the
  player's floor, not the boss's [game decision].
- **`EmittePosType 6` = above and behind the target** (meteor placement): a puddle anchored this way hung several metres up. Vanilla
  brings such bullets down with a falling child (2200410 / 415 / 420 / 423 / 425 / 427, 7600581: shootAngleXZ -90, speed 10, gravity 999,
  map collision on, child on contact). Anchor 0.09 s -> falling detector -> puddle under the target [game].
- **Sanity guards**: a "helper within 3 m of the player" guard failed every time because the helper never moved; it was removed as "the
  bug" and misplaced rows shipped for many builds. When a guard fails every time, find out what it tests first [log, game].
- BulletCreateLimit groups cap live patches (e.g. 30 lava patches) [data].

### 4.7 Full-screen breaths, shelters and certain-kill hits

- Source reference (an MHW stage breath) [data]: body shell = 140 m static sphere on the monster, motion value 500 + 500.0 in the
  fixed-damage slot (the flying fan breath 120 / 500 / 150), no element, Knock_back_Type 17, life 7.8 / 11.8 s, multi-hit Unk_16 = 1 /
  Unk_17 = 15 (re-hit every 15 frames at 60 fps [inferred]); omen MV 5; consecutive special ids 100..114 sit on the monster's signature
  attacks (probably an occlusion handler [inferred]). Distance never saves; only cover.
- **"Certain kill outside cover" as a real lethal hit from the boss** (corrected: was a flat / % max-HP loss SpEffect per machine; the
  tester chose the real hit - the % ticks gave a 1 s grace and no launch). A sphere bullet produced at the own player hit and killed but
  launched in random directions (centred on the victim) [game]. Shipped recipe: `Shoot Bullet(boss, boss, -1, <BehaviorParam refType 1>,
  0, 0, 0)` fired by each machine in a sync-off event for its own player; invisible sphere centred on the boss, radius 1 -> 230 m in
  0.575 s (400 m/s), life 0.625 s, one hit per target, passing map / characters / assets; hit and launch direction = boss -> player
  [game; game-MP: such shots hit in co-op logs]. The front needs up to ~0.3-0.6 s to arrive; the centre follows the boss if it drifts.
  Event bullets are local, which is what makes a boss-centred lethal sphere safe in co-op (it overlaps every player's copy but hits only
  the own player); first co-op test: a sheltered player beside an exposed ally must not be hit.
- **Guardable-from-the-front lethal AtkParam_Npc** [data; calibrate in game]: atkPhys 9999 (every NR guard-capable weapon / shield has
  physGuardCutRate 100: 2,317 rows), atkFire 25 as the guarded chip, atkStam 65, disableGuard 0, dmgLevel 10 ("Huge Launch Back"),
  isDisableParry 1, atkSuperArmor 999, guardAtkRate 100, mapHitType 2, atkObj 0, no SpEffect payload. `disableGuard 1` = ignore guard;
  `isDisableNoDamage 1` = ignore step i-frames (not TAE invincibility).
- **Stamina per guarded hit** = atkStam x boss staminaAttackRate (innate 7767 = 2) x Deep Night stamina rate (877671-675: 1.15 / 1.2 /
  1.3 / 1.45 / 1.5) x (1 - staminaGuardDef / 100) [community formula + data]. At L15 an average shield holds ~2 hits, a greatshield ~3,
  the best ~5, then guard break and death [model]. Whether 7767's rates apply to EMEVD-fired bullets is unproven: keep lethality either
  way, a stamina knob, and calibrate by counting blocked ticks. A guardable "certain kill" needs enough hits to break every guard.
- **What can outlast a lethal tick train** [data]: no SpEffect has `noDead`; immortality = state info 143; Revenant Immortal March
  (705000 / 705010, 15 s) outlasts an 11.5 s train; Executor beast form (707110 / 707140) may; Guardian Wings of Salvation (701510, state
  629) ~2-2.5 s; revive immunity 102160 / 102450 3.5 s; a 99 % cut bubbletear (708810) still dies. Ask the tester before cancelling other
  heroes' ultimates.
- **Per-tick script guards**: skip if the own player rides the spirit hawk (state info 603 / SpEffect 99202), is downed (team type 77;
  102180 = 99 % cut) or has HP <= 0, is inside the shelter box (when its gate flag is ON) or outside the court box; END on the fight-end
  flags [data; sim].
- **Dead ends, do not repeat** [game]: damage in a SpEffect payload whose `invocationConditionsStateChange1 = 452` was never met;
  SpEffects set on party-slot aliases 10002-10004 with effectTargetSelf / Friendly 0 (no damage). What works: own player 20000 in a
  sync-off event, damage in the attack row itself.
- **Shelters as boxes have no line of sight** (the open side of a box is safe) [data]; real cover needs per-player probes with
  `isPenetrateMap 0` (not built). A network-shared gate flag (one player closes a shelter gate) protects everyone inside; shelter tests are
  per machine and never protect another player [data].
- **Visual breath lanes stay visual-only** (atk 1, radius 0) and separate from the real hit. 100 m/s lanes with one sprite every 0.3 s read
  as puffs 30-40 m apart and 30-44 % were emitted under the floor [model]. Passed [game]: pairs per lane (`numShoot 2`,
  `shootAngleInterval 12`), yaw +-3 deg, life trimmed per lane to its floor distance (p95 x 1.08), still penetrating the map, sprites
  x0.88, emission unchanged. Pitfalls [game]: map-stopping visual lanes in an arena full of invisible shells (an always-on enemy-only
  shell + shelter walls cut 45 % of the lines mid-air -> "fewer than before"); 3x emission with x0.68 sprites read as thinner.
- **Prompts**: replacing on-screen hints with the source's own NPC lines (one per breath at its start, adapted nouns, no speaker prefix -
  tester's choice) is a text-only overlay in `EventTextForMap_dlc01` of `menu_dlc01` in every shipped language [game].

### 4.8 Sector damage from the air (a flying fan breath)

- **EMEVD has no angle / facing condition**; geometric conditions are only 3[2] In / Outside Area, 3[3] Entity In / Outside Radius Of
  Entity, 3[7] All Players In / Outside Area, 3[45] Inside Play Area [data]. Build a sector from ring cylinders around the apex
  (`1003[202] SKIP IF In/Outside Area(..., 10000, ring)`) and, per band, the law of cosines against an aim-point region A on the axis
  (angle <= theta <=> |PA| <= c(band)) tested as 3[3] with a Point region as entity B; each condition in its own unused condition group.
  6 m bands matched an ideal 40 deg / 73 m fan to 99.2-99.4 % on a 1 m grid [model; game].
- **Set the near edge from the body, not the apex**: a flying boss's root can stay on the ground at the hover point while the head hangs
  ~19-22 m ahead; a sector from the apex hit players under the chest [game-MP: client replay at 4.3 m]. Near edge 22 m (the source's own
  ground-flame start ~21-31 m) fixed it [game].
- **Fire hits at the TAE blast times** by splitting the script's long wait into whole-frame waits around the hit blocks (sum unchanged).
  One-time opening rows: `dmgHitRecordLifeTime <= 0` = indefinite = hit once per bullet [param doc]; vanilla strong -> weak HitBulletID
  chain precedent c2120 2120292 -> 2120293 [data].
- **`shootAngle` is YAW, `shootAngleXZ` is elevation**: lanes with shootAngle -80 on dummies of an animated bone started ~43 m up and flew
  sideways: nobody in the breath was hit [game]. Sample dummy heights over time (FK), never the bind pose.
- **Ground-fire finders** (gravity 999, `isPenetrateMap 0`) stop on the first collision below, including invisible projectile-only /
  enemy-only shells and tower tops -> flames floating in the air [game]. Fix: rays only inside the damage fan, short lives, first finder
  only after 1.0-1.2 s (none under the boss), then every 14-21 m, flame life 1.3 -> 1.0 s [game].
- **Audit that visible fire lands inside the damage area** (before the fix 0 of the carrier / lane flames did); drop map-native fire points
  outside the area [model].

### 4.9 Set-piece props (siege weapon and similar)

- **"Boss root inside an MSB box every 0.1 s" is blind to yaw**: fit the box with a contact simulation (posed prop vertices vs the boss's
  hurt capsules on a 1 m grid x 24 yaws + thousands of logged root samples); a box from the wall face z 0..28.5 m caught 56 % of real
  contacts at 80 % precision (old 60 % / 62 %) [model; game OK]. Check clearance of the extended prop against the phase's collision
  (>= 0.69 m).
- The prop animates on every machine; only the host applies the damage (a % HP SpEffect) and the scripted knock-down; nothing moves the
  boss [data, game]. Prop clips: `animation.md` 11.

## 5. Hit sizing [game]

- Start from the source: melee = source capsule radii (cm / 100); projectiles = shell collision radii.
- Cap by what is SHOWN: the radius vanilla pairs with that effect id (group vanilla bullets by `sfxId_Bullet / Hit / Flick`) plus
  the FXR emitter / sprite sizes. Donor effects are often smaller than the source's volumes (fireball core 0.5-0.7 m vs source
  2-3 m) and players report "hit without being reached".
- Accepted end state on a dragon: melee = source radii; projectiles and impacts = x1.2 of min(source, shown) (e.g. balls
  0.5-0.85 m, impacts 1 m beyond the visual); beams = source (2 m); delayed blasts with a warning ring = ring x1.1; zero-damage
  roars / winds / body contact unchanged. One size for all strength sets (the source used one) [game].
- FXR has no global scale: enlarging an effect means editing 30-90 size values in a copy (value-slot rule, `fx_sound.md` 1).
- Sample poses over TIME (dummy paths, mouth bearing, claw height), never only the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ bind pose.

## 6. Roll-dodge review (offline) [data]

Model: clip root motion applied, ground y = 0; capsules as sphere chains every 1/30 s; bullets per shootInterval flying straight,
stopped at y = 0 unless they penetrate; children at the end; player = vertical capsule r 0.35 (corrected: test the three body tops of
section 9, not one 0.35-1.35 m capsule). Test one roll in the best of 16 directions started 0-30 frames before the first standing hit
(not before the turn lock / 0.2 s); the roll must survive 0.53 s after the first hit ("strict" = never hit later). Use the vanilla roll
numbers (`tae_turning_windows.md` 9). Fix by trimming dwell (life of standing blasts, end of tracking), not radius: chain blasts 5.0 ->
3.5 m with life 0.25 -> 0.10 s (no-roll share 5.7 -> 0.1 %), fan tracking end 1.95 -> 0.90 s. Leave intended area attacks un-rollable
and say so. Limit: the model does not simulate the boss turning inside a window.

## 7. Performance

- Footprint audit: sum of (length + 2r) x 2r over active capsules in bind pose; flag >= 150 m2; never > 1,000 m2 for > 0.5 s.
  Sixteen 3 m x 45 m capsules (~5,300 m2) over display-derived map collision (millions of triangles) overlapped 0.3-0.55 M
  triangles per frame: 60 -> 10 fps. Moving the damage onto bullets ended it [game].
- Vanilla: every AtkParam_Npc row of 30 m or more has `mapHitType 2` (largest radius with 0 is 22 m) and `atkObj 0` [data];
  apply to roars / winds / area bursts.
- Bullet budgets: vanilla Heolstor's heaviest move peaks ~1,570 bullets / 1,260 FX alive; a heavy ported opener 270-470 /
  170-300 [data]. Emission interval is the main knob (visual owner bullets every 0.6 s instead of 0.15 s: 63 instead of 250 owners).
  GPU budget for denser looks: `fx_sound.md` 12.

## 8. Status scrub and strength variants

- Builder step + independent verifier: every own Bullet (`spEffectId0-4`, `spEffectIDForShooter`) and AtkParam (`spEffectId0-4`)
  reference to a SpEffect with poison / rot / deathblight / frost / sleep / madness power - also through replace / cycle /
  on-hit chains - is set to -1; a refType-2 BehaviorParam with such an effect fails the build. A cloned lingering-fire row
  carried deathblight [data].
- Strength / colour sets per phase via animIdOffset (`donor_graph.md` 3): the variant timelines differ from the base only in
  judge / SpEffect / FX ids; damage = base x the source's own ratio per attack family (e.g. strong 1.3-1.9 x, beams up to 3 x,
  "certain kill" 4 x) [game for selection, data for ratios].
- Phase damage without offsets: clone the AtkParam / Bullet rows and re-point BehaviorParam, or give the phase-2 NpcParam row
  its own behaviorVariationId (explicit no-op rows for judges the other phase lacks). An entity-wide attack-rate SpEffect also
  scales scripted specials that share rows [data, game].

## 9. Hit height vs short characters

- **A horizontal ray from mouth height misses short characters**: from 2.55-2.88 m with r 1.4-1.6 the lowest point is 1.2-1.5 m
  (higher between rays): bodies 1.8 m tall hit 100 %, 1.3 m 0-22 %, 1.0 m (a low pose, e.g. reviving a downed ally) 0 % [model]; the
  tester's short character stood in the fan untouched [game]. Moving only the damage-ray origin to a dummy ~2.0 m up gave 1.00 at all
  three heights with the pillar shadow unchanged [model; game passed]; a 1.08 m origin added terrain stops and leaked into the shadow.
- **Rule: the lowest point of every damage sphere along its flight <= ~0.9 m above the floor**; model body tops 1.8 / 1.3 / 1.0 m.
  Hero hurtbox sizes are not in the params (HeroParam / HeroStatusParam / ChrModelParam carry none) [data]. If the damage origin moves
  down while the flame stays at the mouth, short characters see fire pass overhead and still take the hit: a tester decision.

## Unverified

`mapHitType 2` curing a roar hitch; predictive bullet lead clamps (`predictionShootObserveTime`); emission position type 4 = target's
feet; shared hit records across a multi-shot burst; which of fixed dummy / endless hit / no carrier made the impact circle hit; why a
cross-binder carpet FX copy never rendered; why ground FX born from an expired hold do not render; whether 7767's attack / stamina
rates apply to EMEVD-fired bullets; the guard direction of the boss-centred lethal sphere in a real session; vanilla Absorb skills
erasing fan rays as the cause of a missed reviver; collision layer 117. (Resolved since the last version: +0x8C is the map-collision
radius on rays too; EmittePosType 6 = above / behind the target.)
