# Release packaging: additive installer, fingerprint, upgrade patch, rehearsals, privacy, readme

Tags as in `ids_and_planning.md`. The tester (and other players) run installers by double-click; agents build and rehearse on scratch
copies only and never install into, or run validation on, the live me3 folder. (In the Claude desktop app, writes into AppData
may be redirected into a private container anyway [inferred].)

## 1. Installer: self-contained, additive, side by side

Release folder:
```
一键安装.cmd  指定位置安装.cmd  卸载.cmd  指定位置卸载.cmd   (or English names)
说明.txt  manifest.json
installer\Install.ps1  installer\Uninstall.ps1        (Windows PowerShell 5.1; UTF-8 BOM + CRLF)
payload\<packageDir>\mod\...   payload\<packageDir>\natives\...   payload\<new profile>.me3
<zip> + <zip>.sha256                                  (a local .build.json with local paths is NOT shipped)
```
- Each .cmd: `chcp 65001`; if `installer\Install.ps1` is missing print "extract the whole zip first" and exit 1; else
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...Install.ps1 %*`; pause; return the exit code.
- manifest.json: product, title, version, builtFrom (build tag), built, gameBuild {timeDateStamp, sizeOfImage}, fingerprint,
  packageDir, packageId, baseProfile {name, textSha256}, newProfile {name, sha256}, installedBytes, files [{path, sha256, size}],
  runtimeFiles [globs], userFiles [globs], savedSettingsDir, sideBySide [{label, product, packageDir, profile}], baseFiles [{path,
  sha256, role}], mustBeAbsent [paths], regulation {decompressedBytes, budget, version}. Globs: `*` / `?` never cross `/`,
  case-insensitive. The rules live in manifest + receipt only; the scripts hold no file names.
- Install flow: hash every package file -> locate me3 (`-Me3Root`, default `%LOCALAPPDATA%\Programs\garyttierney\me3`, or ask the
  user to drag the folder) -> game build check (PE TimeDateStamp + SizeOfImage of `nightreign.exe`, found through Steam or asked)
  -> base profile text hash (tolerate CRLF / BOM / trailing blanks), every baseFile hash, mustBeAbsent (no pack package provides
  one of our paths) -> game-process check, disk space, 260-character path limit -> stage into a short-named `.<abbr>_<8hex>`
  folder in the me3 root with a `.lock`, verify, move into place -> write the receipt `installation.json` -> print the fingerprint.
  Any failure withdraws everything.
- Refusals, each ending "nothing was changed": not an me3 folder; wrong game build; exe not found; a pack file changed or missing;
  base profile edited; a pack package provides one of our files; game running; our folder / profile exists with other content;
  another build of the same version installed ("uninstall it first with THIS package's uninstaller"); link / junction on the me3
  side. Re-running the same install = no-op that re-prints the fingerprint (runtime files ignored, user files may differ).
- Uninstall is receipt-driven: removes files with unchanged content + runtime files; copies an edited user file (e.g. a DLL ini) to
  `<me3>\<Mod>_settings_backup\` first; keeps and lists unknown files (exit 2); asks for confirmation (Enter = cancel); falls back
  to the package file list when the receipt is unreadable. A newer package's uninstaller removes any older build.
- Side by side: another add-on's folder + profile are only looked at (existence + receipt version), never written. The new profile
  = base profile text + our natives (`load_after = [{id = "nrsc.dll", optional = false}]` when the pack has its own loader DLL)
  + one package block that `load_after`s every pack package; same savefile / start_online as the base. No version in folder or
  profile names (upgrades keep the entry).
- Fingerprint: `<name> <version> (<builtFrom>) | GAME <ts>/<size> | FILES <first 8 hex of sha256 of sorted "path:sha256" lines +
  profile line> | SC <first 8 hex of the pack loader DLL>`. Every co-op player compares it before a session (it does not cover
  other packages in the player's profile).
- Game-running check: ignore `nightreign.exe` processes with 0 threads (kernel-held zombie after a crash, only a reboot clears it;
  check `Win32_Process.ThreadCount`). Change Install, Uninstall and‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ Patch together.
- Path pitfalls: check reparse points only on the me3 side (the package side may be a OneDrive extraction: tell people to extract
  to a plain folder); short staging names (MAX_PATH); `TrimEnd('\')` turns a drive root `<drive>:\` into `<drive>:`; a quoted path with a trailing
  backslash through the .cmd breaks parsing; clean stale staging folders next run, never one with a journal or a link.
- Windows `tar.exe` (code page 437) skips entries under a Chinese-named top folder: use an ASCII top folder in the zip. Give each
  build's zip a build-specific name.

## 2. In-place upgrade patch

- Every release = full package (new installs) + a small patch zip (`升级.cmd` / `指定位置升级.cmd`, readme, manifest = the
  target's, `patch.json`, `installer\Patch.ps1`, payload = carried files + profile). Rule: any supported older build becomes
  EXACTLY a fresh install of the new one, same entry.
- `patch.json`: product, kind "patch", toVersion, toBuiltFrom, toFingerprint, targetManifestSha256, fullZip, carried [{path, sha256,
  size}], supported [{version, builtFrom, files, replace, add, remove}]. Match old builds by builtFrom, not version number.
- **Accept exactly ONE previous build** (the previous release: built-from tag + zip hash + file hashes) [data]. Its base files
  must be a subset of the new build's; game build, base profile, runtime files and the saved-settings dir unchanged; new user
  files only if absent in the old build (a `mustBeAbsent` list, enforced by the patch script). Test matrix: reference install;
  upgrade from the previous build == fresh install of the new one (added files included); uninstall; negative cases (wrong
  base, modified file, game running, partial / interrupted); the live game folder untouched.
- A content-identical file recompressed by a pack step (DCX_KRAK output is not byte-deterministic) changes the fingerprint and
  must then be carried: better, never recompress unchanged files; re-encrypt regulations with the input IV when a build must be
  reproducible [data].
- Per file (T = target hash, R = receipt hash, D = disk hash): D = T leave; D = R and T differs replace; D = R and not in T remove;
  absent, not in R, in T add; anything else refuse everything. User files: replace only an untouched default. Runtime files: skip.
- Commit: write a journal before the first rename; move the launcher profile out first and back last (a half-patched copy cannot
  be started); the receipt is the last file. The next run rolls an interrupted journal back only if every file is in a state the
  journal explains, else touches nothing (exit 3, "use the full package"). Exit codes 0 / 1 / 3. Flush staged files before the
  journal (power-loss gap).
- Build checks: functions shared with Install.ps1 compared by PowerShell AST; .cmd files byte twins of the installer's; every
  message quoted in the readme exists in the script; per-target change text (an audit caught a patch readme with the previous
  release's text).

## 3. Rehearsals (scratch only)

- Scratch me3 = READ-ONLY copy of the live base profile + base files under a path with spaces and CJK characters; a 4 KB exe stub
  carrying the real PE header; LOCALAPPDATA pointed at an empty folder; `-Me3Root <scratch>` on every run. Snapshot the live me3
  folder before / after: identical.
- Installer suite (35-50 cases): validate-only writes nothing; install; re-install no-op; uninstall restores the exact tree;
  every refusal; failure while copying / before the final move withdraws all; one-click auto-detect; junctions; stale staging;
  unreadable receipt; long / trailing-backslash paths; concurrent install. Fault injection by redefining functions or aliases in a
  `-Command` prefix (fake `Get-Process`, corrupting copy, lock on 2nd call); injected code must survive `Set-StrictMode 2`.
- Full-size rehearsal of the REAL zip: testzip, members = folder, validate -> install -> hash every file against the manifest ->
  parse the profile -> re-run = already installed -> add a log + edit the ini -> still already -> uninstall saves the ini ->
  scratch equals the original.
- Scenario rehearsals as players really are: a player with the other add-on at an old version (installed by ITS installer), a
  player with nothing, a player with the newest other add-on, the developer with an older build + edited ini + logs (refuse ->
  this package's uninstall -> install), the same with the quick-test kit installed. Patch tests: from each supported old build the
  result equals a fresh install; failures and kills at each rename; hostile journals.
- Keep >= 2x the package size free on the build drive.

## 4. Three-way merge of shared files (pack build)

- Own paths (nobody else ships them): whole file, listed in mustBeAbsent. Shared paths: merged = theirs (the pack's effective file =
  last-loaded package's copy, else vanilla) + (ours - vanilla); refuse on double edits, id collisions or a changed base row; record
  the base hash in baseFiles.
- Regulation: copy our rows raw; assert ParamType / DetectedSize match; untouched tables byte-identical; keep THEIR version string
  (a pack may be on an older regulation version); strip row names after merging; decompressed size under the known-bootable budget
  (a slightly larger file crashed at boot); whitelist the rows / ids that ship (dev regulations hold abandoned trial rows).
- EMEVD: ours + their changed events + an instruction-level merge of event 0. MSB: theirs + our entries. msg: theirs + our
  entries. Menus: free cells only. Wwise: their objects + ours (children before parents), replaced node only.
- Do not ship files whose only additions are debug objects. Build on the pack's own hub / arena files, never on vanilla.
- When the other mod's input changes: point the chain at its release through environment variables, plus a consistency guard
  before the first step that stops on any mismatch (hub inputs, readme text, built-from tag).

## 5. Privacy and residue scan

- Scan every shipped file (text, recursively decompressed DCX, DLLs) as ASCII + UTF-16 (+ GBK for CJK) for drive paths, user
  names, workspace names, e-mail, private links, wording about the author's own computer, dev / test markers, abandoned-content keywords. Read the
  private pattern list at run time and never ship it. Positive control (a planted hit must be found); test CJK patterns in UTF-16
  explicitly (a scanner missed some).
- AI scripts: comment-free precompiled bytecode. DLLs: build without `/DEBUG` (PDB path), check the PE debug directory and
  path-like strings (`scripts/dll_strings.py`); without `/Brepro` a rebuild changes the hash: ship only the tested binary.
- Hand out only the zip + `.sha256`; build json / evidence files hold local paths.
- Patches: pass the previous reviewed‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ patch's hits as inherited and require 0 new; public boss names in strings are accepted;
  chance UTF-16 matches inside binary data are recorded as weak; keep the positive control [data].

## 6. Release chain (one command, resumable)

A mod side (effective set -> real-expedition events -> id move + guards -> music -> Lua precompile -> moves) -> B hub verify +
simulate -> C merge on the pack + read-backs -> D payload + checks (provenance complete, no shadowing of an unmerged pack file,
no settable test flag) -> E spec + assemble (zip, `.sha256`, fingerprint) -> F privacy scan + full rehearsal -> G rebuild the
quick-test kit on the release's own files -> H release guard on folder + zip + positive control. `--from <step>` resumes (a full
chain takes ~30 min and can hit time limits); `--final` refuses while readme placeholders remain. Zip: stored unless deflate
level 1 shrinks the first MiB by >= 10 %, ZIP64, testzip, UTF-8 name flag. Then the upgrade patch: make -> scan -> test.

## 7. Readme (audiences first)

- Top: who you are -> what to do (only the other add-on, any version -> install directly; an earlier build of this package ->
  this package's uninstaller first, or the upgrade patch; neither -> install). The patch readme lists the supported builds.
- Body: what it is (offline, non-commercial, private; sources and pack authors credited); prerequisites (working base profile,
  unmodified pack / game, the same package for every co-op player); back up the save (shared with the base entry); extract fully
  to a plain folder; which .cmd; check the "installing to" line; how to read the fingerprint again; how to play (item, merchant,
  "no item = vanilla"); co-op rules and honest limits (confirmed in co-op vs offline only, party sizes tested); known limits;
  uninstall; refusal messages explained; "after a game or pack update: uninstall and wait for a new build".
- Never promise behaviour the build does not keep (an audit found an unverified "both entries are interchangeable").
- **Say per change what was tested**: "tested solo" / "co-op checked offline only" / "4+ players not tested yet" / "not specially
  tested"; review readme claims against the agent reports before shipping; remove stale lines (e.g. "only tested in co-op once").
  Shipping an untested item is the owner's explicit, labelled decision [data].
- Generate the "what changed" text from a per-target file (a patch readme still carried the previous version's hard-coded text).

## 8. Release from a layered dev stack (pins, delta regulation, replay)

Pipeline stage: S11 of `nightreign-boss-port/references/boss_pipeline.md` (gate: the release vs dev field compare differs only by
named dev-only rows). Order per feature, with the dev-first rule: `testing.md` 1.
- **Probe and debug packages never reach a release**: build them behind `--probe` / dev flags, mark them NEVER PACK in the state
  file, and never run the pin generator while one is installed. The debug-panel package and its DLL
  (`nightreign-boss-port/references/debug_panel.md`) never ship; **the pinning tool refuses a profile or pin list that names them**
  [data].
- **Pins**: the release takes, per path, the top-most file from an explicit list of dev packages, read from a COPY of the dev
  profile without the debug / probe blocks (refuse a profile that still names them). The guard refuses any change vs the
  previous pins other than the expected paths and any package outside the naming scheme; pass scratch pins explicitly for dry
  runs so a "newest pins" picker never sees them. Map-side changes (MSB, collision binders, navmesh, asset geometry, msg binders,
  chrbnd) must be in the pins - list them at install time [data]. Pin every upstream input by sha256, even when it is
  byte-identical to the last release.
- **Base-chain proof**: follow every top-most dev file back through the builders' manifest `base_sha256` records to the previous
  release's pin; no link may pass through a probe or debug package [data].
- **Regulation by delta transfer** (the dev regulation carries probe rows - 18 key-item probe rows once): release = previous
  release regulation R0 + exactly the row delta D0 -> D1 (D0 = the regulation the first new dev builder read, D1 = the top-most
  dev one) + release-only cells. Checks: every changed row in R0 equals D0's; every new id absent from R0; untouched tables
  round-trip byte-exact. Acceptance: release vs dev differs only by the named dev-only rows and release-only cells. This replaced
  chained per-version release probes, one of which had 9 Bullet rows built on the wrong base [data].
- **Cells-mode builders**: each builder asserts and edits only its own cells / FXR slots / events at their exact old values plus
  the member's expected content (`--base-check cells`) and refuses otherwise, so outputs stack in any order and the same builder
  replays on release inputs. If the dev builder read exactly the pinned files (prove by input hashes), the dev output IS the
  release output; otherwise replay it on the pins and require byte identity (release probe) [data].
- **Release-only switches** (drop dev markers, probes): run both modes on the same input and diff; expect surprises (one switch
  changed 2 cells per row - FX id and posture - not 1) [data].
- Merge allow-lists per version: a pack merge refused a new BehaviorParam_PC row outside the allowed id patterns; every new param
  table / id band needs an allow-list entry and every new local flag an entry in the id checker's allow-list. Watch the
  regulation size budget (headroom reported per build) [data].
- After each release build, diff it against the previous release: the changed-file list must equal the intended list, and param
  changes are proven by reading the regulation back (only the intended cells) [data].
- Joint packs with another mod's pending release: run the full chain as a stand-in dry run on its previous release ("DRY" in the
  built-from tag), delete dry-run outputs, and make the real build a mechanical re-run once the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ tester confirmed in dev AND the
  other mod's release is staged; if the other owner's session is not running, hand it a self-contained note (inputs, expected
  hashes, readme lines) [data].

## 9. Versions, folders, live-folder checks

- **Version strings vs substring matchers**: a joint-pack generator selected its input pin by `'X_v1.8.1' in folder_name`, which
  also matches `X_v1.8.10`. Never use a version that contains an earlier one (skip to 1.9.0) or match exact tokens with
  delimiters; also add the new version to every other place that lists versions (a tuple that decided the expected event count
  fell back to an old number) [code]. Folder-name-keyed pins need a new branch per release.
- Live-folder "changed" false alarms: NTFS updated two directories' st_size (0 -> 65,536 / 8,192) with unchanged mtime and
  contents after a read or while the game started; compare file hashes and directory mtimes, not directory sizes [data].
- Distribution facts [data]: me3 >= 0.10.1 needed (load_early + a loader fix); the co-op mod's own launcher loads no file mods,
  so its players still need me3; a per-component installer = per-component packages (own files never overlap) + one prebuilt
  glue package per combination (shared files merged per combination) + a generated profile; regression = "all components"
  equals the classic build file for file.

## 10. Disk, locks and shared tools during a release round

- Disk per round: full release (folder + zip) ~2.3 GB, patch 0.2-0.4 GB, pins store ~0.3 GB; keep >= 2x the package size free;
  delete reproducible side copies before the patch test; keep pinned inputs. Deleting anything outside an agent's own scratch
  (old releases, work dirs) needs the owner's approval per group; report every deletion [data].
- Heavy-step lock: one shared lock file for heavy steps across agents, no free-RAM threshold (an invented ">= 3 GB free" rule
  stalled agents and was never the owner's); a lock older than 60 min may be taken over, so long steps refresh it every 5 min.
  A PowerShell child (the BND writer) once died with empty output at low free RAM: re-run once [data].
- Shared-tool edits: back up every edit next to the original (`*.before_<round>`); copy a round's tools into a new per-round
  folder instead of editing last round's [data].

## Unverified

me3 `load_after` resolution for a second overlay that also ships regulation; a runtime warning after a game patch (DLLs disable
themselves silently, me3 keeps loading the old data files); power loss inside the patch commit.
