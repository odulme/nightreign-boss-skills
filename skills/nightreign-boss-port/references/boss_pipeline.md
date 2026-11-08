# BOSS production pipeline S0-S12 (port a boss, or build an original one, for Nightreign)

The backbone of this skill. Every boss goes through the same thirteen stages; each ends with an exit gate. A stage is not
"done" before its gate passed at the evidence level the gate names. The stage ids S0-S12 are stable (other skills refer to
them); sub-stages carry a suffix (S1-alt, S2a ...) and never renumber the main stages.

Tags as in `SKILL.md`: [game-MP] > [game] > [code] > [data] > [sim] / [model] > [inferred]. Only [game] / [game-MP] prove a
fix; [model] and [sim] find causes and predict, they never close a gate that says [game].

Placeholders (here and in the stage references): `<MOD_ROOT>` work tree, `<GAME_DIR>` game folder, `<DEV_PROFILE>` the layered
dev `.me3`, `<STAGE_DIR>` a staged package folder, `<CHR_ID>` your character id, `<DONOR_CHR>` motion donor, `<BEH_DONOR>`
behaviour-graph donor.

Order: S0 -> S1 (or S1-alt) -> S2 in sequence, S3 passed before the first attack is built; S4-S7 run per move and may
overlap (one move can be in S6 while another is still in S4), but every in-game check of them uses the S3 panel; S8-S10 can
start on a body that passed S2, but their gates are run with the moves and AI of S4-S7 in place; S11 packs only what S12
confirmed in the dev profile. Record every gate result with its evidence tag in the coordination file.

---

## 0. Routes and destinations

| route | when | what changes in the pipeline |
|---|---|---|
| A - port, foreign engine (MHW, Relink, Unreal ...) | the boss exists in another game with its own data | S1 = extraction + own decoders; motions converted (S4); AI from the source tree (S7) |
| A' - port, same engine family (DS3, ER-era files) | FromSoftware source | S1 / S4 / S6 / S7 carry files nearly 1:1: skill `ds3-nightreign-port` |
| B - original boss from its own model | no source game; a concept / AI-generated / sculpted model | S1 is replaced by **S1-alt** (model), S2 splits into **S2a-S2e** (rig, base motions by retargeting vanilla donors, export, staged render, show build); attacks / AI are designed, not ported. Gates G0-G8 of this route map onto S0-S10 (table below) |

Routes A and A' begin only after the released-source check (`SKILL.md` Step 0) passed; route B needs none when every asset is
the user's own.

| destination | S8 (fight) | S10 (co-op) | S11 (release) |
|---|---|---|---|
| Nightlord (new / replacing) | `nightreign-nightlord-replace` `fight_script.md`, `item_switch.md` | its `coop.md` | its `release_packaging.md`, `testing.md` |
| arena boss in an own map block | `nightreign-map-port` (block, MSB, collision, navmesh) + the nightlord fight-script skeleton | as Nightlord | as Nightlord |
| field / Shifting Earth boss, large enemy | `nightreign-map-port`, `ds3-nightreign-port` (encounters, bars, rewards) | vanilla co-op rules (same file) | map-port `testing-packaging.md` |

Original-route gates (Blender-OK / format read-back OK / loads in game / fight-ready are the four report words of that route):

| gate | lives in | pass condition (short) |
|---|---|---|
| G0 contract | S0 | form, scale, rigid / cloth / extra-limb parts, donor family, budgets agreed |
| G1 static model | S1-alt | re-import has the same mesh / tri count; finite coordinates; no zero-area tris; interfaces rendered close up |
| G2 game mesh | S1-alt | tri budget met; same-camera compare with the high mesh; UV seams intact |
| G3 rig | S2a | <= 4 influences, no zero-weight / bad-sum vertices; pose sheet; edge-stretch p1-p99 per pose |
| G4 animation (Blender) | S2b (base set), S4 (attacks) | per-clip QA (planted-foot speed, tail-vs-leg hits, floor) + GIFs on a 0.5 m grid reviewed by the owner |
| G5 format | S2c | every output read back: skeleton type hashes, clip round-trip error, FLVER verify, PTCH audit, TAE read-back |
| G6 offline game-data render | S2d | STAGED FLVER posed with STAGED clip data on several frames per clip |
| G7 show build in game | S2 gate | loads, lock-on, hits register, right bar name, textures right, secondary motion stable [game] |
| G8 combat | S4-S10 | attacks, AI, fight script, balance |

---

## 1. One-page overview

| stage | goal | main outputs | exit gate (evidence) | detail |
|---|---|---|---|---|
| S0 Plan | first the released-source check (`SKILL.md` Step 0), then decide what is built and how "done" and "what happened" will be seen | release evidence (title, date, source checked) or "own assets", survey sheet, five decisions, diagnostics plan, shipping configuration, id registry, (G0 contract) | Step 0 passed with its web source written down (routes A / A') or own assets confirmed (route B); written decisions; tester agreed on "done" and fidelity rules; id checker clean over every co-loaded layer [data] | `survey_and_extraction.md` 1, 6; this file S0 |
| S1 Extract | read-only, hashed source + verified decoders + per-attack data | manifest, decoders, action catalogue, attack data table | every motion decodes and renders like the source; attack data table per move [data] | `survey_and_extraction.md` |
| S1-alt Model | (route B) a game-ready static mesh | high mesh, game mesh, textures | G1 + G2 [data] + owner review of renders | `original_model.md` 1 |
| S2 Show build | a body that loads, looks right, can be hit and dies; no attacks | skeleton, FLVER, dummies, hurtboxes, part groups, behbnd, minimal anibnd, rows, names | [game] visible / lockable / hittable / dies, bar name right in every shipped language; hurtbox coverage >= 95 % per part [model] | `skeleton_model.md`, `physics_hurtboxes.md`, `donor_graph.md`, `original_model.md` |
| S3 Debug harness | play any move on demand and read what happened | dev debug panel, sync log, heap gauge, dev AI binder | [game] panel plays a move, logs readable; [sim] wrappers inert with flags off | `debug_panel.md`, `diagnostics.md` |
| S4 Motion + TAE | every move and reaction complete, facing like the source, no slide | clips, variants, TAE, markers, reactions, knock-downs, death | [game] every move complete, no slide; [model] heading model agrees with the log | `animation.md`, `tae_turning_windows.md`, `reactions_death_phases.md` |
| S5 Attacks | each move hurts exactly where and when it shows | judge chains, capsules, bullets, floor / collision rules | [model] per-move tables; [game] each move once via the panel, no "hit without being reached" | `attacks_hits.md` |
| S6 FX + readability | looks accepted, budget kept, sound present | FX copies with value edits, banks, TAE 96 / 129, sparks | [game] tester accepts looks; [model] fill / particles / FX alive <= envelope | `fx_sound.md` |
| S7 AI | source-like move choice; heap survives a real expedition | Lua (precompiled), fidelity report, load-cost report | [sim] fidelity as installed; [game] heap gauge in a real expedition with co-loaded mods | `ai_port.md` |
| S8 Fight script + arena | arrival -> victory / defeat in the destination; clean arena | fight EMEVD, set pieces, collision states, navmesh, texts, key items | [game] arrival -> victory; collision audit 0 orphans [model]; language matrix complete [data] | destination skill; `reactions_death_phases.md` 4-5 |
| S9 Balance | numbers the tester decided, per depth / party | HP, part multipliers, break durability, damage | tester decision recorded with numbers per depth / party; logged max HP = published table [game] | `params_balance.md` |
| S10 Co-op | the same fight on every machine | host / client roles, slot audits, NET decisions | [game-MP] numbered checklist + every machine's log aligned | `reactions_death_phases.md` 7; `nightreign-nightlord-replace` `coop.md` |
| S11 Release | ship exactly what the tester confirmed in dev | pins, delta regulation, installer / patch, readme | release vs dev differs only by named dev-only rows / release-only cells; release vs previous release = intended list; privacy scan 0 new | section 4, 6; `nightreign-nightlord-replace` `release_packaging.md` |
| S12 Live feedback loop | every report becomes one dev overlay, confirmed before any pack | one overlay per report | tester confirmation in dev before the next pack | section 4, 5 |

---

## 2. Gate vocabulary

- **Four report states, never merged**: built -> installed and read back -> the tester saw it work -> the tester accepted it.
  A new in-game counter-example overrides every earlier PASS.
- **Offline gate** = deterministic builder PASS + independent read-back (only the named members / rows / events / FXR slots
  changed) + the model numbers the stage asks for. Use it to decide what to install, never to call something fixed.
- **In-game gate** = the tester confirmed it in the dev profile (S3 debug panel available). Co-op gates need [game-MP] with logs
  from every machine.
- **Shipping-configuration gate** (S7, S9, S10): measured in the configuration players use (co-op DLL, forced Deep Night depth,
  co-loaded mods), not only in a solo dev entry. If that is impossible, present the uncertainty with numbers.
- Mark inferred engine semantics as guesses in every report ("direction value 1 = up [inferred]").

---

## 3. Stages

### S0 Plan

**Goal**: decide what is built, how "done" is judged and how you will see in game what happened - before any file.

**Inputs**: the source game (read-only) or the concept / model (route B); vanilla extracts; the profiles the boss will ship in.

**Tasks**
0. **Released-source check - mandatory, always first** (`SKILL.md` Step 0): before any survey, extraction or brief, verify
   with a web search that the source game (for DLC content, that DLC) is officially released and on sale; write the title,
   release date and the source checked into the coordination file. Unreleased, leaked, datamined-from-unreleased-builds,
   beta / network-test (NDA or not) or unconfirmable sources: refuse the port, explain why, and stop the pipeline here. Route B
   with the user's own assets needs no source-game check; record "own assets" instead.
1. Survey sheet (`survey_and_extraction.md` 1): motions, bones, meshes, timelines, attack / hurt data, effects, sounds, AI,
   numbers that live only in the source exe, phase forms, helper actors.
2. The decisions: destination; donor graph by body plan (`donor_graph.md`; humanoid c2130, quadruped / flyer c4510, ordinary
   c4373); placement (in a vanilla arena block vs an own block - prefer an own block that only its route loads, S7); Deep Night
   link (7767 or 0); switch protocol for Nightlords (`nightreign-nightlord-replace`).
3. **Feasibility of "source-faithful" requests**: survey the source mechanisms early (real lethal hits, guard / cover shadows,
   terrain-blocked fans, target-anchored patterns, NPC lines) and present each as "source does X; we can do A / B / C" with
   numbers. Testers asked for source behaviour after simplifications several times [game decisions].
4. **Diagnostics plan** (built in S3, `diagnostics.md`): sync-log fields - boss animation id, position, yaw, HP; local player
   position, HP and damage taken; every mod flag of the fight incl. per-machine worker / lock flags; part records (base / max /
   current); AI-heap gauge; frame times. Reserve the fight's flags inside a range the log already covers.
5. **Shipping configuration list**: co-op DLL (Seamless Co-op), add-ons that force a Deep Night depth, co-loaded mods (their AI
   binders, who else sits in your arena block), me3 version. Plan one calibration fight in it (S9).
6. **Id registry before building**: chr id (absent from the archive dictionary AND from every co-loaded mod, incl. their dev
   stages), bands for bullets, BehaviorParam judges, AtkParam, SpEffects, FX ids, sound ids, flags, entity ids, navmesh
   NameIDs, key-item rows, text ids. One owner per range, ranges written only in the owner's section (a checker failed because
   another note quoted the debug ranges) [data].
7. **AI heap budget per world for the whole joint profile** (`ai_port.md` 6): aicommon + open-field tiles + the arena block's
   scripts + summons + every co-loaded mod's scripts.
8. Route B, **G0 contract**: form, scale (height in m), which parts are rigid / cloth / extra limb, motion donor family, behaviour
   donor, budgets (tris, bones, texture sizes), what the show build must prove.
9. Ask the tester what "done" means (fidelity rules, what may be simplified, aggro / arrival rules) and agree on the report
   words (section 2). Open a coordination file (ids, owners, decisions) and a STATE.md per line of work.

**Tools / files**: coordination json / md, id checker with allow-lists, the vanilla AI census (`ai_port.md` 6).

**Exit gate**: Step 0 release evidence (or "own assets") written; decisions written; tester agreed on "done" and on fidelity rules; registry passes the id checker over every
layer that may be co-loaded [data]; diagnostics list and shipping configuration written.

**Typical failures -> fix**

| failure | fix |
|---|---|
| no player HP / damage-taken field: "was I hit?" undecidable for three rounds; part HP unlogged, two rounds of inference | the diagnostics plan above, built in S3 |
| tuned solo at depth 0 without the co-op DLL; players used a pack that forced depth 4, in co-op: breaks 4-5x too fast [game-MP] | calibrate once in the shipping configuration |
| NameIDs and a guard flag found unclaimed at pack time; a quick-test kit's event id equalled a new guard flag [data] | one registry, typed scans over every layer |
| a mod boss placed in a shared vanilla arena block: its characters and AI loaded in every expedition there [data, game crash] | own block (S7 heap) |

### S1 Extract (route A)

**Goal**: a complete, hashed, read-only extraction, verified decoders, an action catalogue and a per-attack data table.

**Tasks**
1. Extract everything once (mesh, skeleton, all motions incl. cutscenes, timelines, attack / hurt data, AI, params, banks, text
   tables, textures incl. virtual ones); manifest with size + SHA-256; never write into it (the source may be uninstalled).
2. Own decoders, verified by rendering decoded poses‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ against the source; one clock contract (60 fps + speed curves).
3. **Per-attack data table** (`survey_and_extraction.md` 6): the joint that spawns each shell (MHW breath shells come from a
   breath joint, not the head), shell life vs effect life, radius and growth, speed, re-hit interval, placement rule (anchored
   to the target / the boss / the floor; pattern extents), damage values, special ids, every number that lives only in the exe.
   Six later fix rounds of one port were "aimed / anchored from the wrong place" [game].
4. Label motions by measurement (hip height, root, "does anything start from its end pose"), never by name; action catalogue
   with stable ids built from the installed files.
5. Official names of the boss, phases, attacks, summons in every language from the source's own text tables (S2, S11).

**Exit gate**: every motion decodes and renders like the source; catalogue exists; attack data table per move; manifest
re-check clean [data].

**Typical failures -> fix**: public parsers wrong (write your own, render-check); death / knock-down labels swapped (measure,
ask); a stale patch chunk compared (take the latest chunk per path); an agent overwrote a source table (manifest check after
every agent task, restore from the archive).

**Detail**: `survey_and_extraction.md`.

### S1-alt Model (route B: G1 + G2)

**Goal**: a static, game-budget mesh with clean interfaces and textures, before any rig.

**Tasks** (`original_model.md` 1): generate / sculpt in parts (body, helmet, pack, tail, props) but keep sleeves, cuffs,
gloves, boots in the body; fix interfaces in the static model (collar vs helmet by material maps, cuff vs glove, mounts, tail
socket); weld seams then decimate with Collapse (UV seams stay); angle-based smoothing, never flat shading on hard surfaces;
simplify end caps first; keep every delivered version immutable.

**Exit gate**: G1 - re-import of the exported file has the same mesh / tri count, all coordinates finite, no zero-area tris,
interfaces rendered close up; G2 - tri budget met (a ~167k-tri humanoid with a three-layer tail loaded at 60 fps in a quiet
arena [game]), same-camera comparison with the high mesh, UV seams intact. Owner reviews the renders.

### S2 Show build

**Goal**: the body loads, looks right, is lockable and hittable everywhere and dies normally. No attacks yet.

**Inputs**: S1 decoders / catalogue or S1-alt mesh; donor files; vanilla templates (FLVER, skeleton, physics, behbnd).

**Tasks (both routes)**
1. Skeleton: Master at 0 and identity (route B: rebase Master and fold its transform into the children), Root where the donor
   needs it, -Z facing, parent < child depth-first (`skeleton_model.md` 1-2).
2. FLVER: node order [weighted bones][meshes][dummy owners][other bones], unique material names, display masks, OBB mesh boxes,
   textures with `_l` twins (`skeleton_model.md` 3-5).
3. Dummies: **every placement dummy parented to the fixed SFX owner node** (`Dmypoly_SFX_固定`; parent / attach -1 binds to node
   0 = the animated hip), floor dummies at Y 0.3, a dummy 2.0 m along the source's breath joint for streams, ids < 1000
   (`skeleton_model.md` 6).
4. Hurtboxes: physics hkx from a template with the same body / constraint count, PTCH / THSH repairs, hkxpwv part groups; a
   **coverage check** (logged / modelled hit points vs capsules, mesh coverage per part) before anybody grows capsules
   (`physics_hurtboxes.md`).
5. behbnd from the donor (look-at / twist mapped by name, IK off), hks copied, minimal anibnd: idle, walk, turns, death, the
   2-frame identity additives the graph runs (`donor_graph.md`).
6. Rows: NpcParam hybrid clone (body fields from a body-plan donor, scaling / team / poise from the destination tier), battle
   goal 11000 (do nothing), ChrModelParam, ScratchedPartsParam, LockCam (`params_balance.md` 1-2).
7. Names: NpcName (and any bar / summon name) in **every language the game ships**, official names from the source's text
   tables; in a Nightlord / arena fight the bar name at fight start comes from a local copy of common 90075101 with your
   NpcName, not from NpcParam.nameId and not from 90075901 (that one feeds the victory banner) (`original_model.md` 10).
8. Placement for the show build: replace the target Nightlord's MSB part in a vanilla arena (same entity id) or your own block;
   separate test profile with its own save.

**Route B sub-stages**

| sub-stage | gate | what | detail |
|---|---|---|---|
| S2a Rig | G3 | FromSoftware core names placed from YOUR model's joints; coat chains; tail bones (visible + hidden layers); mesh classified by competing geodesic floods; smoothed weights <= 4 influences; rigid parts 100 % one bone; no cloth shaping in rest by bone rotation | `original_model.md` 2-4 |
| S2b Base motions | G4 | retarget vanilla donor clips (idle, walk, strafes, turns, hits, death); foot / ball lock; stance twist fixed; tail / coat secondary motion with build guards | `animation.md` 10, `original_model.md` 5-6 |
| S2c Export | G5 | skeleton from a JSON spec onto a vanilla template, two readers + type hashes; clips + reference frame, round-trip error; FLVER (UV V flipped, normal-map G, <= 4 weights); physics from a donor template with measured capsules; TAE mapped onto your clip ids | `original_model.md` 8 |
| S2d Staged render | G6 | the STAGED FLVER posed with the STAGED clips on several frames per clip (all secondary-motion bugs were invisible on frame 0) | `original_model.md` 11 |
| S2e Show build | G7 | loads, lock-on, hits, bar name, textures, secondary motion stable in game | this stage's gate |

Work every gate on a NEW version folder and keep the previous one as rollback; build with one fail-fast chain script (each
check exits non-zero) - two "fixes" in a row shipped regressions only visible in game [game].

**Tools / files**: HKLib / own Havok writers, SoulsFormats, Blender (route B), FLVER / hkx / hkxpwv / behbnd / anibnd / chrbnd /
regulation / FMG.

**Exit gate**: [game] visible, lockable, hittable everywhere, dies normally, no crash when the player walks near, bar name right
in every shipped language; [model] hurtbox coverage >= 95 % per part; [data] PTCH audit MISSING 0 / UNHASHED 0, FLVER read-back
(node order, flags, dummies), behbnd read back against the skeleton (0 unmapped references).

**Typical failures -> fix**

| failure | fix |
|---|---|
| crash at load / when walking near (event 1001 offsets 0x1A11B59 / 0x182AC83 / 0x6F3EEA8 / 0x6F3EED7) | hkx PTCH / TYPE repairs; FLVER node order / second skeleton table |
| bullets / helpers spawn as "staircases" 3-38 m up | dummies on node 0 (hip): re-parent to the fixed SFX node |
| textures look like camouflage (route B) | UV V not flipped; an offline renderer that flips back hid it - check the flip explicitly |
| bar shows the vanilla name | name patched in 90075901; copy 90075101 locally and redirect every caller |
| bar name blank in some languages | NpcName rows missing in those languages: id x language audit |
| return / exit event silently missing in the test arena | the builder fell back to the vanilla MSB after the stage moved: assert the MSB candidate is the CURRENT stage |
| unhittable / hard to hit | capsules inside the movement cylinder; empty BaseSkeleton / node flags 0; hover body column |

### S3 Debug harness

**Goal**: before the first attack is built, be able to play any move on demand and read what happened in game. Playing whole
fights to reach one move wastes hours, and set pieces at HP thresholds are almost never reached twice in a row.

**Tasks** (full design, ids rules and build checklist: `debug_panel.md`; logs and gauges: `diagnostics.md`)
1. **Dev-only debug panel**: external always-on-top window <-> dev-only DLL through named shared memory; the DLL writes only a
   reserved block of event flags (whole flag bytes nobody else uses) through the game's flag setter and reads each write back;
   features that paid off: play any AI move by id, loop the last move with a pause, AI stop, face the player, approach / back
   off, HP lock, variant-set override, status line (animation, HP, phase, last request / result, flag words).
2. **Dev AI override** = the shipped source byte for byte + an appended block of flag-reading wrappers that route requests
   through the AI's own attack path (pre-turn, stance switch, after-attack goal); a request waits for the next AI decision and
   never cuts a move; set pieces are never touched. **Dev fight-script events** for what only EMEVD can do (load-time clear of
   every debug flag, HP lock by re-asserted `Set Character Immortality`, variant SpEffect override, alive toggle), sync off.
   **Move catalogue** generated from the shipped AI tables + installed TAE, grouped by stance.
3. **Sync-log DLL** (read-only, may ship): the S0 fields at 10 Hz plus per-change lines; rolling / per-fight files (a fixed
   20 MB cap filled in 8.5 minutes and lost the crash moment); a key missing from an old ini defaults to ON.
4. **AI-heap gauge**: largest free block ("8k = yes / no"), free MiB, blocks, every 5 s and at every block load / unload; take
   signatures from a mid-game dump, log the whole pointer chain once.
5. Install the debug package **last** in `<DEV_PROFILE>` and rebuild it whenever the fight script or AI binder changes (section 4);
   claim its flag / event ranges by a scan over every layer and quote them only in the debug section of the registry; the pinning
   tool refuses debug packages.

**Exit gate**: [game] the panel plays a chosen move, the logs are readable and carry the S0 fields, the gauge logs plausible
values; [sim] with all panel flags off the dev AI makes byte-identical decisions to the shipped AI (e.g. 18,000 decisions).

**From here on, every in-game test step of S4-S10 uses the per-move recipe of `debug_panel.md` 7** (set up -> position -> request
-> watch -> loop -> log -> compare -> report). Set pieces at HP thresholds: AI stop + damage to the threshold (an HP lock does not
block thresholds).

**Typical failures -> fix**: gauge built against an exit-time dump's base vtable logged "unexpected vtable" (use the live vtable
from a mid-game dump); exclusive full screen hides the window (borderless); a window started from inside a sandboxed agent host
ran in a private container (start it by double-click); the debug package shadowed by a later package shipping the same paths.

### S4 Motion + TAE

**Goal**: every move, reaction, knock-down and death plays complete, turns only where the source turns, never slides.

**Tasks**
1. Clips: resample 60 -> 30 fps, root motion in the reference frame, every root-motion clip <= 29.7 s / 892 reference samples
   (split longer chains), distance / mirrored variants with registered leaves, rebuilt source chains (`animation.md`). Route B:
   attack clips retargeted / authored like S2b.
2. TAE from the donor, control events only; heading hold (224 = 0 + JT7) with source turn windows; **re-aim windows between the
   shots of aimed multi-shot moves** (close 0.35 s before each release, reopen 0.5 s after, ~60 deg/s); keep the mouth's sideways
   speed below what reads as sliding (`tae_turning_windows.md` 4).
3. AI windows after the release point of the full source move; goal life >= clip + margin.
4. Event timing: **bullet release events >= 0.1 s, markers >= 0.05 s** on every clip with a speed multiplier; the first shot
   fires at the event start; divide source times by the clip speed (`tae_turning_windows.md` 10).
5. Markers: idle heartbeat, busy, airborne, reaction guards, release markers (`tae_turning_windows.md` 8).
6. Reactions 8060 / 8500 / 8700 / death; knock-downs as event slots importing the source chain; **SpEffect 45 over every forced /
   scripted clip and every variant of it, and over the measured airborne span of AI flight attacks**; AI hand-back after forced
   clips by condition, not by a fixed wait; drop stance-break critical rows when no ThrowParam row exists
   (`reactions_death_phases.md` 1-3, 6).
7. Props with bone chains (siege weapons, telescoping parts): reach from geometry, re-encoded asset clips, enlarged bounding box
   (`animation.md` 11).

**Tools / files**: Havok encoder + three readers, TAE writer with read-back, `scripts/heading_model.py`, clip census, completeness
audit.

**Exit gate**: [game] every move complete, no slide, reactions / knock-downs / death as intended (each move requested and looped
from the debug panel, `debug_panel.md` 7); [model] the offline heading
model agrees with the sync log within ~0-2 deg; [data] clip census (frames, seconds, reference samples, imports) and
completeness audit (source chain vs clip vs AI window) clean.

**Typical failures -> fix**

| failure | fix |
|---|---|
| "slides" | turn windows outside source turn intervals; AttackTunableSpin; missing JT7 |
| "the boss does not turn, only the shots home" (median facing error 57 deg at release) | re-aim windows between shots (model 57 -> 3.6 deg) |
| only half of a move plays | AI window before the release point; goal life shorter than the clip |
| random skipped shots / mine lines on a 1.05-speed clip | one-frame release events: >= 0.1 s |
| scripted knock-down: fell, snapped upright, fell again with a critical glow; 12.8 s frozen idle | SpEffect 45 over the forced chain; condition-based AI hand-back; drop critical rows |
| actor turns by itself in a long clip | clip length / reference samples |
| death freezes in a pose | A10000 / A10001 import a clip you replaced |

### S5 Attacks

**Goal**: each move hurts exactly where and when it is shown, is dodgeable unless it is meant not to be, and is fair to short
characters.

**Tasks** (`attacks_hits.md`)
1. Chain per event (TAE -> BehaviorParam -> Atk / Bullet -> children -> FX / sound ids) with a verifier; status scrub; footprint
   audit.
2. Damage carrier per move from the S1 table: melee capsules from source volumes; streams / beams from the breath-joint dummy,
   ending with the source shell's life; floor child per beam bullet; posture rules (`sfxPostureType` 0 on streams, 1 only on
   splashes).
3. Area patterns: impact circles fired from a TAE event on a fixed floor dummy with `isEndlessHit 1`; delayed mines by the floor
   rule (1.5 m drop, tuned gravity, LC 5 child); player-anchored rows fired from the boss, never by warping a helper.
4. Collision-aware hits: map-collision radius +0x8C = 0.1 on rays; visual and damage rays as one family; projectile-only
   collision copies (HitFilter 16) for blockers; shadows need ray radii near the blocker width; guard-shadow barrier if wanted.
5. **Hit-height rule**: the lowest point of every damage sphere along its flight <= ~0.9 m above the floor (body tops 1.8 / 1.3
   / 1.0 m must all be hit).
6. Certain-kill / full-screen moves as real lethal hits from the boss (boss-centred sphere fired per machine for its own player),
   guardable from the front if wanted; visual lanes separate and harmless.
7. Visible dev marker on every invisible damage volume while building (ask the tester about it explicitly); a release switch
   removes it - diff both modes.
8. Roll-dodge review; sizes capped by what is shown.

**Exit gate**: [model] per-move tables (floor-point error, reach, share stopped by low bumps, shadow / beside / open hit share,
body-top hit shares, roll survival); [game] each changed move played once via the debug panel, "hit when not reached" and "stood
in it untouched" absent; [data] chain verifier PASS.

**Typical failures -> fix**

| failure | fix |
|---|---|
| stream "sprays forward, does not hit in front" | aim from the source's breath joint, not the head |
| stray flames sliding over the floor after a stream | `sfxPostureType 0` on stream bullets |
| ground-flame children lick backward | children take yaw from the parent: attachment 0 + steep elevation, or `isOwnerOverrideInitAngle 1` |
| mines on walls / terraces / in the moat | floor rule instead of "drop to first collision" |
| a row always at the same spot | helper never moved (`Warp ... Copy Floor` with dummy -1): fire from the boss |
| fan dies on small bumps / no shadow behind pillars | +0x8C 0.1; ray r ~1.4-1.6 m; projectile-only blocker collision |
| short character stands in the fan untouched | damage origin ~2.0 m; lowest sphere point <= 0.9 m |
| lethal sphere launches in random directions | centre it on the boss, not on the victim |

### S6 FX + readability

**Goal**: effects and sounds the tester accepts, readable (the boss and the hit moment stay visible), inside the GPU budget.

**Tasks** (`fx_sound.md`)
1. Convert (same family) or borrow + recolour (foreign engine); flat art as new shells with the source texture.
2. **FXR changes only as byte copies with in-place value-slot edits**; never change counts, offsets or node links; never
   round-trip a vanilla FXR through a writer; scan every user of an FXR before editing it in place; give each family its own copy.
3. Brightness: work on the HDR multipliers, ship presets behind a builder flag, expect one tuning round.
4. Readability: ask for a screenshot + a source reference picture; model which emitter covers the screen (the billow, not the
   smoke, blocked the view); upward-jet recipe for blasts.
5. **Budget**: time-aligned quad fill <= the heaviest move that already ships, particles <= 1.5x, FX alive not higher, no new
   point-light / distortion / radial-blur / tracer / GPU-particle node; count lights per instance in map-region FX.
6. Sound: own bank children-first, no references out of the bank, total resident custom media budget; TAE 129 from the source
   timeline; hit‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ sparks / hit sounds through private rows.

**Exit gate**: [game] the tester accepts the looks of every changed move (requested from the panel, screenshot next to a source
reference picture) and heard its sounds; [model] fill / particles / FX alive
<= envelope; [data] FXR proof (bytes differ only inside the target slots, inverse restores the source, every other member
byte-identical).

**Typical failures -> fix**: game froze at the first spawn after a 2-byte unlink that passed every offline proof (value edits
only); RGB x0.75 and the tester saw no change (HDR multipliers); two rounds cutting smoke while the fire billow blocked the view
(identify the emitter by its texture); a cross-binder copy of a vanilla carpet never rendered (build from FX already seen in game
in this port); GPU hang on one machine during the densest blended moment (thin particle / trail counts, keep the look).

### S7 AI

**Goal**: the boss chooses moves like the source (or the design), and the AI heap survives a real expedition next to every
co-loaded mod.

**Tasks** (`ai_port.md`)
1. Decode the source tree; one Lua function per node; unknown exe-side predicates as named switches; per-boss state only in
   `ai:SetStringIndexedNumber`.
2. Fidelity harness under real Lua 5.0 with mocks: pool tests, cells, dynamic runs, "as installed" numbers.
3. **Ship stripped precompiled bytecode with small prototypes**: hoist runs of statements out of over-large FUNCTION BODIES into
   helpers (splitting only the main chunk does not help); targets: no prototype above ~700 instructions / 128 constants, largest
   load block <= ~3 KB, nothing >= 8 KB; proof set (bit-identical unsplit prototypes, round trip, scope, strip, shapes, decision
   traces); regenerate `.luagnl`; keep a restructured-source fallback binder.
4. Panel wrappers only in the dev binder (S3); HP gates as ratios (`GetHpRate`), never absolute HP.
5. Heap: own arena block (an arena block's MSB loads all its characters and AI whatever fight is chosen); count co-loaded mods'
   source-text AI; gauge in a real expedition.

**Exit gate**: [sim] fidelity numbers reported "as installed"; [data] load-cost report within the targets; [game] heap gauge in a
real expedition with the co-loaded mods: "8k = yes" throughout, minimum free recorded; in-game behaviour accepted.

**Typical failures -> fix**: boss idles and never attacks (binder failed to load; one battle goal per binder; unbound keys);
everyone black-screened and crashed at the settlement (Lua OOM at the teardown: source text + resident mod characters); a
precompiled build still left a 15 KB block (one 3,745-instruction Interrupt body: hoist helpers); `.luagnl` stale (17 names
missing: unload did not clear them).

### S8 Fight script + arena

**Goal**: from arrival to victory (and defeat / retry) in the destination, with arena collision, navmesh, texts and items clean.

**Tasks** (destination skill for the script itself; character-side points here)
1. Nightlord: `nightreign-nightlord-replace` `fight_script.md` (start, bar, BGM slot, phases, part HP, victory, credit),
   `item_switch.md`; field: `nightreign-map-port`.
2. Gates as HP ratios (EMEVD `IF Character HP Ratio`, Lua `GetHpRate`); HP-threshold set pieces are tested with "AI off + damage"
   (an HP lock does not block the threshold) [game].
3. Set pieces: every collision piece with an entity id, switched with `2011[1] Activate Hit` in the same wait-free block as the
   visuals, sync off, on every path (setup, retry, set-piece end, late-join rebuild); offline collision ownership audit; one
   arena-wide ledge scan instead of one fix per report.
4. Navmesh: when content moves inside a cloned block, navmesh, NVA ids and NVA connections move with it (`nightreign-map-port`).
5. Part breaks (`params_balance.md` 7-8): carriers created before breakable records, the watcher starts right after Create,
   re-arm in the same frame as the break test, host / solo-only break decision via a network flag.
6. Texts: NpcName and every fight / hub text in every shipped language; key items in the hub via `2003[108]` grants in the vanilla
   key-item band (`nightreign-nightlord-replace`).

**Exit gate**: [game] arrival -> victory text + music in the dev entry (and the destination's real route before release);
[model] collision audit 0 orphans, ledge scan list reviewed with the tester; [data] language matrix complete.

**Typical failures -> fix**: invisible walls left after a set piece (collision without entity ids); fences 3.1 m above a 1 m
ledge (scan, move fence tops to ledge + 0.15 m); summons frozen for several releases (navmesh left at the clone's origin); key
items popped up but never listed (wrong grant instruction / id band / ambiguous probe).

### S9 Balance

**Goal**: HP, part durability and damage the tester decided, with expected numbers per depth and party.

**Tasks** (`params_balance.md`)
1. HP as a multiple of a stated vanilla mean (7 regular Nightlords 3516.29, or 8 entries incl. Heolstor 1408 + 2880: 3612.75);
   offer steps (e.g. 0.75 / 0.9 per phase, or 1.7 / 2.1 / 2.5 for a single big body) with solo and party numbers.
2. **Absolute-HP audit** before any HP change: absolute HP compares, changeHpPoint on the boss, absolute part bases; then the HP
   change is a two-cell patch with anchors.
3. Party / depth: Seamless Co-op max HP = trunc(f32(hp x f32(3.54 x DN x (1 + 1.2 (n - 1))))) (measured at 2P / 3P; 4-6 players
   from the formula, unmeasured); publish the expected max-HP table the tester compares with the log.
4. Parts: multipliers via never-breaking carrier records; break durability by design goal (constant absolute durability vs
   constant fight progress); engine-tested party re-base; second-break rule; when HP changes, rescale every free part base.
5. Damage: transfer from source values; after-break multipliers solved on the defence curve; DPS stake benchmark against vanilla.
6. Before using any log for calibration ask: trainer / damage multiplier, HP lock, buffs, level changes. Calibration fights run
   with every external damage multiplier OFF (a multiplier scales HP damage but not part damage); the debug panel is used only to
   position, never to skip to a phase in a calibration run.

**Exit gate**: the tester's decision recorded with numbers per depth / party size; [game] / [game-MP] logged max HP equals the
published table; break positions in the HP bar reported per depth / party [sim].

**Typical failures -> fix**: three stacked knobs (weak rate x part HP x bullet k) gave x3.3 melee / x6.7 bullets instead of x2 and
"the head never broke" (restate per attack class first); a rescale forgot chest and wings (ask about every breakable part); a
trainer made part loss look like 0.2 per point.

### S10 Co-op

**Goal**: the same fight on every machine, for 1-6 players.

**Tasks** (`reactions_death_phases.md` 7; `nightreign-nightlord-replace` `coop.md`)
1. Every machine runs the whole EMEVD: set pieces as "host director + client follower"; every command that changes the boss
   (warp, gravity, forced animation, AI on / off, enable) under a host test; clients keep only local effects.
2. Summoned / helper combat characters: `isHostSyncChr 0` and AI ON on every machine (vanilla); host-forced animations reach
   clients only on characters that replicate - test per character type.
3. One judge: the host decides (part breaks, "sword down", cast broken) and publishes NET flags, re-sent every few seconds.
4. Party size from per-slot presence (Player No 1..6), never `Is Player Count` under Seamless Co-op; audit every per-player block
   for slots 4-6; target-slot publishing (clear first, set one frame later; no slot -> no shot).
5. Own-player effects per machine, sync off (lethal ticks, guard barriers, key-item grants).
6. Harden long set pieces (host ignores client end signals, clear stale flags, debounce >= 2 frames, breadcrumb flags).
7. Logs from every machine right after the session, aligned by UTC / offset; new pulse flags inside an already-logged range.

**Exit gate**: [game-MP] numbered per-mechanic checklist passed, each player reported their own screen, every machine's log
collected and aligned; [sim] 1-3 players behave identically to the previous build; 4-6 players need a real 4-6 player session.

**Typical failures -> fix**: clients re-landed the boss and switched its AI on ~1.5 s apart from the host (host gate);
summons never animated on clients (`isHostSyncChr 1`); 2 Arts broke a cast meant for 3 (`Is Player Count` read 2 in a 3-player
party); an offline simulator ran 1,488 scenarios without reproducing a real failure (log real sessions).

### S11 Release

**Goal**: ship exactly what the tester confirmed in dev - nothing more, nothing less.

**Tasks** (section 4 and 6; `nightreign-nightlord-replace` `release_packaging.md`)
1. Pins: per path the top-most file from an explicit list of dev packages, read from a COPY of `<DEV_PROFILE>` without the debug /
   probe blocks; the guard refuses other changes vs the previous pins; map-side files (MSB, collision, navmesh, msg, chrbnd) listed.
2. Base-chain proof through the builders' recorded input hashes back to the previous release; no link through a probe / debug package.
3. Regulation by delta transfer: previous release + exactly the dev row delta + release-only cells; untouched tables byte-exact.
4. Release-only switches run in both modes on the same input and diffed.
5. Patch accepts only the previous release; deterministic outputs (do not recompress unchanged files; re-encrypt with the input IV).
6. Language audit, version strings that are not substrings of each other, readme test status per change, privacy scan, rehearsals.

**Exit gate**: release vs dev field compare differs only by the named dev-only rows and release-only cells [data]; release vs
previous release changed-file list = the intended list [data]; privacy scan 0 new hits with a positive control; rehearsals pass
for every audience.

### S12 Live feedback loop

**Goal**: each player / tester report becomes exactly one dev overlay, confirmed in dev before anything is packed again.

**Tasks**: run the tester loop (section 5); reproduce the report offline (replay of logged positions, a model, a render) before
the fix; one overlay per change (section 4); the tester's "pass" for a batch is the pack trigger; then S11.

**Exit gate**: tester confirmation in the dev profile before any pack. Shipping something untested is the owner's explicit,
labelled decision ("not specially tested" in the readme).

---

## 4. Dev-overlay workflow

1. **One change per package, in a NEW folder**, appended to `<DEV_PROFILE>` with `load_after` = the previous top package (later
   package wins per path; the me3 log's `override=` lines prove which copy was served). Never overwrite an installed or staged
   folder: the folders are the rollback history.
2. **One builder per change** that asserts its own base and edits only its own cells / FXR slots / events at their exact old
   values ("cells mode"): outputs stack in any order, several agents can work in parallel, and the same builder replays on the
   release inputs.
3. **Install guards**: refuse when the game runs (ignore 0-thread zombie processes), when the stage hash is not the verified one,
   when the current top package is not the expected one, or when the target folder exists; back up the profile; the next build
   asserts the new top.
4. **The debug package is dev-only, kept LAST, and rebuilt whenever the fight script or AI binder changes** (the publisher only
   appends, so a later package shipping the same paths shadows it or is shadowed). Procedure: remove its block, repoint the next
   block's `load_after`, install the new package, rebuild the debug package on the new base, re-add it last. If a rebuild changes
   a proven DLL binary, put back the binary proven in game.
5. **Probes** (log-only part-HP probes, visible markers, test items) are built behind `--probe` / dev flags, marked NEVER PACK in
   the state file; never run the pin generator while one is installed.
6. Order per feature: read-only research -> build into a stage folder -> independent verification -> install into dev -> tester
   plays -> release build from the dev top -> release diff vs the previous release -> pack -> patch.
7. Dev patches that pass their own offline checks are installed without a separate audit; the tester verifies in game. Anything
   for other people gets one audit + one re-check.
8. Back up every shared-tool edit next to the original and copy a round's tools into a new per-round folder.

## 5. The tester loop

**Before analysing any log, ask**: trainer / damage multiplier / HP lock on?; character, level, weapon, relics; profile (dev entry
vs pack with co-op DLL and forced depth); solo or co-op, host or client; what they aimed at; exact spot (screenshot + panel
history); hit or not when the log cannot tell.

**For looks**: ask what each element of a screenshot is before interpreting it; ask for a source reference picture next to it;
for "stray X in move Y" ask which move, which side and whether it coincides with the move's own effect (other moves may share
the FX).

**Before blaming the mod**: check the test machine (an FPS drop coincided with unrelated CPU-bound processes); check object
lifetimes in code before advising players (a "restart after each expedition" advice was withdrawn).

**How to report each round**: profile + active overlays; what changed per move (catalogue id, second, body part); a 2-minute
"where to look" list; proven vs unproven; rollback. Use the four report states and the evidence tags; [model] / [sim] are never
"fixed".

**Decisions**: present options with numbers (certain kill vs survivable, guard‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ allowed, which ultimates may save, near-edge
distance, brightness level, circle size, multiplier width), build the default, keep alternatives one flag away, record the
choice. Ask balance targets as HP-bar fractions. Quote the tester's numbers and the model's side by side; solve linear targets
on the real curve and say so.

**Never** claim a vanilla or engine mechanic from params, menus or inference - mark it [inferred] and ask; the tester knows the
source and NR better than the files and owns fidelity calls. After an in-game failure, do not stack a new paper cause on a piece
never seen to work: rebuild from pieces already proven in this port and verify against a replay of the tester's logged
positions. After two failed paper explanations ask for a recording.

**Dev first, then pack**: every change (also pack-layer features such as hub key items - give them a dev route) is confirmed in
the dev profile before it is packed. Both times a feature went straight into a release, the release failed. A boss that only
works in one lucky save is a rumour, not a feature.

## 6. Pre-release checklist

- [ ] Every change of this release was confirmed in dev (list overlays with the tester's words); untested items labelled.
- [ ] Profile copy without debug / probe blocks; no probe, debug package, dev marker, quick-test kit trace in the release (guard
      scans folder and zip).
- [ ] Pins guard clean; map-side files listed; base-chain proof complete.
- [ ] Regulation: release vs dev differs only by named dev-only rows and release-only cells; untouched tables byte-exact;
      decompressed size under the known limit; merge allow-lists updated for new tables / id bands / local flags.
- [ ] Release-only switches diffed in both modes.
- [ ] AI binders are stripped bytecode (first byte 0x1B, source `=(none)`), passed through untouched; `.luagnl` regenerated;
      developer-path strings neutralised in the source before compiling.
- [ ] FXR: bytes differ from their source only inside value slots; each FX family has its own copy.
- [ ] Language matrix: every NpcName / FMG id in every shipped language, official names.
- [ ] GPU budget of the densest moment <= envelope; heap gauge run in the shipping configuration with co-loaded mods.
- [ ] Co-op: [game-MP] checklist passed, or the readme says "co-op checked offline only"; 4-6 players labelled if untested.
- [ ] Expected max-HP table published and matched by a log.
- [ ] Version string not a substring of another; every place that lists versions updated.
- [ ] Patch accepts exactly the previous release (fingerprint + hashes), `mustBeAbsent` list enforced, test matrix (reference
      install, upgrade = fresh install, uninstall, wrong base, modified file, game running, interrupted) passed; compare hashes,
      not directory sizes.
- [ ] Deterministic outputs: unchanged files not recompressed; regulation re-encrypted with the input IV where reproducibility matters.
- [ ] Privacy scan of every file incl. DLLs, Lua constants and patches: 0 new hits vs the previous reviewed set, positive control kept.
- [ ] Readme: test status per change, stale lines removed, patch notes generated from a per-target file.
- [ ] Rehearsals for each audience on a scratch me3; reproducible side copies deleted before the patch test (disk).

---

## 7. Pitfalls that cost the most time (merged, ranked by rounds / releases lost)

| # | pitfall | what it cost / symptom | fix | stage |
|---|---|---|---|---|
| 1 | delayed ground patterns placed by "drop to first collision", by a helper that never moved (`Warp ... Copy Floor` with dummy -1), from dummies parented -1 (= the animated hip); a sanity guard that always failed was removed as "the bug" | 7 rounds; mines on walls / in the moat, rows at court centre for many builds | boss-fired movers, floor rule, fixed SFX node dummies; find out what a failing guard tests | S5, S2 |
| 2 | under-belly damage circle via carrier children that never reached the floor, `isEndlessHit 0`, posture-1 children with a backward parent yaw, an FX copy never seen to render | 7 rounds, no hit noticed | TAE event on a fixed floor dummy + endless hit + FX already proven in game | S5, S6 |
| 3 | features packed without a dev route ("the dev profile cannot show it"), e.g. hub key items with the wrong grant instruction, ids outside the key-item band, two probe items with one name | 2 failed packs + 4 dev probes; every release that skipped dev failed | dev first, then pack; probe design with unique names and a vanilla control | S12, S8 |
| 4 | calibrating break durability in the solo dev profile and with an external trainer's damage multiplier on (it scales HP damage but not part damage: part HP seemed to drop ~0.2 per displayed point - a trainer artefact, confirmed by the tester, not an engine factor) | co-op breaks 4-5x too fast; a solo tune off by the multiplier | calibrate in the shipping configuration with trainers off, or divide by the multiplier; ask about trainers before reading any log | S0, S9 |
| 5 | set pieces that let every machine warp / animate / switch the AI of the boss | clients re-landed the boss ~1.5 s apart; top suspect for a client freeze and crash | host director + client follower | S10 |
| 6 | summons / helpers with `isHostSyncChr 1` and AI ON only on the host | they never animated on clients and died at their warp points | `isHostSyncChr 0`, AI ON on every machine | S10 |
| 7 | AI shipped as source text; mod characters resident in a shared always-loaded arena block | everyone crashed at the end-of-expedition settlement (Lua OOM at teardown) | precompiled small prototypes; own block; gauge | S7 |
| 8 | stacked balance knobs (weak rate x part HP x bullet multiplier) | x3.3 melee / x6.7 bullets instead of x2; "head never breaks" | restate each request per attack class before building | S9 |
| 9 | FXR structure edit (2-byte unlink of a sub-emitter) | game froze although every offline proof passed | value-slot edits only | S6 |
| 10 | colour-only dimming of HDR effects; cutting smoke when the fire billow blocked the view | 2+ rounds with "no change" | HDR multipliers; identify the covering emitter by texture and a coverage model | S6 |
| 11 | `Is Player Count` under Seamless Co-op; Art counting from the special's start instead of the visible bar | a cast broken by too few Arts; a teammate's early Art cancelled it | per-slot presence; count only inside the visible window | S10 |
| 12 | fat damage spheres with +0x8C = -1; ray radius >= 2.5 m; visual lanes stopped by invisible shells | fans died on small bumps, no shadows, "fewer flames than before" | +0x8C 0.1, r 1.4-1.6 m, visual lanes penetrate the map | S5 |
| 13 | ray origin at mouth height | short / crouching / reviving characters never hit | origin ~2 m, lowest point <= 0.9 m | S5 |
| 14 | head dummy instead of the source's breath joint; `shootAngle` (yaw) used as elevation on an animated-bone dummy; sector apex at the hover point | streams missed in front; lanes 43 m up; hits under the flying boss | breath-joint dummy, FK-sampled dummy heights, near edge from the body | S5 |
| 15 | lethal sphere centred on the victim; damage in a SpEffect payload behind an unmet condition / on party-slot aliases | random launch direction; no damage at all | sphere centred on the boss, damage in the attack row, own player 20000 in a sync-off event | S5 |
| 16 | scripted knock-downs / set pieces without SpEffect 45 and with fixed AI-off waits | double topple, fake critical glow, 12.8 s frozen idle | SpEffect 45 on every forced clip; condition-based hand-back | S4 |
| 17 | one-frame TAE release events on a 1.05-speed clip | random skipped mine lines | events >= 0.1 s | S4 |
| 18 | AI-heap advice from a wrong lifetime model; gauge calibrated on exit-time dumps | advice withdrawn; no data on the first run | read object lifetimes in code; mid-game dump signatures | S3, S7 |
| 19 | collision without entity ids; fences fixed one report at a time; a cloned block's navmesh left at the old origin | invisible walls after a set piece; repeated ledge reports; summons frozen for several releases | ids on every piece; one arena-wide scan; move block-local data with the content | S8 |
| 20 | no player-HP field in the sync log; debug package not kept last; log cap filled before the crash | "was I hit?" undecidable for three rounds; silent shadowing; crash moment lost | S0 diagnostics plan; S3 rules | S3 |
| 21 | names shipped in two of four languages; machine-translated names | blank boss bars in the other languages; 4 of 13 names differed from the official ones | id x language audit; official text tables | S2, S11 |
| 22 | a version string that contains an earlier one (1.8.1 vs 1.8.10) | a substring matcher picked the wrong input | never reuse a prefix; match exact tokens | S11 |
| 23 | route B: secondary motion written frame by frame (each frame read the previous frame's keys); two fixes in a row without a new version folder | coat roots orbited the waist and shredded in game; regressions only visible in game | compute all targets from the untouched pose, then write; build guards; new version folder per gate | S2b |
| 24 | route B: UV V not flipped, hidden by an offline renderer that flipped back | camouflage-looking textures in game | `uv.y = 1 - uv.y`, check the flip explicitly | S2c |
| 25 | bar name patched in the victory event 90075901 | the vanilla name stayed on the bar | local copy of 90075101, redirect every caller | S2, S8 |
| 26 | route B: coat vs legs separated by a single flood from the hem | puffy breeches followed the coat bones and tore at the knee | two competing geodesic floods | S2a |
| 27 | GPU timeout blamed on textures | slimming textures did not help | dense blended particle / trail load: thin emitters, keep the look | S6 |

---

## 8. Unverified (do not build on these without a test)

Each item is a working hypothesis, not a fact.

- Whether the Seamless Co-op party factor enters NPC part max (hence the engine-tested re-base); the HP formula at 4-6 players
  (measured at 2P / 3P only); solo break timing in a pack without a trainer.
- Whether innate 7767 attack / stamina rates apply to EMEVD-fired bullets; the guard direction of a boss-centred lethal sphere
  in a real session.
- Which of fixed floor dummy / `isEndlessHit` / no carrier made an impact circle hit; why a cross-binder copy of a vanilla carpet
  FX never rendered; why ground FX born from an expired stationary hold do not render.
- Whether summons move on a baked arena navmesh; whether vanilla Absorb skills erasing erasable fan rays explain a co-op
  reviver being missed.
- FXR property meanings used as working names (`fx_sound.md` 11); whether NR keeps the Elden Ring defence curve.
- Stance fixes under a full 6-player load; under Seamless Co-op the vanilla 2P / 3P stance rates (7867 / 7967) appear absent, so
  stance breaks may come ~3x sooner than for a vanilla 3P Nightlord [inferred].
- Main-save uninstall of key items; meaning of collision layer 117.
- Restructured precompiled bytecode: all offline proofs passed; confirm the in-game load of each new build (idle boss = load
  failure).
- Seamless Co-op's nrsc.dll carries RTTI names of 5 EMEVD test classes (EventFlagState, PlayerNo, SortieMemberNum, TeamType,
  ChrDead) and most likely intercepts them [inferred]: treat all five as fragile in co-op.
- Client enabling its helper copies only after a host NET flag; `Set Network Update Rate` for summons (optional hardening, not
  proven necessary).
- Spawning extra bosses / helpers on demand instead of placing them in an always-loaded block (heap saving, not built).
- A GPU hang located in the effect / transparent pass from DRED breadcrumb order [inferred].
- Summon AI compiled late on Day 3 as the cause of "that summon never appears" near a full heap; heap problems reproducing solo
  [inferred].
- Route B: whether `RefTwistEnable = 0` is required without twist bones; lock-on from dummies transferred from a humanoid donor;
  the behaviour donor's reactions on an original skeleton; whether the frontal stance (pelvis + legs turned) reads well in game;
  baked offline cloth onto extra coat bones; LOD tier and final texture budget with effects; hitboxes along a telescoping tail;
  a second form by display masks vs a second character.
- Older open items: MHW `flags2` mirror bit; whether the clip limit is ~30 s or ~1,024 reference samples; whether JT7 stops an
  EMEVD Rotate; > 256 weighted bones (UShort index layout); TAE 760 distance semantics on capsule surfaces; selector fallback to
  the LAST leaf for an unmatched offset; streamed voice lines from a character bank.
