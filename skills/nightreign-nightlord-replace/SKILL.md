---
name: nightreign-nightlord-replace
description: "MUST verify the source game is publicly released before porting (web search; refuse unreleased, leaked or unconfirmed sources; own assets OK). 移植前必须先联网核实源游戏已正式发售，否则拒绝。把其他游戏的 BOSS（怪物猎人世界、碧蓝幻想 Relink、黑暗之魂……）做成《艾尔登法环：黑夜君临》新夜王或替换夜王（离线 me3 MOD）的通用流程与铁律：角色移植、行为树转预编译 Lua AI 与 AI 堆、夜王战事件脚本（开战、血条、多语言名字、BGM 槽位、按血量比例分阶段、部位破坏、胜负、击杀记给原夜王、关键道具）、捏碎道具切换本局夜王战（最后捏碎的为准）、平衡（原版夜王平均血量的倍数、无缝联机血量公式、4~6 人、深夜缩放、部位耐久、读条破招）、联机同步（房主导演/客机跟随、召唤物 isHostSyncChr=0、按槽位数人头）、测试（先开发版后打包、分层开发入口、调试面板、显卡 TDR）、发布（从开发栈钉文件、正则差量转移、增量安装器、升级补丁、隐私扫描）。触发词：替换夜王、新夜王、自制夜王、移植BOSS、捏碎道具、夜王战、夜王联机、无缝联机、召唤物不动、血量平衡、部位破坏、AI堆、显卡崩溃、升级补丁。English: Nightlord replacement / new Nightlord from a ported boss, fight EMEVD, switch item, last crush wins, kill credit, Lua heap, part break HP, key item 2003[108], HP vs the Nightlord mean, Seamless Co-op HP formula, 4-6 players, Deep Night scaling, host director / client follower, isHostSyncChr, DRED GPU hang, debug panel, me3 dev overlay, delta regulation, additive installer, upgrade patch, boss pipeline S8-S12."
---

# Nightreign: a ported boss as a (new or replacing) Nightlord

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

Example: a request to port the Lantern Abbot of Greyfen as a new Nightlord from a game that has only been announced is refused until the game is on sale, however complete the leaked files look.

## Responsible use

- Free, non-commercial mods only. Never sell, paywall or bundle for sale anything that contains another game's assets (models,
  textures, animations, effects, sounds, music, text), and do not help anyone do so.
- Respect the EULAs and terms of service of the source games and of Nightreign; extract only from copies the user owns; credit
  the source game and its rights holder when a port is shared.
- Offline only. Modded Nightreign runs through me3 with Easy Anti-Cheat off and its own save file; never take modified files
  onto the official online service or matchmaking (EAC; bans are possible). Co-op in this skill set means the Seamless Co-op
  mod, which plays outside official matchmaking.

## About this skill

Scope: an offline me3 mod that puts a boss from another game into the Nightlord fight of a Nightreign expedition, switched on
by an item crushed in the Spirit Tree hub, with kill credit to the expedition's original Nightlord, working solo and in co-op
(Seamless Co-op up to 6 players), balanced against the vanilla Nightlords and shipped as an installer (standalone or inside a mod
pack profile). Everything here worked in game unless tagged otherwise. Not repeated here:
- `nightreign-modding` - me3 basics, Smithbox, WitchyBND, FLVER / TPF, param editing, GUI automation.
- `nightreign-map-port` (companion skill, not included in this repository) - building / porting the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ arena itself (map block, MSB, collision, navmesh, gparam, world load list).
- `ds3-nightreign-port` (companion skill, not included in this repository) - if the boss comes from Dark Souls III (same engine family: direct clip / TAE / FXR / FSB conversion).
- `nightreign-boss-port` - the deep character-side version (survey, extraction, donor graph, model, physics, clips, TAE, hits,
  FX / sound, AI, rows, reactions, QA), the standard pipeline `references/boss_pipeline.md` and the dev-only debug panel
  `references/debug_panel.md`; `references/character_port.md` and `ai_lua.md` here are its short form.

**Evidence tags**: [code] static RE of `nightreign.exe`, [data] read from files, [game] confirmed in game by the tester,
[game-MP] confirmed in a real multi-machine session, [sim] offline simulator only, [model] offline geometric / damage model,
[inferred]. **CORRECTS** / **REFINES** mark statements that replace or extend older text of this skill. Exe offsets and vanilla
ids were found on NR 1.3.3.0 (PE TimeDateStamp 0x69e0dc2a, SizeOfImage 0x7c5d600), regulation 10350000: re-verify after any game
patch. Only [game] is proof; offline PASS results were wrong in game more than once.

## When to read what

| task | reference |
|---|---|
| decisions (incl. diagnostics plan, shipping configuration), id bands, id-claim hygiene, flag storage, entity id digits, coordination file, agents | `references/ids_and_planning.md` |
| model, skeleton, physics / hurtboxes, behaviour graph slots and variants, clips, root motion, TAE, turning, hits, FX, sound, sparks, death | `references/character_port.md` |
| behaviour tree -> Lua, fidelity harness, precompiled bytecode, AI heap per world, fragmentation, hoisting big functions, AI vs EMEVD | `references/ai_lua.md` |
| vanilla day-3 flow, constructor events, in-arena vs own block, script skeleton, bar, names in every language, BGM, HP-ratio phases, set pieces + collision ids, part HP engine, victory / defeat, credit, HUD, key items | `references/fight_script.md` |
| switch item data, latch vs "last crush wins", gate routing, joint hub with another mod boss | `references/item_switch.md` |
| HP vs the vanilla means, Seamless Co-op HP formula, Deep Night, absolute-HP audit, part durability scaling, cast bars, damage, certain-kill hits, status, dodge, DPS, helper NPCs | `references/balance.md` |
| what replicates, host director / client follower, summons, one judge, end-condition hardening, per-machine vs host-only, target slots, player count, 4-6 players, late join, simulator limits, logs | `references/coop.md` |
| dev entry layering, dev first, install guards, debug panel package, DEBUG vs REAL, quick-test kit, offline proof, tester loop, trainers, probes, GPU hangs, checklists | `references/testing.md` |
| installer, fingerprint, previous-release-only patch, rehearsals, three-way merge, privacy scan, pins, delta regulation, cells-mode replay, versions, readme | `references/release_packaging.md` |
| damage numbers, custom ride routes, sync log fields, AI-heap gauge, DRED, debug-panel bridge, crash collector (native DLLs) | `references/native_dlls.md` |
| helper scripts (`publish_overlay.py`, `dll_strings.py`) | `scripts/README.md` |

## Pipeline (stage ids of `nightreign-boss-port/references/boss_pipeline.md`)

The boss-port pipeline defines 13 stages S0-S12, each ending in a gate; "[game]" in a gate means the tester saw it in the dev
entry. S1-S7 (extract, show build, debug harness, motion + TAE, attacks, FX + readability, AI) are the character work of
`nightreign-boss-port` (short form here: `character_port.md`, `ai_lua.md`). This skill owns the Nightlord-specific additions to
S0 and the stages S8-S12:

| stage | Nightlord-specific work here | exit gate | references |
|---|---|---|---|
| S0 Plan | **Step 0 released-source web check first (refuse if unreleased / unconfirmed)**; the five decisions + diagnostics plan + shipping configuration + fidelity rules; id bands claimed in one registry | release evidence written (or own assets); written decisions; tester agreed on "done" | `ids_and_planning.md` 1-5 |
| S8 Fight script + arena | in-arena vs own block, constructor copies, bar / names / BGM, HP-ratio gates, set pieces with every collision piece id'd, part records, victory / credit, switch item and gate routing, key items, arena checks | [game] arrival -> victory in the dev entry; collision audit 0 orphans; language matrix complete; REAL-path audit clean | `fight_script.md`, `item_switch.md` |
| S9 Balance | HP as a multiple of a vanilla mean + absolute-HP audit, Seamless formula, depth / party tables, part durability scaling, cast-bar windows, damage | tester decision recorded with numbers per depth / party; logged max HP = published table [game] | `balance.md` |
| S10 Co-op | host director / client follower, summons `isHostSyncChr 0`, one judge, target-slot publishing, end-condition hardening, per-slot presence, 4-6 slot audit, logs from every machine | [game-MP] numbered checklist, every machine's log collected | `coop.md`, `native_dlls.md` |
| S11 Release | pins from the dev stack minus probes / debug, regulation by delta transfer, cells-mode replay, previous-release-only patch, rehearsals, privacy scan, honest readme | release vs dev compare differs only by named dev-only rows | `release_packaging.md` |
| S12 Live feedback loop | every report -> one dev overlay -> tester -> only then the next pack; what to ask; trainers; GPU-hang collection | dev confirmation before any pack | `testing.md` |

Rules of the loop: one change per dev package in a NEW folder; one builder per change that asserts its own base and can replay
on release inputs; the tester confirms in the dev entry before anything is packed; probes and the debug package never reach a
release. The phases below are the same work in build order; their stage ids are in brackets.

## Workflow

Work in rounds: build offline -> self-check -> install ONE overlay into the dev entry -> the tester plays -> their words become the
next round. Keep a coordination file and a STATE.md from day one (`ids_and_planning.md` 6).

### Phase 0 - Plan, no files yet [S0, S1]
0. Step 0 (top of this file): web-verify that the source game / DLC is released and on sale; refuse unreleased, leaked or
   unconfirmable sources before anything else.
1. Take the five decisions (details `ids_and_planning.md` 1) and ask the tester what "done" means (fidelity to the source,
   arrival / aggro rules, what may be simplified). Write them into the coordination file:

| decision | choose A when | choose B when |
|---|---|---|
| A in-arena (inside the target's vanilla block) / B own block | the boss fits a vanilla arena; only one mod boss lives there; you accept its AI / characters loading in every expedition to that block | own arena geometry, another mod already owns the vanilla arena script, or the shared block's AI heap is tight |
| donor graph c2130 (humanoid) / c4510 (quadruped, winged) | biped / humanoid source | quadruped, dragon, flyer |
| one-way latch / last crush wins | exactly one mod item in the profile | several mod bosses share the hub |
| Deep Night scaling on (7767) / off (0) | the fight should feel like a Nightlord at every depth | fixed difficulty wanted |
| standalone / pack layer | own profile on the vanilla base | players use a pack profile: three-way merge on the pack's files |

2. Also write down the diagnostics plan (sync-log fields incl. player HP / damage taken, flag lists, AI-heap gauge, debug panel)
   and the shipping configuration (co-op DLL, forced Deep Night depth, co-loaded mods).
3. Pick the character id and derive every id band from it; claim each band in ONE registry per kind; scan every layer that may be
   co-loaded (vanilla, pack packages, other mods' releases AND dev stages).
4. Flags: only in a block listed in the event-flag alloc list, never fourth digit 6; keep the class you need (world / temporary /
   local). Entities: never thousands digit 5 / 6 / 7. Event ids are flags: keep them disjoint.
5. Extract the source game completely and keep it read-only (it may be uninstalled later); record each attack's spawn joint,
   shell life, radius, re-hit interval and anchoring.

### Phase 1 - Show build (prove the character loads before any move) [S2, S3]
1. Skeleton (Master + Root, -Z facing, depth-first), FLVER (node order rule, unique material names, display masks, placement
   dummies on the fixed SFX node), physics hurtboxes (PTCH / THSH repairs), behbnd copied from the donor, minimal anibnd (idle,
   walk, turns, death), NpcParam cloned from the replaced Nightlord, battle goal 11000 (do nothing). It may sit in a vanilla arena
   slot first (`fight_script.md` 3).
2. Gate: in game the boss is visible, lockable, hittable, dies normally, no crash when walking near. Crash -> event 1001 offset
   -> known table in `character_port.md` 13.
3. Before the first attack: the dev-only debug panel (`nightreign-boss-port/references/debug_panel.md`) and the sync log / heap
   gauge (`native_dlls.md`).

### Phase 2 - Moves [S4-S6]
1. Map every source move to a donor slot (or a variant / appended `W_Event` state); one clip stored once and imported by TAE.
2. Resample 60 -> 30 fps, root motion in the reference frame, every root-motion clip <= 29.7 s / 892 reference samples
   (split longer chains).
3. TAE: start from the donor's TAE, control events only; heading hold (224 = 0 + JT7) with turn windows only where the source
   turns, plus re-aim windows between shots of aimed multi-shot moves; release events >= 0.1 s; SpEffect 45 over every forced
   clip; AI windows after the full move; attack / bullet chains verified end to end; hit sizes from the source volumes.
4. Effects (binder layout rule, value-slot edits only), sounds (children-first bank), hit sparks / hit sounds via private rows.
5. Gate: every move plays complete in the dev entry (via the debug panel); the tester confirms looks against the source (send
   preview renders first).

### Phase 3 - AI [S7]
1. Decode the source behaviour tree into data; write one Lua function per source node; unknown code-computed predicates become
   named switches (default off) and questions.
2. Prove fidelity offline (real Lua under Lua 5.0.2 with mocks, cell distributions + dynamic runs).
3. Ship stripped precompiled bytecode with small prototypes (one fixed 20 MiB AI arena shared by 4 states, rebuilt per world;
   source text fragments it). Keep a restructured-source fallback. Gauge the heap in a real expedition with the co-loaded mods.
4. Big specials: prefer AI-started acts with TAE payload (vanilla way, replicates in co-op) over event-driven set pieces.

### Phase 4 - Fight script [S8]
1. Choose the skeleton of `fight_script.md` 4: DEBUG / REAL head, decider / constructor, aggro gate, start (local copy of
   90075101), 90075902 + 90015012 + 90015020 + 90015008 per boss entity, phase controllers with rebuild heads, victory via
   90075901, vanilla defeat flows, DEBUG-only events, Roundtable clean-up.
2. Music: a `_CL_ReservedNN` slot nobody else uses + an added path in the top music switch of BOTH cs_main.bnk and cs_smain.bnk.
   Names: every NpcName in every shipped language, official source names.
3. Phases and specials gated on HP ratios; set pieces switch every collision piece by entity id (`2011[1]`) with the visuals.
4. Part breaks: records start right after Create (a missing record reads "broken"); host-only break decision; re-arm with
   `(v, 1)` + `(9999999, 0)` in the frame of the break test; party scaling under Seamless Co-op by an engine-tested re-base.
5. Own block: never raise 7511; 7513 -> 7512 at the kill; the target arena's own end chain credits the original Nightlord; hub
   MapConnection anchor; in-world entry only.
6. Gate: dev entry fight from arrival to victory text + music; REAL-path audit (nothing touches player state that a vanilla
   arena does not touch); collision ownership audit.

### Phase 5 - Switch item, routing, credit, key items [S8]
1. Goods cloned from 1290, marker SpEffect, crush FX, icon, 4-language texts, sold by the hub merchant (ShopLineupParam
   2000-2999), never a ground pickup.
2. Protocol: one-way latch if only one mod item exists, else "last crush wins" (host arbiter, decision at gate commit, gate waits
   <= 1.5 s). Decide at the gate, never at arena load (the arena loads with the hub).
3. Kill credit: in-arena = vanilla end chain + credit lines keyed on the variation; own block = target arena's own‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ chain; joint
   hub with another mod boss = hash-anchored patch of a COPY of its decider.
4. Key items: `2003[108]` with ids in the vanilla key-item band, granted once behind a flag, with a dev route first.
5. Gate: quick-test kit (pack route) then one real solo expedition: with item -> mod fight, without -> vanilla fight, kill ->
   normal settlement, hub buffs survive, Roundtable clean.

### Phase 6 - Balance [S9]
Benchmark against the vanilla rows (`balance.md` 1-3), present options with numbers (HP multiple of a named mean, Deep Night on
/ off, damage transfer, status thresholds, break rule (a) / (b), cast-bar counts), let the tester decide, record it. State numbers
at depth 0 and at the depth players really use, with the Seamless party formula; publish the expected max-HP table.

### Phase 7 - Co-op hardening [S10]
1. Audit every event: who runs it, sync state, who holds which copy, who sets / clears each flag and SpEffect; slots 4-6 in every
   per-player block.
2. No per-machine boss commands: big moves from the host AI, or host-driven set pieces (host director, clients keep AI on, never
   command the boss, follow published one-hot decisions). Summons `isHostSyncChr 0` + AI on everywhere. Own-player effects
   owner-applied, self-expiring. One judge for breaks and counts; no slot -> no shot; hardened end conditions.
3. Offline host / client simulator with a negative control (regression / identity only); one adversarial review by an agent that
   did not write the code.
4. Gate: a real session with a numbered per-mechanic checklist; every player reports their own screen; every machine's log
   collected; label fixes "offline only" until then.

### Phase 8 - Release [S11] and the live loop [S12]
Pins from a copy of the dev stack without probe / debug blocks -> regulation by delta transfer -> one-command resumable chain ->
additive self-contained installer + receipt + fingerprint -> rehearsals on a scratch me3 (every audience) -> privacy scan +
quick-test guard -> readme by audience with honest test status -> later releases also as an in-place upgrade patch that accepts
only the previous release. The tester and players run installers themselves. Every report after a release goes back through a dev
overlay first.

## Hard rules (each one cost a failed round)

Data and engine
1. Flags: storage only in alloc-listed blocks and fourth digit != 6 (silent: reads OFF, writes dropped); keep the class when
   renumbering; test a renumbered script in the dev entry before building on it. [code, game]
2. Entity ids with thousands digit 5 / 6 / 7 are group ids: commands on them do nothing. [game]
3. Event id > 299 sets flag (id + slot) when it ends / restarts: never share numbers with plain flags. [code, game]
4. The behaviour graph plays only its own states; `Force Animation` needs a `W_Event<id>` transition; animIdOffset variants need
   a clip leaf `aNNN_` in the selector node, or the base plays silently. [game]
5. Root-motion clips <= 29.7 s / 892 reference samples (frame count alone is not the limit); a 45 s / 1,359-sample clip
   turned the actor by itself. [game]
6. Hold heading with 224 = 0 + JT7; open turn windows only where the source rotates (and between shots of aimed multi-shot
   moves). No 224 row = NpcParam default rate; a Rotate rate <= 0 = 90 deg/s, so Rotate-driven clips freeze with a small
   positive rate (0.01). [code, game]
7. FLVER node order [weighted bones][meshes][dummy owners][other bones]; dummy ids < 1000 (`id % 1000`); dummies with parent -1
   follow node 0 (the hip): parent placement dummies to the fixed SFX node; new hkx need the PTCH / THSH repairs. [code, game]
8. FXR binder members 0..n-1 (+ reslists at 400000 + i); enumeration stops at the first member >= 99999; edit FXRs only in
   value slots of byte copies (a 2-byte structure edit froze the game). [code, game]
9. Wwise: children before parents, no clones referencing other banks' objects: one bad object silences the whole bank;
   budget the total resident custom media (a 108 MB bank stayed silent). [game]
10. `Set Boss BGM` only accepts the 114 cached BgmEnemyType names; anything else is dropped silently. [code, game]
11. Ship AI as stripped precompiled Lua 5.0 bytecode with small prototypes; the AI heap is one fixed 20 MiB arena per world for
    every AI loaded there (all bosses of an always-loaded block, every co-loaded mod); gauge its largest free block. [code, game]
12. Never keep large melee capsule sets active over dense map collision; attack rows >= 30 m use `mapHitType 2`. [game, data]
13. Part HP from `Create NPC Part` is scaled by stage / depth (maxHpRate product); party scaling under Seamless Co-op is unproven
    (**CORRECTS** "already scaled by party"); `Set NPC Part HP(.., v, 0)` is not scaled; `IF NPC Part HP` is TRUE for a missing
    record. [code]
14. SpEffect 45 over every forced / scripted clip (JT24 does not stop stance damage). [game-MP symptoms, code]

EMEVD and flow
15. Forward GOTOs only; loop with END / RESTART; bound every wait; every wait while the boss AI is off has an elapsed-time
    escape. [game]
16. Decide item-dependent things at the gate: the arena block loads together with the hub. [game]
17. Never FadeToBlack / Freeze in the hub around the gate (permanent black); every screen guard has a hard time-out. [game]
18. Own block: never raise 7511 (the still-loaded vanilla arena starts its own Nightlord); a loading-screen warp is not
    acceptable (wipes ultimate charge and buffs). [game]
19. REAL path: your scripts never clear 7500-7599, never call `Bonfire-like Recovery` (hub arrival already does; a second one
    at block load erased consumable buffs), never touch the revival token 6999500 / 6999501. [game]
20. Leave down / revive / wipe to vanilla commons 1180 / 1181 / 1182-1184. [game]
21. The HUD file `menu/01_000_fe.gfx` is global: never restyle vanilla bar placements. [game]
22. Ground pickups with a full item bar lose the item: sell the switch item at the hub merchant. Detect use by its marker
    SpEffect only. [game]
23. Every collision piece a set piece switches (assets, bodies, invisible player walls) has an entity id and is switched with
    `2011[1]` in the same block as the visuals on every path; id 0 parts can never be switched. [game report, data]
24. Gates as HP ratios; absolute HP compares only at the floor (<= 1), so NpcParam.hp stays the single HP knob. [code]
25. Key items: `2003[108]`, ids in the vanilla key-item band, granted once behind a flag (`2003[124]` and large ids failed). [game]

Co-op
26. Force Animation / Rotate / Short Warp act on the local copy only: never drive or warp the boss from every machine; never
    switch the boss AI off on clients; every boss command of a set piece behind `SKIP IF client`. [code, game-MP]
27. Anything a machine must produce for its own player (event bullets, hit volumes, effects) never sits behind a host gate. [game-MP]
28. Never `Set Character Invincibility` on players; use owner-applied self-expiring SpEffects on 20000 in sync-off events. [game-MP]
29. Solo = `Multiplayer State == 4`; count players from per-slot presence, never `Is Player Count` (it read 2 in a 3-player
    Seamless party). Persistent boss state in self-expiring SpEffects (a host's Clear SpEffect did not reach the client copies;
    mechanism likely). [game, game-MP]
30. Summons / helpers: `isHostSyncChr 0` and AI ON on every machine (with 1 they never animated on clients). [game-MP]
31. One judge: the host decides breaks, counts and branches and publishes network flags; in co-op no target slot -> no shot;
    one-hot publishers clear first and set one frame later. [code, sim, game-MP]
32. Long set pieces: host ignores client end signals, stale flags cleared at start, end terms debounced over >= 2 frames,
    breadcrumb flags per end term. [game-MP]

Process
33. Audit the INSTALLED files (dump everything) when the tester says nothing changed; make a broken twin byte-identical to the
    working one before theorising; measure plain sizes / counts first. [game]
34. After two or three failed paper explanations, ask for a recording; ask what they see before guessing a mechanism; ask about
    trainers / multipliers before using any log for calibration. [game]
35. Never assert a vanilla mechanic from params / menu text; never assign a source motion to a role by its‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ name - ask.
36. One overlay per round in a NEW folder; never overwrite installed or frozen-stage files; delete your own superseded entries.
    Dev first, then pack: every feature (hub-layer ones included) is confirmed in the dev entry before it is packaged. [game]
37. A quick-test entrance is its own .me3 and never part of a release (guard script on folder + zip); probe and debug-panel
    packages (and their DLL) never ship and the pinning tool refuses them. [game, data]
38. Agents never launch the game, never run anything on the live me3 folder, never read / write saves; installers are run by
    the tester. Reports to the tester say what is proven vs unproven, where to look, how to roll back.
39. Before shipping: privacy scan of every file incl. DLLs and Lua; rehearse every audience on a scratch me3; one audit + one
    re-check for what goes to other people (none for dev patches); the patch accepts only the previous release; no version
    string that contains an earlier one (1.8.1 vs 1.8.10). [data]
40. An offline simulator never clears a co-op bug; logs from every machine do. [sim vs game-MP]

## Checklists

**Before each dev install**: builder PASS + independent read-back (only the named lines / cells changed); clip lengths listed;
FXR binder layout; bank child order; flag / entity id guard; Lua binder precompiled + .luagnl regenerated; overlay contains only
changed files; entry publisher asserts the last package; debug package still last (rebuilt if fight script / AI binder changed);
game process checked (0-thread zombies ignored).

**After each dev install, tell the tester**: entry + package list, what changed, a 2-minute "where to look" list, proven vs
unproven, rollback.

**Before asking for a real expedition**: renumbered / merged scripts already played in the dev entry; REAL-path audit clean;
scenario simulator win / lose per target arena type; quick-test kit run; list "first in-game run of these files".

**Before a co-op session**: same fingerprint on every machine; every native on every machine; logging ini lists the new flags;
nobody used debug entrances or the debug-panel profile that day; numbered per-mechanic checklist; host and ping noted;
recording requested; every machine sends its log right after.

**Before shipping**: pins from a copy of the dev profile without probe / debug blocks; base-chain proof; regulation delta
transfer + release vs dev compare; one-command chain from the dev stack (stack compare equal); merge read-backs + allow-lists;
regulation budget and version; language audit; scan 0 hits + positive control; quick-test guard clean; rehearsals for each
audience; readme audiences + honest test status; zip + `.sha256` only.

## Most load-bearing engine facts (details in the references)

| fact | tag |
|---|---|
| NR chars face -Z; NR clips 30 fps; MHW LMT 60 fps; Relink attack boxes are half extents | data, game |
| Hurtboxes = physics hkx ragdoll capsules; part groups in hkxpwv -> partsDamageRate | data, game |
| Donor slots: c4510 events 20000/1/2/10/19/20/25/26, loops 30000/5/10/19/25/26 (30011 was appended); c2130 41 attack slots | data, game |
| Death = 10000 -> 10001 loop; 1101x / 1106x / 1107x are throw clips | code |
| Hit sparks via materialSfx -> HitEffectSfxConcept -> HitEffectSfx, looked up in the target's sfxbnd; hit sounds not table-driven | data, game |
| Max HP = base x product of maxHpRate; Nightlord innate 7767 = x3.54 HP / x3.36 attack; vanilla party 7867 x2 / 7967 x3; Deep Night 877671..675 | code, data |
| Seamless Co-op: max HP = trunc(f32(hp x f32(3.54 x DN x (1 + 1.2 (n - 1))))), fixed at ENABLE time; 7867 / 7967 never applied; helpers unscaled | game-MP, data |
| Vanilla Nightlord base HP 3200-3712 (Heolstor 1408 + 2880); mean of 8 = 3612.75, mean of the 7 regular bodies = 3516.29 | data |
| Block position from MapConnection regions of loaded blocks, else absolute zero; hub sits ~400 m above the open field in real runs | code, data |
| 7511 start, 7513 HP 0, 7512 defeated, 7000 clear, 7001 game over, 7500 expedition active, 7510 gate passed | data |
| 2003[69] network flag write; 2003[66] local; set-piece commands local only; client AI off = frozen copy | code, game-MP |
| AI Lua heap: one fixed 20 MiB arena, 4 states, rebuilt at every map move; go / no-go = a free block >= 8 KiB; teardown OOM -> exit(1) | code, game-MP |
| Part records: 40 global slots; only the first matching record's return is HP damage; `IF NPC Part HP` TRUE when missing | code |
| `2011[1] Activate Hit` is the only collision switch in vanilla scripts; per machine | data |
| `Is Player Count` is unreliable under Seamless Co-op (read 2 in 3P); count per-slot presence | game-MP |

## Unverified (do not build on these without a test)

Kill credit for DLC / Heolstor targets redirected into m19; late joiners into a running fight; Seamless Co-op HP at 4-6 players
(formula measured at 2P / 3P); whether the co-op mod's party factor enters NPC part max; damage numbers for all enemies; engine
GoodsDialog prompt; an alloc-list line for a new map block; whether the clip limit is ~30 s or ~1,024 reference samples; whether
summons move on a baked arena navmesh; `2003[6]` as a collision switch; main-save uninstall of key items. **CORRECTS** the old
entry "host-driven set pieces confirmed only offline": host-only boss commands now ran in real sessions (copies within ~1 m /
~1 deg, host-only knock-downs seen on clients) [game-MP]. Each reference ends with its own unverified list.
