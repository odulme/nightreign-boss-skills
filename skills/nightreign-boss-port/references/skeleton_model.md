# Coordinates, skeleton, FLVER, materials, textures, dummies, cloth

Tags as in `SKILL.md`. Pipeline stage S2 (`boss_pipeline.md`). FLVER Editor / WitchyBND / texconv basics: skill `nightreign-modding`.
Route B (an original boss rigged in Blender): `original_model.md` - its coordinate conjugation, UV V flip, smoothing / vertex budget,
Master rebasing and naming rules complement this file.

## 1. Coordinates and facing

- NR characters face -Z (vanilla c2130 walk-forward root motion ends at z -3.42; toes at -Z of the ankle) [data].
- Y-up source facing +Z with left = +X (MHW, Relink): position (x, y, -z) x unit, quaternion (-qx, -qy, qz, qw); vertices and
  normals with S = diag(1, 1, -1). MHW unit 1/100 (cm) [game].
- The MAP transform of the same source is different (MHW arena: (-x, y, z) / 100, quaternion (qx, -qy, -qz, qw)), so MSB
  character yaw = map-asset yaw + 180. An MSB part with rotY t faces (-sin t, -cos t) [data].
- Prove handedness on an asymmetric feature (left-eye mesh at +X, expression bones per side, sword hand) [game].

## 2. Skeleton

- Master at index 0, identity, never animated. Parent < child, depth-first [game].
- Root: insert one after Master when the donor's IK / look-at needs it (humanoid on c2130); a dragon on c4510 with IK off ran
  with the source hip bone as the effective root and generic bone names (`b000..`) [game]. Parentless source bones (weapon
  mounts, ground anchors) become children of Master.
- Rename only the core humanoid bones the donor's look-at / twist uses (FromSoftware names); keep source names for the rest.
- Same engine family: keep the source skeleton and its reference pose; NR helper bones with a different ref pose do not matter
  when every bone has a track in every clip [data, game].
- Bone count: skeletons of 246 and 538 bones ran [game]; vanilla census of 277 characters: skeleton max 522, FLVER weighted
  max 489, one mesh max 386, 28 characters with >= 256 bones [data]. Every port that ran had <= 256 WEIGHTED bones: with the
  common UByte4 bone-index vertex layout weighted nodes must sit at indices 0..255; more‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ needs the UShort index layout (vanilla
  and one DS3 port precedent, not tested in a boss port) [data].
- Reducing weighted bones (if needed): merge bones without motion data (face expressions, hair) into their parent, then
  chains with tiny motion by measured error (p99 <= 1.2 cm over all frames). Make the merge deterministic (fixed hash seed:
  a set iteration produced two different FLVERs) [data].
- Binding: FLVER binds to the skeleton by NAME; clips and ragdoll mappers by INDEX. Append new bones at the END only; old clips
  keep playing through sparse track binding; align the physics anim-skeleton copy, mapper and hkxpwv bone count too; new clips
  fill appended bones with the bind pose [game].
- Skeleton hkx, two routes that worked [game]:
  - HKLib only: load a vanilla skeleton template + its compendium, replace bones / parents / reference pose, write standalone
    (no compendium reference); read back bit-exact as float32.
  - soulstruct-havok encoder (Blender's Python) then HKLib for the tagfile.
  Check with two independent readers and a TYPE-hash comparison against a vanilla standalone skeleton.

## 3. FLVER

**Template**: a vanilla FLVER for header fields, vertex layout and GX lists (c2130's worked for a humanoid AND a quadruped
dragon); rebuild nodes, materials, meshes, dummies and skeleton tables with SoulsFormats [game]. Keep one GX list.

**Vertex buffers**: one buffer per stream (Position F3, Normal UB4, Tangent UB4, BoneIndices UB4, Weights UB4N, UV Short4 / 2048).
The buffer row's first int is the STREAM number (SoulsFormats writes a running index: patch it). Mixed buffers + GXIndex -1
gave white areas, flicker and spikes [game]. UVs raw (no V flip) for sources already in DirectX convention (MHW, Relink); Blender
exports need `uv.y = 1 - uv.y` (`original_model.md` 8) [game]. Tangent T = dP/dv, sign w such that cross(N, T) . w = +dP/du.
After the (1, 1, -1) reflection keep the triangle order (the reflection already gives NR's winding); assert "against" winding
dominates (> 20 x) [data].

**Node table** [code, game]: [weighted bones][mesh nodes][dummy owner nodes][other bones]; second skeleton table (AllSkeletons)
depth-first and sorted on its own parents (vanilla keeps control / ragdoll parents that differ from Nodes - never copy the
Nodes tree into it); BaseSkeleton entry i = node i. Flags: bone 8 (listed by a vertex, has a bone-space box), mesh 4,
dummy owner 2 (attach bones also carry 2: 8 + 2 = 10), disabled 1; a weighted node satisfies flags & 9 == 8. A zero-mesh actor
with all flags 0 and an empty BaseSkeleton was unhittable [game]. Signature of the node-order bug: in 255 / 267 vanilla FLVERs
"first mesh node index = number of weighted bones" [data].

**Mesh bounding box**: Min = half extent, Max = 0, Unk = centre (OBB form) [game].

**Weights** [data, game]: <= 4 influences; least-squares fit of 4 influences over ~60 training poses (validated on others) beat
plain renormalisation (p99 2.8 cm vs 3.0-3.6 cm, max 15-18 cm); drop < 1.5 %; quantised sums 252-255 are normal (vanilla);
no zero-weight vertex (it collapses to the origin); vertices weighted to cloth-only bones must be moved to body bones when the
cloth is not simulated (2,582 vertices hung 2 m in the air). Weights on a few high node slots gave spikes in a player port;
moving them to other slots fixed it (cause unknown) [game].

**LOD face sets**: None = source LOD0; LodLevel1 = LOD0 again when the source has nothing near 60 %; LodLevel2 = source LOD1
(~14 %); LOD vertices appended to the same buffer [data].

## 4. Materials and textures

Route that worked for foreign sources [game]: generic `Chr_Base` matbins with texture paths in the FLVER, no allmaterial edit.

| material | matbin |
|---|---|
| opaque body, metal plates | `C[AMSN]` |
| alpha-tested (wings, hair, fur edges) | `C[AMSN]_e` (alpha test ~50 in NR terms; do not write DS3's 128) |
| eyes, heat states, glowing parts | `C[AMSN]_Glow[Int]` + emissive map |
| skin with subsurface look | vanilla SSS character matbins exist (`C[DetailBlend]_SSS`); plain AMSN loses the look [data] |

- Sampler names / order exactly as in the matbin; material names unique (a duplicate stopped a texture from loading);
  Material.Index = index of the first material with the same matbin; GXIndex 0 with a copied GX list [game].
- Texture maps:

| NR map | format (TPF byte) | content |
|---|---|---|
| `_a` | BC7 sRGB (102) or BC1 sRGB | albedo; alpha binarised at 128 for `_e` |
| `_n` | BC7 (106) | R, G = normal (flip G when the source convention differs), B = gloss, A = 255 |
| `_m` | BC4 (103) | metal (cloth / skin 0) |
| `_em` | BC7 sRGB (102) | emissive, kept DARK (peak ~0.35; NR emissive reads ~15 x the texture [inferred]) |
| `_l` twin | same formats | every texture at 1/4 size in `c<chr>_l.texbnd` |

- Normal-map green: decide by a curl test, not lore: corr(dR/dv, dG/du) had opposite signs for MHW (-0.30) and vanilla NR
  (+0.36..+0.42) -> flip; Relink and DS3 match NR -> no flip [data].
- Gloss from roughness: MHW B = 255 (1 - R / 255)^2 (heuristic calibrated on vanilla statistics); Relink mask R -> gloss,
  G -> metal, B (AO) 35 % into albedo; DS3 metal from `_r` by a spec / gloss solve [data].
- BC7 re-encode of cut-out alpha can break edges: refit endpoints only, keep mode / partition / indices [data].
- Glow strength DS3-style lives in the FLVER (GX item), not the material: bake it into‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the emissive map [data].
- Budget: largest vanilla Nightlord `_h` bundle ~32 MB; a faithful ported boss reached 55 MB (88 MB in GPU memory). Write only
  textures a material references; helper actors cloned from the boss must ship only their own textures (8 helper bundles
  227 MB -> 6.6 MB, 365 MB less per arena load) [data].
- An optional "NR-blended" texture set (albedo x0.8, saturation 0.88, darker AO) can ship as an alternative entry; keep the
  faithful set as default.

## 5. Display masks (parts, breaks, phases)

- Material prefix `#NN#` = mask group NN; NpcParam `modelDispMaskNN` = 1 for every group that should show at spawn [game].
  No prefix = always shown.
- Scheme that worked for a breakable dragon: intact / broken / heated copies of each breakable region as separate groups
  (chest plate intact / heated / broken / heated-broken, exposed flesh, heat-off / heat-on body, head intact / break 1 / break
  2, wings intact / broken, eyelids); EMEVD ChangeCharacterDispmask switches them [game for visibility].
- Phase-2 body in the same model: own groups; overlapping faces (a phase-2 face over the base face) hide together. A phase 2
  as a SEPARATE MSB enemy = exact NpcParam clone except the mask fields (vanilla Heolstor pattern) [game].
- Hiding a helper: scale 0.001 + all 32 masks off did NOT hide it; removing every face-set index (keep metadata, skeleton,
  physics) did [game]. Refined: that leaves meshes with 0 indices whose vertex data is never drawn (81 such meshes = 37 MB in one port's
  helpers); vanilla invisible helpers use a FLVER with **0 meshes** - prefer that form [data] (it did not cure a GPU hang by itself
  [game-MP]). Keep the node flags / BaseSkeleton valid: a zero-mesh actor with all flags 0 and an empty BaseSkeleton was unhittable,
  which matters only for helpers that must take hits.

## 6. Dummy polys

- Position / Forward / Up are MODEL-space bind coordinates (59 fire mounts written bone-local were off by up to 13 m) [game].
- ParentBoneIndex = owner node `Dmypoly_*` (planning / general / SFX / anim / death-cloud groups, `*_固定` = no attach bone);
  AttachBoneIndex = a bone node with flag 2; Unk30 = 3 x ordinal within its owner group; copy forward / up magnitudes, flags,
  colour per owner group from the donor; do not normalise the donor's short axes on mouth dummies [data, game].
- **A dummy with ParentBoneIndex -1 / AttachBoneIndex -1 is NOT at the model origin: the engine binds it to node 0**, which on an
  MHW-style skeleton is the animated hip (moves up to 3 m, tilts up to 74 deg; a helper's turn clip lifted its hip 21 m). Bullets
  spawned from such dummies rose as "staircases" of tilted plates 3-15 m up, helper rows 17-38 m up [model reproduced every report;
  game fixed]. **Parent every placement dummy to the fixed SFX owner node** (`Dmypoly_SFX_固定` in FromSoftware FLVERs): it is in the
  FLVER but not in the HKX skeleton, so it never animates; place floor dummies at Y 0.3 [game].
- New spawn points: clone an existing fixed-node dummy to a new id (e.g. a floor point under the mouth) - the reliable way to give a TAE
  bullet event a fixed floor origin [game]. For streams add a dummy along the source's breath joint (2.0 m along its axis = the source
  spawn offset) instead of the head / mouth dummy (`attacks_hits.md` 4.1) [game].
- Sample dummy heights over time (FK of the installed clips), never only the bind pose: lanes on dummies of an animated bone started
  ~43 m up [game].
- Ids < 1000 and unique (`id % 1000` in the getter; high ids aliased low ones and broke every attack) [code, game].
- Conventions to copy: 220 lock-on (222-228 multi), 200 hit / status surface (many, on vertices with weight >= 0.5), 960 death
  cloud (x15-18), 10 / 15 mouth / breath origin, 900 / 901 trace head / tail, 211 / 228 / 242-249 engine dummies [game].
- Generous counts are fine (445 dummies ran; Adel has 502). Plan blocks: fixed capsule ends, wave / line segments, ground FX
  points, blade hilt / mid / tip, points along a blade at 8 / 16 / 24 / 32 / 40 m [game].
- A dummy change is atomic across FLVER, TAE, AtkParam, Bullet: install anibnd + chrbnd + regulation together (a FLVER rebuilt
  without new dummies broke every judge) [game]; release pins must include the chrbnd. A fixed point not attached to an animated bone (e.g. "8 m in front") is a
  cheap anchor for ground effects that must not follow the head.

## 7. Weapons and cloth

- Weapons‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ held for the whole fight: rigid meshes on their mount bones inside the body FLVER, mount mapping proven by the
  source's own sync motions (constant weapon-root to mount offset); weapon bones flag 10 and node slots reserved early so
  adding them needs no reorder [game]. Weapons that fly independently: separate helper actors (`reactions_death_phases.md` 5).
- Cloth on a boss: the rigid route works (skin cloth meshes to their bones, ordinary matbin, no cloth members 700 / 1200)
  [game]. Ported cloth hkx: check operator order (an InputConvert before the operator that declares its buffer writes through
  a null / stale pointer on hitch frames; fix by moving it, `ds3-nightreign-port`) [code]. Real cloth needs Bitangent + second
  Position streams and a cloth matbin; custom cloth graphs do simulate (player ports) but need much tuning [game].

## 8. Props and culling

A bone-chain prop whose motion reaches far beyond its rest pose (telescoping drill, siege weapon) needs its FLVER header bounding
box enlarged to the whole motion, or the far tip is culled [game OK; culling reason inferred]. Prop clips: `animation.md` 11.

## 9. Cheap first look

A static, CPU-skinned idle pose placed as a map asset (map shader) in a separate preview entry checked size, placement and
textures before any character file existed [game]. Delete that entry once the real character loads.

## Unverified

UShort bone indices for > 256 weighted bones in a port; whether a 0-mesh helper FLVER needs anything else to stay hittable;
SSS matbins on a ported skin; NR emissive ~15 x texture; the `_n` gloss
formula (heuristic); alpha-reference scaling; bone-scale tracks hiding segments drawn as in the source (QS chain rule).
