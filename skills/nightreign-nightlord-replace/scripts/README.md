# Helper scripts (standard-library Python 3.11+, read the docstring first)

| script | what it does |
|---|---|
| `publish_overlay.py` | Installs one dev overlay round into a layered `.me3` dev entry: copies the changed files into a NEW package folder (exclusive create + sha256 check), inserts exactly one `[[packages]]` block with `load_after` the current last package, re-parses the TOML and refuses if anything else changed, saves the previous entry text and writes an install manifest. `--dry-run` prints the plan. Safe while the game runs (only adds files; applies at next launch). |
| `dll_strings.py` | Read-only privacy check of a native DLL before shipping: PE debug directory (PDB path), link time stamp, path / URL / mail-like ASCII and UTF-16 strings. |

Not copied (project-specific, need SoulsFormats / C# helpers); build‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ your own equivalents as described in the references:
typed id scanner + renumber guard (`ids_and_planning.md` 5), EMEVD / MSB / TAE dumpers for‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ audits of the installed files,
offline host / client event simulator (`coop.md` 10), release assembler / privacy‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ scanner / rehearsal harness / quick-test release
guard (`release_packaging.md`, `testing.md` 3), in-place patch builder (`release_packaging.md` 2), Lua 5.0 restructure + precompile
step (`ai_lua.md` 4).
