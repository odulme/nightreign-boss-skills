# Move debugging: a small tool that controls the boss's moves (dev only)

Build this in stage S3 of `boss_pipeline.md`, before the first attack, and use it in every test step of S4-S10. Tags as in
`SKILL.md`. The design below was built and used in game for a three-phase boss port [game]; numbers in angle brackets are
placeholders you choose for your own mod (`<DBG_BASE>`, `<BOSS_ENTITY>`, `<CHR_ID>`, `<DEV_PROFILE>`).

## 1. Why

- Reaching one move by playing the fight wastes most of a test session: the AI picks moves at random, by distance, stance, phase
  and cooldown; flight moves come every few minutes; phase-3 variants need two thirds of the bar gone; a tester needs 5-15
  minutes to see a given move once, and a fix needs the same move seen several times from several positions.
- Set pieces and forced knock-downs hang on HP thresholds and part breaks; a debug route without help never reaches them twice in
  a row.
- With the panel a move is requested by name, repeated with a pause, seen from chosen positions, and its animation history
  matches screenshots to casts. It turned rounds of "I think it was the left one" into "index 15 at 12:41:07" [game].
- If a move cannot be summoned on demand, it cannot be tested on purpose.

## 2. Architecture

```
 window app (always on top)  <-- named shared memory, no network -->  dev-only native DLL (bridge)
                                                                         | writes ONLY a reserved block of event flags
                                                                         v   (through the game's own flag setter)
                                   dev-only fight-script events  <--  event flags  -->  dev-only AI override (ai:IsEventFlag)
                                   (HP lock, variant override,                          (play move id, AI stop, face /
                                    alive toggle, load-time clear)                       approach / back off, loop + pause)
```

Every piece is dev only. The shipped files are never touched: the dev fight script and the dev AI binder are COPIES of the shipped
ones with additions, installed in one dev-only package that sits last in `<DEV_PROFILE>` (section 5).

### 2.1 Window app

- A small WinForms (or similar) window, always on top, started by double-click (a process started from inside a sandboxed agent
  host may run in a private container and never see the game's shared memory). Play the game windowed or borderless: exclusive
  full screen hides an always-on-top window. Clicking the panel takes focus; click the game window to play on.
- Controls that paid off: one button per catalogue entry (tabs by stance / kind, section 3); **AI stop** (the boss makes no
  decisions of its own, it only plays requests); **HP lock** (cannot die, HP floors at 1); **loop the last move** with a pause
  chosen from a short list (0.5 / 1 / 1.5 / 2 / 3 / 4 / 6 / 8 s - fits 3 bits); **variant override** (auto / base / variant set 1
  / variant set 2: the phase colour / strength sets selected by animIdOffset SpEffects); **face the player**, **approach**,
  **back off**; **stop / clear** (cancels the loop and a request that has not started; the move in progress finishes).
- Tooltips per button: readable name in both languages, AI move key, slot list it plays (fixed or "AI's own choice"), which
  variant timelines exist for it, panel index.
- Closing the window = every debug flag off‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ within ~1.5 s (the DLL sees the heartbeat stop) and the boss returns to its normal AI.

### 2.2 Channel

- Named shared memory (`Local\<name>`, 4 KB) with two blocks: the app block (what the window wants) and the DLL block (what the
  DLL sees). Each block: magic, version, a seqlock (odd while writing, readers retry), a heartbeat counter, the writer's process id.
- App block: idle, loop, HP lock, variant choice, pause code, request counter, request index.
- DLL block: state (ok / disabled with a reason / flag store unavailable), boss present (0 absent / 1 just appeared / 2 stable),
  HP, max HP, current animation, an animation-change counter + a ring of the last 16 animation ids, a bit mask of watched SpEffects
  (phase, final form, set piece running, part-break markers, variant sets, idle heartbeat, busy, rage, stance reset), the flag words
  read back, the last request taken, a result code + text, a write counter.
- Test the channel offline with two processes (a test program using the DLL's own core code on one side, the app in a
  `--selftest` mode on the other) and render the window off-screen to pictures for review.

### 2.3 Native DLL bridge

- One worker thread, every ~50 ms. Fail closed: check the game build (PE timestamp + image size) and the code bytes of every
  function it calls or reads through; on any mismatch log it and do nothing. A `<dll>.off` file next to it disables it. No code
  patch, no hook, no vtable change.
- Finds the boss read-only (model `<CHR_ID>` + `<BOSS_ENTITY>` in the loaded arena block), every read guarded.
- **Writes only its own flag ids, only through the game's own event-flag setter** (compare the setter's and reader's bytes before
  the first call) and reads every write back. On NR 1.3.3.0 (PE TimeDateStamp 0x69e0dc2a) the setter was exe+0x60d330 (179 bytes
  compared) and the reader exe+0x60ce40 (164 bytes) [code, game]; on any other build find them again and keep the byte check. Rules:
  - nothing is written unless the boss is present in the loaded block and has been for >= 1 s;
  - window connected (heartbeat changed < 1.5 s ago) and boss stable: master flag ON and the panel state in the DLL-owned flags;
    otherwise every DLL-owned flag OFF;
  - master goes OFF before anything else and ON after everything else, so the AI never sees a half-written state;
  - a request = the index (7 bits) written FIRST, then a 2-bit Gray-code counter steps by one (exactly one bit changes); the AI
    reads the counter before the index; several presses between two ticks are one request with the newest index;
  - a mismatched write is retried on the next ticks (the dev fight script clears all debug flags once at block load); three failing
    ticks in a row stop all writing for that fight.
- Own the flags as whole bytes nobody else uses (the flag store keeps 8 flags per byte, group = id / 1000): the setter's
  read-modify-write then never clobbers a game write.
- Reports HP, animation, SpEffect mask, flag read-back and the last result to the window.
- Log next to the DLL, rewritten at each start, capped (1 MB): build check, signature count, boss attach facts, each connect /
  disconnect, each request (index + counter), every write failure.

### 2.4 Dev-only fight-script events

Appended to a COPY of the installed dev fight script; every other event stays instruction for instruction; the initialisation
lines go at the end of event 0 (prove that no SKIP in event 0 reaches past its last line, so they always run). All events
`Set Network Sync State(0)`; character instructions only on `<BOSS_ENTITY>`; they read the DLL-owned flags and write only the
EMEVD-owned ones.

| event | rest | what it does |
|---|---|---|
| load-time clear | default, once | at block load clear the whole debug range (DLL-owned + EMEVD-owned), so no debug state survives a load; the DLL re-writes the panel state 1 s after the boss appears |
| HP lock | restart every 0.25 s | master AND lock -> `Set Character Immortality(boss, 1)` re-asserted + an "applied" flag; otherwise, only if applied: immortality off, applied off. The shipped script never sets immortality on the boss, so nothing else is undone |
| variant override | restart every 0.25 s | nothing while a set piece runs; master AND override -> on the first poll save which variant SpEffects are present, then make each variant SpEffect present exactly when its "want" flag is ON (set / clear only where the state differs); override off -> restore the saved set once |
| alive | restart every 0.5 s while master is ON | toggles one flag so the window can show "dev fight script running" (catches a missing debug package) |

Prove offline: read back (original events first, in order, + the new ones; the others identical), run the new events in a small
interpreter of exactly the instructions they use against panel scenarios.

### 2.5 Dev-only AI override

- Dev AI binder = the shipped AI source **byte for byte** + an appended override block, packed and precompiled exactly like the
  shipped binder (restructure, LuaC `-s`, the same proofs as `ai_port.md` 6). Assert the prefix equals the shipped source and that the
  chunk assigns no new global.
- The block wraps a few functions of the shipped AI (decision entry `Think`, the watchdog, the reach check, the play helpers). With
  the master flag OFF each wrapper calls the shipped function with the same arguments: no random draw, no goal, no state write - one
  flag read per decision / update tick. Prove it: sub-goal traces and per-boss state byte-identical to the shipped AI over many
  decisions, on the dev source AND the dev bytecode [sim]; then every panel action with flags on.
- Flags are read with `ai:IsEventFlag(<DBG_BASE> + n)`; multi-bit numbers are assembled bit by bit. Per-boss state lives in
  `ai:SetStringIndexedNumber` (sequence seen, request index, loop phase, an "armed" marker reset whenever the master rises).
- Request handling:
  - taken at the next decision of the battle goal; when the boss stands idle (idle heartbeat present, busy marker absent) a new
    request also ends the current decision at once; a running move is never cut;
  - played **through the AI's own attack path** (pre-turn or back-off, stance switch, spin, after-attack goal), so turning, bullets
    and FX are the AI's; a requested move plays even where the AI's reach test would refuse it;
  - a fixed slot list or "the AI's own choice" for that key (e.g. left / right member by target side);
  - control actions use the common goals (`GOAL_COMMON_Turn`, `ApproachTarget`, `LeaveTarget`), rising from a low stance first;
  - AI stop = no own decisions (short waits, rise from a low stance once);
  - loop: after the move, a wait of the chosen pause, then the move again.
- **Set pieces are never touched**: while the set-piece SpEffect is on, the override yields exactly as the shipped AI does.

## 3. The move catalogue

Generate one table (the single source of truth) from the shipped data, never type it by hand:

- Inputs: the shipped AI source (hash-checked) - its move keys, the slot list bound to each key, the alternative lists the AI itself
  plays for a key (left / right members, flank / front variants); a dump of the installed TAE (every slot exists; which variant
  timelines `aNNN_` exist); readable names from the action catalogue (stable ids, `survey_and_extraction.md` 5) with a fix list for
  names the catalogue has stale or missing.
- Entries: index 1..127 (7 flag‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ bits), AI key, forced slot list or "AI's own choice", group, names in the tester's language and in
  English, note, loopable or control action. Group by stance and kind (e.g. biped melee / biped ranged / quadruped / airborne /
  combos and stance switches / control actions) so the tabs match how the tester thinks.
- The build fails when a key is not an AI move key, a forced list is not one the AI plays for that key, a slot is missing from the
  TAE, an index repeats or leaves 1..127, or an AI-requestable slot has no entry (except an explicit exclusion list with reasons, e.g.
  a roar the tester removed).
- Outputs: the Lua table appended to the override block (ASCII), the app's table (names, slot lists, variants) and an animation-name
  table for the status line (every TAE id + engine ids), plus a json copy.
- Regenerate it whenever the AI binding or the TAE changes; a stale catalogue mislabels moves.

## 4. Status readout and logs

Status lines that paid off:
1. connection: "DLL online / boss present (stable) / dev fight script alive" (alive toggle seen) - or the reason it is not;
2. current animation id + readable name (variant offset shown as "variant n");
3. HP / max HP (%) and "HP lock on";
4. phase, active variant set, "set piece running (requests wait)", part-break markers, rage, idle heartbeat;
5. last request and its result: "started: <anim id> <name>" when the animation history since the request contains a slot of the
   move; after ~20 s without it, a hint (set piece or knock-down running? AI switched off by the fight script? dev AI not installed?);
6. the DLL's result line ("request #n written", "disconnected: all debug flags off", "boss absent: request dropped", "flag write
   could not be verified: writing stopped for this fight");
7. a grey developer line: DLL-owned flag word, EMEVD-owned flag word, write count, last animation ids.

Logs: the DLL log (section 2.3); the shipped sync log (`diagnostics.md` 1) with boss animation, position, yaw, HP and the local
player's position, HP and damage taken - the panel's animation history plus the sync log's time stamps tie every screenshot to a
cast; the AI's debug hook in the offline harness.

## 5. Reserved ids and keeping it out of every release

- **Flags**: a reserved block of 32 DLL-owned + 8 EMEVD-owned flags in an unused, storage-backed (world-class) range of the arena's
  flag group, aligned to whole bytes (storage rule: `nightreign-nightlord-replace` ids_and_planning.md 3, `nightreign-map-port`
  events-flags-ids.md 2 - a flag without storage reads OFF and drops writes); **events**: 4 dev event ids in the same group, disjoint from every flag (an event id > 299 sets
  flag id + slot when it ends or restarts).
- **Flag scan before claiming**: over every EMEVD of every layer (vanilla scripts, every own dev package and release, co-loaded mods'
  releases and dev stages): every decoded integer argument counts (superset of entity / region / flag ids), every event id, event id
  + slot of every Initialize Event, the intervals of every batch / range instruction; plus AI sources, DLL inis (flag lists) and the
  id-claim document. Report used numbers, covering ranges and free whole bytes; the build asserts the claimed ids are free and fill
  free bytes.
- **The scan counts text**: write the debug ranges only in the debug section of the id registry (the scan skips its own section) and
  nowhere else - not in other notes, readmes or skills. A checker failed once because another note quoted the debug ranges.
- **Dev-only package kept LAST** in `<DEV_PROFILE>`, rebuilt by its build script whenever the fight script or the AI binder below it
  changes (`boss_pipeline.md` 4): the build script reads `<DEV_PROFILE>`, finds the effective dev files (later package wins) and
  asserts their hashes equal the expected bases (an explicit allow-base switch for a new base), refuses when a debug package is
  already loaded, and writes only into its own work folder and a NEW DLL folder (path guard refusing release / stage / pins / app-data
  paths). If a rebuild changes the proven DLL binary, put back the binary proven in game.
- **Release guards**: the pinning tool accepts only packages of the release naming scheme and refuses a profile that still names a
  debug / probe block (never pins it silently); the release natives folder accepts only the listed DLLs; the debug build's last step
  proves that pins, release natives and base profile files mention none of the debug files or hashes and that the release payload's
  fight script / AI binder differ from the debug ones. Name every debug file `..._DEBUG` and put a "dev only - never release"
  readme next to each.
- Nobody uses the debug profile on a co-op day; the panel is a solo dev tool.

## 6. What it cannot do (and how to get there anyway)

- **Set pieces and HP-threshold specials are excluded** (the override yields while the set-piece SpEffect is on; the specials are
  started by the fight script, not the AI). Reach them with AI stop + damage down to the threshold. **HP lock does NOT block the
  thresholds** (immortality only floors HP at 1; the ratio gates fire as HP passes them) - lock to keep the boss alive after the
  special, not to avoid it. An external damage multiplier gets there fast, but then that session is useless for balance and
  part-break calibration (it scales HP damage, not part damage; `params_balance.md` 9).
- Requests wait for the next AI decision: during knock-downs, stance breaks and forced clips nothing starts.
- The dev fight script runs the DEBUG route; it cannot show REAL-path behaviour (expedition state, settlement, co-op).
- It does not replace the destination test (real expedition) or a real co-op session.

## 7. Test recipe per move (S4-S10)

1. **Set up**: AI stop on; HP lock if the test may kill the boss; variant override to the set‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ under test (or auto).
2. **Position**: face / approach / back off until the boss is where the move starts in the source; stand where the check needs you
   (in front, beside, behind cover, under the body; a short character too).
3. **Request** the move; wait for "started: <anim id>".
4. **Watch** with the 2-minute list: complete (no early cut), heading (turns only where the source turns), hit timing = visual
   timing, hit size <= what is shown, floor points / pattern placement, FX look and brightness, sound, frame rate.
5. **Loop** with a 2-4 s pause and repeat from several positions / distances / bearings; switch the variant set and repeat.
6. **Log**: note the clock time or take a screenshot per observation; keep the sync log; the panel's animation history ties them to
   the cast.
7. **Compare**: replay the logged positions against the model of that move (hit model, heading model, floor-point model) and against
   the source reference; only then change the move.
8. **Report** with the panel index + animation id + what was seen; label the result (built / installed / tester saw it / accepted).

Stage use: S4 completeness and heading per move; S5 hit / dodge / short-character / cover checks; S6 looks and brightness with a
source picture side by side; S7 behaviour with AI ON (panel off) after per-move checks; S8 set pieces via the threshold route
above; S9 calibration runs WITHOUT trainers or damage multipliers, panel used only to position; S10 never (solo tool) - co-op uses
the sync logs.

## 8. Minimal build checklist

- [ ] Flag scan over every layer; claimed flags fill free whole bytes; event ids disjoint; ranges written only in the debug section.
- [ ] Catalogue generated from the shipped AI + installed TAE; build fails on any missing / foreign entry.
- [ ] Dev AI = shipped source byte for byte + override block; precompiled like the shipped binder; flags-off traces identical to
      the shipped AI on source and bytecode; every panel action tested offline.
- [ ] Dev fight script = installed dev script + the four events; read back; other events identical; interpreter scenarios pass.
- [ ] DLL: build / signature checks fail closed; writes only its own flags through the game's setter with read-back; protocol tested
      offline against a synthetic flag store; `.off` switch; capped log.
- [ ] Window: channel two-process test passes; off-screen pictures reviewed; closing it clears every flag.
- [ ] Debug package installed LAST; build script asserts the bases; rebuilt after every fight-script / AI-binder change.
- [ ] Release guards: pin tool refuses debug packages; natives allow-list; no debug file or hash in pins / payload; files named `_DEBUG`.
