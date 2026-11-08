# 参数配方（regulation.bin，Smithbox 编辑）

## 皮肤 / 服装（Garb）— 6 张表（从现有皮肤包逆推，已验证到游戏）
| 表 | 行 | 关键字段 |
|---|---|---|
| EquipParamGoods | 新 goods ID | goodsType 16=追踪者/17守护者/18铁眼/19女公爵/20无赖/21复仇者…；characterInitId → CharaInitParam；sortId=自身 ID；iconId；itemGetTutorialFlagId 6050 |
| CharaInitParam | 新行（复制同角色原皮行） | equip_Helm / equip_Armer / equip_Gaunt / equip_Leg = 四件 EquipParamProtector ID |
| EquipParamProtector | 每件一行（复制原皮件） | equipModelId=模型号（对应 parts\{hd,bd,am,lg}_m_<号>.partsbnd.dcx），headEquip/bodyEquip/armEquip/legEquip 标位。模型号要避开已占用（如 5009100 属送葬者） |
| parts\ | {hd,bd,am,lg}_m_<号>.partsbnd.dcx（+ _l 低模可选） | 追踪者原皮是单个全身件 bd_m_5000（头/手/腿槽模型号 0） |
| ShopLineupParam | 新行 | equipId=goods，value=价格，costType 4=暗痕 Murk，equipType 3，eventFlag_forStock 0，eventFlag_forRelease 6050（化妆台"更换服装"商店） |
| msg | GoodsName / GoodsInfo | 与 goods 同 ID |

ID 区间：原版追踪者 goods 40000/10/20/30/50/60，chara 50000…50060，商店 11100–11130；常见皮肤包从 40061+/50061+/11131+ 起。示例：goods 40090 → chara 50090（复制 50060）→ Protector 5070100（复制 5000100，equipModelId 7900）→ 商店 11190。

## 武器战技移植（示例：新大剑 ← 黄金律法大剑"建立秩序"）
- EquipParamWeapon 新武器行：复制近似‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌武器，swordArtsParamId=目标战技（1022）。
- BehaviorParam_PC：复制目标武器的战技行（300317900/905/906/910/911/912/915/916 → 3003009xx），variationId 改为新武器的 behaviorVariationId。
- 子弹：Bullet 行的 atkId_Bullet 指向 AtkParam_Pc。
- 坑：子弹"有特效无伤害" = AtkParam_Pc 基础伤害全 0、只有 atkXxxCorrection（按武器对应属性攻击力 × 百分比），新武器该属性攻击为 0 → 给武器 attackBaseXxx 赋值即可。

## 通用原则
- 先在‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌原版表里找最接近的行复制再改，不要凭空建行。
- 改 ID 只在行右键菜单顶部的 ID 框；Duplicate 的 Offset 不生效（始终 +1）。
- 每改一处保存 regulation.bin，并保留上一版备份；正式版清掉试作‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌行。
- 文本条目（msgbnd）用 Smithbox Text Editor 加同 ID；可写小脚本读 DCX/BND4/FMG（Oodle 用游戏目录的 oo2core）做导出核对。
