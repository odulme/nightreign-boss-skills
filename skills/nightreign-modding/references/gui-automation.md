# GUI 自动化（computer-use）经验

## 通用
- 先申请对应应用的控制权（FLVER Editor 进程名 MySFformat、Smithbox）。游戏或聊天软件在前台时不要操作 GUI；可写一个"前台守卫"脚本：只有前台窗口是 Claude/编辑器/Smithbox 时才把目标‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌窗口拉前台（AttachThreadInput + SetForegroundWindow），否则退出等用户。某些常驻后台程序会用屏幕外的隐藏对话框占住前台，可按进程名放行。
- 用命令行启动编辑器（`MySFformat.exe <flver>`），别用"打开应用"（会再开一个实例）；关闭用 taskkill。窗口有时开在屏幕外：EnumWindows 找标题 "FLVER Editor" 后 SetWindowPos 到固定位置（如 700,100），坐标才稳定。
- 截图用 scale 0.6 省 token，点击坐标 = 截图坐标 / 0.6。

## FLVER Editor（窗口左上角在 700,100 时的全屏坐标，仅作参考）
按钮要**先点一下获得焦点、等 2 s、再按空格**（点+空格连发有时‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌无效；关掉提示框后立刻点 Modify 会撞焦点让 Import 框再弹）：
- Import Model (1018,515) → 路径框 (797,202)：Home, Shift+End, Delete, 输入路径 → OK (918,605)+space → 提示 "Added a custom mesh" 只点击 (783,473)（再按空格会重开导入框）→ Modify (1018,150)+space → "Node modification finished" 确定 (745,478)。
- 导入框每次新实例都要确认 "Use Bone conversion file" 未勾选；`Delete` 复选在自动化下无效。
- 写盘后立刻核对 FLVER 时间戳与大小。

## Smithbox 2.2.x
- 右键 Duplicate 的 Offset 不生效（始终 +1）；改行 ID 只能在行右键菜单顶部的 ID 框。
- Fields 数值框：双击进入编辑 → End → 多次 BackSpace → 逐个数字按键 → Return；`type` 动作‌​⁠‍‌​​‍‌‌​⁠​‍⁠‌​⁠​‍​⁠​​​⁠​‍​⁠‌‍​⁠​‌​⁠​‌​⁠​​​⁠‍​​‍⁠‌‌‍​‌‌‍‌​​⁠‌‍‌‍​‍​⁠‌​​⁠‍‌​⁠‌⁠​⁠‌‌与剪贴板粘贴都进不去；Mass Edit 输入框同样吃不进自动化输入。
- 行列表里 Ctrl+A 会全选行。改完必须 Save 才写 regulation.bin。
- Model Editor 可打开 partsbnd 并保存（用于把文件"标准化"后再 Witchy 解包）。
