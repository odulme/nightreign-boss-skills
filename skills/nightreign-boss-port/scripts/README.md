# Helper scripts (Python 3, no dependencies, read-only on their inputs)

| script | use |
|---|---|
| `wwise_fnv.py` | Wwise short ids (FNV-1 32 of the lower-case name) for `play_c<id>` / `play_s<id>` / `stop_...` events, state names, bank names: `python wwise_fnv.py --event c 123400100`, `python wwise_fnv.py _CL_Reserved03`. Checked against a known state id. |
| `lua50_lint.py` | Token-level check of an AI Lua script for constructs Lua 5.0 rejects (`#`, `%`, `goto`, `//`, bitwise ops, leveled long brackets, `...` outside parameter lists, methods on string literals), non-ASCII bytes and path-like string constants (they survive precompiling). Prints a main-chunk size estimate. Confirm with `luac50 -p`. |
| `heading_model.py` | Offline heading model of one attack clip from its TAE 224 rows, JT7 windows, NpcParam default rate and clip root yaw: rotation before the first hit, max deg/s, mouth sideways speed, heading error at each hit, for several target bearings and a strafing player. `python heading_model.py --example` prints an input template. Use it to compare TAE variants (`references/tae_turning_windows.md` 6), not as proof. |

Run Python with `-I` when‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ the input folder holds untrusted files.

Each helper‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ only reads its inputs and prints what it finds; treat
the‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ output as a lead to check in game, never as proof.
