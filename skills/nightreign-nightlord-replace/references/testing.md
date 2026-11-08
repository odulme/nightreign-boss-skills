# Testing protocol: dev entry, debug vs real, quick-test kit, offline proof, the tester's time

Tags as in `ids_and_planning.md`. The tester plays; agents never launch, attach to or drive the game (no computer use), never
read or write saves, never touch process memory. Pipeline stage: S12 "Live feedback loop" of
`nightreign-boss-port/references/boss_pipeline.md` (every report -> one dev overlay -> tester -> only then the next pack).

## 1. Layered dev entry, dev first

- One dev entry per line of work: `<Mod>_dev.me3` with its own `savefile = "<Mod>Dev.co2"`, `start_online = false`.
  Packages: one consolidated base -> overlay 1 -> overlay 2 ..., each `load_after` the previous one; natives listed explicitly.
- [data] When two packages ship the same relative path the later-loaded wins; the me3 log (`%LOCALAPPDATA%\garyttierney\me3\data\
  logs\<profile>\<time>.log`) prints one `override=<path>` line per served file - the final proof of which copy is live (no line =
  never requested). me3 resolves relative paths from the profile's folder.
- Each round = ONE overlay with only the changed files, in a NEW folder (`<dev>/<mod>_vNNN/mod`); never overwrite a round folder
  (they are the rollback history). Install with `scripts/publish_overlay.py`: asserts the expected last package, appends exactly
  one `[[packages]]` block, re-parses the TOML, copies with exclusive create + sha256 check, backs up the old entry text, writes
  an install manifest. Rollback = remove the block or restore the backup. One profile held ~48 such packages for one boss.
- **Dev first, then pack** [game]: every change goes into the dev profile as a new top package and the tester confirms it in game
  before it is packaged. Both times a feature went straight into a release package, the release failed (a hub-layer feature,
  key items, shipped in two packs without a dev route because "the dev profile cannot show it"). Give pack-layer features a dev
  route (a dev-only hub event / overlay). Shipping untested is the owner's explicit, labelled decision.
- **Install guards** of each dev package's install script: refuse when the game runs (0-thread processes ignored), when the stage
  hash is not the verified one, when the current top package is not the expected one, or when the target folder exists; back up
  the profile. The next chain build asserts the new top package (`ids_and_planning.md` 7: `packages[:-N]`).
- **Order per feature**: (1) read-only research with evidence labels; (2) build into a stage folder only; (3) verify by an
  independent re-run, not by the builder; (4) install into dev; (5) in-game test; (6) release build from the dev top package;
  (7) release diff against the previous release; (8) joint pack; (9) patch.
- Merge overlays‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ into a new consolidated base now and then (stack compare first, section 4).
- Risky sub-features get their own test launcher (main entry + one test package) that refuses when the main package is not its
  base; after approval merge the byte-identical files into the main line and empty the test layer.
- **Debug-panel package kept LAST** (the tool: `nightreign-boss-port/references/debug_panel.md`): the overlay publisher only
  appends, so a later package shipping the same paths (fight script, AI binder) shadows or is shadowed by it. Each time the fight
  script or the AI binder changes: remove its block, repoint the next block's `load_after`, install the new package, rebuild the
  debug package on the new base (explicit allow-base flag), re-add it last; packages shipping other paths may sit after it. Before
  any pin / release step take a profile copy without debug and probe blocks; the debug package and its DLL never ship.
- Delete your own superseded entries (and their package folders once the game is closed) in the same step; the tester otherwise
  launches stale ones. Entries of other lines of work: ask first.
- Game running: adding NEW files (new .me3, new package folder, new DLL name) is safe; overwriting a file the running game loaded
  (DLL, mod file, regulation) waits for the game to close or goes to a new name. Check the process first; a `nightreign.exe` with
  0 threads / 0 handles is a kernel-held zombie (only a reboot clears it) - not a running game (`release_packaging.md` 1).
- Never write in place into a frozen stage folder (old stages may be hard-linked to each other; view folders may hold junctions:
  never delete those recursively).
- Dev patches that pass their own offline checks are installed without a separate audit; the tester verifies in game. Packages
  for other people get one audit + one re-check.

## 2. DEBUG vs REAL mode in the scripts

- Gate every test-route behaviour (debug endings, retry dialog, debug warps, recovery at load, flag clears, item hand-over) behind
  LOCAL debug flags that only dev-only files can set (Roundtable debug object, debug m10 events). The release drops those files
  and rows; a verifier proves no shipped EMEVD (including the pack's own) can set a debug flag.
- The dev entry runs DEBUG, so it cannot show a REAL-only fix: say so to the tester.
- REAL-path audit before shipping (`fight_script.md` 4).
- A debug route without an expedition (flag 7500 OFF) cannot test downs / revives / defeat: use DEBUG mode there, not a
  "real-like" mode.
- The dev entry is usually solo, depth 0, without the co-op DLL or a forced-depth add-on: list the shipping configuration (co-op
  DLL, forced Deep Night depth, co-loaded mods) and calibrate balance in it at least once (`balance.md` 2) [game-MP].
- A show build can sit in a vanilla arena slot before any own map exists (`fight_script.md` 3).

## 3. Quick-test kit (pack route), never shipped

- Separate profile (`<pack>_<Mod>_quicktest.me3`) with the dev save; = release profile text + one overlay (Roundtable dialog that
  warps to the hub and hands over the switch items, one text binder, regulation + one item-lot row) + its own install / uninstall.
- One spec json holds every id, text and event line of the kit; builder, verifier, trace model and guard read it. Pick kit ids with
  a typed scan over every layer including other mods' dev stages (a kit's event id once equalled a new guard flag).
- The kit refuses to install on any release but the one it was built for; rebuild it and re-run its installer after each release.
- **Release guard**: scans the release folder AND the zip and fails on any kit trace (file names, kit strings in UTF-8 / UTF-16LE /
  GBK, a .me3 with a non-release savefile, kit event / flag ids in any EMEVD, kit text ids in any FMG, the dev item-lot row);
  `--selftest` = positive control on the kit itself. Wired in after assembly; must exit 0.
- The kit does not reproduce the open field below the hub, the Lua heap of a real world, expedition state, end screens, co-op.

## 4. Offline proof before asking for a real run

- An offline PASS is a weather forecast: useful for planning, never proof of the weather.
- "Nothing changed" -> audit the INSTALLED package: dump every event, MSB, TAE, param from the files the entry really loads.
- Every builder: deterministic, inputs as arguments, writes only changed files, ends with PASS / FAIL + check count, and an
  independent read-back proving that only the named lines / cells / members changed.
- Regulation writes get a new container IV each time: compare decrypted member content, not file hashes [data]. Pack EMEVDs may be
  DarkScript3 round-trips: compare events after masking parameter bytes, not bytes.
- Stack compare: the chain's computed effective set must equal the installed dev stack (later package wins per path,
  case-insensitive) before a release is built from the chain.
- Offline scenario simulators on the real event lines: win / lose per target arena (credit, text, 7000 / 7001), host + clients
  for co-op flows, plus a negative control (the previous script must FAIL the new check). Label results [sim]; a simulator never
  clears a co-op bug (`coop.md` 10).
- Offline replay of logs: replay logged player and boss positions against the hit model / damage-area event lines on a 1 m grid
  to locate damage-area bugs (it found a hover-point sector error, a mis-parked helper, a reviver geometry); align host and client
  logs by UTC [model]. Models and renders reproduced each tester report before the fix (`nightreign-boss-port` `testing_qa.md`).
- Release due diligence: a table "files whose‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ FIRST in-game run is this release" (tell the tester), a release-vs-previous diff,
  and a list "unprovable offline, most likely to cost a session".

## 5. The tester's time and the feedback loop (a real expedition costs 30+ minutes)

- One unified install per round, not one per fix; the tester tests several dev overlays per session. Say which ones are active,
  what to look at per move (a 2-minute list), and what is unproven; the tester's "pass" for a batch is the pack trigger.
  Verify renumbered / merged scripts in the dev entry before building a release.
- After each install tell the tester: entry name and package list; what changed; exactly where to look (a 2-minute checklist); what is
  proven vs unproven; how to roll back. No long PASS reports. Evidence labels in every report: built / installed and read back /
  tester saw it / tester accepted; [model] and [sim] are never "fixed".
- Every co-op fix gets its own switch so it can be reverted alone; tell the tester that.
- Ask for the exact visible sequence early, ask for a recording after two failed paper explanations, ask what they see before
  guessing a mechanism.
- **Before analysing any log, ask**: trainer / damage multiplier / HP lock / buffs on?; character, level, weapon, relics since the
  last test; profile (dev entry vs pack with co-op DLL and forced depth); solo or co-op, host or client; what they aimed at; the
  exact spot (screenshot + debug-panel history); hit or not when the log cannot tell [game].
- Ask what each element of a screenshot is before interpreting it (an empty inventory cell plus a costume placeholder icon seen
  through the menu was misread as "our item listed but broken"); for look problems ask for a source-game reference picture next to
  the screenshot (it settled smoke vs fire billow at once). "Stray flames in move X" may come from another move sharing X's FX: ask
  which move, which side, and whether it appears together with the move's own effect [game].
- Check the test machine before blaming the mod for an FPS drop (a drop after half HP coincided with unrelated CPU-bound processes)
  [game]. Check object lifetimes in code before advising players (a "restart after each expedition" heap tip was withdrawn).
- Present options with numbers; the tester decides; record it; build the default and keep alternatives one flag away. Quote the
  tester's numbers and the model's side by side; solve linear targets on the real damage curve and say so. Ask targets as HP-bar
  fractions. Accept fidelity calls (source lines instead of prompts, source-size circles, uninterruptible set pieces) and never
  argue them with inferred mechanics [game].
- After an in-game failure, do not stack a new paper cause on a piece never seen to work (an FX never seen, a helper assumed to
  have moved): rebuild from pieces already proven in this port and verify against a replay of the tester's logged positions.
- Order of tests per feature: dev entry (DEBUG) -> quick-test kit -> one real solo expedition -> co-op session.

## 6. Runtime probes, logs, crashes and GPU hangs

- EMEVD dialog probe: generic dialogs with own EventTextForMap texts (zhocn + engus) at each state change; the tester reports the
  letter sequence (settled the backward-GOTO question). Remove after.
- DLL logs: rewritten at each game start, attach facts (boss found, HP at attach = proof the scaling applied), block load /
  unload / position table, co-op sync log, AI-heap gauge; shipped as runtime files the installer ignores, rolling, with a size cap
  (`native_dlls.md`). For co-op collect every machine's log right after the session (`coop.md` 11).
- Crash: Application event 1001 gives the module offset. **Minidumps hold the exe's static .data** (enough for the AI arena
  counters and free bins), not Lua heap contents - **CORRECTS** "minidumps hold no heap" [data]. Read-only dump tooling: an x64
  `.pdata` unwinder on the on-disk exe of the same build, per-frame registers with RTTI, function naming from assert strings and
  RTTI, a per-dump singleton-slot table, the arena gauge, a HEAP_FAILURE_INFORMATION reader. Before attributing a crash, look for
  the same signature in dumps from before the mod existed (a quit-time c0000374 in a GameMan teardown, 0x6aaaa0, was in 9 dumps
  incl. pre-mod ones: base setup). Players get a read-only crash collector.
- Settlement / teardown crashes: treat as budget problems (AI heap, characters of always-loaded blocks; `ai_lua.md` 4), not as
  content bugs of the fight [game-MP].
- **GPU hangs (TDR) on one machine** [game-MP]:
  - Separate overload from a fault: one tester's PC, ~1 in 3 fight openers, 0 crashes in 100+ other fights = a boss-specific
    trigger even when frame times are fine; frame logs showed a steady 60 fps (max frame 39 ms) up to the hang, which started
    within one frame.
  - Get a DRED report from a DLL (`native_dlls.md`): DEVICE_HUNG without a page fault, stopped in the effect / transparent pass
    at the densest alpha-blended moment (~230 FX alive, up to ~1,500 particles per laser, tracer ribbons, a point light per
    laser). Only the affected machine reproduces it: ship diagnostics (DRED, labelled draws), not guesses.
  - Audit converted assets against vanilla before guessing: every index < its mesh's vertex count, every weighted bone index <
    bone count, buffer length = stride x count, no NaN / Inf in vertices, bones, dummies, boxes, FXR values or gparam, texture data
    matching declared mips / format / size, every reference resolving, FXR field layouts and action types that vanilla uses. Unique
    traits found and removed (both invisible): invisible helper FLVERs with 81 meshes of 0 indices (37 MB never drawn; vanilla
    invisible helpers have 0 meshes) and HUD items hidden with an all-zero matrix (vanilla uses alpha 0). They did not stop the
    hang; thinning the densest emitter did reduce reports (sparkle max 1000 -> 40, -74 % effect load per laser, 16 bytes changed,
    look kept), sample small.
  - Budget for "denser without more crash risk": time-aligned quad fill <= the heaviest move that already ships; particles <=
    1.5x; FX alive not higher; no new point-light / distortion / radial-blur / tracer / GPU-particle node; FXR changes only as byte
    copies with in-place values (`nightreign-boss-port` `fx_sound.md`). Count lights per instance in map-region FX (96 of 99 point
    lights of one breath came from one ground FX x 48 regions).
  - Ship testers a small collector (OS event-log entries for display-driver resets and app crashes, WER folders, kernel
    live-dump names, the mod's logs, a fixed list of running overlay / capture tools; no personal files). Tester-side factors:
    memory overclock profiles, overlays / capture tools, driver debug options, virtual display adapters. Heap-corruption crashes
    with display-driver frames on the stack belong to the same investigation.

## 7. Measuring and probing (break progress, trainers, probe design)

- **Trainer pitfall**: external trainers / damage multipliers scale HP damage but not part damage, so a part seems to lose only a
  fraction of each displayed point. One calibration of a solo head break was made with a trainer multiplier on (confirmed by the
  tester): any "part HP loses ~0.2 per displayed point" reading from it is that artefact, never an engine factor. Co-op pack fights
  without a trainer fit ~1 per point, as the code says. Before using any log for calibration ask about trainers, HP locks, buffs and
  level changes; bases tuned with a trainer on must be re-checked without it [game for the trainer; generalisation inferred].
- **Log-only probe** [game, twice]: host / solo-only events wait for fight start + a few seconds (records must exist, `IF NPC Part
  HP` is TRUE for a missing record); on `IF NPC Part HP(part, T, <)` each applies a one-shot boss SpEffect with a tiny distinctive
  changeHpPoint that the damage DLL logs as "HP lost without a hit: N". Use amounts whose singles, pair sums and sums with known
  damage-over-time ticks are distinct (3 / 5 / 7 / 11 / 17 works; 3 / 7 / 13 / 19 / 29 collides: 3 + 29 = 13 + 19); two probes in
  one frame log as one sum. Thresholds on the part (90 / 75 / 50 / 25 %) AND on any carrier (max - 2000) separate the hypotheses.
  Thresholds are absolute (valid for‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the tested depth / party only). Build behind `--probe`, never ship or pin it.
- **Classify hits by the boss's hit reaction, not by position**: a boss-local "head box" over-counted neck / chest hits (13-16 %
  head share once, real 72-75 %). On the c4510 graph, 9090 = weak-part group 31, 9100 / 9110 / ... = PartBlend n per group (76 of 79
  matched the posed geometry); or use value pairs (same attack x1.2 = head) [game, data].
- **Probe design**: every outcome must map to a cause; include a vanilla control; banners at the probe event's start and end;
  unique display names per probe entry; report popup and listing (or spawn and visibility) separately. A visible dev marker on an
  invisible damage volume separates "never spawns" from "spawns, FX invisible" - make it distinct, ask about it explicitly, and
  switch it off in the release build [game].
- Vanilla censuses settle undecoded semantics (event durations, events shorter than their interval, warp dummies in 199 scripts,
  ...), then confirm with one in-game look [data].

## 8. What to test when

- AI / Lua changes: solo, start to kill; watch for an idle boss or summon (a load failure), attack mixes and set-piece pauses.
- Event sync changes: a co-op session with DLL logs on every machine, then a log comparison by offset.
- 4-6 players: real 4-6 player sessions; simulator identity runs only protect 1-3 players.
- GPU hangs: only the affected machine reproduces them (section 6).
- HP: compare the logged max HP with the published table (`balance.md` 3).
- Breaks: in the shipping configuration, without a trainer (section 7).
- Do not state vanilla mechanics deduced from menus or params as facts; ask an experienced player first.

## 9. Checklist templates

**Per round (solo, dev entry)**: boss passive until arrival; bar + name (every language you ship); music start / heat-up / stop;
sound effects present (a broken bank silences everything); each changed move once (debug panel); phase transitions; part breaks;
victory text + music; nothing left on the player afterwards.

**Real solo expedition**: buy / crush item; gate with and without item (vanilla fight still works); entry without loading screen;
fight, kill, normal settlement and result screen; death -> revival token used once -> defeat flow; buffs from the hub survive;
key items listed once.

**Co-op session** (each player reports their own screen; columns "what to look at" / "if not, tell me"): same fight for everybody;
same take-off / landing / breath point on every screen; a mark on the same player everywhere; each hit lands once; cast bars move
on clients; summons animate on clients; a sheltered player beside an exposed ally is not hit; downed / revive / wipe as vanilla;
no leftover bar / mark / effect after a special; who was host; ping; every machine's log collected.
