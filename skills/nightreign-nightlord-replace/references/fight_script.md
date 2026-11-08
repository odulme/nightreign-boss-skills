# Fight scripting (EMEVD): hooks, skeleton, start, bar, music, phases, parts, victory, defeat, credit, key items

Tags as in `ids_and_planning.md`. Vanilla event / flag / param ids found on NR 1.3.3.0 + regulation 10350000. EMEVD basics:
forward GOTOs only (loop with END / RESTART; backward GOTOs are ignored or end the event [game]); every wait bounded.
Arena / map-block building (MSB, collision, gparam, worldmsblist) is the topic of the skill `nightreign-map-port`.
Pipeline stage: S8 "Fight script + arena" of `nightreign-boss-port/references/boss_pipeline.md` (gate: [game] arrival ->
victory in the dev entry; collision audit 0 orphans).

## 1. Vanilla day-3 flow you hook into [data]

- Field -> staging area (Spirit Tree hub, m12): common 90005910 (beacon button) warps each player itself (per machine).
- Hub arrival 12002000: flag 9052, `Bonfire-like Recovery`, flask refill; solo only (`Multiplayer State 4`): SpEffect 6999500 =
  solo auto-revival token on 20000.
- **Gate 12002001**: waits `9052 AND All Players Inside Area 12002200`, 1 s, `GOTO IF Targeting Boss 7 / 8 / 9` -> m18 / m16_00 /
  m16_10, every other target -> m19 point 19002200 via `Play Cutscene To Player And Warp(12000010, ...)`; sets network 7510;
  disables the merchant. Every machine runs it itself. **Late / reload gate 12002099**: 7510 already ON -> `Warp Player With
  Player No(19, 0, 0, 0, 19002200)`.
- **The target's arena block is loaded TOGETHER with the hub**: its events 0 / 50 run on hub arrival; the gate is a warp, not a
  load [game]. Decide anything item-dependent at the gate, never at arena load.
- m19 map variation = the selected Nightlord (NightBossMenuParam row: 0-6 normal, 10-16 Everdark); events can only read it
  (`Map Variation` conditions); nothing sets it.
- Victory chain: common 90075901(boss, bgmConv, nameId): HP 0 -> 509 on players, network **7513**, 5 s, "NIGHTLORD FELLED", BGM off,
  network **7512**, `END IF 7516`; then the arena's 19002590: 7512 -> Text Effect 4000 VICTORY -> 15 s -> **7000** -> result
  screen. The felled text is picked by `Player In/Out Map` 16 / 16,10 / 18 / 19,0 only.
- Credit tail in the arena's event 0, keyed on the variation: 90075920 (defeat flags), 90075931 (Everdark unlocks), 90015200 /
  90015201 (trophies), 90085027 (missions). Relics, flag 110 and the antique lottery always go to the SELECTED target (engine side).
- Defeat: common 1180 (MP) / 1181 (solo), gated on 7500 + (7510 or 7515): revival token 6999500, Wandering Grace 540155,
  6999100, else DEFEAT 4010 -> 7516 -> 7001. 1182 = per-player standing flags 7005-7007, 1183 = self-revive 7010-7012, 1184 =
  host clean-up after a leaver.

| flag | meaning | flag | meaning |
|---|---|---|---|
| 7500 | expedition active (common 1100: `Game Mode(2) OR 69991`) | 7516 / 7519 | defeat record |
| 7510 | gate passed (day 3) | 7530 | boss-fight flag (90015020) |
| 7511 | fight started (90075900) | 7000 / 7001 | clear / game over |
| 7512 | Nightlord defeated | 7005-7007 | standing players |
| 7513 | boss HP 0 | 9052 | in the staging area |

## 2. Vanilla constructor events: keep or replace [data; shipped in a playable in-arena replacement]

| event | does | rule |
|---|---|---|
| 90075100 | hide bar + camera 7510 | keep |
| 90075101 | fight start: bar, name, BGM, forced 30029 / 20029 | hard-codes the vanilla boss: replace by a LOCAL copy with your BGM conv, NpcName, clips |
| 90075900 | start on region 19002801 or damage -> network 7511 | keep in-arena; own block: write your own start |
| 90075901 | victory | re-point args (boss, own BGM conv, own NpcName) |
| 90075902 | host Forced / client Normal network authority, restarts on host change | keep for EVERY boss entity |
| 90015012 | Activate Multiplayer-dependant Buffs | keep per boss entity |
| 90015020 | sets 7530 | keep |
| 90015008 | BGM heat-up | keep with your conv id |
| per-boss decor / weather events | vanilla boss only | drop |

90015008 args: `(startFlag 7511, endFlag 7512, bgmConvId, boss, heatSpEffect, hpRatioBits)`; with heatSpEffect 0 the last
argument is a float (int bits) and heat-up fires at that HP ratio (0.7 worked) [data, game].

90075101 hard-codes the vanilla boss's NpcName in `2003[11]` (bar) and `2003[102]`; copy it into the map EMEVD as a LOCAL event
with your name id and redirect every caller for your entity from `InitializeCommonEvent 2000[6]` to `InitializeEvent 2000[0]`
(slot 0); read back that no caller is left [data; game]. Patching 90075901's name argument changes only the victory banner
(2003[100]), not the bar [game].

## 3. Two placements

**In-arena (inside the target's vanilla block)** [game]:
- Make every mod part variation-agnostic (MSB `Variation = -1`); if your boss took a vanilla part's slot, restore that vanilla
  boss as a separate part with a free id, or that target's normal runs break.
- Event 50 (REAL path): disable every variation's Nightlord, minions, Everdark entities, decor groups and your own parts; start
  a decider. The vanilla branch must re-enable everything before the deferred vanilla body runs (freezing AI left minions
  frozen).
- Decider waits for the gate commit (or an in-arena reload: 7510 + player in map) and branches on the gate decision.
- Arrival guard: black + freeze for at most ~6 s with a hard fail-safe fade-in. **Never FadeToBlack / Freeze in the hub around
  the gate**: it cancelled the gate cutscene -> permanent black [game].
- **Cost for every other fight**: an arena block's MSB loads ALL its characters and their AI scripts in every expedition that
  targets the block, whichever Nightlord is fought; EMEVD disable does not unload a character. A mod boss placed as 13 MSB
  characters (5 AI scripts) in m19_00 was resident during other bosses' fights and shares their AI Lua heap [data, game log;
  `ai_lua.md` 4]. Prefer an own block that only its route loads, or spawn extra bosses / helpers on demand [inferred].

**Own block (new map block entered in-world)** [game]:
- The hub AND the target's vanilla arena stay loaded with their scripts running during your fight. **Never raise 7511** (the
  vanilla arena starts its Nightlord, bar and BGM on it). At the kill raise 7513 then 7512 + `Increment Team Bosses Killed(1)`;
  the target arena's own 19002590 + credit ends the expedition. Safety net: `7512 -> 25 s -> set 7000 if still OFF`.
- Entry: the gate's in-world `Play Cutscene to Player and Warp(12000010, 0 | 16, <arrival region>, <block map id>, ...)`;
  late gate `Warp Player With Player No(<area>, <block>, 0, 0, <region>)`. A loading-screen `Warp Player` drops hub + arena and
  wipes ultimate-art charge and some buffs: rejected [game].
- Placement [code]: a legacy block's world position is set once per load from MapConnection‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ regions of already-loaded blocks
  that name it; nobody names it -> absolute (0, 0, 0) of the current floating-origin world. In a real expedition the hub sits
  ~400 m above an open-field frame, so an unanchored block lands far below the hub. Fix: a MapConnection region in the hub MSB
  naming your block, and the block's content translated clear of hub and arenas (vanilla arenas sit hub + (0, -30, -500..-650)).
  A block that is neither current map, warp target nor named by ConnectCollision of the current ground hit is unloaded ~3 frames
  later [code]. Never add a ConnectCollision from an open-field tile to your block. A new block is registered through
  `map/worldmsblist.worldloadlistlist.dcx` and runs its script [game]. Its flags need an existing block's storage
  (`ids_and_planning.md` 3). A cloned block whose content was translated also needs its navmesh moved / rebuilt or path-moving
  summons stand still (`nightreign-map-port` collision-traversal.md 6) [data, game].
- `Player In/Out Map` matches exactly (area, block, region, index; only -1 is a wildcard) [code]; "Inside Play Area" is true in
  such a block (no play-area circle outside area 60) [code].
- If the target is Heolstor (m18): its arena starts its own fight 60 s after 7510 (common 90075701 timer): ship a wrapper that
  ENDs when the gate went to your boss [data, sim].
- Location name on arrival: "?PlaceName?" showed for a new block [game]; fix used: LocationTextID 0 (or a real text) in the block.

**Show build in a vanilla arena slot (dev only, before any own map)** [game]: replace the target Nightlord's MSB part with yours
(same entity id, variation -1) and keep everything else vanilla; params as new rows (NpcParam from the target's row with very low
HP, NpcThinkParam whose battle goal does nothing, ChrModelParam, NpcName text); a hub action button that warps to the arena and a
debug retry / return flow. If a builder generates the return event from an anchor it finds in the arena MSB, point it at the
CURRENT stage's MSB and assert the event exists (a builder silently fell back to the vanilla MSB and dropped it) [data].

## 4. Fight script skeleton (generic)

1. **Event 0 / 50 head**: DEBUG (dev-only local flag) vs REAL. REAL: neutral state, start the decider. Clear only own flag ranges.
2. **Decider / constructor**: own parts on, AI off, invulnerable, pre-fight loop clip; nothing that touches player state.
3. **Arrival / aggro gate**: the boss stays passive (AI off, invulnerable) until the OWN player is in the arena (landing
   region); then a network start flag, a local copy of 90075101 (bar, name, BGM start, roar clip), AI on; 90075902 + 90015012
   + 90015020 + 90015008. Any player's arrival starts it for all.
4. **Phase / special controllers**: HP-ratio or AI-marker triggers, idle-heartbeat gate + time-out, network progress flags,
   rebuild head (`7512 -> END`; `start flag ON -> jump to the current phase from network flags`).
5. **Victory**: 90075901 (or a copy with own music / text) on the LAST entity -> 7513 / 7512; then 19002590 (in-arena) or the
   target arena's own chain (own block); safety net to 7000.
6. **Defeat / revive**: vanilla 1180 / 1181 / 1182-1184 unchanged; only mirror 7516 into your own "lost" flag.
7. **DEBUG-only events** (unreachable when the debug flags are OFF, proven by a static walk): debug constructor, retry dialog,
   exit objects, debug defeat.
8. **Roundtable clean-up (m10)**: every load, clears what the fight / item left (protocol flags, markers, buffs, leftover items,
   weather, every SpEffect the fight put on the player).

**REAL-path audit before shipping**: walk every REAL-reachable instruction (Initialize Event / Common Event) and list everything
that touches player state (SpEffect set / clear, `Bonfire-like Recovery`, warps, HP); diff against a vanilla arena script. A
`Bonfire-like Recovery()` at block load erased consumable buffs (SpEffects with `eraseOnBonfireRecover` = 1) in real runs only
[game]. Never clear 7500-7599 or the revival token 6999500 / 6999501 on the REAL path [game].

## 5. Start, health bar, name, music

- Health bar: `Display Boss Health Bar` / link to the boss with the NpcName id from `msg/<lang>/item_dlc01.msgbnd.dcx` NpcName.fmg;
  ship zhocn, zhotw, engus, jpnjp (a missing language shows a placeholder) [game]. In-world own block: the vanilla arena's bar
  appears only if you raised 7511 [game]. The bar name comes from your copy of 90075101 (section 2), not from NpcParam.nameId.
- **Names in every language the game ships**: boss, phase, attack and summon names (NpcName, used by the health bar and by summon
  nameIds) existed only in Simplified Chinese and English once - the bars showed BLANK names in Traditional Chinese and Japanese
  [game]. An NpcName id missing in every language shows "?Name?" (a talk-menu title on an invisible helper shows that helper's
  NpcParam nameId) [game]. Run an id x language audit of every text id of the fight / hub before every release [data].
- **Official names from the source game's own text tables**, not machine translation: e.g. Granblue Fantasy Relink keeps them in
  msgpack tables `system/table/text/<lang>/text_battle.msg` and `text_chara.msg` (a minimal msgpack reader is enough); 4 of 13
  machine-made Japanese names differed from the official ones [data]. The official Traditional Chinese localisation is not a
  character conversion of Simplified Chinese (several names differ entirely): let the owner choose, and say where the source has
  no row (mod-only terms).
- Phase 2 as a separate entity (Heolstor pattern 90075703): own MSB part, cloned NpcParam with switched display masks, own
  NpcName; 90075901 only on the phase-2 entity; 90075902 + 90015012 on it keyed on a network phase-2 flag. Trigger: phase 1
  immortal, `HP <= 1 OR dead`. Transition: network flag -> fade + freeze -> each machine warps ONLY its own player -> phase 1
  disabled, phase 2 enabled + warp + intro clip + AI on -> fade in -> bar. A reload with the phase-2 flag ON shows phase 2 [game].
  Under Seamless Co-op the phase-2 body's HP is fixed for the party present when it is ENABLED (`balance.md` 2) [game-MP].
  Phase-switch warp points (one per player, 6 under 6-player add-ons) must be floor-checked against assets, not only collision.
- **Boss BGM [code, game]**: `Set Boss BGM(convId, state)` (2010[10]) takes the WwiseValueToStrParam_BgmBossChrIdConv row's
  ParamStr and string-compares it (case-sensitive, <= 31 chars) with a fixed array of 114 names cached at init from
  WwiseValueToStrParam_BgmEnemyType rows 10000000..10000113. **No match -> the whole request is dropped silently.** Rows
  10000114+ are never read; there is no free slot. State id = FNV-1 32 of the lower-case name; group "BgmEnemyType". state 0 /
  1 / 2 = start / heat-up 1 / heat-up 2, -1 stop, -2 silent.
  - Slots 22..29 = `_CL_Reserved00..07` are boss class and equivalent in code. Recipe that worked: point your conv row at a
    reserved name nobody else uses and ADD a path for that state key to the top music switch (1001573296) in BOTH
    `sd/cs_main.bnk` and `sd/cs_smain.bnk` (cs_main opens first; only these two banks hold the switch) leading to your own
    music container [game].
  - Check every co-loaded mod's fight scripts for the slot (in one pack: Reserved00 game + a map mod, Reserved01 the game's
    m16_11 row + another mod boss, Reserved02 a map mod). A new name outside the table was silent [game].
  - Long tracks: streamed loose `.wem` (`character_port.md` 11). Victory music: `Play SE` from your copy of 90075901, with your
    own felled-text row (clone FeTextEffectParam 1051 with seId -1) [game].
- Clear your own music / mechanic state flags and stop your music at block load: a previous fight's phase music played again on
  the next run [game: symptom; the clear fixed it, no further report].
- Prompts: replacing on-screen hints with the source's own NPC lines (one per move at its start, adapted nouns, no speaker
  prefix - a tester choice) is a text-only overlay in `EventTextForMap_dlc01` of `menu_dlc01` in every language [game].

## 6. Phases, set pieces, gauges

- **Gates as HP ratios**: HP-ratio conditions on the boss (`4[2]`) inside events worked solo [game]; vanilla keeps such gates in
  the AI (`GetHpRate`). With every gate a ratio (`IF Character HP Ratio` in EMEVD, `GetHpRate` in the AI) a base-HP change needs
  no event edit; keep absolute HP compares only at the floor (<= 1) (`balance.md` 3) [code]. Prefer AI-started specials
  (`ai_lua.md` 6, `coop.md` 4). HP-threshold set pieces are not reachable from a debug move list: test them with "AI off + damage"
  (an HP lock does not block the threshold) [game].
- Idle-heartbeat gate for event-started specials + ~4 s fallback; Lua stops choosing new acts while pending [game].
- Every wait while the AI is OFF: `IF Elapsed Seconds` escape [game].
- **Hand the AI back after a forced clip by condition, not a fixed wait**: replace `WAIT fixed` by `fixed OR (>= 1 s elapsed AND
  idle heartbeat present AND busy marker absent)` in one AND group (vanilla 90035012 pattern), the fixed time kept as the upper
  bound (frozen idle 12.8 s -> 0.3 s) [model]. Never inside set-piece chains (it would hand the AI back mid-chain).
- **SpEffect 45 over every forced / scripted clip** (vanilla: saReceiveDamageRate 0, effectEndurance 0, net-synced; TAE type-67
  row from 0 to the clip end on every entry of every event-forced chain, every distance / colour variant included). Without it a
  scripted knock-down drained the stance pool and the engine's `ExecSaBreakDamage` replaced the clip with 8700 / 8060 ("fell,
  snapped upright, fell again with a critical glow"; 12.8 s idle with the AI still off) [game-MP symptoms, code]. JT24 super armour
  does NOT stop stance damage [inferred, code]. AI flight attacks: SpEffect 45 only over the measured airborne span. Details:
  `nightreign-boss-port` `reactions_death_phases.md` / `tae_turning_windows.md`.
- Gauges / cast bars made from a helper's HP: never clear a one-shot HP SpEffect right after setting it (deferred HP writes get
  cancelled -> frozen gauge); reuse a tick id only every >= 0.4-0.5 s; finish with a "set to 1 HP" row; bound every wait [game].
  Counting rules for "break the cast with N Arts": `balance.md` 5.
- Scripted knock-down (part break, siege weapon): host sets a request flag, waits <= 20 s for "not busy" (no set piece pending,
  not airborne), then forces the knock-down event slot; never wait unboundedly for the heartbeat. Host only (`coop.md` 4c).
- **Set pieces that change the arena** (walls, gimmicks, props): a source gimmick splits into a visible asset, a body collision
  and separate invisible player walls (MHW hunter walls, HitFilter 22). A set piece that switched only the pieces with entity ids
  left the walls without an id standing (~27 m2 of floor blocked, up to 23 m high) [model, game report]; a collision part with
  entity id 0 can never be switched [data]. Rule: give EVERY piece (asset, body collision, player walls, projectile-only copies)
  an entity id and‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ switch it in the same wait-free block as the visuals, sync off, on every path (setup, retry, set-piece end,
  late-join / reload rebuild). `2011[1] Activate Hit` is the only collision switch in the 200 vanilla scripts (18 uses; `2011[2]`
  / `[3]` never): vanilla hides the asset, then `Activate Hit(part, 0)` (m13_00 13002800, common 90035212). Collision switching
  is per machine, nothing is sent [data]. Verify `2003[6]` before relying on it (absent from the vanilla scan).
- Contact tests for set-piece props: "boss root inside an MSB box every 0.1 s" is blind to yaw; fit the box with a contact
  simulation (posed prop vertices vs the boss's hurt capsules on a grid x 24 yaws + logged root samples) [model; game OK]. The
  prop animates on every machine; only the host applies its damage and the knock-down [data, game].
- **Sector / cover tests**: EMEVD has no angle or facing condition; the geometric conditions are 3[2] In / Outside Area, 3[3]
  Entity In / Outside Radius Of Entity, 3[7] All Players In / Outside Area, 3[45] Inside Play Area [data]. Build a sector from
  ring cylinders around the apex (`1003[202] SKIP IF In/Outside Area(..., 10000, ring)`) and, per band, the law of cosines against
  an aim-point region A on the axis (angle <= theta <=> |PA| <= c(band)) tested as 3[3] with a Point region as entity B; each
  condition in its own unused condition group (6 m bands matched an ideal 40 deg / 73 m fan to 99.2-99.4 %) [model; game]. Set
  the near edge from the body, not the apex (a flying boss's root stayed at the hover point while the head hung ~19-22 m ahead;
  the sector hit players under the chest) [game-MP]. Shelter boxes have no line of sight (the open side is safe) [data].
- Fire scripted hits at the TAE blast times by splitting a long wait into whole-frame waits around the hit blocks (sum
  unchanged) [game].
- **Patterns through a player**: never lay them by warping an invisible helper onto the player with dummy -1 (`Warp Character and
  Copy Floor(helper, 2, player, -1, player)` had no lasting effect; the helper stayed at its MSB parking spot for many builds; in
  199 vanilla scripts characters are warped onto players only with a player dummy 210 / 220 / 13 / 36 / 900 / 200) [log, model,
  game]. Fire them from the boss: `Shoot Bullet(boss, T, -1, behaviour, 0, 0, 0)` at target T (20000 solo; in co-op the slot from
  host-published one-hot flags, `coop.md` 5) -> invisible stationary root -> child mover with `isOwnerOverrideInitAngle 1` ->
  floor-rule fall (`nightreign-boss-port` `attacks_hits.md`) [code, model; game]. Log the helper's / pattern's position; when a
  sanity guard fails every time, find out what it tests before removing it.

## 7. Part HP / breaks [code unless marked]

Design choices (scaling with HP / depth / party, timing targets, multi-knob requests): `balance.md` 4.
- **Records**: `2004[22] Create NPC Part(entity, part id, group, base HP, DamageCorrection, BodyDamageCompensation, Is Invincible,
  ...)` creates a record in CSEventPartsDamageCtrl, a global table of **40 slots shared by every entity**; a Create into a full
  table fails silently: count slots per fight (15 used after per-part multipliers). Re-creating an existing (entity, part)
  rebuilds in place, resets the bullet multiplier to 1.0 and SE / SFX to -1 (= the hit's own sparks and sounds). Records are freed
  by creator id when the creating map event script unloads / reloads, not when the creating event ends [code, inferred].
- **Damage path** (CalcDamage 0x439e80 -> total 0x6c5fc0 -> part control 0x617960 -> decrement 0x5ce700): the hit damage D
  already contains defence, absorption, SpEffect rates and the NpcParam part rate. For EVERY record whose group equals the hit
  capsule's group (and its `2004[93]`-linked records): x = D x DC (x the bullet multiplier for bullets), the part loses trunc(x)
  unless already < 0 (at exactly 0 it still loses); return max(0, x x BDC). **Only the FIRST matching record's return becomes the
  HP damage**; no record in the group -> HP damage = D; invincible / dead records return 0. Capsule damage types and part rates:
  `character_port.md` 3.
- **Scaling**: `Create NPC Part`: max = trunc(base x product of all maxHpRate) - scaled by stage and Deep Night; re-applied about
  once per second; current follows only while full. Party: true for vanilla 7867 / 7967; **unproven under Seamless Co-op** ->
  engine-tested re-base below. **CORRECTS** the old "already scaled by party - do not multiply by player count yourself".
- `Set NPC Part HP(e, part, v, 0)`: current = min(v, max) - NOT scaled. `(e, part, v, 1)`: base = v, max = trunc(v x rate). These
  and the ~1 s rescale write only base / max / current, never DC / BDC / multiplier. Re-arm a broken part to a scaled threshold:
  `(v, 1)` then `(9999999, 0)` **in the same frame as the break test**. A part below 0 takes no damage until re-armed.
- **`IF NPC Part HP` returns TRUE for a missing record** (0x5a08b0 sets true before the lookup), and a record <= 0 for 3
  consecutive updates is freed (0x5ced00 / 0x617f70): a watcher that starts late (e.g. after a 5 s re-base wait) fired both breaks
  in consecutive frames, and a probe running before the fight-start Create reads "broken". Start the watch right after Create.
  `IF NPC Part HP(.., T, '<')` means current <= T - 1 [code, sim].
- **Host-only break decision** [code, sim; game-MP plausible]: wait for `(part HP <= 0 AND (Player Is In World Type 0 OR
  Multiplayer State 4)) OR networkBreakFlag`; only host / solo sets the flag; every machine runs the break lines (masks, SpEffects)
  on the flag; the forced knock-down stays host-only; replay the flag for late joiners from the host refresh. **CORRECTS** "the
  first machine whose part reaches 0 raises a network flag, everyone adopts" (vanilla 90075865 checks three times 0.5 s apart with
  sync off, then commits): under the co-op mod a client copy reached 0 early and broke the head early (`coop.md` 1).
- **Party re-base with an engine test**: at Create, at the 5 s re-base and at re-arm test `IF NPC Part HP(e, part, G, >)` with
  G = ceil(1.5 x max over depths trunc(f32(f32(3.54 x DN_k) x base_k))) - 1; above G the engine already scales; else
  `Set NPC Part HP(e, part, base x (1 + 1.2 (n - 1)), 1)` with n = the host's present-player count. Assert G >= every solo max and
  G < the smallest party max; keep diagnostic flags for which path ran [code, sim].
- Constant thresholds at every Deep Night depth (design choice (a)): choose the base per depth SpEffect (base / depth factor,
  integer, error ~+-11) at Create and re-base 5 s later in case the depth effect arrives late [code + offline; in-game depth > 0
  unverified].
- **Per-part HP-damage multipliers without moving breaks** [code; game: logged ticks x0.90 / x1.10 / x0.85 of base]: one
  never-breaking carrier record per non-head group (base 999999, DC 1, BDC = multiplier) created before any other record of that
  group; the breakable record of the same group gets the same BDC (slot order then cannot matter); BDC > 1 works (vanilla uses
  only 0.5 on armour records via common 90075660 with HP shared by 2004[93], and 0.1 once in 90075360). Breaks need exactly the
  same hits; only shown numbers change. Carriers must never reach 0 (999999 x rate = 3.54 M solo, ~54 M at 6P / depth 5;
  int32-safe up to rate ~2,000); after 3 updates <= 0 a record is freed and the group falls back to x1.0.
- **Bullet-only part reduction, HP damage unchanged** [code; game probe]: create a group HP carrier (999999, DC 1, BDC 1) BEFORE the
  head record, then `2004[25] Set NPC Part Bullet Damage Multiplier(entity, headPart, k)` right after the head Create (k 0.5 /
  0.67 shipped); top up the carrier at every re-arm. The carrier does NOT absorb the decrement (every matching record is
  decremented). 2004[25] alone also lowers HP damage; vanilla never uses it. "Bullet" = the BehaviorParam refType of the creating
  behaviour (0 attack, 1 bullet, 2 SpEffect): player arrows and ranged weapon arts counted [game, game-MP fit]; skill AoE waves /
  explosions are bullets too; melee, weapon buffs and damage over time are not [inferred].
- Not possible natively: per-attribute (slash / strike / pierce) part scaling; scripted refunds (EMEVD only sets absolute part HP);
  arrow-vs-melee tests (4[30] `IF NPC Part Attribute Damage` tests the damage attribute only); Bullet / Magic params have no part
  field; SpEffect applyPartsGroup is a filter, not a scale.
- Player characters reach lower than source-game hunters: lower or move high break zones (tester request).

## 8. Kill credit to the expedition's original Nightlord

- In-arena: run 19002590 and copy the vanilla credit lines (90075920 x7, 90075931, 90015200 x14, 90015201 x14, 90085027 x8); they
  key on the loaded variation = selected target. Targets 7 / 8 / 9 redirected into m19: skip the m19 variation credit and start
  the m18 / m16 credit inits keyed on `Targeting Boss` [data; game for m19 targets only].
- Own block: the target arena's own chain does it (7512 after 7513); show no own text 4000 [game: real solo expedition settled].
- Several mod bosses in one profile where another mod owns the m19_00 script: patch a COPY of that mod's decider at build time
  so "other boss decided" starts ONLY its end + credit events (19002590 + credit lines, no boss, no music, no bar); the patch is
  anchored on the expected file hash and refuses on any difference [game].
- Heolstor's story ending (18002610 / 620, 6020, Finalize Expedition) is not replicated by a redirect: result = VICTORY + 7000.
  If the target arena finalises by itself, your safety net must END on 6020.

## 9. HUD [game]

- `menu/01_000_fe.gfx` is shared by every fight: restyling the boss-bar list broke vanilla multi-boss bars in real expeditions.
  Keep vanilla placements byte-identical; show custom UI only as mirrors recognised by your baked NpcName strings, as the last
  HUD-overriding step; rebuild it when a boss name id changes. Hide HUD items with alpha 0 as vanilla does, not with an all-zero
  placement matrix (a unique trait removed during a GPU-hang audit) [data].
- Custom buff icons appended to 05_dummy never showed; status icons live in `menu/01_common_{h,l}` / `21_common_dlc01_{h,l}`.

## 10. Test route vs real expedition (what a debug entrance cannot show)

- No expedition (no `Game Mode 2`, no 7500): vanilla down / revive / defeat never start, a downed solo player stays down; build
  your own‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ debug defeat flow and test downs only in REAL [game].
- Hub position, open-field frame, Lua heap of a real world, end-of-expedition screens, credit, co-op: only a real run shows them.
- Stale flags after debug runs (7511 / 7512 / 7513 / 7516 left ON break the next debug fight): in TEST mode only, snapshot then
  clear 7510-7519 + 7530 at staging arrival; REAL never touches them [sim].
- Debug Roundtable objects: an ActionButtonParam clone of 6860 "Examine" on an invisible anchor sets a LOCAL debug flag and warps
  to the arena (or to the hub to test item -> gate -> arena) [game].
- Hub-layer features (key items, hub events) need a dev route too (a dev-only hub event / overlay): two packs that shipped key
  items without one failed (`testing.md` 1).

## 11. Key items in the hub (permanent buffs) [game, after 2 failed packs and 4 dev probes]

- **Grant with `2003[108] Display Network-connected Permanent Buff Popup`** (vanilla once-only grants m10 100002450 and every co-op
  grant; always sync off on the local player, e.g. m19 19004500: `Set Network Sync State(0)` ... `2003[108](131)` + `Set
  SpEffect(20000, 9731)`). `2003[124]` from a Roundtable restart event showed and listed nothing, not even a vanilla control buff.
  Removal = `2003[126]` [game, data].
- **Ids in the vanilla key-item band**: large mod ids popped up but were never listed (three rounds, even with vanilla icons).
  Next free slots after the DLC items (goods 45100-45108, buffs 150-157 / 160, SpEffects 9800-9808, texts 10001000-10001008 in use
  at the time) - a future official item there would collide: re-check after game updates. No param links a key item to a flag
  [data].
- Row recipe: Goods copy of 45023 (goodsType 11, sortGroupId 10, own sortId / iconId, `vagrantItemLotId` = buff id, isDrop 1 as the
  template); PermanentBuffParam copy of 131 + spEffectId; SpEffectParam copy of 9731 + iconId + spEffectTextId_1; texts in the
  `*_dlc01` members (GoodsName / Info / Caption + PermanentBuffName / Info / Caption); list icon `MENU_ItemIcon_0<icon>` in a free
  cell of `SB_ItemIcon_DLC01_0`; large picture `MENU_Knowledge_0<icon>` in `menu/20_solo_dlc01` (tpfbhd / tpfbdt) keyed by iconId.
- **Grant once, behind a flag**: restart event `Set Network Sync State(0) | END IF flag F ON | IF Elapsed Seconds(3) |
  2003[108](a) | WAIT 5 s | 2003[108](b) | Set Event Flag(F, ON)`; F = a hub world-class flag free by a typed scan and not equal to
  any event id; space the grants (same-frame bursts); one guard flag per item if items install separately; every machine grants
  its own player.
- Uninstall: a save holding buffs whose rows were removed loaded fine, orphans unlisted [game, dev save; main-save uninstall
  unverified].
- Probe hygiene for item tests: unique display names per probe entry (two test items sharing a name produced a false "large ids
  work" conclusion and three extra rounds); a vanilla control; report popup and listing separately (`testing.md` 7).

## 12. Arena-side checks for a Nightlord fight (methods in `nightreign-map-port`)

- Keep a table of every collision part with its hit filter and on / off phases: a boss floor made enemy-only, rubble made
  player-only, projectile-only copies and invisible shells later explained bullets passing through "solid" props and ground
  finders stopping in mid-air [data, game].
- Collision ownership audit (offline): replay every `2005[3]` / `2011[1]` of the fight script into phases; flag active collision
  whose visible owner is gone; capsule walk test before / after [model].
- Ledges and invisible walls: one arena-wide scan instead of one fix per report; some fences are intentional platform limits -
  list them and ask [game].
- Summons that path (NpcThinkParam `disablePathMove 0`) need a navmesh at the content's real position [data, game].
- MSB RegionIDs must be unique (vanilla m19 has 0 duplicates in 129 regions; one mod MSB had 5) [data]. Ground seals / decals on
  tessellated terrain: lift ~0.35 m or use a non-tessellated surface (a seal 12.5 cm above the sand showed half missing) [data,
  inferred]; verify by an MSB round-trip that only the Y values changed.

## Unverified

Credit for DLC / Heolstor targets redirected into m19; what `Map Variation` reads inside a non-vanilla block (use `Targeting
Boss`); Seamless Co-op re-join into a running arena; add-bank (SoundAddBankId) sounds on a modded row; an alloc-list line for a
new block; whether the co-op mod's party factor enters NPC part max; `2003[6]` as a collision switch; main-save uninstall of key
items; whether summons move on a baked arena navmesh.
