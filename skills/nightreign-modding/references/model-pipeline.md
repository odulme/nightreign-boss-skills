# 模型 / 贴图替换流水线（partsbnd → FLVER / TPF）

## 文件结构（以追踪者原皮 bd_m_5000 为例）
- `bd_m_5000.partsbnd.dcx` = BND4：`BD_M_5000.flver`（版本 0x20021，Y-up，245 骨含 [Cloth] 骨与 Hip/Knee/Twist 辅助骨，8 网格、7 材质 P[BD_M_5000]_body/Face/fur/leather/mant/others/body_Cloth.matxml）+ `BD_M_5000.tpf`（_a 4096² BC1 sRGB、_n 4096² BC7、_m 1024 BC4、mant_v2_a/_n 披风）+ anibnd + `_c.clm2/_c.hkx` 布料。
- WitchyBND `-p` 解包到 `X-partsbnd-dcx\`（含 `_witchy-bnd4.xml`）；TPF 再 `-p` 得 `X-tpf\*.dds` + `_witchy-tpf.xml`。对目录再 `-p` 即重打包。
- 参考尺度（追踪者世界坐标，米）：髋关节 z≈0.97、膝 0.55、肩点 (0.24,1.43)、脸 z 1.50–1.72、头盔 1.535–1.78、手套腕 |x|≈0.55 半径 0.05。原版身体约 21 万三角/13 万顶点；参考皮肤单件 2–3 万三角也够。

## 工具能力边界
- **FLVER Editor**（`MySFformat.exe [flver]`，asasasasasbc 分支，支持 NR）：导出 DAE/FBX（骨骼+权重+双 UV）；`Import Model` 导入 FBX（勾掉 Use Bone conversion；材质名前缀 `<fbx名>_`，matxml 需事后映射；**忽略节点变换只取网格数据**；`Delete` 复选在自动化下无效）；`Modify` 才写盘（弹 "Node modification finished"）。导入逐‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌三角拆顶点（顶点数≈3×三角数）。
- io_soulstruct（Blender 插件）不支持 NR 的 FLVER 顶点格式，放弃。
- SoulsFormats 小工具（本 skill `scripts/*.cs`）：flverkeep（--info/--cullinfo/--nocull/--cull/--empty/--crop/--uvskirt/--remap）、flverdiag、flverbones、flverdump（→JSON，可把参考皮肤按骨名绑到自己的骨架摆姿势做对照渲染）。
- 贴图：texconv 解 DDS→PNG（`-ft png`，BC7 也可）与编码；Pillow 只解 BC1（dxgi 72→71）。

## Blender 侧（头less，参数化脚本每版一个 tag）
- 坐标：Blender Z 上、−Y 正面；FLVER/OBJ dump 为 Y-up。
- 造型路线结论：**逐点整形**（把外壳推向目标截面）在交界处必然出缝/棱；**目标形状基元的体素并集**（躯干椭圆放样 + 颈锥 + 袖锥/裤锥沿拟合的肢体轴线 + 盆骨块 + 裆桥）→ 分组 remesh+smooth 再并集 → 只轻平滑保留有意的台阶，最稳。来源身体网格有开口/薄片时在轴线内塞填充球做实心骨架，否则重网格产生内壁/隧道。
- 权重：从源身体权重 KDTree 转移；零权重顶点必须补（游戏里塌到原点）；删除所有非骨名顶点组；限 4 骨、剪 <1.5%、归一化；腋下/髋部/裆部用显式 smoothstep 过渡；Hip/Knee 等辅助骨在 Blender 不动但游戏里会动，预览时按主骨一半角度驱动。
- 上衣/裤子拆两块网格（参考皮肤结构）：裤子 100% 大腿到髋下约 12 cm，在上衣内向上延伸到髋关节并 smoothstep 过渡到骨盆、顶部封口朝下；上衣下摆刚性骨盆（大腿份额 ≤10–15%）、罗纹收拢贴住裤腰（间隙 1.5–2.5 cm）；裆部中线两条大腿各一半（分腿对称、深蹲随腿上抬）。任何 z≈髋下 15 cm 处带骨盆权重的顶点在双腿同屈时会吊在下摆下。
- UV：躯干绕 Z 圆柱、袖子绕**拟合的手臂轴线**（固定轴会压缩角度）、腿绕腿轴；判定袖子用 |x| 阈值而不是高度（A 姿势前臂较低）。贴图密度目标 ≥800 px/m。
- 导‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌出：对所有新对象执行 `me.transform(M)`（M = 骨架世界矩阵的逆 × 对象世界矩阵）、矩阵置单位、parent=armature；材质名用原材质名以便映射。
- 渲染检查：固定视图集（front/side/back/quarter/特写）+ 姿势视图（大腿骨 Z=外展、Y=前抬、X=扭转；深蹲 = 大腿 85 + 小腿 −100 + 脊柱 40；跨步 35/−25；分腿 12；高踢 80；举臂）+ 仰视机位（臀后下方）；材质双面、法线强度 1.0；分色平光渲染（Workbench + 每对象纯色）区分阴影与真洞。

## 贴图通道约定（统计原版 + 参考皮肤得出）
- `_n`：R/G 法线（社区说 FromSoft 为 DirectX 绿），**B = 光泽度**（金属 64–128、皮肤≈37、布料 0–30），A=255（或遮罩）。黑色布料 B 6–12。
- `_m`：金属度，原版布料 79% 像素为 0 → 布料区必须 0。
- `_a`：BC1 sRGB，完整 mip（texconv `-m 0`）；标志按 UV 岛投影，跨岛接缝保护阈值 ≥0.15·纹理边长。
- 织物：CC0 素材（Poly Haven cotton_jersey/knitted_fleece）漫反射归一化压成近黑（基色 11–16 ±3），法线 ×1.2 铺 1024px/循环；罗纹带用正弦法线。程序化宏观褶皱**不要**放法线（游戏里成斑块）。

## 装机流程（编辑器 GUI 见 gui-automation.md）
1. 编辑器打开原皮 FLVER 的干净副本 → Import Model <tag>_full.fbx → Modify。
2. 删原网格 + 材质映射：`flverkeep in out --empty <原网格序号> --remap <fbx名>_`（保留网格槽位以防布料按序号绑定；若确定无物理可整网格删除）。
3. `flverkeep --info` 列网格；衣物网格 `--nocull`，Face 材质与面部贴片 `--cull`（序号随 FBX 导入顺序变，按材质/顶点数认）。
4. `flverdiag` 核查（bbox 合理、zeroW=0、nearOrigin=0）。
5. `WitchyBND -p <tpf目录>`、`WitchyBND -p <partsbnd目录>` → 复制 dcx 到 `mod\parts\`；每版备份 FLVER。
6. 关闭编辑器，把干净原版 FLVER 复制回输入位置备下次。

## 布料物理结论
`_c.hkx`（Havok 2018 tagfile）只有 hclObjectSpaceSkinOperator + hclObjectSpaceMeshMeshDeformOperator：骨→模拟网格→**显示网格顶点变形**，不‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌驱动 [Cloth] 骨；`_c.clm2` 极小。自制网格无法加物理；复用原版带物理网格：保持顶点顺序，可用 flverkeep --empty/--crop/--uvskirt 裁面改 UV。

## 质量标准
见 QA_STANDARD.md（廓形数值、拓扑、蒙皮、接缝、贴图、贴合度，权重 20/10/30/20/10/10，放行 ≥90 且接缝≥90、蒙皮≥85）。检查脚本思路：权重规则统计、袖口 UV 落点、纹理密度（面在 3D 与 UV 中的边长比）、姿势下边长绝对伸长；裆部膜在单腿大幅摆动时伸长 20–30 cm 属线性蒙皮固有（原版同级）。
