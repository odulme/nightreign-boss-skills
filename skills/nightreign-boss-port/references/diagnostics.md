# Diagnostics tooling: sync log, heap gauge, dumps, GPU reports, offline replay, probes

Tags as in `SKILL.md`. Exe offsets: NR 1.3.3.0 (PE TimeDateStamp 0x69e0dc2a) - every DLL re-checks them at start and fails closed
(`nightreign-nightlord-replace` `native_dlls.md`). The move-control debug panel has its own file: `debug_panel.md`. Plan the fields
in S0, build them in S3 (`boss_pipeline.md`).

## 1. Sync-log DLL (read-only, may ship)

- Per machine, 10 Hz plus one line per change: UTC + monotonic time; boss animation id, position (relative to the arena block origin,
  comparable across machines despite the floating origin), yaw, HP; local player position; flag lines for a configurable flag list;
  SpEffects of a configurable list; frame times (max / mean present interval per 100 ms); "HP lost without a hit: N" lines.
- **Must-have fields that were missing and cost rounds**: local player HP and damage taken ("was I hit?" stayed undecidable for three
  rounds of one move); part records base / max / current (CSEventPartsDamageCtrl `[[exe+0x3c117c8]+0x20]`, base / max / current at
  +0 / +4 / +8 - proposed, unbuilt); every mod flag of the fight incl. per-machine worker / lock flags.
- **Yaw convention**: prove it before using any log - forward bearing = logged yaw + 180 on one build, found statistically on 111
  attack starts (median bearing to the target 28 vs 152 deg) [data]. The heading model (TAE 224 rate per real second, 0 under JT7,
  x clip speed) then matched the log within 0-2 deg.
- **Size**: log only real changes; rolling or per-fight files. A fixed 20 MB cap filled in 8.5 minutes of helper spam and‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ lost the crash
  moment [game-MP]. A "lost without a hit" counter capped at 50 entries stopped exactly when needed: read residual HP steps instead.
- **Ini**: usually a kept user file - a key missing from an old, user-edited ini counts as ON. Ship a default list of sync flags in the
  release ini; put new diagnostic pulse flags (e.g. a 0.15 s local "mechanic fired here" pulse) inside an already-logged range so a
  release logs them without an ini change (an ini change also forces the patch to replace the ini). Keep dev-only monitor flags out of
  the shipped ini.
- **Co-op**: collect every machine's log right after the session (each holds only its own player; rolling logs keep only the last
  launches); align by UTC or by the measured offset on replicated AI attacks (client +0.34-0.48 s on one pack, ~8.6 s clock offset on
  another); compare sequences.
- A DLL damage correction in the hit hook is wrong in co-op (remote full hit packets bypass the private-vtable slot): keep hit hooks
  read-only (log the damage category `[dmg+0x3c]`, hit capsule group `[dmg+0x264]`, `[dmg+0x29c]`) [code].

## 2. AI-heap gauge (read-only, may ship)

- `[exe+0x3c2da68]` -> arena object exe+0x39d7d98 (+0x28 free, +0x30 blocks, +0x10 free-size bins; bin n = [2^n, 2^(n+1)) bytes) ->
  log free MiB, block count, highest non-empty bin and **"8k = yes / no" (any bin >= 13 non-empty)** every 5 s and at every block load /
  unload [code, game].
- Validate against the LIVE vtable exe+0x2cb4960 (`HeapAllocator<DLDynamicHeap<...>>`, +0x48 alloc / +0x68 free); the base vtable
  exe+0x2bdcc80 appears only in exit-time dumps - a gauge built on it logged "unexpected vtable" in game. Take signatures from a
  mid-game dump and log the whole pointer chain once.
- Read the numbers as a budget for ONE world: the arena is rebuilt at every map move (`ai_port.md` 6). In-game reference on a
  vanilla-based dev route with only one mod boss: 20 MiB free at world start, ~11 MiB after loads, 9.67 MiB minimum in the fight,
  8 KiB block available throughout [game].
- Do not enlarge the arena with a native patch and do not build a probe that exhausts the heap; validate against a dump's bins.

## 3. Crash dumps (read-only tooling)

- x64 `.pdata` unwinder on the on-disk exe of the same build; per-frame registers with RTTI; function names from assert strings and
  RTTI; a per-dump singleton-slot table; the arena gauge applied to the dump; a HEAP_FAILURE_INFORMATION reader.
- Minidumps hold the exe's static `.data` (enough for arena counters and bins), not Lua heap contents (corrected: "minidumps hold no
  heap" was too strong) [data].
- Before attributing a crash, look for the same signature in dumps from before the mod existed (a quit-time c0000374 in a GameMan
  teardown, 0x6aaaa0, was in 9 dumps including pre-mod ones: base setup) [data].
- When the fault is a DL_PANIC inside atexit / static destructors (e.g. "DCManager is not finalized." writing to address 0 at
  exe+0x214e298, panic routine 0x214e1d0), read further down the stack for the real exit cause (here an unhandled Lua out-of-memory
  -> `exit(1)`; `ai_port.md` 6) [code].

## 4. GPU hangs (TDR)

- Separate overload from a fault: one tester's machine, ~1 in 3 fight openers, 0 crashes in 100+ other fights, steady 60 fps (max frame
  39 ms) up to the hang, hang within one frame -> a boss-specific trigger on that‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ machine, not overload [game-MP].
- **D3D12 DRED from a DLL**: auto-breadcrumbs + page-fault reporting, write the report on device removal. Result on one case:
  DXGI_ERROR_DEVICE_HUNG, no page fault (no out-of-bounds / freed resource), GPU stopped inside a long run of DrawIndexedInstanced in an
  unnamed command list after the opaque lists and before post-process / HUD - the effect / transparent pass [inferred], 9 s into the
  densest set piece. Next step if it recurs: label draws (draw ids as DRED contexts) and log VRAM per second.
- **Audit converted assets against vanilla before guessing**: index < vertex count per mesh; weighted bone index < bone count; buffer
  length = stride x count; no NaN / Inf in vertices, bones, dummies, boxes, FXR values or gparam; texture data matches declared mips /
  format / size; every reference resolves; FXR field layouts and action types are ones vanilla uses. Two invisible deviations found and
  removed: invisible helper FLVERs with 81 meshes of 0 indices (37 MB of never-drawn vertex data; vanilla invisible helpers have 0
  meshes) and HUD placements hidden with an all-zero matrix (vanilla hides with alpha 0) [data]; they did not stop the hang [game-MP].
- What reduced reports: thinning the densest blended emitter while keeping its look (spawn-distance thresholds, maxConcurrent, spawn
  intervals, 16 bytes in total; -74 % effect load per laser; sparkle max 1000 -> 40 in a sibling port) [game-MP, small sample]. Budget
  rules: `fx_sound.md` 12.
- Ship testers a collector script: OS event-log entries for display-driver resets and app crashes, WER folders and kernel live-dump
  names, the mod's logs, a fixed list of running overlay / capture tools - never personal files; tell players paths may contain their
  user name. Tester-side factors to ask about: memory overclock profiles, overlays / capture tools, driver debug options, virtual display
  adapters. Heap-corruption crashes with display-driver frames on the stack belong to the same investigation.

## 5. Offline replay of logs

- Replay logged player and boss positions against the hit model / damage-area event lines on a 1 m grid to locate damage-area bugs; it
  found a sector anchored at a hover point, a helper parked mid-court and a reviver's geometry [model].
- Align host and client logs by UTC; replicated attacks give the offset.
- When flags were not logged, reconstruct breaks from forced animations in the host's log (the knock-down id) and from variant ids
  (fire-set offsets) that prove which flags were set [data].

## 6. Log-only probes (part HP and other invisible state)

- Host / solo-only events wait for fight start + a few seconds (records must exist); on `IF NPC Part HP(part, T, <)` each applies a
  one-shot boss SpEffect with a tiny distinctive `changeHpPoint`, which the damage DLL logs as "HP lost without a hit: N".
- Choose amounts whose singles, pair sums and sums with known damage-over-time ticks are distinct (3 / 5 / 7 / 11 / 17 works; 3 / 7 / 13
  / 19 / 29 collides: 3 + 29 = 13 + 19); two probes in one frame log as one sum.
- Thresholds on the part (90 / 75 / 50 / 25 %) AND on any carrier record (max - 2000) separate competing hypotheses ("bullet multiplier
  working" / "not a bullet" / "carrier‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ absorbs"). Thresholds are absolute: valid only for the tested depth / party.
- Build behind `--probe` / `--release`; never ship or pin a probe (`boss_pipeline.md` 4).

## 7. Probe design and vanilla censuses

- Every outcome of a probe must map to a cause; include a vanilla control; banners at the probe event's start and end; unique display
  names per probe entry (two test items sharing a name produced a false "large ids work" conclusion and three extra rounds); report
  popup and listing (or spawn and visibility) separately [game].
- A visible dev marker on an invisible damage volume separates "never spawns" from "spawns, FX invisible"; make it distinct, ask about it
  explicitly, switch it off in the release build and diff both modes (the switch changed 2 cells per row, not 1) [game, data].
- Vanilla censuses settle undecoded semantics cheaply (event durations, events shorter than their interval, `isEndlessHit` share,
  LC-5 parents, warp dummies in 199 scripts, stationary growing bullets, player Absorb rows, emitter up-axis statistics); confirm the
  conclusion with one in-game look [data].

## 8. Models and renders as evidence

Each of these reproduced a tester report before the fix (details in the topic files):

| model / render | answers |
|---|---|
| FK of dummies over time | "staircases" of bullets, lanes 43 m up (dummy bound to the hip; `skeleton_model.md` 6) |
| source breath-joint FK vs the port's dummy | stream floor points off by metres (`attacks_hits.md` 4.1) |
| placement sweep (boss every 3 m, 16 facings, targets 6 / 12 / 24 m x 8 bearings, both collision states) | mines on walls / terraces |
| fan blocking (court grid 4 m x 12 headings x 17 rays) | share stopped by low bumps vs tall geometry |
| shadow model (blocker / barrier, 1-6 m behind, body tops 1.8 / 1.3 / 1.0 m, 30 and 60 fps) | cover and short-character hits |
| FX fill / density / repetition model | "looping", "mouth stronger than the far end" |
| screen-coverage model (camera 1.8 m high at 3 / 8 / 15 m looking at the boss 12 m behind the effect, 16:9, vertical FOV 50 deg, ground hides sprites; "cover" = screen share at >= 50 % opacity; "boss hidden" = share of a 14 x 9 m silhouette at >= 50 % and its duration; a disc model overstates opacity) | "cannot see the boss" |
| brightness model (texture x colours x rgbMul, coverage clamp, bloom energy, tone curve at exposures 0.5 / 1 / 2 - ratios only) | "too bright" without visible change after colour edits |
| collision ray casts over EVERY triangle incl. vertical faces and all hit filters, with the fight's Activate Hit state at that moment | lanes dying mid-air on invisible shells (a floor-only grid of one filter claimed 0 stops where 45 % died) |
| contact simulation (posed prop vertices vs hurt capsules on a 1 m grid x 24 yaws + logged root samples) | a set-piece trigger box blind to yaw |
| staged-render of the WRITTEN files on several frames per clip | secondary-motion bugs invisible on frame 0 (`original_model.md` 11) |

A model or render is [model]: it finds the cause and predicts; only the tester's in-game look closes the gate.
