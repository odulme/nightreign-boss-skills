# Universal dev / release workflow for Nightreign mods

Applies to every kind of mod (skins, params, maps, bosses). Tags: [game-MP] confirmed in a real multi-machine session, [game]
confirmed in game by the owner / tester, [code] static RE of the exe, [data] read from files, [sim] / [model] offline simulation or
model, [inferred] reasoning only - in that order of strength. Placeholders: `<MOD_ROOT>` work tree, `<GAME_DIR>` game folder,
`<DEV_PROFILE>` the layered dev `.me3`, `<PACK>` a joint pack shipping several mods. Deeper versions: `nightreign-boss-port`
`references/boss_pipeline.md` 4-6, `nightreign-nightlord-replace` `references/testing.md` and `release_packaging.md`,
`nightreign-map-port` `references/testing-packaging.md`.

## 1. Evidence and report words

- Put an evidence tag on every claim; resolve conflicts between sources by that order; keep [inferred] items [inferred] until a test.
- Four report states, never merged: built -> installed and read back -> the owner saw it work -> the owner accepted it. A new in-game
  counter-example overrides every earlier PASS.
- Mark inferred engine semantics as guesses; never present a vanilla mechanic deduced from params or menus as fact - ask an
  experienced player.
- Label untested items honestly in readmes ("tested solo", "co-op checked offline only", "4+ players not tested yet").

## 2. me3 profiles, load order, dev overlays

- Profile = TOML: `profileVersion`, `savefile` (own save), `start_online = false`, `[[supports]]`, `[[packages]]` (id, source,
  `load_after`), `[[natives]]` (DLLs, `load_early` / `load_after`). Relative paths resolve from the profile's folder. me3 >= 0.10.1
  needed for `load_early` and a loader fix; Seamless Co-op's own launcher loads no file mods, so co-op players still need me3 [data].
- **Later package wins per path** (case-insensitive); the me3 log's `override=<path>` lines prove which copy was served; no line =
  never requested [data].
- **Dev profile**: one consolidated base -> overlay 1 -> overlay 2 ..., each `load_after` the previous one. One change per overlay, in
  a NEW folder (the folders are the rollback history). Merge overlays into a new base now and then after a stack compare (the computed
  effective set equals the installed stack). Name every overlay so that a stranger could roll it back at three in the morning.
- **Install guards** (a script, not by hand): refuse when the game runs (a `nightreign.exe` with 0 threads / 0 handles is a kernel-held
  zombie, not a running game - only a reboot clears it), when‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the stage hash is not the verified one, when the current top package is
  not the expected one, when the target folder exists; append exactly one block, re-parse the TOML, copy with exclusive create + hash
  check, back up the old profile text, write an install manifest. Rollback = remove the block or restore the backup.
- Game running: adding NEW files (a new profile, package folder, DLL name) is safe; overwriting a file the running game loaded waits
  for the game to close or goes to a new name.
- Never edit installed or staged files in place (stagings are often hard-linked); build a copy, verify, then rename over.
- **Dev-only packages** (debug panels, probes, quick-test entrances, visible markers): built behind dev flags, named `..._DEBUG` /
  `..._PROBE`, marked NEVER PACK, kept LAST in the dev profile and rebuilt when a file they copy changes below them; a release step that
  sees one refuses. Nobody uses debug profiles on a co-op day.
- Delete your own superseded entries (and their package folders once the game is closed) when a new entry replaces them; entries of
  other lines of work: ask first.

## 3. Builders, regulation, FXR

- **Every builder**: deterministic; inputs as arguments; writes only changed files into its own output folder (path guard refusing
  release / stage / pins / app-data paths); ends with PASS / FAIL + check count; an independent read-back proves that only the named
  lines / cells / members / slots changed; negative controls (the previous bad file must still FAIL the new check). Never edit a
  verifier until it turns green; add assertions for the new contract. A generator first rebuilds the previous version byte-identically
  before applying its edits.
- **Cells mode**: a builder asserts its own base and edits only its own cells / FXR slots / events at their exact old values plus the
  member's expected content, and refuses otherwise. Outputs from several builders (or agents working in parallel) then stack in any
  order, and the same builder replays on the release inputs.
- **Release probe**: if the dev builder read exactly the pinned release inputs (prove by input hashes), the dev output IS the release
  output; otherwise replay the cells-mode builder on the pins and require byte identity.
- **Regulation editing**:
  - plan edits as `{table, id, field, value}` cell sets and `{table, id, clone_of, fields}` new rows; private rows only (clone a vanilla
    row to a new id and repoint your caller; never edit a row the game or other mods share); keep tables sorted by id (binary search);
    diff every clone field by field against its source (inherited fields bite);
  - decrypt, edit only the PARAM members you change, write back; untouched members stay byte-identical - do not re-serialize untouched
    (possibly name-stripped) tables through a paramdef writer; prove it member by member;
  - compare decrypted content (each write normally gets a new container IV); re-encrypt with the input file's own IV (first 16 bytes)
    when a build must be reproducible;
  - HP / balance retunes are anchored cell patches (old value asserted), never a regeneration of a whole table or event;
  - strip editor row names and dev / probe rows before shipping and measure the decompressed size (a hard limit exists:
    79,293,432 B decompressed crashed at boot with a "network message param missing" panic; 78,838,728 B is known to boot) [game].
- **Delta transfer for releases**: release regulation = previous release regulation + exactly the row delta between the regulation the
  first‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ new dev builder read and the top-most dev one + release-only cells. Checks: every changed row in the previous release equals the
  dev base; every new id is absent from the previous release; untouched tables round-trip byte-exact. Acceptance: release vs dev differs
  only by named dev-only rows and release-only cells.
- **FXR**: byte copies with in-place float value-slot edits only (prove: target slots found, bytes differ only inside them, inverse
  restores the source, every other member byte-identical); never change counts, offsets or node links (a 2-byte unlink froze the game
  although every offline proof passed); never round-trip a vanilla FXR through a writer (one writer reproduced only 27 of 110 FXRs of a
  binder) [game, data].
- **Lua AI**: bytecode binders (first byte 0x1B, stripped, source `=(none)`) pass through every pack step untouched [data].
- **Version strings**: never use one that contains an earlier one (1.8.1 vs 1.8.10 - a substring matcher picked the wrong input);
  update every place that lists versions [code].

## 4. Releases and patches (short form)

- Pins: per path the top-most file from an explicit list of dev packages, read from a COPY of the dev profile without debug / probe
  blocks; a guard refuses changes vs the previous pins other than the expected paths and packages outside the naming scheme.
- Base-chain proof: every top-most dev file traces back through the builders' recorded input hashes to the previous release; no link
  through a probe or debug package.
- Release-only switches (drop dev markers): run both modes on the same input and diff - expect surprises.
- Upgrade patches accept exactly ONE previous build (fingerprint + file hashes), carry a `mustBeAbsent` list for new user files, and pass
  a test matrix (reference install; upgrade = fresh install incl. added files; uninstall; wrong base, modified file, game running,
  interrupted; live game folder untouched). Do not recompress unchanged files (some DCX compressors are not byte-deterministic). Compare
  file hashes and directory mtimes, not directory sizes (NTFS changed two directories' size fields without any write).
- Readme / patch notes generated from a per-target file; review readme claims against the reports before shipping.

## 5. Heavy steps, agents, disk

- **Heavy-step lock**: one shared lock file for heavy steps (big BND / Havok / render builds) across agents; no free-RAM threshold (an
  invented ">= 3 GB free" rule stalled agents and was never the owner's); a lock older than 60 min may be taken over, so long steps
  refresh it every 5 min. A child process (e.g. a BND writer) that dies with empty output at low free RAM: re-run once [data].
- Agents work in their own folders, copy tools instead of running them inside read-only projects, back up every shared-tool edit next
  to the original and copy a round's tools into a new per-round folder; they never install, never launch the game, never touch saves or
  the live me3 folder.
- Stopping a background shell task may not stop a multi-step chain script it started: check the process list / log afterwards.
- **Disk**: large intermediates and extractions on a large drive; a full release (folder + zip) of a big pack ran ~2.3 GB, a patch
  0.2-0.4 GB; delete reproducible side copies before‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ patch tests, experiment outputs, and editor backups (Blender keeps `*.blend1` next to
  every save); keep pinned inputs and source extractions (often irreplaceable). Deleting anything outside your own scratch needs the
  owner's approval per group; report every deletion.

## 6. Before sharing anything

- **Privacy scan** of every file you ship or post (incl. DLL strings, Lua constants - bytecode keeps string constants -, logs, ini,
  readmes, patch scripts): local paths and drive letters, user names, e-mail addresses, private links, nicknames of people or projects,
  machine names. Keep a positive control; for patches, pass the previous reviewed set as inherited and require 0 new hits; public game /
  boss names are fine; record chance UTF-16 matches inside binary data as weak. Neutralise developer paths in sources BEFORE compiling.
- Build DLLs without debug info paths; ship only the binary that was tested.
- Dev content (quick-test entrances, debug panels, probes, trace DLLs, dev saves) never in a release: a guard scans the release folder
  and the zip (file names, kit strings in UTF-8 / UTF-16LE / GBK, non-release save files, dev ids in EMEVD / FMG / params).
- Rehearse every audience's install on a scratch me3 folder; the owner and players run installers themselves.
- One audit + one re-check for anything that goes to other people; none for dev patches that passed their own checks.
