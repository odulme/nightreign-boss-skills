# Switch item: "crush it in the hub and the expedition's Nightlord fight becomes the mod boss"

Tags as in `ids_and_planning.md`. Vanilla ids: NR 1.3.3.0 / regulation 10350000. Placeholders: `<GOODS>`, `<MARKER>`, `<REQ_x>` ...

## 1. Data recipe [game unless marked]

- **Goods**: clone EquipParamGoods **1290** (Starlight Shards: refCategory 2 -> SpEffect 501290, goodsUseAnim 65, isUseNoAttackRegion
  1). Keep isConsume 1 (isConsume 0 with refCategory 2 = no use, no marker). isDrop 1 (dropped goods stay on the ground for
  anyone, as vanilla), maxNum 1, isDeposit 0, sellValue -1, refId_default -> your marker. cast / fire effects -> your crush FX.
- **Marker SpEffect**: minimal clone of 501290 with effectEndurance 1.0, changeMpRate 0, replaceSpEffectId -1, vfxId -> your
  crush look. It is applied at the crush frame (~0.63 s) and never by a drop. **Detect use ONLY by the marker**; inventory-count
  detection misfired on drops.
- **Crush FX**: colour-only clones of vanilla 302220 / 302221 (+ 301052 / 302223 afterglow) in `sfx/sfxbnd_m12` with a private
  wrapper id.
- **Icon**: a 160 x 160 sprite `MENU_ItemIcon_0<icon>` in a free cell of `SB_ItemIcon_DLC01_0` in `menu/21_common_dlc01_{h,l}`
  (check cells used by other mods).
- **Texts** in 4 languages (zhocn, zhotw, engus, jpnjp): item_dlc01 GoodsName / Info / Caption; menu_dlc01 EventTextForMap notices
  ("target is now X", "nothing changed"). zhocn may come from zhotw by character conversion, then checked (mod-own texts only:
  names of source-game characters come from the source's official localisation, `fight_script.md` 5). Include every item text id
  in the id x language audit before each release.
- **Acquisition = the hub (Spirit Tree) merchant, never a ground pickup**: a ground pickup with a full item‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ bar silently loses
  the item. The hub merchant runs `OpenRegularShop(2000, 2999)` [data]; field merchants use other ranges. Add one ShopLineupParam
  row in 2000-2999: clone of 2001, equipId = goods, value 1 rune, sellQuantity 1, eventFlag_forRelease 0, eventFlag_forStock =
  your counter flag (vanilla limited rows use 90100-90700; check other mods), list position. Clear the stock counter in your
  hub bootstrap at every arrival (engine reset not proven). Purchase in a real expedition worked.
- No confirmation prompt: the engine GoodsDialog is unproven (every NR goods row has -1) and an EMEVD dialog during the use
  motion is auto-cancelled [sim]. The crush is the commit.

## 2. Choosing the protocol

| situation | protocol | evidence |
|---|---|---|
| exactly one mod item in the profile | **one-way latch**: first crush -> network flag + host heartbeat; gate waits <= 1.5 s for the host decision | [game-MP] 3 players routed correctly |
| several mod bosses / items | **last crush wins** (below) | [game] single machine; protocol [sim] |

## 3. "Last crush wins" protocol (hub m12 script; one generator writes it for all items)

| piece | runs on | does |
|---|---|---|
| bootstrap | event 0 of the hub | clear own stock counters, local commit / snapshot flags, stale "holding" flags; start the others |
| use detector per item | every machine, sync off | `IF own player has <MARKER_x>` -> network `<REQ_x>`, kept ON until acknowledged, re-sent every 3 s |
| arbiter | host only | one request per pass -> current target `<T_x>` (new ON, then old OFF), acknowledge |
| heartbeat | host only | re-publish `<T_x>` every 1 s |
| notice | every machine, sync off | on a change of its own copy of T: "target is now X" once; the crusher whose crush changed nothing gets "nothing changed" |
| gate commit | edited vanilla 12002001 / 12002099, at the vanilla condition | set local COMMIT + a copy in an m10-block flag; a crush after the own commit never counts; remove unused items |
| host decision | host, commit + 1 s, re-sent every 2 s | network `<D_vanilla>` / `<D_x>` |
| routing | gate events (waits wrapped in sync off / on) | wait <= 1.5 s for D, route by D; else by own last T; extra label "vanilla routing by Targeting Boss" |
| arrival | arena decider / own block | branch on the gate decision, never on load |
| clean-up | m10 event at every Roundtable load | clear protocol flags, markers, buffs, leftover items, weather, every SpEffect the fight left |

- Stock: one of each item per player per hub arrival -> any crush order converges to the last acknowledged request; same-frame
  tie -> the request that changes the target wins.
- Your gate GOTO on a positive decision overrides `Targeting Boss 7 / 8 / 9`, so DLC / Heolstor targets can be redirected too.
- A client whose signal the host never saw must still follow the host decision when it arrives [sim].
- Limits: host leaving in the hub; latency above ~1.5 s plus a crush in the last 2 s. Player rule for co-op: crush at least 5 s
  before the gate, everybody sees the notice, then go through together (written in the readme).
- A host heartbeat that never stops can leak a stale route into the next expedition: stop it at the fight start and make the
  Roundtable clean-up repeatable [inferred].
- Signals survive hub -> arena: hub-block (12xxxxxx) and Roundtable-block (10xxxxxx) flags are readable in the arena scripts [game].

## 4. Joint hub with another mod's boss (that mod is released and must not change)

- Generate ONE hub script for all items on the pack's own hub files (pack‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ variants of 12002000, extra warp points), never on
  vanilla. Each mod keeps its own goods, marker, stock flags, shop row, texts, FXR and Roundtable clean-up event.
- **Shim** instead of editing the other mod: the joint hub additionally writes the signals the other mod's shipped arena script
  already reads (its commit flags at gate commit; its "redirect" / "vanilla" decision flags from your host decision; its local
  fallback flag + party buff on each machine's copy of its target). Never write its one-way latches.
- If your boss lives in its own block while the other mod's arena script stays loaded: the other mod's decider must NOT build
  anything for your decision. Patch a COPY of its arena script at build time (a few instructions: wait term for your decision,
  GOTO to a new label that starts only the arena's end + credit events, releases its arrival guard, END), anchored on the
  expected file hash and refusing on any difference (`fight_script.md` 8).
- Ownership table in the coordination file: protocol events and network party state (joint generator), each item (its mod),
  gate events (joint generator), the other decider (other mod; patched copy only in the joint build).

## 5. Co-op hygiene for every hub event

- `Set Network Sync State(0)` as line 0 of every per-machine watcher / notice / guard.
- Host decisions as a host term INSIDE the waited condition (`IF Player Is In World Type(0)`), then `SKIP IF client` behind it.
- All waits bounded (grace 1 s, host <= 1.5 s, settle 1 s). Never FadeToBlack / Freeze in the hub near the gate.
- Party buff icons‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌ for the signal: optional; a custom icon in 05_dummy never showed - use iconId -1 (hidden signal) or a status
  icon sheet (`fight_script.md` 9).

## 6. Tests (tester, solo dev profile, then pack, then co-op)

Buy every item; crush A then B, B then A, only one, none -> each reaches the right fight; win and lose each; back at the
Roundtable no leftover item / buff / weather / marker; a target of every arena type (m19 variation, m18, m16) at least once.
Co-op: host crushes, client crushes, both crush in different order, crush late; every player reports which fight their own screen
showed.

## Unverified

Engine reset of shop stock flags per expedition; GoodsDialog prompt; client shop purchase under Seamless Co-op; late joiners
without the decision flags; credit for redirected DLC targets.
