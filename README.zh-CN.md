# Nightreign Boss Skills（黑夜君临 BOSS 制作技能包）

[English](README.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

一组 Claude Code 技能（skills），用于以离线 MOD 的形式为《艾尔登法环：黑夜君临》(ELDEN RING NIGHTREIGN) 制作 BOSS：把其他已正式发售游戏里的
BOSS 移植过来、用自己的模型做原创 BOSS，以及把它们做成夜王战。内容提炼自真正进入实际游玩的移植与制作项目，只保留在游戏里验证有效的方法。
这些笔记写给宁愿读帧表、也不愿靠猜的人。

> 非官方粉丝项目，与 FromSoftware、万代南梦宫（Bandai Namco）及 Anthropic 均无关联，也未获其认可。

## 技能内容

| 技能 | 覆盖范围 |
|---|---|
| `nightreign-boss-port` | BOSS 本体，按 13 个阶段（S0-S12）的流水线推进，每个阶段都有出口关卡：调研与提取、原创模型路线（绑骨、重定向原版动作）、行为图供体、FLVER 与 dummy、受击胶囊、根运动与 TAE（锁朝向、转身/重新瞄准窗口）、仅开发版使用的招式调试面板、伤害载体（吐息、地雷、扇形）、特效与音效（只改数值槽、显卡负载预算）、预编译 Lua AI 与 AI 堆、血量对标、部位破坏、联机，以及发布前检查清单。 |
| `nightreign-nightlord-replace` | 把 BOSS 做成新夜王或替换夜王：夜王战事件脚本、切换道具（"最后捏碎的为准"）、击杀记给原夜王、各语言名字、BGM 槽位、按血量比例分阶段、对标原版夜王的平衡（无缝联机血量公式、4~6 人、深夜）、联机同步（房主导演 / 客机跟随）、测试与发布打包（钉文件、正则差量转移、安装器、升级补丁、隐私扫描）。负责 S8-S12 阶段。 |
| `nightreign-modding` | 另外两个技能共用的基础：me3 配置与加载顺序、分层开发叠加包、Smithbox 与 regulation.bin 单元格修改、WitchyBND、FLVER / TPF 替换、参数配方、FXR 只改数值槽、单元格模式构建器、隐私扫描、证据标签与质量验收标准。 |

每个技能由一个 `SKILL.md`、按需读取的 `references/` 和几个小型辅助 `scripts/` 组成。各条结论都带有证据标签（`[game-MP]`、`[game]`、`[code]`、
`[data]`、`[sim]`、`[model]`、`[inferred]`），可以分清哪些是在游戏里亲眼确认的，哪些只是推理。引擎相关事实基于黑夜君临 1.3.3.0
（regulation 10350000）测得，游戏‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌更新后请重新核实。

技能正文以英文为主，描述（description）为中英双语（两种语言都能触发），`nightreign-modding` 的少数参考文档为中文。

文中提到但未包含在本仓库的两个配套技能：`nightreign-map-port`（竞技场、地图块、碰撞、导航网格）和 `ds3-nightreign-port`（黑暗之魂3 配方）。
没有它们，本仓库的技能照样可用，只是不涉及这些主题。

## 铁律：只移植已发售的游戏

每个技能开头都有强制执行的**第 0 步**，并已接入 BOSS 流水线的 S0 阶段。在着手移植其他游戏的 BOSS、角色、敌人、模型、动作、特效、音效或地图之前，
模型必须：

1. 用网络搜索核实源游戏（或包含该内容的 DLC）已经正式公开发售、可以购买，并记下依据（名称、发售日期、所查来源）；
2. 若游戏或 DLC 尚未发售（已公布或开发中），或素材来自泄露、未发售版本的解包数据、测试版 / 网络测试（无论是否签有保密协议），或者无法确认发售状态，
   就必须**拒绝**这次移植并说明原因。

用自己的模型和素材制作的原创 BOSS 不需要这项核实。如果你 fork 或改编这些技能，请保留这条规则。

## 运行需求

- **Claude Code**（支持 skills），并开启网络搜索（第 0 步需要）。
- PC 版**《艾尔登法环：黑夜君临》**（你自己拥有的正版），以及你要移植的、已发售的源游戏的正版。
- **me3**（MOD 加载器，0.10.1 或更新）、**Smithbox**（参数、文本）、**WitchyBND**（解包 / 打包）。
- 视任务而定：**FLVER Editor**（支持黑夜君临的分支版本）、**Blender** 4.x、**texconv**（DirectXTex）、**SoulsFormats** 与
  .NET Framework 4.x 的 C# 编译器（用于几个 C# 小工具）、**Python** 3.11+、编译 AI 脚本用的 **Lua 5.0.2** 编译器（`luac50`）、
  **DarkScript3**（事件脚本）、**Seamless Co-op**（无缝联机，仅联机测试需要）。

## 安装

把三个技能文件夹全部复制到 Claude Code 的技能目录（BOSS 相关技能会引用 `nightreign-modding`）：

```
git clone <本仓库地址> nightreign-boss-skills
cp -r nightreign-boss-skills/skills/* ~/.claude/skills/
```

- 个人技能（所有项目可用）：`~/.claude/skills/`（Windows 下为 `%USERPROFILE%\.claude\skills\`）。
- 项目技能（仅某个项目）：`<你的项目>/.claude/skills/`。

之后新开一个 Claude Code 会话即可。当你询问黑‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌夜君临的 BOSS、夜王或 MOD 制作时，技能会根据描述自动加载；也可以直接点名（"用 nightreign-boss-port"）。

## 负责任地使用

- 只做免费、非商业的 MOD。不得出售、设置付费门槛或打包出售任何含有其他游戏素材（模型、贴图、动作、特效、音效、音乐、文本）的内容。
- 遵守各源游戏及黑夜君临的最终用户许可协议（EULA）和服务条款；只从你自己拥有的正版中提取；分享移植作品时注明源游戏及其版权方。
- 仅限离线。带 MOD 的黑夜君临一律通过 me3 启动，关闭 Easy Anti-Cheat（EAC）并使用独立存档。切勿带着改动过的文件连接官方在线服务或官方匹配：
  黑夜君临使用 Easy Anti-Cheat，可能被封号。本技能中的"联机"均指 Seamless Co-op（无缝联机）MOD，它在官方匹配之外运行。

## 许可协议

本仓库的全部内容——文档以及 Python / C# 辅助脚本——均采用**知识共享 署名-非商业性使用-相同方式共享 4.0 国际**许可协议
（CC BY-NC-SA 4.0）。版权所有 (c) 2026 odulnme。完整法律文本见 [LICENSE](LICENSE)，简要说明见 [NOTICE](NOTICE)：

- **署名**：必须注明（"Nightreign Boss Skills by odulnme"、原仓库链接、许可协议，并说明你做了哪些修改）。
- **禁止商业使用**：不得出售、转售、设置付费门槛，或把本内容（原版或修改版）打包进付费产品或服务。
- **相同方式共享**：改编作品必须采用相同的许可协议。

由于带有非商业条款，这是"源码可见"（source-available）的许可，而不是 OSI 认可的开源许可。本仓库不含任何游戏文件，许可协议也不涵盖任何游戏内容。

## 致谢

- 技能作者与维护者：**odulnme**。
- 《艾尔登法环：黑夜君临》由 **FromSoftware** 开发；游戏本身、其内容及商标归 FromSoftware 与**万代南梦宫娱乐（Bandai Namco Entertainment）**所有。
  技能中‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌作为示例提到的源游戏同样归各自权利人所有（《怪物猎人：世界》—— Capcom；《碧蓝幻想 Relink》—— Cygames；《黑暗之魂3》—— FromSoftware）。
- 感谢这些技能所依赖的工具及其作者与贡献者：**me3**（garyttierney）、**Smithbox**（vawser）、**WitchyBND**（ividyon）、**SoulsFormats**（TKGP）、
  **FLVER Editor** 及其黑夜君临分支（asasasasasbc）、**DarkScript3**、**Seamless Co-op**（LukeYui）、**Blender**（Blender 基金会）、
  **DirectXTex / texconv**（微软）、**Lua**（PUC-Rio）。
- 感谢 FromSoftware MOD 社区，正是大家公开分享的研究和文档让这些工作成为可能。

## 免责声明

本项目为非官方粉丝项目，与 FromSoftware、万代南梦宫、Capcom、Cygames、Anthropic 以及任何工具作者均无关联。所有商标归各自所有者所有。
技能和脚本按"原样"提供，不附带任何担保。MOD 可能损坏存档；如果把改动过的文件带到线上，还可能导致封号。请先备份存档，风险自负。
