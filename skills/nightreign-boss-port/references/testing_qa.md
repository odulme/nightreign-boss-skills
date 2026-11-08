# Testing and QA for a boss: report states, order of proof, previews, models, installed-state audits, crashes, the tester loop

Tags as in `SKILL.md`. Every stage gate of `boss_pipeline.md` uses this file. Move control in game: `debug_panel.md`; logs, heap
gauge, dumps, DRED, replays, probes: `diagnostics.md`. Dev-entry layering, DEBUG vs REAL scripts, quick-test kits and release
checks: `nightreign-nightlord-replace` `testing.md` and `release_packaging.md`. Visual QA scoring: `nightreign-modding`
`QA_STANDARD.md`.

## 1. Four states, never mixed

"built" -> "installed and read back" -> "the tester saw it work" -> "the tester accepted it". A new in-game counter-example
overrides every earlier PASS. Offline checks are for finding causes; never claim a fix from them. Put an evidence tag on every claim
in a report; mark inferred engine semantics as guesses ("direction value 1 = up [inferred]"); [model] and [sim] are never "fixed".

## 2. Order of proof per feature

1. Offline: builder PASS + independent read-back (only the named members / rows / events / FXR slots changed).
2. Preview renders of the written files (section 3) when looks change; the tester approves them.
3. Dev entry (one new overlay, `boss_pipeline.md` 4) -> the tester plays the changed moves from the debug panel with a 2-minute
   checklist (`debug_panel.md` 7).
4. Destination test (real expedition / field placement) in the shipping configuration (co-op DLL, forced depth, co-loaded mods),
   then a real co-op session for anything multiplayer (logs from every machine).
5. Only then pack ("dev first, then pack": every feature that skipped the dev entry failed in a release).

## 3. Previews before installs [game]

- Render the WRITTEN files: skin the written FLVER with poses decoded from the written NR clips (Havok QS chain rule for
  scale), not the source scene. Fixed sheet: idle, walk, run, turns, each changed attack at its hit‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ frame, flight / specials,
  reactions, stance break, death; one image per display-mask set; capsule pictures (with a coverage number); always in colour
  (a clay render hid wrong textures). Render several frames per clip, not frame 0 only: secondary-motion bugs were invisible on
  frame 0 (`original_model.md` 11).
- For new moves: a short contact sheet or clip per move with the source next to it.
- A static posed model as a map asset is a cheap first in-game look (size, textures) before the character exists.
- Visual QA by an independent agent on a FROZEN, hash-bound version; items not seen in game are never scored as full; the
  tester's eyes win above the agent noise (+-3 points).

## 4. Offline models that reproduced tester reports (build one before guessing)

| model | answers |
|---|---|
| heading model (60 Hz; 224 rates, JT7, NpcParam default, clip root yaw; several target angles + a strafer) | "slides", "tracks where the source does not", heading error at hits and at each shot release |
| clip census (frames, seconds, reference samples, imports) | turning inside long clips, frozen deaths |
| trajectory / trunk-heading tool on installed clips | flights overshooting, root yaw bookkeeping |
| flight / set-piece model from installed regions + clip distances | wrong breath heading, landing too far |
| roll-dodge simulator | "cannot dodge", which trim keeps the source shape |
| footprint audit (melee capsule area x time) | frame drops |
| AI harness (real Lua, mocks, cells, dynamic runs) | move frequencies, unbound keys, starving gates |
| completeness audit (source chain vs clip vs AI window) | "only half plays", wrong directional member |
| chain verifier (TAE -> rows -> FX / sound ids) | missing effect / sound / damage |
| hurtbox coverage check (`physics_hurtboxes.md` 5) | "the head breaks too slowly" |
| FK dummies, breath joint, placement sweep, fan blocking, shadow, FX fill / repetition, screen coverage, brightness, collision ray casts, contact simulation, log replay (`diagnostics.md` 5, 8) | streams missing in front, misplaced mines, fans dying on bumps, short characters untouched, view blocked, invisible walls |
| break-timing and DPS models (`params_balance.md` 8, 10) | breaks too early / late per depth and party, pacing vs vanilla |

Every builder: deterministic, inputs as arguments, writes only changed files, ends with PASS / FAIL, and keeps negative
controls (the previous bad file must still FAIL the new check). Never edit a verifier until it turns green; add assertions for
the new contract instead. Vanilla censuses settle undecoded semantics cheaply; confirm with one in-game look (`diagnostics.md` 7).

## 5. Audit the installed state [game]

- When the tester says "nothing changed": dump every event, MSB, TAE, graph, param from the files the entry really loads; the
  me3 log's `override=` lines prove which copy was served (no line = never requested). Check that the debug package still sits
  last and was rebuilt on the current fight script / AI binder (`debug_panel.md` 5).
- Compare regulation by decrypted content (a new IV each write); compare behaviour graphs by "undo the additions == original".
- When two near-identical sequences differ in game, make the broken one byte-identical to the working one first, then
  compare plain sizes / counts (the 892 vs 1,359 root samples were visible in an audit and dismissed as implausible).
- After three "only remaining difference" conclusions fail in a row, stop eliminating on paper: ask for a recording; prefer
  mechanisms already proven in game over ones whose semantics are not understood. After an in-game failure do not stack a new paper
  cause on a piece never seen to work (an FX never seen, a helper assumed to have moved): rebuild from pieces already proven in this
  port and verify against a replay of the tester's logged positions [game].
- When a sanity guard fails every time, find out what it tests before removing it as "the bug" (a helper-distance guard was right:
  the helper never moved) [game].
- Do not replay old generators blindly (they bring back old states); copy the previous stage, patch only what changes,
  verify, install. A generator must first rebuild the previous version byte-identically before applying edits.

## 6. Crashes and freezes

- Crash: Windows Application event 1001 gives the module offset. Bisect with packages that swap ONE member each (stick-figure
  FLVER, no physics, donor anibnd, donor chrbnd) on the same base [game]. Before attributing a crash, look for the same signature in
  dumps from before the mod existed (`diagnostics.md` 3).

| offset / signature (NR 1.3.3.0) | cause |
|---|---|
| 0x1A11B59 | HKLib hkx without hkRelArray PTCH entries |
| 0x182AC83 | hkx without THSH type hashes (TYPE transplant) |
| 0x6F3EEA8 (load) / 0x6F3EED7 (player walks near) | FLVER node order / second skeleton table not depth-first |
| 0x22ca5c0 in Lua `sweeplist` half a second after an arena load | AI heap fragmented by source-text Lua inside one expedition (`ai_port.md` 6; corrected: not "after a long run" - the heap is rebuilt per world) |
| DL_PANIC "DCManager is not finalized." writing to 0 at exe+0x214e298 during static destructors (+ a second WER report ~10 s later from exe+0x81d7c5), everyone at the end-of-expedition settlement | unhandled Lua out-of-memory at the map-move teardown -> `exit(1)`: heap budget / always-loaded mod characters (`ai_port.md` 6) |
| 0x175582b at a hitch / cutscene start | ported cloth operator order |
| "Memory allocation request overflow" on approach | hks patched without updating its debug line count |
| freeze at the first spawn of one effect | FXR structure (count / offset / link) edit (`fx_sound.md` 1) |
| boot crash "network message param missing" | regulation decompressed size over the limit (79,293,432 B crashed at boot; stay below 78,838,728 B, a size known to boot; strip row names, measure after every merge) |

- Freeze then crash on ONE player's machine: collect read-only (Application 1000 / 1001 / 1002 / 1005, System 41 / 4101 / 6008 +
  display-driver events, WER reports, crash dumps, live kernel reports, me3 + mod logs, profiles). A display-driver reset event
  seconds before the crash + a GPU watchdog live dump = GPU‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ timeout (TDR); the game then writes to a null buffer in render code
  and is the victim. Unwind the dump with the LOCAL exe of the same build; check for watchdog dumps older than the mod; rule out
  content differences between builds. Slimming textures did not prevent it; the trigger was dense blended particle / trail load and
  thinning emitters reduced reports (`fx_sound.md` 12); get a DRED report from a DLL and audit converted assets against vanilla
  (`diagnostics.md` 4) [game-MP]. Tell players that collected paths may contain their user name.
- Launching while a previous game process is still alive makes the me3 attach fail; a 0-thread / 0-handle game process is a
  kernel-held zombie (reboot); "game is running" checks must ignore 0-thread processes [game].
- Check the test machine before blaming the mod for an FPS drop (a drop after half HP coincided with unrelated CPU-bound processes
  started on the same machine) [game].

## 7. The tester loop

Full loop (questions, reports, decisions, labels): `boss_pipeline.md` 5. The essentials:

- **Ask before analysing any log**: trainer / damage multiplier / HP lock on?; character, level, weapon, relics since the last test;
  profile (dev entry vs pack with the co-op DLL and a forced depth); solo or co-op, host or client; what they aimed at; the exact spot
  (screenshot + debug-panel history); hit or not when the log cannot tell. An external damage multiplier scales HP damage but not part
  damage: a run with one on is useless for break calibration [game].
- Give stable catalogue ids and plain-language candidate descriptions; ask which motion plays which role.
- Ask early for the exact visible sequence ("same every time? independent of the gate / target?"); ask what is SEEN before
  guessing a mechanism; ask what each element of a screenshot is before interpreting it (an empty inventory cell plus a placeholder
  icon seen through a menu was misread as "our item listed but broken"); ask for a source reference picture next to a screenshot for
  look problems; after two failed paper explanations ask for a recording.
- "Stray X in move Y" may come from other moves that share Y's FX: ask which move, which side, and whether it appears together with
  the move's own effect [game].
- The tester often knows the source game and always knows NR better than the files: present inferred mechanics as guesses; accept
  fidelity calls (source lines instead of prompts, source-size circles, uninterruptible set pieces) and never argue them with inferred
  mechanics. Check object lifetimes in code before advising players.
- Fidelity rules are the tester's: shortcuts (teleports in set pieces, fireballs instead of a breath, lava instead of fire,
  slow motion instead of a wind-up) were rejected; when the source data does not say something, say so and propose.
- Present options with numbers, build the default, keep alternatives one flag away, record the decision; ask balance targets as
  HP-bar fractions; solve linear‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ targets on the real curve and say so.
- One install round per batch (several overlays, one change each, `boss_pipeline.md` 4): say which overlays are active, what to look at per move (2-minute list), what is unproven,
  how to roll back; the tester's "pass" for a batch is the pack trigger.

Per-round character checklist: visible / lockable / hittable everywhere; each changed move once from the panel (complete, heading,
hit timing vs visual, hit size, dodge, short characters, cover); effects and sounds of those moves; reactions and knock-downs; death and
dissolve; part-break visuals; bar name in every language; frame rate during the heaviest move; nothing left on the player afterwards.

## 8. Multi-agent rules for a boss

One owner per shared file (anibnd, chrbnd, texbnds, behbnd, regulation, AI binder, bank, FX binder); others send requests
(row / FX / sound / event json). Several builders may run in parallel when each runs in cells mode (asserts and edits only its own
cells / slots / events at their exact old values, `boss_pipeline.md` 4). Agents work in their own folders, copy tools instead of running
them in read-only projects, save scripts and data early (they can die with the session or be unable to write reports - the coordinator
saves their hand-back), never install, never launch the game. Heavy steps share one lock file (no free-RAM threshold; a lock older than
60 min may be taken over, so long steps refresh it every 5 min); report every deletion an agent made.
