---
name: nightreign-modding
description: "MUST verify the source game is publicly released before porting content from another game (web search; refuse unreleased, leaked or unconfirmed sources). 移植前必须先联网核实源游戏已正式发售，否则拒绝。制作《艾尔登法环：黑夜君临》(ELDEN RING NIGHTREIGN) 离线 MOD 的通用工作流：me3 包结构与加载顺序（后加载的包覆盖）、开发版分层叠加包、Smithbox 改 regulation.bin 参数（只改目标单元格、差量转移进发布版）、WitchyBND 解包/打包、FLVER 模型与 TPF 贴图替换（Blender → FLVER Editor → SoulsFormats 小工具修正 → 打包）、皮肤/武器战技等参数配方、FXR 特效只改数值槽、单元格模式构建器与发布回放、重活锁、分享前隐私扫描、证据标签、GUI 自动化坑、质量验收标准。用户提到 Nightreign/黑夜君临 MOD、me3、Smithbox、regulation.bin、partsbnd、FLVER、皮肤/服装/模型替换、参数移植、开发入口、叠加包、发布打包时使用；BOSS / 地图移植的深入内容见 nightreign-boss-port / nightreign-map-port / nightreign-nightlord-replace。English: Nightreign offline modding basics - me3 profile and package load order (later package wins), dev overlays, Smithbox params, regulation.bin cell edits and delta transfer, WitchyBND, FLVER / TPF replacement, skin and weapon-skill param recipes, FXR value-slot edits, cells-mode builders, privacy scan, evidence labels, GUI automation, QA standard."
---

# Nightreign modding (vanilla game is the reference)

## Step 0 - MANDATORY before any port: released games only

This step comes first, before every other step of this skill, and is never skipped, shortened or assumed already done.
Before you plan, research, extract, convert or brief anyone about porting a boss, character, enemy, model, animation, effect,
sound or map from another game:

1. **Verify with a web search** (WebSearch or any web tool you have) that the source game - for DLC / expansion content, that
   exact DLC - has been officially and publicly released and is commercially available. Do not rely on memory or on the
   user's word alone: release dates move. Write the title, the release date and the source you checked (publisher or store
   page, or a reputable outlet) into your reply or the plan.
2. **Refuse the port and explain why** when any of these is true:
   - the game or DLC is announced, in development, delayed or otherwise not on sale yet;
   - the material comes from a leak, a datamine of an unreleased build or update, a press / review build, or a beta or network
     test (under NDA or not) of a game that is not out yet;
   - the release status cannot be confirmed: no web search available, or only conflicting or rumour-level results. Then stop
     and ask the user to enable web search or to name an official source; do not continue on a guess.
3. **Allowed without a source-game check**: original bosses built from the user's own models and assets (or assets they hold
   the rights to), and work on Nightreign's own content (vanilla Nightreign motions retargeted onto an original model included).
4. The check is per source: repeat it for every new source game or DLC.

Example: a request to port the Thornveil Matriarch's armour set from a game that has only been announced is refused until the game is on sale, however complete the leaked files look.

## Responsible use

- Free, non-commercial mods only. Never sell, paywall or bundle‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ for sale anything that contains another game's assets (models,
  textures, animations, effects, sounds, music, text), and do not help anyone do so.
- Respect the EULAs and terms of service of the source games and of Nightreign; extract only from copies the user owns; credit
  the source game and its rights holder when a port is shared.
- Offline only. Modded Nightreign runs through me3 with Easy Anti-Cheat off and its own save file; never take modified files
  onto the official online service or matchmaking (EAC; bans are possible). Co-op in this skill set means the Seamless Co-op
  mod, which plays outside official matchmaking.

## About this skill

Boundary: offline, free, non-commercial mods only. Launch through me3 (not the EAC launcher; offline + own save file); **never
"take mods online / dodge EAC"**: modded play is me3 only, co-op only through the Seamless Co-op mod. For visual work (skins, models)
the owner is the final QA: show renders / data of every version first and install into the game only after an explicit OK. Dev
patches that pass their own offline checks may go into the dev profile without a separate audit; anything for other people gets one
audit + one re-check (section 6).

Depth lives elsewhere: bosses (port or original) `nightreign-boss-port` (pipeline S0-S12); Nightlord fights, co-op and releases
`nightreign-nightlord-replace`; maps / arenas `nightreign-map-port`; DS3 content `ds3-nightreign-port` (these two are companion skills, not included in
this repository).

## 0. Tools and work area (install as needed; paths depend on the user's machine)

- **me3**: mod loader; a `.me3` profile (TOML) launched by double-click or `me3 launch -p <file>`; >= 0.10.1 for `load_early` and a
  loader fix.
- **Smithbox** (nightly, Nightreign GameType = 15): regulation.bin params, texts, Model Editor.
- **WitchyBND**: DCX / BND4 / TPF unpack and repack (`-p` passive mode: a file unpacks, a folder repacks).
- **FLVER Editor** (the asasasasasbc fork with NR support): FLVER <-> DAE / FBX.
- **Blender 4.x** (headless scripts): modelling, weights, UV, check renders.
- **texconv** (DirectXTex): DDS encode / decode.
- **SoulsFormats helpers** (this skill's `scripts/*.cs`, compiled with the .NET Framework csc, each needs a same-named `.exe.config`
  binding SoulsFormats.dll): flverkeep (face-set cull flags / mesh cropping / material mapping), flverdiag (bbox / zero-weight checks),
  flverbones (bone table), flverdump (FLVER -> JSON).
- Optional: Nuxe (full bhd / bdt unpack), DarkScript3 (event scripts), UXM.
- Suggested layout: `<workspace>/<ModName>/` (me3 package), `<workspace>/vanilla/` (vanilla regulation.bin backup), `<workspace>/work/`
  (unpacked files and intermediates, on a large drive), `<workspace>/tools/`.
- When reverse-engineering someone else's pack, read a copy only; never edit the original.

## 1. me3 package structure (one mod = one folder)

```
MyMod/
  MyMod.me3          # profileVersion="v1"; savefile="MyMod.co2"; start_online=false
                     # [[supports]] game="nightreign"; [[packages]] id="MyMod" source="./mod"; [[natives]] path="./natives/x.dll"
  mod/               # mirrors the game's folder layout: regulation.bin, parts/*.partsbnd.dcx, msg/zhocn|engus/*.msgbnd.dcx, param/...
  natives/           # DLL mods (optional; ordered with load_early / load_after)
```

- An own `savefile` keeps the real save clean. Several `[[packages]]` overlay each other: **when two packages ship the same relative
  path, the later-loaded one wins**; the me3 log prints one `override=<path>` line per served file - the proof of which copy is live (no
  line = never requested). me3 resolves relative paths from the profile's folder [data].
- A profile whose later package carries a whole older regulation silently undoes every regulation change before it: keep exactly one
  merged regulation per profile [game].
- Dev profiles stack one package per change (section 6). Release profiles carry only release packages.

## 2. Param changes (Smithbox)

- Changes reach `mod/regulation.bin` only after **Save**; back up first; strip trial rows from a release.
- Common tables and recipes: [references/params.md](references/params.md) (the six skin tables, porting a weapon skill's
  Behavior / Atk / Bullet chain).
- Texts (GoodsName / GoodsInfo etc.): Text Editor or same-id entries in the msgbnd; ship every language you support.
- GUI-automation traps when driving Smithbox: [references/gui-automation.md](references/gui-automation.md).
- Scripted regulation edits (no GUI) and how releases take them over: section 6 and [references/workflow.md](references/workflow.md) 3.

## 3. Model / texture replacement (partsbnd)

Full pipeline and‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ traps: [references/model-pipeline.md](references/model-pipeline.md). Backbone:
1. `WitchyBND -p x.partsbnd.dcx` unpacks to `X-partsbnd-dcx/` (FLVER + TPF + anibnd + `_c.hkx / _c.clm2` cloth).
2. FLVER Editor exports DAE / FBX (bones, weights, two UV sets) -> Blender scripts for modelling / weights / UV (Blender Z up, facing
   -Y; FLVER is Y-up).
3. Back in: Blender FBX export (**bake every object's world transform into its mesh and parent it to the armature first** - FLVER
   Editor ignores node transforms) -> FLVER Editor `Import Model` (bone conversion unticked) -> `Modify` writes the file -> delete the
   original meshes + map the imported materials back (flverkeep `--empty` / `--remap`) -> cull flags per material (`--nocull` /
   `--cull`) -> `flverdiag` check -> `WitchyBND -p` repacks the TPF and the partsbnd -> into `mod/parts/`.
4. Textures: `_a` BC1 sRGB (`-f BC1_UNORM_SRGB -srgb -m 0`), `_n` BC7 (R / G normal, **B = gloss**, A = 255), `_m` BC4 (metalness,
   cloth = 0).
5. Attach a new part to a hero: a new `EquipParamProtector` row with equipModelId = model number -> referenced by `CharaInitParam`
   -> the skin's goods / shop rows (params.md).

## 4. Hard rules (traps already hit)

- **Vanilla clothing face sets have CullBackfaces = false (double-sided)**; meshes imported by FLVER Editor default to cull = true ->
  every gap shows the background. Face-material meshes keep culling.
- Zero-weight vertices collapse to the origin in game; non-bone vertex groups are exported as bones -> before export keep only bone
  groups, <= 4 influences, drop < 1.5 %, renormalise.
- Cloth physics (`_c.hkx`) deforms display-mesh vertices, it does not drive [Cloth] bones; a custom mesh cannot get physics; reusing
  a vanilla physics mesh requires its vertex order (faces may be deleted, UVs changed).
- Linear-skinning seat / crotch as vanilla does it: the leg mesh reaches up to the hip joint, thigh 100 % until ~12 cm below the hip,
  then a smoothstep to the pelvis; the top's hem follows the pelvis rigidly and covers it; the hem sits on the waistband without a step.
- Check renders with materials as in game: double-sided, normal strength 1.0; procedural macro wrinkles do not go into the normal map
  (they read as blotches in game).
- Acceptance: the numbers of [references/QA_STANDARD.md](references/QA_STANDARD.md) + an agent score; agent instances vary by about
  +-3 points, so above 85 the owner's in-game look decides.
- FXR effects: edit only float value slots in place - never counts, offsets or node links (a 2-byte structure edit froze the game
  although every offline proof passed); never round-trip a vanilla FXR through a writer. Details: `nightreign-boss-port`
  `references/fx_sound.md` 1 / 11.
- Do not state vanilla mechanics deduced from menus or params as fact; mark them [inferred] and ask an experienced player.

## 5. Common commands

```
WitchyBND.exe -p <file-or-dir>                      # unpack / repack
flverkeep.exe in.flver out.flver --info | --cullinfo | --nocull 0,1 | --cull 3 | --empty 0,1 | --crop idx:z0:z1 | --uvskirt idx | --remap prefix_
flverdiag.exe x.flver                               # per-mesh bbox (Y-up) / zero weights / vertices near the origin
flverbones.exe x.flver [--all]                      # bone name / parent / translation / referencing vertex count
flverdump.exe x.flver out.json                      # vertices / triangles / weights -> JSON
csc.exe //nologo //r:SoulsFormats.dll //r:System.Numerics.dll //out:x.exe x.cs   # needs x.exe.config
blender.exe -b -P script.py -- <args>               # headless
texconv.exe -f BC7_UNORM -m 0 -y -o out -ft dds in.png
```

## 6. Universal dev / release workflow (details: [references/workflow.md](references/workflow.md))

1. **Evidence labels on every claim**: [game-MP] > [game] > [code] > [data] > [sim] / [model] > [inferred]; four report states -
   built / installed and read back / owner saw it work / owner accepted. Offline checks find causes, they never prove a fix.
2. **Dev overlays**: one change per package in a NEW folder, appended to the dev profile with `load_after` = the previous top; install
   guards (game closed - ignore 0-thread zombie processes -, expected top package, verified stage hash, target folder absent, profile
   backed up); never overwrite an installed or staged folder; delete your own superseded entries in the same step. Dev-only debug
   packages sit LAST and never ship.
3. **Dev first, then pack**: a change is confirmed in the dev profile before it goes into any release; features that skipped this
   failed in releases.
4. **Cells-mode builders**: each builder asserts its base and edits only its own cells / FXR slots / events at their exact old
   values, refuses otherwise, writes only changed files and ends with PASS / FAIL + an independent read-back. Outputs then stack in any
   order and the same builder replays on release inputs ("release probe": byte-identical result, or a proof that the dev‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ build read the
   pinned inputs).
5. **Regulation**: planned cell / row edits on the decrypted BND; write back only the PARAM members you changed (never re-serialize
   untouched, possibly name-stripped tables; prove untouched members byte-identical); compare decrypted content (each write gets a new
   IV) or re-encrypt with the input IV for reproducible builds; releases take the dev row delta onto the previous release (delta
   transfer); watch the decompressed size limit (79,293,432 B crashed at
   boot; stay below 78,838,728 B, a size known to boot) [game].
6. **Heavy steps**: one shared lock file for heavy builds across agents; no free-RAM threshold (an invented ">= 3 GB" rule stalled
   agents); a lock older than 60 min may be taken over, so long steps refresh it every 5 min.
7. **Disk hygiene**: large intermediates on a large drive; delete reproducible side copies, experiment outputs and editor backups
   (Blender `*.blend1`); deleting anything outside your own scratch needs the owner's approval per group; report every deletion.
8. **Before sharing anything**: privacy scan of every file incl. DLLs, Lua constants, logs and readmes (paths, user names, private
   links, nicknames) with a positive control; dev content (quick-test entrances, probes, debug DLLs) never in a release.
9. Agents never launch the game, never touch saves or the live me3 folder; the owner plays and runs installers.
