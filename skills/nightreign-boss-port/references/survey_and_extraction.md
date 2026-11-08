# Survey, extraction, decoding, catalogue

Tags as in `SKILL.md`. Pipeline stages S0 / S1 (`boss_pipeline.md`; the rest of planning - decisions, diagnostics plan, shipping
configuration, id registry - is in its S0). Source-format facts below are [data] (decoded and checked against renders / known values)
unless marked.

## 1. Feasibility survey (do this before choosing a donor)

First run the released-source check (`SKILL.md` Step 0): an unreleased, leaked or unconfirmable source ends the survey
here, with a refusal.

Count, per source boss:

| item | why it matters |
|---|---|
| motions: total, unique after content hashing, with root motion, multi-block, cutscene / stage-anchored | library size; duplicates are stored once; stage-anchored clips need re-anchoring |
| per-motion speed curves (MHW `mMotionSpeed`, Relink speed timelines) | clip timing; ~4 % of MHW motions had them |
| skeleton: bones, weighted bones, parentless specials (weapon mounts, ground anchors), solver-driven helper bones | FLVER index format, bake step, retarget |
| meshes, LODs, break / damage groups, phase forms, separate face / weapon models | display masks, phase-2 body, merges |
| materials and maps (albedo, normal convention, roughness / metal, emissive, masks, virtual textures) | channel mapping |
| attack volumes: shape, units, half / full extents, attach bone, frames | hit sizes and timing |
| hurt / part data (part ids, weak points, break counts, HP) | hurtbox groups, part breaks |
| timelines per motion: attack windows, shells / projectiles, effects, sounds, flags | TAE rows |
| effects: format and count | convert or borrow (`fx_sound.md` 1) |
| sound: banks, codec, voice / SE split, music stems, trigger tables | bank build |
| AI: data (trees, pools) or code; node count; registers | AI route (`ai_port.md`) |
| numbers that live only in the source exe (damage tables, landing points, loop counts of a downed pose, tick damage, action -> motion table) | become explicit choices, asked of the tester |
| per-attack spawn geometry: spawn joint, shell life vs effect life, radius / growth, speed, re-hit interval, anchor (target / boss / floor), pattern extents | the per-attack data table (section 6); six fix rounds of one port were "aimed / anchored from the wrong place" |
| source mechanisms the tester may want "as in the source" (real lethal hits, cover / guard shadows, terrain-blocked fans, target-anchored rows, NPC lines) | survey early, present "source does X; we can do A / B / C" with numbers [game decisions] |
| official names (boss, phases, attacks, summons) in every language the game ships | NpcName / FMG in every language; machine translations differed from the official names |

What turned out to matter most (in this order of cost): the source clock (60 fps + speed curves), which motion plays which
role, root track vs body compensation, flight heights held by the source engine (not in the motion data), clip length,
donor graph slots, mirror flags.

Choose the full model variant: MHW ships a lightweight variant of some monsters (fewer meshes, no break groups, placeholder
textures) next to the real one - check break groups before choosing [data].

## 2. Keep the extraction read-only

- Extract EVERYTHING once (mesh, skeleton, all motions incl. cutscenes, timelines, attack / hurt data, AI, params, all sound
  banks incl. music, textures incl. streamed / virtual ones). Write a manifest with size + SHA-256 per file; check the source
  archive sizes / times unchanged afterwards. The source game may be uninstalled later: the extraction becomes irreplaceable.
- Never write into the extraction or the source install. Tools‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ that write next to their input (decompilers writing into the
  cwd, unpackers creating folders) run on copies. Verify against the manifest after every agent task; restore from the
  archive if something was overwritten [data: one sound table was overwritten by an agent and restored].
- Patch archives: take the latest patch chunk for every path (MHW: later chunks override earlier ones; a comparison against
  a stale chunk failed) [data].
- Keep vanilla NR extracts in a shared add-only folder.

## 3. Source families

### 3.1 Monster Hunter World / Iceborne
- Extraction: WorldChunkTool over all chunks in the tool's numeric order (needs an Oodle 8/9 DLL), validated by structure
  checks + sample hashes against another unpacker.
- Encrypted `.shlp`, `.dtt_eda`, `.dtt_epg`: Blowfish ECB with every 32-bit word byte-swapped before and after the cipher;
  keys as published with MHW-Editor.
- MOD3 model: bone record byte 3 = symmetric bone (255 on some wing bones: pair them by mirrored bind position < 5 cm and
  assert the map is an involution). Weights: 4-weight blocks = 3 x 10 bit / 1023, 4th = 1 - sum; 8-weight blocks = 3 x 10 bit
  + 4 bytes in 1/1023, 8th = 1 - sum.
- LMT v95 action header 0x60 bytes: fcurveOffset, fcurveCount, frameCount, loopFrame, end translation / rotation, flags
  (byte +64), flags2 (byte +67), timlOffset. Track record: buffer type, usage (0 local rot, 1 local pos, 2 local scale,
  3 root rot, 4 root pos), boneId (-1 = root), bounds `value = raw * mult + add`; each key stores the frame count to the next.
  Values are ABSOLUTE local transforms in cm; bones without a track keep the bind local; duplicate (bone, usage) records:
  the LAST wins.
- Public LMT parsers are wrong in several places (first key only of float root buffers, zeroed non-encoded components of
  single-axis quaternion buffers, wrong normaliser - correct is (v - 8) / (2^n - 16), chosen by quaternion unit-norm spread):
  write your own and verify by rendering against the source.
- TIML timelines are embedded in the LMT: 20-byte keys (value, two controls, frame, interpolation, easing); type hash =
  ~crc32 & 0x7FFFFFFF, property hash = ~crc32 (name dictionaries from community anim tools). Timelines that mattered:
  mMotionSpeed (clock), mTurnSpeed / mTurnAng (turn windows), mFlag (bit 0x10 "busy" cleared at the release point;
  0x1000000 = bipedal stance bit), EventGroup / EventCollision / EventLoop (sounds, footsteps), effect parameters.
- Attacks: `em###.col` capsules (radius in cm; ATK records = node order - 4); shells (`.shlp`, lifespans in SECONDS,
  collision radius, speed); motion values in col / shell `object.col` (damage transfer, `params_balance.md` 3).
- Textures: `.tex` via the community MHWorld tools (pick the mip <= 2048). Maps: BML albedo, NM normal, RMT (R roughness,
  G metal), EM emissive, XM effect mask. MRL3: raster nibble 1 = back-face cull; alpha test at 0.502.
- AI: THK (`ai_port.md` 1); difficulty / rage tables `em_difficulty.dtt_dif`, `.dtt_agr`.
- Sound: Wwise 2016 banks (v120) + `.wwev` request tables with variable-length path tails (a fixed-length reader drifted and
  picked wrong sounds).
- Units: cm, 60 fps (prove it: stride timing, roar audio vs clip length, a 90 / 180 deg turn = 121 frames = 2.0 s).

### 3.2 Granblue Fantasy Relink
- Extraction: GBFRDataTools (`list-files`, `extract-all -f <prefix>`, `extract -f`, `bxm-to-xml`, `tex-to-dds`,
  `hash-string`) on `data.i`; build the work list by filtering the file list (boss id, its weapons / face / effect prefixes,
  shared tables); loose sound banks copied separately. Empty placeholder entries (size 0) are not missing files.
- Virtual textures: GraniteTextureReader with the 64-bit hash from `.mmat` -> TGA.
- Model: `model/em/<id>/` (minfo, skeleton, sop, mmat) + streamed LOD meshes; the face can be a SEPARATE model to merge; phase
  forms can live in the same model. The‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ public Blender addon imports meshes only; its motion import is wrong: own decoder.
- `.mot` (Platinum mot v2): 0x2C header (flag != 0 = cutscene in stage coordinates); 12-byte records (i16 bone, -1 = root
  motion, else hex of the bone name; i8 property 0-2 translation, 3-5 Euler, 7-9 scale, 16 = 0..1 scalar; i8 interpolation
  1-8 incl. quantised Hermite / pghalf; key count; constant or offset); Hermite evaluation with pre-scaled tangents; hold
  first / last values; duration (F - 1) / 60; Y-up, faces +Z, character right = -X; Euler XYZ (R = Rz Ry Rx); absolute locals.
- `.skeleton` is FlatBuffers (parent < child); `.sop` = constraint solver for helper bones (twist share, swing / twist,
  slerp copy, angle-driven translation, Euler copy) reading LOCAL rotations of non-helper sources: one pass in file order;
  check by back-solving the rest pose (< 1e-5 deg). Helper bones can be PARENTS of weighted regions.
- Timelines: `*_seq_edit_{attack,effect,se,flags,speed,...}.bxm` -> xml; behaviour trees under `system/behaviortree/`.
  The move -> motion link is in the program, not the data: infer from SE / hitbox / camera names, mark confidence.
  Variants hang under a subtree gate (e.g. a hard-mode check) - port the subtree the tester wants.
- Sound: Wwise 2021 Vorbis 48 kHz (NR is 2019.2): strip only `cue ` / `LIST` chunks, no re-encode [game].
- Text: official names in msgpack tables `system/table/text/<lang>/text_battle.msg` and `text_chara.msg`; a minimal msgpack reader is
  enough. 4 of 13 machine-made Japanese names differed from the official ones; Traditional Chinese official names are not a character
  conversion of Simplified Chinese (several differ entirely) - let the owner choose, and say where the source has no row (a mod-only
  term) [data].

### 3.3 Same engine family (DS3, ER-era files)
Use `ds3-nightreign-port`. The method to learn conversion rules for any FromSoftware source: find a character FromSoftware
itself ported into NR (e.g. DS3 Dancer c5270 -> NR c7920) and diff the pair (bones, clip payload, TAE event types, param
fields, Lua API); carry what is equal, convert what differs.

### 3.4 Other engines (seen in player-model ports only)
Unreal titles: FModel (CLI); Unity: AssetRipper (its PNG export swaps R / B); PMX: Blender MMD Tools. Same discipline: own
read-back of every converted file against the source.

## 4. One clock for everything

Write the frame -> seconds mapping once ("clock contract"): `t = t0 + (f - a) / (60 x speed)` with the source speed curves
applied (constant / linear / standard easing implemented; unknown interpolation types REFUSE instead of guessing), used by the
clip sampler AND every timeline row (attacks, shells, effects, sounds, flags). Every rebuilt duration must equal the clip.

## 5. Labelling motions and the action catalogue

- Labels from action-name lists were wrong twice (death vs knock-down, both directions) [game]. Measure each candidate:
  duration, hip height over time, root motion, start / end pose distance to idle, and whether any motion starts from its end
  pose (none = a death). Show contact sheets and ask the tester, who often knows the source game.
- Directional families (0 / +-90 / 180 deg members chosen by the source exe from the target angle): decode the root as the
  game reads it and rebase on frame 0 before calling a member "0 deg" (a +180 member made a move fire backwards) [game].
- Action catalogue (one self-contained HTML; built from the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ INSTALLED files): stable ids never renumbered - A = NR slot,
  M = source bank:motion, S = encounter sequences (A20010 -> A30005 -> ...); skinned textured viewer, ~12 sampled poses per
  action, search / filter, root-motion view, id copy. The tester names moves by id; regenerate it whenever slot contents
  change (a stale catalogue mislabels death and set pieces) [game: used in every round].
- Before editing a move from a description, list its neighbours (variants, mirrored members, chain parts) from the catalogue
  and ask which one in plain words ("(a) stands, snaking flame, ends on all fours, or (b) drops first ...").

## 6. Per-attack data table (S1 exit gate)

One row per attack (and per shell / child), filled from the source data before any attack is built:

| column | why |
|---|---|
| move id (catalogue), source action / motion | ties every later fix to one move |
| spawn joint of each shell (MHW breath shells come from a separate breath joint, not the head) and spawn offset along it | streams aimed from the head missed the floor in front by metres (`attacks_hits.md` 4.1) |
| shell life vs effect life | a damage beam that outlived the shell sprayed 50 m ahead |
| radius, growth (R0 -> R1 over t), height, speed, gravity | circle and ray sizes, floor rules |
| re-hit interval / multi-hit settings, shared hit lists | one hit per 0.5 s etc. |
| anchor: to the target, to the boss, to the floor; pattern extents (e.g. +-24 m around the hunter, a line -12..+36 m through him) | rows "always at one place" vs player-anchored |
| line-of-sight / wall-stop data (ray-cast ids, wall end offsets), blocker collision | collision-aware fans and shadows |
| damage values, element, knock-back type, fixed-damage slots, special ids | damage transfer, certain-kill moves |
| clip speed multiplier that will apply in NR | divide every time by it (`tae_turning_windows.md` 10) |

Keep times on the clock contract (section 4). Numbers that live only in the source exe are marked as such and become questions.

## Unverified

Meaning of the MHW mFlag bit 0x10 ("busy") is inferred from its pattern (the result passed in game); which `flags2` bit marks
mirrored MHW aliases (bit 0 is set on every alias; another reading says 0x10); Relink sop D-type amplitude units; Relink
`.mot` property 16 meaning (physics blend).
