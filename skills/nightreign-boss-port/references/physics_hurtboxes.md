# Hurt capsules, physics hkx, part groups, part rates, movement capsule

Tags as in `SKILL.md`. Pipeline stage S2 (`boss_pipeline.md`).

## 1. What is what [data, game]

| thing | file / field | role |
|---|---|---|
| hurtboxes | physics hkx in the chrbnd (member 300): keyframed ragdoll capsules | what player attacks hit |
| part groups | `.hkxpwv` (member 500): one group + flags per ragdoll body | NpcParam `partsDamageRate1..8`, weak flag -> `weakPartsDamageRate`, NPC part HP, additive hit layers |
| movement capsule | NpcParam `hitHeight / hitRadius / chrHitHeight / chrHitRadius` | walking collision, AI distance (`GetMapHitRadius`) - NOT the hurtbox |
| player-vs-boss push | NpcParam `chrHitGroupAndNavimesh 5` | players collide with the ragdoll capsules (Ancient Dragon pattern) |

## 2. Build route that worked [game]

1. Template = a vanilla physics hkx with the SAME body count and constraint count as you need (winged large boss: c4800,
   60 capsule bodies / 59 ball-and-socket constraints; humanoid: c7900, 16 bodies / 15 constraints / 2 mappers; DS3-like:
   c4373). The count must match because step 4 transplants the type section.
2. Geometry: per body one capsule along its anim bone; skin points = vertices whose dominant bone is in the body's bone set,
   projected inside the segment; radius = p85-p95 distance to the segment (clamp e.g. 0.3-3.0 m on a 40 m dragon; humanoid
   max(r_max, r95 + 3 cm)); maxAllowedPenetration 0.33 r; constraint pivot = origin of body A's anim bone.
3. HKLib fills the template object graph (`build_physics` script refuses another topology) and writes the hkx.
4. Repairs (mandatory for every HKLib-written hkx) [code]:
   - hkRelArray fix: move each referenced item directly after its owner object, 16-byte aligned, in member order, and register
     the field in PTCH under its own type. Missing entries leave the raw item index in the field; the convex-shape fix-up then
     runs an aligned SSE compare on a misaligned address -> crash at exe+0x1A11B59.
   - TYPE‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ transplant: copy the TYPE section of the vanilla template verbatim; refuse unless the type lists are identical except
     hash and alignment (HKLib also drops the high alignment bits of hkpConstraintAtom, 0xF010 -> 0x10). Missing THSH hashes
     crash at exe+0x182AC83.
   - PTCH audit MISSING 0 / UNHASHED 0 and an offline loader emulation ("would fault" 0). Fail the build on any non-zero.
5. Ragdoll body names may stay the template's (a head body named after a pelvis worked): binding comes from the anim -> ragdoll
   mapper (body j -> its anim bone, identity aFromB). Only 3 mapper fields change when you re-parent one body.
6. Write the hkxpwv yourself (SoulsFormats cannot read NR's).

A "pack only" rebuild step in a pipeline may skip physics: rebuild physics whenever geometry or bones change [data].

## 3. Payload and file layouts [data, checked against all vanilla capsules]

- hknpCapsuleShape: a.w = R, convexRadius = 0.99 R, inner box half size 0.01 R, 8 vertices with W = float(0x3F000000 + i),
  planes [p, -q, q, -p, -d, +d], index pattern `2,6,4,0,1,5,7,3,1,0,4,5,7,6,2,3,3,2,0,1,7,5,4,6`. Cached radius =
  convexRadius / 0.99; hkHalf16 = the upper 16 bits of a float32.
- hkxpwv v2: header i32 version 2, u16 unk0, u16 n1, u16 n2, u16 n3, zero padding to 0x20; then n1 x 4 B (count = bodies),
  n2 x 8 B (count = anim bones), n3 x 16 B (count = bodies). 16-byte body record: i32 -1, u8 group, u8 flags (0x09 = weak
  head, 0x10 = wings / limbs), u16 0, u8 0xFF (0x14 on some vanilla wings, meaning unknown), zeros.
- Converted SOURCE capsules (same family) convert exactly; keep NR's memOffsetToAngleOffset 160 [data].

## 4. Part groups (c4510 scheme, worked for a dragon) [game for hits]

31 head (weak, flags 0x09), 8 neck, 1 chest (unused by the donor, free for a chest break), 10 body, 5 / 4 left / right foreleg,
3 / 2 left / right hind leg, 9 tail, 12 / 11 wing arms, 7 / 6 wing membranes (flags 0x10). Groups 1-12 also select the
additive hit layers PartBlend_Add1..12 (anims 9100-9174); 9090 = the weak-part group 31 - the boss's hit reaction therefore tells
which part was hit (better than a position box; `params_balance.md` 9). NPC part HP, carriers and breaks: `params_balance.md` 7-8.

**Capsule damage type -> NpcParam rate** [code: CSEnemyDamageModule vt[4] 0x43fa20 -> 0xe952e0]: the capsule's damage-type nibble =
(hkxpwv dword +4 >> 8) & 0xF; 1-8 -> `partsDamageRate1-8`, 9 -> `weakPartsDamageRate`, 0 -> none; one rate per hit. NpcParam
`partsDamageType` (+0x13a) = 0 applies the rate only to attacks with AtkParam `isArrowAtk` (+0x7e bit 5). A `partsDamageRate` on a type no
capsule carries does nothing (the Ancient Dragon donor row's partsDamageRate1 2 was dead). Vanilla Nightlords: weakPartsDamageRate 1.3 +
partsDamageType 1, nothing else above 1.0 [data]. The rate scales HP damage AND part damage alike (`params_balance.md` 7).

## 5. Sizes that worked

- Hurt capsules must stick out of the movement cylinder, or short weapons cannot reach them: keep `chrHitRadius` below
  `hitRadius` (e.g. 0.45 vs 0.6) so capsules protrude 0.2+ m [game].
- Large flyer: +25-45 % radius by region (head +45, proximal neck +40, chest / forelegs / wing edges +35, body / hind legs / wing
  arms +30, tail +25 %; max +0.56 m); keep the distal neck small so it does not cover the head weak point. After that, bows‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ hit
  the flying body and melee / fireballs connected [game].
- Hovering humanoid (body ~0.9 m above the entity root): re-parent ragdoll body 0 from Pelvis to Root (which never tilts) and
  make it a vertical column r 0.70 from 2 m below to 0.25 m above Root; head stays a small weak point (~0.18 m, upper half
  exposed). Complaints "hard to hit" stopped [game]. Side effect: baked vertical travel lifts the column, so high moves are
  unhittable (accept or design for it).
- Same-family rigs: fit, never copy (source rigs 2-49 % longer per bone); the fit rule fails predictably on two-bone necks
  (head capsule above the skull), reversed pelvis frames, plate armour (lateral factors 2.8-3.3) and zero-length scale-hidden
  segments (give them no body). Wings, tail and horns without a capsule do not register hits [data].
- Coverage metric for pictures and reviews: % of body vertices within 10 / 20 cm of a capsule (an in-game pilot sat at
  86 / 91 %) [data]. Render capsule pictures with every install that changes them.
- **Coverage check before anybody grows capsules** ("the head breaks too slowly" is usually not a hitbox problem) [data]: pose the
  installed skeleton at each logged hit (animation + time since entry x TAE speed; try the previous clip in the first 0.5 s for
  blends); signed distance of the hit to every capsule; first capsule along eye -> hit and eye -> skull rays; mesh coverage = share of
  vertices whose dominant bone is in the part's subtree that lie inside a part capsule. One dragon's head was 99.6 % covered (3.3x the
  source's head volume; the source covered 65 %), median hit distance -0.002 m: slow breaks came from balance and a trainer, not from
  capsules. Gate for the show build: >= 95 % per part [model].
- Route B (original model): build the physics hkx from a donor physics template with capsules measured on YOUR body (column placed by
  world offsets, limited head radius), then the repairs and audits of section 2 and a convex fault simulation [game: hits land].

## 6. Movement capsule and ground behaviour

- Take `hitHeight / hitRadius / weight / moveType` from a vanilla character of similar size (Ancient Dragon 14.1 x 7.0, moveType 9)
  [game]. A source's own movement capsule may be smaller than the body (DS3 Winged Knight 2.3 x 0.6 for a 3 m body): parts
  then poke through‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ door frames; that is the source's choice, not a port error [data].
- `isUnduration 0` when foot IK is off, else the body tilts from one contact normal and jitters on bumpy ground [code, game].
- Inherited stand-in fields bite: `hitYOffset 0.8` floated a ported flyer [game]. Diff every cloned NpcParam row against the
  source.
- NR has no vertical root motion for the entity: in flight the entity stays on the ground and the body is raised inside the
  clip, so only ranged attacks (and enlarged capsules) reach a flyer [game]. Keep JT8 / JT132 out of ordinary flight clips.

## Unverified

hkxpwv byte b8 meaning; whether aligning physics / hkxpwv to appended bones is REQUIRED (it was done, never isolated);
directional stagger with converted original source capsules; NpcParam sound / hit distance fields on very large bosses; hit capsules
along a telescoping tail (on the hidden layer bones?).
