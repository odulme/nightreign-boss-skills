# Donor character, behaviour graph, hks

Tags as in `SKILL.md`. Pipeline stages S0 (choice) and S2 / S4 (slots) of `boss_pipeline.md`. Route B (original model): the motion donor
is chosen separately by posture (`animation.md` 10); the behaviour donor supplies graph + hks as below.

## 1. What the donor gives you

The donor supplies the behaviour graph (`Behaviors/c9997.hkx` inside the behbnd), its hks callbacks, the animation ids the
graph and common hks ask for, and TAE templates. It does NOT need to match the FLVER template or the skeleton (a humanoid
FLVER template worked for a quadruped dragon) [game].

| donor | body plan | what is there |
|---|---|---|
| c2130 (Morgott) | biped humanoid | attacks 3000-3016, 3018-3021, 3023, 3025, 3026, 3028, 3029, 3031-3039; event slots used as attacks 20005-20009, 20016-20022; steps 6001-6003; turns 5000-5003; generic hks [game] |
| c4510 (Ancient Dragon) | winged quadruped | 87 graph ids; attacks 3000-3038 without 3018 / 3020 / 3035 / 3039; single events 20000 / 1 / 2 / 10 / 19 / 20 / 25 / 26; loop events 30000 / 5 / 10 / 19 / 25 / 26; idle 0 / 20, walk 2000 / 2001 / 2300, run 2100, turns 5000-5003, fall / land 7000 / 7400, damage 8060 / 8700, death 10000 / 10001, additives 9090 / 9100-9174 / 9500; own hks (generic + 2 extra callbacks) [data, game] |
| c4373 generic `c9997` | ordinary enemies, DS3-like bosses | a state for nearly every DS3 animation id; every DS3 boss port used it [game] |

Rejected: c2130 for a quadruped (humanoid step / parry / throw states, no rest states). c7510 / c7580 have extra event states
(e.g. Event30029) that c2130 lacks [data].

Things to know per donor:
- Every id the graph references needs a TAE entry (real clip or an import), or the state plays nothing [data].
- The c2130 graph always runs additive 9500 and hit-additive 9000: point both at a 2-frame zero-additive clip (pointing them at
  idle double-adds and distorts the body) [game]. c4510 additives 9090 / 9100-9174 / 9500 likewise get 2-frame identity
  ADDITIVE clips.
- Some vanilla slots‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ are unreachable by the vanilla AI or have only `a002_` leaves (c2130: 3017 / 3022 / 3024 / 3027 / 3030);
  add an `a000_` leaf before using them [game: both played afterwards].
- NR's graph has stance break 8700 only (front); DS3's directional 8701-8703 have no state [data].
- c4510 hit reactions identify the part hit: 9090 = weak-part group 31, 9100 / 9110 / ... = PartBlend n per group (76 of 79 matched the
  posed geometry) - useful to classify hits in logs (`params_balance.md` 9) [game, data].
- On c4510, AI attack requests for slots appended beyond the donor's range (3040+) left the boss standing idle in one port; the fix
  restricted AI requests to 3000-3039 and kept the extra clips for other uses [game]. Keep AI-requested moves inside the donor's attack
  range until an appended attack state is proven (Unverified below).
- A humanoid behaviour donor copied with your own skeleton swapped in (original model, 118 bones, no twist bones) loads and idles
  [game]; set `RefTwistEnable 0` when there are no twist bones [inferred]; humanoid graphs run the identity additive `a000_009500`
  (2 frames) [code].

## 2. behbnd and hks

- Members: 7000300 project, 7000400 `Characters\c<chr>.hkx`, 7000500 `Behaviors\c<chr>.hkx` (wrapper), 7000501
  `Behaviors\c9997.hkx` (the real graph, copied verbatim from the donor). A behbnd with DS3-style member ids and no c9997 was
  rejected [game].
- `Characters`: rename; luaFiles lists `c<chr>`; clear foot / hand IK (donor bone indices are out of range for your rig);
  look-at / twist bones mapped BY NAME (Neck > Head; spine twist start / end - a rig with two spine bones needs
  `RefTwistSpineEnd = Spine1`, otherwise the donor's Spine2 becomes -1 and switches twist off); RefTwistEnable 0 when the source
  local axes differ from FromSoftware's. Read the staged behbnd back against the staged skeleton (0 unmapped references).
- Wrapper `Behaviors\c<chr>`: IK control modifiers off, GetHandleOnBone bone -1, look-at / twist modifiers off with bone -1.
- HKLib reads / writes project, Characters and wrapper; NR's c9997 needs a tagfile reader / writer that keeps the TYPE
  section (CustomManualSelectorGenerator has an extra `isBasePoseAnim` field HKLib does not know) [data].
- hks: copy the donor's `c<donor>.hks` verbatim as `action/script/c<chr>.hks` (the generic stub, ~35 KB, is identical for
  c2130 / c7510 / c7900 / c4820; the real logic and constants live in the shared `c9997.hks`: death 10000, stance break 8700,
  parry 8500, special damage 8060, being-thrown 11010 / 11060 / 11070) [data]. A helper chr whose behbnd names an hks must
  ship it [game].
- Editing an hks: clone an existing per-slot callback (`Event20002_onUpdate`: EventCommonFunction(id); on IsAnimEnd ->
  Fire("W_Idle")) changing only the name and the constant; round-trip byte-exact; when‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ inserting instructions update the debug
  metadata line count to the instruction count (a stale count crashed the game on approach: "Memory allocation request
  overflow") [game].

## 3. Slots, states, leaves

A playable slot is: a state in Attack_SM / EventSingle_SM / EventLoop_SM + a wildcard transition on `W_Attack<id>` /
`W_Event<id>` + a CustomManualSelectorGenerator (animId, offsetType 15) with hkbClipGenerator leaves named `aNNN_<id:06>` +
an hks callback. TAE entries without a state are dead [data].

**Append a state** [game for event states; attack states built and audited only]:
1. Append `W_Event<id>` / `W_Attack<id>` to eventNames AND eventInfos (clone a neighbour's entry).
2. Clone a donor state + its selector with stateId = max + 1, set animId.
3. userData = (donor.userData & ~0xFFFF) | ordinal, ordinal = index in the state array (the native fast path uses the low 16
   bits as that index) [code].
4. Clone the donor's wildcard transition (flags as the donor's) with the new eventId / toStateId.
5. Append-only writer: carry PTCH entries over, keep TYPE byte-identical, prove "undoing the additions gives the original
   DATA", PTCH audit MISSING 0. Install anibnd and behbnd together.
A transition NAME existing in c9997 is not enough: `W_Event30029` existed in c2130's graph with no bound state, and forcing it
did nothing until a state was appended [game].

**Append a variant leaf** (animIdOffset sets; colour / power / distance / mirrored variants) [game]:
1. Clone the selector's first leaf (`a000_<id>`): name `aNNN_<id>_hkx_AutoSet_00`, animationName `aNNN_<id>`,
   animationInternalId = len(animationNames).
2. Append the animation path (base path, prefix swapped) to stringData.animationNames; extend the selector's generators.
3. Keep mode / flags / playbackSpeed / crop / startTime / enforcedDuration / userPartitionMask equal to the base leaf.
Without the leaf the base clip and base TAE play silently (fire sets, take-off distances and jump travel all "did not exist"
until 65 leaves were added to 26 selectors).

**animIdOffset**: a SpEffect with animIdOffset N x 1,000,000 selects `aNNN_`. NpcParam spEffectID0 5400 = none; vanilla offsets
go up to 353M. Set the selector SpEffect >= 3 frames before the request; two offset SpEffects must never overlap (park fire-set
offsets during a flight that uses distance offsets). A TAE entry `aNNN_<id>` importing the base clip is enough for the data;
its rows must differ from the base only in judge / SpEffect / FX ids (variant timelines that never played drifted: old‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ turn
rates, early cancels - diff row by row before switching on) [game, data].

## 4. Forcing animations

- EMEVD Force Animation reaches only states with a bound `W_Event<id>` transition; damage states 8060 / 8700 (only
  `W_DamageExtraLarge` / `W_SABreak`) cannot be forced: copy their timeline into an event slot that imports their clip [game].
- Rotate Character with an animation id plays a single-shot event clip (vanilla precedent: common_func 9005800) [data].
- In-arena replacement: every id the vanilla arena script forces (e.g. 20029 / 30029 at fight start) must exist and be
  harmless in your TAE [game].
- The automatic turn route (Rotate with animation -1) can select generic 260xx motions your actor lacks: request an explicit
  id [data].

## Unverified

Appended ATTACK states (3018 / 3020 / 3039-style) actually playing in game; selector fallback for an unmatched offset (a tool
note says the native selector falls back to the LAST leaf, not a000); private c9997 with directional stance breaks; what
SpEffects 5980 / 14895 and JT71 do natively (kept from the donor because vanilla does).
