# Boss AI: source behaviour tree -> Nightreign Lua AI

Tags as in `ids_and_planning.md`. Param ids: regulation 10350000; exe facts: NR 1.3.3.0. DS3-family AI notes (binder goals,
dead subgoals) are in the skill `ds3-nightreign-port`. Deep version (THK decoding, Lua structure, harness, build steps):
skill `nightreign-boss-port` `ai_port.md`.

## 1. How a NR boss AI is built [data]

- Lookup: NpcParam -> NpcThinkParam.battleGoalID (e.g. 750000) -> `script/<goal>_battle.luabnd.dcx`; optional logicId ->
  `<id>_logic.luabnd.dcx`; shared helpers in `aicommon.luabnd.dcx` (common_battle_func, common_func_plan, ai_define).
- Binder: member 1000 = the Lua chunk; member 1000000 = `.luagnl` = every global the chunk assigns (SETGLOBAL), in order of first
  assignment. Rebuild the .luagnl whenever globals change.
- Vanilla scripts are **stripped Lua 5.0 bytecode** (same header as the x64 LuaC 5.0.2 bundled with Soulstruct); the largest
  vanilla prototype has 2,746 instructions.
- Skeleton: `RegisterTableGoal(GOAL_<Name>_Battle, "...")` + `Goal.Initialize / Activate / Update / Terminate / Interrupt`; usual
  extra = an after-attack goal (id + 1) whose own Activate queues sideways / spacing moves.
- Act choice (`Common_Battle_Activate`): weights for acts 1..50, one `GetRandam_Int(1, sum)`, first running-sum hit wins. Weight
  999 / 9999 / 10000000 or "only non-zero entry" = forced.
- `SetCoolTime(ai, goal, anim, sec, w, fallback)`: returns 0 if w <= 0, `fallback` while time since that animation <= sec, else w.
- Attack sub-goals (`GOAL_COMMON_AttackTunableSpin`, `ComboAttackTunableSpin`, `ComboRepeat`, `ComboFinal`, ...) pass the
  animation id to `GOAL_COMMON_CommonAttack`; `StepSafety` uses 6000-6003; in-place turns `GOAL_COMMON_Turn` (clips 5000-5003).
- Follow-ups: a 0-s marker SpEffect in the TAE observed with `AddObserveSpecialEffectAttribute`; `Interrupt` answers with
  ClearSubGoal + ComboRepeat. State: `ai:SetStringIndexedNumber / GetStringIndexedNumber`, `ai:SetTimer / GetTimer`, HP ratio
  `ai:GetHpRate(TARGET_SELF)`.
- Target: no Nightlord script changes target; the engine's aggro model (EnemyCommonParam + NpcThinkParam targetSys fields, 100
  on Nightlords) picks it. Nightlords never pick random targets.
- Animation offset sets: SpEffect animIdOffset (NpcParam spEffectID0 = 5400..5403 = none / 1 / 2 / 3) selects `aNNN_` sections;
  registration rule in `character_port.md` 4.
- **How vanilla big moves start** (59 Nightlord ultimates): 48 are started by the AI Lua alone (HP-ratio gate, latch SpEffect,
  SpEffect replace-chain timer, cooldown, reaction). Once per fight = a permanent SpEffect the move applies at t = 0; recurring
  = a replace chain the move restarts. Big acts run ~3-5 times per 480 s fight with 40-120 s locks. EMEVD only forces intro,
  transition and death clips; no live event switches a Nightlord's AI off mid-fight or sets its HP.
- When EMEVD needs the boss to act, it puts a REQUEST SpEffect on the boss that the Lua reads, waits for the boss's own TAE
  "done" marker (re-issue after a time-out), then latches a network flag.

## 2. Porting a source tree (recipe that worked)

1. Decode the source tree into data first: an executable model of every node, pool, counter, register.
2. Write the Lua so one function = one source node (`F.N[<node>]`), plus a binding table key -> animation slot(s) per phase.
   Every diff stays traceable.
3. Source predicates computed in the source game's CODE (no meaning in data): each becomes a named switch, default false, listed
   and asked of the tester. Never invent their meaning.
4. Pre-steps of the source ("turn if behind", "back off within N m") -> `GOAL_COMMON_Turn` (in-place turn clips) and
   `GOAL_COMMON_LeaveTarget` with the source's measured root travel. If turn clips exist‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ for one stance only, let the attack
   spin in the other stance.
5. Keep the engine target (highest aggro) unless the tester decides otherwise.
6. Change cadence only on the tester's decision (raising flight frequency was rejected: few anti-air options in NR).
7. The AI source of truth is the Lua inside the INSTALLED binder: unpack, edit, repack, read back (generator copies drift).
8. Keep a global debug hook (`if <Boss>_Debug ~= nil then ... end`), nil in game, defined by the offline harness.
9. Report fidelity "as installed": weight by source move frequency how much has its own clip, a borrowed clip, or none.

## 3. Fidelity harness (offline; trusted)

- Run the REAL Lua under Lua 5.0 (an x86 5.0.3 build served the harness, x64 5.0.2 the precompile / refactor proofs) with mocked
  `ai` / `goal` objects (load the real vanilla aicommon for vanilla runs);
  log every decision.
- Static cells: phase x stance x distance band x angle bin x state variant (~2,400 cells) x 6,000 draws; compare against the
  exact source distribution by total-variation distance above the noise floor. Dynamic runs: ~200k decisions per phase; move
  frequencies and bigram chains (noise ~0.7 % / 2.5 %).
- Refactor proof: same seed -> byte-identical decision logs for original, restructured and precompiled builds.
- Vanilla fight model for benchmarks (target at reference distances, HP linear over 480 s, SpEffect durations / chains /
  interrupts modelled, animation duration = hkx length): use for ratios between bosses, not absolutes.

## 4. Shipping the script: the AI Lua heap (hard rule)

Pipeline stage: S7 of `nightreign-boss-port/references/boss_pipeline.md` (gate: [sim] fidelity + heap gauge in a real expedition
with the co-loaded mods). Deep version: `nightreign-boss-port` `ai_port.md`.

**Lifetime and budget** [code; game]
- The 4 AI Lua states share ONE fixed 20 MiB arena (static object exe+0x39d7d98: +0x28 free bytes, +0x10 bin bitmap, +0x30
  block count); it never grows. Each binder is loaded into all 4 states; each state also has a private 1 MiB heap used only
  during script calls (loading and GC use the shared arena).
- **The arena is a budget for ONE world, not for a play session.** The AI manager (singleton slot exe+0x3c0abd8, owns the 4
  states) is deleted at every map move (`CS::MoveMapStep::~MoveMapStep` 0xc31100 -> 0x62ec70 -> 0x62d540 -> manager dtor
  0x32f900) and rebuilt by the next world (0x632280, ctor 0x32daf0 creating "AiLua%02u"); a read-only DLL logged "ai manager
  deleted / created" at every map move [code, game]. Nothing carries over between expeditions; restarting the game does not
  help; the Roundtable is its own world. **CORRECTS** "crash after a long modded run" / "second expedition": the crash is
  fragmentation inside one expedition (arena block load, end-of-expedition teardown). Advice "restart the game after each
  expedition" was given once and withdrawn.
- One world must hold aicommon + the open-field tiles + the arena block's scripts + summons + every co-loaded mod's scripts.
  Modelled kept cost per context (x4 states, MiB, vanilla) [model]: aicommon (+ dlc01) 3.58; open field 16 base tiles 6.95; + one
  Shifting Earth variant 7.6-9.5; hub 0.02; arenas m19_00 1.57 / m18 0.12 / m16_00 0.58 / m16_10 0.48. Real use was 1.5-1.8x
  the static model (it omits each live AI's runtime data): trust rankings, calibrate absolutes with the in-game gauge
  (`native_dlls.md`). Measured on a vanilla-based dev route with only one mod boss: 20 MiB free at world start, ~11 MiB after
  loads, minimum 9.67 MiB in the fight, an 8 KiB block available throughout [game]. The worst moment is the arena block load on
  Day 3 when the arena is ~2/3 full.
- **Characters of an always-loaded block load their AI in every expedition there**: m19_00 carries the AI of all 8 vanilla
  Nightlords (750000-756000, ~1.57 MiB x4 kept); a mod boss placed there as 13 MSB characters with 5 AI scripts was resident
  whichever Nightlord was fought; EMEVD disable does not unload [data, game log]. Put a mod boss in its own block that only its
  route loads, or spawn on demand [inferred] (`fight_script.md` 3).
- Spirit / summon AIs load at summon time when no MSB part of the world uses them; a source-text summon script compiled late on
  Day 3 is the leading candidate for "that summon never appears" when the heap is near full [inferred]. Heap problems reproduce
  solo (they depend on which maps load, not on party size) [inferred].

**Fragmentation and the crash signatures** [code; data]
- Lua objects <= 128 B come from a pool refilled in 8 KB chunks from the arena (0x21d09a0(alloc, 0x2000, 0x80, ...)). **Gauge the
  largest free block, not total free**: the fatal dump had 1.47 MiB free in 12,816 blocks and no free piece >= 8 KiB (free-size
  bins: bin n = [2^n, 2^(n+1)) bytes; bins 5..12 present, 13+ empty) -> "8k = any bin >= 13 non-empty" is the go / no-go figure.
- Teardown OOM (3 players, end-of-expedition settlement, every machine exited): an AI script unload does `_G[name] = nil`
  (0x22b8c30, from CSAiLua unload 0x3284d8 / registry 0x3296a0), allocates 40 bytes, the pool refill fails, `luaD_throw(LUA_ERRMEM)`
  with errorJmp NULL -> panic -> `exit(1)` -> during static destructors the deliberate DL_PANIC "DCManager is not finalized." writes
  to address 0 at exe+0x214e298 (panic routine 0x214e1d0, caller 0x2219300), then a nested stub at exe+0x81d7c5 (a second WER
  report ~10 s later) [game-MP, code]. When a fault is a DL_PANIC inside atexit / static destructors, read further down the
  stack for the real exit cause.
- Load-time crash: source text is parsed in-engine with doubling vectors and line info: a 6,380-instruction main chunk needed
  32 KB blocks x 4 states. `luaM_realloc` frees‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the old block even when the new allocation fails -> dangling pointer -> later crash
  in the GC sweep (an access violation in Lua 5.0 `sweeplist` shortly after the arena loads).
- [data] An earlier crash dump with several mod AI scripts: 2.24 MiB free, no free block >= 64 KB.
- **Source text is the main fragmenter**: bytecode undumps into exact-size blocks once; source compiles in all 4 states and
  leaves many short-lived 4-20 KB blocks between long-lived ones. One port's source: 1.10 MB requested per state, 0.86 MB of
  it transient, largest block 20 KB; precompiled + restructured: 0.18 MB requested = kept, largest block 2.3 KB [model of the
  Lua 5.0.2 x64 allocator]. Another: a 102 KB source binder requested 567 KB per state (kept 120 KB, largest block 20 KB); its
  restructured bytecode 148 KB = kept, largest block 2.6 KB [model]. A co-loaded base pack shipped 65 of 203 AI binders as source and an aicommon with 5 source members (1,532 KB
  per state vs vanilla 906 KB): precompiling third-party files is the owner's decision (distribution, credit) - propose, ranked by
  measured effect, with a self-contained recipe note [data].
- Do not enlarge the arena with a native patch (writes engine memory) and do not build a probe that exhausts the heap; validate
  against the dump's free-bin histogram [decision].

**Fix [game]: ship stripped, precompiled x64 Lua 5.0.2 bytecode with small prototypes**
- All 118 vanilla AI members are stripped Lua 5.0.2 x64 bytecode with source name `=(none)` [data]. Compile with x64 LuaC 5.0.2
  `-s`; check the header against vanilla (ESC Lua 0x50, little endian, int 4, size_t 8, instruction 4, number 8).
- Targets: no prototype above ~700 instructions / 128 constants (**REFINES** the older ~1,000), largest load block ~3 KB,
  nothing >= 8 KB. Restructure first: wrap main-chunk sections as `do local __f = function() ... end __f() end`; split huge keyed
  table constructors into per-field assignments (refuse when the table is iterated with pairs / next). Result once: load cost per
  state 574 KB requested / largest block 32,768 B (source) -> 104 KB / 2,264 B, no transient allocations; real long expeditions
  and co-op ran without the crash afterwards.
- **Precompiling alone is not enough when the big prototypes are FUNCTION BODIES** (Goal.Activate / Goal.Interrupt; one 3,745-
  instruction Interrupt left a 15 KB block). Hoist instead: move runs of a function's statements into `local __lpN =
  function(params)` helpers defined once just before that function; turn long elseif chains into a flat cascade of segment
  helpers (a segment returns a sentinel when none of its conditions held), nesting at most 2 deep; pass locals as parameters and
  read their writes back; return as `return K, e...` and re-issue the same return at the call site; allocate nothing per call.
  Cost: a slightly deeper Lua stack per AI call (one Interrupt went from 25 to 68 slots) [data].
- Proof set before shipping the bytecode [data, sim]: (a) every unsplit prototype bit-identical and in order (code, constants,
  nested functions, stack, upvalues, params); (a') split functions pass a round trip (removing the helper wrappers gives back the
  original tokens), a scope check (helpers use exactly the original globals) and a strip check; (b) the globals a load creates
  and the tables reachable through upvalues have identical shapes for source / restructured / bytecode; (c) byte-identical
  decision traces with the same seed in a mocked engine running the real vanilla aicommon bytecode (long dynamic runs, e.g. 24 x
  420 s, plus thousands of random-state cells over Initialize, Activate, every interrupt kind, every TAE window, Update,
  Terminate; report line coverage); (d) the load-cost report.
- **Regenerate `.luagnl` by the vanilla rule** (every global the script assigns, in order of first assignment): a stale one
  lacked 17 names, so unload did not clear them [data].
- Plain source loads too [game] and is fine for small scripts; budget the heap for ALL mod bosses loaded together.
- If a precompiled chunk fails to load, the boss idles and never attacks [inferred]: keep a restructured-source fallback binder
  with the same code (stripped bytecode has no line numbers, so an in-engine error will not say where).
- Precompiling drops comments but KEEPS string constants: neutralise path strings in the source and scan the bytecode constants
  (a developer path survived precompiling once).
- Pipeline consequences [code]: tools that patch AI text take the source from BELOW the bytecode package and re-run the
  precompile; the release / pack builder passes bytecode binders (first byte 0x1B) through untouched after a format check (Lua 5.0
  x64 header, every prototype stripped, source `=(none)`) and refuses anything else that starts with ESC; test launchers that
  patch AI text break - rebuild them from the source.
- Debug-panel wrappers (play a move by id, AI on / off ...) belong only in a DEV AI binder (shipped source + appended wrappers that
  read flags and route requests through the AI's own attack path); with the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ flags off its sub-goal traces must be byte-identical to
  the shipped AI's [sim; game]. The tool: `nightreign-boss-port/references/debug_panel.md`; it never ships.

## 5. Move completeness and turning

- AI windows = TAE JT23 / 86 / 78 / 79: the attack goal ends at the window and the next request cancels the clip. No window
  before the last content or the source's release point [game].
- Goal life of an attack (`AttackTunableSpin` life) >= clip length, or the goal times out mid-clip [data].
- Heading: attack TAEs hold heading (224 = 0 + JT7); turn windows only where the source rotates; pre-turn with in-place clips
  outside +-45 deg [game]. Details: `character_port.md` 6.
- With the AI OFF there is no engine turning [game]: aiming during a set piece needs an AI-driven mode (forced target + TAE turn
  windows), not helper warps.

## 6. AI and EMEVD together

- Preferred (vanilla) architecture: specials are AI acts; payload (damage, bullets, FX, marks, timers, phase markers) in TAE
  events and boss SpEffects (992 of 993 Nightlord TAE SpEffect applications use net-synced rows); EMEVD only reacts and presents.
  This is also the co-op-safe architecture (`coop.md`).
- If EMEVD must start a special: the Lua stops choosing NEW acts while a pending flag / SpEffect is set; the event waits for a
  fresh idle heartbeat with a fallback time-out (~4 s; a phase AI that never idled starved the gate once) [game].
- Every EMEVD wait that runs while the boss AI is OFF needs an `IF Elapsed Seconds` escape (one missed flag left the AI off for
  good) [game].
- Never switch the boss AI off on client machines and never drive the boss with per-machine EMEVD commands (`coop.md` 4).
- HP-ratio triggers in EMEVD worked solo [game]; vanilla keeps such gates in the Lua (`GetHpRate`), which replicates. Use only
  the ratio API in the AI, so a base-HP change needs no AI edit (`balance.md` 3) [code].
- Summoned helpers with their own AI: `isHostSyncChr 0` and AI ON on every machine (`coop.md` 1) [game-MP].

## Unverified

Converting event-driven specials to AI-requested moves (designed, not built); which machine simulates the boss (host assumed);
pace numbers of the strafe tuning are model outputs; the in-game load of a hoisted (function-body-split) bytecode binder was not
yet confirmed when the proof set passed; whether a late-compiled summon script explains a missing summon.
