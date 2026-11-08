# Nightreign Boss Skills

**English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

Claude Code skills for making bosses in ELDEN RING NIGHTREIGN as offline mods: porting a boss from another, publicly released
game, building an original boss from your own model, and turning either one into a Nightlord fight. They were distilled from
ports and builds that reached real play, and they keep only the methods that worked in game. The notes are written for people
who would rather read a frame table than guess.

> Unofficial fan project. Not affiliated with or endorsed by FromSoftware, Bandai Namco or Anthropic.

## What the skills do

| skill | covers |
|---|---|
| `nightreign-boss-port` | The boss itself, as a 13-stage pipeline (S0-S12) with an exit gate per stage: survey and extraction, an original-model route (rig, retargeted vanilla motions), donor behaviour graphs, FLVER and dummies, hurtboxes, root motion and TAE (heading hold, turn / re-aim windows), a dev-only move debug panel, hit carriers (breaths, mines, fans), effects and sound (value-slot edits only, GPU budget), precompiled Lua AI and the AI heap, HP benchmarks, part breaks, co-op and a pre-release checklist. |
| `nightreign-nightlord-replace` | A boss as a new or replacing Nightlord: fight event scripts, the switch item ("last crush wins"), kill credit, names in every language, BGM slot, HP-ratio phases, balance against the vanilla Nightlords (Seamless Co-op HP formula, 4-6 players, Deep Night), co-op sync (host director / client follower), testing and release packaging (pins, delta regulation, installer, upgrade patch, privacy scan). It owns stages S8-S12. |
| `nightreign-modding` | The shared base the other two build on: me3 profiles and load order, layered dev overlays, Smithbox and regulation.bin cell edits, WitchyBND, FLVER / TPF replacement, param recipes, FXR value-slot edits, cells-mode builders, privacy scan, evidence labels and a QA standard. |

Each skill is a `SKILL.md` plus `references/` (read on demand) and a few small helper `scripts/`. Claims carry evidence tags
(`[game-MP]`, `[game]`, `[code]`, `[data]`, `[sim]`, `[model]`, `[inferred]`) so you can tell what was seen in game from what
was‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ only reasoned out. Engine facts were found on Nightreign 1.3.3.0 (regulation 10350000); re-check them after a game patch.

The skill bodies are mostly English, the descriptions are Chinese + English (so they trigger in either language), and a few
`nightreign-modding` references are in Chinese.

Two companion skills are referenced but not included: `nightreign-map-port` (arenas, map blocks, collision, navmesh) and
`ds3-nightreign-port` (Dark Souls III recipes). The skills here work without them; those topics are simply not covered.

## The hard rule: released games only

Every skill begins with a mandatory **Step 0**, also wired into stage S0 of the boss pipeline. Before any work on porting a boss,
character, enemy, model, animation, effect, sound or map from another game, the model must:

1. use web search to verify that the source game, or the DLC that contains the content, has been officially and publicly
   released and is commercially available, and write down the evidence (title, release date, source checked);
2. **refuse** the port and explain why if the game or DLC is unreleased (announced or in development), if the material comes
   from leaks, datamines of unreleased builds, or betas / network tests (under NDA or not), or if the release status cannot
   be confirmed.

Original bosses built from your own models and assets are allowed without this check. Please keep this rule if you fork or
adapt the skills.

## Requirements

- **Claude Code** with skills support, and web search enabled (Step 0 needs it).
- **ELDEN RING NIGHTREIGN** on PC (a copy you own), plus a copy you own of any released source game you port from.
- **me3** (mod loader, 0.10.1 or later), **Smithbox** (params, texts), **WitchyBND** (unpack / repack).
- Depending on the task: **FLVER Editor** (a Nightreign-capable fork), **Blender** 4.x, **texconv** (DirectXTex),
  **SoulsFormats** with the .NET Framework 4.x C# compiler (for the small C# helpers), **Python** 3.11+, a **Lua 5.0.2**
  compiler (`luac50`) for AI scripts, **DarkScript3** (event scripts), **Seamless Co-op** (only for co-op testing).

## Install

Copy all three skill folders into your Claude Code‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ skills folder (the boss skills refer to `nightreign-modding`):

```
git clone <this repository> nightreign-boss-skills
cp -r nightreign-boss-skills/skills/* ~/.claude/skills/
```

- Personal skills (every project): `~/.claude/skills/` (on Windows `%USERPROFILE%\.claude\skills\`).
- Project skills (one project only): `<your project>/.claude/skills/`.

Start a new Claude Code session afterwards. The skills load from their descriptions when you ask about Nightreign bosses,
Nightlords or modding, or you can name them directly ("use nightreign-boss-port").

## Responsible use

- Free, non-commercial mods only. Do not sell, paywall or bundle for sale anything that contains another game's assets
  (models, textures, animations, effects, sounds, music, text).
- Respect the EULAs and terms of service of the source games and of Nightreign; extract only from copies you own; credit the
  source game and its rights holder when you share a port.
- Offline only. Run modded Nightreign through me3 with Easy Anti-Cheat off and its own save file. Never take modified files
  onto the official online service or matchmaking: Nightreign uses Easy Anti-Cheat and bans are possible. Co-op in these
  skills means the Seamless Co-op mod, which plays outside official matchmaking.

## License

Everything in this repository - the documentation and the Python / C# helper scripts alike - is licensed under the
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International** license (CC BY-NC-SA 4.0). Copyright (c) 2026
odulnme. The full legal code is in [LICENSE](LICENSE), and [NOTICE](NOTICE) has the short version:

- **Attribution** is required ("Nightreign Boss Skills by odulnme", a link to the original repository, the license, and
  what you changed).
- **No commercial use**: selling, reselling, paywalling or bundling this material, original or modified, into paid products
  or services is not permitted.
- **ShareAlike**: adaptations must use the same license.

Because of the non-commercial term this is a source-available license, not an OSI-approved open-source license. No game files
are included, and the license does not cover any game content.

## Credits

- Skills written and maintained by **odulnme**.
- ELDEN RING NIGHTREIGN is developed by **FromSoftware**; the game, its content and trademarks belong to FromSoftware and
  **Bandai Namco Entertainment**. Example‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ source games named in the skills belong to their owners as well (Monster Hunter: World - Capcom;
  Granblue Fantasy: Relink - Cygames; Dark Souls III - FromSoftware).
- Tools these skills rely on, with thanks to their authors and contributors: **me3** (garyttierney), **Smithbox** (vawser),
  **WitchyBND** (ividyon), **SoulsFormats** (TKGP), **FLVER Editor** and its Nightreign fork (asasasasasbc), **DarkScript3**,
  **Seamless Co-op** (LukeYui), **Blender** (Blender Foundation), **DirectXTex / texconv** (Microsoft), **Lua** (PUC-Rio).
- The FromSoftware modding community, whose shared research and documentation made this work possible.

## Disclaimer

This is an unofficial fan project with no affiliation with FromSoftware, Bandai Namco, Capcom, Cygames, Anthropic or any of
the tool authors. All trademarks belong to their owners. The skills and scripts are provided as is, without any warranty.
Modding can break saves and, if modified files are taken online, lead to bans: back up your saves and use the skills at your
own risk.
