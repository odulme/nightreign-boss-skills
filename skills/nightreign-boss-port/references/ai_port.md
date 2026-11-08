# AI: source behaviour tree -> Nightreign Lua

Tags as in `SKILL.md`. Pipeline stage S7 (`boss_pipeline.md`). The short version (lookup chain, goal API, vanilla big-move
statistics, heap rule) is in `nightreign-nightlord-replace` `ai_lua.md`; DS3 binder / dead-subgoal rules in `ds3-nightreign-port`
`enemies_ai.md`.

## 1. Route by what the source gives

| source AI | route |
|---|---|
| data tree (MHW THK, Relink behaviour trees) | decode -> executable model -> one Lua function per node -> prove fidelity offline |
| code only, or the tester wants "like X but" | fork a vanilla goal of a similar boss (e.g. Morgott 213005 + after-attack 213006; 213000 is ER's id with no file in NR), own goal id, phase from your own SpEffect, disable the donor's phase ultimates and forced HP moves |
| same family (DS3 Lua) | decompile, retype, precompile; one battle goal per binder; dead subgoals routed through aiCommon hosts (`ds3-nightreign-port`) |

Check every goal id against NR's goal list (aicommon `goal_list.lua`, ~858 ids; e.g. a DS3 common goal id collided) [data].

## 2. Decoding MHW THK (worked; the pattern transfers to other tree formats) [data]

- Of 60 THK files only four carry logic: combat main (223 nodes), a global library (one node per action / action group, called
  from every context), combat enter, rage enter; the rest are stubs.
- Layout: 32-byte header ('THK\0', version, node count, hash, monster id, header size); 16-byte nodes (segment offset, count,
  id); 128-byte segments (116-byte struct + 12 padding, missing after the file's last segment) with endRandom, flowControl,
  branchingControl, functionType, two parameters, external ref (file, node ID), local ref (node INDEX), actionID + 5 unknowns.
- Control flow as a stack machine: branching 2 = if, 4 = elif / else, 8 = endif, 1 = endRandom, 0x10 = conclude; endRandom
  0x40 = random with weight = parameter1, 0x80 / 0xC0 = elseRandom; flow 4 = repeat, 8 = return, 0x80 = reset.
- References: external calls use node IDs, local calls use node INDEXES - resolve both to ids first.
- Conditions: functionType < 0 = negated; register ops (unary / binary on r0..r21); distances in cm; angles in degrees
  clockwise from the facing with wrap-around ranges ((330, 30) front); weights raw, normalise per random block. Names from the
  community decompiler's dictionary; unnamed ones stay `fn_0xNN`.
- Actions are the exe's enum; the action -> motion link is in the exe: assign motions from evidence (shell ids, collision names)
  with a confidence per action.
- Registers = the source's state machine (stance counters, ground / air decision counters with probabilistic switching, phase
  one-shots, "just switched" flags, combo counter). One decision = one pass of the main node in a fixed order.
- Pools: stance -> distance band -> phase (-> variant) -> target-angle sector -> weighted pick; pre-steps (turn, back walk)
  live inside the library nodes.
- Pipeline: decompiler -> raw json -> AST (fn / action / call / repeat / return / reset; if / random) -> two INDEPENDENT
  consumers (a pool extractor that writes Lua tables and an executable tree model) cross-checked to 0 mismatches.
- Unknown exe-side functions / tables: each is an input flag of the model (default False, every evaluation counted) and in
  the Lua either absent or a named switch marked as a guess (e.g. a wide-fire cooldown standing in for an exe timer). Put a
  number on each unknown in a model world (with one flag true the source makes 1.3-1.5 moves per decision, the Lua 1.02) and
  ask the tester; keep them as built when the tester cannot decide.

## 3. Lua structure that worked [data; behaviour accepted in game]

- `local F = {}` file-local namespace (Lua 5.0 allows at most 32 upvalues per function); globals only the goal constants and
  generated tables. `RegisterTableGoal(<goal>, ...)` + `REGISTER_GOAL_NO_SUB_GOAL(<goal>, true)`; Initialize -> InitState;
  Activate -> `Init_Pseudo_Global(ai, goal)` then `F.Think`; Update -> `Update_Default_NoSubGoal`; Interrupt -> `F.Interrupt`.
  After-attack goal `<goal>+1` with the same shape.
- **Per-boss state only in `ai:SetStringIndexedNumber("<prefix>_" .. key)`** (stance, flying, source registers, last moves,
  pending thresholds, rage, decision count) + ai timers; never Lua globals / upvalues (one chunk serves every instance).
- Decision‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ order: set-piece SpEffect on -> `Wait 0.5` and stop; just after a set piece -> reset air / stance state (keep the
  source's long counters); pick target, build context (phase from SpEffects, breaks, rage, stance, distance, angle); air
  failsafe (flying older than ~45 s = grounded); rage roar; phase entry; HP-threshold pending; enter node once; flight timer;
  air or ground pools; queue the after-attack goal.
- One function per source node `F.N[id](ai, goal, c)`; move table `F.MOVE[key]` = {stance needed, stance after, pre-turn,
  back-walk distance, far threshold, fallback key, aim flag}.
- Binding generator rewrites GENERATED blocks only: key -> slot chain (phase overrides as `key` + phase suffix 2), left / right variants,
  end-stance overrides, flight mode, pools as rows {kind, a, b, {entry, weight, ...}}; match order key -> source action name
  -> source motion id; REFUSES EMEVD set-piece slots and ids the graph cannot play.
- Pool pick: one `GetRandam_Int(1, total)`; an entry without a slot is dropped and the rest re-rolled (up to ~12 tries) so
  missing clips renormalise; fallback chain up to ~6 deep; nothing bound -> idle logic (turn / approach / wait).
- Distance = `GetDist + GetMapHitRadius(TARGET_SELF)` to recreate the source's centre distance [inferred]; angle bins with
  `IsInsideTarget(t, dir, 2e)` over the bin edges.
- HP thresholds: land first if airborne, then `Wait 0.5` loops up to ~8 s so EMEVD finds an idle heartbeat; each threshold
  yields once.
- Pre-steps: back walk = bound clip or `GOAL_COMMON_LeaveTarget(life, far, tgt, GetDist + source travel, TARGET_SELF, true, -1)`;
  turn = `GOAL_COMMON_Turn(3, tgt, 45)` where turn clips exist. Test the source condition AFTER its pre-step (distance after
  the back walk, front / back after the turn) - getting the order wrong cost fidelity.
- Attack calls: first clip `GOAL_COMMON_AttackTunableSpin(life, anim, tgt, 999, spin, front, 0, 0)`; later clips of a chain
  `GOAL_COMMON_ComboRepeat(life, anim, tgt, 999, 0, 0, 0, 0)`; life >= longest clip + margin.
- After-attack goal: set piece -> Wait 0.3; pending follow-up (e.g. 35 %, target in front and > 8 m) -> queue it; else short
  idle / Wait 0.3-0.9 s. A strafe after unchained attacks (`GOAL_COMMON_SidewayMove`) gives safe windows.
- Interrupt: count hits for source rage rules; counter-on-hit only if the source really does it (MHW reacts on clinging, not on
  hits; the tester removed the counter).
- Flight without a flight state ("sortie" mode): each flight move is one self-contained slot (take-off + air attack + landing);
  cadence from the source but halved per air time; the tester rejected the source's exact flight frequency (few anti-air options
  in NR). Single-stance donor: source stances become a logical variable that only selects pools; stance switches are clips.
- Target: keep the engine target (highest aggro); a random pick exists but stays off.
- Debug hook: `if <Boss>_Debug ~= nil then <Boss>_Debug(event, ...) end` (nil in game, defined by the harness).
- Lua 5.0 dialect: ASCII only; no `#`, `%`, `goto`, `//`, `select('#')`, string methods on literals; use `table.getn`,
  `math.mod`, `arg` (`scripts/lua50_lint.py`, then `luac50 -p`).

## 4. AI <-> EMEVD contract [game]

- Set-piece SpEffect on the boss -> the AI only waits; heartbeat / busy markers from the TAE tell EMEVD when the boss is idle
  (fallback time-out ~4-6 s); EMEVD requests a move by a REQUEST SpEffect the Lua reads, waits for the TAE "done" marker,
  re-issues after a time-out.
- Phase / break markers as SpEffects set by EMEVD (phase 2, final form, head broken 1 / 2); the AI reads flags by NUMBER, so
  move Lua flag constants together with any id renumbering.
- Audit AI-read flags: one "warp to centre" flag was read by the Lua and set by nothing.
- Fixed follow-ups at a TAE window (e.g. burst -> triple slash if <= 6 m in front, else teleport then slash), with cooldown refunds
  when the hop lands far away [game].
- Pursuit / blinks: >= 1.0 s from reappear to the first hit, a strafe after stand-alone blinks, move-cancel window after a blink
  at ~0.8 s (Heolstor's value); cap hops per chase [game].
- A cooldown keyed on a TAE window that fires repeatedly needs a grace period (one window fired 15 times) [game].
- **HP gates as ratios only**: boss gates as `IF Character HP Ratio` in EMEVD and `GetHpRate` in the Lua, so base-HP changes need no
  edits; audit for absolute HP tests before changing HP (`params_balance.md` 5) [code]. HP-threshold set pieces are not reachable from a
  debug move list: use "AI off + damage" (an HP lock does not block the threshold) [game].
- Vanilla design numbers for specials: forced weights 999 / 9999 / 10000000; lock SpEffects 50-90 s; cooldowns 90-120 s;
  replace chains 40-90 s; sub-poise break gauges (stateInfo 610, subSa 30-70, mostly with multiplayer correction); EMEVD
  requests re-issued after 10 s, watchdog 15 s [data].

## 5. Fidelity harness (offline; trusted for cause-finding, not proof) [sim]

- Run the REAL Lua under Lua 5.0 (x64 5.0.2 for precompile proofs) with mocked `ai` / `goal`: direction ids, goal ids (Wait,
  Turn, ApproachTarget, LeaveTarget, ComboRepeat, AttackTunableSpin), `GetMapHitRadius`, `GetDist`, `IsInsideTarget`, string
  numbers, timers, flags and SpEffects as tables; log every decision and every requested key ("requested > bound").
- Pool test: ~4,000 decisions per pool row with every key bound to dummy slots vs the source weights (tolerance 4.5 sigma +
  0.4 pp); flow tests (set piece -> only waits, thresholds idle, airborne lands first, phase rules, stance cadence, reserved
  slots never requested).
- Static cells: phase x stance x distance band x angle bin x variant (~2,400 cells); source side exact (enumerate every
  random branch), Lua side ~6,000 draws; total-variation distance on move sequences (pre-steps stripped / kept / first move);
  noise floor from samples of the exact distribution; "off" when TV > 0.03 + 2 x noise. Two modes: logic only (all keys bound)
  and AS INSTALLED (current binding). Dynamic runs ~200k decisions per phase: move frequencies, bigrams, counts per 100.
- Numbers reached: logic-only 98.2 -> 99.8 % after 13 source-backed corrections; as installed ~94-95 %; report clip coverage
  weighted by source move frequency (own clip / borrowed / none per phase).
- Refactor proof: same seed -> byte-identical decision logs for original, restructured and precompiled builds. Behaviour
  change proof: the diff of two logs contains only the intended insertions.

## 6. Shipping: precompiled bytecode and the AI heap [code, game]

**The heap is a budget per world, not per play session** (corrected: earlier text spoke of crashes "after a long modded run").
The AI manager (singleton slot exe+0x3c0abd8, owns the 4 states) is deleted in `CS::MoveMapStep::~MoveMapStep` (0xc31100 -> 0x62ec70
-> 0x62d540 -> manager dtor 0x32f900) and rebuilt by the next world at 0x632280 (alloc 0x3a80, ctor 0x32daf0 creating "AiLua%02u")
[code]; a read-only DLL logged "ai manager deleted / created" at every map move [game]. Nothing carries over between expeditions and
restarting the game does not help; the Roundtable is its own world. Budget every world for EVERYTHING it loads: aicommon + the
open-field tiles + the arena block's scripts + summons + every co-loaded mod's scripts.

- Load: when a binder is ready the engine‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ loads it into all 4 Lua states (text -> parser, first byte 0x1B -> undump). Each
  state has a private 1 MiB heap used only during script calls; loading and GC go to the shared fixed 20 MiB parent heap (one arena,
  exe+0x39d7d98); blocks <= 128 B come from a pool refilled in 8 KB chunks from the arena (0x21d09a0(alloc, 0x2000, 0x80, ...));
  `luaM_realloc` always allocates new, copies, frees the old block - even when the new allocation failed. A full GC of one state runs
  every frame (round robin).
- **Fragmentation decides, not total free**: the fatal dump had 1.47 MiB free in 12,816 blocks and no free piece >= 8 KiB (bins 5..12
  present, 13+ empty). Go / no-go figure = "8k: any free-size bin >= 13 non-empty"; gauge it in game (`diagnostics.md` 2) [code, data].
- **Crash signatures**:
  - access violation in Lua `sweeplist` (string-table loop) half a second after an arena loads, the "next" pointer decoding as a Lua
    instruction (freed script memory reused); heap at the crash 2.24 MiB free, no block >= 64 KB;
  - **map-move teardown OOM** (everyone black-screened and crashed at the end-of-expedition settlement in a 3-player session
    [game-MP]): an AI script unload does `_G[name] = nil` (0x22b8c30, from CSAiLua unload 0x3284d8 / registry 0x3296a0), allocates 40
    bytes, the pool refill fails, `luaD_throw(LUA_ERRMEM)` with errorJmp NULL -> panic -> `exit(1)` -> during static destructors the
    deliberate DL_PANIC "DCManager is not finalized." writes to address 0 at exe+0x214e298 (panic routine 0x214e1d0, caller 0x2219300),
    then a nested stub at exe+0x81d7c5 (a second WER report ~10 s later). Treat settlement / teardown crashes as budget problems (heap,
    character count of always-loaded blocks), not content bugs of the fight [code, data].
- **Source-text AI is the main fragmenter** [code, model]: bytecode undumps into exact-size blocks once; source compiles in-engine in
  all 4 states with doubling vectors and line info, leaving many 4-20 KB transients between resident blocks. Measured per state: a
  102 KB source binder with a 3,745-instruction function requested 567 KB, kept 120 KB, largest block 20 KB; another source script 1.10 MB
  requested (0.86 MB transient), largest block 20 KB; restructured + precompiled 148 KB / 0.18 MB requested = kept, largest block
  2.3-2.6 KB, nothing above 4 KB. One 6,380-instruction chunk: source 574 KB / largest 32 KB; restructured source 718 KB / 5 KB;
  precompiled restructured 104 KB / 2.3 KB. The worst moment is the arena block load on Day 3 when the arena is ~2/3 full.
- **Targets**: no prototype above ~700 instructions / 128 constants (corrected from ~1,000), largest load block <= ~3 KB, nothing >= 8 KB.
- **Restructure**: wrap consecutive top-level statements as `do local __f = function() ... end __f() end` (top-level locals stay as
  upvalues, mind 32); split over-large keyed table constructors into per-field assignments (refuse when iterated with pairs / next or
  positional). **Splitting only the main chunk does not help when the big prototypes are FUNCTION BODIES** (Goal.Activate /
  Goal.Interrupt): precompiling a split main chunk still left a 15 KB block from one 3,745-instruction Interrupt. Hoist instead:
  - move runs of a function's statements into `local __lpN = function(params)` helpers defined once just before that function;
  - turn long elseif chains into a flat cascade of segment helpers (a segment returns a sentinel when none of its conditions held), so
    helpers nest at most 2 deep;
  - pass locals as parameters and read their writes back, as the compiler reports them;
  - return as `return K, e...` and re-issue the same return at the call site;
  - allocate nothing per call.
  Cost: a slightly deeper Lua stack per AI call (one Interrupt went from 25 to 68 slots) [data].
- **Proof set before shipping the bytecode** [data, sim]: (a) every unsplit prototype bit-identical and in order (code, constants,
  nested functions, stack, upvalues, params); (a') split functions pass a round trip (removing the helper wrappers gives back the
  original tokens), a scope check (helpers use exactly the original globals) and a strip check (stripped and unstripped compiles equal);
  (b) the globals a load creates and the tables reachable through upvalues have identical shapes for source / restructured / bytecode;
  (c) decision traces byte-identical, same seed, in a mocked engine that runs the real vanilla aicommon bytecode and traces every engine
  call (long dynamic runs, e.g. 24 x 420 s, plus thousands of random-state cells: Initialize, Activate, every interrupt kind, every TAE
  window, Update, Terminate; report line coverage); (d) the load-cost report. In-game load of each new bytecode build stays to be
  confirmed by the tester (an idle boss = load failure).
- Build: neutralise developer-path strings IN THE SOURCE (a path constant survived precompiling and was caught only by the
  privacy scan) -> restructure -> x64 LuaC 5.0.2 `-s` -> proofs (section 5) -> header / strip check against vanilla (all 118
  vanilla AI members are stripped bytecode with source "=(none)") -> regenerate `.luagnl` -> load-cost report -> pack two
  binders from the input binder as template (precompiled + restructured-source fallback; same member ids, names, flags, DCX).
- `.luagnl` = u64 offsets (0-terminated) + UTF-16LE names of every global the chunk assigns, in order of first assignment, padded to
  16; drop stale names (a stale one lacked 17 names, so unload did not clear them).
- Member 1000 keeps a vanilla-style source path NAME even when it holds bytecode [data].
- Keep a restructured-source fallback binder with the same code for debugging: stripped bytecode has no line numbers, so an in-engine
  error will not say where.
- **Pipeline consequences** [code]: tools that patch AI text take the source from below the bytecode package and re-run the
  precompile; the release builder passes bytecode binders through untouched after a format check (Lua 5.0 x64 header, every prototype
  stripped, source `=(none)`) and refuses anything else that starts with ESC (0x1B); any pack-builder step that touches Lua must pass
  bytecode through; test launchers that patch AI text break - rebuild them from the source.
- Small scripts as source text also load [game], but they fragment: budget the heap for ALL mod bosses loaded together.
- **An arena block's MSB loads all its characters and AI scripts whatever fight is chosen**; EMEVD disable does not unload. The vanilla
  Nightlord block m19_00 carries the AI of all 8 vanilla Nightlords (750000-756000) (~1.57 MiB x4 kept). Another mod boss placed as 13 MSB
  characters in that shared block (5 source-text scripts) was resident during a different boss's fights [data, game log]. Put a mod
  boss in its own block that only its route‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ loads (or spawn on demand - not built [inferred]).
- **Modelled kept cost per context** (x4 states, MiB, vanilla) [model]: aicommon (+ dlc01) 3.58; open field 16 base tiles 6.95; + one
  Shifting Earth variant 7.6-9.5; hub 0.02; arenas m19_00 1.57 / m18 0.12 / m16_00 0.58 / m16_10 0.48. Real use was 1.5-1.8x the static
  model (it omits each live AI's runtime data): trust the rankings, calibrate absolutes with the in-game gauge.
- **Co-loaded mods' AI**: a base pack shipped 65 of 203 AI binders as source and an aicommon with 5 source members (1,532 KB per state vs
  vanilla 906 KB, 80 KB largest block) [data]. Precompiling third-party files is the owner's decision (distribution, credit): propose
  ranked by measured effect and hand the owner a self-contained note with recipe and proofs.
- Spirit / summon AIs load at summon time when no MSB part of the world uses them; a source-text summon script compiled late on Day 3 is
  the leading candidate for "that summon never appears" near a full heap [inferred]. Heap problems reproduce solo (they depend on which
  maps load, not on party size) [inferred].
- **Do not** enlarge the arena with a native patch (writes engine memory) or build a probe that exhausts the heap; validate against a
  dump's free-bin histogram [decision]. Check object lifetimes in code before advising players ("restart the game after each
  expedition" was told and withdrawn).

## 7. Helper-actor AI (multi-actor bosses) [game]

Every helper always holds a real 2-3 s goal (approach / orbit / back off): gating attacks on team-record counts with a 0.7 s
positioning goal froze them. Reaction / turn slots that replay a long idle need AI cancels from 0.3 s. Spawn with a NON-looping
forced idle. A hit while a helper's AI is still off can leave it out of battle: invincible until AI on + a watchdog on the AI
state [sim for the fix].

## 8. Dev-only debug wrappers

The move-control debug panel's AI override is appended to a COPY of the shipped source and lives only in a dev binder that is never
shipped: with its master flag off it must make byte-identical decisions to the shipped AI; requests go through the AI's own attack
path; set pieces are never touched. Design, proofs and release guards: `debug_panel.md` 2.5, 5.

## Unverified

GetDist meaning (surface vs centre); the in-game load of each restructured precompiled build; summon AI compiled late as the cause of
missing summons; the attack goal ending exactly at the AI window (inferred, accepted in game); MHW mFlag
0x10 as release bit; per-angle member choice of source turn families; heap numbers are computed from stock Lua 5.0.2 layouts;
what the engine does with `.luagnl`; whether a failed precompiled load idles the boss.
