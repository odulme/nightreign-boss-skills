# Balance: HP, party and Deep Night scaling, part breaks, damage, status, dodge, helpers

Tags as in `ids_and_planning.md`. Rows / values: regulation 10350000 (vanilla). Balance numbers are design decisions: offer
options with numbers, the tester decides; record the answer. Pipeline stage: S9 of
`nightreign-boss-port/references/boss_pipeline.md` (gate: tester decision recorded with numbers per depth / party).

## 1. Vanilla Nightlord rows [data]

| boss | NpcParam row | base hp |
|---|---|---|
| Gladius | 75000020 | 3200 |
| Adel | 75100020 | 3712 |
| Gnoster | 75200020 | 3680 |
| Faurtis | 75300010 | 3456 |
| Maris | 75400020 | 3584 |
| Libra | 75600020 | 3686 |
| Fulghor | 76000010 | 3360 |
| Caligo | 49000010 | 3392 |
| Heolstor phase 1 / 2 | 75800000 / 75802000 (placed AI rows 75800010 / 75802010) | 1408 / 2880 |

Two benchmark means are in use; always say which one a multiplier refers to:
- **mean of 8** (Gnoster without Faurtis, Heolstor as 1408 + 2880) = 3612.75;
- **mean of the 7 regular main bodies** (Gladius, Adel, Gnoster, Maris, Libra, Fulghor, Caligo; final boss, DLC bosses and
  Everdark rows left out) = 24,614 / 7 = 3,516.29.

## 2. How max HP is formed

- **Max HP = base hp x product of maxHpRate over all active SpEffects** [code; game: a DLL log read 26280 = 7424 x 3.54 solo].
- Innate Nightlord SpEffect 7767: maxHpRate 3.54, attack rates 3.36 [data]. The placed Heolstor rows (75800010 / 75802010) carry
  7767 too; 7760 (same rates) sits only on the unplaced rows 75800000 / 75802000 [data].
- **Party, vanilla** [data]: NpcParam.multiPlayCorrectionParamId 7767 -> 2 players SpEffect 7867 (maxHpRate x2, poise damage
  taken 0.55, status build-up 75 %, status defence 0.85), 3 players 7967 (x3 / 0.30 / 50 % / 0.70); client3 = -1 in every row.
  Activated by `Activate Multiplayer-dependant Buffs` (common 90015012).
- **Party, Seamless Co-op** [game-MP; data + arithmetic]: the co-op mod scales enemy HP itself and 7867 / 7967 never appear on
  the boss. Measured 2P / 3P boss HP fits exactly
  `max HP = trunc(f32(hp x f32(3.54 x DN x (1 + 1.2 (n - 1)))))` - the party factor sits INSIDE the single-precision rate product
  (211,982 = trunc(9032 x f32(3.54 x 1.95 x 3.4)); multiplying the truncated HP afterwards gives 211,979). For n = 1..6 the
  factor is x1.0 / 2.2 / 3.4 / 4.6 / 5.8 / 7.0 (+120 % per extra player; 4-6 from the formula, not yet measured). Consequences:
  - do not top up in events (it would multiply on top) [inferred]; logic keyed on 7867 / 7967 never fires [game-MP];
  - **HP is fixed when the character is ENABLED**, for the party at that moment: a phase-2 body enabled after a player left got
    2-player HP [game-MP];
  - characters without a multiPlayCorrection id (helpers, summons) are not scaled at all (they stayed at NpcParam HP in 3P)
    [game-MP]: scale them yourself from per-slot presence (`coop.md` 7) with maxHpRate SpEffects (copies of a vanilla row with
    only maxHpRate changed);
  - the vanilla 2P / 3P stance rates (saReceiveDamageRate 0.55 / 0.3) are absent, so stance breaks come ~3x sooner than for a
    vanilla 3P Nightlord; offer a party-scaled stance option with numbers [inferred].
  **CORRECTS** the earlier "under a 6-player mod follow its own adjustments": follow it, but write this formula into every HP /
  part table and check everything keyed on 7867 / 7967.
- **Deep Night** [data]: NpcParam.chaosMatchingCorrectParamId -> ChaosMatchingCorrectParam (5 SpEffect columns = depth 1..5
  [inferred]). Row 7767 -> 877671..877675: maxHpRate 1.25 / 1.4 / 1.57 / 1.95 / 2.16; attack 1.25 / 1.55 / 1.92 / 2.83 / 3.31;
  stamina attack rate 1.15 / 1.2 / 1.3 / 1.45 / 1.5. Row 7760 (unplaced Heolstor rows only) -> 877601..605: maxHpRate 1.3 / 1.378 /
  1.461 / 1.636 / 1.718. Link 0 = exempt [game: HP unchanged in a forced depth-3 run]; 7767 = scales like a Nightlord. Both were
  shipped at different times: ask.
- Packs may force a Deep Night depth on every run: state‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ every number at depth 0 AND at the depth players actually use. **Calibrate
  in the shipping configuration** (co-op DLL, forced depth, co-loaded mods): head breaks tuned in a solo depth-0 dev entry came
  4-5x too fast in a pack that forced depth 4 and was played in co-op [game-MP]. Either run one calibration fight in that
  configuration or present the uncertainty with numbers [data].

## 3. HP: method and recorded decisions

- **Express each phase as a multiple of a vanilla mean** (section 1), round half up; e.g. 0.75 x 3,516.29 = 2637, 0.9 x = 3165;
  2.1 x 3,612.75 = 7587 [data]. Offer 2-3 multiples with solo and party numbers per depth.
- **Recorded decisions (each was iterated; do not copy, offer)** [game]: a three-phase quadruped went 1.7 -> 2.5 -> 2.1 x the
  mean of 8 (final hp 7587) - **REFINES** the old "1.7 x played well": it was one step. A two-phase humanoid went 0.7 -> 1.0 / 1.3
  -> 0.75 / 0.9 x the mean of 7 within days; an earlier two-phase step sat at ~+14 % total effective HP versus Heolstor (Heolstor
  effective solo 4,984 + 11,215 = 16,199; its phase 2 also carries SpEffect 7352, maxHpRate 1.1 / attack x1.12).
- Effective HP for comparisons = hp x innate rates x party effect x depth effect [model].
- **Make a retune a two-cell param patch with anchors** (old value -> new value, refuse on anything else), never a regeneration of
  the event: an HP-only change touched exactly the 2 boss NpcParam rows; a helper row with hp 1 stays [data].
- **Absolute-HP audit before changing HP** [code, data]: absolute compares (`IF Character HP Value`) only at the floor (<= 1);
  every SpEffect set on the boss has changeHpPoint 0 (fixed-point damage SpEffects belong to the players' side only); phase and
  special thresholds are HP ratios (`4[2]` in EMEVD, `GetHpRate` in the AI); TAE-applied SpEffects do not change HP by points.
  With all of this true, NpcParam.hp is the single knob and every scaling multiplies it.
- **Prove the change and publish the expected numbers**: read the regulation back (only those cells changed, every other table
  identical) [data]; give testers a table of expected max HP per party size and Deep Night depth to compare with the DLL log.

## 4. Part / break durability when HP or scaling changes

Engine side of parts (records, re-arm, host decision, bullet multiplier): `fight_script.md` 7. Design side:
- **Absolute part durabilities do not follow base HP.** When hp changes by s: multiply every free base by s (head, chest, wings,
  re-arm values, co-op bases), then re-derive guards, party values and per-depth picks with the ORIGINAL formulas - first assert
  those formulas reproduce every old number (plain round(old x s) differed by 1 in 8 of 22 values). Break positions in the HP bar
  then held within 0.125 % (head) / 0.10 % (chest, wings) at every depth and party size [sim]. Unaffected: changeHpRate losses
  (siege weapon 5 %, breath ticks), flat changeHpPoint losses on players, HP-ratio gates [code].
- **Ask about every breakable part when a durability / HP number changes**, not only the one the tester names (a rescale that
  forgot chest and wings moved their breaks ~19 % later in the bar) [sim].
- **Part max = trunc(f32(base x f32(product of maxHpRate)))**: evaluate every f32 multiply order when picking integer bases [code].
- **Depth / party rule is a design choice (tester decision)** [game]: (a) constant absolute durability = per-depth bases (pick
  the integer whose 1 / 2 / 3-player max is closest to the depth-0 max, error <= +-21 HP; e.g. 1500 -> 1200 / 1071 / 955 / 769 /
  694 for depth 1-5); (b) constant fight progress = no depth division (the part scales like boss HP) and a party factor equal to
  the boss's (1 + 1.2 (n - 1)). With (a) + a x n party rule, at 3P depth 4 the break came at ~1/2.2 of the intended fight
  fraction (boss x1.95 x 3.4 vs head x3). One tester chose (b) for the head and kept (a) for chest / wings. **REFINES** the old
  text that presented only (a).
- **Break timing model** [model]: fight fraction at the first break ~ part max / (k x boss max HP x head share). Targets that
  played: solo ranged with ~75 % of damage on the head -> first break around mid-fight (head damage ~38 % of boss max HP); melee
  first break after ~2 min [game]. A real 3P party put only 42 % on the head: ask which aiming style the target assumes, and ask
  targets as HP-bar fractions ("first break at ~1/3 or 1/2 of the bar, solo ranged / melee / co-op").
- Second break of the same part slightly harder than the first (re-arm base = 4/3 of the first was one tester's rule; the first
  gives a long knock-down).
- **Multi-knob requests**: restate the effect per attack class in body-equivalent damage, part HP / (weak x k). Three stacked
  changes (weakPartsDamageRate 2 -> 1.2, part HP x2, bullets x0.5) gave x3.3 melee / x6.7 bullets instead of the x2 asked, and the
  head "never broke" [game]. `weakPartsDamageRate` scales HP damage AND part damage alike [code].
- Per-part HP-damage multipliers without moving breaks (carrier records), bullet-only part reduction: `fight_script.md` 7;
  localising source hitzones: m = 1.2 x (e / e_head)^gamma with e = 0.5 Sever + 0.2 Blunt + 0.3 Shot, gamma chosen so the
  damage-weighted mean of the non-head multipliers = 1.00 (0.263 once), rounded to 0.05; offer x0.5 / x1.5 width variants
  [model; tester approved]. Vanilla Nightlords: weakPartsDamageRate 1.3 + partsDamageType 1, nothing else above 1.0 [data].
- Measuring break progress (trainers, log-only probes, classifying hits): `testing.md` 7.

## 5. "Break the cast with N ultimate Arts" (cast bars)

- **Count only inside the visible window** [game-MP bug; sim]: Arts counted from the special's START (its name banner), ~5 s
  before the bar appeared; a teammate's early‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ Art broke the special and refreshed the others' Arts, so the cast never happened.
  Open the counting window at the event line that SHOWS the bar; latch Arts already running when it opens (a held "Active during
  Ultimates" SpEffect would otherwise count instantly); take local copies of the remote toggles at the special's start; refresh
  the others' Arts only for Arts inside the window.
- **Required count = players present at that moment** from per-slot presence, never `Is Player Count` (it read 2 in a 3-player
  party) (`coop.md` 7).
- One owner per toggle: each player writes only their own network toggle; the host counts and decides; clients follow.
- Gauges built from a helper's HP: `fight_script.md` 6.

## 6. Damage

- Largest single hit per attack animation, raw AtkParam total, all Nightlords (n = 289) [data]: p25 210, median 280, p75 320, p90
  400, max 500; in game x3.36 (innate rate). Roster per-move mean 262. Tiers: light < 200, heavy 200-299, ultimate >= 300.
- Reference players at level 15: HP 740 (Recluse) .. 1280 (Guardian), Wylder 1120; armour negation 14-29 % [data].
- Transfer from a source game: anchor on that game's attack values and compare a usage-weighted mean hit against the Nightlord
  median. The tester kept source-derived values instead of a proposed global re-scale: present the comparison, do not apply it.
- Phase-specific damage: clone the AtkParam / Bullet rows of the AI moves and re-point BehaviorParam refId; an entity-wide rate
  also scales scripted specials and dividing back hits integer rounding [data].
- **Attack multipliers after part breaks**: a permanent self SpEffect (effectEndurance -1, spCategory 0, unique id) with the five
  AttackPowerRate fields multiplies with innate 7767 and the depth rows; scales TAE attacks, bullets and boss-owned EMEVD Shoot
  Bullets, not flat changeHpPoint losses; each machine sets it on its own copy from network flags [code]. Damage after defence
  grows MORE than the rate for small hits (steep curve): x1.35 attack gave x1.7-1.9 damage; when the tester quotes linear targets,
  solve the rate on the curve and say so (x1.35 / x1.75 became 1.16 / 1.67 and were accepted) [model, game decision].
- **"Certain kill unless X" from the source** - two shipped designs, a tester decision:
  - survivable loss: flat HP loss SpEffect (positive changeHpPoint = flat loss, positive changeHpRate = percent loss,
    effectEndurance 0 = one shot) applied by each machine to its own player once per move [game: losses read back]; a 40 % max-HP
    SpEffect every 0.5 s gave a 1 s grace and no launch;
  - **real lethal hit from the boss** (REFINES the above when the source kills): each machine fires, in a sync-off event for its
    own player, `Shoot Bullet(boss, boss, -1, <BehaviorParam refType 1>, 0, 0, 0)` = an invisible sphere centred on the BOSS
    (radius 1 -> 230 m in 0.575 s, life 0.625 s, one hit per target, passing map / characters / assets); hit and launch direction
    = boss -> player [game; game-MP]. A sphere centred on the victim killed but launched in a random direction [game]. Guardable
    from the front: AtkParam_Npc atkPhys 9999 (every NR guard-capable shield has physGuardCutRate 100), atkFire 25 as guarded
    chip, atkStam 65, disableGuard 0, dmgLevel 10, isDisableParry 1, atkSuperArmor 999, guardAtkRate 100, mapHitType 2 [data;
    calibrate in game]. Stamina per guarded hit = atkStam x boss staminaAttackRate (7767 = 2) x depth stamina rate x (1 -
    staminaGuardDef / 100) [community formula + data]: at L15 an average shield holds ~2 hits, a greatshield ~3, the best ~5.
    Ask before cancelling other heroes' ultimates (Revenant Immortal March 705000 / 705010 outlasts an 11.5 s train; Guardian
    Wings of Salvation 701510 ~2-2.5 s; no SpEffect has `noDead`; immortality = state info 143) [data]. Co-op rules: `coop.md` 1.
- Dead ends [game]: damage in a SpEffect payload whose `invocationConditionsStateChange1 = 452` was never met; SpEffects on party
  slot aliases 10002-10004 with effectTargetSelf / Friendly 0.

## 7. Status, poise, absorption, aggro [data]

- Status thresholds via ResistCorrectParam 154 -> 252 -> 542 -> 999; immunity = disable SpEffects 90000 / 90010 / 90020 / 90030 /
  90040 / 90300 / 90060. Co-op build-up x0.85 / x0.7 (vanilla rows; absent under Seamless Co-op [inferred]). The tester rejected
  copying Heolstor's immunities: poison / bleed / frost at 252 (roster median). Benchmark for difficulty, not for removing player
  tools.
- Absorption: one clear weakness like the Nightlords (xDamageCutRate > 1, e.g. holy 1.35); NightBossMenuParam.effectiveAffinity
  matches the > 1 fields.
- Poise: superArmorDurability = stance pool (Heolstor 130); recover correction (SA - 65) / 65; saReceiveDamageRate 0.55 / 0.3 at 2 /
  3 players (vanilla only, section 2); stance break = 8700. A critical window needs ThrowParam rows and defender animations (the
  tester did not want one; drop the stance-break critical glow rows when no ThrowParam row has the boss's DefChrId).
- Aggro: leave NpcThinkParam aggro fields equal to Nightlords; the engine model picks the target.

## 8. Roll-dodge review and hit sizes

| vanilla dodge [data, c0000] | invincible | travel |
|---|---|---|
| light roll | 0-0.433 s | 3.94 m front / 3.43 back / 5.0 side |
| medium / heavy roll | 0-0.40 s | 3.65 / 3.31 m |
| Guardian step | 0-0.333 s | 3.0 m |
| Duchess step | 0-0.333 s | 3.77 m |
| Recluse step | 0-0.5 s | 5.0 m |

Locomotion: walk 1.5, run ~4-4.8, dash ~6-6.8, sprint 8.28 m/s.
Method [model]: on a player-position grid measure each hit volume's dwell and test "one roll in the best of 16 directions";
everything except intended area attacks should be escapable with one roll. Trim dwell (life of standing blasts, end of tracking)
rather than radius. Hit sizes: source radii for melee, projectiles / impacts x1.2, effects unscaled [game]; an earlier x0.85
shrink was reverted at the tester's request. Short characters: the lowest point of every damage sphere along its flight must sit
<= ~0.9 m above the floor (a ray from mouth height missed 1.3 m / 1.0 m bodies) - details `nightreign-boss-port`
`attacks_hits.md` [model; game].

## 9. Pace and DPS (optional benchmarks) [model]

- Run the real goal scripts in a 2-D simulator (4 player styles x 3 seeds x 600 s): threat per minute, safe-window time (gaps >=
  2.5 s), hit moments per minute, longest pressure run. Heolstor phase 1 / 2 safe window ~45 s per minute. A lever that worked
  in the model and shipped: an after-attack goal that strafes (`GOAL_COMMON_SidewayMove`) after unchained‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ attacks; chain caps did
  not help.
- 60 s stake benchmark: stationary player capsule r 0.4; 12 starts (4 / 12 / 24 m x 4 directions) x 10 seeds per cell; real AI
  (installed bytecode in a real Lua); moves from TAE / BehaviorParam / AtkParam / Bullet geometry; reference Wylder L15 (HP 1120,
  defence 156, absorption 19 %); damage on the Elden Ring defence curve (NR keeping it is [inferred]). Vanilla Nightlord cells
  median ~7,480 per 60 s; accepted targets once: phases 1 / 2 at 1.06 / 1.13 x median, final form 1.96-2.40 x [game decision].
  Model rules that changed results: one hit per TAE attack event per target; child bullets share the parent's hit list; lingering
  ground fire re-hits per `dmgHitRecordLifeTime`; list scripted set pieces separately. The simulator was not bit-reproducible
  across processes even with fixed seeds: measure a pure rate change by paired re-scoring, not by cell differences.

## 10. Mod-added helper NPCs

Helper rows carry no Nightlord SpEffect and no depth link, so their hits are mostly eaten by player defence. Scale their
AtkParam rows to a target ratio of a reference boss hit, and give them an own ChaosMatchingCorrectParam row whose 5 SpEffects
copy the boss's depth effects with only the attack rates kept (factors needed to hold the ratio 1.21 / 1.44 / 1.74 / 2.49 / 2.90
[model]). Every helper NpcParam row needs a valid chaosMatchingCorrectParamId (0 = none; no vanilla row uses -1). Their HP is not
party-scaled under Seamless Co-op (section 2).

## Unverified

Whether changeHpPoint ignores damage negation and how shelters interact; Deep Night SpEffect application time; party link 7767
combined with Deep Night link 0 has no vanilla precedent (worked for HP); negative changeHpPoint = restore; the 15.2k upper end of
a quoted Nightlord solo HP range (base x 3.54 gives at most ~13.1k); Seamless Co-op HP at 4-6 players (formula only); whether the
co-op mod's party factor enters NPC part max; solo break timing in a pack without a trainer; whether innate 7767 attack / stamina
rates apply to EMEVD-fired bullets; the Elden Ring defence curve in NR; stance fixes under a full 6-player load.
