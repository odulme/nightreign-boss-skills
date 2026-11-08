# TAE: layouts, jump tables, timeline mapping, heading, turn windows, AI windows, event timing

Tags as in `SKILL.md`. Pipeline stage S4 (`boss_pipeline.md`). Write TAE with AsmTool or own tools on Smithbox's
`TAE.Template.NR.xml`; read back after every write (an event stores no parameter length: after inserting an event one neighbour
reads back with trailing zero padding - compare without trailing zeros [data]).

## 1. Start from the donor TAE

- Copy the donor's TAE so every animation name the graph references resolves; map unmapped names to idle; scale times to the
  new clip length.
- Keep control events (jump tables, blend, turn speed, cancel windows) and the donor's generic state SpEffects that vanilla
  uses everywhere: attack-state SpEffect 5980 over attacks, 14895 over death and stance break, the stance-break set on 8700
  (SpEffect 50 +20 % damage taken, 36 riposte window, critical-spot FX 600700 on dummy 970) - remove pieces only when the tester
  does not want them (a scripted knock-down without the critical spot) [game].
- Delete the donor's attacks, bullets, FX, sounds, invulnerability and status SpEffects; your own rows replace them.
- Every event must sit inside an event group: an ungrouped event never fired; type-118 trails must sit in a type-96 group [game].
- Never inject damage into posture-transition prefixes the source has no collision window for (a generator put a 4 m shock into
  every stance drop) [data].

## 2. Parameter layouts that were written and played [data]

| type | meaning | layout |
|---|---|---|
| 0 | jump table | int JT +0, float 0 +4, int -1 +8, byte 6 +12; AI windows end = 100 (open to clip end) |
| 1 | attack | int attackType +0 (0), int AttackIndex +4, int BehaviorJudgeId +8, byte direction 0xFF +12; 32 bytes; Source / StateInfo 0 (donor 412 / 413 are phase conditions) |
| 2 | bullet | int dummy +0, int AttackIndex +4, int judge +8, byte attachment +12 (2 = along the dummy's forward, 0 = actor front + bullet angle), byte enable +13; 32 bytes |
| 16 | blend | event length = blend time |
| 67 | SpEffect | int id +0 |
| 96 | FX | int fx +0, int dummy +4, -1 +8 (99 = same-slot replace), follow byte +13, 1 +14, zero tail; ALWAYS 32 bytes (StateInfo u16 at +16 is read unconditionally; 16-byte records read the next header and the FX was rejected) [code] |
| 129 | sound | SoundType, SoundID, Dummy, Slot -1, StateInfo 0, play mode (0 one-shot, 1 stop at event end), 1, 1, 0, OffsetType -1 |
| 144 | camera shake | s16 rumble id, u16 dummy, float near, float far |
| 193 | opacity fade | blink / dissolve (copy vanilla bytes) |
| 224 | set turn speed | float deg/s +0, byte 0 +4, byte 0xFF +5 |
| 760 | root-motion multiplier to target | byte enable, floats reference distance (= the clip's own horizontal travel in the window), min, max, arrive angle (180 = land behind), arrive distance; displacement = clamp(distance - arrive, min, max) |

TAE 760 census: 2,144 vanilla events in 131 characters; min must be 0 for close-range use (a min > 0 made a 4 m teleport slash
pass through the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ player) [data, game]. Template a type-1 row from the donor's first attack event of the same entry (vanilla
type 1 exists at 24 and 32 bytes; keep vanilla's length).

## 3. Jump tables used (Smithbox names; what they did for us)

| JT | name / use | where |
|---|---|---|
| 7 | DisableTurning - heading hold | every attack outside source turn windows; scripted bodies |
| 8 | Invincible | only airborne set-piece time; never in ordinary flight attacks (with larger capsules it let nothing hit) |
| 12 | death state / reward pulse at impact | death clip (the death finaliser also pays runes once per machine [code]) |
| 23 / 86 | AI combo continuation / end if AI attack queued | AI windows |
| 78 / 79 | AI move / dodge cancel | AI windows |
| 24 | super armour | airborne span of flight attacks, set pieces - stops ordinary flinches but NOT stance damage (corrected: it does not protect set pieces; add SpEffect 45, `reactions_death_phases.md` 2) |
| 27 / 51 / 113 | ignore gravity / disable fall / height correction | flight spans (51 over the whole flight clip); JT27 is not a reliable airborne measure (`animation.md` 3) |
| 39 / 50 / 49 / 95 | collision / hurtbox off, lock-on off, shadow off | blinks, death dissolve |
| 71 | stop poise recovery (donor 8700 pattern) | stance break, knock-down |
| 132 | jump frames / flight bit | event set pieces only |

## 4. Heading: hold and turn windows [game: "all fine" after this recipe]

- Defect "it slides" (tester's words: rotation without a turn animation): generator turn windows of 45-110 deg/s up to the first
  hit plus attacks issued as `AttackTunableSpin`. With the pivot under the hip and the mouth 13.8 m ahead, 110 deg/s moves the
  mouth sideways at ~26 m/s.
- Recipe for every attack and every fire-set / variant entry: remove all 224 rows and all JT7 / JT110 rows; lay 224 = 0 plus JT7
  over everything except the source turn windows; inside the windows 224 = source rate and no JT7. Keep only 224 = 0 (no JT7)
  over intervals where the clip itself yaws (sample-to-sample yaw > 0.2 deg, padded 0.1 s). Vanilla model: c7500 3010 (JT7
  holds, a 224 window opens between JT7 rows); vanilla event clips hold with JT7 throughout or with 360 deg/s rows between JT7.
- Source turn windows, how they were measured:
  (a) source turn-speed keys (deg/s between keys); (b) an allowance ramp 0 -> A deg over f1..f2 -> rate A / (t2 - t1);
  (c) the 0-deg member of a directional family: allow a residual of ~45 deg over that motion [inferred]; (d) flight sorties:
  ~45 deg/s in the hover before the air attack [approximation]. Merge overlapping windows, keep the faster rate.
- Result on a 31-attack dragon: 22 attacks fully held; windows only where the source rotates (e.g. 0.2-0.8 s windows at
  48-360 deg/s inside long moves).
- In-place turns: clips 5000-5003 (source turn motions, 1.5 s, root yaw -90 / +90 / -180 / +180; right turns can be mirrored
  left turns), no 224 row, AI windows from ~1.05 s; the Lua queues `GOAL_COMMON_Turn(life 3, target, 45)` before moves when
  the target is in the rear half, or outside the front arc for "aim" moves that start with a directional family; the common hks
  plays 5000-5003 for |angle| >= 45 and the 180 clip from 135 deg. Where no turn clips exist for a stance, let the attack spin
  (AttackTunableSpin, spin 1.5 s, 45 deg) [game].
- Shockwave / line attacks: freeze turning during the hits (inherited tracking bent the wave) [game].
- **Aimed multi-shot moves need re-aim windows between the shots** (refines "hold the heading through attacks"): bullets aim at the
  target only while it is inside the Bullet's `lockShootLimitAng` (45 / 90 deg) of the muzzle, even with homing 0 / auto-homing 0 /
  follow 0. With the heading held through a whole chain, balls left the mouth sideways and the tester read it as "the dragon does
  not turn, only the shots home"; logged facing error at release median 57 deg, shots 2-3 median 119 deg [data, game log]. The
  source kept the body still and blended head-aim variants (0 / +-85 deg; +-45-52 deg on all fours) [data]. NR substitute that
  passed: 224 windows that close 0.35 s before each release (0.25 s for a shot 0.62 s into the move) and reopen 0.5 s after it, at
  ~60 deg/s; release times unchanged (dodge timing unchanged). Model 57 -> 3.6 deg median, max 132 -> 23 deg [model, game].
- **Turn rate vs perceived sliding**: the mouth sits 8-12 m ahead of the pivot; at 60 deg/s it moves sideways 8-12.5 m/s (accepted),
  at 110 deg/s ~26 m/s (read as sliding) [model, game]. Shots released < ~0.45 s after the move start get no window; players under
  the mouth (4-7 m) cannot be hit by any turn [model].

## 5. Turn-rate and Rotate semantics [code, game]

- No 224 row in the playing clip = NpcParam default turn rate (5 deg/s on one ported boss), not 90 [game]; one native audit
  reads a 90 deg/s fallback for explicit turns without a row: give every clip a Rotate starts an explicit 224 row.
- EMEVD `Rotate Character` (2004[14]) aligns local -Z with the target; the yaw controller runs every frame while "animation
  active"; with an explicit animation id the rate override is -1 and the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ controller reads the current turn rate: a rate <= 0
  becomes 90 deg/s. So a TAE 224 of 0 cannot stop a Rotate; use a small positive rate (0.01) in Rotate-driven clips
  (a stage-breath body that worked: 240 deg/s for 1 s, then 0.01).
- One Rotate request per actor (a new one replaces it); it can survive a following Force Animation; `Rotate(wait = 1)` waits on
  "animation playing", not on reaching the angle; animation -1 = automatic selection (thresholds 40 / 110 deg, generic 260xx
  motions), not "keep the clip". Leave 2-3 EMEVD frames between a Rotate ending and the next Force.
- Aim Rotate / swoops at points hundreds of metres away so an overshoot cannot reverse the bearing; never rely on authored root
  yaw right after a Rotate-driven clip; end a chain with a Rotate toward where the actor must face.
- With the AI OFF there is no engine turning: aiming during a set piece needs an AI-driven mode or warps (co-op: `coop.md` 4).

## 6. Offline heading model (run before and after every turn change) [data]

Sample at 60 Hz; the engine turns toward the target at the 224 rate of the moment (0 under JT7, NpcParam default where no row);
add the clip's own root yaw; targets at 30 / 60 / 90 / 150 deg plus one strafing at 6 m/s from 12 m. Report rotation before the
first hit, max deg/s, mouth sideways speed (arm = mouth distance), heading error at each hit. `scripts/heading_model.py` is a
minimal version.

## 7. AI windows and move completeness [game]

- Mechanism [data + inferred]: the attack goal ends when the clip's windows open; the after-attack goal runs; the next act
  cancels the clip at JT86 (attacks) or JT78 (turn / approach / leave). JT23 matters only for ComboRepeat / ComboFinal.
- Vanilla rule (c4510, 33 animations; c4900 / c7500 / c7510 agree): JT86 is never before the last attack / bullet event
  (median +2.0 s); JT23 is never after JT86 [data].
- Release point from the source: MHW mFlag "busy" bit 0x10 is set through attacks / turns and cleared in recoveries; where it
  is never cleared, play to the end. Relink / others: last content of the source move.
- Placement rule: JT23 = JT86 = JT78 = JT79 (same start, end 100) at max(last content incl. purely visual flame, busy-bit
  clear, the frame where an appended stance rise completes); at least ~0.3 s before the clip end. Opening inside a stance rise
  starts the next clip from the wrong stance. The tester accepted 1-3 s longer commitment; "last hit + 0.6 s" had cut a 4.9 s
  flame at 2.7 s ("only the first half plays").
- Reaction windows that worked: 8060 ~2.4 s; 8700 clip end - 1.0 s; scripted knock-down last 0.8 s; turns 1.05 / 1.5 s.
- Goal life of the attack goal >= the longest clip + margin (a 10.4 s clip under a 10 s life let the next act start before
  landing; a 20 s life under a 23.5 s clip times out in the landing - harmless only while no window is open) [game].
- Completeness audit per move: source chain vs our clip, content times, cut class, confidence; it also found a wrong
  directional member (fired backwards) and a variant playing a member without wind-up.

## 8. Markers (TAE 67 -> SpEffect) for AI and EMEVD [game]

- Idle heartbeat: an inert SpEffect (endurance ~0.3 s) pulsed 0.05 s every 0.1 s in idle, walk, run, turn clips.
- Busy: the same in every non-idle clip. "Heartbeat present and busy absent" = standing idle = the safe hand-off moment.
- Airborne marker over flight spans (scripts reject knock-downs while it is on).
- Reaction / recovery guards on 8060 (1.6 s), 8500 (5.05 s), 8550 (5.45 s), 8700 (6.6 s): scripts defer specials until
  recovery is complete (one-second markers expired inside a 6.3 s stance break and let a cast start too early).
- Release markers at source frames (capture / point SpEffects) let EMEVD place delayed ground blasts at the source's timing.
- "Max N attacking" between helper actors: inert SpEffect pulsed until JT86, read by EMEVD / Lua.
- SpEffect 45 (no stance damage) as a type-67 row from 0 to the clip end on every forced / scripted clip and every variant of it, and
  over the measured airborne span of AI flight attacks (`reactions_death_phases.md` 2, 6).
- Release markers obey the timing‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ rules of section 10 (>= 0.05 s).

## 9. Fairness numbers from vanilla [data]

Vanilla roll: invincible 0-0.43 s, actionable ~0.60 s, slowest recovery 0.77 s. A DamageLv3 hit allows the next roll only
1.167 s after a FIRST hit (0.5 s after a second hit in a row), so a shorter gap is a guaranteed follow-up. Combo gaps >= 0.83 s
start-to-start and >= 0.58 s end-to-start; blink reappear -> first hit >= 1.0 s (vanilla minimum). Dodge distances:
`balance.md` ("Roll-dodge review and hit sizes") of `nightreign-nightlord-replace`.

## 10. Event timing on speed-multiplied clips [data]

- **Release events at least 0.1 s for bullets, 0.05 s for markers, on every clip with a speed multiplier.** A one-frame event
  (0.0167 s) at a TAE 608 speed of 1.05 (17.5 ms of clip time per 60 fps frame) falls between two frames ~5 % of the time (more on
  slow frames); a lost capture marker skipped a whole mine line [data; no missing-fire report after the change]. Vanilla: 0 of 1,136
  bullet events in 7 Nightlord TAEs are shorter than 0.0667 s. A longer window does not fire a single-shot bullet twice
  (`shootInterval 0`; 996 vanilla events of 0.0667-0.3 s).
- **The first shot fires at the event start, not one interval later** (387 vanilla bullet events are shorter than their bullet's
  shootInterval) [data, inferred strong]. A continuous type-2 event keeps consuming shootInterval while enabled (`fx_sound.md` 6).
- **Divide source times by the clip speed multiplier** when a TAE 608 speed applies (1.05: growth 0.333 -> 0.317 s, life 2.58 ->
  2.457 s).
- Speeding a move up (e.g. a first blast 10.9 -> ~7 s after take-off) is a TAE / script timing change only; keep the flight to its
  hover point and the co-op sync [game].

## Unverified

Whether JT7 suppresses an EMEVD Rotate; whether a missing 224 row inside a Rotate means the NpcParam rate or 90 deg/s;
why JT7 must stay off clip-yaw intervals; AttackTunableSpin under JT7 on all fours;
the 45 deg residual / 45 deg/s hover re-aim as stand-ins for the source exe's member choice; the meaning of TAE 233 / 601 / 795.
