# Native DLL extras (optional): damage numbers, custom ride routes, co-op sync log, heap gauge, GPU reports, debug bridge

Only for things data files cannot do. Offsets / classes found on NR 1.3.3.0 (TimeDateStamp 0x69e0dc2a); every DLL must re-check
them at start. Agents build and test DLLs offline; the tester runs the game. Plan the diagnostics with the boss (stage S0 / S3 of
`nightreign-boss-port/references/boss_pipeline.md`), not after the first bug: missing log fields cost whole test rounds.

## Rules that every shipped DLL followed [game]

- Gate on the game build (PE TimeDateStamp + SizeOfImage) AND on code signatures of every function / vtable slot it relies on;
  on any mismatch log it and do nothing (fail closed). No byte of `nightreign.exe` is patched.
- Prefer a private vtable copy on ONE object you own (your boss's module, your block's resource object) over inline hooks:
  nothing else in the game changes, and foreign inline hooks of other mods on verified function starts can be tolerated (log
  their names); a replaced verified vtable slot disables the DLL.
- A `<dll>.off` file next to it disables it; a `.ini` re-read live for tunables; a `.log` rewritten at each start with: build
  check‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ result, signature count, attach facts (which object, boss name, HP at attach - doubles as proof that the HP scaling
  applied), and a size cap.
- The ini is usually a kept user file: a key missing from an old, user-edited ini must default to ON [game-MP].
- Take signatures from a mid-game dump and log the whole pointer chain once: a gauge built against exit-time dumps expected
  the wrong vtable and logged "unexpected vtable" in its first run [code, game].
- Build without `/DEBUG` (no PDB path), scan strings before shipping (`scripts/dll_strings.py`), ship only the tested binary (a
  rebuild without `/Brepro` changes the hash: put back the binary proven in game).
- Load order in a pack profile: `load_after` the pack's own loader DLL; every co-op player needs every DLL a mechanic needs.

## Damage numbers at the hit point (per hit, own hits)

- [code] The HUD's own damage number is an accumulated sum (cleared 1.5 s after the last hit, includes other players' damage,
  anchored to the bar): it cannot give per-hit, per-position numbers.
- Capture [code, game]: private vtable copy on the boss's `CSEnemyDamageModule`, slot 7 = hit handler (this = victim's module,
  rdx = attacker character, r8 = damage struct: +0x280 HP damage of this hit, +0x1f0 hit position, +0x3c damage category =
  BehaviorParam refType 0 attack / 1 bullet / 2 SpEffect, +0x264 hit capsule group, +0x29c); slot 1 = destructor. It fires only
  on the machine that owns the attack -> each player sees their own hits (and their summons' if computed locally).
- **Use the hook read-only.** Remote full hit packets go 0x51f040 -> ApplyDamage directly and never pass the private slot 7, so a
  damage CORRECTION in the hook would apply on one machine only: wrong in co-op [code].
- Draw [game]: own D3D12 overlay by wrapping the dxgi swap-chain vtable slots 8 / 22 (Present / Present1); numbers pinned in
  world space at the hit point; camera matrix auto-detected with ini overrides; tested with OBS recording.
- Filters that worked: HP lost without a hit (poison etc.) not shown; hits on a dead target not shown; size in percent of the
  screen height (ini). A global "all enemies" switch = one pointer in the game's own vtable: built, never run in game.
- "HP lost without a hit: N" lines double as a probe channel (log-only part-HP probes, `testing.md` 7); the DLL stopped logging
  them after 50 entries - read residual HP steps from the sync log.

## Custom ride routes (e.g. a vanilla spirit-hawk ride to your arena)

- A vanilla ride on a custom route needs a native DLL that registers the route in the game's own manager per machine [data]; the
  route DLL swapped‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the vtable of the arena block's WorldBlockRes object (4 wrapped virtuals) after the checks above [game].
- Log a block table (load / unload / position per block) in the same DLL: it diagnosed block placement and early releases
  (`fight_script.md` 3).

## Co-op sync log [game-MP: used to settle several co-op bugs]

- Per machine, 10 Hz: UTC + monotonic time, boss animation id (time-act module's animation ring), boss position relative to the
  arena block origin (comparable across machines despite the floating origin), yaw / quaternion, HP; local player position; a line
  per animation change; ini switch; size cap with rotation. A compare script aligns host and client logs by UTC (or by the
  measured offset: ~8.6 s between two machines' clocks in one session; ~0.34-0.48 s client lag on replicated attacks).
- **Log from day one** (each missing field cost rounds): local player HP and damage taken (without it "was I hit?" stayed
  undecidable for three rounds of one move); every mod flag of the fight incl. per-machine worker / lock flags (ini list) and
  chosen SpEffects; enable state per entity; frame times (max / mean present interval per 100 ms); part records
  (CSEventPartsDamageCtrl `[[exe+0x3c117c8]+0x20]`, base / max / current at +0 / +4 / +8 - proposed, unbuilt; part HP was then
  inferred for two rounds); the AI-heap gauge below.
- Check the yaw convention of any log statistically before using it: the forward bearing was logged yaw + 180 (on 111 attack
  starts the median bearing to the target was 28 deg vs 152 deg) [data]. A heading model (TAE 224 rate per real second, 0 under
  JT7, x clip speed) then matched the log within 0-2 deg.
- **Cap trap**: log only real changes and use rolling or per-fight files; a fixed 20 MB cap was filled by helper spam in 8.5
  minutes, so the crash moment was lost [game-MP].
- Release ini: a default list of sync flags; new diagnostic pulse flags inside an already-logged range; dev-only monitor flags
  only in the dev ini (`coop.md` 11).

## AI-heap gauge (read-only) [code, game]

`[exe+0x3c2da68]` -> arena object exe+0x39d7d98 (+0x28 free, +0x30 blocks, +0x10 bins) -> log free MiB, block count, highest
non-empty bin and "8k = yes / no" (any bin >= 13 non-empty) every 5 s and at every block load / unload (ini `ai_heap_gauge = 1`).
The live vtable is exe+0x2cb4960 (`HeapAllocator<DLDynamicHeap<...>>`, +0x48 alloc / +0x68 free); the base vtable exe+0x2bdcc80
appears only in exit-time dumps. Also log "ai manager deleted / created" at map moves (`ai_lua.md` 4).

## GPU hang reports (D3D12 DRED) [game-MP]

- Turn on DRED auto-breadcrumbs and page-fault reporting from a DLL, and write the report when the device is removed. One result:
  DXGI_ERROR_DEVICE_HUNG, no page fault (so no out-of-bounds or freed-resource access); the GPU stopped inside a long run of
  DrawIndexedInstanced in an unnamed‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ command list, after the opaque lists and before post-process / HUD - the effect / transparent
  pass [inferred] - 9 s into the fight's densest set piece.
- Next steps when it recurs: label draws (draw ids as DRED contexts) and log VRAM per second. Workflow: `testing.md` 6.

## Dev-only debug panel bridge (never shipped)

A window app <-> dev-only DLL bridge that writes only its own event flags, plus dev-only fight-script events and a dev AI binder
with override wrappers: play any AI move by id, loop it, AI on / off, face / approach, HP lock. Described in
`nightreign-boss-port/references/debug_panel.md`. Release rule: **the debug package and its DLL never ship; the pinning tool
refuses a profile or pin list that names them** (`release_packaging.md` 8).

## Crash collector for players (read-only)

A PowerShell 5.1 script + .cmd that zips event-log crash / hang / display-driver entries, WER reports and kernel live-dump names,
minidumps, me3 + mod logs, profiles, install receipts and a fixed list of running overlay / capture tools to the Desktop; finds the
me3 folder or accepts a dragged folder; tells the player that paths may contain their user name; collects no personal files;
writes nothing else.
