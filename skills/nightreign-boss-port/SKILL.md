---
name: nightreign-boss-port
description: "MUST verify the source game is publicly released before porting (web search; refuse unreleased, leaked or unconfirmed sources; own assets OK). 移植前必须先联网核实源游戏已正式发售，否则拒绝。把其他游戏的 BOSS 或大型敌人（怪物猎人世界、碧蓝幻想 Relink、黑暗之魂3……）移植进《艾尔登法环：黑夜君临》(ELDEN RING NIGHTREIGN) 离线 me3 MOD，或用自己的模型做原创 BOSS：以 S0-S12 制作流水线为主干，覆盖提取与每招数据表、原创模型绑骨与重定向原版动作、行为图供体、FLVER 与 dummy、受击胶囊、根运动与 TAE（锁朝向、转身/重新瞄准窗口、AI 窗口）、调试面板、判定（吐息、伤害圈、地雷、扇形遮挡）、特效与音效（只改数值槽、HDR 亮度、显卡 TDR）、预编译 Lua 与 AI 堆、血量对标与部位破坏、联机。触发词：移植BOSS、原创BOSS、自制BOSS、BOSS制作流程、动作重定向、绑骨、行为树、AI移植、受击判定、转身滑步、调试面板、特效太亮、显卡崩溃、部位破坏、破头太慢、矮个打不到。English: port a boss from another game (MHW, Relink, DS3 ...) or build an original boss for Nightreign: pipeline S0-S12 with stage gates, extraction, Blender rig, retarget vanilla motions, donor graph c2130 / c4510 / c4373, FLVER dummies, root motion, TAE heading hold, turn / re-aim windows, debug panel, AI heap, breath / mine / fan hits, FXR value-slot edits, GPU TDR, precompiled Lua, HP vs Nightlord mean, Seamless Co-op HP, part breaks, pre-release checklist."
---

# Porting or building a BOSS for Nightreign (offline me3 mod)

## Step 0 - MANDATORY before any port: released games only

This step comes first, before every other step of this skill, and is never skipped, shortened or assumed already done.
Before you plan, research, extract, convert or brief anyone about porting a boss, character, enemy, model, animation, effect,
sound or map from another game:

1. **Verify with a web search** (WebSearch or any web tool you have) that the source game - for DLC / expansion content, that
   exact DLC - has been officially and publicly released and is commercially available. Do not rely on memory or on the
   user's word alone: release dates move. Write the title, the release date and the source you checked (publisher or store
   page, or a reputable outlet) into your reply or the plan.
2. **Refuse the port and explain why** when any of these is true:
   - the game or DLC is announced, in development, delayed or otherwise not on sale yet;
   - the material comes from a leak, a datamine of an unreleased build or update, a press / review build, or a beta or network
     test (under NDA or not) of a game that is not out yet;
   - the release status cannot be confirmed: no web search available, or only conflicting or rumour-level results. Then stop
     and ask the user to enable web search or to name an official source; do not continue on a guess.
3. **Allowed without a source-game check**: original bosses built from the user's own models and assets (or assets they hold
   the rights to), and work on Nightreign's own content (vanilla Nightreign motions retargeted onto an original model included).
4. The check is per source: repeat it for every new source game or DLC.

Example: a request to port the Vesper Wyrm of Hollowmere from a game that has only been announced is refused until the game is on sale, however complete the leaked files look.

## Responsible use

- Free, non-commercial mods only. Never sell, paywall or bundle for sale anything that contains another game's assets (models,
  textures, animations, effects, sounds, music, text), and do not help anyone do so.
- Respect the EULAs and terms of service of the source games and of Nightreign; extract only from‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ copies the user owns; credit
  the source game and its rights holder when a port is shared.
- Offline only. Modded Nightreign runs through me3 with Easy Anti-Cheat off and its own save file; never take modified files
  onto the official online service or matchmaking (EAC; bans are possible). Co-op in this skill set means the Seamless Co-op
  mod, which plays outside official matchmaking.

## About this skill

Scope: everything about the boss itself - from "can this boss be made" to a body that looks, moves, attacks, sounds, thinks,
reacts and dies like the source (or the design), with numbers benchmarked against vanilla, shipped through a dev-first loop.
Where it ends up (field boss, arena boss, Nightlord) changes only the integration stages. Distilled from ports and builds that
reached real play: an MHW quadruped flying dragon, a Relink hovering swordsman with helper actors, an original armoured boss built
from its own model, and DS3 enemies / bosses. Only methods that worked are written here; a failure appears as one line "do X,
because Y".

Not repeated here (read them when the stage needs them):
- `nightreign-modding` - me3 package basics and load order, Smithbox, WitchyBND, FLVER Editor / TPF basics, param editing, the
  universal dev / release workflow, QA scoring.
- `nightreign-nightlord-replace` - Nightlord fight integration (fight EMEVD, switch item, hub, kill credit, Nightlord balance,
  co-op flows, release). It owns the Nightlord-specific parts of S0 and S8-S12 of this skill's pipeline; its
  `character_port.md` and `ai_lua.md` are the SHORT version of this skill.
- `nightreign-map-port` (companion skill, not included in this repository) - arenas, map blocks, collision, navmesh, lighting, map-side effects and music.
- `ds3-nightreign-port` (companion skill, not included in this repository) - same-engine-family (DS3) recipes: direct clip / TAE / FXR / FSB conversion, dead subgoals, cloth fix.

**Evidence tags** (strongest first): [game-MP] confirmed in a real multi-machine session (or a replay of its per-machine logs),
[game] confirmed in game by the tester, [code] static RE of `nightreign.exe`, [data] read from files / measured offline,
[sim] offline simulation of event text / AI, [model] offline geometric / particle / damage model, [inferred] reasoning only.
Conflicts are resolved by this order. Exe offsets and vanilla ids were found on NR 1.3.3.0 (PE TimeDateStamp 0x69e0dc2a),
regulation 10350000: re-verify after a game patch. Only [game] / [game-MP] prove a fix; offline PASS results were wrong in game many
times.

## The pipeline (backbone)

Every boss runs through thirteen stages S0-S12, each ending with an exit gate. Full detail per stage (goal, inputs, tasks, tools,
gate with pass criteria and evidence level, typical failures and fixes), the dev-overlay workflow, the tester loop, the pre-release
checklist, the ranked pitfalls and the unverified list: **`references/boss_pipeline.md`**. Earlier versions of this skill used
phases P0-P9: P0 = S0, P1 = S1, P2 = S2, P3 + P4 = S4, P5 = S5, P6 = S6, P7 = S7, P8 = S9, P9 = S8 / S10.

| stage | do | exit gate | read |
|---|---|---|---|
| S0 Plan | **Step 0 released-source web check first (refuse if unreleased / unconfirmed)**; survey, five decisions, fidelity rules, diagnostics plan, shipping configuration, id registry, heap budget per world; route B: G0 contract | release evidence written (or own assets); decisions written, "done" agreed, id checker clean | `boss_pipeline.md` S0, `survey_and_extraction.md` 1 |
| S1 Extract | read-only hashed extraction, own decoders, catalogue, per-attack data table | every motion renders like the source; table per move | `survey_and_extraction.md` |
| S1-alt Model | route B: parts, interfaces, budget, smoothing (G1 / G2) | read-back stats + owner-reviewed renders | `original_model.md` 1 |
| S2 Show build | skeleton, FLVER, dummies on the fixed SFX node, hurtboxes + coverage, part groups, behbnd, minimal anibnd, rows, names in every language; route B: S2a rig, S2b base motions, S2c export, S2d staged render (G3-G6) | [game] visible / lockable / hittable / dies, right bar name; coverage >= 95 % | `skeleton_model.md`, `physics_hurtboxes.md`, `donor_graph.md`, `original_model.md` |
| S3 Debug harness | dev-only move-control panel, sync log, heap gauge - before the first attack | [game] panel plays a move; logs readable | `debug_panel.md`, `diagnostics.md` |
| S4 Motion + TAE | clips, variants, heading hold + turn / re-aim windows, AI windows, event timing, markers, reactions, SpEffect 45 | [game] complete, no slide; heading model = log | `animation.md`, `tae_turning_windows.md`, `reactions_death_phases.md` |
| S5 Attacks | chains, carriers from source data, floor / collision rules, hit height, certain-kill, roll review | [model] per-move tables; [game] each move via the panel | `attacks_hits.md` |
| S6 FX + readability | value-slot FX edits, brightness, coverage, GPU budget, banks, sparks | [game] looks accepted; budget <= envelope | `fx_sound.md` |
| S7 AI | tree -> Lua, fidelity, precompiled small prototypes, heap | [sim] fidelity; [game] heap gauge in a real expedition | `ai_port.md` |
| S8 Fight script + arena | destination flow, set pieces, collision ids, navmesh, breaks, texts, key items | [game] arrival -> victory; collision audit 0 orphans | destination skill; `reactions_death_phases.md`, `params_balance.md` 7-8 |
| S9 Balance | HP vs a stated vanilla mean, absolute-HP audit, part carriers, break durability, damage | tester decision with numbers; log = published HP table | `params_balance.md` |
| S10 Co-op | host director / client follower, isHostSyncChr 0, one judge, per-slot presence, logs from every machine | [game-MP] checklist + aligned logs | `reactions_death_phases.md` 7; nightlord `coop.md` |
| S11 Release | pins from the dev stack minus debug / probes, delta regulation, patch, privacy scan | release vs dev = named dev-only rows only | `boss_pipeline.md` 6; nightlord `release_packaging.md` |
| S12 Live feedback loop | one report -> one dev overlay -> tester -> next pack | dev confirmation before any pack | `boss_pipeline.md` 4-5 |

Routes: A = port from a foreign engine; A' = same family (DS3, via `ds3-nightreign-port`); B = original boss from its own model
(S1-alt, S2a-S2e, gates G0-G8). Destinations: Nightlord / own-block arena boss -> `nightreign-nightlord-replace` for S8-S12 (S9
balance also in `params_balance.md`); field boss -> `nightreign-map-port`.

## When to read what

| stage / question | reference |
|---|---|
| The stages in detail, gates, dev-overlay workflow, tester loop, pre-release checklist, ranked pitfalls, unverified list | `references/boss_pipeline.md` |
| Is this boss portable? Source formats per game family, extraction, clock, labelling motions, catalogue, per-attack data table | `references/survey_and_extraction.md` |
| Original boss from its own model: modelling budget, skeleton design, rig, telescoping tail, coat secondary motion, cloth limits, export, show-build setup, bar name | `references/original_model.md` |
| Donor character, behaviour graph slots, appending states / variant leaves, hks, Force Animation preconditions | `references/donor_graph.md` |
| Coordinates, skeleton hkx, FLVER (template, nodes, weights, materials, textures, display masks, dummies, fixed SFX node), cloth, props | `references/skeleton_model.md` |
| Hurt capsules, physics hkx build and repairs, hkxpwv part groups, capsule damage type -> part rates, coverage check, movement capsule | `references/physics_hurtboxes.md` |
| Clips: resampling, root motion, airborne spans, clip length, variants, stitching, retargeting vanilla motions, bone-chain props | `references/animation.md` |
| TAE layouts and jump tables, heading hold, turn and re-aim windows, Rotate semantics, AI windows, markers, event timing | `references/tae_turning_windows.md` |
| Attack chain, judge ids, melee volumes, streams, impact circles, fans, collision-aware hits, guard shadows, mines, certain-kill breaths, sectors, sizing, hit height, roll review, performance | `references/attacks_hits.md` |
| Effects (convert vs donor, binders, value-slot edits, recolour, brightness, readability, GPU budget) and sounds (bank build, events, voice, budget) | `references/fx_sound.md` |
| Source behaviour tree -> Lua, harness, precompiled bytecode with hoisted helpers, proof set, AI heap per world, AI <-> EMEVD contract | `references/ai_port.md` |
| Rows, damage transfer, HP benchmark and Seamless Co-op formula, part-damage path, carriers, break durability, measuring breaks, DPS | `references/params_balance.md` |
| Reactions, knock-down, SpEffect 45, death, dissolve, part breaks, phase-2 bodies, helper actors, flight, co-op roles | `references/reactions_death_phases.md` |
| Move-control debug panel: architecture, catalogue, reserved ids, release guards, per-move test recipe | `references/debug_panel.md` |
| Sync log, heap gauge, crash dumps, DRED / GPU hangs, log replay, log-only probes, models as evidence | `references/diagnostics.md` |
| Report states, order of proof, previews, installed-state audits, crash table, the tester loop, multi-agent rules | `references/testing_qa.md` |
| Small helpers (Wwise FNV ids, Lua 5.0 lint, offline heading model) | `scripts/README.md` |

## Decision tables

**1. Source -> route**

| source | route |
|---|---|
| Same engine family (DS3, ER, Sekiro-era FromSoftware) | Carry clips / TAE / FXR nearly 1:1 (`ds3-nightreign-port`); keep the source skeleton, ids and Master track |
| Foreign engine (MHW, Relink, Unreal games ...) | Own decoders for mesh / motion / timelines / AI; rebuild everything on an NR donor; NR donor effects recoloured |
| No source game (original design / generated model) | Route B: own skeleton with FromSoftware core names, retargeted vanilla motions, designed attacks and AI (`original_model.md`) |
| Source AI is data (MHW THK, Relink behaviour trees) | Decode to an executable model, port node by node, prove fidelity offline |
| Source AI lives in code, or there is none | Port the observable rules (cooldowns, ranges, HP gates) from a vanilla goal fork; mark every guess as a switch |

**2. Destination -> what changes on the character side** (the body work is identical)

| destination | NpcParam clone source and scaling | benchmark | integration skill |
|---|---|---|---|
| Nightlord / Nightlord replacement | a Nightlord row (innate 7767, party 7767, Deep Night 7767 or 0) | a stated vanilla mean: 3516.29 (7 regular Nightlords) or 3612.75 (8 entries incl. Heolstor 1408 + 2880); hits vs the Nightlord median | `nightreign-nightlord-replace` |
| Arena boss in an own map block | same as Nightlord if it ends an expedition, else the tier row of the slot you take | as above, or the tier's vanilla bosses | `nightreign-map-port` + nightlord-replace fight script |
| Field / Shifting Earth boss, large enemy | the NR stand-in row of that tier (tier, co-op, day scaling stay NR's) | source HP x source area scaling ~ NR HP x NR tier factor [data] | `nightreign-map-port`, `ds3-nightreign-port` |

**3. Donor behaviour graph by body plan** (details `donor_graph.md`)

| body plan | donor | proven slots |
|---|---|---|
| biped / humanoid, sword or caster, hovering humanoid, original humanoid rig | c2130 (Morgott) or another humanoid graph | 41 attack slots, ~19 event slots, steps 6001-6003, generic hks [game] |
| quadruped, dragon, winged flyer | c4510 (Ancient Dragon) | 36 attacks 3000-3038 (no 3018 / 3020 / 3035 / 3039), events 20000/1/2/10/19/20/25/26, loops 30000/5/10/19/25/26 [game] |
| ordinary or DS3-like enemy, smaller bosses | c4373 generic `c9997` | a state for nearly every DS3 id [game] |

No NR graph has a flight locomotion state: flight lives inside attack / event clips [data]. Missing slots are appended
(state or variant leaf), never assumed.

**4. Effects: convert or borrow** (details `fx_sound.md`)

| case | do |
|---|---|
| same engine family | convert the source FXR (DS3: 1:1, GPU trail / 30) |
| foreign engine, particle effects | NR donor effect the tester names, as a byte copy with value-slot edits only; source FX only as look reference [game: converted Relink casts were rejected as "too poor"] |
| flat art (rings, seals, sigils) | new FXR shell with the SOURCE texture [game] |

**5. Big moves: AI act or EMEVD set piece**

| choose AI act + TAE payload when | choose an EMEVD set piece when |
|---|---|
| default; it replicates in co-op for free (48 of 59 vanilla Nightlord ultimates) | arena state must change (walls, map fire, cover); then host director + client follower, clients keep AI on (`nightreign-nightlord-replace` references/coop.md 4) |

**6. Damage carrier**

| shape | carrier |
|---|---|
| claws, bites, body slams, sword swings | TAE type 1 capsules from the source volumes |
| beams, streams | invisible damage bullets from a dummy along the source's breath joint, life = source shell life, floor child per bullet |
| fans, sweeps, waves, anything >= ~30 m or > 1,000 m2 for > 0.5 s | invisible ray bullets r ~1.4-1.6 m, map-collision radius +0x8C 0.1, origin ~2 m, lowest point <= 0.9 m |
| impact circles, delayed mines, player-anchored rows | TAE event on a fixed floor dummy (`isEndlessHit 1`); mines by the floor rule; rows fired from the boss |
| certain-kill / arena-wide breaths | a real lethal sphere centred on the boss, fired by each machine for its own player |
| visuals | separate no-damage owner bullets or TAE 96 - never the damage row |

## Hard rules (each one cost at least one failed round)

Data and engine
1. NR characters face -Z; MHW / Relink motion data is 60 fps; MHW units are cm; Relink attack boxes are half extents. [data, game]
2. FLVER node order [weighted bones][mesh nodes][dummy owners][other bones], second skeleton table depth-first, node flags
   as vanilla (bone 8, mesh 4, dummy owner 2, disabled 1); otherwise crash near the player or an unhittable body. [code, game]
3. Dummy positions are MODEL-space bind coordinates, ids < 1000 (`id % 1000`), unique; **placement dummies are parented to the
   fixed SFX node** - parent / attach -1 binds to node 0, the animated hip. [code, game]
4. Every new hkx: hkRelArray PTCH entries + TYPE section transplanted from a vanilla file with the identical type list +
   PTCH audit MISSING 0 / UNHASHED 0 - else crash at load (exe+0x1A11B59 / 0x182AC83). [code, game]
5. The graph plays only its own states: a new id needs a bound `W_Event<id>` / `W_Attack<id>` state; an animIdOffset variant
   needs a clip leaf `aNNN_<id>` in that selector - else‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the base plays silently. [game]
6. Keep every clip with root motion <= 29.7 s / 892 reference samples; a 45 s / 1,359-sample clip turned the actor by itself. [game]
7. Attack TAEs hold heading (224 = 0 + JT7) and open turn windows only where the source rotates - plus re-aim windows between the
   shots of aimed multi-shot moves; no 224 row = NpcParam default rate; inside an EMEVD Rotate a rate <= 0 means 90 deg/s. [code, game]
8. AI windows (JT23 / 86 / 78 / 79) go after the last content of the full source move (release point), never "last hit + x". [game]
9. Bullet release events >= 0.1 s, markers >= 0.05 s on speed-multiplied clips; the first shot fires at the event start. [data]
10. SpEffect 45 over every forced / scripted clip (and every variant) and over measured airborne spans; JT24 does not stop stance
    damage. [game-MP, code]
11. Damage volumes from the source's own data (spawn joint, size, life), capped by what the visible effect shows; never keep large
    melee capsule sets active over dense map collision; rows >= 30 m use `mapHitType 2`; lowest point of every damage sphere <= ~0.9 m
    above the floor. [game, data, model]
12. Clone donor Bullet / Atk / SpEffect rows, then scrub every status SpEffect reference (a cloned fire row carried deathblight). [data]
13. FXR: byte copies with in-place float value-slot edits only; never change counts, offsets or node links (a 2-byte unlink froze the
    game); never round-trip a vanilla FXR through a writer. [game]
14. FXR binder members 0..n-1 + reslists at 400000 + i; registration stops at the first member id >= 99999; the character's binder is
    `sfxbnd_c<NpcParam.SfxResBankId>`, not `sfxbnd_c<chr id>` - prove it with the me3 log. [code, game]
15. Wwise banks: children before parents, no reference out of the bank, byte-copied vanilla attenuations; budget the TOTAL
    resident custom media (a 108 MB bank stayed silent). [game]
16. Ship AI as stripped precompiled Lua 5.0.2 bytecode with small prototypes (<= ~700 instructions / 128 constants, largest load
    block <= ~3 KB): the 20 MiB AI heap is shared by 4 states and rebuilt per world; fragmentation, not total free, kills it. [code, game-MP]
17. Per-boss AI state only in `ai:SetStringIndexedNumber`, never in Lua globals / upvalues (one chunk serves every instance). [data]
18. TAE 96 records are 32 bytes (StateInfo at +16 is read unconditionally); TAE 129 one-shots use play mode 0. [code, data]
19. Before replacing a clip list every TAE entry that imports it (death entries often import another clip). [game]
20. `isUnduration 0` on creatures without foot IK; diff every cloned row against the source (inherited `hitYOffset` floated a flyer). [code, game]
21. HP gates as ratios; absolute-HP audit before any HP change; HP changes are anchored cell patches; part bases do not follow base
    HP. [code, data]
22. Co-op: every machine runs the whole EMEVD - boss commands under a host test; summons / helpers `isHostSyncChr 0` with AI ON on
    every machine; the host decides breaks and casts; party size from per-slot presence, never `Is Player Count`. [game-MP]
23. Names (NpcName and every FMG text) in every language the game ships, official names from the source; the bar name comes from a
    local copy of common 90075101. [game]

Process
24. Never assign a source motion to a role (death, knock-down, turn, member of a directional family) from its label: measure
    it and ask the tester. [game: death / knock-down swapped]
25. Never present a vanilla mechanic inferred from params / menus as fact; mark it [inferred] and ask the tester.
26. When the tester says "nothing changed", dump the INSTALLED files; when one of two near-identical things fails, make it
    byte-identical to the working one before theorising; compare plain sizes / counts first. [game]
27. After two failed paper explanations ask for a recording; ask what is SEEN before guessing ("slides" = rotation without a
    turn animation); never stack a new paper cause on a piece never seen to work. [game]
28. Rebuild the source's own motion chain and mechanisms instead of generic substitutes; build visible effects from FX already seen
    in game in this port. [game]
29. Preview renders of the WRITTEN files (model, poses on several frames, capsules) before every install that changes looks. [game]
30. One change per overlay in a NEW folder, the dev-only debug package kept LAST; never overwrite installed or frozen-stage files;
    one owner per shared file. Dev first, then pack: every feature that skipped dev failed in a release. [game]
31. Before reading any calibration log ask about trainers / damage multipliers, HP locks, buffs; calibrate in the shipping
    configuration. [game]
32. Agents never launch the game, never touch saves or the live me3 folder; the tester plays and installs releases.
33. Report "built", "installed and read back", "tester saw it work", "tester accepted" as four different states. [game]

## Checklists

Per stage: the exit gates of `boss_pipeline.md`; before shipping: its pre-release checklist (section 6).

**Before each dev install (character files)**: clip lengths + root samples‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ listed; every TAE entry's imported clip exists;
graph states / leaves for every id the TAE, Lua and EMEVD use; FLVER node-order / flag / dummy checks (placement dummies on the fixed
SFX node); hkx PTCH audit; judge chain verifier (TAE -> BehaviorParam -> Atk / Bullet -> children, FX ids in a loaded binder, sound ids
in a loaded bank); status scrub; footprint audit; FXR bytes differ only in value slots; bank child order; Lua precompiled +
`.luagnl` regenerated; only changed files in the overlay; anibnd + chrbnd + regulation installed together when dummies changed; debug
package rebuilt and still last if the fight script or AI binder changed.

**After each install, tell the tester**: profile + active packages, what changed per move (catalogue / panel id, second, body
part), a 2-minute "where to look" list with the panel recipe, proven vs unproven, rollback.

**A move is done when**: source chain complete (no cut by an early AI window), heading as the source (turns only where it
turns; aimed shots re-aimed), hit timing = visual timing, hit size <= what is shown, short characters hit, roll-dodgeable unless it is
an intended area attack, its effect (readable, inside the GPU budget) and sound present, the AI picks it at the source's frequency,
and the tester said so.

## Symptom -> first check

| symptom | first check |
|---|---|
| crash at load / when the player walks near | Windows Application event 1001 offset: 0x1A11B59 / 0x182AC83 = hkx PTCH / TYPE; 0x6F3EEA8 / 0x6F3EED7 = FLVER node order / second skeleton table |
| body invisible / one part missing | `modelDispMaskNN` for every `#NN#` group; unique material names; TPF format bytes; `_l` twins; mesh box form |
| textures look like camouflage (Blender source) | UV V not flipped (`original_model.md` 8) |
| giant spikes, flicker, white areas | mixed vertex buffers or GXIndex -1; zero-weight vertices; weights on odd node slots |
| hard or impossible to hit | hurt capsules inside the movement cylinder; hover height; empty BaseSkeleton / node flags 0; no capsule on wings |
| "the head breaks too slowly" | coverage check first; then trainer / damage multiplier on?; stacked knobs; party / depth rule (`params_balance.md` 8-9) |
| bullets / helpers spawn in "staircases" metres up | dummies with parent -1 bound to the hip: re-parent to the fixed SFX node |
| forced animation does nothing | no bound `W_Event<id>` state (a name alone is not enough); damage states 8060 / 8700 cannot be forced |
| colour / power / distance variant never plays | missing `aNNN_` leaf in that selector; selector SpEffect set < 3 frames before the request |
| actor turns by itself inside a long clip | clip length / root samples (rule 6); then the clip's own root yaw as the game reads it |
| "it slides" / tracks where the source does not | engine turn windows (224 > 0) outside source turn intervals; AttackTunableSpin spin; missing JT7; turn rate x mouth distance |
| "it does not turn, only the shots home" | aimed multi-shot move without re-aim windows |
| only half of a move plays | AI window before the release point; goal life shorter than the clip |
| random skipped shots / mine lines | one-frame release events on a speed-multiplied clip |
| "hit without being reached" / hit before the flame | capsule between helper bones full size from frame 0; radius > effect; persistent window after the visual |
| stream misses in front / sprays forward | aimed from the head, not the source's breath joint; damage outliving the source shell |
| mines on walls / rows always at one spot | "drop to first collision"; a helper that never moved (warp with dummy -1) |
| fan dies on small bumps / no shadow / short character untouched | +0x8C = -1, ray radius too big, origin at mouth height |
| scripted knock-down: falls, snaps up, falls again with a glow; AI frozen after | no SpEffect 45; fixed AI-off wait; stance-break critical rows without ThrowParam |
| frame drop during one move | large melee capsules over display-derived collision; big spheres with mapHitType 0; emission rate of owner bullets |
| game freezes at the first spawn of one effect | FXR structure edit (counts / offsets / links) |
| effect "too bright" after colour edits, or the boss hidden | HDR multipliers, not colour; the covering emitter (billow vs smoke) |
| move fires backwards | wrong member of a directional family (root starts at 180); rebase on frame 0 |
| all sounds of the boss gone | bank child order; reference to an object outside the bank; total custom media budget |
| effect missing | binder layout / id >= 99999; binder name follows SfxResBankId (me3 log); short TAE 96 record; writer round-trip of a vanilla FXR; donor child id dangling |
| blood sparks on an armoured boss, silent hits | donor `materialSfx*`; hit sounds need wrapper FXRs (`fx_sound.md` 7) |
| boss idles and never attacks | AI binder failed to load (precompile, one battle goal per binder); unbound move keys; set-piece SpEffect left on; AI requests for appended attack slots |
| crash in Lua `sweeplist` after an arena load, or everyone crashes at the settlement | AI heap fragmented inside one expedition (corrected: the heap is rebuilt per world, not worn out by a "long modded run"): source-text Lua, mod characters in an always-loaded block; gauge the largest free block (`ai_port.md` 6) |
| boss tilts / jitters on bumpy ground; floats above ground | `isUnduration`; inherited `hitYOffset` |
| death freezes in a pose, no dissolve | A10000 / A10001 import a clip you replaced; effects on 1101x / 1106x (throw clips) instead of 10000 |
| helpers keep standing after the boss dies | disable / collision off / backread off after the death clip |
| summons frozen / never animate on clients | `isHostSyncChr 1` or AI ON only on the host; navmesh not where the content sits |
| bar name vanilla or blank | name patched in 90075901; NpcName missing in that language |
| blink attacks feel unfair | reappear -> first hit < 1.0 s (vanilla minimum); hits closer than the roll recovery |
| clients see teleports / different heading | per-machine EMEVD boss commands or AI switched off on clients (`nightreign-nightlord-replace` references/coop.md 4) |
| one player's game freezes then crashes | collect logs; display-driver reset + GPU watchdog dump = GPU timeout: dense blended particles, DRED (`diagnostics.md` 4) |

## Unverified (do not build on these without a test)

The full, labelled list is `boss_pipeline.md` 8; each reference ends with its own list. Most load-bearing open items: whether the
Seamless Co-op party factor enters NPC part max; whether 7767 rates apply to EMEVD-fired bullets; which change made an impact circle
hit; why some cross-binder FX copies never render; summons on a baked navmesh; the in-game load of each new precompiled build; whether
the clip limit is ~30 s or ~1,024 reference samples; > 256 weighted bones; route-B frontal stance, twist flag and baked cloth.
