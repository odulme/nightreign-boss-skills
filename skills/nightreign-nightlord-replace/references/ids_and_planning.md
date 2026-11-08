# Planning, ids and coordination

Evidence tags used in every file of this skill: **[code]** static reverse engineering of `nightreign.exe`, **[data]** read from
game / mod files, **[game]** confirmed in game by the tester, **[game-MP]** confirmed in a real multi-machine session,
**[sim]** offline simulator only, **[model]** offline geometric / particle / damage model, **[inferred]** reasoning only.
Markers: **CORRECTS** = replaces an older statement of this skill; **REFINES** = the older statement was right but incomplete.
Exe facts were found on NR 1.3.3.0 (PE TimeDateStamp 0x69e0dc2a, SizeOfImage 0x7c5d600 = 130,405,888 B) with regulation
10350000; re-verify every offset after a game patch. Planning is stage S0 of `nightreign-boss-port/references/boss_pipeline.md`.

## 1. Decisions to take before the first file

| decision | options | consequence |
|---|---|---|
| Source release status (always first) | web-verified as released and on sale / unreleased or unconfirmable | released: continue; otherwise refuse the port and stop (`SKILL.md` Step 0); a boss from the user's own original assets needs no check |
| Where the fight lives | **in-arena**: inside the target's vanilla arena block (e.g. m19_00, taking a vanilla Nightlord's place) / **own block**: a new map block (e.g. `m19_10_00_00`) entered in-world from the hub | in-arena: must keep the vanilla boss of every other map variation working, can use vanilla 90075900 / 7511, but its characters and AI scripts load in EVERY expedition that targets the block (AI heap cost for all fights, `ai_lua.md` 4); own block: needs a hub anchor, no own flag storage, must never raise 7511 (see `fight_script.md`) |
| Donor behaviour graph | humanoid (c2130 Morgott) / quadruped winged (c4510 Ancient Dragon) / other | fixes which animation slots exist (`character_port.md` section 4) |
| Switch protocol | one-way latch (only one mod item exists) / "last crush wins" (several mod bosses) | `item_switch.md` |
| Deep Night policy | scale like a Nightlord (ChaosMatchingCorrectParam 7767) / exempt (0) | `balance.md`; both have shipped, ask |
| Release shape | standalone package / third layer inside a mod pack profile | pack = three-way merge of shared files (`release_packaging.md`) |
| Diagnostics plan | written before the first attack: sync-log fields (boss animation / position / yaw, local player position + HP + damage taken, every mod flag incl. per-machine worker / lock flags, part records, AI-heap gauge), flag lists, the dev-only debug panel | missing fields cost whole rounds ("was I hit?" undecidable for three rounds) (`native_dlls.md`) |
| Shipping configuration | the co-op DLL, forced Deep Night depth, co-loaded mods the players will really use | calibrate balance in it at least once; dev entries are solo depth 0 (`balance.md` 2) |
| Fidelity rules | what "source-faithful" means for each mechanism (real lethal hit vs % loss, cover rules, source NPC lines vs prompts) | survey the source mechanism early; present "source does X, we can do A / B / C" with numbers |

## 2. Id bands (pick once, register, scan)

Pick a character id `c<chr>` that is absent from the game's archive dictionary AND from every other mod you may be co-loaded
with (c7580 is vanilla Heolstor; mods like to take the free ids right after the vanilla Nightlords, so scan every co-loaded mod). Derive every band from it so
collisions are obvious:

| kind | band (example for a placeholder chr 9876) | note |
|---|---|---|
| NpcParam / NpcThinkParam | `<chr>0000..` (98760000, 98760010, phase-2 / helpers 98770000) | clone the replaced Nightlord's row first |
| Lua battle goal | `<chr>00` -> `script/<chr>00_battle.luabnd.dcx` | NpcThinkParam.battleGoalID |
| AtkParam_Npc, Bullet, SpEffect | `<chr>000..<chr>999` (7 digits) | private rows only |
| BehaviorParam | 200000000 + behaviorVariationId x 1000 + judgeId | judge convention `ai_lua.md` |
| FXR | `<chr>xx` (6 digits) | binder layout rule `character_port.md` 10 |
| sound | bank `sd/cs_c<chr>.bnk`, events `play_c<chr>xxxxx` | |
| NpcName | `90<chr>000` style (vanilla 9075x0000) | `msg/<lang>/item_dlc01.msgbnd.dcx` NpcName.fmg, 4 languages |
| goods / icon | goods `<chr>00`, icon `<chr>` | `item_switch.md` |
| shop row | a free row in 2000-2999 (Spirit Tree merchant range) | stock flag in a free 90xxx range |
| map script events / flags / entities | a hundred-block of an existing flag block (see 3) | register per kind |
| key items (permanent buffs) | the vanilla key-item band right after the DLC items (goods 451xx, buffs 15x / 16x, SpEffects 98xx, texts 100010xx) | large ids pop up but never list (`fight_script.md` 11); re-check after game updates |
| navmesh NameIDs | area x 2,560,000 + block x 25,600 + index (bit 31 on the o set) | a cloned block keeps the source block's ids: fix them (`nightreign-map-port` collision-traversal.md 6) |
| debug / probe / quick-test ids | own sub-bands, registered like the rest | never equal to an event id or a new guard flag |

## 3. Event flags: storage rule [code]

- 8-digit flag `AABB S xxx`: group = id / 1000. It has storage only if map `mAA_BB` is listed in
  `event/eventflag/LegacyMap.eventflagalloclist` (vanilla: m10_00, m11_00, m12_00, m16_00, m16_10, m16_11, m18_00, m19_00) AND
  S is in {0,1,2,3,4,5,7,8,9}. **S = 6 never has storage**: reads are always OFF, writes are dropped, no error, no log.
- A NEW map block is not in the alloc list, so `<its prefix>Sxxx` flags have no storage at all. Keep the flags of an own block
  inside an existing block's range (e.g. m19_00's). Adding an alloc-list line was‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ never tried (shared file, not recommended).
- Storage classes (matter in co-op): {0,1,7,8,9} world class (on a guest the block is a session copy filled from the host),
  {2,3,5} temporary (3 = session block not transferred), {4} local. **Keep the digit / class of an id when renumbering.**
- An event whose id is > 299 sets flag (event id + slot) ON when it ends or restarts [code]. So event ids and plain flags must
  never share numbers, and multi-slot events need a gap after them [game: a start event collided with an AI flag].
- Flags of the hub (m12_00, 12009xxx) and the Roundtable (m10_00, 10009xxx) are readable from the arena scripts [game].
- As found on NR 1.3.3.0 for m19_00: 19001000-19001999 world class and unused by vanilla [code+data]; 19003xxx / 19005xxx valid
  but another class; 19000 / 19002 / 19004 / 19008 vanilla. Re-scan: other mods may own blocks (one used 19007-19009).
- Batch clears: only your own ranges. Never clear 7500-7599 or vanilla arena flags on the real path [game: clearing them broke
  the vanilla defeat / revive flow].

## 4. Entity ids [game]

- Thousands digit `(id % 10000) / 1000` of 5, 6 or 7 = GROUP id to the engine: commands on such an entity silently do nothing.
- Vanilla convention: 0 enemies, 1 assets, 2 regions / events. Mod entities with digits 1, 3, 4, 9 worked; the hard rule is
  "never 5 / 6 / 7".
- Entity ids and flags are separate lookups (equal numbers do not interact) [code], but keep them distinct anyway: renumbering
  tools work on numbers of all namespaces.

## 5. Checking that an id is free

- "Free" is per KIND (flag, event id, entity / region, param row, FXR, text, sound object) and across EVERY layer that may be
  loaded: vanilla, every pack package, every other mod's release AND its dev stage (a first choice once collided with flags
  only another mod's dev stage used).
- Use a typed scan: every number by kind and layer, EMEVD parameters resolved through the callee's parameter table (common
  events), MSB snapshot, regulation rows, Lua constants. A raw grep finds numbers but not their kind.
- Renumbering: a digit-preserving id map json per kind, applied by one builder to EMEVD, MSB, regulation, FXR, TAE, Lua; guards
  that fail the build (storage rule, class kept, no flag = event id + slot, per-kind collision scan), and an independent
  read-back "only numbers changed". **Test a renumbered script in the dev entry before building anything on it**
  [game: a renumber into digit 6 left the boss active from load with no bar and no music].
- **Id-claim hygiene** [data]: claim every new band in ONE registry before building (bullets, BehaviorParam judges, FX ids,
  SpEffects, flags, navmesh NameIDs, key-item rows, debug / probe ranges). Navmesh NameIDs and a guard flag were found unclaimed at
  pack time; a quick-test kit's event id equalled a new guard flag. Keep the number ranges of one owner only in that‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ owner's
  section of the registry (a checker failed because another note quoted the debug ranges as text). Every new param table / id
  band also needs an entry in the pack merge's allow-list, and every new local flag one in the id checker's allow-list
  (`release_packaging.md` 8).
- A new FXR id must not occur as an int inside any FXR; MSB RegionIDs must be unique within an MSB (vanilla m19: 0 duplicates in
  129 regions) [data].

## 6. Coordination file (one per boss project; read first, keep updated)

```
# <boss> - coordination
## Goal (tester's words, date)            what "done" means; source-game fidelity rules; aggro / arrival rules
## Hard rules (all agents)                write scope; read-only projects; no installs; no game launch; language rules
## Current installed state                entry name, package list, natives, last change
## Id registry                            proposed -> verified -> owner (per kind; date)
## Ownership                              one owner per shared file (regulation, map script, MSB, anibnd, AI binder, bank)
## Decisions log                          append-only: date, task, decision, evidence
```

Also keep a `STATE.md` per line of work (what is installed, what the tester said, what is proven / unproven, next step) and a
short top block in the handover file that supersedes older text.

## 7. Multi-agent rules that paid off

- One owner per shared file; every other agent sends requests (FX / sound / param patch json) to that owner.
- Agents work in their own `work/<task>` and `tools/<task>` folders, copy tools from read-only projects instead of running them
  there, and never install, never touch the live me3 folder (not even a read-only `-ValidateOnly` run unless the tester agreed).
- Background agents can die with the session and may be blocked from writing report files: tell them to save scripts and data
  early in their folder; the coordinator saves their hand-back text.
- A chain step that derives its base from the installed profile must assert the expected last package and slice
  `packages[:-N]`, or it reads already-patched files after the next install.
- Double-check the agent id before sending it a follow-up (a brief once went to the wrong agent).
- For co-op changes that cannot be tested solo, one adversarial review by an agent that did not write them; cap reviews at one
  audit + one re-check, and only for what ships to other people.
- Parallel builders: each runs in cells mode (asserts and edits only its own cells / slots / events at their exact old values,
  refuses otherwise), so outputs stack in any order and replay on release inputs; one builder per change that asserts its own
  base (`release_packaging.md` 8).
- Heavy steps: one shared lock file across agents, refreshed every 5 min, taken over after 60 min; no invented free-RAM threshold
  (a ">= 3 GB free" rule stalled agents and‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ was never the owner's) - at most one heavy step at a time.
- Shared tools: back up every edit next to the original; copy a round's tools into a new per-round folder.

## 8. Talking to the tester (the tester decides and plays)

- Ask early for the exact visible sequence ("same every time? independent of X?") and for a recording after two failed paper
  explanations. Ask what they see before guessing the mechanism ("slides" meant engine rotation without a turn clip).
- Never present a vanilla mechanic inferred from params / menu text as fact; say it is a guess and ask (the tester knows the
  game far better than the files suggest).
- Never assign a source motion to a role (death, knock-down, turn) from its name; verify by data and ask the tester.
- Collect design decisions (balance numbers, item rules, music) as explicit questions; record answers in the decisions log.
- Reports: what changed, what is proven vs unproven, where to look in game, how to roll back. No long PASS lists.
- What to ask before analysing a log or a screenshot, how to present options, batching rounds: `testing.md` 5.
