# Rows, damage transfer, HP benchmark, part damage, break durability, pacing, helper rows

Tags as in `SKILL.md`. Pipeline stage S9 (rows also in S2 / S5; `boss_pipeline.md`). Regulation 10350000; exe offsets NR 1.3.3.0.
Nightlord tables (vanilla HP rows, party / Deep Night factors, status, poise, dodge numbers) are in `nightreign-nightlord-replace`
`balance.md`; this file adds the character-side method and the part-damage mechanics. Balance numbers are design decisions: present
options with numbers, the tester decides, record the answer.

## 1. NpcParam: a hybrid clone [game]

Take BODY fields from a vanilla character of the same body plan and size, and SCALING / TEAM / POISE fields from the row of the
destination tier (a Nightlord for a Nightlord, the stand-in for a field enemy). Diff the result against the source.

| field group | from | notes |
|---|---|---|
| hitHeight / hitRadius / chrHit*, weight, moveType, defaultLodParamId, lockGazePoint*, overlapCameraDmypolyId, toughnessRecoverCorrection, undulation, knockbackRate 0, guardLevel | body-plan donor (e.g. Ancient Dragon for a dragon) | chrHitRadius below hitRadius so hurt capsules protrude |
| resident spEffectID0-9, multiPlayCorrectionParamId, chaosMatchingCorrectParamId, teamType, superArmorDurability, resistCorrectId* | destination tier row | innate 7767 for Nightlords; 5400 in slot 0 = no animIdOffset |
| hp, SoundBankId, SoundAddBankId, SfxResBankId, lockCameraParamId, lockScoreOffset, modelDispMaskNN, partsDamageRate*, weakPartsDamageRate, partsDamageType, damage cut rates, turnVellocity, materialSfx*, isUnduration 0 | own | one clear weakness like the Nightlords; part-rate mechanics in `physics_hurtboxes.md` 4 |

- teamType: vanilla Nightlords use 33 / 7 / 6; a boss with helper actors must use 33 (with 7 they damaged each other) [game].
- superArmorDurability = poise pool; recover correction = (SA - 65) / 65 [data].
- Remove donor resident SpEffects that do not fit (a body donor's ParryResist, ExecTypeDamage, immunities); unaudited ones are
  a risk [data].
- Inherited fields that bit: `hitYOffset` (floating), `logicId`, `enableWeaponOnOff`, `thinkAttr_doAdmirer` (idle in groups)
  [game].

## 2. NpcThinkParam, model rows

- battleGoalID = your goal; logicId 10000; long search / sight / memory times (9999) and back-home distances (9999) for a boss
  that must never leash; BattleStartDist ~60; disablePathMove 1 on floors without navmesh (enemies then need `Set Character
  Home` where they actually stand) [data, game]. Path-moving summons (`disablePathMove 0`) need a navmesh where the content really
  sits (`boss_pipeline.md` S8).
- Show builds: goal 11000 (vanilla do-nothing) or a probe row pointing at the body donor's own vanilla goal [game].
- ChrModelParam (memory class as the destination's vanilla bosses), ScratchedPartsParam, LockCamParam: clone the donor rows
  [data].

## 3. Helper rows

- Zero-mesh emitter actor: teamType 0, hp 1, hit sizes 0.001, very high turn rate, lockScoreOffset -1000, the boss's
  SfxResBankId and scaling links [data].
- Invisible HUD / HP carrier: a clone without drawable geometry (`skeleton_model.md` 5) [game]. Avoid a CharaInit-based
  helper (player-like chr): its HP followed CharaInit, the bar emptied at once [game, cause inferred].
- Helpers carry no innate attack rate and no depth link: their hits were "no threat" until their AtkParam rows were scaled to a
  target ratio of a boss hit, and they need their own ChaosMatchingCorrectParam row whose 5 SpEffects keep only the attack
  rates (vanilla precedent: attack-only depth rows for event-enabled split enemies) [game]. Strip inherited multiplayer / depth
  links when the event scales helper HP itself (no double scaling) [game].
- **Party HP of helpers under Seamless Co-op**: characters without a multiPlayCorrection id (helpers, summons) are not scaled at all -
  they stayed at NpcParam HP in 3P [game-MP]. Scale them yourself from per-slot presence (Player No 1..6 present) with maxHpRate SpEffects
  (copies of a vanilla row with only maxHpRate changed); never key it on "boss has 7867 / 7967" (section 5).

## 4. Damage

- Final attack power = AtkParam value x the product of every active attack-rate SpEffect (Nightlord innate x3.36; a phase row
  may add more, e.g. Heolstor phase 2 x1.12) [data].
- Transfer from source motion values: proposed raw total = K x (source motion value + element), keeping the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ row's physical :
  element split; anchor K on one well-understood move (a small fireball: K = 3.0 raw points per MHW point); stream / tick rows
  get only the anchor ratio (hit rates differ between games); one-of-a-kind "certain kill" moves stay explicit [data].
- Usage weighting: weight each move's largest hit by its source frequency (from the AI model) and compare the expected hit per
  chosen move with the Nightlord per-move mean (262) / median (280) [data].
- Compare in MULTIPLES of the vanilla Nightlord median in-game hit (941 after x3.36), not in player-HP shares: player defence is
  not in the tables and a guessed defence gave implausible shares [data].
- The tester kept the source-derived values instead of a proposed re-scale: present the comparison, do not apply it [game].
- Strength sets: base x the source's own per-family ratio (`attacks_hits.md` 8).
- **Attack multipliers after part breaks**: a permanent self SpEffect (effectEndurance -1, spCategory 0, unique id) with the five
  AttackPowerRate fields multiplies with innate 7767 and the depth rows; it scales TAE attacks, bullets and boss-owned EMEVD Shoot
  Bullets, not flat changeHpPoint losses; each machine sets it on its own copy from network flags [code]. Damage after defence grows MORE
  than the rate for small hits (steep curve): x1.35 attack gave x1.7-1.9 damage. When the tester quotes linear targets, solve the rate on
  the curve (x1.35 / x1.75 became 1.16 / 1.67 and the tester took them) and say so [model, game decision].
- "Certain kill unless X" (corrected: was a flat / % max-HP loss SpEffect per machine): a real lethal hit from the boss, guardable from
  the front if wanted - recipe in `attacks_hits.md` 4.7 [game, game-MP]. The old flat-loss route (token hit + one positive changeHpPoint
  SpEffect per machine on its own player, source fixed values scaled by a reference hero's HP ratio, e.g. a 200-HP hunter ~ a 1000-HP
  hero) still works where the tester prefers a survivable loss [data, built].

## 5. HP

- **Max HP = trunc(f32(base x f32(product of maxHpRate)))**, single precision, truncated [code; game: a DLL log read 26280 = 7424 x 3.54].
- **Seamless Co-op party factor sits inside the f32 rate product** (refines "a session factor multiplies maxHpRate under an unknown
  flag"): boss max HP = trunc(f32(hp x f32(3.54 x DN x (1 + 1.2 (n - 1))))), i.e. x1.0 / 2.2 / 3.4 / 4.6 / 5.8 / 7.0 for n = 1..6
  (+120 % per extra player; measured at 2P / 3P, the 4-6 values come from the formula [inferred]); e.g. 211,982 = trunc(9032 x f32(3.54 x 1.95 x 3.4)) at depth 4 (Deep Night SpEffect 877674 = 1.95);
  multiplying the truncated HP afterwards gives 211,979, and other bosses' logged HP discriminate the same way [data + arithmetic,
  game-MP]. It replaces the vanilla MultiPlayCorrection SpEffects 7867 / 7967, which never appear on the boss under Seamless Co-op:
  logic keyed on "boss has 7867 / 7967" never fires there [game-MP]. Write this formula into every HP / part table.
- **HP is fixed when the character is ENABLED**, for the party at that moment: a phase-2 body enabled after a player left got 2-player
  HP [game-MP]. Do not top up in events (it would multiply on top) [inferred].
- **Benchmark against a stated vanilla mean**, in NpcParam terms: the 7 regular Nightlords' main-body hp = 24,614 / 7 = **3,516.29**
  (Gladius 3200, Adel 3712, Gnoster 3680, Maris 3584, Libra 3686, Fulghor 3360, Caligo 3392; final boss, DLC and Everdark rows left out);
  with Heolstor counted as one entry of 1408 + 2880 the mean of 8 is **3,612.75** [data, arithmetic]. Always say which mean.
- Targets that played: a single-phase large boss at 1.7 x 3612.75 = 6142 was a step, not an end point (refined): a three-phase boss
  went 1.7 -> 2.5 -> 2.1 x of 3612.75 (final hp 7587), each a tester decision; a two-phase hovering boss went 0.7 -> 1.0 / 1.3 -> 0.75 / 0.9 x of the
  7-Nightlord mean (2637 / 3165, rounded half up) within days [game]. Offer steps (e.g. 1.7 / 2.1 / 2.5, or per-phase multipliers) with
  solo and party numbers. Two phases ~+14 % total effective HP over Heolstor also played; Deep Night link 7767 (scales like a Nightlord)
  or 0 (exempt: HP unchanged at a forced depth 3) - both shipped, ask [game].
- Heolstor reference: only the unplaced rows carry 7760; the placed rows carry 7767 like the other Nightlords (same rates); phase 2
  also carries 7352 (maxHpRate 1.1): effective solo 1408 x 3.54 + 2880 x 3.54 x 1.1 = 4,984 + 11,215 = 16,199 [data].
- **Absolute-HP audit before changing HP** [data, code]: absolute HP compares (`IF Character HP Value`) only at the floor (<= 1); every
  SpEffect on the boss has changeHpPoint 0 (fixed-point damage SpEffects belong to the players' side only); phase / special thresholds
  are ratios; the AI Lua uses only `GetHpRate`; TAE-applied SpEffects do not change HP by points; part bases (section 8) are the one
  thing that does NOT follow base HP. With all of this true, NpcParam.hp is the single knob.
- **An HP change is a targeted cell patch with anchors** (old value asserted): an HP-only change touched exactly 2 cells (both boss
  NpcParam rows; a helper row with hp 1 stays) [data]; never regenerate a whole event or table for it (other features' edits live in the
  same files). Read the regulation back (only those cells changed) and publish the expected max HP per party size and depth; the tester
  compares it with the DLL log.

## 6. Field / Shifting Earth bosses and large enemies

- Clone the NR stand-in row of the tier (tier, co-op and day scaling stay NR's), put the source identity in [game].
- Anchor: source raw HP x source area scaling ~ NR raw HP x NR tier HP factor (e.g. 922 x 4.4 ~ 2760 x 1.47); damage scaled by the
  same comparison [data; difficulty not tested].
- Rewards: runes via TAE JT12 (or 47) in the death clip - the death finaliser pays getSoul x rate once, to each machine's local
  player; a death clip without it pays nothing [code]. Orb drops via `rewardItemLot` + its chaos-matching twin (+10) [game].
  Health bars and "great enemy felled" come from events, not rows (`ds3-nightreign-port`) [game].

## 7. The part-damage path (what each lever scales) [code: CalcDamage 0x439e80 -> total 0x6c5fc0 -> part control 0x617960 -> decrement 0x5ce700]

1. D = 5 elements x 8 scalar factors, floored at 0 and >= 1; D already contains defence, absorption, SpEffect rates and the NpcParam
   part rate - so `weakPartsDamageRate` scales HP damage AND part damage alike (cutting 2 -> 1.2 cut head-part damage by 40 %) [code;
   game: head numbers exactly x1.2 of body]. Which capsule selects which rate: `physics_hurtboxes.md` 4.
2. 0x617960 walks the victim's records in slot order and calls 0x5ce700 for EVERY record whose group (+0x134) equals the hit capsule
   group `[dmg+0x264]`, and for its 2004[93]-linked records. 0x5ce700: x = D x DamageCorrection (+0x110), x BulletMultiplier (+0x114) if
   the hit is a bullet, max(0, x); the part loses trunc(x) unless already < 0 (at exactly 0 it still loses); return = max(0, x x
   BodyDamageCompensation (+0x118)). **Only the FIRST matching record's return becomes the HP damage `[dmg+0x280]`**; other records only
   lose part HP; with no record in the group, HP damage = D. Return 0 for invincible (+0x11d) or dead (+0x11e) records.
3. **`Create NPC Part` 2004[22] = (entity, part id, group, base HP, DamageCorrection, BodyDamageCompensation, Is Invincible, ...)**: DC
   scales part and HP damage, BDC only HP damage, the bullet multiplier both for bullets. Re-creating an existing (entity, part) rebuilds
   it in place, resets the bullet multiplier to 1.0 and SE / SFX to -1 (= use the hit's own sparks and sounds). `Set NPC Part HP` (flag 0 /
   1) and the ~1 s engine rescale write only base / max / current, never DC / BDC / multiplier.
4. **Part records are a small global table**: CSEventPartsDamageCtrl has 40 slots shared by every entity; a Create into a full table
   fails silently - count slots per fight (15 used in one fight after per-part multipliers) [code].
5. **Per-part HP multipliers without touching breaks** [code; game: logged‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ ticks x0.90 / x1.10 / x0.85 of base]: one never-breaking
   carrier record per non-head group (base 999999, DC 1, BDC = multiplier) created before any other record of that group; the breakable
   record of the same group gets the same BDC (slot order then cannot matter); BDC > 1 works (vanilla uses only 0.5 on armour records via
   common 90075660 with HP shared by 2004[93], and 0.1 once in 90075360). Breaks need exactly the same hits; only the shown numbers
   change. Accepted table on a dragon: chest / forelegs 1.10, neck 1.00, wings 0.95, body / hind legs 0.90, tail 0.85, head 1.20 (stays
   highest); overall damage change ~+0.1 %.
6. **Localising source hitzones** [model; tester approved]: effective source value e = 0.5 Sever + 0.2 Blunt + 0.3 Shot; m = 1.2 x
   (e / e_head)^gamma; choose gamma so the damage-weighted mean of the non-head multipliers = 1.00 (gamma 0.263 there); round to 0.05;
   offer x0.5 / x1.5 width variants (scale the deviations from 1.0).
7. **Carriers must never reach 0**: 999999 x rate is 3.54 M solo, ~54 M at 6P / depth 5 (int32-safe up to rate ~2,000). Below 0 a record
   keeps returning x x BDC; after 3 consecutive updates <= 0 it is freed (0x5ced00 / 0x617f70) and the group falls back to x1.0 [code].
8. **Bullet-only part reduction, HP damage unchanged** [code; game: a probe showed bullets x0.67 while head numbers stayed x1.2]: create a
   group HP carrier (999999, DC 1, BDC 1) BEFORE the head record, then `2004[25] Set NPC Part Bullet Damage Multiplier(entity, headPart,
   k)` right after the head Create (k 0.5 / 0.67 shipped), and top up the carrier at every re-arm. The carrier does NOT absorb the
   decrement (every matching record is decremented) - an earlier "carrier absorbs" theory was wrong [code; game probe]. 2004[25] alone
   also lowers HP damage; vanilla never uses it. Fallback: a linked counter part in an unused group carrying k and all break logic,
   `2004[93](e, head, counter, -1, -1, -1)` (0x6185c0 writes the id list into each record, +0x150).
9. **"Bullet" is the engine category**: `[dmg+0x3c]`, copied from descriptor +0x34 = BehaviorParam refType of the creating behaviour (0
   attack, 1 bullet, 2 SpEffect), travels in the full hit packet (+0x8a). Player arrows and ranged weapon arts counted [game, game-MP
   fit]; skill AoE waves / explosions are bullets too; melee, weapon buffs, damage over time are not [inferred].
10. **Not possible natively** [code]: per-attribute (slash / strike / pierce) part scaling; scripted refunds (EMEVD only sets absolute
    part HP); arrow-vs-melee tests (4[30] `IF NPC Part Attribute Damage` tests the damage attribute only); Bullet / Magic params have no
    part field; SpEffect applyPartsGroup is a filter, not a scale. A DLL damage correction in the hit hook is wrong in co-op (remote full
    hit packets go 0x51f040 -> ApplyDamage directly, past a private-vtable slot-7 hook): keep hooks read-only (`diagnostics.md` 1).

## 8. Break durability, depth and party scaling

1. **Part max = trunc(f32(base x f32(product of maxHpRate)))**; evaluate every f32 multiply order when picking integer bases [code, data].
   Part HP lives per machine in the parts object (decrement: section 7). `Set NPC Part HP(e, p, v, 1)` sets base = v, max = trunc(v x
   rate), current untouched; `(e, p, 9999999, 0)` sets current = max. The engine re-applies max = base x rate about once per second; a
   part below 0 takes no damage until re-armed [code].
2. **Choose the depth / party rule by design goal; it is a tester decision** (refines "constant thresholds via per-depth bases", which
   is only option a) [game]:
   - (a) constant absolute durability: per-depth bases (pick the integer whose 1 / 2 / 3-player max is closest to the depth-0 max, error
     <= +-21 HP; e.g. 1500 -> 1200 / 1071 / 955 / 769 / 694 for depth 1-5);
   - (b) constant fight progress: no depth division (the part scales like boss HP) and a party factor equal to the boss's (1 + 1.2 (n - 1)).
   With (a) + a x n party rule, at 3P depth 4 the break came at ~1/2.2 of the intended fight fraction (boss x1.95 x 3.4 vs head x3). One
   tester chose (b) for the head and kept (a) for chest / wings.
3. **Party re-base with an engine test** (corrected: "Create NPC Part is already scaled by party - do not multiply yourself" is true for
   vanilla 7867 / 7967, unproven under Seamless Co-op): at Create, at the 5 s re-base and at re-arm test `IF NPC Part HP(e, part, G, >)`
   with G = ceil(1.5 x max over depths trunc(f32(f32(3.54 x DN_k) x base_k))) - 1; above G the engine already scales; else `Set NPC Part
   HP(e, part, base x (1 + 1.2 (n - 1)), 1)` with n = the host's present-player count (per-slot presence). Assert G >= every solo max and
   G < the smallest party max; keep diagnostic flags for which path ran [code, sim].
4. **Break timing model** [model]: fight fraction at the first break ~ part max / (k x boss max HP x head share). Targets that played:
   solo ranged with ~75 % of damage on the head -> first break around mid-fight (head damage ~38 % of boss max HP); melee first break after
   ~2 min [game]. A real 3P party put only 42 % on the head: ask which aiming style the target assumes; ask targets as HP-bar fractions.
5. **Second break**: re-arm base = 4/3 of the first (one tester's rule; "slightly harder, the first gives a long knock-down"). Re-arm
   `(v, 1)` then `(9999999, 0)` in the SAME frame as the break test. **`IF NPC Part HP` returns TRUE for a missing record** (0x5a08b0 sets
   true before the lookup) and a record <= 0 for 3 updates is freed: a watcher that starts late (e.g. after a 5 s re-base wait) fires both
   breaks in consecutive frames, and a probe running before the fight-start Create reads "broken". Start the watch right after Create
   [code, sim]. `IF NPC Part HP(.., T, '<')` means current <= T - 1 [code].
6. **Record lifetime**: records are freed by creator id (+0x13c) when the creating map event script unloads / reloads, not when the
   creating event ends [code, inferred].
7. **Host-only break decision** (corrected: was "first machine at 0 commits, the others adopt") [code, sim; game-MP plausible]: part HP is
   decremented only where ApplyDamage -> CalcDamage runs (local hits and full hit packets; compact HP packets do not touch it), so the host
   counts everyone and a client misses the host's own hits - but a client copy can still reach 0 from its own hits, and "first machine at
   0 raises the network flag" broke the head early. Pattern: wait for `(part HP <= 0 AND (Player Is In World Type 0 OR Multiplayer State
   4)) OR networkBreakFlag`; only host / solo sets the flag; every machine runs the break lines (masks, SpEffects) on the flag; the forced
   knock-down stays host-only; replay the flag for late joiners from the host refresh.
8. **When base HP changes by s, rescale the absolute part bases** [sim]: multiply every free base by s (head, chest, wings, re-arm
   values, co-op bases), then re-derive guards, party values and per-depth picks with the original formulas (plain round(old x s) differed
   by 1 in 8 of 22 values; first assert the formulas reproduce every old number). Break positions in the HP bar then held within 0.125 %
   (head) / 0.10 % (chest, wings) at every depth and party size. Ask about EVERY breakable part when a durability / HP number changes, not
   only the one the tester names (a rescale that forgot chest and wings moved their breaks ~19 % later in the bar). Unaffected:
   changeHpRate losses (set pieces, breath ticks), flat changeHpPoint losses on players, HP-ratio gates [code].
9. **Multi-knob requests**: restate the effect per attack class in body-equivalent damage, part HP / (weak x k), before building. Three
   stacked changes (weak 2 -> 1.2, part HP x2, bullets x0.5) gave x3.3 melee / x6.7 bullets instead of the x2 asked, and the head "never
   broke" [game].
10. **Stance pool under Seamless Co-op** [inferred]: the vanilla 2P / 3P saReceiveDamageRate 0.55 / 0.3 (7867 / 7967) are absent, so stance
    breaks may come ~3x sooner than for a vanilla 3P Nightlord; offer a party-scaled stance option with numbers.

## 9. Measuring break progress

1. **Trainer / external damage multiplier pitfall** (confirmed by the tester): during a solo head-break calibration run part HP seemed to
   drop only ~0.2 per displayed damage point; the tester confirmed an external trainer's damage multiplier was on. Such multipliers scale
   HP damage but not the part counter, so the "0.2" is a trainer artefact, NOT an engine factor - the code‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ decrements ~1 part HP per point
   (section 7) and co-op pack fights fit that [game, code]. Rule: before using any log for calibration ask whether a trainer / damage
   multiplier, HP lock, buffs or level changes were active; calibrate with them off, or divide the part loss per displayed point by the
   multiplier. Bases tuned while one was on are off by that multiplier. Hints in a log: all hits multiples of 10, x2 jumps between two
   fights.
2. **Log-only probes** (part thresholds -> distinctive tiny HP losses logged by the damage DLL): `diagnostics.md` 6. Thresholds are
   absolute (valid for the tested depth / party only); never ship or pin a probe.
3. **Classify hits by the boss's hit reaction, not by position**: a boss-local "head box" over-counted neck / chest hits and gave a 13-16 %
   head share once (real 72-75 %). On the c4510 graph, 9090 = weak-part group 31, 9100 / 9110 / ... = PartBlend n per group (76 of 79
   matched the posed geometry); or use value pairs (the same attack x1.2 = head) [game, data].
4. When flags are not logged, reconstruct breaks from forced animations in the host's log (the knock-down id) and from variant ids that
   prove which flags were set; measure the client clock offset on replicated AI attacks (+0.48 s on one pack) [data].

## 10. DPS / pacing benchmark [model]

1. **60 s stake benchmark**: stationary player capsule r 0.4; 12 starts (4 / 12 / 24 m x 4 directions) x 10 seeds = 120 runs per cell;
   real AI (decompiled vanilla scripts, installed bytecode in a real Lua); moves via TAE / BehaviorParam / AtkParam / Bullet geometry;
   reference Wylder L15 (HP 1120, defence 156, absorption 19 %); damage = attack x mult(r = attack / defence) x (1 - absorption) with the
   Elden Ring curve (0.9 for r > 8; 0.9 - 0.2 ((8 - r) / 5.5)^2 for 2.5 < r <= 8; 0.7 - 0.5 ((2.5 - r) / 1.5)^2 for 1 < r <= 2.5;
   0.1 + 0.1 ((r - 0.125) / 0.875)^2 for 0.125 < r <= 1; 0.1 below) - NR keeping this curve is [inferred]. Vanilla Nightlord cells median
   ~7,480 per 60 s; accepted targets on one port: phases 1 / 2 at 1.06 / 1.13 x median, final form 1.96-2.40 x [game decision].
2. **Model rules that changed results**: one hit per TAE attack event per target; child bullets share the parent's hit list
   (`isUseSharedHitList`; independent lists raised the port x1.7-1.9 and vanilla almost not); lingering ground fire re-hits per
   `dmgHitRecordLifeTime`; report sensitivities (2 s knock-down protection, second minute only); list scripted set pieces separately.
3. **The simulator was not bit-reproducible across processes even with fixed seeds**: measure a pure rate change by paired re-scoring of
   the baseline hit lists with attack x m; do not trust cell differences inside the 95 % intervals [data].

## Unverified

Whether changeHpPoint ignores damage negation; whether the Seamless Co-op party factor enters NPC part max; solo break timing in a pack
without a trainer; Deep Night SpEffect application time; K = 3.0 beyond its anchor move; the Elden Ring defence curve in NR; stance
scaling under Seamless Co-op; whether 7767 rates apply to EMEVD-fired bullets.
