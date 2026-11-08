# Reactions, knock-down, death, part breaks, phases, helper actors, flight, co-op notes

Tags as in `SKILL.md`. Pipeline stages S4 (reaction clips), S8 (breaks, phases), S10 (co-op) of `boss_pipeline.md`. Fight scripts
(phase controllers, part-break events, victory, credit): `nightreign-nightlord-replace` `fight_script.md`; co-op mechanics: its
`coop.md`.

## 1. Reaction set

- Nightlords have only 7400, 8060 (poise break), 8500 (parried), 8700 (stance break), 9000 + death; big vanilla enemies have no
  small / middle flinch either [data]. Map source reactions onto these; alias what the common hks asks for (e.g. idle 0 <- the
  source's battle idle; side walks <- forward walk; heavy flinch -> 8060) [data].
- Put the generic impact cues back when you rebuild reaction clips: 8060 c999999999, 8500 c999999991, 8700 c999999986 at 0.0 s
  (type 129) [data].
- Stance-break reward lives in the 8700 TAE: AI act point (first JT23), SpEffect 50-53 (+20 % damage taken), SpEffect 30 / 36
  critical window (needs ThrowParam rows + defender animations) + critical-spot FX on dummy 970. Port the meaning, not the number
  (DS3 and NR use different throw conditions). The tester may not want a critical spot: ask [game].
- **Drop the critical rows (SpEffect 36 riposte window + FX 600700 on dummy 970) when no ThrowParam row has the boss's DefChrId**: the
  glow promised a critical that cannot happen [data, game]. Keep SpEffect 50 (+20 % damage taken). Every reaction clip must still send
  the AI's stance-reset marker.
- Recovery guards: marker SpEffects over the whole reaction clip so scripts defer specials (`tae_turning_windows.md` 8).

## 2. Scripted knock-downs (part break, siege weapon, special) [game]

- 8060 / 8700 cannot be forced (no `W_Event` transition): play knock-downs in an EVENT slot whose TAE imports the source's own
  knock-down chain (fall + downed loop x n + get-up), with JT71 + JT51 over the clip, 224 = 0, busy pulses, blend ~0.3 s, a shake
  at the impact, AI windows in the last ~0.8 s; omit the stance-break rows unless wanted.
- **SpEffect 45 over every forced / scripted clip** (refines "JT71 + JT51"): vanilla SpEffect 45 (saReceiveDamageRate 0, effectEndurance
  0, net-synced) as a TAE type-67 row from 0 to the clip end; vanilla precedent c7520 20003 / 20004 / 20010-20012 / 20019 / 30005, c7540
  20000, c7530 30015, every character's 11060 [data]. Without it a scripted knock-down (forced event clip, AI off for a fixed time, JT71 =
  stop stance recovery) drained the stance pool with no recovery, and the engine's `ExecSaBreakDamage` (shared c9997.hks) replaced the clip
  with 8700 or 8060: "fell, snapped upright, fell again‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ with a critical glow" and, after a set-piece knock-down, 12.8 s of idle with the AI
  still off [game-MP symptoms, code]. Put it on every entry of every event-forced chain including every distance / colour variant (100
  entries in one port). Side effect: stance damage during set pieces no longer counts toward the next break.
- **JT24 super armour stops ordinary flinches but NOT stance damage** [inferred from vanilla using SpEffect 45 on top of JT24; code]. A
  stance break inside a set piece corrupts the chain: visuals stop, scripted damage keeps firing on timers, the boss hangs in the air with
  AI and gravity off (up to ~25 s), the end warp hides it [code risk; not observed].
- **Hand the AI back after a forced clip by condition, not a fixed wait**: replace `WAIT fixed` with `fixed OR (>= 1 s elapsed AND idle
  heartbeat present AND busy marker absent)` in one AND group (vanilla 90035012 pattern), keeping the fixed time as the upper bound (frozen
  idle 12.8 s -> 0.3 s) [model]. Never inside set-piece chains (it would hand the AI back mid-chain).
- The downed duration is often an exe value of the source (loop count): choose it with the tester ("too short" was the verdict
  on a 10 s copy of the stance break; the rebuild from the source chain - fall + downed loop x2 + get-up - is ~17 s, no explicit
  verdict yet).
- EMEVD waits tied to the clip length must be updated whenever the clip changes.
- Trigger: a head break interrupts at once, deferred while a set piece runs or the boss is airborne (airborne marker); small
  parts flinch only from idle.

## 3. Death [code, game]

- HP 0 -> A10000 (DeathStartDefault) -> A10001 (DeathIdle, loop). 11010 / 11060 / 11070 are BEING THROWN and 11011 / 11061 /
  11071 thrown-and-killed: an ordinary kill never plays them.
- Source death -> 10000 (JT12 at the impact frame), its last pose held ~1 s -> 10001. Identify the death by measurement (nothing
  starts from its end pose) and ask the tester: labels swapped death and knock-down once [game].
- Before replacing any clip, list the TAE entries that import it: in a c2130-based TAE, A10000 / A10001 imported A11011's clip;
  effects placed on 1101x and a replaced 11011 clip froze every ordinary kill in a pose [game].
- Two dissolve patterns, both worked:
  - Nightlord style: JT50 + JT39 at 0 s, FXR 203 on the dummies 960 (0.2-2.2 s), TAE 193 fade to 0 (e.g. 1.3 -> 2.2 s), FXR 213 on
    the chest dummy, JT95 late, JT12 kept; A10001 holds opacity 0 + the same jump tables. The fade must finish INSIDE A10000
    (A10001 loops and would restart it). Vanilla A10000 has no JT49 (lock-on off is an extra) [game].
  - Ordinary-enemy style (Ancient Dragon): FX 204 on dummies 960, 214 on the chest dummy, JT12 at impact, SpEffect 14895 over
    the clip, no fade [game: real run with normal settlement].
- Optional safety net: an event disables the entity some seconds after death.

## 4. Part breaks (character side)

- Hurtbox part groups + NpcParam part rates (`physics_hurtboxes.md` 4); part-damage path, carriers, multipliers, break durability,
  re-arm, the "missing record reads true" trap and the host-only break decision (`params_balance.md` 7-8); visuals by display-mask swaps
  (`skeleton_model.md` 5); the break reaction is a scripted knock-down (section 2).
- Source break rules are usually damage based and immediate; the source's AI checks of other parts are often wings / limbs.
- NR heroes reach less high than source hunters: lower break HP for high parts (head) was a tester request [game].

## 5. Phase-2 bodies and helper actors

- Phase 2 as a SEPARATE MSB enemy (exact NpcParam clone except masks / name / think rows; vanilla Heolstor pattern) worked;
  host authority (common 90075902) for every body [game, game-MP].
- Same entity with phase SpEffects + animIdOffset sets + BehaviorParam variation per NpcParam row also worked [game].
- Helpers (independent weapons, summons, twins, emitters) [game]:
  - teamType 33 for boss + helpers (7 let them damage each other).
  - Clone the boss model and strip it (only the needed face sets, own skeleton binding, TAE, NpcParam / Think, goal, variation);
    keep a known-safe physics topology and shrink unused capsules to 0.001 m; one meaningful capsule that follows the visible
    part (Root mirrors the blade).
  - Region warp destination type: 0 = asset, 1 = region, 2 = character - type 0 made helpers invisible and once relocated a
    player [game].
  - Grounding: switch map hit ON first, then gravity ON after spawn; never copy an airborne boss's floor (they fell through);
    gravity off for life froze them at spawn height [game].
  - HP per party size (corrected: "from the boss's own multiplayer SpEffects 7867 / 7967" - under Seamless Co-op those never appear on
    the boss, and helpers without a multiPlayCorrection id stay at NpcParam HP [game-MP]): scale helpers yourself from per-slot presence
    with maxHpRate SpEffect copies (`params_balance.md` 3); immortality floors HP at 1, so a script can treat "<= 1 HP" as defeated and fade
    / re-heal on retry [game].
  - **Combat helpers / summons: `isHostSyncChr 0` and AI ON on every machine**, as vanilla does (every Nightlord body, add, helper and
    clone in m19 has 0, e.g. the Everdark Libra clones of common_func 99075466; vanilla sets AI ON on every machine in 99075466,
    90075001, 90075452). With `isHostSyncChr 1` on three summoned swords (rows copied from a boss donor) clients never saw them animate:
    they stood at their warp points and died there, although their HP reached the clients and the boss itself mirrored perfectly
    [data, game-MP]. Fix that shipped: flag 0 on the summon rows and no `SKIP IF WorldType(client)` in front of the AI ON line.
    Optional hardening: enable the client copy only after a host-written NET flag; `Set Network Update Rate` for the summons as vanilla
    does for boss bodies [inferred].
  - Helpers killed with the main boss keep standing after their death clip: disable them, collision‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ off, backread off [game].
  - Carrying one actor on another: short warp to the carrier's dummy every frame, keep hurtboxes on, map hit off [game].
  - Hidden helpers: remove face indices (`skeleton_model.md` 5); helper damage and depth rows: `params_balance.md` 3.

## 6. Flight and set-piece clips

- Flight inside clips: JT51 over the whole clip, JT24 / 27 / 113 over the airborne span, airborne marker SpEffect; horizontal
  travel in the reference frame, height in the body; no JT8 / JT132 in ordinary flight attacks [game]. (Corrected: JT24 does not protect
  a flight or set piece from stance damage - section 2.)
- **AI flight attacks: SpEffect 45 only over the MEASURED airborne span** (tester's choice over "knock it out of the air", which needs
  its own fall / land reaction); measure on posed skeletons, not from JT27 (`animation.md` 3). Wind-ups and landings stay breakable
  [data; game no complaint].
- AI-driven sorties (take-off + air attack + landing in one slot) replicate in co-op like any attack [game].
- Scripted flights switch map collision and gravity by EMEVD: `2004[31]` polarity is 1 = collision ON, 0 = OFF (the EMEDF label
  is wrong; the boss fell through the floor) [game].
- Take-off / travel distances: distance variants (`animation.md` 5); swoops and turn requests aimed at points hundreds of metres
  away; landing points the source engine computes are not in the data: pick them with the tester.
- Rebuild the source chain; prove a set piece's heading offline (flight model from installed regions + clip distances
  reproduced a tester report) before changing the flow [game].

## 7. Co-op facts that concern the character [game-MP unless marked]

- Replicates: animations the host's AI plays, SpEffects the host's events SET on the boss, TAE SpEffects on net-synced rows
  (992 of 993 vanilla Nightlord TAE applications) [data].
- Does not: Force Animation / Rotate / Short Warp act on the local copy only [code]; a client copy whose AI is switched off
  freezes (and teleports when it comes back); the host's Clear SpEffect did not reach clients (use self-expiring rows); event
  bullets hit only the firing machine's player; part HP is per machine.
- So: big moves as AI acts with TAE payload; anything a machine must produce for its own player never behind a host gate;
  never move the boss with per-machine event commands (`coop.md` 4).
- **Every machine runs the whole EMEVD: design set pieces as "host director + client follower"** [data, game-MP]: every command that
  changes the boss (warp, gravity, forced animation, AI on / off, re-plan, enable / disable) under a host test; at the end of one opening
  set piece every client re-landed the boss and switched its AI on ~1.5 s apart from the host - the top suspect for a client-only freeze
  and crash [data; link to the crash inferred]. Keep on every machine only what is local: screen effects, the HUD, the player's own state.
- **Host-forced animations reach clients only on characters that replicate**: on the boss they arrived; on `isHostSyncChr 1` summons
  nothing arrived - test per character type before relying on host-only animation lines [game-MP].
- **One judge**: the host decides ("sword n is down", "ring n breaks", part breaks, cast broken), publishes a NET flag, clients follow, and
  the host re-sends it every few seconds for re-joined clients [data, sim].
- Per-machine vs host-only, as built and confirmed:

  | mechanic | who | evidence |
  |---|---|---|
  | lethal breath tick (boss-centred sphere) | each machine for its own player, sync off | [game-MP log] |
  | guard-shadow barrier | the guarder's machine (own bullet; others sheltered after it replicates, ~RTT/2 + 1-2 frames) | [code, inferred] |
  | part-break decision | host / solo only, network flag, everyone applies the break lines | [code, sim; game-MP plausible] |
  | scripted knock-down / set-piece damage | host only; clients see the replicated animation ~+0.48 s later, no double topples | [game-MP log] |
  | prop animation (siege weapon) | every machine | [data, game] |
  | attack-rate-after-break SpEffect | each machine on its own copy from network flags | [code] |
  | collision switches (Activate Hit) | every machine, sync off | [data] |
  | key-item grants | every machine, own player | [game] |

- Player-anchored patterns read host-published one-hot target-slot flags (the host polls `Character Targeted By` every 0.2 s): in co-op
  no slot -> no shot (a fallback "no slot -> 20000" fired rows through each client's own player wherever he stood); the publisher clears
  the other slots first and sets the new slot one frame later (never OFF and ON in one frame) [code fix, sim, game-MP report]. Clients'
  scripted hits land 0.1-0.6 s after the host's when their script follows a host flag [sim]; host and client boss copies agreed within
  ~1 m / ~1 deg at a breath start [game-MP log].
- **Party size**: never trust `Is Player Count` under Seamless Co-op (it read 2 in a 3-player party that left together, letting 2 Arts
  break a cast meant for 3) [game-MP]; derive the party from per-slot presence (Player No 1..6). Audit every per-player block for slots 4-6
  (warps, target picks, "another player is standing" checks, per-player toggles and counters, alive flags, test-mode handlers); add‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ warp
  regions for players 4-6 and floor-check every point against assets [data].
- **Harden every end condition of a long set piece** [game-MP]: the host ignores end signals that can arrive from clients; clear stale
  flags at the start; read end terms over >= 2 frames (a one-frame wrong read latched a wait and aborted a cast); one breadcrumb flag per
  end term, logged by the DLL; never put a NET flag into a local batch reset.
- **Cast-break mechanics** ("break the cast with N ultimate Arts"): count only inside the visible window (open it at the line that SHOWS
  the bar; latch Arts already running when it opens; local copies of remote toggles at the special's start; refresh the others' Arts only
  for Arts inside the window); the required count = players present at that moment by per-slot presence; one owner per toggle (each
  player writes only their own NET toggle, the host counts) [game-MP bug, sim].
- Concealed players (Finale / invisibility effects): detect by their SpEffect ids (e.g. 703500 / 7260703 / 8970041); a
  `Has State Info 600` test was suspected to read true in game; no vanilla script reacts, the engine drops the target [data,
  game symptom].

## Unverified

Stance fixes under a full 6-player load; client enabling helper copies only after a host NET flag (optional hardening);
directional stance breaks through a private c9997 + hks override; flinch slot 30011-style appended single events playing;
helper watchdog fixes (sim only); depth rows attached by the engine to event-enabled helpers; a client's HUD bar following a
helper's replicated HP; the downed duration of the source.
