# Co-op (vanilla 3 players, Seamless Co-op up to 6)

Tags as in `ids_and_planning.md`; **[game-MP]** = seen in a real multi-machine session (usually with DLL logs from every
machine), **[sim]** = offline only. Exe / ids: NR 1.3.3.0, regulation 10350000. A solo pass proves nothing about multiplayer
branches. Pipeline stage: S10 of `nightreign-boss-port/references/boss_pipeline.md` (gate: [game-MP] numbered checklist, every
machine's log collected).

## 0. Instruction cheat-sheet [code / data]

| instruction | meaning |
|---|---|
| `2000[2] Set Network Sync State(0 / 1)` | per event; 0 = each machine runs it for itself |
| `3[26] IF Player Is In World Type(g, 0)` | own world = host; `1003[12] SKIP IF Player Is In World Type(n, 1)` = "client skips n lines" |
| `3[6] IF Multiplayer State(g, 4)` / `1003[5] SKIP IF Multiplayer State(n, 4)` | 4 = Singleplayer, 0 = Host, 1 = Client, 2 = Multiplayer, 3 = Pending |
| `2003[66] Set Event Flag` | local write only |
| `2003[69] Set Network-connected Event Flag` | the same write + a send; works inside sync-off events |
| `2003[22] Batch Set Event Flags` | local, one id at a time |
| `2003[18] Force Animation`, `2004[14] Rotate Character`, `2004[41] Issue Short Warp Request` | act on the LOCAL copy only; no owner test, nothing sent [code] |
| `2004[28] Set Network Update Authority(ent, 0 / 8192)` | Normal / Forced |
| `2004[89]` | in-map player warp (no loading screen) |
| `2011[1] Activate Hit(part, 0 / 1)` | collision part on / off; per machine, nothing sent [data] |
| `Shoot Bullet(owner, target, -1, behaviour, 0, 0, 0)` | the bullet exists on the firing machine only (section 1) |

Entity 10000 = local player; 20000 = own player in vanilla sync-off loops; 10002-10004 = players 1-3; 10005-10007 = players 4-6
under 6-player add-ons.

## 1. What replicates and what does not

- Boss AI runs on the authority machine; vanilla gives the host Forced authority through common 90075902 (sync off, restarts on a
  host change). Run it for EVERY boss entity (phase 2, helpers you need consistent) [data; game-MP].
- Animations the host forces on the boss are seen on clients [game-MP]. **Only on characters that replicate**: host-only forced
  animations reached clients on the boss, but nothing arrived on summons with `isHostSyncChr = 1` [game-MP]. Test this per
  character type before relying on host-only animation lines.
- **A client copy whose LOCAL AI is switched off stops following the host** (frozen in its last loop); nothing from the host
  turns it back on. When its AI comes back on it is pulled to the host = visible teleport [game-MP].
- A host-only warp of an ENABLED, AI-on boss copy put it at the same place on every screen [game-MP]. A character a client has
  not enabled yet misses a host warp: enable on every machine first [game-MP symptom, cause likely] - but after a host-written
  network flag, not on the client's own clock (vanilla clients never enable before host-produced state) [inferred].
- **Summoned / helper combat characters: `isHostSyncChr = 0` and AI ON on every machine, as vanilla** [data; game-MP]. With 1
  (rows copied from a boss donor) three summoned swords never animated on clients: they stood at their warp points and died there,
  although their HP reached the clients. Every vanilla Nightlord body, add, helper and clone in m19 has 0 (e.g. the Everdark Libra
  clones of common_func 99075466), and vanilla switches their AI on on every machine (99075466, 90075001, 90075452). Shipped fix:
  flag 0 on the summon rows and the `SKIP 1 IF WorldType(client)` in front of the AI ON line removed. Optional: `Set Network
  Update Rate` for the summons as vanilla does for boss bodies [data].
- SpEffects the host's event SETS on the boss reached clients; the host's CLEAR did not (clients kept stacked damage cuts)
  [game-MP, mechanism likely]. Put persistent boss state in self-expiring rows, or every machine sets AND clears its own copy.
  Vanilla Nightlord events never use Clear SpEffect (0 of 224).
- 992 of 993 SpEffect applications in vanilla Nightlord TAEs use net-synced rows [data]: state carried by the boss's own
  animations and SpEffects replicates for free.
- **Event bullets are local**: a player is hit only by what their own machine fires [game-MP]. Anything a machine must produce
  for its own player (event bullets, hit volumes, FX, player effects) must never sit behind a host-only gate. The same fact makes a
  boss-centred lethal sphere safe in co-op: fired by each machine in a sync-off event, it overlaps every player's copy on that
  machine but hits only the own player [game-MP log: a client under the boss was shot by his own machine at both‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ blasts; the host's
  machine did not shoot the host there].
- Damage-module hit handlers run only on the machine that owns the attack [code]; per-hit tools see own hits only. Remote full hit
  packets go 0x51f040 -> ApplyDamage directly, past a private-vtable hit hook: a DLL damage correction in the hook is wrong in
  co-op (`native_dlls.md`) [code].
- **NPC part HP is per machine, the break decision is the host's** (`fight_script.md` 7). Part HP is decremented only where
  ApplyDamage -> CalcDamage runs (local hits and full hit packets; compact HP packets do not touch it): the host counts everyone, a
  client misses the host's own hits, yet a client copy can still reach 0 from its own hits. **CORRECTS** the earlier "first machine
  at 0 commits by network flag, the others adopt": that broke the head early [code, sim; game-MP plausible].
- Party scaling: vanilla MultiPlayCorrection 7767 -> 7867 / 7967 via 90015012. **Under Seamless Co-op these two never appear on
  the boss**; the co-op mod scales HP itself (`balance.md` 2) [game-MP]: logic keyed on "boss has 7867 / 7967" never fires there.
- Copies under a host-driven set piece agreed within ~1 m / ~1 deg at a breath start [game-MP log]; clients' scripted hits land
  0.1-0.6 s after the host's when their script follows a host flag [sim]; replicated AI attacks show ~0.34-0.48 s client offset
  [game-MP log].

## 2. Flags in co-op

- Shared state with 2003[69]; 2003[66] is local [code]. Storage class from the 4th digit (`ids_and_planning.md` 3); keep it.
- Write a network latch once, as a level; re-test the flag on the line before the write; never OFF and ON in the same frame
  (arrival of the pair is undefined) [data; a follower chain keyed on such a pair broke, game-MP].
- **One-hot publishers** (target slot, branch, take-off point): clear the other members first and set the new one ON one frame
  later. A target-slot publisher that switched slots OFF / ON in one frame misfired [code fix, sim, game-MP report].
- Host refresh: re-send ON level flags every 2-3 s for late / lossy machines [data idiom; sim]. Single writes reached the others
  within ~1 s both ways [game-MP].
- The host's AI Lua reads the host's LOCAL flags only [inferred]: every flag the AI reads must be set on the host.
- Do not let clients write local flags with ids the host also reads (whether they reach the host is unresolved).
- **Flag scope**: never put a network flag into a local batch reset (a reset on one machine does not reach the others and the
  host's refresh re-sends it later) [game-MP fix].

## 3. Vanilla idioms to copy [data]

- By default every machine runs the same state machine keyed on replicated BOSS state: `END IF 7512 / IF boss has sp X / act /
  IF boss NOT sp X / RESTART`.
- Host decision = host TERM INSIDE the waited condition (`IF ANDn Player Is In World Type(0)`), never `END IF` (a new host then
  satisfies it without restart), then `SKIP IF client` right behind the wait; what follows is an NPC action or a network flag,
  never an action on a player.
- Random draws: "Randomly Set Network-Connected Event Flag" behind a one-machine gate.
- Network barrier: `IF OR elapsed 9 / IF OR flag ON / IF MAIN`, then flag ON: the first machine through pulls the others.
- Effects on players: the OWNER applies them to 20000 in a sync-off event keyed on boss state, ended by an end-effect row or
  duration; view-only copies for other slots use rows with isDisableNetSync 1.
- Party state: each machine publishes its own standing flag 7005 + n (common 1182); downed = team type 77, not HP.
- Fight start / death / victory events are un-gated on every machine (90075900 / 90075901).
- Phase switch (Heolstor 90075703): trigger = a boss SpEffect from its own animation; barrier; fade + freeze; each machine warps
  ONLY its own slot; second entity enabled + animated + AI on; only elapsed-time waits inside the black window.
- Every set-up / switch event has a REBUILD head: `7512 -> clean up + END`; `start flag ON -> jump to the current phase from
  network progress flags + END`. This is what makes late / reloaded machines consistent.
- Never in a vanilla Nightlord event: Is Player Count, Shoot Bullet, Clear SpEffect, Set Character Event Target on a player,
  invincibility / SpEffects on players during a phase switch. **REFINES** Shoot Bullet: a sync-off `Shoot Bullet` with the BOSS as
  owner, fired by each machine for its own player, works in co-op [game-MP]; never fire one for another player's slot.
- Big moves: 48 of 59 ultimates are started by the host's AI Lua, payload in TAE, state on the boss. EMEVD that needs the boss to
  act puts a REQUEST SpEffect on it ("SKIP 1 IF the boss already has the marker", re-issued after 10 s) and waits for the TAE
  "done" marker (Gnoster fusion pattern).
- Marks on players: a no-damage homing bullet from the boss animation carries the mark SpEffects (Adel: 508 + a si 622 row,
  45 s, self-expiring; the boss gets a si 621 row the same frame).

## 4. Set pieces: host director + client follower

- **Every machine runs the whole EMEVD of the map** (Seamless Co-op included): a set piece written for solo runs N times, once per
  machine, each on its own clock [data; game-MP]. Design every set piece as "host director + client follower".
- **Never move or turn the boss with per-machine EMEVD commands** (Force Animation / Rotate / Short Warp / AI off on every
  machine, with per-machine area tests, own-position choices, own-clock time-outs, fallback warps). Copies drift apart; seen as
  a client teleport mid-air, a different breath point on clients, a teleport at landing [game-MP]. At the end of one opening set
  piece every client re-landed the boss and switched its AI back on ~1.5 s after the host: top suspect for a freeze and crash that
  happened only on clients [data; link to the crash inferred].
- Lockstep (all machines identical commands on the same timeline, zero per-machine choices) worked for an opener and a phase
  switch [game-MP] but is fragile: a ~1 m start offset changed a per-machine pick and desynced the same script in a later session.
- Host-only boss commands while client copies keep their AI OFF froze the clients [game-MP].
- **Pattern to use (vanilla way)**: start big moves from the host AI (HP-gated act, weight 9999, request SpEffect), payload in TAE,
  so the engine replicates them [data]. If an EMEVD set piece is unavoidable: run it with `Set Network Sync State(0)`; put every
  command that changes the boss (warp, gravity, Force Animation, Rotate, animation reset, AI on / off, re-plan, enable / disable,
  scripted knock-down) behind `SKIP 1 IF client`; clients keep their AI ON and never command the boss; the host makes every choice
  and publishes it as one-hot network flags (take-off point, branch, "done"); clients follow the timeline only for their own
  presentation, their own-player effects and their own collision switches, with a ~20 s safety time-out; single player = the host
  path. Evidence: [sim] client copy = host within 0.01 m; [game-MP] copies within ~1 m / ~1 deg at a breath start, host-only
  forced knock-downs seen on clients ~0.48 s later without double topples. **CORRECTS** the old "game-MP pending".
- Keep on every machine only what is local: screen effects, HUD, the own player's state, own event bullets, collision switches
  (`2011[1]`, sync off), prop animations (a siege-weapon prop animated on every machine while only the host applied its‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ damage and
  knock-down) [data, game].
- Choices that depend on a player (attack direction, mark target): the host decides from the boss's target and publishes a slot
  flag (section 5).
- Client time-outs take the SAFE branch: release a damaging finale only on the host's "done" flag; on a time-out spare instead
  of nuke. A client must never end a shared mechanic on its own HP or own observation [game-MP report, fix sim-only].

### 4a. One judge

- Do not let each machine decide "sword n is down / ring n breaks / the head broke" from its own HP reading: a client whose copy
  is late or reads 0 shows a different arena [data, sim]. The host (or the solo player) decides and publishes a network flag; every
  machine runs the presentation lines (masks, SpEffects) on that flag; the host re-sends it every few seconds so re-joined clients
  catch up. Wait term for the host: `(condition AND (Player Is In World Type 0 OR Multiplayer State 4)) OR networkFlag`.
- One owner per toggle: each player writes only their own network toggle (e.g. "my ultimate Art is active"); the host counts and
  decides; clients follow (`balance.md` 5, cast bars).

### 4b. End conditions of long set pieces [game-MP: fixed a cast that silently aborted after a player dropped]

- Host-owned set pieces: the host ignores end signals that can arrive from clients; it ends only on its own terms.
- Clear stale flags at the set piece's start.
- Debounce: read end terms over at least 2 frames. A one-frame wrong read of a flag latched the wait and ended the set piece; the
  flags read OFF again right after.
- One breadcrumb flag per end term (which term ended it, where it was) and log them with the DLL: the real cause lay outside the
  event text, so only the breadcrumbs could name it.

### 4c. Per-machine vs host-only (as built and confirmed)

| mechanic | who | evidence |
|---|---|---|
| boss commands of a set piece (warp, gravity, forced clips, AI on / off, re-plan) | host only, clients AI on | [game-MP] |
| lethal breath tick (boss-centred sphere) | each machine for its own player, sync off | [game-MP log] |
| guard-shadow barrier (guarding player blocks a fan) | the guarder's machine (own bullet; others sheltered after it replicates, ~RTT/2 + 1-2 frames) | [code, inferred] |
| part-break decision | host / solo only, network flag; everyone applies the break lines | [code, sim; game-MP plausible] |
| scripted knock-down, siege-weapon damage | host only; clients see the replicated animation ~+0.48 s later | [game-MP log] |
| prop animation (siege weapon) | every machine | [data, game] |
| attack-rate-after-break SpEffect | each machine on its own copy, from network flags | [code] |
| collision switches (`2011[1]`) | every machine, sync off, on every path incl. rebuild | [data] |
| key-item grants in the hub | every machine, own player | [game] |
| summon / helper AI ON | every machine (`isHostSyncChr 0`) | [game-MP] |
| target slot of a player-anchored pattern | host polls and publishes one-hot slot flags | [code fix, sim, game-MP report] |

## 5. Target-slot publishing ("no slot, no shot")

- Rows aimed "through the boss's target" read host-published one-hot slot flags (the host polls `Character Targeted By` every
  0.2 s) and fire from the boss at that slot's player.
- **In co-op, no slot -> no shot.** A fallback "no slot ON -> fire at 20000" fired rows through each client's own player wherever
  he stood, even behind the boss [code fix, sim, game-MP report]. Solo may fall back to 20000.
- The publisher clears the other slots first and sets the new slot ON one frame later (section 2).
- Shared vs per-player cover: a network-shared gate flag (one player closes a shelter gate) protects everyone inside; shelter
  tests are per machine and never protect another player [data]. First co-op test for any per-machine lethal design: a sheltered
  player beside an exposed ally must not be hit.

## 6. Player effects, invincibility, marks

- Never `Set Character Invincibility` on players: a client stayed immune for a whole phase [game-MP]. Use an owner-applied,
  self-expiring SpEffect (full damage cut, ~20-24 s) from a sync-off helper on 20000, plus an OFF watchdog [game-MP].
- Apply effects to the OWN player only, never to remote slot entities with sync on (marks stuck) [game-MP]. SpEffects set on party
  slot aliases 10002-10004 with effectTargetSelf / Friendly 0 did no damage [game].
- Check spCategory before choosing rows (a skill effect shared category 20 with a mark row and displaced it) [data].

## 7. Party size, solo and 4-6 players

- Solo = `Multiplayer State == 4`; with the Seamless Co-op DLL loaded a solo player IS Singleplayer [game; the solo revival token
  appears]. The exe tests a game-mode byte (`[[exe+0x3c078d0]+0xdc] == 1`, EcTestMultiplayState 0x5a5d00), false on host and
  clients under the co-op mod [data, code]. Check the enum before building a fix around it (a co-op "skip bug" suspicion was a
  mis-remembered enum).
- **Never trust `Is Player Count` (EcTestSortieMemberNum) under Seamless Co-op**: it read **2 in a 3-player party** that left
  together, nobody joined late or reconnected (proven by elimination from the host's logs); 2 Arts then broke a cast that needed 3
  [game-MP]. Earlier it read ~0 at a debug entrance and did not drop after a leaver; vanilla Nightlord events never use it. The
  co-op DLL carries RTTI names of exactly 5 of the game's 104 EMEVD test classes (EventFlagState, PlayerNo, SortieMemberNum,
  TeamType, ChrDead) and most likely intercepts their answers [code-strings; inferred]: expect the other four to be fragile too.
- **Count players from per-slot presence**: team types of slots 10002-10007 (present 1 / 2 / 20 / 29 / 77, standing 1 / 2 / 20 / 29
  and HP > 0), published per owner or latched by the host at the start of each mechanic. Keep Is Player Count only as a fallback.
- **4-6 players**: audit every per-player block for slots 4-6 - vanilla and first mod events checked slots 1-3 only (phase-switch
  player warps, target picks for marks / beams, "another player is standing", per-player Art toggles and counters, alive flags of
  personal attacks, a test-mode defeat handler) [data]. Add warp regions for players 4-6 and floor-check every point against
  assets as well as collision (one proposed point was 3 cm inside an asset). Prove 1-3 players byte-identical before / after with
  simulated identity runs (only new local flags and intended tier changes may differ) [sim]. Re-count every SKIP after inserting
  lines (231 SKIP counts changed in one pass). Put the new flags into the logging ini before the first 4-6 player session.
- HP under Seamless Co-op is fixed when a character is ENABLED, for the party at that moment (`balance.md` 2) [game-MP].

## 8. Downed / revive / wipe / late join

- Use the vanilla flows (common 1180 / 1181 / 1182-1184); mirror 7516 into your own "lost" flag; never clear 7500-7599 or the
  revival token on the REAL path [game].
- In co-op, common 1310 kills a downed player outside the play area after 15 s; an in-world own block counts as inside [code].
- Late joiner / reloader re-runs event 0 / 50 (local resets wipe its copies): rebuild heads keyed on network progress flags,
  followers keyed on network GO flags, host refresh running [data; sim]. Replay host decisions (break flags, slot flags) for late
  joiners from the host refresh.
- Every native DLL a mechanic needs must be installed on every machine (route registrations are per machine) [data].
- Lethal per-machine ticks skip the own player when he rides the spirit hawk (state info 603 / SpEffect 99202), is downed (team
  type 77; 102180 = 99 % cut) or has HP <= 0, and END on the fight-end flags [data; sim].

## 9. Backward GOTOs

Never jump backwards in EMEVD (ignored or ends the event [game, dialog probe]; ~2 in ~1,800 vanilla GOTOs). Multiplayer-only
branches with backward jumps died in the first co-op session. Scan every build for backward and missing-label GOTOs.

## 10. Offline host / client simulator: use and limits

Interpreter of the real event lines on host + 1-2 clients with latency 0.1-0.5 s, jitter, lost / late flags, client-copy error
1-3 m / 6 deg, two client-copy models. Uses: solo identity (solo action log byte-identical to the previous build), 1-3 player
identity after a 4-6 player change, negative control (the old build must reproduce the reported bug), scenario sweeps (downed host
/ client at each moment, late or lost decisions, leaver), finding every writer of a flag. Limits: it models the event text, not
the engine, the network or the co-op mod. It missed two real bugs (a mechanic invisible to clients, tiny client damage), and
1,488 leave / drop scenarios gave 0 reproductions of a real co-op failure (the cast abort of 4b) [sim vs game-MP]. **An offline
simulator never clears a co-op bug**: log real sessions on every machine (section 11). Label every fix "offline only" until a
real session confirms it.

## 11. Diagnostics

- Session protocol: every player reports what HIS OWN screen showed, who was host, who was‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ down when; "now" on voice at key
  moments; a numbered per-mechanic checklist (what should happen / "tell me if"); a recording.
- Before a session: identical package on every machine (compare the installer fingerprint), natives on every machine, nobody
  used debug entrances or the debug-panel profile that day (a local debug flag carried into an expedition breaks the fight; the
  debug package is never in the pack).
- Per-machine sync log from a native DLL (10 Hz: time, boss animation id, boss position relative to the arena block origin, yaw,
  HP, local player position + HP + damage taken, chosen flags and SpEffects from an ini list, frame times) plus a compare script
  aligning host and client logs by UTC / measured offset; see `native_dlls.md` [game-MP].
- **Logs from every machine, right after the session**: each machine's log holds only its own player, and rolling logs keep only
  the last launches. Ship a default list of sync flags in the release ini; put new diagnostic pulse flags (e.g. a 0.15 s local
  "mechanic fired here" pulse) inside an already-logged range so release logs carry them without an ini change (an ini change also
  forces the patch to replace the ini). Keep dev-only monitor flags out of the shipped ini [data]. When flags were not logged,
  reconstruct events from forced animations in the host's log (the knock-down id) and from variant ids that prove which flags were
  set [data].
- Cheap probe: generic dialogs with own texts at each state change printing Multiplayer State, host or not, slot team types.
- Crashes: collect Application events 1000 / 1001 / 1002 / 1005, System 41 / 4101 / 6008 / 1001 and display-driver events,
  WER reports, `%LOCALAPPDATA%\CrashDumps`, me3 + mod logs, receipts with a read-only collector (tell players paths may contain
  their user name). A display-driver reset event (System log, source = the GPU driver) seconds before the crash plus a GPU watchdog live dump = GPU
  timeout (TDR); the game is the victim; check for watchdog dumps older than the mod [game-MP]. GPU-hang workflow (DRED, asset
  audit, effect load): `testing.md` 6. Unwind the dump with the local exe before blaming event logic.
- Settlement / teardown crashes on every machine ("everyone black-screened at the settlement"): treat as a budget problem (AI Lua
  heap, characters of always-loaded blocks; `ai_lua.md` 4), not as a bug of the fight [game-MP].

## Unverified

Whether a wait passed on one machine in a sync-on event releases the others; whether a client's event SpEffect / warp / AI switch
on the boss reaches the host; host refresh / late-join design in a real session; Seamless Co-op 4-6 player HP (formula measured
at 2P / 3P only, 4-6 sessions pending); whether the co-op mod's party factor enters NPC part max; whether the host changes when
the host leaves; guard direction of the boss-centred lethal sphere in a real session; whether vanilla Absorb skills erasing
fan rays (`isHitOtherBulletForceEraseB`) is what a co-op reviver experienced; enable-after-host-flag hardening for summons.
